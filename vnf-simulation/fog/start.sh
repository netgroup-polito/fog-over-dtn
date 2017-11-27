#!/bin/bash

echo 1 > /proc/sys/net/ipv4/ip_forward

ifconfig eth1 192.168.100.254/24

iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT

#dtnd -c dtn-default.conf &

while ! exec 6<>/dev/tcp/localhost/4550; do
    sleep 1
done

python gateway-dtn-mqtt.py
