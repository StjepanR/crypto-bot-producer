import logging
import ssl
import json

from kafka import KafkaProducer
from config.config import Config


class Producer:
    def __init__(self):
        config = Config()
        self.producer = KafkaProducer(bootstrap_servers=[config.kafka_broker_url],
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def produce(self, topic, message):
        topic = topic.lower()
        logging.info("sending message to topic: " + topic)
        (self.producer
         .send(topic=topic, value=message)
         .add_callback(on_send_success)
         .add_errback(on_send_error))
        self.producer.flush()

def on_send_success(metadata):
    logging.info("message sent to topic: " + metadata.topic)


def on_send_error(e):
    logging.error("error occurred sending message", exc_info=e)
