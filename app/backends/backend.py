import abc
from typing import Optional, List


class Backend():
    @abc.abstractmethod
    async def complete(
        self,
        prompt: str,
        max_tokens: int = 16,
        stop: Optional[List[str]] = None,
        temperature: Optional[float] = 1.0
    ) -> str:
        pass
