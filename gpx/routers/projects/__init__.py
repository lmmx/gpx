from fastapi import APIRouter
from . import add, get

__all__ = ["router"]

router = APIRouter()
router.include_router(add.router)
router.include_router(get.router)
