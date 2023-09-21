# Energy network

Implementation of an energy network for the [Secure Prescriptive Analytics](https://www.prescriptiveanalytics.org) platform.

## Overview

### Components

| Component   | Description                                                                                                   |
|-------------|---------------------------------------------------------------------------------------------------------------|
| consumers   | Load nodes with a defined load profile, i.e., households or industry                                          |
| generator   | Generator nodes with a defined generation profile                                                             |
| network     | Defines the connection of the nodes, every node is connected by a bus                                         |
| coordinator | Application, which uses the network and its components for specific needs, e.g., analysis, optimization, etc. |


# References

# spa - distributed application toolkit

https://spa-distributed-application-tools.readthedocs.io/en/latest/