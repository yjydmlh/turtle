from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app import crud
from app.api import deps
from app.schemas.kline import KlineInDB
from app.models.kline import SYMBOL_TO_MODEL
from app.core.logger import app_logger
from app.core.exceptions import (
    InvalidParameterException,
    ResourceNotFoundException,
    DatabaseException,
    create_success_response
)

router = APIRouter()

@router.get("/{symbol}/")
def read_kline(
    *,
    db: Session = Depends(deps.get_db),
    symbol: str,
    skip: int = 0,
    limit: int = 100,
):
    """获取K线数据列表"""
    app_logger.debug(f"Fetching kline data for symbol: {symbol}, skip: {skip}, limit: {limit}")
    if symbol not in SYMBOL_TO_MODEL:
        app_logger.error(f"Unsupported symbol: {symbol}")
        raise InvalidParameterException(f"不支持的交易品种: {symbol}")
    kline = crud.kline.get_multi(db=db, symbol=symbol, skip=skip, limit=limit)
    app_logger.debug(f"Successfully fetched {len(kline)} kline records")
    return create_success_response(data=kline)

@router.get("/{symbol}/{id}")
def read_kline_by_id(
    *,
    db: Session = Depends(deps.get_db),
    symbol: str,
    id: int,
):
    """根据ID获取K线数据"""
    app_logger.debug(f"Fetching kline data for symbol: {symbol}, id: {id}")
    if symbol not in SYMBOL_TO_MODEL:
        app_logger.error(f"Unsupported symbol: {symbol}")
        raise InvalidParameterException(f"不支持的交易品种: {symbol}")
    kline = crud.kline.get(db=db, symbol=symbol, id=id)
    if not kline:
        app_logger.warning(f"Kline data not found for symbol: {symbol}, id: {id}")
        raise ResourceNotFoundException("K线数据不存在")
    app_logger.debug(f"Successfully fetched kline data for id: {id}")
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