import os


class Config:
    def __init__(self):
        self.kafka_broker_url = "crypto-bot-kafka.default.svc.cluster.local:9092"
        self.coinbase_api_key = os.environ.get("COINBASE_API_KEY")
        self.coinbase_api_secret = os.environ.get("COINBASE_API_SECRET")
