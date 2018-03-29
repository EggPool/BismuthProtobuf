# A stripped down Bismuth node server - For connection benchmark only
# Protobuf protocol version

import time
import socketserver
import threading

# Our modules
import comhandler
import commands_pb2

version_allow = 'posnet0001,posnet0002'
PORT = 6969


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Handle connections with comhandler abstraction"""

    def handle(self):
        peer_ip = self.request.getpeername()[0]
        handler = comhandler.Connection(socket=self.request)
        print("Handler", handler.status())
        print("Init Client")
        message = handler.init_client()
        print("Handler", handler.status())
        print(message.__str__())
        if message.command != commands_pb2.Command.version:
            print("Version needed")
            self.request.close()
            return
        if message.string_value in version_allow:
            print("Protocol version matched: {}".format(message.string_value))
            handler.send_void(commands_pb2.Command.ok)
        else:
            print("Protocol version mismatch: {}, should be {}".format(message.string_value, version_allow))
            self.request.close()
            handler.send_void(commands_pb2.Command.notok)
            return
        print("Handler", handler.status())
        while True:
            try:
                # Failsafe
                if self.request == -1:
                    raise ValueError("Inbound: Closed socket from {}".format(peer_ip))
                message = handler.get_message()
                print("Got message", message.__str__())
                print("Handler", handler.status())
            except Exception as e:
                print("Error >{}< for {}.".format(e, peer_ip))
                return


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    global PORT
    server = None
    try:
        HOST = '0.0.0.0'

        ThreadedTCPServer.allow_reuse_address = True
        ThreadedTCPServer.daemon_threads = True
        ThreadedTCPServer.timeout = 65
        ThreadedTCPServer.request_queue_size = 10  # lower than on production node.

        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        ip, port = server.server_address

        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server thread running on port {}.".format(PORT))

        while True:
            time.sleep(1)

    except Exception as e:
        print(e)
        if server:
            server.shutdown()
            server.server_close()
