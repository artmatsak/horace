import logging
from backends.backend import Backend
from typing import Tuple, Callable, Coroutine, List, Optional


class Chatbot():
    STATE_LISTENING = "listening"
    STATE_REPLYING = "replying"
    STATE_ENDED = "ended"

    def __init__(
        self,
        backend: Backend,
        initial_prompt: str,
        utterance_coroutine: Callable[[str], Coroutine],
        state_coroutine: Optional[Callable[[str], Coroutine]] = None,
        names: Tuple[str, str] = ("AI", "Human"),
        end_token: Optional[str] = None,
        temperature: Optional[float] = 0.9
    ):
        self.backend = backend
        self.prompt = initial_prompt
        self.utterance_coroutine = utterance_coroutine
        self.state_coroutine = state_coroutine
        self.names = names
        self.end_token = end_token
        self.temperature = temperature

        self.stop = [f"{name}:" for name in names]
        self._state = self.STATE_LISTENING

        logging.debug(f"Initialized chatbot with prompt:\n{self.prompt}")

    @property
    def state(self):
        return self._state

    async def _set_state(self, value):
        self._state = value

        if self.state_coroutine:
            await self.state_coroutine(self._state)

    async def send_responses(self, responses: List[str]):
        if self.state != self.STATE_LISTENING:
            raise RuntimeError(
                f"Attempting to send responses in wrong state: {self.state}")

        for response in responses:
            self._add_response(self.names[1], response.strip())

        await self._set_state(self.STATE_REPLYING)
        await self._get_all_utterances()
        await self._set_state(self.STATE_LISTENING)

    def _add_response(self, name: str, response: str):
        log_response = f"{name}: {response}"
        logging.debug(f"Adding response: {repr(log_response)}")
        self.prompt += f"\n{name}: {response}"

    async def _get_all_utterances(self):
        utterance = await self._get_next_utterance(self.temperature)

        if utterance:
            await self.utterance_coroutine(utterance)

        self._add_response(self.names[0], utterance)

    async def _get_next_utterance(self, temperature: float) -> str:
        utterance = await self.backend.complete(
            self.prompt + f"\n{self.names[0]}:",
            max_tokens=750,
            stop=self.stop,
            temperature=temperature
        )
        utterance = utterance.strip()
        logging.debug(f"Got utterance: {repr(utterance)}")

        if self.end_token:
            end_token_pos = utterance.find(self.end_token)
            if end_token_pos != -1:
                utterance = utterance[:end_token_pos].strip()
                self.state = self.STATE_ENDED

        return utterance
