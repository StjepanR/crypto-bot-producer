import collections
import logging

from service.coinbaseSocket import CoinbaseSocket
from service.kubernatesService import KubernetesService
from prometheus_fastapi_instrumentator import Instrumentator
from config.config import Config
from fastapi import FastAPI

config = Config()

logging.root.setLevel(logging.INFO)

app = FastAPI()
Instrumentator().instrument(app).expose(app)

kubernetesService = KubernetesService()

IMAGE = "stjepanruklic/crypto-bot-worker"
VERSION = "latest"
PORT = 5001
AVAILABLE_MODELS = {"lstm", "cnn", "dense", "gru"}

socket = CoinbaseSocket(api_key=config.coinbase_api_key, api_secret=config.coinbase_api_secret)
socket.start()

configurations = collections.defaultdict(set)


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

@app.get("/configurations/list")
async def list_streams():
    try:
        logging.info("fetching configurations")
        return configurations
    except Exception as e:
        logging.error("failed to fetch list of subscriptions", e)



@app.get("/stream/subscribe/{channel}")
async def subscribe(channel, model):
    channel = channel.lower()
    model = model.lower()
    configuration = channel + "-" + model
    logging.info("subscribing to configuration: " + configuration)

    if model in AVAILABLE_MODELS:
        logging.info("selected model is: " + model)
    elif model is None:
        logging.info("model is not specified")
        return {"message": "model is not specified"}
    else:
        logging.info("model is not supported")
        return {"message": "model: " + model + " is not supported"}

    if model in configurations[channel]:
        return {"message": "same configuration: " + channel + "-" + model + " is already being used"}

    configurations[channel].add(model)

    if "ticker" not in socket.ws_client.subscriptions.keys() or channel not in socket.ws_client.subscriptions["ticker"]:
        socket.subscribe(channel)

    deployment_name = configuration + "-worker"
    deployment = kubernetesService.create_deployment_object(channel, IMAGE + ":" + VERSION, PORT,
                                                            deployment_name, channel, model)
    kubernetesService.create_deployment(deployment, deployment_name)

    return {"message": "configuration: " + channel + "-" + model + " created"}


@app.get("/stream/unsubscribe/{channel}")
async def unsubscribe(channel, model):
    channel = channel.lower()
    model = model.lower()
    configuration = channel + "-" + model
    logging.info("unsubscribing from configuration: " + configuration)

    if model in AVAILABLE_MODELS:
        logging.info("selected model is: " + model)
    elif model is None:
        logging.info("model is not specified")
        return {"message": "model is not specified"}
    else:
        logging.info("model is not supported")
        return {"message": "model: " + model + " is not supported"}

    if model not in configurations[channel]:
        return {"message": "configuration: " + configuration + " is not being used"}

    configurations[channel].remove(model)

    if "ticker" in socket.ws_client.subscriptions.keys() and channel in socket.ws_client.subscriptions["ticker"]:
        socket.unsubscribe(channel)

    deployment_name = configuration + "-worker"
    kubernetesService.delete_deployment(deployment_name)

    return {"message": "configuration: " + channel + "-" + model + " deleted"}
