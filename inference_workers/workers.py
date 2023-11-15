import functools
import logging
import pickle
import threading
import time

from app.config.const import RABBITMQ_QUEUE
from inference_workers.rabbitmq_bridge import rabbitmq_client, redis_client

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -10s %(funcName) '
              '-10s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

def ack_message(channel, delivery_tag):
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        pass


def do_work(ch, delivery_tag, header_frame, body):
    thread_id = threading.get_ident()
    LOGGER.info('Thread id: %s Delivery tag: %s Message body: %s', thread_id,
                delivery_tag, body)

    # Sleeping to simulate 10 seconds of work
    time.sleep(1)
    audio_content = pickle.loads(body)
    redis_client.set(header_frame.headers["inference_id"], "HELLO WORLD")

    cb = functools.partial(ack_message, ch, delivery_tag)
    ch.connection.add_callback_threadsafe(cb)


def on_message(ch, method_frame, header_frame, body, args):
    thrds = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=do_work, args=(ch, delivery_tag, header_frame, body))
    thrds.append(t)
    t.start()


threads = []
on_message_callback = functools.partial(on_message, args=(threads))
rabbitmq_client.basic_qos(prefetch_count=4)
rabbitmq_client.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=on_message_callback)

try:
    rabbitmq_client.start_consuming()
except KeyboardInterrupt:
    rabbitmq_client.stop_consuming()

# Wait for all to complete
LOGGER.info(f"Number of Workers: {len(threads)}")
for thread in threads:
    thread.join()

rabbitmq_client.close()