from fastapi import HTTPException, Request
from pydantic import BaseModel
import logging
from .config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = ["User", "get_user"]


class User(BaseModel):
    access_token: str


def get_user(request: Request):
    logger.warning(f"Request data: {request}")
    logger.warning(f"Session data: {request.session}")
    user = request.session.get("user")
    logger.warning(f"User data from session: {user}")
    override_access_tok = settings.github_access_token_override
    if override_access_tok:
        user = {"access_token": override_access_tok}
        logger.warning(f"User data overridden: {user}")
    if not user:
        logger.warning("User not found in session")
        raise HTTPException(status_code=401, detail="User not authenticated")
    return User(**user)
