# Energy Scheduling - Power Network Simulator

## Overview

This project is designed to serve as an energy network simulator that includes consumers, generators (photovoltaic) and grid connections. The user can load and visualize different consumer and generator models in form of scenarios by selecting a desired day. The data is covering a 24-hour period with readings taken every fifteen minutes.
The consumer models are generated on the basis of a [dataset from London](https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households) from 2011-2014. The generator models are developed with the data provided by the [Photovoltaic Geographical Information System](https://re.jrc.ec.europa.eu/pvg_tools/en/) (PVGIS) and the power-supply lines and network are represented with models from [Pandapower](http://www.pandapower.org/). 

## Environment Setup Instructions

Follow these steps to set up your environment for working with MQTT and Docker:

### Install Docker Desktop

- Download and install Docker Desktop for your operating system from the official Docker website: [Docker Desktop](https://www.docker.com/products/docker-desktop).
- Follow the installation instructions specific to your operating system.

### Install MQTT-Explorer

- Download and install MQTT-Explorer, a versatile MQTT client tool for interacting with MQTT brokers and topics.
- You can get MQTT-Explorer from its official GitHub repository: [MQTT-Explorer](https://mqtt-explorer.com/).
- Refer to the GitHub page for installation instructions based on your operating system.

## Other Prerequisites

- Install Python on your system
- Install package [spa-dat](https://pypi.org/project/spa-dat/)
- Other packages?

### Open a Command Prompt (Windows) or Terminal (macOS and Linux)

- Launch the default command prompt or terminal for your operating system. You can usually find it in your system's applications or utilities folder.
- Ensure your command prompt or terminal is ready for use.

## Usage

1. Open Docker Desktok
2. Opon the MQTT-Explorer
3. Open a command prompt and navigate to the directory named `docker`.
4. Run the command `docker-compose -f .\docker-compose-spa-energy.yml up`
5. Open the localhost website http://localhost:port/
6. Choose a date and press the `Calculate` button

To shut down the docker run the command `docker-compose -f .\docker-compose-spa-energy.yml down`. This resets all settings.