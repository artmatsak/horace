import re
import logging
from openai_chatbot import OpenAIChatbot
from router import Router
from typing import Dict, Callable


class GRACEChatbot(OpenAIChatbot):
    INITIAL_PROMPT_TEMPLATE = """You are an AI assistant for {}. You process customers' requests as follows:

1. Greet the customer and ask how you can be of help.
2. Identify the customer's request and the backend command to process it.
3. Keep asking questions until you have gathered concrete values for all the parameters required by the backend command and nothing else. Do not assume that you know any of the values. Do not use values from command examples. Empty values are not accepted.
4. Ask the customer to hold on and then process their request by sending a command JSON to the backend in the following format:

AI: All right, let me look into this for you. [json]{{"command": "cancel_booking", "params": {{"reference": "GLEYHL"}}}}[/json]
Backend: Booking canceled

5. Confirm the execution result back to the customer and ask if there's anything else you can do for them.
6. If there's nothing else, say goodbye and output "END".

Only the following Python commands are available to you. If the customer's request is not among the provided commands, you refuse to process it:

{}

You use all dates exactly as provided by the customer, without rephrasing or converting them. {}

A transcript of a chat session with a customer follows."""
    NAMES = ("AI", "Customer")
    BACKEND_NAME = "Backend"

    def __init__(
        self,
        openai,
        backend: Router,
        domain: Dict[str, str],
        output_callback: Callable[[str], None],
        openai_engine: str = "text-davinci-003"
    ):
        commands_string = "\n".join([f'- {c["python_sig"]} - {c["desc"]}. Example JSON: {c["example_json"]}'
                                     for c in backend.registry.values()])
        initial_prompt = self.INITIAL_PROMPT_TEMPLATE.format(domain["business_name"],
                                                             commands_string,
                                                             domain["extra_instructions"])
        super().__init__(openai=openai,
                         initial_prompt=initial_prompt,
                         output_callback=output_callback,
                         names=self.NAMES,
                         openai_engine=openai_engine)

        self.stop.append(f"{self.BACKEND_NAME}:")
        self.backend = backend
        self.domain = domain

    def _get_all_utterances(self):
        utterance = super()._get_next_utterance()

        m = re.match(
            r"^(.*?)( \[json\](.*?)\[/json\].*)?$", utterance, re.IGNORECASE)
        command_json = m[3]

        self.output_callback(m[1].strip())

        if command_json:
            logging.debug(f"Invoking backend command: {repr(command_json)}")

            try:
                result = self.backend.invoke(command_json)
                logging.debug(f"Got backend response: {repr(result)}")
            except Exception as e:
                result = str(e)
                logging.error(e)

            self._add_response(self.BACKEND_NAME, result)
            self._get_all_utterances()
