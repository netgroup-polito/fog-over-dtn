#!/usr/bin/env python
import pika
import json

rabbitmq_host = 'RABBITMQ_HOST'
rabbitmq_user = 'RABBITMQ_USER'
rabbitmq_password = 'RABBITMQ_PASSWORD'
rabbitmq_queue = 'RABBITMQ_QUEUE'
rabbitmq_topic = 'RABBITMQ_TOPIC'
threshold_temp = THRESHOLD_TEMP
threshold_pres = THRESHOLD_PRES
threshold_hum = THRESHOLD_HUM
queue_to_filter = rabbitmq_queue + '.DataToFilter'

cred = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=cred))
channel = connection.channel()

channel.queue_declare(queue=queue_to_filter, durable=True)
channel.queue_bind(exchange='amq.topic', queue=queue_to_filter, routing_key=rabbitmq_topic)


def callback(ch, method, properties, body):
    readings = json.loads(body)

    if float(readings["Temperature"]) >= threshold_temp:
        message = {}
        message["DeviceId"] = readings["DeviceId"]
        message["Timestamp"] = readings["Timestamp"]
        message["Temperature"] = readings["Temperature"]

        channel.basic_publish(exchange='amq.topic', routing_key='Tierra.FilteredData.Temp', body=json.dumps(message))
        print(' Message published: ' + json.dumps(message))

    if float(readings["Pressure"]) >= threshold_pres:
        message = {}
        message["DeviceId"] = readings["DeviceId"]
        message["Timestamp"] = readings["Timestamp"]
        message["Pressure"] = readings["Pressure"]

        channel.basic_publish(exchange='amq.topic', routing_key='Tierra.FilteredData.Pres', body=json.dumps(message))
        print(' Message published: ' + json.dumps(message))

    if float(readings["Humidity"]) >= threshold_hum:
        message = {}
        message["DeviceId"] = readings["DeviceId"]
        message["Timestamp"] = readings["Timestamp"]
        message["Humidity"] = readings["Humidity"]

        channel.basic_publish(exchange='amq.topic', routing_key='Tierra.FilteredData.Hum', body=json.dumps(message))
        print(' Message published: ' + json.dumps(message))


channel.basic_consume(callback, queue=queue_to_filter, no_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
    
connection.close()
