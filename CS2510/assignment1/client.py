import argparse
import asyncio
import logging
import sys

import chat_pb2
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


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-client_id', type=int, required=True)
    parser.add_argument('-server_ip', required=True)
    parser.add_argument('-port', type=int, required=True)
    args = parser.parse_args()

    async with grpc.aio.insecure_channel(f'{args.server_ip}:{args.port}') as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)

        async def message_generator():
            # First message identifies the client
            yield chat_pb2.ChatMessage(sender_id=args.client_id, text='__join__')
            while True:
                msg = await asyncio.to_thread(input, '')
                yield chat_pb2.ChatMessage(sender_id=args.client_id, text=msg)

        try:
            async for msg in stub.chat(message_generator()):
                logging.info(
                    f'[CLIENT{args.client_id}] From client {msg.sender_id}: {msg.text}'
                )
        except grpc.aio.AioRpcError as e:
            logging.warning(
                f'[CLIENT{args.client_id}] RPC failed: {e.code().name}: {e.details()}'
            )
        except asyncio.CancelledError:
            logging.info(f'[CLIENT{args.client_id}] Stream closed normally.')


if __name__ == '__main__':
    asyncio.run(main())
