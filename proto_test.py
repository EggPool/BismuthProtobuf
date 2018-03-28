
import time,json
import ipaddress
import commands_pb2

bcommand = commands_pb2.Command()
bcommand.command = commands_pb2.Command.sendsync

# Simple command
serial = bcommand.SerializeToString()
print("sendsync",len(serial),serial)

# List of ips (peers)
test_ip="127.0.0.1"
bcommand.command = commands_pb2.Command.peers
ip=bcommand.ips.add()
ip.ipv4=int(ipaddress.ip_address(test_ip))
serial = bcommand.SerializeToString()
print("ipv4",len(serial),serial)

ip.port=6060
serial = bcommand.SerializeToString()
print("ipv4+port",len(serial),serial)

bcommand = commands_pb2.Command()
bcommand.command = commands_pb2.Command.peers
for i in range(100):
	ip=bcommand.ips.add()
	ip.ipv4=int(ipaddress.ip_address('127.0.0.'+str(i)))
serial = bcommand.SerializeToString()
print("100 ipv4",len(serial),serial)


ROUNDS = 100000
bcommand = commands_pb2.Command()
bcommand.command = commands_pb2.Command.sendsync
start = time.time()
for i in range(ROUNDS):
	serial = bcommand.SerializeToString()
print("protoE",time.time()-start)
start = time.time()
for i in range(ROUNDS):
	bcommand.ParseFromString(serial)
print("protoD",time.time()-start)

start = time.time()
data="sendsync"
for i in range(ROUNDS):
	serial = str(json.dumps(data)).encode("utf-8")
print("jsonE",time.time()-start)
start = time.time()
for i in range(ROUNDS):
	test = json.loads(serial.decode("utf-8"))
print("jsonD",time.time()-start)
