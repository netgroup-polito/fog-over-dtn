#!/bin/bash
RUN_TIME=1800
S1=0.1
S2=0.2
T=0.3
for TEST in `seq 30 3 42`;
do
	SEED=$RANDOM
	sed -i '/stop_event.wait/s/^#//' tester.py
	sed -i 's/^\(N_RUN = \).*$/\1'"$TEST"'/gm' tester.py
	sed -i 's/^\(RANDOM_SEED = \).*$/\1'"$SEED"'/gm' tester.py
	sed -i 's/^\(NUM_RASPI = \).*$/\15/gm' tester.py
    sed -i 's/^\(S = \).*$/\1'"$S1"'/gm' tester.py
    sed -i 's/^\(T = \).*$/\1'"$T"'/gm' tester.py
    sed -i 's/^\(RUNNING_TIME = \).*$/\1'"$RUN_TIME"'/gm' tester.py
	python tester.py
	let "TEST += 1"
	sed -i '/stop_event.wait/s/^/#/' tester.py
    sed -i 's/^\(N_RUN = \).*$/\1'"$TEST"'/gm' tester.py
    sed -i 's/^\(NUM_RASPI = \).*$/\115/gm' tester.py
	python tester.py
	let "TEST += 1"
	sed -i 's/^\(N_RUN = \).*$/\1'"$TEST"'/gm' tester.py
	sed -i 's/^\(S = \).*$/\1'"$S2"'/gm' tester.py
	python tester.py
done
