from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
from config import Config

def create_app():
    app = Flask(__name__)

    metrics = PrometheusMetrics(app)
    metrics.info("app_info", "Crypto Bot application for trading with crypto currencies", version="1.0.0")

    @app.route("/")
    def hello_world():
        return "Hello, Docker!"

    return app

if __name__=="__main__":
    config = Config().get_config()

    app = create_app()
    app.run(host=config["host"], port=config["port"])