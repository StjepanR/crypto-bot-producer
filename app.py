import collections
import threading
import logging

from service.coinbaseSocket import CoinbaseSocket
from config.config import Config
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

config = Config()

app = FastAPI()
Instrumentator().instrument(app).expose(app)

threads = collections.defaultdict(threading.Thread)


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
    return threads.keys() if threads.keys() else []


@app.get("/stream/subscribe/{channel}")
async def subscribe(channel):
    try:
        logging.info("subscribing to channel " + channel)
        thread = threading.Thread(target=producer, args=(channel,))
        threads[channel] = thread
        thread.start()

        return {"message": "subscribed to channel: " + channel}
    except:
        logging.log("failed to subscribed to channel: " + channel)
        raise RuntimeError("failed to subscribed to channel: " + channel)


@app.delete("/stream/unsubscribe/{channel}")
async def unsubscribe(channel):
    try:
        logging.info("unsubscribing from channel: " + channel)
        threads.get(channel).join()

        return {"message": "unsubscribed from channel: " + channel}
    except:
        logging.error("failed to unsubscribe from channel: " + channel)
        raise RuntimeError("failed to unsubscribe from channel: " + channel)
