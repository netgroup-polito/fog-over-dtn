import paho.mqtt.client
import json
import datetime
import time
import random
import socket

# sleepTime = round(random.uniform(5, 10), 0)
sleepTime = 1
# MQTT details
mqttDeviceId = socket.gethostname()
mqttBrokerHost = "localhost"
mqttBrokerPort = 1883
mqttUser = "guest"
mqttPassword = "guest"
mqttTelemetryTopic = "Tierra.SensorsData"


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

# Collect telemetry information and publish to MQTT broker in JSON format
while True:
    telemetryData = {}
    telemetryData["DeviceId"] = mqttDeviceId
    telemetryData["Timestamp"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    telemetryData["Temperature"] = str(round(random.uniform(20, 30), 2))
    telemetryData["Humidity"] = str(round(random.uniform(0, 100), 2))
    telemetryData["Pressure"] = str(round(random.uniform(900, 1100), 2))
    telemetryDataJson = json.dumps(telemetryData)
    mqttClient.publish(mqttTelemetryTopic, telemetryDataJson, 0)
    time.sleep(sleepTime)

mqttClient.loop_stop()
mqttClient.disconnect()
