#!/usr/bin/env python

import socket
import errno
from struct import pack, unpack
import base64

# Address and port to listen to MQTT messages
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 1883
# Address and port of the DTN daemon
DAEMON_ADDRESS = 'localhost'
DAEMON_PORT = 4550
# Demux token of this application, which will be concatenated with the DTN Endpoint identifier of the node
# where this script actually runs
SOURCE_DEMUX_TOKEN = 'sender'
# DTN Endpoint identifier of the destination application running on the node where the MQTT broker actually runs
DESTINATION_EID = 'dtn://otvm1/broker'


def decode_remaining_length(length_bytes):
    """
    Decode remaining message length according to MQTT specifications

    Args:
        length_bytes: Bytes containing the remaining length of the MQTT message encoded according to specifications

    Returns:
        a tuple containing the decoded remaining length and the number of bytes used by the encoded length (up to 4)
    """
    i = 0
    multiplier = 1
    value = 0
    while True:
        encoded_byte = length_bytes[i]
        i += 1
        int_byte = unpack('!B', encoded_byte)
        value += (int_byte[0] & 0x7f) * multiplier
        if (int_byte[0] & 0x80) == 0:
            break
        else:
            multiplier *= 128
            if multiplier > 128 * 128 * 128:
                # Remaining length field not encoded properly, return error value
                i = -1
                break
    return value, i


def parse_message(msg):
    """
    Parse a MQTT message received from a client and possibly reply with the appropriate response

    Args:
        msg: Bytes received from the MQTT client

    Returns:
        -2 if the first message received from the client isn't a CONNECT message
        -1 if the message is not in a known format and there is a parsing error
        0 if the message isn't complete and more bytes have to be read from client socket
        1 parsing finished
    """
    global unprocessed_buffer
    global current_raw_message

    current_raw_message += msg

    if new_message:
        packet_type = unpack('!B', current_raw_message[0])[0] & 0xF0
        if first_message and packet_type != 0x10:
            return -2
        elif not first_message and packet_type != 0x30 and packet_type != 0x60 and packet_type != 0xC0:
            return -1

    if len(current_raw_message) < 5:
        return 0

    remaining_bytes, n = decode_remaining_length(current_raw_message[1:5])
    # If remaining length field is not encoded properly, return parsing error
    if n == -1:
        return -1

    message_length = 1 + n + remaining_bytes

    if len(current_raw_message) < message_length:
        return 0
    elif len(current_raw_message) == message_length:
        unprocessed_buffer = ''
    else:
        unprocessed_buffer = current_raw_message[message_length:]
        current_raw_message = current_raw_message[:message_length]

    packet_type = unpack('!B', current_raw_message[0])[0] & 0xF0
    # CONNECT
    if packet_type == 0x10:
        print("CONNECT Received\n")
        # Send CONNACK
        c.send('\x20\x02\0\0')
    # PUBLISH
    elif packet_type == 0x30:
        qos = (unpack('!B', current_raw_message[0])[0] & 0x06) >> 1

        topic_length = unpack('!H', current_raw_message[1 + n:3 + n])[0]
        topic = current_raw_message[3 + n:3 + n + topic_length]

        # QoS = 0
        if qos == 0:
            payload = current_raw_message[3 + n + topic_length:]
            print("PUBLISH Received - Topic: %s; Message: %s\n" % (topic, payload))
            send_bundle(topic, payload)
        # QoS > 0
        else:
            packet_identifier = unpack('!H', current_raw_message[3 + n + topic_length:5 + n + topic_length])[0]
            payload = current_raw_message[5 + n + topic_length:]
            print("PUBLISH Received - Topic: %s; Message: %s; MID: %d\n" % (topic, payload, packet_identifier))
            send_bundle(topic, payload, qos, packet_identifier)
    # PUBREL
    elif packet_type == 0x60:
        packet_identifier = unpack('!H', current_raw_message[2:])[0]
        # Send PUBCOMP
        pubcomp = pack('!BBH', 112, 2, packet_identifier)
        c.send(pubcomp)
    # PINGREQ
    elif packet_type == 0xC0:
        print("PINGREQ Received\n")
        # Send PINGRESP
        c.send('\xD0\0')

    current_raw_message = ''
    return 1


def send_bundle(topic, message, qos=0, mid=0):
    """
    Create a bundle from a MQTT message and send it through IBR-DTN deamon

    Args:
        topic: The topic of the MQTT message
        message: The MQTT payload
        qos: QoS level of the MQTT message
        mid: Packet Identifier of the MQTT message
    """
    payload = "%s\n%s" % (topic, message)

    bundle = "Source: %s\n" % SOURCE_EID
    bundle += "Destination: %s\n" % DESTINATION_EID

    if qos == 0:
        bundle += "Processing flags: 148\n"
    elif qos > 0:
        bundle += "Processing flags: 156\n"

    bundle += "Blocks: 1\n\n"
    bundle += "Block: 1\n"
    bundle += "Flags: LAST_BLOCK\n"
    bundle += "Length: %d\n\n" % len(payload)
    bundle += "%s\n\n" % base64.b64encode(payload)

    d.send("bundle put plain\n")
    fd.readline()

    d.send(bundle)
    fd.readline()

    d.send("bundle send\n")
    fd.readline()

    if qos == 1:
        # Send PUBACK
        puback = pack('!BBH', 64, 2, mid)
        c.send(puback)
    elif qos == 2:
        # Send PUBREC
        pubrec = pack('!BBH', 80, 2, mid)
        c.send(pubrec)

    print("Bundle sent\n")


# Create the socket to communicate with the DTN daemon
d = socket.socket()
# Connect to the DTN daemon
d.connect((DAEMON_ADDRESS, DAEMON_PORT))
# Get a file object associated with the daemon's socket
fd = d.makefile()
# Read daemon's header response
fd.readline()
# Switch into extended protocol mode
d.send("protocol extended\n")
# Read protocol switch response
fd.readline()
# Set endpoint identifier
d.send("set endpoint %s\n" % SOURCE_DEMUX_TOKEN)
# Read protocol set EID response
fd.readline()
# Read the full DTN Endpoint identifier of this application
d.send("registration list\n")
fd.readline()  # Read the header of registration list response
SOURCE_EID = fd.readline().rstrip()  # Read the full DTN Endpoint identifier of this application
fd.readline()  # Read the last empty line of the response

# Create the socket to listen to MQTT messages coming from client
s = socket.socket()
# Optional: this allows the program to be immediately restarted after exit.
# Otherwise, you may need to wait 2-4 minutes (depending on OS) to bind to the
# listening port again.
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind to the desired address(es) and port
s.bind((SERVER_ADDRESS, SERVER_PORT))
# How many "pending connections" may be queued. Exact interpretation of this
# value is complicated and operating system dependent. This value is usually
# fine for an experimental server.
s.listen(5)

print("Listening on address %s. Kill server with Ctrl-C" % str((SERVER_ADDRESS, SERVER_PORT)))

# Now we have a listening endpoint from which we can accept incoming
# connections. This loop will accept one connection at a time, then service
# that connection until the client disconnects. Lather, rinse, repeat.
while True:
    c, addr = s.accept()
    print("\nConnection received from %s" % str(addr))

    unprocessed_buffer = ''
    current_raw_message = ''
    first_message = True
    new_message = True
    while True:

        try:
            data = c.recv(1024)
        except socket.error as error:
            # In Windows WSAECONNRESET: 10054
            if error.errno == errno.ECONNRESET or error.errno == 10054:
                print("Connection reset by peer. Resetting")
                break

        if not data:
            print("Client closed connection. Resetting")
            break

        res = parse_message(data)
        first_message = False
        if res == -2:
            print("The first message received must be a CONNECT message. Closing connection and resetting")
            break
        elif res == -1:
            print("Wrong message format. Closing connection and resetting")
            break
        elif res == 0:
            new_message = False
            continue

        new_message = True
        while len(unprocessed_buffer) > 0:
            res = parse_message(unprocessed_buffer)
            if res == -1:
                print("Wrong message format. Closing connection and resetting")
                break
            elif res == 0:
                new_message = False
                break
            new_message = True

        if res == -1:
            break

    c.close()

d.close()
