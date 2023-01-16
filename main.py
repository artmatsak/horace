from colorama import Fore, Back, Style
import mocks.openai as openai
from router import Router
from openai_chatbot import OpenAIChatbot


backend = Router()


@backend.command(desc="book a table", example_params=(2, "2023-03-04 6:00 pm"))
def book_table(num_people: int, datetime: str) -> str:
    return "Booking successful, reference: YEHBZL"


if __name__ == '__main__':
    openai.api_key = ""

    initial_prompt = "Some prompt"
    first_utterance = "Hello there! How can I help you?"

    chatbot = OpenAIChatbot(openai=openai,
                            initial_prompt=initial_prompt,
                            first_utterance=first_utterance)

    utterance = chatbot.start_session()

    while not chatbot.session_ended():
        print(Fore.BLUE + utterance + Style.RESET_ALL)
        response = input(Fore.MAGENTA + "Your input -> " + Fore.YELLOW)
        utterance = chatbot.send_response(response)

    print(Fore.BLUE + utterance + Style.RESET_ALL)
