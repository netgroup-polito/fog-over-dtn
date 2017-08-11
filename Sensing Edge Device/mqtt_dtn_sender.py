import socket
import errno
from struct import unpack
import base64

# Address and port to listen to MQTT messages
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 1883
# Address and port of the DTN daemon
DAEMON_ADDRESS = 'localhost'
DAEMON_PORT = 4550
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
    while i < 4:
        encoded_byte = length_bytes[i]
        i += 1
        int_byte = unpack('!B', encoded_byte)
        value += (int_byte[0] & 0x7f) * multiplier
        if (int_byte[0] & 0x80) == 0:
            break
        else:
            multiplier *= 128
            # TODO: Verify correctness of the "remaining length" encoding as per protocol specification
            # if multiplier > 128 * 128 * 128:
            #    raise Exception
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
        elif not first_message and packet_type != 0x30:
            return -1

    if len(current_raw_message) < 5:
        return 0

    remaining_bytes, n = decode_remaining_length(current_raw_message[1:5])
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
    # TODO: Support for QoS=1-2
    elif packet_type == 0x30:
        topic_length = unpack('!H', current_raw_message[1 + n:3 + n])
        topic = current_raw_message[3 + n:3 + n + topic_length[0]]
        payload = current_raw_message[3 + n + topic_length[0]:]
        print("PUBLISH Received - Topic: %s; Message: %s\n" % (topic, payload))
        send_bundle(topic, payload)

    current_raw_message = ''
    return 1


def send_bundle(topic, message):
    """
    Create a bundle from a MQTT message and send it through IBR-DTN deamon

    Args:
        topic: The topic of the MQTT message
        message: The MQTT payload
    """
    payload = "%s\n%s" % (topic, message)

    bundle = "Destination: %s\n" % DESTINATION_EID
    bundle += "Processing flags: 144\n"
    bundle += "Blocks: 1\n\n"
    bundle += "Block: 1\n"
    bundle += "Flags: LAST_BLOCK\n"
    bundle += "Length: %s\n\n" % str(len(topic) + len(message) + 1)
    bundle += "%s\n\n" % base64.b64encode(payload)

    d.send("bundle put plain\n")
    fd.readline()

    d.send(bundle)
    fd.readline()

    d.send("bundle send\n")
    fd.readline()
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
            if error.errno == errno.ECONNRESET:
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
