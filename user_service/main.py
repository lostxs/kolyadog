import logging
import os

import uvicorn
from fastapi import FastAPI, APIRouter

app = FastAPI()

main_api_router = APIRouter()
app.include_router(main_api_router)


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
