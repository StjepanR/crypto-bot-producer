import json

from coinbase.websocket import WSClient
from config.logger import logger

class CoinbaseSocket:

    def __init__(self, api_key, api_secret, verbose=True):
        print(api_key)
        print(api_secret)
        self.ws_client = WSClient(api_key=api_key, api_secret=api_secret, on_message=self.on_message, verbose=verbose)

    def subscribe(self, channel):
        try:

            self.ws_client.subscribe(product_ids=list(channel), channels=["level2"])
        except:
            logger.info("failed to subscribe to channel: " + channel)
            raise RuntimeError("failed to subscribe to channel: " + channel)

    def unsubscribe(self, channel):
        try:
            self.ws_client.unsubscribe(list(channel), ["heartbeats", "ticker"])
        except:
            logger.info("failed to unsubscribe from channel: " + channel)
            raise RuntimeError("failed to unsubscribe from channel: " + channel)

    def on_message(self, message):
        try:
            message_data = json.loads(message)
            print(message_data)
        except:
            logger.info("failed processing message")
            raise RuntimeError("failed processing message")

    def close(self):
        try:
            self.ws_client.close()
        except:
            logger.info("closing coinbase socket failed")
            raise RuntimeError("closing coinbase socket failed")
