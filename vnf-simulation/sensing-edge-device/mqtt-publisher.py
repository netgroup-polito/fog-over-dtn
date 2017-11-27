#!/usr/bin/env python

import sys
import paho.mqtt.client
import json
import datetime
import time
import random

# Identify the run number and type of a simulation (e.g 1_DIRECT, 1_DTN)
RUN_ID = sys.argv[1]
# Simulation time in seconds. It represents the operative time during which messages are generated and sent to the
# Fog node by sensing nodes while un-orchestrator performs nodes switching.
RUNNING_TIME = int(sys.argv[2])
# Final wait in seconds in order to let all undelivered messages to flow to the Fog node
FINALIZATION_WAIT = int(sys.argv[3])
# How often a new message is generated
GENERATION_TIME = int(sys.argv[4])
# MQTT details
mqttDeviceId = "Raspi-20"
mqttBrokerHost = "localhost"
mqttBrokerPort = 1883
mqttUser = "guest"
mqttPassword = "guest"
mqttTelemetryTopic = "Tierra.SensorsData"

# Debug code
orig_stdout = sys.stdout
f = open('pub.log', 'w')
sys.stdout = f


# Callback methods
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker (RC: %s)" % rc)
    else:
        print("Connection to MQTT broker failed (RC: %s)" % rc)


def on_log(client, userdata, level, buf):
    print(buf)


def on_publish(client, userdata, mid):
    print("Data published (Mid: %s)" % mid)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnect")
    print("Disconnected from MQTT broker")


# Set MQTT client
mqttClient = paho.mqtt.client.Client()
mqttClient.username_pw_set(mqttUser, mqttPassword)
# Register callbacks
mqttClient.on_connect = on_connect
mqttClient.on_log = on_log
mqttClient.on_publish = on_publish
mqttClient.on_disconnect = on_disconnect
# Connect to MQTT broker
mqttClient.connect(mqttBrokerHost, mqttBrokerPort, 60)
mqttClient.loop_start()

# Wait 10 seconds in order to let the un-orchestrator to start nodes switching
#time.sleep(10)

# Loop until simulation time is expired
start_time = time.time()
test_end = start_time + RUNNING_TIME
while time.time() < test_end:
    # Collect telemetry information and publish to MQTT broker in JSON format
    telemetryData = {}
    telemetryData["DeviceId"] = mqttDeviceId
    telemetryData["RunId"] = RUN_ID
    telemetryData["ElapsedTime"] = time.time() - start_time
    telemetryData["Timestamp"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    telemetryData["Temperature"] = str(round(random.uniform(20, 30), 2))
    telemetryData["Humidity"] = str(round(random.uniform(0, 100), 2))
    telemetryData["Pressure"] = str(round(random.uniform(900, 1100), 2))
    telemetryDataJson = json.dumps(telemetryData)
    mqttClient.publish(mqttTelemetryTopic, telemetryDataJson, 0)
    time.sleep(GENERATION_TIME)

# Wait to let all undelivered messages to flow to the Fog node
#time.sleep(FINALIZATION_WAIT)

mqttClient.loop_stop()
mqttClient.disconnect()

sys.stdout = orig_stdout
f.close()
