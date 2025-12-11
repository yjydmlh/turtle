from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.deps import get_db
from app.crud.kline_dao import kline
from app.core.exceptions import create_success_response, create_error_response
from app.core.logger import app_logger

router = APIRouter()


@router.get("/klines")
def get_database_klines(
    timeframe: str = Query("1m", description="时间周期 (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(1000, ge=1, le=5000, description="返回的K线数量"),
    symbol: str = Query("btc_usd", description="交易品种"),
    start_time: Optional[str] = Query(None, description="开始时间 (ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO格式)"),
    db: Session = Depends(get_db)
):
    """
    从PostgreSQL数据库获取BTC/USDT K线数据
    
    支持的功能:
    - 获取1分钟原始数据
    - 支持时间范围查询
    - 支持不同时间间隔聚合
    - 返回标准化的K线数据格式
    """
    try:
        app_logger.info(f"📊 获取数据库K线数据 - 周期: {timeframe}, 数量: {limit}")
        
        # 转换时间周期为分钟数
        interval = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }.get(timeframe, 1)
        
        # 解析时间参数
        start_dt = None
        end_dt = None
        
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="开始时间格式错误，请使用ISO格式")
        
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="结束时间格式错误，请使用ISO格式")
        
        # 如果没有指定时间范围，默认获取最近的数据
        if not start_dt and not end_dt:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=1)  # 默认获取最近1天的数据
        
        # 验证时间范围
        if start_dt and end_dt and start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")
        
        # 从数据库获取K线数据
        klines_data = kline.get_kline_data(
            db=db,
            symbol=symbol,
            interval_minutes=interval,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit
        )
        
        app_logger.info(f"✅ 成功获取 {len(klines_data)} 条K线数据")
        
        return create_success_response(data={
            "klines": klines_data,
            "metadata": {
                "symbol": "BTC/USDT",
                "interval_minutes": interval,
                "count": len(klines_data),
                "time_range": {
                    "start": start_dt.isoformat() if start_dt else None,
                    "end": end_dt.isoformat() if end_dt else None
                },
                "data_source": "PostgreSQL数据库"
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ 获取K线数据失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")


@router.get("/latest")
def get_latest_database_klines(
    timeframe: str = Query("1m", description="时间周期 (1m, 5m, 15m, 1h, 4h, 1d)"),
    count: int = Query(100, ge=1, le=500, description="最新数据条数"),
    symbol: str = Query("btc_usd", description="交易品种"),
    db: Session = Depends(get_db)
):
    """
    获取最新的数据库K线数据
    
    返回指定数量的最新K线数据，按时间倒序排列
    """
    try:
        app_logger.info(f"📊 获取最新数据库K线数据 - 周期: {timeframe}, 数量: {count}")
        
        # 转换时间周期为分钟数
        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }.get(timeframe, 1)
        
        # 获取最新数据
        klines_data = kline.get_kline_data(
            db=db,
            symbol=symbol,
            interval_minutes=timeframe_minutes,
            limit=count
        )
        
        if not klines_data:
            return create_success_response(
                data=[],
                message="暂无数据"
            )
        
        return create_success_response(
            data=klines_data,
            message=f"成功获取 {len(klines_data)} 条最新K线数据"
        )
        
    except Exception as e:
        app_logger.error(f"❌ 获取最新数据库K线数据失败: {str(e)}")
        return create_error_response(
            message=f"获取最新数据失败: {str(e)}",
            error_code="DATABASE_LATEST_ERROR"
        )


@router.get("/chart-data")
def get_database_chart_data(
    timeframe: str = Query("1m", description="时间周期 (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(500, ge=20, le=1000, description="图表数据量"),
    symbol: str = Query("btc_usd", description="交易品种"),
    start_time: Optional[str] = Query(None, description="开始时间 (ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO格式)"),
    db: Session = Depends(get_db)
):
    """
    获取优化的图表数据格式
    
    返回适合前端图表组件使用的K线数据格式
    """
    try:
        app_logger.info(f"📊 获取数据库图表数据 - 周期: {timeframe}, 数量: {limit}")
        
        # 转换时间周期为分钟数
        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }.get(timeframe, 1)
        
        # 解析时间参数
        start_dt = None
        end_dt = None
        
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="开始时间格式错误")
        
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="结束时间格式错误")
        
        # 获取K线数据
        klines_data = kline.get_kline_data(
            db=db,
            symbol=symbol,
            interval_minutes=timeframe_minutes,
            limit=limit,
            start_time=start_dt,
            end_time=end_dt
        )
        
        if not klines_data:
            return create_success_response(
                data=[],
                message="暂无图表数据"
            )
        
        return create_success_response(
            data=klines_data,
            message=f"成功获取 {len(klines_data)} 条图表数据"
        )
        
    except Exception as e:
        app_logger.error(f"❌ 获取数据库图表数据失败: {str(e)}")
        return create_error_response(
            code=1000,
            message=f"获取图表数据失败: {str(e)}",
            status_code=500
        )


@router.get("/statistics")
def get_database_statistics(
    symbol: str = Query("btc_usd", description="交易品种"),
    db: Session = Depends(get_db)
):
    """
    获取数据库K线数据统计信息
    
    返回数据库中K线数据的统计信息，包括：
    - 数据总量
    - 时间范围
    - 最新更新时间
    - 数据质量指标
    """
    try:
        app_logger.info("📊 获取数据库统计信息")
        
        # 获取基本统计信息
        total_count = kline.get_count(db, symbol="btc_usdt")
        
        if total_count == 0:
            return create_success_response(
                data={
                    "total_count": 0,
                    "message": "数据库中暂无K线数据"
                },
                message="数据库为空"
            )
        
        # 获取最新数据
        latest_klines = kline.get_multi(
            db=db,
            symbol=symbol,
            skip=0,
            limit=1
        )
        
        # 获取最旧数据
        total_count = kline.get_count(db, symbol=symbol)
        oldest_klines = kline.get_multi(
            db=db,
            symbol=symbol,
            skip=max(0, total_count - 1),
            limit=1
        )
        
        latest_time = None
        oldest_time = None
        
        if latest_klines:
            latest_time = latest_klines[0].get("timestamp")
        
        if oldest_klines:
            oldest_time = oldest_klines[0].get("timestamp")
        
        return create_success_response(
            data={
                "total_count": total_count,
                "time_range": {
                    "earliest": oldest_time,
                    "latest": latest_time,
                    "earliest_formatted": datetime.fromtimestamp(oldest_time / 1000).isoformat() if oldest_time else None,
                    "latest_formatted": datetime.fromtimestamp(latest_time / 1000).isoformat() if latest_time else None
                },
                "symbol": "BTC/USDT",
                "data_source": "PostgreSQL Database",
                "base_interval": "1分钟"
            },
            message=f"数据库包含 {total_count} 条K线数据"
        )
        
    except Exception as e:
        app_logger.error(f"❌ 获取数据库统计信息失败: {str(e)}")
        return create_error_response(
            code=1000,
            message=f"获取统计信息失败: {str(e)}",
            status_code=500
        )