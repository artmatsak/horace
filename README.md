# GRACE: GPT Reprogrammable Assistant with Code Execution

**Important:** The war in Ukraine is still ongoing. Every day, Russian soldiers rape, murder, torture and deport Ukrainian civilians. Visit [this page](https://war.ukraine.ua/support-ukraine/) to see how you can support Ukraine today.

GRACE leverages GPT-3 to implement a human-like chatbot that's capable of retrieving information from a knowledge base and processing the customers' requests via an API backend. Learn more in the [announcement blog post](https://artmatsak.com/post/grace/).

## Installation

Clone this repository and `cd` to it:

```
cd grace
```

Create a Python virtual environment:

```
python3 -m venv ./venv
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

The default configuration implements an AI assistant for an imaginary restaurant in Cupertino. The assistant can help you manage a table reservation as well as answer questions about the restaurant (try asking it about gluten-free menu options, for example). Feel free to throw curveballs at it!

## Running Tests

A couple of tests are implemented for illustration purposes. The tests use another chatbot to play the role of the human counterpart to GRACE. Use this command to run them:

```
pytest -s
```

## Chatbot Customization

To adapt the bot for your use case, take a look at `backend.py` and `domain.yaml`.

* `backend.py` implements the Python API that defines the types of customer requests that the bot can process, such as booking a table.
* `domain.yaml` provides basic business information, adds any extra instructions for the chatbot, as well as includes the FAQ/knowledge base with answers to questions about your business.

Check out the code and comments in those two files to see how you can customize the chatbot.
