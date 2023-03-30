import re
import json
import logging
from chatbot import Chatbot
from backends.backend import Backend
from router import Router
from typing import Optional, Callable


class HoraceChatbot(Chatbot):
    INITIAL_PROMPT_TEMPLATE = """You have access to the following plugin APIs, as defined by their OpenAPI specification YAML:

{plugins_string}

You can use the APIs above if you determine that you need the functionality they provide. You do not proactively steer the user towards performing any actions available to you.

To call an API method, use the following format: CALL [JSON], where [JSON] is a JSON object with the following properties:

- plugin_name: The system name for the plugin as defined above
- request_object_params: A dictionary of parameters for instantiation of the corresponding requests.Request object in Python.

For example:

AI: Sure, let me look into that. CALL {{"plugin_name": "[plugin_name for the plugin]", "request_object_params": {{"method": "POST", [other parameters for requests.Request()]}}}}
API: (To AI) [HTTP 200] Response body: OK
AI: All done!

No further text can follow an API call.

Your API calls and the responses from the API are invisible to the user.

You do not disclose any implementation details to the user, including the API methods available to you, the calls that you make etc.
"""
    NAMES = ("AI", "User")
    ROUTER_NAME = "API"

    def __init__(
        self,
        backend: Backend,
        router: Router,
        output_callback: Callable[[str], None],
        extra_instructions: Optional[str] = None
    ):
        plugins_string = "\n\n".join([f'plugin_name: {name}\n{plugin["manifest"]["description_for_model"]}\n```\n{plugin["spec_yaml"]}\n```'
                                      for name, plugin in router.registry.items()])

        initial_prompt = self.INITIAL_PROMPT_TEMPLATE.format(
            plugins_string=plugins_string
        )
        if extra_instructions:
            initial_prompt = f'{extra_instructions}\n\n{initial_prompt}'

        super().__init__(
            backend=backend,
            initial_prompt=initial_prompt,
            output_callback=output_callback,
            names=self.NAMES
        )

        self.stop.append(f"{self.ROUTER_NAME}:")
        self.router = router

    def _get_all_utterances(self):
        utterance = self._get_next_utterance()

        m = re.match(r"(.*?)($|CALL (.*))", utterance, re.DOTALL)
        utterance = m[1].strip()
        command_json = m[3]

        if utterance:
            self.output_callback(utterance)

        if self.prompt is not None:
            self.prompt = f"{self.prompt} {m[0]}"

        if command_json:
            logging.debug(f"Evaluating expression: {repr(command_json)}")

            try:
                try:
                    call_dict, ind = json.JSONDecoder().raw_decode(command_json)
                except json.decoder.JSONDecodeError:
                    raise ValueError(f"Malformed JSON: {repr(command_json)}")

                truncate_len = len(command_json) - ind
                if truncate_len:
                    # Truncate the prompt so that the AI's utterance correctly
                    # ends with the JSON
                    self.prompt = self.prompt[:-truncate_len]

                result = self.router.call(
                    call_dict["plugin_name"], call_dict["request_object_params"])
                logging.debug(f"Got router response: {repr(result)}")
            except Exception as e:
                result = str(e)
                logging.error(e)

            if self.prompt is not None:
                self._add_response(self.ROUTER_NAME, f"(To AI) {result}")
                self._get_all_utterances()
