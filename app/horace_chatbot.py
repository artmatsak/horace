import re
import json
import logging
from chatbot import Chatbot
from backends.backend import Backend
from router import Router
from typing import Optional, Callable, Coroutine


class HoraceChatbot(Chatbot):
    INITIAL_PROMPT_TEMPLATE = """You have access to the following plugin APIs, as defined by their OpenAPI specifications:

{plugins_string}

You can use the APIs above if you determine that you need the functionality they provide. You do not proactively steer the user towards performing any actions available to you.

To call an API method, use the following format: {call_opening_tag}[JSON]{call_closing_tag}, where [JSON] is a JSON object with the following properties:

- plugin_system_name: The system name for the plugin as defined above
- request_object_params: A dictionary of parameters for instantiation of the corresponding requests.Request(method, url, data, json, params) object in Python.

Here is an example with made-up values:

{names[1]}: OK, now add that item to my list.
{names[0]}: Sure, let me look into that. {call_opening_tag}{{"plugin_system_name": "test", "request_object_params": {{"method": "POST", "url": "https://www.example.com/api/"}}}}{call_closing_tag}
{names[2]}: API responded with HTTP status code 200, response body: OK
{names[0]}: All done!

If you have multiple calls to make, you wait for the API response before making the next one.

Your API calls and any {names[2]} responses are invisible to the user.

You do not disclose any implementation details to the user, including the API methods available to you, the calls that you make etc."""
    NAMES = ("AI", "User", "System")
    CALL_OPENING_TAG = "<call>"
    CALL_CLOSING_TAG = "</call>"

    def __init__(
        self,
        backend: Backend,
        router: Router,
        utterance_coroutine: Callable[[str, Optional[bool]], Coroutine],
        state_coroutine: Optional[Callable[[str], Coroutine]] = None,
        extra_instructions: Optional[str] = None,
        temperature: Optional[float] = 0.9,
        retry_temperature: Optional[float] = 0.9,
        max_validation_retries: int = 0,
        debug_mode: bool = False
    ):
        prompt_blocks = []
        if extra_instructions:
            prompt_blocks.append(extra_instructions)

        plugin_blocks = []
        for name, plugin in router.registry.items():
            plugin_blocks.append(f"""plugin_human_name: {plugin["manifest"]["name_for_human"]}
plugin_human_description: {plugin["manifest"]["description_for_human"]}
plugin_system_name: {name}
{plugin["manifest"]["description_for_model"]}
{json.dumps(plugin["spec_dict"])}""")

        if plugin_blocks:
            prompt_blocks.append(self.INITIAL_PROMPT_TEMPLATE.format(
                names=self.NAMES,
                call_opening_tag=self.CALL_OPENING_TAG,
                call_closing_tag=self.CALL_CLOSING_TAG,
                plugins_string="\n\n".join(plugin_blocks)
            ))

        super().__init__(
            backend=backend,
            initial_prompt="\n\n".join(prompt_blocks) + "\n",
            utterance_coroutine=utterance_coroutine,
            state_coroutine=state_coroutine,
            names=self.NAMES,
            temperature=temperature
        )

        self.router = router
        self.retry_temperature = retry_temperature
        self.max_validation_retries = max_validation_retries
        self.debug_mode = debug_mode
        self.stop.append(self.CALL_CLOSING_TAG)

    async def _get_all_utterances(self):
        prepared_request = None

        for attempt_count in range(self.max_validation_retries + 1):
            temperature = self.retry_temperature if attempt_count > 0 else self.temperature
            utterance = await self._get_next_utterance(temperature)

            m = re.match(
                r"(.*?)($|" + re.escape(self.CALL_OPENING_TAG) + r"(.*))", utterance, re.DOTALL)
            stripped_utterance = m[1].strip()
            call_json = m[3]

            if self.debug_mode:
                await self.utterance_coroutine(utterance)

            if call_json:
                logging.debug(f"Processing API call: {repr(call_json)}")

                try:
                    try:
                        call_dict, ind = json.JSONDecoder().raw_decode(call_json)
                    except json.decoder.JSONDecodeError:
                        raise ValueError(f"Malformed JSON: {repr(call_json)}")

                    truncate_len = len(call_json) - ind
                    if truncate_len:
                        # Truncate the utterance so that it correctly ends with
                        # the JSON
                        utterance = utterance[:-truncate_len]

                    prepared_request = self.router.prepare(
                        call_dict["plugin_system_name"], call_dict["request_object_params"])
                except Exception as e:
                    result = str(e)
                    logging.error(e)

                    if self.debug_mode:
                        await self.utterance_coroutine(result, is_system=True)
                finally:
                    # Add back the closing call tag to the utterance - it's not
                    # generated due to self.stop
                    utterance += self.CALL_CLOSING_TAG

                if prepared_request:
                    break
            else:
                break

        if stripped_utterance and not self.debug_mode:
            await self.utterance_coroutine(stripped_utterance)

        self._add_response(self.names[0], utterance)

        if call_json:
            if prepared_request:
                status_code, text = self.router.send(prepared_request)
                logging.debug(
                    f"Got router response: {repr((status_code, text))}")

                result = f"API responded with HTTP status code {status_code}"
                if status_code >= 200 and status_code < 300:
                    result += f", response body: {text}"

                if self.debug_mode:
                    await self.utterance_coroutine(result, is_system=True)

            self._add_response(self.names[2], result)
            await self._get_all_utterances()
