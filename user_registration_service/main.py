import logging
import os
import uvicorn
from fastapi import FastAPI, APIRouter

from api.handlers import user_router
# from rabbitmq import get_rabbit_connection

app = FastAPI()

main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)


# @app.on_event("startup")
# async def startup_event():
#     await get_rabbit_connection()


# @app.on_event("shutdown")
# async def shutdown_event():
#     rabbit_connection = await get_rabbit_connection()
#     await rabbit_connection.close()


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "8000"))
    )
