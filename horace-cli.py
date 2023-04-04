# import argparse
import asyncio
import websockets
from colorama import Fore, Style


async def client(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            response = input(
                Fore.MAGENTA + "Your input -> " + Fore.YELLOW).strip()

            await websocket.send(response)

            utterance = await websocket.recv()

            # print((Fore.GREEN if is_router_result else Fore.BLUE) +
            #       utterance + Style.RESET_ALL)
            print(Fore.BLUE + utterance + Style.RESET_ALL)


if __name__ == '__main__':
    asyncio.run(client("ws://localhost:8001/"))
