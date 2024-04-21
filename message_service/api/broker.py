import json
import logging

from aio_pika import IncomingMessage, ExchangeType
from sqlalchemy.future import select

from rabbitmq import get_rabbit_connection
from db.session import async_session
from db.models import User


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_consumer(queue_name, routing_key, handler_function):
    logger.info(f"Setting up consumer for {routing_key} events.")
    connection = await get_rabbit_connection()
    channel = await connection.channel()

    exchange = await channel.declare_exchange('user_exchange', ExchangeType.DIRECT, durable=True)
    queue = await channel.declare_queue(queue_name, durable=True)
    await queue.bind(exchange, routing_key=routing_key)
    await queue.consume(handler_function)
    logger.info(f"Consumer for {routing_key} events setup complete. Waiting for messages...")


async def handle_user_created(message: IncomingMessage):
    async with message.process():
        user_data = json.loads(message.body.decode('utf-8'))
        logger.info(f"Processing user created event for: {user_data['username']}")
        async with async_session() as session:
            try:
                async with session.begin():
                    existing_user = await session.execute(select(User).where(User.username == user_data['username']))
                    if existing_user.scalar_one_or_none():
                        logger.info(f"User with email {user_data['username']} already exists.")
                        return
                    message_user = User(
                        user_id=user_data['user_id'],
                        username=user_data['username'],
                        is_active=user_data['is_active']
                    )
                    session.add(message_user)
                    await session.commit()
                    logger.info(f"User {user_data['username']} added or confirmed in message DB.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to add user {user_data['username']}: {str(e)}")


async def handle_user_activated(message: IncomingMessage):
    async with message.process():
        user_data = json.loads(message.body.decode('utf-8'))
        logger.info(f"Processing user activation for: {user_data['user_id']}")
        async with async_session() as session:
            async with session.begin():
                user = await session.get(User, user_data['user_id'])
                if not user:
                    logger.error("User not found")
                    return
                user.is_active = user_data['is_active']
                await session.commit()
                logger.info(f"User {user.user_id} activation status updated to {user.is_active}")
