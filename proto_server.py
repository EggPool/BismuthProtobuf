# A stripped down Bismuth node server - For connection benchmark only
# Protobuf protocol version

import json,time
import socketserver,socks,threading
#import connections
import comhandler
import commands_pb2

version_allow="mainnet0014,mainnet0015,mainnet0016,mainnet0017"

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
	"""Handle connections with comhandler abstraction"""
	
	def handle(self):
		peer_ip = self.request.getpeername()[0]
		
		handler = comhandler.Connection(socket=self.request)
		print("Handler",handler.status())
		
		print("Init Client")
		message = handler.init_client();
		print("Handler",handler.status())
		print(message.__str__())
		if message.command != commands_pb2.Command.version :
			print("Version needed")
			self.request.close()
			return
			
		if  message.string_value in version_allow:
			print("Protocol version matched: {}".format(message.string_value))
			handler.send_void(commands_pb2.Command.ok)
		else:
			print("Protocol version mismatch: {}, should be {}".format(message.string_value, version_allow))
			self.request.close()
			handler.send_void(commands_pb2.Command.notok)
			return

		print("Handler",handler.status())

		while True:
			try:
				# Failsafe
				if self.request == -1:
					raise ValueError("Inbound: Closed socket from {}".format(peer_ip))
					return
				
				message = handler.get_message()
				print("Got message",message.__str__())
				print("Handler",handler.status())
				
				"""

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
				"""
			except Exception as e:
				print(peer_ip,e)
				return



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass

if __name__ == "__main__":
	try:
		HOST, PORT = "0.0.0.0", 6569

		ThreadedTCPServer.allow_reuse_address = True
		ThreadedTCPServer.daemon_threads = True
		ThreadedTCPServer.timeout = 65
		ThreadedTCPServer.request_queue_size = 10 # lower than on production node.

		server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
		ip, port = server.server_address

		server_thread = threading.Thread(target=server.serve_forever)
		# Exit the server thread when the main thread terminates
		server_thread.daemon = True
		server_thread.start()
		print("Server thread running on port {}.".format(PORT))

		while True:
			time.sleep(1)

		server.shutdown()
		server.server_close()
	except Exception as e:
		print(e)
