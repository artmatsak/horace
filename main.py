import argparse
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


def print_utterance(utterance: str, is_router_result: bool = False):
    print((Fore.GREEN if is_router_result else Fore.BLUE) +
          utterance + Style.RESET_ALL)


if __name__ == '__main__':
    logging.basicConfig(filename='sessions.log',
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)

    # Increase log level for OpenAI API
    openai_logger = logging.getLogger("openai")
    openai_logger.setLevel(logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='enable debug mode')
    args = parser.parse_args()

    config = parse_config("config.yaml")

    chatbot = HoraceChatbot(
        backend=BACKENDS[config["backend"]["name"]](
            **config["backend"]["params"]),
        router=Router(plugins=config.get("plugins")),
        output_callback=print_utterance,
        extra_instructions=config.get("extra_instructions"),
        debug_mode=args.debug
    )

    while True:
        response = input(Fore.MAGENTA + "Your input -> " + Fore.YELLOW).strip()

        if not response:
            continue

        if not chatbot.is_session_active():
            chatbot.start_session([response])
        else:
            chatbot.send_responses([response])

        if not chatbot.is_session_active():
            break
