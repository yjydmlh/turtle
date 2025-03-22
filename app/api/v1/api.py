from fastapi import APIRouter
from app.api.v1.endpoints import kline

api_router = APIRouter()
api_router.include_router(kline.router, prefix="/kline", tags=["kline"]) 