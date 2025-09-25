from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import crud
from app.api import deps
from app.schemas.kline import BtcUsdtKline
from app.models.kline import SYMBOL_TO_MODEL
from app.core.logger import app_logger
from app.core.exceptions import (
    InvalidParameterException,
    ResourceNotFoundException,
    create_success_response,
    AppException
)
from app.db.session import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{symbol}/")
def read_kline(
    *,
    db: Session = Depends(deps.get_db),
    symbol: str,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数限制"),
):
    """获取K线数据列表"""
    app_logger.debug(f"Fetching kline data for symbol: {symbol}, skip: {skip}, limit: {limit}")
    if symbol not in SYMBOL_TO_MODEL:
        app_logger.error(f"Unsupported symbol: {symbol}")
        raise InvalidParameterException(f"不支持的交易品种: {symbol}")
    kline = crud.kline.get_multi(db=db, symbol=symbol, skip=skip, limit=limit)
    app_logger.debug(f"Successfully fetched {len(kline)} kline records")
    return create_success_response(data=kline)

@router.get("/{symbol}/{kline_id}")
def read_kline_by_id(
    *,
    db: Session = Depends(deps.get_db),
    symbol: str,
    kline_id: int,
):
    """根据ID获取K线数据"""
    app_logger.debug(f"Fetching kline data for symbol: {symbol}, kline_id: {kline_id}")
    if symbol not in SYMBOL_TO_MODEL:
        app_logger.error(f"Unsupported symbol: {symbol}")
        raise InvalidParameterException(f"不支持的交易品种: {symbol}")
    kline = crud.kline.get(db=db, symbol=symbol, id=kline_id)
    if not kline:
        app_logger.warning(f"Kline data not found for symbol: {symbol}, kline_id: {kline_id}")
        raise ResourceNotFoundException("K线数据不存在")
    app_logger.debug(f"Successfully fetched kline data for kline_id: {kline_id}")
    return create_success_response(data=kline)

@router.get("/{symbol}/timestamp/{timestamp}")
def read_kline_by_timestamp(
    *,
    db: Session = Depends(deps.get_db),
    symbol: str,
    timestamp: int,
):
    """根据时间戳获取K线数据"""
    app_logger.debug(f"Fetching kline data for symbol: {symbol}, timestamp: {timestamp}")
    if symbol not in SYMBOL_TO_MODEL:
        app_logger.error(f"Unsupported symbol: {symbol}")
        raise InvalidParameterException(f"不支持的交易品种: {symbol}")
    kline = crud.kline.get_by_timestamp(db=db, symbol=symbol, timestamp=timestamp)
    if not kline:
        app_logger.warning(f"Kline data not found for symbol: {symbol}, timestamp: {timestamp}")
        raise ResourceNotFoundException("K线数据不存在")
    app_logger.debug(f"Successfully fetched kline data for timestamp: {timestamp}")
    return create_success_response(data=kline)

@router.get("/{symbol}/time-range/")
def read_kline_by_time_range(
    *,
    db: Session = Depends(deps.get_db),
    symbol: str,
    start_time: datetime,
    end_time: datetime,
):
    """获取指定时间范围内的K线数据"""
    app_logger.debug(f"Fetching kline data for symbol: {symbol}, time range: {start_time} to {end_time}")
    if symbol not in SYMBOL_TO_MODEL:
        app_logger.error(f"Unsupported symbol: {symbol}")
        raise InvalidParameterException(f"不支持的交易品种: {symbol}")
    kline = crud.kline.get_by_time_range(
        db=db, symbol=symbol, start_time=start_time, end_time=end_time
    )
    app_logger.debug(f"Successfully fetched {len(kline)} kline records in time range")
    return create_success_response(data=kline)

@router.get("/btc_usdt/", response_model=List[BtcUsdtKline])
def get_btc_usdt_klines(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数限制")
):
    """获取BTC/USDT K线数据列表"""
    try:
        klines = crud.kline.get_multi(db, symbol="btc_usdt", skip=skip, limit=limit)
        return klines
    except Exception as e:
        app_logger.error(f"Error getting BTC/USDT klines: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/btc_usdt/{kline_id}", response_model=BtcUsdtKline)
def get_btc_usdt_kline(
    kline_id: int,
    db: Session = Depends(deps.get_db)
):
    """根据ID获取BTC/USDT K线数据"""
    try:
        kline = crud.kline.get(db, symbol="btc_usdt", id=kline_id)
        if not kline:
            raise HTTPException(status_code=404, detail="K线数据不存在")
        return kline
    except Exception as e:
        app_logger.error(f"Error getting BTC/USDT kline: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/btc_usdt/timestamp/{timestamp}", response_model=BtcUsdtKline)
def get_btc_usdt_kline_by_timestamp(
    timestamp: int,
    db: Session = Depends(deps.get_db)
):
    """根据时间戳获取BTC/USDT K线数据"""
    try:
        kline = crud.kline.get_by_timestamp(db, symbol="btc_usdt", timestamp=timestamp)
        if not kline:
            raise HTTPException(status_code=404, detail="K线数据不存在")
        return kline
    except Exception as e:
        app_logger.error(f"Error getting BTC/USDT kline by timestamp: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/btc_usdt/range/", response_model=List[BtcUsdtKline])
def get_btc_usdt_klines_by_range(
    start_time: datetime = Query(..., description="开始时间"),
    end_time: datetime = Query(..., description="结束时间"),
    db: Session = Depends(deps.get_db)
):
    """获取指定时间范围内的BTC/USDT K线数据"""
    try:
        klines = crud.kline.get_by_time_range(
            db, 
            symbol="btc_usdt",
            start_time=start_time,
            end_time=end_time
        )
        return klines
    except Exception as e:
        app_logger.error(f"Error getting BTC/USDT klines by range: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/btc_usdt/aggregate/")
def read_aggregated_kline(
    interval_minutes: int = Query(1, ge=1, le=1440),
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取聚合后的BTC/USDT K线数据
    """
    try:
        # 如果没有提供时间范围，默认获取最近24小时的数据
        if start_time is None:
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = end_time - (24 * 60 * 60 * 1000)
        elif end_time is None:
            end_time = int(datetime.now().timestamp() * 1000)

        start_dt = datetime.fromtimestamp(start_time / 1000)
        end_dt = datetime.fromtimestamp(end_time / 1000)

        klines = crud.kline.get_kline_data(
            db,
            interval_minutes=interval_minutes,
            start_time=start_dt,
            end_time=end_dt
        )
        logger.info(f"Successfully fetched {len(klines)} aggregated K-line records")
        return create_success_response(data=klines)
    except Exception as e:
        logger.error(f"Error fetching aggregated K-line data: {str(e)}")
        raise AppException(
            code=500,
            message="获取聚合K线数据失败"
        )