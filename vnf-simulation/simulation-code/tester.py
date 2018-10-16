#!/usr/bin/env python
import subprocess
import time
import random
import requests
import itertools
import csv
import threading
import os

from nffg_library.nffg import *


# Base URL of un-orchestrator REST APIs
BASE_URL = 'http://localhost:8080/NF-FG/'
# If False we are in the MQTT-over-DTN test case
MQTT_DIRECT = False
# Identify the number of simulation run
N_RUN = 44
RUN_ID = str(N_RUN) + "_MQTT" if MQTT_DIRECT else str(N_RUN) + "_DTN"
# Simulation time of running in seconds. It represents the actual time during which messages are generated and sent
# to the Fog node by sensing nodes while un-orchestrator performs nodes switching.
RUNNING_TIME = 600
# Min and Max number of interations a contact can hold
MIN_INTERVAL = 1
MAX_INTERVAL = 5
# Sleep time between each iteration of the simulation
ITERATION_TIME = 3
# How often a new message is generated by a MQTT publisher
GENERATION_TIME = 1
# Final wait in seconds in order to let all undelivered messages to flow to the Fog node
FINALIZATION_WAIT = 0
# Set the seed for pseudo-random number generator so the test could be reproducible
RANDOM_SEED = 17814
# Number of simulated sensing nodes
NUM_RASPI = 15
# This value is needed to retrieve the ID of containers instantiated by the un-orchestrator
# To be changed if the 'raspi-node' docker image will be changed and rebuilt
DOCKER_IMAGE_ANCESTOR = 'd2adf55bb0d9'
# S is the probability that 2 IoT nodes can be connected in this iteration
S = 0.2
# T is the probability that 1 IoT node and the Fog node can be connected in this iteration
T = 0.3
# Fog node VNF template id on datastore
FOG_VNF_ID = 'TAF0QZ'
# File containing Raspi nodes VNF template ids on datastore
RASPI_VNF_IDS = 'raspi_vnf_ids.txt'
#raspi_vnf_ids = ['WWUFUD', 'W9M4X8', 'TOERH8', '55F70I', 'SEL3I7', 'VZAFG1', 'VK9DFB', 'E9S1QE', 'IMTAVB', '9OT6PY',
#                 'SMD5EZ', 'SAMMF9', 'BXJW6O', 'V1C80M', '95I1YU', 'NW6F04', 'BLC1TI', 'DUG2Z8', 'GVPCO8', '1QA9PP']


class Link(object):
    def __init__(self, vnf1_id, vnf2_id, up=False, iterations=0):
        self.vnf1_id = vnf1_id
        self.vnf2_id = vnf2_id
        self.up = up
        self.iterations = iterations

    def get_vnf1_id(self):
        return self.vnf1_id

    def get_vnf2_id(self):
        return self.vnf2_id

    def is_up(self):
        return self.up

    def set_up(self):
        self.up = True

    def set_down(self):
        self.up = False

    def get_iterations(self):
        return self.iterations

    def set_iterations(self, it):
        self.iterations = it

    def decrement_iterations(self):
        self.iterations -= 1


def add_link_between_vnfs(graph, vnf1_id, vnf2_id):
    vnf1_flow_rules = graph.getFlowRulesSendingTrafficFromPort(vnf1_id, 'L2Port:0')
    if not vnf1_flow_rules:
        match = Match(port_in='vnf:' + vnf1_id + ':L2Port:0')
        actions = [Action(output='vnf:' + vnf2_id + ':L2Port:0')]
        flow_rule = FlowRule(_id=uuid.uuid4().hex, priority=1, match=match, actions=actions)
        graph.addFlowRule(flow_rule)
    else:
        flow_rule_index = graph.flow_rules.index(vnf1_flow_rules[0])
        action = Action(output='vnf:' + vnf2_id + ':L2Port:0')
        graph.flow_rules[flow_rule_index].actions.append(action)
        graph.flow_rules[flow_rule_index].id = uuid.uuid4().hex

    vnf2_flow_rules = graph.getFlowRulesSendingTrafficFromPort(vnf2_id, 'L2Port:0')
    if not vnf2_flow_rules:
        match = Match(port_in='vnf:' + vnf2_id + ':L2Port:0')
        actions = [Action(output='vnf:' + vnf1_id + ':L2Port:0')]
        flow_rule = FlowRule(_id=uuid.uuid4().hex, priority=1, match=match, actions=actions)
        graph.addFlowRule(flow_rule)
    else:
        flow_rule_index = graph.flow_rules.index(vnf2_flow_rules[0])
        action = Action(output='vnf:' + vnf1_id + ':L2Port:0')
        graph.flow_rules[flow_rule_index].actions.append(action)
        graph.flow_rules[flow_rule_index].id = uuid.uuid4().hex


def delete_link_between_vnfs(graph, vnf1_id, vnf2_id):
    for flow_rule in graph.flow_rules[:]:
        if flow_rule.match.port_in == 'vnf:' + vnf1_id + ':L2Port:0':
            for action in flow_rule.actions:
                if action.output == 'vnf:' + vnf2_id + ':L2Port:0':
                    flow_rule_index = graph.flow_rules.index(flow_rule)
                    graph.flow_rules[flow_rule_index].actions.remove(action)
                    if not graph.flow_rules[flow_rule_index].actions:
                        graph.flow_rules.pop(flow_rule_index)
                    else:
                        graph.flow_rules[flow_rule_index].id = uuid.uuid4().hex

        if flow_rule.match.port_in == 'vnf:' + vnf2_id + ':L2Port:0':
            for action in flow_rule.actions:
                if action.output == 'vnf:' + vnf1_id + ':L2Port:0':
                    flow_rule_index = graph.flow_rules.index(flow_rule)
                    graph.flow_rules[flow_rule_index].actions.remove(action)
                    if not graph.flow_rules[flow_rule_index].actions:
                        graph.flow_rules.pop(flow_rule_index)
                    else:
                        graph.flow_rules[flow_rule_index].id = uuid.uuid4().hex


def bundles_count_test(containers, runid, stop_event):
    with open(os.path.normpath(os.path.join(os.getcwd(), '../run-logs/%s_bundles_count.csv' % runid)), 'w') as csvfile:
        while(not stop_event.is_set()):
            count_list = []
            for container in containers:
                process = subprocess.Popen(['docker', 'exec', container, 'sh', '-c', 'ls -1q /var/spool/ibrdtn/bundles/blocks | wc -l'], stdout=subprocess.PIPE)
                out, err = process.communicate()
                count_list.append(out.rstrip())
            wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            wr.writerow(count_list)
#            stop_event.wait(2)


# TEST INITIALIZATION
# Set the seed for pseudo-random number generator so the test could be reproducible
random.seed(RANDOM_SEED)

# Debug code
orig_stdout = sys.stdout
f = open(os.path.normpath(os.path.join(os.getcwd(), '../run-logs/%s.txt' % RUN_ID)), 'w')
sys.stdout = f

# Print run info
print "RUN_ID: " + RUN_ID
print "Simulation parameters used by this run:"
print "\tNUM_RASPI: " + str(NUM_RASPI)
print "\tRUNNING_TIME: " + str(RUNNING_TIME)
print "\tITERATION_TIME: " + str(ITERATION_TIME)
print "\tMIN_INTERVAL: " + str(MIN_INTERVAL)
print "\tMAX_INTERVAL: " + str(MAX_INTERVAL)
print "\tGENERATION_TIME: " + str(GENERATION_TIME)
# print "\tFINALIZATION_WAIT: " + str(FINALIZATION_WAIT)
print "\tRANDOM_SEED: " + str(RANDOM_SEED)

# Create the initial NF-FG
print "Create the initial NF-FG"

with open('raspi_vnf_ids.txt') as f:
    raspi_vnfs = f.read().splitlines()

vnfs = []
for i in range(NUM_RASPI):
    raspi_vnf = VNF(_id="raspi" + str(i + 1), name="raspi" + str(i + 1), vnf_template_location=raspi_vnfs[i],
                    ports=[Port(_id="L2Port:0", name="data-port")])
    vnfs.append(raspi_vnf)

fog_vnf = VNF(_id="fog", name="fog", vnf_template_location=FOG_VNF_ID, ports=[Port(_id="L2Port:0", name="data-port")],
              unify_control=[UnifyControl(host_tcp_port=4550, vnf_tcp_port=4550)])
vnfs.append(fog_vnf)

nffg = NF_FG(name="MQTT-DTN simulation graph", vnfs=vnfs)

print "Initialize links"
links = []
for pair in itertools.combinations(range(1, NUM_RASPI + 1), 2):
    link = Link(vnf1_id='raspi' + str(pair[0]), vnf2_id='raspi' + str(pair[1]))
    links.append(link)

for i in range(1, NUM_RASPI + 1):
    link = Link(vnf1_id='fog', vnf2_id='raspi' + str(i))
    links.append(link)

#print "Initial graph:\n%s" % json.dumps(json.loads(nffg.getJSON()), indent= 4)
#sys.exit(1)

# Uploading the initial forwarding graph
print "Uploading the initial forwarding graph"
r = requests.post(BASE_URL, json=json.loads(nffg.getJSON()))
if r.status_code != 201:
    print nffg.getJSON()
    print "Error occured during graph uploading. See un-orchestrator logs."
    sys.exit(1)

# Extract graph_id assigned by the un-orchestrator for further graph updating
graph_id = json.loads(r.text)['nffg-uuid']
print "Initial graph succesfully uploaded with id: %s" % graph_id

# Retrieve the ID of 'raspi-node' containers instantiated by the un-orchestrator
print "Retrieving the ID of containers instantiated by the un-orchestrator"
process = subprocess.Popen(
    ['docker', 'ps', '-f', 'ancestor={}'.format(DOCKER_IMAGE_ANCESTOR), '-f', 'status=running', '-q'],
    stdout=subprocess.PIPE)
out, err = process.communicate()
containers = out.splitlines()

# Wait for gateway-mqtt-dtn.py to be up
time.sleep(10)

count_stop = threading.Event()
count_thread = threading.Thread(target=bundles_count_test, args=(containers, RUN_ID, count_stop))
count_thread.start()

# Spawn the MQTT publisher of each node
print "Starting MQTT publisher on each sensing node"
if (MQTT_DIRECT):
    for container in containers:
        subprocess.Popen(
            ['docker', 'exec', '-d', container, '/mqtt-direct-publisher.py', RUN_ID, str(RUNNING_TIME),
             str(FINALIZATION_WAIT), str(GENERATION_TIME)], stdout=subprocess.PIPE)
else:
    for container in containers:
        subprocess.Popen(
            ['docker', 'exec', '-d', container, '/mqtt-publisher.py', RUN_ID, str(RUNNING_TIME),
             str(FINALIZATION_WAIT), str(GENERATION_TIME)], stdout=subprocess.PIPE)

# Starting the simulation
print "Simulation start"
test_start = time.time()
test_end = test_start + RUNNING_TIME
while time.time() < test_end:
    t = time.time() - test_start
    print "[Switching nodes at %02d:%02d:%02d]: " % (t / 3600, t / 60 % 60, t % 60)
    for link in links:
        x_ij = random.random()
        link_prob = T if link.get_vnf1_id() == 'fog' else S
        if x_ij < link_prob and not link.is_up():
            link.set_up()
            add_link_between_vnfs(nffg, link.get_vnf1_id(), link.get_vnf2_id())
            print "\tLink between %s and %s set up" % (link.get_vnf1_id(), link.get_vnf2_id())
        elif x_ij >= link_prob and link.is_up():
            link.set_down()
            delete_link_between_vnfs(nffg, link.get_vnf1_id(), link.get_vnf2_id())
            print "\tLink between %s and %s set down" % (link.get_vnf1_id(), link.get_vnf2_id())

    # Send the updated graph to the un-orchestrator
    #print json.dumps(json.loads(nffg.getJSON()), indent=4)
    r = requests.put(BASE_URL + graph_id, json=json.loads(nffg.getJSON()))
    if r.status_code != 202:
        print "Error occured during graph updating. See un-orchestrator logs."
        sys.exit(1)

    # Sleep before next iteration
    time.sleep(ITERATION_TIME)

count_stop.set()
count_thread.join()

#print "Simulation end. Waiting for nodes to come back to depot."
#
# TEST FINALIZATION
#while True:
#    t = time.time() - test_start
#    connected_nodes = 0
#    for link in links:
#        if link.is_up() and link.get_vnf1_id() == 'fog':
#            connected_nodes += 1
#            print "\tNode %s already came back to depot" % link.get_vnf2_id()
#            continue
#        elif link.is_up() and link.get_vnf1_id() != 'fog':
#            link.set_down()
#            delete_link_between_vnfs(nffg, link.get_vnf1_id(), link.get_vnf2_id())
#            continue
#        elif not link.is_up() and link.get_vnf1_id() == 'fog':
#            x_ij = random.random()
#            if x_ij < T:
#                connected_nodes += 1
#                link.set_up()
#                add_link_between_vnfs(nffg, link.get_vnf1_id(), link.get_vnf2_id())
#                print "\tNode %s comes back to depot at %02d:%02d:%02d" % (link.get_vnf2_id(), t / 3600, t / 60 % 60, t % 60)
#
#    # Send the updated graph to the un-orchestrator
#    #print json.dumps(json.loads(nffg.getJSON()), indent=4)
#    r = requests.put(BASE_URL + graph_id, json=json.loads(nffg.getJSON()))
#    if r.status_code != 202:
#        print "Error occured during graph updating. See un-orchestrator logs."
#        sys.exit(1)
#
#    if connected_nodes == NUM_RASPI:
#        break
#
#    time.sleep(ITERATION_TIME)
#

print "Simulation end. Undeploying NF-FG."

requests.delete(BASE_URL + graph_id)

print "Exit from simulation"

sys.stdout = orig_stdout
f.close()