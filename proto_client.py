# A stripped down Bismuth node client - For connection benchmark only
# Protobuf protocol version with abstraction layer

import json,time
import socketserver,socks,threading
import comhandler
import commands_pb2

version="mainnet0016"

HOST = "127.0.0.1"
#PORT = 6568 #6568 for legacy protocol, 6569 is the server running the protobuff protocol
PORT = 6569

# This client can talk to both
#PROTOCOL_VERSION = comhandler.VER_LEGACY
PROTOCOL_VERSION = comhandler.VER_PROTO


if __name__ == "__main__":

	handler = comhandler.Connection(version=PROTOCOL_VERSION)
	print("Handler",handler.status())

	
	try:
		print("Connecting to",HOST,PORT)

		handler.connect(HOST, PORT)
		print("Handler",handler.status())
		# communication starter

		#connections.send(s, "version", 10)
		#connections.send(s, version, 10)
		handler.send_string(commands_pb2.Command.version,version)
		print("Handler",handler.status())

		#data = connections.receive(s, 10)
		message = handler.get_message()
		print("Got message",message.__str__())
		print("Handler",handler.status())

		if (message.command == commands_pb2.Command.ok):
			print("Outbound: Node protocol version of {} matches our client".format(HOST))
		else:
			raise ValueError("Outbound: Node protocol version of {} mismatch".format(HOST))


		print("Sending Hello")
		#connections.send(s, "hello", 10)
		handler.send_void(commands_pb2.Command.hello)
		# communication starter
		print("Handler",handler.status())

		print("Sleep 10s and close")
		time.sleep(10)

	except Exception as e:
		print("Could not connect to {}: {}".format(HOST+':'+str(PORT), e))
