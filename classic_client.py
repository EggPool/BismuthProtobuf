# A stripped down Bismuth node client - For connection benchmark only
# Classic protocol version

import json,time
import socketserver,socks,threading
import connections

version="mainnet0016"

HOST = "127.0.0.1"
PORT = 6568 #6568 for legacy protocol, 6569 is the server running the protobuff protocol
PORT = 6569



if __name__ == "__main__":
	try:
		s = socks.socksocket()
		s.connect((HOST, PORT))
		print("Client: Connected to ",HOST,PORT)

		# communication starter

		connections.send(s, "version", 10)
		connections.send(s, version, 10)

		data = connections.receive(s, 10)

		if (data == "ok"):
			print("Outbound: Node protocol version of {} matches our client".format(HOST))
		else:
			raise ValueError("Outbound: Node protocol version of {} mismatch".format(HOST))

		print("Sending Hello")
		connections.send(s, "hello", 10)
		# communication starter
		
		print("Sleep 10s and close")
		time.sleep(10)

	except Exception as e:
		print("Could not connect to {}: {}".format(HOST+':'+str(PORT), e))
