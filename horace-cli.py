# import argparse
import json
import asyncio
import websockets
from colorama import Fore, Style


STATE_LISTENING = "listening"
STATE_REPLYING = "replying"
STATE_ENDED = "ended"


async def client(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            utterance = input(
                Fore.MAGENTA + "Your input -> " + Fore.YELLOW).strip()

            await websocket.send(json.dumps({"type": "utterance", "text": utterance}))

            while True:
                message = await websocket.recv()
                event = json.loads(message)

                if event["type"] == "state":
                    if event["state"] == STATE_LISTENING:
                        break
                    elif event["state"] == STATE_ENDED:
                        return
                elif event["type"] == "utterance":
                    # print((Fore.GREEN if is_router_result else Fore.BLUE) +
                    #       utterance + Style.RESET_ALL)
                    print(Fore.BLUE + event["text"] + Style.RESET_ALL)


if __name__ == '__main__':
    asyncio.run(client("ws://localhost:8001/"))
