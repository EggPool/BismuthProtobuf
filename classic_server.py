# A stripped down Bismuth node server - For connection benchmark only
# Classic protocol version

import json,time
import socketserver,socks,threading
import connections

version_allow="mainnet0014,mainnet0015,mainnet0016,mainnet0017"

class ThreadedTCPRequestHandler_legacy(socketserver.BaseRequestHandler):
	"""Handle connections the old way, no comhandler abstraction"""
	
	def handle(self):
		peer_ip = self.request.getpeername()[0]
		while True:
			try:
				# Failsafe
				if self.request == -1:
					raise ValueError("Inbound: Closed socket from {}".format(peer_ip))
					return

				data = connections.receive(self.request, 10)

				print("Server: Received: {} from {}".format(data, peer_ip))  # will add custom ports later

				if data == 'version':
					data = connections.receive(self.request, 10)
					if data not in version_allow:
						print("Protocol version mismatch: {}, should be {}".format(data, version_allow))
						connections.send(self.request, "notok", 10)
						return
					else:
						print("Inbound: Protocol version matched: {}".format(data))
						connections.send(self.request, "ok", 10)
			except Exception as e:
				print(peer_ip,e)
				return



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

if __name__ == "__main__":
	try:
		HOST, PORT = "0.0.0.0", 6568

		ThreadedTCPServer.allow_reuse_address = True
		ThreadedTCPServer.daemon_threads = True
		ThreadedTCPServer.timeout = 65
		ThreadedTCPServer.request_queue_size = 10 # lower than on production node.

		server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler_legacy)
		ip, port = server.server_address

		server_thread = threading.Thread(target=server.serve_forever)
		# Exit the server thread when the main thread terminates
		server_thread.daemon = True
		server_thread.start()
		print("Server thread running.")

		while True:
			time.sleep(1)

		server.shutdown()
		server.server_close()
	except Exception as e:
		print(e)
