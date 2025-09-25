from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db
from app.services.kline_aggregator import kline_aggregator
from app.core.exceptions import create_success_response, create_error_response
from app.core.logger import app_logger

router = APIRouter()


@router.get("/timeframes")
def get_supported_timeframes():
    """获取支持的时间周期列表"""
    try:
        timeframes = kline_aggregator.get_available_timeframes()
        return create_success_response(data={
            "timeframes": timeframes,
            "description": {
                "1m": "1分钟",
                "5m": "5分钟",
                "15m": "15分钟",
                "30m": "30分钟",
                "1h": "1小时",
                "4h": "4小时",
                "1d": "1天"
            },
            "note": "系统自动将1分钟K线聚合为其他时间周期"
        })
    except Exception as e:
        app_logger.error(f"获取时间周期失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取时间周期失败")


@router.get("/klines")
def get_klines(
        timeframe: str = Query("1h", description="时间周期"),
        limit: int = Query(200, ge=1, le=1000, description="数据条数"),
        symbol: str = Query("btc_usd", description="交易品种"),
        start_time: Optional[str] = Query(None, description="开始时间 (ISO格式)"),
        end_time: Optional[str] = Query(None, description="结束时间 (ISO格式)"),
        db: Session = Depends(get_db)
):
    """
    获取K线数据 - 支持多时间周期聚合

    功能特点:
    - 自动将1分钟K线聚合为目标时间周期
    - 支持时间范围查询
    - 返回标准化的K线数据格式

    支持的时间周期: 1m, 5m, 15m, 30m, 1h, 4h, 1d
    """
    try:
        # 验证时间周期
        if timeframe not in kline_aggregator.get_available_timeframes():
            raise HTTPException(
                status_code=400,
                detail=f"不支持的时间周期: {timeframe}，支持的周期: {kline_aggregator.get_available_timeframes()}"
            )

        # 解析时间参数
        start_dt = None
        end_dt = None

        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="开始时间格式错误，请使用ISO格式 (例: 2024-01-01T00:00:00)")

        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="结束时间格式错误，请使用ISO格式 (例: 2024-01-01T23:59:59)")

        # 验证时间范围
        if start_dt and end_dt and start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")

        app_logger.info(f"📊 获取K线数据 - 周期: {timeframe}, 数量: {limit}")

        # 获取聚合K线数据
        klines = kline_aggregator.aggregate_klines(
            db=db,
            timeframe=timeframe,
            symbol=symbol,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit
        )

        # 获取数据统计
        stats = kline_aggregator.get_data_statistics(db, symbol=symbol)

        app_logger.info(f"✅ 成功返回 {len(klines)} 条 {timeframe} K线数据")

        return create_success_response(data={
            "klines": klines,
            "metadata": {
                "count": len(klines),
                "timeframe": timeframe,
                "request_params": {
                    "limit": limit,
                    "start_time": start_time,
                    "end_time": end_time
                },
                "data_range": {
                    "start": klines[0]["open_time"] if klines else None,
                    "end": klines[-1]["close_time"] if klines else None
                }
            },
            "database_stats": stats
        })

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ 获取K线数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/latest")
def get_latest_klines(
        timeframe: str = Query("1h", description="时间周期"),
        count: int = Query(100, ge=1, le=500, description="最新数据条数"),
        symbol: str = Query("btc_usd", description="交易品种"),
        db: Session = Depends(get_db)
):
    """获取最新的K线数据"""
    try:
        app_logger.info(f"📈 获取最新K线数据 - 周期: {timeframe}, 数量: {count}")

        klines = kline_aggregator.aggregate_klines(
            db=db,
            timeframe=timeframe,
            symbol=symbol,
            limit=count
        )

        latest_timestamp = kline_aggregator.get_latest_timestamp(db, symbol=symbol)

        return create_success_response(data={
            "klines": klines,
            "metadata": {
                "count": len(klines),
                "timeframe": timeframe,
                "is_latest": True,
                "latest_timestamp": latest_timestamp,
                "last_update": datetime.fromtimestamp(latest_timestamp / 1000).isoformat() if latest_timestamp else None
            }
        })

    except Exception as e:
        app_logger.error(f"❌ 获取最新K线数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取最新数据失败")


@router.post("/fetch-data")
def fetch_new_data():
    """手动触发数据获取 - 从币安API获取最新数据"""
    try:
        app_logger.info("🔄 手动触发数据获取...")

        from app.scripts.simple_fetch_data import SimpleBinanceDataFetcher

        fetcher = SimpleBinanceDataFetcher()
        success = fetcher.fetch_recent_data(hours=2)  # 获取最近2小时数据

        if success:
            app_logger.info("✅ 数据获取成功")
            return create_success_response(
                message="数据获取成功",
                data={
                    "status": "success",
                    "hours_fetched": 2,
                    "note": "数据已更新，建议等待2-3秒后重新查询K线数据",
                    "next_steps": [
                        "等待2-3秒让数据写入完成",
                        "调用 /api/v1/simple/klines 查看新数据",
                        "调用 /api/v1/chan/analyze 进行缠论分析"
                    ]
                }
            )
        else:
            app_logger.error("❌ 数据获取失败")
            return create_error_response(
                code=5001,
                message="数据获取失败",
                status_code=500
            )

    except Exception as e:
        app_logger.error(f"❌ 手动获取数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据获取失败: {str(e)}")


@router.get("/stats")
def get_data_statistics(
        symbol: str = Query("btc_usd", description="交易品种"),
        db: Session = Depends(get_db)
):
    """获取数据库统计信息"""
    try:
        stats = kline_aggregator.get_data_statistics(db, symbol=symbol)

        return create_success_response(data={
            "statistics": stats,
            "supported_timeframes": kline_aggregator.get_available_timeframes(),
            "aggregation_info": {
                "source": "1分钟K线数据",
                "method": "pandas.resample聚合",
                "supported_operations": ["开盘价(first)", "最高价(max)", "最低价(min)", "收盘价(last)", "成交量(sum)"]
            }
        })

    except Exception as e:
        app_logger.error(f"❌ 获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """健康检查 - 检查K线API和数据库状态"""
    try:
        # 检查数据库连接
        stats = kline_aggregator.get_data_statistics(db)
        data_available = stats.get("total_klines", 0) > 0

        # 检查最新数据时间
        latest_timestamp = kline_aggregator.get_latest_timestamp(db)
        data_freshness = "unknown"

        if latest_timestamp:
            latest_time = datetime.fromtimestamp(latest_timestamp / 1000)
            time_diff = datetime.now() - latest_time

            if time_diff.total_seconds() < 3600:  # 1小时内
                data_freshness = "fresh"
            elif time_diff.total_seconds() < 86400:  # 24小时内
                data_freshness = "recent"
            else:
                data_freshness = "stale"

        return create_success_response(data={
            "status": "healthy",
            "components": {
                "database": "connected",
                "kline_aggregator": "ready",
                "data_available": data_available,
                "data_freshness": data_freshness
            },
            "statistics": stats,
            "recommendations": {
                "fresh": "数据是最新的，可以进行分析",
                "recent": "数据较新，建议获取最新数据",
                "stale": "数据较旧，建议调用 /fetch-data 获取新数据",
                "unknown": "无数据，请先调用 /fetch-data 获取数据"
            }.get(data_freshness, "请检查数据状态")
        })

    except Exception as e:
        app_logger.error(f"❌ 健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="健康检查失败")