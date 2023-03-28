import re
import logging
from openai_chatbot import OpenAIChatbot
from router import Router
from typing import Dict, Callable


class HoraceChatbot(OpenAIChatbot):
    INITIAL_PROMPT_TEMPLATE = """You have access to the following plugin APIs, as defined by their OpenAPI specifications:

{plugins_string}

You can use the APIs above in your interactions with the user. To call an API method, use the following format: EXECUTE [Python requests function call]. For example:

AI: Sure, let me look into that. EXECUTE requests.post([some parameters])
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
        plugins_string = "\n\n".join([f'{name}: {plugin["manifest"]["description_for_model"]}\n```\n{plugin["openapi_spec"]}\n```'
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

        m = re.match(r"(.*?)($|EXECUTE (.*))", utterance,
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
                result = self.backend.eval(command_json)
                logging.debug(f"Got backend response: {repr(result)}")
            except Exception as e:
                result = str(e)
                logging.error(e)

            if self.prompt is not None:
                self._add_response(self.BACKEND_NAME, f"(To AI) {result}")
                self._get_all_utterances()
