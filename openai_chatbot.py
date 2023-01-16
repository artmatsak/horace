from typing import Tuple


class OpenAIChatbot():
    def __init__(
        self,
        openai,
        initial_prompt: str,
        first_utterance: str,
        names: Tuple[str, str] = ("AI", "Human"),
        end_token: str = "END",
        openai_engine: str = "text-davinci-003"
    ):
        self.openai = openai
        self.initial_prompt = initial_prompt
        self.first_utterance = first_utterance
        self.names = names
        self.end_token = end_token
        self.openai_engine = openai_engine

        self.prompt = ""
        self.stop = [f"{name}:" for name in names]

    def start_session(self) -> str:
        self.prompt = f"{self.initial_prompt}\n\n{self.names[0]}: {self.first_utterance}"
        return self.first_utterance

    def send_response(self, response: str) -> str:
        self.prompt += f"\n{self.names[1]}: {response.strip()}\n{self.names[0]}:"

        completion = self.openai.Completion.create(
            engine=self.openai_engine,
            prompt=self.prompt,
            stop=self.stop,
            temperature=0.7
        )

        utterance = completion.choices[0]["text"].strip()

        end_token_pos = utterance.find(self.end_token)
        if end_token_pos != -1:
            utterance = utterance[:end_token_pos].strip()
            # Ending the session
            self.prompt = ""
        else:
            self.prompt = f"{self.prompt} {utterance}"

        return utterance

    def session_ended(self) -> bool:
        return not self.prompt
