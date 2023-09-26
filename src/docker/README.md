# Build the images

Change into the directory of the node and build the images.

## coordinator

` docker build -f Dockerfile-test -t spa-energy-coordinator .`

## consumer

` docker build -f Dockerfile-test -t spa-energy-consumer .`

## generator

` docker build -f Dockerfile-test -t spa-energy-generator .`

## network

` docker build -f Dockerfile-test -t spa-energy-network .`


# Start use case

Create `.env` file to set `MQTT_HOST` to the correct ip address, e.g.

```
MQTT_HOST=127.0.0.1
```
or

```
MQTT_HOST=host.docker.internal
FLASK_DEBUG=false
```

Start the docker container:
`docker-compose -f docker-compose-spa-energy.yml up`

# Run the website

http://<hostname>:8050
