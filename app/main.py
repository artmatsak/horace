import argparse
import json
import asyncio
import websockets
from pyaml_env import parse_config
import logging
from backends.openai_backend import OpenAIBackend
from router import Router
from horace_chatbot import HoraceChatbot
from typing import Dict, Any


BACKENDS = {
    "openai": OpenAIBackend
}


def get_handler(config: Dict[str, Any], router: Router, debug_mode: bool = False):
    async def handler(websocket):
        async def send_state(state: str):
            await websocket.send(json.dumps({"type": "state", "state": state}))

        async def send_utterance(utterance: str, is_system: bool = False):
            source = "system" if is_system else "ai"
            await websocket.send(json.dumps({"type": "utterance", "source": source, "text": utterance}))

        chatbot = HoraceChatbot(
            backend=BACKENDS[config["backend"]["name"]](
                **config["backend"]["params"]),
            router=router,
            utterance_coroutine=send_utterance,
            state_coroutine=send_state,
            extra_instructions=config.get("extra_instructions"),
            debug_mode=debug_mode
        )

        async for message in websocket:
            try:
                event = json.loads(message)

                if event["type"] == "utterance":
                    await chatbot.send_responses([event["text"]])
            except Exception as e:
                message = f'{type(e).__name__}: {e}'
                await websocket.send(json.dumps({"type": "error", "message": message}))

            if chatbot.state == chatbot.STATE_ENDED:
                break

    return handler


async def main(handler, host, port):
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)

    # Increase log level for OpenAI API
    openai_logger = logging.getLogger("openai")
    openai_logger.setLevel(logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='bind host name', default='0.0.0.0')
    parser.add_argument('--port', help='bind port number', default=8001)
    parser.add_argument('--debug', action='store_true',
                        help='enable debug mode')
    args = parser.parse_args()

    config = parse_config("config.yaml")
    router = Router(plugins=config.get("plugins"))
    handler = get_handler(config, router, args.debug)

    asyncio.run(main(handler, args.host, args.port))
