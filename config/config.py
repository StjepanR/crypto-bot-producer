import os


class Config:
    def __init__(self):
        self.kafka_broker_url = "crypto-bot-kafka.default.svc.cluster.local:9092"
        self.coinbase_api_key = os.getenv("COINBASE_API_KEY")
        self.coinbase_api_secret = os.getenv("COINBASE_API_SECRET")
