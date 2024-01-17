#!/bin/sh

echo "Starting mosquitto mqtt service"

service mosquitto start

echo "Updating Python environments"

cd src/network_area
poetry install
cd ../..

echo "Done"