#!/bin/bash

if [ -z "$RABBITMQ_HOST" ]; then
  RABBITMQ_HOST="172.17.0.2"
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

sed -i 's/RABBITMQ_HOST/'"$RABBITMQ_HOST"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_USER/'"$RABBITMQ_USER"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_PASSWORD/'"$RABBITMQ_PASSWORD"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_QUEUE/'"$RABBITMQ_QUEUE"'/g' /etc/logstash/conf.d/02-beats-input.conf
sed -i 's/RABBITMQ_TOPIC/'"$RABBITMQ_TOPIC"'/g' /etc/logstash/conf.d/02-beats-input.conf

exec "$@"
