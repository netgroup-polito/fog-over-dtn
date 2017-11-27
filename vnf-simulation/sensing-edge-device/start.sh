#!/bin/bash

ifconfig eth0 192.168.100.20/24
route add default gw 192.168.100.254 eth0

#dtnd -c dtn-default.conf &

#sleep 10

while ! exec 6<>/dev/tcp/localhost/4550; do
    sleep 1
done

python gateway-mqtt-dtn.py
