#!/bin/sh

DIR=`pwd`
echo "Working directory $DIR"

echo "Starting mosquitto mqtt service"
service mosquitto start

echo "Updating Python environments"

cd src/consumer
poetry install
cd ../..

cd src/generator
poetry install
cd ../..

cd src/coordinator
poetry install
cd ../..

cd src/network
poetry install
cd ../..

cd src/network_area
poetry install
cd ../..

cd src/pvnode

echo "Done"
