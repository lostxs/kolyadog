import json
import logging

from aio_pika import IncomingMessage, ExchangeType
from sqlalchemy import select

from db.models import AuthUser
from rabbitmq import get_rabbit_connection
from db.session import async_session

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
        logger.info(f"Processing user created event for: {user_data['email']}")
        async with async_session() as session:
            try:
                async with session.begin():
                    existing_user = await session.execute(select(AuthUser).where(AuthUser.email == user_data['email']))
                    if existing_user.scalar_one_or_none():
                        logger.info(f"User with email {user_data['email']} already exists.")
                        return
                    auth_user = AuthUser(
                        user_id=user_data['user_id'],
                        email=user_data['email'],
                        hashed_password=user_data['hashed_password'],
                        is_active=user_data['is_active']
                    )
                    session.add(auth_user)
                    await session.commit()
                    logger.info(f"User {user_data['email']} added to authentication DB.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to add user {user_data['email']}: {str(e)}")


async def handle_user_activated(message: IncomingMessage):
    async with message.process():
        user_data = json.loads(message.body.decode('utf-8'))
        logger.info(f"Activating user: {user_data['user_id']}")
        async with async_session() as session:
            async with session.begin():
                user = await session.get(AuthUser, user_data['user_id'])
                if not user:
                    logger.error("User not found")
                    return
                user.is_active = user_data['is_active']
                await session.commit()
                logger.info(f"User {user.user_id} activation status updated to {user.is_active}")
