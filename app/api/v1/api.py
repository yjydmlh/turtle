from fastapi import APIRouter
from app.api.v1.endpoints import kline, kline_simple, chan_analysis, kline_database

api_router = APIRouter()

# 原有的详细K线API
api_router.include_router(kline.router, prefix="/kline", tags=["kline-detailed"])

# 新增的简化K线API - 支持多时间周期聚合
api_router.include_router(kline_simple.router, prefix="/simple", tags=["kline-simple"])

# 新增的数据库K线API - 直接从PostgreSQL查询btc_usdt表
api_router.include_router(kline_database.router, prefix="/database", tags=["kline-database"])

# 新增的缠论分析API - 集成Chan模块
api_router.include_router(chan_analysis.router, prefix="/chan", tags=["chan-analysis"])