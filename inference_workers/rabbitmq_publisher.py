import logging

import pika
from pika import BasicProperties
from pika.exchange_type import ExchangeType

from app.config.const import RABBITMQ_QUEUE, RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY
from app.config.utils import config

logger = logging.getLogger(__file__)

class RabbitMQPublisher:
    def __init__(self, host, port, username, password):
        self._params = pika.connection.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.credentials.PlainCredentials(username, password),
        )
        self._conn = None
        self._channel = None

    def connect(self):
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

    def _publish(self, msg, headers=None):
        if not self._conn or self._conn.is_closed:
            self.connect()
        self._channel.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key=RABBITMQ_ROUTING_KEY,
            body=msg,
            properties=BasicProperties(
                headers=headers,
            )
        )
        logger.debug('message sent: %s', msg)

    def publish(self, msg, headers=None):
        try:
            self._publish(msg, headers)
        except pika.exceptions.ConnectionClosed:
            logger.debug('reconnecting to queue')
            self.connect()
            self._publish(msg)
        except pika.exceptions.AMQPConnectionError as e:
            logger.debug('EOF Connection', e)
            self.connect()
            self._publish(msg)

    def close(self):
        if self._conn and self._conn.is_open:
            logger.debug('closing queue connection')
            self._conn.close()

rabbitmq_publisher = RabbitMQPublisher(
    host=config.RABBITMQ_URL,
    port=config.RABBITMQ_PORT,
    username=config.RABBITMQ_USER,
    password=config.RABBITMQ_PASSWORD,
)
