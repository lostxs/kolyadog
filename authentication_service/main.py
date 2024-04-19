import asyncio
import logging
import os
from uuid import UUID

import uvicorn
from fastapi import FastAPI, APIRouter, WebSocketDisconnect, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from api.actions.auth import check_token_expiration
from api.broker import setup_consumer, handle_user_created, handle_user_activated
from api.handlers import auth_router
from rabbitmq import get_rabbit_connection
from db.redis import get_redis_auth_pool

app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

main_api_router = APIRouter()
main_api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(main_api_router)


@app.on_event("startup")
async def startup_event():
    await get_redis_auth_pool()
    await get_rabbit_connection()
    consumer_tasks = [
        asyncio.create_task(
            setup_consumer('auth_user_events_queue', 'user.created', handle_user_created),
            name="consumer_user_created"
        ),
        asyncio.create_task(
            setup_consumer('auth_activated_events_queue', 'user.activated', handle_user_activated),
            name="consumer_user_activated"
        )
    ]
    await asyncio.gather(*consumer_tasks)


@app.on_event("shutdown")
async def shutdown_event():
    redis_pool = await get_redis_auth_pool()
    rabit_pool = await get_rabbit_connection()
    await redis_pool.close()
    await rabit_pool.close()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
            session_active = await check_token_expiration(user_id)
            if not session_active:
                await websocket.send_json({"error": "Session expired"})
                break

            await websocket.send_json({"message": "Session is active"})
    except WebSocketDisconnect:
        logging.info("Client disconnected")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "8000")),
    )
