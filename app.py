from service.coinbaseSocket import CoinbaseSocket
from config.config import Config
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

config = Config()

app = FastAPI()
Instrumentator().instrument(app).expose(app)

socket = CoinbaseSocket(config.coinbase_api_key, config.coinbase_api_secret)
socket.start("BTC-USD")

def get_app():
    return app

@app.get("/")
async def root():
    return {"message": "Hello World"}