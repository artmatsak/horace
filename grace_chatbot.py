import re
import logging
from openai_chatbot import OpenAIChatbot
from router import Router
from typing import Dict


class GRACEChatbot(OpenAIChatbot):
    INITIAL_PROMPT_TEMPLATE = """You are an AI assistant for {}. You process customers' requests as follows:

1. Greet the customer and ask how you can be of help.
2. Identify the customer's request.
3. Gather all the information necessary to process the request.
4. Summarize all of the information for the customer and ask them to confirm it.
5. Ask the customer to hold on and then process the request by sending a command JSON to the backend as follows: (To Backend) [json]{{command JSON}}[/json]
6. Confirm the result back to the customer and ask if there's anything else you can do for them.
7. If there's nothing else, say goodbye and output the special "END" token.

A typical interaction proceeds similar to the following:

Customer: I'd like to cancel my table reservation.
AI: Sure. Can you give me the booking reference please?
Customer: It's GLEYHL.
AI: I understand that you'd like to cancel your reservation GLEYHL, is that correct?
Customer: Yes.
AI: All right, let me look into this for you. (To Backend) [json]{{"command": "delete_booking", "params": {{"reference": "GLEYHL"}}}}[/json]
Backend: (To AI) Booking canceled
AI: I have now canceled your booking. Is there anything else I can do for you?
Customer: That's it, thanks!
AI: No problem, have a nice day! END

Only the following Python commands are available to you. You must get all command parameters from the customer. A parameter cannot be empty. If the customer's request is not among the provided commands, you refuse to process it:

{}

{}

A transcript of a chat session with a customer follows."""
    NAMES = ("AI", "Customer")
    BACKEND_NAME = "Backend"

    def __init__(
        self,
        openai,
        backend: Router,
        domain: Dict[str, str],
        openai_engine: str = "text-davinci-003"
    ):
        commands_string = "\n".join([f'- {c["python_sig"]} - {c["desc"]}. Example JSON: {c["example_json"]}'
                                     for c in backend.registry.values()])
        initial_prompt = self.INITIAL_PROMPT_TEMPLATE.format(domain["business_name"],
                                                             commands_string,
                                                             domain["extra_instructions"])
        super().__init__(openai=openai,
                         initial_prompt=initial_prompt,
                         names=self.NAMES,
                         openai_engine=openai_engine)

        self.stop.append(f"{self.BACKEND_NAME}:")
        self.backend = backend
        self.domain = domain

    def _get_all_utterances(self):
        utterance = super()._get_next_utterance()

        m = re.match(
            r"^(.*?)(\(To Backend\) \[json\](.*)\[/json\].*)?$", utterance)
        utterances = [m[1].strip()]
        command_json = m[3]

        if command_json:
            logging.debug(f"Invoking backend command: {repr(command_json)}")

            try:
                result = self.backend.invoke(command_json)
                logging.debug(f"Got backend response: {repr(result)}")
            except Exception as e:
                result = str(e)
                logging.error(e)

            self._add_response(self.BACKEND_NAME, f"(To AI) {result}")
            utterances += self._get_all_utterances()

        return utterances
