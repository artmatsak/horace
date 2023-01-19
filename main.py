import os
import logging
from colorama import Fore, Style
# import mocks.openai as openai
import openai
from backend import backend, domain
from grace_chatbot import GRACEChatbot
from dotenv import load_dotenv
from typing import List

load_dotenv()


def print_utterances(utterances: List[str]):
    for utterance in utterances:
        print(Fore.BLUE + utterance + Style.RESET_ALL)


if __name__ == '__main__':
    logging.basicConfig(filename='sessions.log',
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)

    # Increase log level for OpenAI API
    openai_logger = logging.getLogger("openai")
    openai_logger.setLevel(logging.ERROR)

    openai.api_key = os.environ["OPENAI_API_KEY"]

    chatbot = GRACEChatbot(openai=openai, backend=backend, domain=domain)

    utterances = chatbot.start_session()

    while not chatbot.session_ended():
        print_utterances(utterances)
        response = input(Fore.MAGENTA + "Your input -> " + Fore.YELLOW)
        utterances = chatbot.send_response(response)

    print_utterances(utterances)
