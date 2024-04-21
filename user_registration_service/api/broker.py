# import json

# from aio_pika import Message, ExchangeType

# from rabbitmq import get_rabbit_connection


# async def publish_user_created_event(user_data):
#     connection = await get_rabbit_connection()
#     async with connection:
#         channel = await connection.channel()
#         exchange = await channel.declare_exchange('user_exchange', ExchangeType.DIRECT, durable=True)
#         message = Message(
#             json.dumps(user_data).encode('utf-8'),
#             delivery_mode=2
#         )
#         await exchange.publish(
#             message, routing_key="user.created"
#         )


# async def publish_user_activated_event(user_data):
#     connection = await get_rabbit_connection()
#     async with connection:
#         channel = await connection.channel()
#         exchange = await channel.declare_exchange('user_exchange', ExchangeType.DIRECT, durable=True)
#         message = Message(
#             json.dumps(user_data).encode('utf-8'),
#             delivery_mode=2
#         )
#         await exchange.publish(
#             message, routing_key="user.activated"
#         )
