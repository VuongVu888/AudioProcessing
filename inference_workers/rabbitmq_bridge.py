import pika
from pika import PlainCredentials
from pika.exchange_type import ExchangeType
import redis

from app.config.utils import config
from app.config.const import RABBITMQ_QUEUE, RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=config.RABBITMQ_URL,
        port=config.RABBITMQ_PORT,
        credentials=PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD),
        heartbeat=5,
    )
)
rabbitmq_client = connection.channel()
rabbitmq_client.exchange_declare(
    exchange=RABBITMQ_EXCHANGE,
    exchange_type=ExchangeType.fanout,
    passive=False,
    durable=True,
    auto_delete=False,
)
rabbitmq_client.queue_declare(queue=RABBITMQ_QUEUE)
rabbitmq_client.queue_bind(
    queue=RABBITMQ_QUEUE,
    exchange=RABBITMQ_EXCHANGE,
    routing_key=RABBITMQ_ROUTING_KEY,
)

redis_client = redis.Redis(host=config.REDIS_URL, port=config.REDIS_PORT)
