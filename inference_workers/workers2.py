import functools
import logging
import sys
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, cpu_count

import redis

from app.config.const import RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY, RABBITMQ_QUEUE
from app.config.utils import config
from inference_workers.rabbitmq_client import RabbitMQConnector
from transcription_model.transcription_service import TranscriptionService

LOGGER = logging.getLogger(__name__)

_ONE_DAY = datetime.timedelta(days=1)
NUMBER_OF_CPU = cpu_count()
THREAD_CONCURRENCY = NUMBER_OF_CPU

def ack_message(channel, delivery_tag):
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        pass

def do_work(properties, body, executor, transcription_srv, redis_client):
    file_path = body.decode("utf-8")
    inference_result = transcription_srv.inference(file_paths=[file_path])
    inference_id = properties.headers["inference_id"]
    executor.submit(redis_client.set, inference_id, inference_result[0])
    LOGGER.info(f"Inference Result for %s: %s", inference_id, inference_result)

# def on_message(ch, method_frame, properties, body, executor, transcription_srv, redis_client):
#     delivery_tag = method_frame.delivery_tag
#     do_work(ch, delivery_tag, properties, body, executor, transcription_srv, redis_client)

def _wait_forever():
    try:
        while True:
            time.sleep(_ONE_DAY.total_seconds())
    except KeyboardInterrupt:
        pass

def subprocess_main():
    executor = ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY)
    transcription_srv = TranscriptionService()
    redis_client = redis.Redis(host=config.REDIS_URL, port=config.REDIS_PORT)
    on_message_callback = functools.partial(
        do_work,
        executor=executor,
        transcription_srv=transcription_srv,
        redis_client=redis_client,
    )
    rabbitmq_consumer = RabbitMQConnector(
        host=config.RABBITMQ_URL,
        port=config.RABBITMQ_PORT,
        username=config.RABBITMQ_USER,
        password=config.RABBITMQ_PASSWORD,
    )
    rabbitmq_consumer.receive(
        exchange=RABBITMQ_EXCHANGE,
        routing_key=RABBITMQ_ROUTING_KEY,
        queue_name=RABBITMQ_QUEUE,
        handler=on_message_callback,
        prefetch_count=5,
    )
    _wait_forever()

def main():
    workers = []
    for _ in range(NUMBER_OF_CPU):
        worker = Process(
            target=subprocess_main
        )
        workers.append(worker)
        worker.start()

    for i in range(len(workers)):
        LOGGER.info("Starting consumer %d", i + 1)

    for worker in workers:
        worker.join()

if __name__ == "__main__":
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[PID %(process)d] %(message)s")
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)

    LOGGER.info(f"Process Pool Size: %d", NUMBER_OF_CPU)
    main()
