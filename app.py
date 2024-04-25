import logging

from service.coinbaseSocket import CoinbaseSocket
from service.kubernatesService import KubernetesService
from prometheus_fastapi_instrumentator import Instrumentator
from config.config import Config
from fastapi import FastAPI

config = Config()

app = FastAPI()
Instrumentator().instrument(app).expose(app)

kubernetesService = KubernetesService()

IMAGE = "stjepanruklic/crypto-bot-worker"
VERSION = "latest"
PORT = 5001

socket = CoinbaseSocket(api_key=config.coinbase_api_key, api_secret=config.coinbase_api_secret)
socket.start()


@app.get("/")
async def root():
    return {"status": "up"}


@app.get("/stream/list")
async def list_streams():
    try:
        logging.info("fetching subscriptions")
        return socket.ws_client.subscriptions
    except Exception as e:
        logging.error("failed to fetch list of subscriptions", e)


@app.get("/stream/subscribe/{channel}")
async def subscribe(channel):
    logging.info("subscribing to channel: " + channel)

    deployment_name = channel.lower() + "-worker"

    if deployment_name not in socket.ws_client.subscriptions["ticker"]:
        deployment = kubernetesService.create_deployment_object(channel.lower(), IMAGE + ":" + VERSION, PORT,
                                                                deployment_name, channel)
        kubernetesService.create_deployment(deployment, deployment_name)
    else:
        return {"message": "already subscribed to channel: " + channel}

    return {"message": "subscribed to channel: " + channel}


@app.delete("/stream/unsubscribe/{channel}")
async def unsubscribe(channel):
    logging.info("unsubscribing from channel: " + channel)

    deployment_name = channel.lower() + "-worker"

    if deployment_name in socket.ws_client.subscriptions["ticker"]:
        kubernetesService.delete_deployment(deployment_name)
    else:
        return {"message": "not previously subscribed to channel: " + channel}

    return {"message": "unsubscribed from channel: " + channel}
