import re
import json
import logging
from openai_chatbot import OpenAIChatbot
from router import Router
from typing import Dict, Callable


class HoraceChatbot(OpenAIChatbot):
    INITIAL_PROMPT_TEMPLATE = """You have access to the following plugin APIs, as defined by their OpenAPI specification YAML:

{plugins_string}

You can use the APIs above in your interactions with the user. To call an API method, use the following format: CALL [JSON], where [JSON] is a JSON object with the following properties:

- plugin_name: The system name for the plugin as defined above
- request_object_params: A dictionary of parameters for instantiation of the corresponding requests.Request object in Python.

For example:

AI: Sure, let me look into that. CALL {{"plugin_name": "[plugin_name for the plugin]", "request_object_params": {{"method": "POST", [other parameters for requests.Request()]}}}}
API: (To AI) [HTTP 200] Response body: OK

No further text can follow an API call. If you have multiple calls to make, you wait for the API response before making the next one.

You do not disclose the details of your inner workings to the user, nor the Python code that you execute.

User: Hi, how are you?"""
    NAMES = ("AI", "User")
    BACKEND_NAME = "API"

    def __init__(
        self,
        openai,
        backend: Router,
        domain: Dict[str, str],
        output_callback: Callable[[str], None],
        openai_model: str = "text-davinci-003",
        openai_endpoint: str = "completions"
    ):
        plugins_string = "\n\n".join([f'plugin_name: {name}\n{plugin["manifest"]["description_for_model"]}\n```\n{plugin["spec_yaml"]}\n```'
                                      for name, plugin in backend.registry.items()])

        initial_prompt = self.INITIAL_PROMPT_TEMPLATE.format(
            plugins_string=plugins_string
        )
        if 'extra_instructions' in domain:
            initial_prompt = f'{domain["extra_instructions"]}\n\n{initial_prompt}'

        super().__init__(openai=openai,
                         initial_prompt=initial_prompt,
                         output_callback=output_callback,
                         names=self.NAMES,
                         openai_model=openai_model,
                         openai_endpoint=openai_endpoint)

        self.stop.append(f"{self.BACKEND_NAME}:")
        self.backend = backend
        self.domain = domain

    def _get_all_utterances(self):
        utterance = self._get_next_utterance()

        m = re.match(r"(.*?)($|CALL (.*))", utterance,
                     re.IGNORECASE | re.DOTALL)
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

                result = self.backend.call(
                    call_dict["plugin_name"], call_dict["request_object_params"])
                logging.debug(f"Got backend response: {repr(result)}")
            except Exception as e:
                result = str(e)
                logging.error(e)

            if self.prompt is not None:
                self._add_response(self.BACKEND_NAME, f"(To AI) {result}")
                self._get_all_utterances()
