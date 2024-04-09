import uvicorn
from coinbase.websocket import WSClientConnectionClosedException, WSClientException

from service.coinbaseSocket import CoinbaseSocket

from config.config import Config
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

def get_app():
    return app

@app.get("/")
async def root():
    return {"message": "Hello World"}

Instrumentator().instrument(app).expose(app)

if __name__=="__main__":
    config = Config()

    try:
        socket = CoinbaseSocket(config.coinbase_api_key, config.coinbase_api_secret)
        socket.ws_client.open()
        socket.subscribe("BTC-USD")
        socket.ws_client.run_forever_with_exception_check()
    except WSClientConnectionClosedException as e:
        print("Connection closed! Retry attempts exhausted.")
    except WSClientException as e:
        print("Error encountered!")

    uvicorn.run(app, host=config.host, port=config.port)