import os
import logging
from colorama import Fore, Style
# import mocks.openai as openai
import openai
from router import Router
from grace_chatbot import GRACEChatbot
from dotenv import load_dotenv
from typing import List

load_dotenv()

backend = Router()

domain = {
    "business_name": "Death Star, a Star Wars-themed restaurant in Cupertino, CA",
    "extra_instructions": "In your speech, you impersonate Jedi Master Yoda."
}


@backend.command(desc="book a table", example_params=("Jose James", 2, "2023-03-04 6:00 pm"))
def book_table(name: str, num_people: int, datetime: str) -> str:
    return "Booking successful, reference: YEHBZL"


def print_utterances(utterances: List[str]):
    for utterance in utterances:
        print(Fore.BLUE + utterance + Style.RESET_ALL)


if __name__ == '__main__':
    logging.basicConfig(filename='sessions.log',
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)

    openai.api_key = os.environ["OPENAI_API_KEY"]

    chatbot = GRACEChatbot(openai=openai, backend=backend, domain=domain)

    utterances = chatbot.start_session()

    while not chatbot.session_ended():
        print_utterances(utterances)
        response = input(Fore.MAGENTA + "Your input -> " + Fore.YELLOW)
        utterances = chatbot.send_response(response)

    print_utterances(utterances)
