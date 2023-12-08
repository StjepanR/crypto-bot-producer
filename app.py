import uvicorn

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
    config = Config().get_config()

    uvicorn.run(app, host=config["host"], port=config["port"])