#!/bin/bash

if [ -z "$RABBITMQ_HOST" ]; then
  RABBITMQ_HOST="localhost"
fi
if [ -z "$RABBITMQ_USER" ]; then
  RABBITMQ_USER="guest"
fi
if [ -z "$RABBITMQ_PASSWORD" ]; then
  RABBITMQ_PASSWORD="guest"
fi
if [ -z "$RABBITMQ_QUEUE" ]; then
  RABBITMQ_QUEUE="Tierra.Telemetry"
fi
if [ -z "$RABBITMQ_TOPIC" ]; then
  RABBITMQ_TOPIC="Tierra.SensorsData"
fi

RABBITMQ_QUEUE_TEMP="${RABBITMQ_QUEUE}.FilteredTemp"
RABBITMQ_QUEUE_PRES="${RABBITMQ_QUEUE}.FilteredPres"
RABBITMQ_QUEUE_HUM="${RABBITMQ_QUEUE}.FilteredHum"

sed -i 's/RABBITMQ_HOST/'"$RABBITMQ_HOST"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_USER/'"$RABBITMQ_USER"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_PASSWORD/'"$RABBITMQ_PASSWORD"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_QUEUE_TEMP/'"$RABBITMQ_QUEUE_TEMP"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_QUEUE_PRES/'"$RABBITMQ_QUEUE_PRES"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_QUEUE_HUM/'"$RABBITMQ_QUEUE_HUM"'/g' /etc/logstash/conf.d/02-beats-input.conf

exec "$@"