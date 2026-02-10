import argparse
import asyncio
import logging
import sys
from typing import AsyncIterator, NamedTuple, Sequence

import chat_pb2_grpc
import grpc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('test.log', mode='a'),
        logging.StreamHandler(sys.stdout),
    ],
)


class ChatMessage(NamedTuple):
    sender_id: int
    text: str


type RequestIterator = AsyncIterator[ChatMessage]
type Context = grpc.aio.ServicerContext[ChatMessage, ChatMessage]


class ChatServer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self, client_ids: Sequence[int]):
        self.client_ids = set(client_ids)
        self.clients = {}
        self.history = []
        self.lock = asyncio.Lock()

    async def chat(self, request_iterator: RequestIterator, context: Context):
        try:
            # Convention: The first message from the client is used to identify itself
            first_msg = await anext(request_iterator)
            client_id = first_msg.sender_id
        except StopAsyncIteration:
            logging.warning(
                '[SERVER] Client disconnected before sending identity message.'
            )
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                'Missing initial identity message.',
            )

        # Not in the allowed client group, reject connection
        if client_id not in self.client_ids:
            logging.warning(
                f'[SERVER] Connection attempt from unauthorized client {client_id}.'
            )
            await context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                f'Client {client_id} not in allowed client group.',
            )

        queue = asyncio.Queue()

        async with self.lock:
            if client_id in self.clients:
                logging.warning(
                    f'[SERVER] Client {client_id} already connected. Rejecting new connection.'
                )
                await context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    f'Client {client_id} already connected.',
                )
            self.clients[client_id] = queue

        logging.info(f'[SERVER] Client {client_id} connected.')

        # Send all previous messages to the new client, except those sent by itself
        for old_msg in self.history:
            if old_msg.sender_id != client_id:
                await queue.put(old_msg)

        async def receive():
            try:
                async for msg in request_iterator:
                    logging.info(f'[SERVER] Client {msg.sender_id}: {msg.text}')

                    # Save the message to history buffer
                    self.history.append(msg)

                    targets = []
                    async with self.lock:
                        for cid, q in self.clients.items():
                            if cid != msg.sender_id:
                                targets.append(q)

                    for q in targets:
                        await q.put(msg)

            except asyncio.CancelledError:
                pass

        recv_task = asyncio.create_task(receive())

        try:
            while True:
                msg = await queue.get()
                yield msg
        except asyncio.CancelledError:
            pass
        finally:
            recv_task.cancel()
            async with self.lock:
                self.clients.pop(client_id, None)
            logging.info(f'[SERVER] Client {client_id} disconnected.')


async def serve(port: int, client_ids: Sequence[int]):
    server = grpc.aio.server()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServer(client_ids), server)
    server.add_insecure_port(f'127.0.0.1:{port}')
    await server.start()
    logging.info(f'[SERVER] Started on port {port} with clients {client_ids}.')
    await server.wait_for_termination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-client_ids', required=True)
    parser.add_argument('-port', type=int, required=True)
    args = parser.parse_args()

    client_ids = list(map(int, args.client_ids.split(',')))
    asyncio.run(serve(args.port, client_ids))
