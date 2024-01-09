import sys
import json
import asyncio
import logging

from spa_dat.application.application import DistributedApplication
from spa_dat.config import PayloadFormat, SocketConfig
from spa_dat.provider import SocketProviderFactory
from spa_dat.socket.mqtt import MqttConfig
from spa_dat.socket.typedef import SpaMessage, SpaSocket

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

# spa configuration
socket_provider = SocketProviderFactory.from_config(
    SocketConfig(payload_format=PayloadFormat.JSON, socket_config=MqttConfig(host="localhost", port=1883))
)
app_dat = DistributedApplication(socket_provider)
# app_dat2 = DistributedApplication(socket_provider)

test_config = {
    "lat": 48.399, 
    "lon": 14.513,
    "peakpower": 1,
    "angle": 22,
    "aspect": 0
}

# @app_dat2.producer()
# async def query_consumers(socket: SpaSocket, state):
#     # # query consumers
#     consumers_response = await socket.request(
#         SpaMessage(
#             payload = "",
#             topic = "consumer/all",
#             response_topic = "consumer/all/response"
#         )
#     )
#     logging.debug("received consumers=%s", consumers_response)

@app_dat.producer()
async def main(socket: SpaSocket, state):
    logging.debug("query pvnode")
    pvnode_response = await socket.request(
        SpaMessage(
            payload = json.dumps(test_config),
            topic = "pvnode/1/model",
            response_topic = "pvnode/1/model/response"
        )
    )
    logging.debug("received pvnode_response=%s", pvnode_response)

if __name__ == '__main__':
    app_dat.start()
