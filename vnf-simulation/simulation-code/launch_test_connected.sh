#!/bin/bash
RUN_TIME=1800
TEST=45

sed -i 's/^\(N_RUN = \).*$/\1'"$TEST"'/gm' tester_connected.py
sed -i 's/^\(MQTT_DIRECT = \).*$/\1False/gm' tester_connected.py
sed -i 's/^\(NUM_RASPI = \).*$/\115/gm' tester_connected.py
sed -i 's/^\(RUNNING_TIME = \).*$/\1'"$RUN_TIME"'/gm' tester_connected.py
python tester_connected.py
let "TEST += 1"
sed -i 's/^\(N_RUN = \).*$/\1'"$TEST"'/gm' tester_connected.py
sed -i 's/^\(MQTT_DIRECT = \).*$/\1True/gm' tester_connected.py
python tester_connected.py
