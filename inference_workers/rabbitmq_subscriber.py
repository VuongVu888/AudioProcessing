import logging

import pika
from pika.exchange_type import ExchangeType

from app.config.const import RABBITMQ_EXCHANGE, RABBITMQ_QUEUE, RABBITMQ_ROUTING_KEY
from app.config.utils import config

logger = logging.getLogger(__file__)

class RabbitMQSubsriber:
    def __init__(self, host, port, username, password):
        self._params = pika.connection.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.credentials.PlainCredentials(username, password),
        )
        self._conn = None
        self._channel = None

    def connect(self, message_callback):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.exchange_declare(exchange=RABBITMQ_EXCHANGE,
                                           exchange_type=ExchangeType.fanout,
                                           passive=False,
                                           durable=True,
                                           auto_delete=False)
            self._channel.queue_declare(queue=RABBITMQ_QUEUE)
            self._channel.queue_bind(
                queue=RABBITMQ_QUEUE,
                exchange=RABBITMQ_EXCHANGE,
                routing_key=RABBITMQ_ROUTING_KEY,
            )
            self._channel.basic_qos(prefetch_count=8)
            self._channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=message_callback,
            )

    def consume(self):
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            self._channel.stop_consuming()
            self.close()

    def close(self):
        if self._conn and self._conn.is_open:
            logger.debug('closing queue connection')
            self._channel.close()
            self._conn.close()

rabbitmq_consumer = RabbitMQSubsriber(
    host=config.RABBITMQ_URL,
    port=config.RABBITMQ_PORT,
    username=config.RABBITMQ_USER,
    password=config.RABBITMQ_PASSWORD,
)
