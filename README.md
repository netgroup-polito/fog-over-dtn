# Telemetry system over DTN

This repository contains the first prototype implementation and tests of an MQTT/DTN Gateway architecture enabling a telemetry system to propagate data over challenged networks. The mqtt-to-dtn and the dtn-to-mqtt gateways, core of this repository, are the embrion of [Æther](https://bitbucket.tierraservice.com/projects/AR/repos/aether), which provides additional functionalities while integrating the mqtt protocol support as a plugin.

This repository also provides a simulated environment that allows to setup a multi device telemetry system on a single machine through virtualized nodes. Please refer to the proper [readme](README_SIMULATION.md) for the detailed instruction regarding the installation and execution of the simulation.

## Abstract
Fog computing is an emerging paradigm that extends Cloud computing distributing resources and services of computing, storage, control and networking anywhere along the continuum from Cloud to Things.

In contexts such as agriculture, construction, surveying, forestry or mining, the connection of physical things to analytics and machine learning applications can help glean insights from gathered data. Fog computing will add value by pushing analytics closer to data sources. Fog nodes placed on field could perform data preparation and preliminary data analysis. Only filtered and/or aggregated data could be send up to Cloud for further analysis and persistent storage, thus reducing bandwidth consumption and improving privacy.

Communications, mostly done through wireless networks, could suffer from disrupted connectivity in these challenged environments. Also, the connections change over time due to mobility of machines. Application protocols based on TCP/IP may take impractical amounts of time or fail completely in the absence of an end-to-end path between source and destination. A way to overcome the problem is by using store-carry-and-forward message switching, where blocks of application data are moved from node to node along a path that eventually reaches the destination. Disruption/Delay Tolerant Networks implements this logic by overlaying a new transmission protocol, called the Bundle Protocol, on top of lower layers. 

This project implements an architecture that, transparent with respect to pub/sub based IoT messaging protocols, exploits devices mobility and their occasional contacts for providing the benefits of Fog computing in such environments. In particular, a Proof-Of-Concept telemetry application is developed. Raspberry-Pis, connected through a Wi-Fi Ad-Hoc network, act as data sources and can forward each other produced data to a Fog node, where data elaboration takes place, exploiting an implementation of the Bundle Protocol called IBR-DTN.
