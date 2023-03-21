import os
import yaml
import logging
from colorama import Fore, Style
# import mocks.openai as openai
import openai
from backend import backend
from grace_chatbot import GRACEChatbot
from dotenv import load_dotenv

load_dotenv()


def print_utterance(utterance: str):
    print(Fore.BLUE + utterance + Style.RESET_ALL)


if __name__ == '__main__':
    logging.basicConfig(filename='sessions.log',
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)

    # Increase log level for OpenAI API
    openai_logger = logging.getLogger("openai")
    openai_logger.setLevel(logging.ERROR)

    openai.api_key = os.environ["OPENAI_API_KEY"]

    with open("config.yaml", "r") as stream:
        config = yaml.safe_load(stream)
    with open("domain.yaml", "r") as stream:
        domain = yaml.safe_load(stream)

    print("Initializing, please wait... ")

    chatbot = GRACEChatbot(openai=openai, backend=backend,
                           domain=domain, output_callback=print_utterance,
                           openai_model=config["openai"]["model"],
                           openai_endpoint=config["openai"]["endpoint"])

    chatbot.start_session()

    while not chatbot.session_ended():
        response = input(Fore.MAGENTA + "Your input -> " + Fore.YELLOW).strip()
        if response:
            chatbot.send_responses([response])
