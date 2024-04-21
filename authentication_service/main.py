import asyncio
import os
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

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


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "8000")),
    )
