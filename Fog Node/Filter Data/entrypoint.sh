#!/bin/sh

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
if [ -z "$THRESHOLD_TEMP" ]; then
  THRESHOLD_TEMP="29"
fi
if [ -z "$THRESHOLD_PRES" ]; then
  THRESHOLD_PRES="1050"
fi
if [ -z "$THRESHOLD_HUM" ]; then
  THRESHOLD_HUM="90"
fi

sed -i 's/RABBITMQ_HOST/'"$RABBITMQ_HOST"'/g' filter_data.py
sed -i 's/RABBITMQ_USER/'"$RABBITMQ_USER"'/g' filter_data.py
sed -i 's/RABBITMQ_PASSWORD/'"$RABBITMQ_PASSWORD"'/g' filter_data.py
sed -i 's/RABBITMQ_QUEUE/'"$RABBITMQ_QUEUE"'/g' filter_data.py
sed -i 's/RABBITMQ_TOPIC/'"$RABBITMQ_TOPIC"'/g' filter_data.py
sed -i 's/THRESHOLD_TEMP/'"$THRESHOLD_TEMP"'/g' filter_data.py
sed -i 's/THRESHOLD_PRES/'"$THRESHOLD_PRES"'/g' filter_data.py
sed -i 's/THRESHOLD_HUM/'"$THRESHOLD_HUM"'/g' filter_data.py

exec "$@"