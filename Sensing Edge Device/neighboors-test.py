import socket
import RPi.GPIO as GPIO
import signal
import sys

# Address and port of the DTN daemon
DAEMON_ADDRESS = 'localhost'
DAEMON_PORT = 4550


def exit_handler(signal, frame):
    # Turn off LEDs before exit
    GPIO.output(22, GPIO.LOW)
    GPIO.output(17, GPIO.LOW)
    d.close()
    sys.exit(0)


# Ctrl-C Signal Handler
signal.signal(signal.SIGINT, exit_handler)

# Using GPIO pins BCM17 and BCM22 to drive the two LEDs.
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

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

nebbioloLEDOn = False
anyDeviceLEDOn = False

while True:
    nebbioloDiscovered = False
    anyDeviceDiscovered = False
    neighboors = []

    d.send("neighbor list\n")
    fd.readline()
    while True:
        res = fd.readline()
        if res == "\n":
            # List end
            break
        neighboors.append(res)

    for neighbor in neighboors:
        if neighbor.startswith("dtn://otvm1"):
            nebbioloDiscovered = True
        else:
            anyDeviceDiscovered = True

    if nebbioloDiscovered and not nebbioloLEDOn:
        print "FogNode Connected - Green LED On\n"
        nebbioloLEDOn = True
        GPIO.output(17, GPIO.HIGH)
    elif not nebbioloDiscovered and nebbioloLEDOn:
        print "FogNode Disconnected - Green LED Off\n"
        nebbioloLEDOn = False
        GPIO.output(17, GPIO.LOW)

    if anyDeviceDiscovered and not anyDeviceLEDOn:
        print "Peer device(s) connected - Red LED On\n"
        anyDeviceLEDOn = True
        GPIO.output(22, GPIO.HIGH)
    elif not anyDeviceDiscovered and anyDeviceLEDOn:
        print "No Peer device(s) connected - Red LED Off\n"
        anyDeviceLEDOn = False
        GPIO.output(22, GPIO.LOW)
