import requests
import json
import pandas as pd
from pathlib import Path
import datetime
import logging
import pickle
import os

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

"""
This python script is designed to create and export optimal power flow json files based on a preloaded model.
It sets up the SPA_DAT library for communication using MQTT, with configurations including payload format and MQTT host/port settings.
The script defines query parameters such as the start timestamp, time interval, and the number of intervals to query. It calculates 
query times based on these parameters. The script checks for a cache directory and stores queried results there to avoid redundant queries. 
It logs information about queried files.

Usage:
1. Ensure the "config.json" file contains the necessary configuration settings.
2. Set the desired query parameters, such as the start timestamp, time interval, and the number of intervals.
3. Run the script to start the distributed application and query network data.
4. Queried data is cached in the specified directory for future use.

"""

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

config_file = Path(__file__).parent / "config.json"
config = None

with open(config_file, "r") as input_file:
    config = json.load(input_file)
    
config["host"] = os.getenv("MQTT_HOST", config["host"])
config["port"] = os.getenv("MQTT_PORT", config["port"])

logging.debug(f"read config file: {config}")
# spa configuration
socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host=config["host"], port=config["port"]))
)
app_dat = DistributedApplication(socket_provider)
results = dict()

start_timestamp = datetime.datetime(2022, 1, 1, 0, 0, 0).timestamp()
interval = 900
number_intervals = int(365*24*4)
# number_intervals = int(24*4)
query_times = [start_timestamp + i*interval for i in range(0, number_intervals)]

cache_dir = "./results_cache"

@app_dat.producer()
async def query_range(socket: SpaSocket, state):
    queried_files = set()
    logging.debug(cache_dir)
    if cache_dir:
        if not os.path.exists(cache_dir):
            logging.debug(f"cache_dir does not exist, creating {cache_dir}")
            os.mkdir(cache_dir)
        logging.debug(f"checking {cache_dir}")
        files = os.listdir(cache_dir)
        queried_files = [int(f[4:-5]) for f in files]
        logging.debug(f"queried files {len(queried_files)}")
    opfs = {}
    for ts in query_times:
        ts = int(ts)
        if ts in queried_files:
            logging.debug(f"skip opf for timestamp {ts}, opf already in {cache_dir}")
            with open(f"./{cache_dir}/opf_{int(ts)}.json", "rt") as infile:
                opf_json = json.load(infile)
                opfs[ts] = opf_json
            continue
        print(f"opf query: {datetime.datetime.fromtimestamp(ts)} ")
        
        network_opf_response = await socket.request(
            SpaMessage(
                    payload = str(ts),
                    topic = "network/opf",
                    # response_topic = "network/opf/response"
            )
        )
        
        result_json = json.loads(network_opf_response.payload)

        with open(f"./{cache_dir}/opf_{int(ts)}.json", "wt") as outfile:
            outfile.write(json.dumps(result_json, indent=4))

        opfs[ts] = result_json
    return opfs


if __name__ == '__main__':
    app_dat.start()
