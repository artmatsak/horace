# GRACE: GPT Reprogrammable Assistant with Code Execution

**Important:** The war in Ukraine is still ongoing. Every day, Russian soldiers rape, murder, torture and deport Ukrainian civilians. Visit [this page](https://war.ukraine.ua/support-ukraine/) to see how you can support Ukraine today.

GRACE leverages the OpenAI API to implement a human-like chatbot that's capable of retrieving information from a knowledge base and processing the customers' requests via an API backend. It showcases how large language models can be made to interact with external systems for knowledge retrieval and performing actions in the real world. Learn more in the [announcement blog post](https://artmatsak.com/post/grace/).

**Update March 28, 2023:** Added support for GPT-4 in addition to ChatGPT and the default `text-davinci-003` model.

The default configuration implements an AI assistant for Death Star, an imaginary Star Wars-themed restaurant in Cupertino, CA. The assistant is instructed to impersonate Jedi Master Yoda.

Example interaction:

```
AI: Greetings, young Padawan! What can I do for you?
Customer: Hi Yoda, may the Force be with you! Is Darth Vader around?
AI: Not today, youngling. Would you like me to help you with something else?
Customer: Yes, what can you do?
AI: Of course, what is it that you seek? I can help you with making a reservation, changing an existing one, or canceling it. What can I do for you?
Customer: Do you have a table for 3 people tomorrow?
AI: Absolutely! What time would you like for the reservation?
Customer: 4:15 pm
AI: Good news, youngling - the table is available. Would you like to book it?
Customer: Yes sir!
AI: Very well, what is your full name?
Customer: Why do you need the name?
AI: I need your full name for the booking, to make sure that you are the rightful owner.
Customer: Ah, OK. It's Jeremy Biggs.
AI: The booking is confirmed and your reference is 7APZN6. Is there anything else I can do for you?
Customer: Just had a question, what's the parking situation at the restaurant?
AI: Excellent! Free parking is available on site and you can also park on the street (charges may apply). Is there anything else I can do for you?
Customer: Nope, that's it, thanks.
AI: It's been an honor serving you. May the Force be with you!
```

Unlike the GPT-3 and ChatGPT demos you might have seen so far, this is not just fantasy chitchat on the part of the bot. The bot actually executes backend commands to check table availability and make the booking, as well as to answer the customer's question about the parking. It also interprets the execution results and retranslates them to the customer.

## Installation

Clone this repository and `cd` to it:

```
cd grace
```

Create a Python virtual environment:

```
python3 -m venv ./venv
```

Activate the environment:

```
source ./venv/bin/activate
```

Install the required packages:

```
pip3 install -r requirements.txt
```

Copy `.env.example` to `.env`:

```
cp .env.example .env
```

Edit `.env` to set your OpenAI API key. You can obtain the key by signing up for OpenAI API [here](https://beta.openai.com/signup).

```
OPENAI_API_KEY=sk-...
```

## Running the Chatbot

Run the command below to start your interactive chat session. On the first run, the chatbot will download a semantic search model from Hugging Face Hub. This may take some time.

```
python3 main.py
```

The default assistant, impersonating Yoda, can help you manage a table reservation as well as answer questions about the imaginary restaurant it works for (try asking it about gluten-free menu options, for example). Feel free to throw curveballs at it!

## Running Tests

A couple of tests are implemented for illustration purposes. The tests employ another chatbot instance to play the role of the human counterpart to GRACE. Use this command to run them:

```
pytest -s
```

## Model Selection

In addition to the default `text-davinci-003` model, GRACE can also work with ChatGPT and GPT-4. See `config.yaml` for the details and example settings.

GPT-4 is the best, but also the most expensive. The default `text-davinci-003` is cheaper but still produces excellent results. ChatGPT is the cheapest but may suffer from a number of issues (hallucinations, failure to execute commands etc.)

## Chatbot Customization

To adapt the bot for your use case, take a look at `backend.py` and `domain.yaml`.

* `backend.py` implements the Python API that defines the types of customer requests that the bot can process, such as booking a table.
* `domain.yaml` provides basic business information, adds any extra instructions for the chatbot, as well as includes the FAQ/knowledge base with answers to questions about your business.

Check out the code and comments in those two files to see how you can customize the chatbot.
