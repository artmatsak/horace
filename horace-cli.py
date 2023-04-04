# import argparse
import json
import asyncio
import websockets
from aioconsole import ainput
from colorama import Fore, Style


STATE_LISTENING = "listening"
STATE_REPLYING = "replying"
STATE_ENDED = "ended"


async def client(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            utterance = await ainput(Fore.MAGENTA + "Your input -> " + Fore.YELLOW)
            await websocket.send(json.dumps({"type": "utterance", "text": utterance.strip()}))

            while True:
                message = await websocket.recv()
                event = json.loads(message)

                if event["type"] == "state":
                    if event["state"] == STATE_LISTENING:
                        break
                    elif event["state"] == STATE_ENDED:
                        return
                elif event["type"] == "utterance":
                    print((Fore.GREEN if event["source"] == "system" else Fore.BLUE) +
                          event["text"] + Style.RESET_ALL)


if __name__ == '__main__':
    asyncio.run(client("ws://localhost:8001/"))
