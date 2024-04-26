import logging
import ssl

from kafka import KafkaProducer
from config.config import Config

sasl_mechanism = 'PLAIN'
security_protocol = 'SASL_PLAINTEXT'

# Create a new context using system defaults, disable all but TLS1.2
context = ssl.create_default_context()
context.options &= ssl.OP_NO_TLSv1
context.options &= ssl.OP_NO_TLSv1_1


class Producer:
    def __init__(self):
        config = Config()
        self.producer = KafkaProducer(bootstrap_servers=[config.kafka_broker_url])

    def produce(self, topic, message):
        logging.info("sending message to topic: " + topic)
        (self.producer
         .send(topic, message)
         .add_callback(self.on_send_success)
         .add_errback(self.on_send_error))

    def on_send_success(self, metadata):
        logging.info("message sent to topic: " + metadata.topic)

    def on_send_error(self, e):
        logging.error("error occurred sending message", exc_info=e)
