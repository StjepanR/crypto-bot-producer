import collections
import logging

from service.coinbaseSocket import CoinbaseSocket
from service.kubernatesService import KubernetesService
from config.config import Config
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

config = Config()

app = FastAPI()
Instrumentator().instrument(app).expose(app)

kubernetesService = KubernetesService()

deployments = collections.defaultdict(str)

IMAGE = "stjepanruklic/crypto-bot-worker"
VERSION = "latest"
PORT = 5001


def get_app():
    return app


async def producer(channel):
    socket = CoinbaseSocket(api_key=config.coinbase_api_key, api_secret=config.coinbase_api_secret, channel=channel)
    socket.start()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/stream/list")
async def list():
    return deployments.keys() if deployments.keys() else []


@app.get("/stream/subscribe/{channel}")
async def subscribe(channel):
    logging.info("subscribing to channel " + channel)

    deployment_name = channel.lower() + "-worker"

    if deployment_name not in deployments.keys():
        deployment = kubernetesService.create_deployment_object(channel, IMAGE + ":" + VERSION, 5001, deployment_name)
        kubernetesService.create_deployment(deployment, channel + "-worker")

        deployments[deployment_name] = deployment
    else:
        return {"message": "already subscribed to channel: " + channel}

    return {"message": "subscribed to channel: " + channel}


@app.delete("/stream/unsubscribe/{channel}")
async def unsubscribe(channel):
    logging.info("unsubscribing from channel: " + channel)

    deployment_name = channel.lower() + "-worker"

    if deployment_name in deployments.keys():
        kubernetesService.delete_deployment(deployment_name)
    else:
        return {"message": "not previously subscribed to channel: " + channel}

    return {"message": "unsubscribed from channel: " + channel}