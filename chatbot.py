import string
import logging
from backends.backend import Backend
from typing import Tuple, Callable, List, Optional


class Chatbot():
    def __init__(
        self,
        backend: Backend,
        initial_prompt: str,
        output_callback: Callable[[str], None],
        names: Tuple[str, str] = ("AI", "Human"),
        end_token: Optional[str] = None
    ):
        self.backend = backend
        self.initial_prompt = initial_prompt
        self.output_callback = output_callback
        self.names = names
        self.end_token = end_token

        self.prompt = None
        self.stop = [f"{name}:" for name in names]

    async def start_session(self, responses: List[str]):
        self.prompt = self.initial_prompt
        logging.debug(f"Starting chatbot session with prompt:\n{self.prompt}")
        await self.send_responses(responses)

    async def send_responses(self, responses: List[str]):
        if self.prompt is None:
            raise RuntimeError("Chatbot session is not active")

        for response in responses:
            self._add_response(self.names[1], response.strip())

        await self._get_all_utterances()

    def is_session_active(self) -> bool:
        return self.prompt is not None

    def _add_response(self, name: str, response: str):
        log_response = f"{name}: {response}"
        logging.debug(f"Adding response: {repr(log_response)}")
        self.prompt += f"\n{name}: {response}"

    async def _get_all_utterances(self):
        utterance = await self._get_next_utterance()

        if utterance:
            await self.output_callback(utterance)

        if self.prompt is not None:
            self.prompt = f"{self.prompt} {utterance}"

    async def _get_next_utterance(self) -> str:
        self.prompt += f"\n{self.names[0]}:"

        utterance = await self.backend.complete(
            self.prompt,
            max_tokens=750,
            stop=self.stop
        )
        utterance = utterance.strip()
        logging.debug(f"Got utterance: {repr(utterance)}")

        if self.end_token:
            end_token_pos = utterance.find(self.end_token)
            if end_token_pos != -1:
                utterance = utterance[:end_token_pos].strip()
                # Ending the session
                self.prompt = None

        return utterance
