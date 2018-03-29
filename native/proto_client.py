# A stripped down Bismuth node client - For connection benchmark only
# Protobuf protocol version with abstraction layer

import time

# Our modules
import comhandler
import commands_pb2

version = "posnet0001"

HOST = "127.0.0.1"
# 6969 may be temporary
PORT = 6969


if __name__ == "__main__":
    handler = comhandler.Connection()
    print("Handler", handler.status())
    try:
        print("Connecting to", HOST, PORT)
        handler.connect(HOST, PORT)
        print("Handler", handler.status())
        # communication starter
        print("Sending version")
        handler.send_string(commands_pb2.Command.version, version)
        print("Handler", handler.status())
        message = handler.get_message()
        print("Got message", message.__str__())
        print("Handler", handler.status())
        if message.command == commands_pb2.Command.ok:
            print("Outbound: Node protocol version of {} matches our client".format(HOST))
        else:
            raise ValueError("Outbound: Node protocol version of {} mismatch".format(HOST))
        print("Sending Hello")
        handler.send_void(commands_pb2.Command.hello)
        print("Handler", handler.status())
        print("Sleep 10s and close")
        time.sleep(10)
    except Exception as e:
        print("Could not connect to {}: {}".format(HOST+':'+str(PORT), e))
