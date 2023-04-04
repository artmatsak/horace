import argparse
import json
import asyncio
import websockets
from urllib.parse import urlunsplit
from aioconsole import ainput, aprint
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
                    await aprint((Fore.GREEN if event["source"] == "system" else Fore.BLUE) +
                                 event["text"] + Style.RESET_ALL)
                elif event["type"] == "error":
                    await aprint(Fore.CYAN +
                                 f'Server error: {event["message"]}' + Style.RESET_ALL)
                    break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='server host name', default='0.0.0.0')
    parser.add_argument('--port', help='server port number', default=8001)
    args = parser.parse_args()

    url = urlunsplit(('ws', f'{args.host}:{args.port}', '/', '', ''))
    asyncio.run(client(url))
