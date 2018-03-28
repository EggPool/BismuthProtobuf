# Command Handler
# Abstraction for the socket connection dialog

import struct,socks, time, json
import commands_pb2

#
TOR_TIMEOUT = 5

# Logical timeout
LTIMEOUT = 45
# Fixed header length for legacy protocol
SLEN = 10

# Index for stats 
STATS_COSINCE = 0
STATS_MSGSENT = 1
STATS_MSGRECV = 2
STATS_BYTSENT = 3
STATS_BYTRECV = 4

VER_LEGACY = 1
VER_PROTO = 2

class Connection:
	"""The connection layer, protocol independant"""
	# version 1 = json over sockets
	# version 2 = protobuff over sockets
	# version -1 : autodetect on first message
	version = VER_LEGACY
	socket = None
	logstats = True
	peer_ip = ''
	connected = False
	# first 4 bytes allow to ID the protocol version
	first_bytes = []
	# connection stats
	stats = [0,0,0,0,0]
	# cmd : from us to peer
	protocmd = None
	# msg : from peer to us
	protomsg = None
	
	def __init__(self, version=-1, socket = None, logstats= True):
		""" Default version is -1, will auto detect if needed on first receive
		Socket may be provided when in the context of a threaded TCP Server.
		"""
		self.version = version
		self.protocmd = commands_pb2.Command()
		self.protomsg = commands_pb2.Command()
		self.logstats = logstats
		self.socket = socket
		if socket:
			self.connected = True
			self.peer_ip = socket.getpeername()[0]
			if logstats:
				self.stats[STATS_COSINCE] = time.time()

	def status(self):
		"""Returns a status as a dict"""
		status={"version":self.version,"connected":self.connected,"peer_ip":self.peer_ip,"stats":self.stats}
		return status
		
	def connect(self,host='127.0.0.1',port=6568,timeout=LTIMEOUT,tor=False):
		"""
		Initiate connection to the given host, 
		"""
		self.socket = socks.socksocket()
		self.socket.settimeout(timeout)
		if tor:
			self.socket.settimeout(TOR_TIMEOUT)
			self.socket.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
		self.socket.connect((host, port))
		if self.socket:
			self.connected = True
			self.peer_ip = host
			if self.logstats:
				self.stats[STATS_COSINCE] = time.time()
				
	def send_precheck(self):
		"""Checks if we are connected"""
		if not self.connected:
			raise ValueError("Not connected")
		if self.version < 0:
			raise ValueError("Version not set")
		if self.logstats:
			self.stats[STATS_MSGSENT] += 1

	def get_precheck(self,need_version=True):
		"""Checks if we are connected and protocol version is set"""
		if not self.connected:
			raise ValueError("Not connected")
		if need_version and self.version < 0:
			raise ValueError("Version not set")


	def _get_legacy_message(self,header=None):
		if header == None:
			header=self.socket.recv(SLEN)
		if len(header) != SLEN:
			raise RuntimeError("Socket EOF")
		size=int(header)
		if self.logstats:
			self.stats[STATS_MSGRECV] += 1
		print("Legacy Size",size)
		chunks = []
		bytes_recd = 0
		while bytes_recd < size:
			chunk = self.socket.recv(min(size - bytes_recd, 2048))
			if not chunk:
				raise RuntimeError("Socket EOF2")
			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)            
		segments = b''.join(chunks).decode("utf-8")
		if self.logstats:
			self.stats[STATS_BYTRECV] += SLEN+size
		data = json.loads(segments)
		print("Legacy got",data)
		return data


	def _legacy_to_proto(self,data):
		"""Converts legacy string message to protobuff.
		Fetches more data from the socket if needed for that message."""
		self.protomsg.Clear()
		# TODO : make that prettier (dict and generic processing?)
		if data == 'version':
			self.protomsg.command = commands_pb2.Command.version
			self.protomsg.string_value = self._get_legacy_message()
		if data == 'hello':
			self.protomsg.command = commands_pb2.Command.hello
		if data == 'ok':
			self.protomsg.command = commands_pb2.Command.ok
		if data == 'notok':
			self.protomsg.command = commands_pb2.Command.notok
		# TODO - other commands

	def _proto_to_legacy(self):
		"""Converts a protobuf item into an array of json legacy message"""
		data=''
		# TODO : make that prettier (dict and generic processing?)
		if self.protocmd.command == commands_pb2.Command.ok:
			data= ['"ok"']
		elif self.protocmd.command == commands_pb2.Command.notok:
			data= ['"notok"']
		elif self.protocmd.command == commands_pb2.Command.hello:
			data= ['"hello"']
		elif self.protocmd.command == commands_pb2.Command.version:
			data= ['"version"',json.dumps(self.protocmd.string_value)]
		else:
			raise ValueError("Unknown command to convert",self.protocmd.__str__())
		return data


	def _get_legacy(self,header=None):
		data = self._get_legacy_message(header)
		# TODO : encode as protomsg
		self._legacy_to_proto(data)

	def _send_legacy(self):
		datas = self._proto_to_legacy()
		print("converted data to send",datas)
		for data in datas:
			#load = str(json.dumps(data)) # already encoded
			self.socket.sendall(str(len(data)).encode("utf-8").zfill(SLEN)+str(data).encode("utf-8"))
			if self.logstats:
				self.stats[STATS_BYTSENT] += SLEN+len(data)


	def _send_proto(self):
		"""Sends our protobuf command """
		data = self.protocmd.SerializeToString()
		data_len = len(data)
		self.socket.sendall(struct.pack('>i', data_len)+data)
		if self.logstats:
			self.stats[STATS_BYTSENT] += 4+data_len

	def _get_proto(self,header=None):
		if header == None:
			header=self.socket.recv(4)
		if len(header) < 4:
			raise RuntimeError("Socket EOF")
		size=struct.unpack('>i', header[:4])[0]
		if self.logstats:
			self.stats[STATS_MSGRECV] += 1
		data=self.socket.recv(size)
		self.protomsg.ParseFromString(data)
		if self.logstats:
			self.stats[STATS_BYTRECV] += 4+size

	def init_client(self):
		"""Call once for a new inbound client. Will ID the protocol and Handle the Communication start
		   The socket has to be new, nothing processed yet"""
		self.get_precheck(False) # we do not know the version yet, only check it's connected
		self.first_bytes=self.socket.recv(4)
		if len(self.first_bytes) < 4:
			raise RuntimeError("Socket EOF")
		if self.first_bytes == b'0000':
			# This is legacy proto
			self.version = VER_LEGACY
			self.first_bytes += self.socket.recv(6) # Get the rest of the header
			self._get_legacy(self.first_bytes)
		else:
			# protobuf
			self.version = VER_PROTO
			self._get_proto(self.first_bytes)
		return self.protomsg

	def _send(self):
		# TODO : decorator to avoid send_precheck() everywhere?
		self.send_precheck()
		if self.version == VER_LEGACY:
			self._send_legacy()
		else:
			self._send_proto()

	def send_void(self,cmd):
		"""sends a command without param"""
		self.protocmd.Clear()
		self.protocmd.command = cmd
		self._send()

	def send_string(self,cmd,value):
		"""sends a command with string param"""
		self.protocmd.Clear()
		self.protocmd.command = cmd
		self.protocmd.string_value = value
		self._send()

		
	def get_message(self):
		"""returns a full message from a peer"""
		self.get_precheck()
		if self.version == VER_LEGACY:
			self._get_legacy()
		else:
			self._get_proto()
		return self.protomsg
	"""
	def send_notok():
		self.protocmd.Clear()
		self.protomsg.command = commands_pb2.Command.notok
		self._send()

	def send_notok():
		self.protocmd.Clear()
		self.protomsg.command = commands_pb2.Command.ok
		self._send()
	"""

	"""
	def send_version(self,version):
		#Sends our version, communication starter
		self.send_precheck()
		if self.version == 1:
			len = connections.send(self.socket, "version", 10)
			len += connections.send(self.socket, version, 10)
			if logstats:
				self.stats[STATS_BYTSENT] += len
		else:
			self.protocmd.command =  commands_pb2.Command.version
			self.protocmd.string_value = version
			self._send_proto() # Will take care of updating stats

	def get_string_message(self):
		#returns the expected string answer
		self.get_precheck()
		if self.version == 1:
			data = connections.receive(s, 10)
			if logstats:
				self.stats[STATS_BYTRECV] += len(data)+2+10 # 10 for header + 2 for json encode (est.)
		else:
			rawdata = self._get_proto()
			self.protomsg.ParseFromString(rawdata)
			data = self.protomsg.string_value
		return data
	"""
