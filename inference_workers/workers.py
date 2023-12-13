import functools
import logging
import sys
from concurrent.futures import ThreadPoolExecutor

import redis

from app.config.utils import config
from inference_workers.rabbitmq_subscriber import rabbitmq_consumer
from transcription_model.transcription_service import TranscriptionService

LOGGER = logging.getLogger(__name__)

transcription_srv = TranscriptionService()
redis_client = redis.Redis(host=config.REDIS_URL, port=config.REDIS_PORT)

executor = ThreadPoolExecutor(max_workers=20)

def ack_message(channel, delivery_tag):
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        pass

def do_work(ch, delivery_tag, properties, body):
    file_path = body.decode("utf-8")
    inference_result = transcription_srv.inference(file_paths=[file_path])
    redis_client.set(properties.headers["inference_id"], inference_result[0])
    # executor.submit(redis_client.set, properties.headers["inference_id"], inference_result[0])

    cb = functools.partial(ack_message, ch, delivery_tag)
    ch.connection.add_callback_threadsafe(cb)

def on_message(ch, method_frame, properties, body):
    delivery_tag = method_frame.delivery_tag
    executor.submit(do_work, ch, delivery_tag, properties, body)

def main():
    rabbitmq_consumer.connect(message_callback=on_message)
    rabbitmq_consumer.consume()

if __name__ == "__main__":
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[PID %(process)d] %(message)s")
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)

    main()
