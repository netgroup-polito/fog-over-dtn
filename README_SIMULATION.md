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

#### Source code

Download the source code from this repository

    $ git clone https://github.com/netgroup-polito/fog-over-dtn
    $ git submodule init && git submodule update
    
The cloned directory (i.e., the project root folder) will be referred as [fog-over-dtn] in the reminder of this readme.

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

> - **NOTE:** if you have a particular setup for the rabbitmq broker, then please configure corresponding fog node parameters in [gateway-dtn-mqtt.py](vnf-simulation/fog/gateway-dtn-mqtt.py) under '# Broker connetion details', before running the 'docker build' command for the fog node.

> - **NOTE:** if you need more than 20 sensing end devices, please modify the for loop in both [build_images.sh](vnf-simulation/sensing-edge-device/build_images.sh) and [deploy_templates.sh](vnf-simulation/sensing-edge-device/deploy_templates.sh) files (simply changing the '20' in the for statement) in order to have the needed number of iterations.

#### External tools images

The simulation make use of the rabbitmq server as MQTT broker, and of the ELK stack as consumer application and for monitoring purpose. Both these tools are executed inside ad-hoc containers (official provided images are used).

##### Rabbitmq

    $ cd [fog-over-dtn]/Fog\ Node/Rabbit-MQ-MQTT/
    # docker build --tag=rabbitmq .
    
##### ELK Stack

    $ cd [fog-over-dtn]/Fog\ Node/ELK\ Fog/
    # docker build --tag=elk .


> - **NOTE:** If you have a particular setup for the rabbitmq broker, then please configure corresponding ELK Stack parameters in [entrypoint.sh](Fog%20Node/Elk_Fog/entrypoint.sh) (e.g., rabbitmq host, mqtt user and password) before running the 'docker build' command.


### Run

##### Orchestration tools

Run both the datastore and the universal node following the instruction provided into the corresponding repositories.

> - **WARNING (November 2018):** in the setup we build at the moment of writing this documentation, the universal node presents a bug where it hangs during startup after prompting the message:  
    ```[INFO] Creating the LSI-0...```  
If this is the case, simply send SIG_INT (pressing Ctrl+C) signal twice, and the startup will resume without any problem.

##### External tools

Run rabbitmq and the elk stack containers:

    # docker run -d rabbitmq
    # docker run -d elk

If you encounter issues running the elk container concerning the elastic search module, please follow the istruction provided in this [official page](https://elk-docker.readthedocs.io/#prerequisites).

##### Simulation scripts

###### Single instance

If you need to execute a single instance simulation run the following script:

    $ cd [fog-over-dtn]/vnf-simulation/simulation-code/
    # python tester.py
    
This will deploy the dtn nodes through the orchestrator and will dynamically modify instantiate/remove network links between them to simulate device moving. The simulation is driven by the following parameters:

- RUNNING_TIME (default 1800): total simulation time, in seconds (the time needed by the orchestrator to periodically modify the inter-device connection is excluded).
- ITERATION_TIME (default 3): number of seconds that the simulator waits before to modify the network links at each iteration (used to model the inter-device connection duration).
- GENERATION_TIME (default 5): period of MQTT message generation (sensors measurement) from sensing devices.
- NUM_RASPI (default 15): number of sensing end devices.
- S (default 0.2): probability that 2 given end devices have a direct connection on a given iteration.
- T (default 0.3): probability that a given end device has a direct connection with the fog node on a given iteration.

You can modify these parameter by editing the header of the script [tester.py](vnf-simulation/simulation-code/tester.py).

###### Multiple instances (validation purpose)

It is possible to run multiple simulations in a row with different configurations using the [launch_test.sh](vnf-simulation/simulation-code/launch_test.sh) script.

    # ./launch_test.sh

Inside the script some significant parameters can be modified (the script automatically inject them in the simulator).

### Output collection

##### Rabbitmq

After running the simulation, you can check that everithing is working by accessing the rabbitmq web interface, where you should see two clients connected (the fog node and the elk stack) and periodic messages delivered. The web interface is available at 172.17.0.3:15672 (assuming this is the ip address that docker assigned to the rabbitmq container in your setup). Unless particular configurations, use the default rabbitmq username and password to access the web gui.

##### Kibana

The ELK stack provides the kiban web app at 172.17.0.2:5601/app/kibana (assuming this is the ip address that docker assigned to the elk container in your setup). To visualize all messages create a new index 'rpi*'. To export data of each simulation in csv format you can install the 'x-pack' ELK plugin.

##### Logs

Logs are generated by each component of the system.

- Simulation run logs are stored in the [run-logs](vnf-simulation/run-logs/) folder.
- Log of the 'dtn to mqtt' gateway can be found on the fog node container root folder, in the 'gw.log' file.
- Logs of the sensors data publishers are created on the root folder of each end device container.
- On each dtn device, the ibrdtn deamon logs on /var/log/ibrdtn.log.
