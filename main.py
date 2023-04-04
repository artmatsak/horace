import asyncio
import websockets
from pyaml_env import parse_config
import logging
from backends.openai_backend import OpenAIBackend
from router import Router
from horace_chatbot import HoraceChatbot
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()


BACKENDS = {
    "openai": OpenAIBackend
}


def get_handler(config: Dict[str, Any], router: Router):
    async def handler(websocket):
        async def send_utterance(utterance: str, is_router_result: bool = False):
            await websocket.send(utterance)

        chatbot = HoraceChatbot(
            backend=BACKENDS[config["backend"]["name"]](
                **config["backend"]["params"]),
            router=router,
            output_callback=send_utterance,
            extra_instructions=config.get("extra_instructions"),
            debug_mode=False
        )

        async for message in websocket:
            if not message:
                continue

            if not chatbot.is_session_active():
                await chatbot.start_session([message])
            else:
                await chatbot.send_responses([message])

            if not chatbot.is_session_active():
                break

    return handler


async def main(handler):
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                        encoding='utf-8', level=logging.DEBUG)

    # Increase log level for OpenAI API
    openai_logger = logging.getLogger("openai")
    openai_logger.setLevel(logging.ERROR)

    config = parse_config("config.yaml")
    router = Router(plugins=config.get("plugins"))
    handler = get_handler(config, router)

    asyncio.run(main(handler))
