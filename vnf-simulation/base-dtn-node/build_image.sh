#!/bin/bash
docker rmi base-dtn
docker build --tag=base-dtn .
docker images -q base-dtn > base-dtn-image.txt
mv base-dtn-image.txt ../simulation-code/

