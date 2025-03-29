from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.core.logger import app_logger

app = FastAPI(
    title=settings.APP_NAME,
    description="Trading System API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# 注册全局异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    app_logger.info("Application startup...")

@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("Application shutdown...") 