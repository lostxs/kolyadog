import logging
import os

import uvicorn
from fastapi import FastAPI, APIRouter

from api.handlers import user_router
from rabbitmq import get_rabbit_connection

app = FastAPI()

main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)


@app.on_event("startup")
async def startup_event():
    await get_rabbit_connection()


@app.on_event("shutdown")
async def shutdown_event():
    rabbit_connection = await get_rabbit_connection()
    await rabbit_connection.close()


logging.basicConfig(level=logging.INFO)

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
