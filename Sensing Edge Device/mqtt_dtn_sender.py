import socket
import errno
from struct import unpack

# Address and port to listen to MQTT messages
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 1883


def decode_remaining_length(length_bytes):
    """
    Decode message length according to MQTT specifications
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


# Return values:
# -2: ERROR_CONNECT
# -1: ERROR_PARSING
#  0: NEED_MORE_DATA
#  1: PARSING_FINISHED

def parse_message(msg):
    global unprocessed_buffer
    global current_raw_message

    current_raw_message += msg

    if new_message:
        packet_type = unpack('!B', current_raw_message[0])[0] & 0xF0
        if first_message and packet_type != 0x10:
            return -2
        elif not first_message and packet_type != 0x30:
            return -1

    # TODO: Fix the code. Could raise exception if len(current_raw_message) < 5
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
        # TODO: Create a Bundle and send it through DTN daemon

    current_raw_message = ''
    return 1


# Create the socket
s = socket.socket()
# Optional: this allows the program to be immediately restarted after exit.
# Otherwise, you may need to wait 2-4 minutes (depending on OS) to bind to the
# listening port again.
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind to the desired address(es) and port.
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
            if error.errno == errno.WSAECONNRESET:
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
