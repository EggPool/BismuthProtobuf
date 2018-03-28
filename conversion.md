# Conversion from old style "connections" to "comhandler"

See proto_client.py for an example of a very simple client (Communication starter only) using comhandler.  
This client can talk to both legacy and protobuf servers.  
- When talking to a protobuf server, the server auto detects the protocol and respond with the same.
- When talking to a legacy server, the server doesn't see any differecne from a legacy client.

## Import classes
```import comhandler
import commands_pb2```

## Define a handler instance

`handler = comhandler.Connection(version=PROTOCOL_VERSION)`

PROTOCOL_VERSION is one of
- `comhandler.VER_LEGACY`
- `comhandler.VER_PROTO`

The comhandler interface is protocol agnostic: no matter what it really sends and receice over the sockets (json or protobuf), what it exposes on our side is always a commands_pb2 instance, hence a structured object with properties validation and such.

## Simple commands

Sending a simple command (one message, no argument)

Oldstyle 
> `connections.send(s, "hello", 10)`

becomes
> `handler.send_void(commands_pb2.Command.hello)`

## Other commands

Sending a command with a string param

Oldstyle
> ```connections.send(s, "version", 10)
connections.send(s, version, 10)```

becomes
> `handler.send_string(commands_pb2.Command.version,version)`

## Receiving a message

Oldstyle
> `data = connections.receive(s, 10)`

becomes
> `message = handler.get_message()`

## Helpers

- `handler.status()` A Json output of the internal comhandler vars. Including stats: a list of [start_timestamp,MSGSENT,MSGRECV,BYTSENT,BYTRECV]
- `message.__str__()` Where message is a protobuf instance (commands_pb2 class) : a readable version of the protobuf
