# Bismuth Node Commands

commands_pb2.Command.*

## sendsync
id 0
no param

## version
id 1
string_value : the peer version (mainnet0016) 

## ok
id 2
no param
Inbound: Protocol version matched

## notok
id 3
no param
Inbound: Protocol version mismatch

## tx
id 4
TX : list of commands_pb2.Command.TX
One or several tx from the node mempool

## peers
id 5
IPS : list of ip and ports. commands_pb2.Command.IP
List of peers, with default port.
* maintain a bin version of that, in memory, within a protobuf, no need to convert each time

    sync = 4;
    blockscf = 5;
    blocksrj = 6;
    nonewblk = 7;
    blocksfnd = 8;
    message = 9;
    /*
    // The following will be "message" type : just an optional string
    Mempool_insert_finished = 8;
    Alias_free = 9;
    Alias_registered = 10;