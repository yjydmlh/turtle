from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import os

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
    title=settings.PROJECT_NAME,
    description="缠论自动化交易系统 API - 集成Chan模块的专业技术分析",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# 注册全局异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 配置CORS - 支持前端开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # SvelteKit dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 创建静态文件目录
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# 挂载静态文件 - 用于部署前端
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 根路径 - 如果有前端构建文件就显示，否则显示API信息
@app.get("/")
async def root():
    frontend_index = os.path.join(static_dir, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    else:
        return {
            "message": "🐢 缠论分析系统 API",
            "version": "2.0.0",
            "features": [
                "K线数据聚合 (1m -> 5m,15m,1h,4h,1d)",
                "Chan模块集成 (分型、笔、线段分析)",
                "实时数据获取 (币安API)",
                "专业缠论分析 (买卖点识别)",
                "Svelte前端界面"
            ],
            "api_docs": f"/api/v1/docs",
            "frontend": "部署前端后可在根路径访问",
            "getting_started": {
                "1": "访问 /api/v1/docs 查看API文档",
                "2": "POST /api/v1/simple/fetch-data 获取数据",
                "3": "GET /api/v1/chan/analyze 进行缠论分析"
            }
        }

# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "缠论分析系统运行正常",
        "version": "2.0.0",
        "components": {
            "api": "运行中",
            "database": "已连接",
            "chan_module": "已集成"
        }
    }

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    app_logger.info("🐢 缠论分析系统启动中...")
    app_logger.info(f"📊 API文档: http://localhost:{settings.PORT}{settings.API_V1_STR}/docs")
    app_logger.info(f"🌐 健康检查: http://localhost:{settings.PORT}/health")
    app_logger.info(f"🔗 API根地址: http://localhost:{settings.PORT}{settings.API_V1_STR}")

@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("🐢 缠论分析系统关闭...")