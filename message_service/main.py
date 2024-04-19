import asyncio
import logging
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, APIRouter, Depends, WebSocketDisconnect, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from starlette.websockets import WebSocket

from api.actions.auth import authenticate_user_via_redis, get_user_details_by_id, query_or_cookie_extractor
from api.broker import setup_consumer, handle_user_created, handle_user_activated
from db.session import get_db

from rabbitmq import get_rabbit_connection
from db.redis import get_redis_messages_pool, get_redis_auth_pool
from websocket.actions import manager, handle_messages, handle_websocket_disconnect

app = FastAPI()

main_api_router = APIRouter()
app.include_router(main_api_router)


@app.on_event("startup")
async def startup_event():
    await get_redis_messages_pool()
    await get_redis_auth_pool()
    await get_rabbit_connection()
    consumer_tasks = [
        asyncio.create_task(
            setup_consumer('msg_user_events_queue', 'user.created', handle_user_created),
            name="consumer_user_created"
        ),
        asyncio.create_task(
            setup_consumer('msg_activated_events_queue', 'user.activated', handle_user_activated),
            name="consumer_user_activated"
        )
    ]
    await asyncio.gather(*consumer_tasks)


@app.on_event("shutdown")
async def shutdown_event():
    redis_pool_messages = await get_redis_messages_pool()
    redis_pool_auth = await get_redis_auth_pool()
    rabit_pool = await get_rabbit_connection()
    await redis_pool_messages.close()
    await redis_pool_auth.close()
    await rabit_pool.close()


@app.websocket("/ws/")
async def websocket_endpoint(
        websocket: WebSocket,
        q: Optional[str] = Depends(query_or_cookie_extractor),
        redis_auth: Redis = Depends(get_redis_auth_pool),
        redis_messages: Redis = Depends(get_redis_messages_pool),
        db: AsyncSession = Depends(get_db)
):
    user = None
    try:
        user_id = await authenticate_user_via_redis(q, redis_auth)
        user = await get_user_details_by_id(db, user_id)
        await manager.connect(websocket, user, db, redis_messages)
        join_message = f"Client #{user.username} joined the chat."
        await manager.broadcast_message(
            join_message, user.username, websocket, system_message=True
        )
        await handle_messages(websocket, user, db, redis_messages)
    except WebSocketDisconnect:
        if user:
            await handle_websocket_disconnect(user, websocket, db)
    except Exception as e:
        logging.error(f"error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


if __name__ == "__main__":
    key_path = "/app/certs/server.key"
    cert_path = "/app/certs/server.crt"
    logging.info(f"Using SSL key: {key_path}")
    logging.info(f"Using SSL certificate: {cert_path}")

    if not os.path.exists(key_path) or not os.path.exists(cert_path):
        logging.error("SSL certificate or key file does not exist.")
    else:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("APP_PORT", "8000")),
            ssl_keyfile=key_path,
            ssl_certfile=cert_path
        )
