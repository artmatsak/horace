import string
import logging
from typing import Tuple, Callable, List


class OpenAIChatbot():
    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    def __init__(
        self,
        openai,
        initial_prompt: str,
        output_callback: Callable[[str], None],
        names: Tuple[str, str] = ("AI", "Human"),
        end_token: str = "END",
        openai_model: str = "text-davinci-003",
        openai_endpoint: str = "completions"
    ):
        self.openai = openai
        self.initial_prompt = initial_prompt
        self.output_callback = output_callback
        self.names = names
        self.end_token = end_token
        self.openai_model = openai_model
        self.openai_endpoint = openai_endpoint

        self.prompt = None
        self.stop = [f"{name}:" for name in names]

    def start_session(self):
        self.prompt = self.initial_prompt
        logging.debug(f"Starting chatbot session with prompt:\n{self.prompt}")
        self._get_all_utterances()

    def send_responses(self, responses: List[str]):
        if self.prompt is None:
            raise RuntimeError("Chatbot session is not active")

        for response in responses:
            self._add_response(self.names[1], response.strip())

        self._get_all_utterances()

    def session_ended(self) -> bool:
        return self.prompt is None

    def _add_response(self, name: str, response: str):
        log_response = f"{name}: {response}"
        logging.debug(f"Adding response: {repr(log_response)}")
        self.prompt += f"\n{name}: {response}"

    def _get_all_utterances(self):
        utterance = self._get_next_utterance()

        if utterance:
            self.output_callback(utterance)

        if self.prompt is not None:
            self.prompt = f"{self.prompt} {utterance}"

    def _get_next_utterance(self) -> str:
        self.prompt += f"\n{self.names[0]}:"

        openai_params = {
            "max_tokens": 150,
            "stop": self.stop,
            "temperature": 0.9
        }

        if self.openai_endpoint == "completions":
            completion = self.openai.Completion.create(
                model=self.openai_model,
                prompt=self.prompt,
                **openai_params
            )
            utterance = completion.choices[0]["text"]
        elif self.openai_endpoint == "chat":
            completion = self.openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[{"role": self.ROLE_SYSTEM, "content": self.prompt}],
                **openai_params
            )
            utterance = completion['choices'][0]['message']['content']

        utterance = utterance.strip(string.whitespace + '"')
        logging.debug(f"Got utterance: {repr(utterance)}")

        end_token_pos = utterance.find(self.end_token)
        if end_token_pos != -1:
            utterance = utterance[:end_token_pos].strip()
            # Ending the session
            self.prompt = None

        return utterance
