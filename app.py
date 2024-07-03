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
AVAILABLE_MODELS = {"lstm", "conv", "dense", "gru", "arima", "prophet", "sarima", "naive"}
AVAILABLE_FREQUENCIES = {"1m", "1h", "1d"}
AVAILABLE_SCALERS = {"standard", "minmax", "maxabs", "robust", "none"}

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


@app.get("/stream/subscribe")
async def subscribe(channel, model, epochs="100", window_size="24", batch_size="32", frequency="1h", steps="24", scaler="none"):
    channel = str(channel).lower()
    model = str(model).lower()
    epochs = str(epochs)
    window_size = str(window_size)
    batch_size = str(batch_size)
    frequency = str(frequency).lower()
    steps = str(steps)
    scaler = str(scaler).lower()
    configuration = channel + "-" + model
    logging.info("subscribing to configuration: " + configuration)

    if frequency in AVAILABLE_FREQUENCIES:
        logging.info("selected frequency is: " + frequency)
    else:
        logging.info("frequency value is not supported")
        return {"message": "frequency: " + frequency + " is not supported",
                "hint": "values 1m, 1h and 1d are supported"}

    if steps.isdigit() and 0 < int(steps) < 100:
        logging.info("selected steps value is: " + steps)
    else:
        logging.info("steps value is not supported")
        return {"message": "steps: " + steps + " is not supported", "hint": "specify positive integer less than 100"}

    if epochs.isdigit():
        logging.info("selected epochs value is: " + epochs)
    else:
        logging.info("epochs value is not supported")
        return {"message": "epochs: " + epochs + " is not supported",
                "hint": "specify positive integer"}

    if window_size.isdigit():
        logging.info("selected window size value is: " + window_size)
    else:
        logging.info("window size value is not supported")
        return {"message": "window size: " + window_size + " is not supported",
                "hint": "specify positive integer less than 100"}

    if batch_size.isdigit() and 0 < int(window_size) < 1000:
        logging.info("selected batch size value is: " + batch_size)
    else:
        logging.info("batch size value is not supported")
        return {"message": "batch size: " + batch_size + " is not supported", "hint": "specify positive integer"}

    if scaler in AVAILABLE_SCALERS:
        logging.info("selected scaler is: " + scaler)
    else:
        logging.info("scaler is not supported")
        return {"message": "scaler: " + scaler + " is not supported", "hint": "supported scalers are: \"standard\", \"minmax\", \"maxabs\", \"robust\", \"none\""}

    if model in AVAILABLE_MODELS:
        logging.info("selected model is: " + model)
    elif model is None:
        logging.info("model value is not specified")
        return {"message": "model is not specified",
                "hint": "supported models are: \"lstm\", \"conv\", \"dense\", \"gru\", \"arima\", \"prophet\", \"sarima\", \"naive\""}
    else:
        logging.info("model is not supported")
        return {"message": "model: " + model + " is not supported",
                "hint": "supported models are: \"lstm\", \"conv\", \"dense\", \"gru\", \"arima\", \"prophet\", \"sarima\", \"naive\""}

    if model in configurations[channel]:
        return {"message": "same configuration: " + channel + "-" + model + " is already being used"}

    configurations[channel].add(model)

    if "ticker" not in socket.ws_client.subscriptions.keys() or channel not in socket.ws_client.subscriptions["ticker"]:
        socket.subscribe(channel)

    deployment_name = configuration + "-worker"
    deployment = kubernetesService.create_deployment_object(channel, IMAGE + ":" + VERSION, PORT,
                                                            deployment_name, channel, model, frequency, steps, epochs,
                                                            window_size, batch_size)
    kubernetesService.create_deployment(deployment, deployment_name)

    return {"message": "configuration: " + channel + "-" + model + " created"}


@app.get("/stream/unsubscribe")
async def unsubscribe(channel, model):
    channel = str(channel).lower()
    model = str(model).lower()
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
