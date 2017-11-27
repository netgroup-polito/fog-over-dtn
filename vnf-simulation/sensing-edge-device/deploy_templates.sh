#!/bin/bash
for NODE in `seq 1 20`;
do
	echo Deployng VNF $NODE on datastore
	sed -i 's/\(raspi-node\):[0-9]*/\1:'"$NODE"'/g' template.json
	VNFID=$(curl -s -H "Content-Type: application/json" -d "@template.json" -X PUT http://localhost:8081/v2/nf_template/)
	if [ $NODE -eq 1 ]; then
		echo $VNFID > ../simulation-code/raspi_vnf_ids.txt
	else
		echo $VNFID >> ../simulation-code/raspi_vnf_ids.txt
	fi
	echo
done
