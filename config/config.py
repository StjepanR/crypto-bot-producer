import yaml
import os

class Config:
    def __init__(self):
        with open("./config/config.yml", "r") as f:
            config = yaml.safe_load(f)
        self.host = config["host"]
        self.port = config["port"]
        self.kafka_broker_url = config["kafka-broker-url"]
        self.coinbase_api_key = os.environ.get("COINBASE_API_KEY")
        self.coinbase_api_secret = os.environ.get("COINBASE_API_SECRET")
