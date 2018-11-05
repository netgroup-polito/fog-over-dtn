## Simulation deployment

The simulated environment allow to execute mqtt applications over aether on a docker-based setup. The sporadic connectivity between devices (containers) is emulated through dynamically deployed sdn flow rules.

#### Orchestration tools

In order to deploy the simulated environment, you need first to install the universal node, an orchestration software that manages the deployment of virtual devices and flow rules. Please download the source code from the repository and follow the provided instructions.

    # apt install git
    $ git clone https://github.com/netgroup-polito/un-orchestrator
    ; Follow the instruction provided in README_COMPILE.md
    ; - install the orchestrator
    ; -- with support for docker and ovs
    ; -- while configuring compiling options with ccmake, disable all the additional flags except for 'ENABLE_DOCKER'.
    ; - install the datastore
    
Once installed, run both the node-orchestrator and the datastore.

#### Source code

Download the source code from this repository

    $ git clone https://github.com/netgroup-polito/fog-over-dtn

#### Simulated devices images

Fog and end devices are simulated through docker containers. You need to load the information about these components on the datastore and build the related images on docker.
Deploy docker templates on the datastore:

    $ cd [fog-over-dtn]/vnbf-simulation/
    $ ./deploy_templates.sh
    
Please ensure that templates have been correctly loaded on the datastore by checking the datastore output (response codes should be '200 OK').

[work in progress...]
