import openai
from backends.backend import Backend
from typing import Optional, List


class OpenAIBackend(Backend):
    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    def __init__(
        self,
        api_key: str,
        model: str = "text-davinci-003",
        endpoint: str = "completions",
        temperature: float = 1.0
    ):
        openai.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.temperature = temperature

    async def complete(
        self,
        prompt: str,
        max_tokens: int = 16,
        stop: Optional[List[str]] = None
    ) -> str:
        openai_params = {
            "max_tokens": max_tokens,
            "stop": stop,
            "temperature": self.temperature
        }

        if self.endpoint == "completions":
            completion = await openai.Completion.acreate(
                model=self.model,
                prompt=prompt,
                **openai_params
            )
            completion = completion.choices[0]["text"]
        elif self.endpoint == "chat":
            completion = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": self.ROLE_SYSTEM, "content": prompt}],
                **openai_params
            )
            completion = completion['choices'][0]['message']['content']

        return completion
