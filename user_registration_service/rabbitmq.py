import asyncio
import ssl

from aio_pika import connect_robust


async def get_rabbit_connection():
    ssl_context = ssl.create_default_context(cafile="/app/certs/ca.crt")
    ssl_context.load_cert_chain(
        "/app/certs/client.crt",
        "/app/certs/client.key"
    )

    return await connect_robust(
        url="amqps://user:user@rabbitmq:5671/",
        virtual_host="/",
        loop=asyncio.get_running_loop(),
        ssl_context=ssl_context
    )
