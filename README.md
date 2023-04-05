# Horace: LLM Chatbot Server with ChatGPT Plugins

**Important:** The war in Ukraine is still ongoing. Every day, Russian soldiers rape, murder, torture and deport Ukrainian civilians. Visit [this page](https://war.ukraine.ua/support-ukraine/) to see how you can support Ukraine today.

Horace lets you implement a custom chatbot with your choice of an LLM and a set of ChatGPT plugins. It runs as a WebSocket server, allowing you to easily add an LLM-powered chatbot to your web or mobile app.

Features:

* WebSocket chatbot server
* Docker-friendly
* Sample web and CLI clients provided
* Pluggable LLM backends (currently OpenAI API with ChatGPT or GPT-4)
* Out-of-the-box support for ChatGPT plugins
* ChatGPT plugin auth methods supported: `none`, `user_http`, `service_http`
* Request validation for the plugins according to their OpenAPI specifications
* Prompt customization for fine-grained instructions.

Horace builds upon and extends [GRACE](https://github.com/artmatsak/grace), my original LLM-powered chatbot. Here is Horace running in debug mode with the Klarna ChatGPT plugin, accessed via a web client:

<div align="center">
  <video src="https://user-images.githubusercontent.com/5328078/230124595-203b4316-e5f8-4d6b-b0b8-b3d0d6609756.mp4" />
</div>

## Quick Start

1. Install Python 3.10, if not already installed.
2. Clone this repository.
3. Navigate to the cloned repository directory: `cd horace`
4. Create a new virtual environment: `python3 -m venv ./venv`
5. Activate the virtual environment: `source ./venv/bin/activate`
6. Install project requirements: `pip3 install -r requirements.txt`
7. Navigate to the `app` directory: `cd app`
8. Start the server: `OPENAI_API_KEY=openai-api-key python3 main.py` (replace `openai-api-key` with your OpenAI API key - get it [here](https://platform.openai.com/signup))
9. Launch a client:
  * For the CLI client, run this in another terminal window:
```
cd horace
source ./venv/bin/activate
python3 app/horace-cli.py
```
  * For the web client, double-click `client-demo/index.html` in Explorer/Finder etc. to open it in your browser.

## Running via Docker

1. Clone this repository.
2. Navigate to the cloned repository directory: `cd horace`
3. Build the Docker image: `docker build -t horace:latest .`
4. Start the server:
```
docker run --rm \
  -e OPENAI_API_KEY=openai-api-key \
  -p 8001:8001 \
  --name horace \
  horace:latest
```
5. Launch a client:
  * For the CLI client, run this in another terminal window: `docker exec -it horace python3 /app/horace-cli.py`
  * For the web client, double-click `client-demo/index.html` in Explorer/Finder etc. to open it in your browser.

## Command-Line Arguments

`main.py` and `horace-cli.py` support a few command-line arguments:

```
python3 main.py --help
usage: main.py [-h] [--host HOST] [--port PORT] [--debug]

optional arguments:
  -h, --help   show this help message and exit
  --host HOST  bind host name
  --port PORT  bind port number
  --debug      enable debug mode
```
```
python3 app/horace-cli.py --help
usage: horace-cli.py [-h] [--host HOST] [--port PORT]

optional arguments:
  -h, --help   show this help message and exit
  --host HOST  server host name
  --port PORT  server port number
```

## Working with the LLM Backends

At the moment, only the OpenAI API backend is supported. (I am not aware of non-OpenAI LLMs with a level of instruction-following sufficient for plugin invocation right now.) However, adding a custom LLM backend with Horace is quite straightforward:

1. Inherit a new backend class from the `Backend` base located in `backends/backend.py` and implement the `complete()` method
2. Place the new class module in the `backends` directory
3. Add an import of the new module to `main.py`
4. Adjust the `BACKENDS` mapping in `main.py` to include your new backend's alias and class name
5. Switch to the new backend in `config.yaml`:

```
backend:
  name: my_llm_backend
```

Refer to the OpenAI API backend (`backends/openai_backend.py`) as an example.

### Model Switching with the OpenAI API Backend

The OpenAI API backend lets you switch between the following models:

* ChatGPT (default): A cheap-to-access model that works reasonably well.
* GPT-4: Much more expensive than ChatGPT but should be more bullet-proof.

See `config.yaml` for switching between the OpenAI API models.

## Using ChatGPT Plugins

Horace works with ChatGPT plugins out of the box. To enable a plugin, add its hostname with an optional port number to the `plugins` section in `config.yaml`:

```
router:
  plugins:
    # For https://github.com/artmatsak/chatgpt-todo-plugin/
    # - localhost:5002
    - www.klarna.com
```

Upon starting, the server requests `http://[hostname]/.well-known/ai-plugin.json` for each plugin and takes it from there to load them.

Horace currently supports the `none`, `user_http` and `server_http` auth methods for ChatGPT plugins. If an auth token is required for a plugin, Horace asks you for one during server startup. At the moment, auth tokens are saved unencrypted in `.plugin_auth.json`.

## Providing Extra Prompt Instructions

The default LLM prompt for Horace is designed to make the bot neutral. The bot is neither limited to plugin-facilitated user requests (like a restaurant booking bot would be, for example), nor does it proactively push the plugin-enabled functionality onto the user. In other words, you can chat with the bot like you normally would with ChatGPT; if the bot feels that invoking a plugin method is needed, it will do so.

In real-world scenarios, you may want to limit the bot to a particular scope like booking a table (see [GRACE's prompt](https://github.com/artmatsak/grace/blob/master/grace_chatbot.py#L11) for inspiration), or perhaps provide it with a unique voice/personality. To do this, you can add instructions to the LLM prompt using the `extra_instructions` property in `config.yaml`:

```
horace:
  # Any extra instructions to prepend the prompt with
  extra_instructions: >-
    You are a helpful and polite AI assistant.
  # extra_instructions: >-
  #   In your speech, you impersonate Jedi Master Yoda and crack jokes in response
  #   to mentions of other Star Wars characters.
```

Try uncommenting the Yoda block above to see how the voice of the chatbot changes accordingly. (Don't forget to restart the server after making any changes to the config.)

## Running Tests

Tests have not yet been updated since forking from GRACE. To be fixed.
