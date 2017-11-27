#!/bin/bash
for NODE in `seq 1 20`;
do
	echo Building node: $NODE
	sed -i 's/\.[0-9]\+\//.'"$NODE"'\//' start.sh
	sed -i 's/^\(mqttDeviceId = \).*$/\1"Raspi-'"$NODE"'"/gm' mqtt-publisher.py
	sed -i 's/^\(mqttDeviceId = \).*$/\1"Raspi-'"$NODE"'"/gm' mqtt-direct-publisher.py
	sed -i 's/^\(local_uri = \).*$/\1dtn:\/\/Raspi-'"$NODE"'/gm' dtn-default.conf
	docker build --tag=raspi-node:$NODE .
	echo
done

echo Remove dangling images
docker rmi $(docker images -f "dangling=true" -q)
