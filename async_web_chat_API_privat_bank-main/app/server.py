import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from exchange import GetExchage


logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def send_exchange_rate(self, name, exchrt):
        result = await exchrt.get_exchange()
        await self.send_to_clients(f"Exchange rate for: {name}")
        await self.send_to_clients(f"{result}")

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.lstrip().startswith("exchange"):
                exchrt = GetExchage(message, ws.name)
                asyncio.create_task(self.send_exchange_rate(ws.name, exchrt))
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
