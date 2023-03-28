import os
import yaml
# import mocks.openai as openai
import openai
from openai_chatbot import OpenAIChatbot
from horace_chatbot import HoraceChatbot
from datetime import datetime
from dotenv import load_dotenv
import pytest

load_dotenv()

# Suppress the tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

openai.api_key = os.environ["OPENAI_API_KEY"]

with open("config.yaml", "r") as stream:
    config = yaml.safe_load(stream)
with open("domain.yaml", "r") as stream:
    domain = yaml.safe_load(stream)


@pytest.fixture
def customer_prompt_template() -> str:
    return """You are a customer of {business_name}, {business_description}. You are chatting to the restaurant's AI assistant. {{task_description}}

A transcript of your chat session with the AI assistant follows.
""".format(**domain)


def test_book_table(customer_prompt_template):
    backend.bookings = {}

    task_description = f"You are looking to book a table on the name of Jeremiah Biggs, for 3 people at 8 pm on June 23, 2023. You don't provide all of this information at once but rather respond to the AI assistant's prompts."
    customer_prompt = customer_prompt_template.format(
        task_description=task_description)

    _run_session(customer_prompt)

    assert list(backend.bookings.values()) == [{
        "full_name": "Jeremiah Biggs",
        "num_people": 3,
        "time": datetime(2023, 6, 23, 20, 0, 0)
    }]


def test_change_booking(customer_prompt_template):
    reference = "S8W308"

    backend.bookings = {
        reference: {
            "full_name": "Ann Hicks",
            "num_people": 4,
            "time": datetime(2023, 7, 14, 18, 0, 0)
        }
    }

    task_description = f"You'd like to change a table booking with reference {reference} that you made earlier. You're looking to change it from 4 people to 3 people and from 6 PM to 5:30 PM. You don't provide all of this information at once but rather respond to the AI assistant's prompts."
    customer_prompt = customer_prompt_template.format(
        task_description=task_description)

    _run_session(customer_prompt)

    assert list(backend.bookings.values()) == [{
        "full_name": "Ann Hicks",
        "num_people": 3,
        "time": datetime(2023, 7, 14, 17, 30, 0)
    }]


def test_cancel_booking(customer_prompt_template):
    reference = "ZBA4HB"

    backend.bookings = {
        reference: {
            "full_name": "Mary Ashcroft",
            "num_people": 5,
            "time": datetime(2023, 6, 2, 18, 15, 0)
        }
    }

    task_description = f"You are looking to cancel your booking with reference {reference}. The reference is all information you have about the booking."
    customer_prompt = customer_prompt_template.format(
        task_description=task_description)

    _run_session(customer_prompt)

    assert reference not in backend.bookings


def _run_session(customer_prompt: str):
    ai_utterances = []
    customer_utterances = []

    ai_chatbot = HoraceChatbot(
        openai=openai,
        backend=backend.backend,
        domain=domain,
        output_callback=lambda u: ai_utterances.append(u),
        openai_model=config["openai"]["model"],
        openai_endpoint=config["openai"]["endpoint"]
    )

    ai_chatbot.start_session()

    customer_prompt += "".join(["\nAI: " + u for u in ai_utterances])
    print(ai_utterances)
    ai_utterances = []

    customer_chatbot = OpenAIChatbot(
        openai=openai,
        initial_prompt=customer_prompt,
        output_callback=lambda u: customer_utterances.append(u),
        names=("Customer", "AI"),
        openai_model=config["openai"]["model"],
        openai_endpoint=config["openai"]["endpoint"]
    )

    customer_chatbot.start_session()

    while not ai_chatbot.session_ended():
        ai_chatbot.send_responses(customer_utterances)
        print(customer_utterances)
        customer_utterances = []

        customer_chatbot.send_responses(ai_utterances)
        print(ai_utterances)
        ai_utterances = []
