# CS 2510 Assignment 1 Report

Project Name: Group RPC Communication System \
Completion Date: February 9, 2026 \
Author: jshn9515

## Overview

In this assignment, we implemented an asynchronous RPC-based group chat system using Python and gRPC. The system consists of one server and multiple clients. Clients connect to the server, send messages, and receive messages from other clients in the group. The server maintains message history and ensures that each client only receives unread messages, as specified in the assignment requirements.

The system uses asynchronous bidirectional streaming RPC to allow real-time communication between clients and the server.

## Design and Implementation

The server is implemented using `grpc.aio` and maintains three main data structures:

- `client_ids`: set of authorized client IDs
- `clients`: dictionary mapping client ID to message queue
- `history`: list storing all previous messages

Each connected client is assigned an `asyncio.Queue`, which stores unread messages. When a client sends a message, the server:

1. Stores the message in the history buffer
2. Forwards the message to all other connected clients
3. Does not send the message back to the sender

When a new client connects, the server sends all unread messages from the history buffer except those sent by the client itself.

Concurrency is handled using `asyncio.Lock` to ensure thread-safe access to shared data structures.

The client uses asynchronous streaming to both send and receive messages. It continuously reads user input and sends messages to the server, while simultaneously receiving messages from other clients.

## Testing

Two automated test cases were implemented.

Test 1 verifies delayed client connection. Alice sends a message before Bob and Chad connect. When Bob and Chad join later, they receive Alice’s message from the server history buffer.

Test 2 verifies real-time message broadcasting. Alice, Bob, and Chad are connected. Bob sends a message, and only Alice and Chad receive it. Alice sends a message, and only Bob and Chad receive it. An unauthorized client (Doug) attempts to connect and is rejected.

The [log file](test.log) from the tests is available.

## Possible Improvements

Several improvements could enhance the system:

- Persistent storage to prevent message loss after server restart
- Authentication to prevent client ID spoofing
- Multiple server support for fault tolerance
- Message encryption for security

## Conclusion

We successfully implemented an asynchronous RPC-based group communication system using gRPC and Python. The system supports concurrent clients, reliable message delivery, and unread message tracking. The asynchronous design ensures efficient and scalable communication.
