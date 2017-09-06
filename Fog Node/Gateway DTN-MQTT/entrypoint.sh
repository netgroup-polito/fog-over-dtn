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
if [ -z "$DTN_DAEMON_ADDRESS" ]; then
  DTN_DAEMON_ADDRESS="localhost"
fi
if [ -z "$DTN_DAEMON_PORT" ]; then
  DTN_DAEMON_PORT="4550"
fi
if [ -z "$DTN_SRC_DEMUX_TOKEN" ]; then
  DTN_SRC_DEMUX_TOKEN="broker"
fi

sed -i 's/RABBITMQ_HOST/'"$RABBITMQ_HOST"'/g' gateway-dtn-mqtt.py
sed -i 's/RABBITMQ_USER/'"$RABBITMQ_USER"'/g' gateway-dtn-mqtt.py
sed -i 's/RABBITMQ_PASSWORD/'"$RABBITMQ_PASSWORD"'/g' gateway-dtn-mqtt.py
sed -i 's/DTN_DAEMON_ADDRESS/'"$DTN_DAEMON_ADDRESS"'/g' gateway-dtn-mqtt.py
sed -i 's/DTN_DAEMON_PORT/'"$DTN_DAEMON_PORT"'/g' gateway-dtn-mqtt.py
sed -i 's/DTN_SRC_DEMUX_TOKEN/'"$DTN_SRC_DEMUX_TOKEN"'/g' gateway-dtn-mqtt.py

exec "$@"