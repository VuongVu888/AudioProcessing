import functools
import logging
from concurrent.futures import ThreadPoolExecutor

import redis

from app.config.utils import config
from inference_workers.rabbitmq_subscriber import rabbitmq_consumer
from transcription_model.transcription_service import TranscriptionService

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -10s %(funcName) '
              '-10s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

transcription_srv = TranscriptionService()
redis_client = redis.Redis(host=config.REDIS_URL, port=config.REDIS_PORT)

executor = ThreadPoolExecutor(max_workers=5)

def ack_message(channel, delivery_tag):
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        pass

def do_work(ch, delivery_tag, properties, body):
    file_path = body.decode("utf-8")
    inference_result = transcription_srv.inference(file_paths=[file_path])
    redis_client.set(properties.headers["inference_id"], inference_result[0])

    cb = functools.partial(ack_message, ch, delivery_tag)
    ch.connection.add_callback_threadsafe(cb)

def on_message(ch, method_frame, properties, body):
    delivery_tag = method_frame.delivery_tag
    executor.submit(do_work, ch, delivery_tag, properties, body)

rabbitmq_consumer.connect(message_callback=on_message)
rabbitmq_consumer.consume()
