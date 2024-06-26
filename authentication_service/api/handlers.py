import logging
from datetime import timedelta
import settings
from security import create_access_token

from fastapi import APIRouter, Depends, HTTPException, status, Response, WebSocket, WebSocketDisconnect, Query
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from api.actions.auth import authenticate_user, _get_user_by_email_for_auth, check_token_expiration, verify_token
from db.session import get_db


auth_router = APIRouter()


@auth_router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        user_inactive = await _get_user_by_email_for_auth(form_data.username, db)
        if user_inactive and not user_inactive.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not activated, please activate your account",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        user_id=user.user_id,
        expires_delta=access_token_expires,
        # additional_claims={"username": user.username}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",
    )
    return {"message": "Authentication successful"}


@auth_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    await websocket.accept()
    user_id, token_valid = await verify_token(token)
    if not token_valid:
        await websocket.close(code=4001)
        return

    logging.info(f"User {user_id} connected via websocket.")
    try:
        while True:
            message = await websocket.receive_text()
            session_active = await check_token_expiration(user_id)
            if not session_active:
                await websocket.send_json({"error": "Session expired"})
                await websocket.close(code=1000)
                break
            await websocket.send_json({"message": "Session is active, message received: " + message})
    except WebSocketDisconnect:
        logging.info(f"User {user_id} disconnected")
