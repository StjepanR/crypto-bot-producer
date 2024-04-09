import json
import logging

from coinbase.websocket import WSClient, WSClientConnectionClosedException, WSClientException

class CoinbaseSocket:

    def __init__(self, api_key, api_secret, verbose=True):
        print(api_key)
        print(api_secret)
        self.ws_client = WSClient(api_key=api_key, api_secret=api_secret, on_message=self.on_message, verbose=verbose)

    def start(self):
        try:
            self.ws_client.open()
            self.subscribe("BTC-USD")
            self.ws_client.run_forever_with_exception_check()
        except WSClientConnectionClosedException as e:
            logging.error("Connection closed! Retry attempts exhausted.", e)
        except WSClientException as e:
            print("Error encountered!", e)

    def subscribe(self, channel):
        try:

            self.ws_client.subscribe(product_ids=list(channel), channels=["level2"])
        except:
            logging.info("failed to subscribe to channel: " + channel)
            raise RuntimeError("failed to subscribe to channel: " + channel)

    def unsubscribe(self, channel):
        try:
            self.ws_client.unsubscribe(list(channel), ["heartbeats", "ticker"])
        except:
            logging.info("failed to unsubscribe from channel: " + channel)
            raise RuntimeError("failed to unsubscribe from channel: " + channel)

    def on_message(self, message):
        try:
            message_data = json.loads(message)
            print(message_data)
        except:
            logging.info("failed processing message")
            raise RuntimeError("failed processing message")

    def close(self):
        try:
            self.ws_client.close()
        except:
            logging.info("closing coinbase socket failed")
            raise RuntimeError("closing coinbase socket failed")
