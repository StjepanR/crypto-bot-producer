import json
import logging

from coinbase.websocket import WSClient, WSClientConnectionClosedException, WSClientException
from service.producerService import Producer

SUBSCRIPTION_CHANNEL = "level2"

class CoinbaseSocket:

    def __init__(self, api_key, api_secret, verbose=True):
        self.ws_client = WSClient(api_key=api_key, api_secret=api_secret, on_message=self.on_message, verbose=verbose)
        self.producer = Producer()

    def start(self):
        logging.info("opening connection to socket")
        try:
            self.ws_client.open()
        except WSClientConnectionClosedException as e:
            logging.error("Connection closed! Retry attempts exhausted.", e)
        except WSClientException as e:
            print("Error encountered!", e)

    def subscribe(self, channel):
        logging.info("subscribing to channel: " + channel)
        try:
            self.ws_client.subscribe(product_ids=[channel], channels=[SUBSCRIPTION_CHANNEL])
        except Exception as e:
            logging.error("failed to subscribe to channel: " + channel, e)
            raise RuntimeError("failed to subscribe to channel: " + channel)

    def unsubscribe(self, channel):
        logging.info("unsubscribing from channel: " + channel)
        try:
            self.ws_client.unsubscribe(product_ids=[channel], channels=[SUBSCRIPTION_CHANNEL])
        except Exception as e:
            logging.error("failed to unsubscribe from channel: " + channel, e)
            raise RuntimeError("failed to unsubscribe from channel: " + channel)

    def close(self):
        logging.info("closing connection to socket")
        try:
            self.ws_client.close()
        except Exception as e:
            logging.error("closing coinbase socket failed", e)
            raise RuntimeError("closing coinbase socket failed")


    def on_message(self, message):
        try:
            logging.info("got new message: " + message)

            message_data = json.loads(message)

            if "channel" in message_data and message_data["channel"] == SUBSCRIPTION_CHANNEL:
                price_data = get_product_data(message_data)
                self.producer.produce(price_data["product_id"], price_data)

        except Exception as e:
            logging.error("failed processing message", e)
            raise RuntimeError("failed processing message")


def get_product_data(message_data):
    if "events" in message_data and len(message_data["events"]) > 0:
        event = message_data["events"][0]
        if "tickers" in event and len(event["tickers"]) > 0:
            ticker = event["tickers"][0]
            return ticker


def get_product_id(message_data):
    if "events" in message_data and len(message_data["events"]) > 0:
        event = message_data["events"][0]
        if "tickers" in event and len(event["tickers"]) > 0:
            ticker = event["tickers"][0]
            if "product_id" in ticker:
                return ticker["product_id"]
