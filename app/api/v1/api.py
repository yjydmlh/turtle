from fastapi import APIRouter
from app.api.v1.endpoints import kline, kline_simple, chan_analysis, kline_database, chan_strategy

api_router = APIRouter()

# 简化K线API - 支持多时间周期聚合 (主要接口)
api_router.include_router(kline_simple.router, prefix="/kline_simple", tags=["kline-simple"])

# 原有的详细K线API
api_router.include_router(kline.router, prefix="/kline", tags=["kline-detailed"])

# 数据库K线API - 直接从PostgreSQL查询btc_usdt表
api_router.include_router(kline_database.router, prefix="/database", tags=["kline-database"])

# 缠论分析API - 集成Chan模块
api_router.include_router(chan_analysis.router, prefix="/chan", tags=["chan-analysis"])

# 缠论策略API - 多级别联立分析交易策略
api_router.include_router(chan_strategy.router, prefix="/strategy", tags=["chan-strategy"])