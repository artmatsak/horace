import os
from pyaml_env import parse_config
import logging
from colorama import Fore, Style
from backends.openai_backend import OpenAIBackend
from router import Router
from horace_chatbot import HoraceChatbot
from dotenv import load_dotenv

load_dotenv()


BACKENDS = {
    "openai": OpenAIBackend
}


def print_utterance(utterance: str):
    print(Fore.BLUE + utterance + Style.RESET_ALL)


if __name__ == '__main__':
    logging.basicConfig(filename='sessions.log',
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)

    # Increase log level for OpenAI API
    openai_logger = logging.getLogger("openai")
    openai_logger.setLevel(logging.ERROR)

    config = parse_config("config.yaml")

    print("Initializing, please wait... ")

    chatbot = HoraceChatbot(
        backend=BACKENDS[config["backend"]["name"]](
            **config["backend"]["params"]),
        router=Router(plugins=config["plugins"]),
        output_callback=print_utterance,
        extra_instructions=config.get("extra_instructions")
    )

    chatbot.start_session()

    while not chatbot.session_ended():
        response = input(Fore.MAGENTA + "Your input -> " + Fore.YELLOW).strip()
        if response:
            chatbot.send_responses([response])
