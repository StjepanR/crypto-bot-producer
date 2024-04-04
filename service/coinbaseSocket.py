from coinbase.websocket import WSClient
import json
import math

class CoinbaseSocket:

    def __init__(self, api_key, api_secret, verbose=True):
        self.ws_client = WSClient(api_key=api_key, api_secret=api_secret, on_message=self.on_message, verbose=verbose)

    def subscribe(self, channel):
        print(channel)

    def unsubscribe(self, channel):
        print(channel)

    def on_message(self, message):
        message_data = json.loads(message)
        print(message_data)
