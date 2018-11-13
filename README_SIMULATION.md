## Simulation deployment

The simulated environment allow to execute mqtt applications over aether on a docker-based setup. The sporadic connectivity between devices (containers) is emulated through dynamically deployed sdn flow rules.

### Install

#### Preliminar packages

Use apt to download and install required packages:

    # apt update
    # apt install git python-pip
    # pip install requests==2.20.0

#### Orchestration tools

In order to deploy the simulated environment, you need first to install the universal node, an orchestration software that manages the deployment of virtual devices and flow rules. Please download the source code from the repository and follow the provided instructions.

    $ git clone https://github.com/netgroup-polito/un-orchestrator
    ; Follow the instruction provided in README_COMPILE.md
    ; - install the orchestrator
    ; -- with support for docker and ovs
    ; -- while configuring compiling options with ccmake, disable all the additional 'ENABLE_*' flags except for 'ENABLE_DOCKER' and 'ENABLE_UNIFY_PORTS_CONFIGURATION'.
    ; - install the datastore
    
Once installed, run both the node-orchestrator and the datastore.

#### Source code

Download the source code from this repository

    $ git clone https://github.com/netgroup-polito/fog-over-dtn
    $ git submodule init && git submodule update

#### Simulated devices images

Fog and end devices are simulated through docker containers. You need to load the information about these components on the datastore and build the related images on docker.

First build the base base docker image that implements common dtn features:

    $ cd [fog-over-dtn]/vnf-simulation/base-dtn-node/
    # ./build_image.sh
    
The script will paste the id of the built image in a file inside the [simulation-code](vnf-simulation/simulation-code) directory.

Build docker images for the sensing end devices and publish their templates on the datastore:

    $ cd [fog-over-dtn]/vnf-simulation/sensing-edge-device/
    # ./build_images.sh
    $ ./deploy_templates.sh
    
Do the same for the fog node:

    $ cd [fog-over-dtn]/vnf-simulation/fog/
    # docker build --tag=fog-node .
    $ ./deploy_template.sh
       
Please ensure that templates have been correctly loaded on the datastore by checking the datastore output (response codes should be '200 OK'). The scripts paste template ids inside the [simulation-code](vnf-simulation/simulation-code) directory.

NOTE: if you have a particular setup for the rabbitmq broker, then please configure corresponding fog node parameters in [gateway-dtn-mqtt.py](vnf-simulation/fog/gateway-dtn-mqtt.py) under '# Broker connetion details', before running the 'docker build' command for the fog node.

#### External tools images

The simulation make use of the rabbitmq server as MQTT broker, and of the ELK stack as consumer application and for monitoring purpose. Both these tools are executed inside ad-hoc containers (official provided images are used).

##### Rabbitmq

    $ cd [fog-over-dtn]/Fog\ Node/Rabbit-MQ-MQTT/
    # docker build --tag=rabbitmq .
    
##### ELK Stack

    $ cd [fog-over-dtn]/Fog\ Node/ELK\ Fog/
    # docker build --tag=elk .
    
NOTE: If you have a particular setup for the rabbitmq broker, then please configure corresponding ELK Stack parameters in [entrypoint.sh](Fog Node/Elk_Fog/entrypoint.sh) (e.g., rabbitmq host, mqtt user and password) before running the 'docker build' command.


####

[work in progress...]
