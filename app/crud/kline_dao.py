from typing import List, Optional, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.logger import app_logger
from sqlalchemy import text

from common.model import SymbolEnum, TimeframeEnum


class KlineDao:
    def get_model(self, symbol: str) -> Type[BtcUsdtKline]:
        """获取对应交易品种的模型类"""
        try:
            if symbol not in SYMBOL_TO_MODEL:
                app_logger.error(f"Unsupported symbol: {symbol}")
                raise ValueError(f"不支持的交易品种: {symbol}")
            app_logger.debug(f"Getting model for symbol: {symbol}")
            return SYMBOL_TO_MODEL[symbol]
        except Exception as e:
            app_logger.error(f"Error getting model for symbol {symbol}: {str(e)}", exc_info=True)
            raise

    def create(self, db: Session, *, symbol: str, obj_in: BtcUsdtKlineCreate) -> BtcUsdtKline:
        """创建新的K线数据"""
        model = self.get_model(symbol)
        db_obj = model(
            timestamp=obj_in.timestamp,
            open_time=obj_in.open_time,
            close_time=obj_in.close_time,
            open_price=obj_in.open_price,
            high_price=obj_in.high_price,
            low_price=obj_in.low_price,
            close_price=obj_in.close_price,
            volume=obj_in.volume,
            quote_volume=obj_in.quote_volume,
            trades_count=obj_in.trades_count,
            taker_buy_volume=obj_in.taker_buy_volume,
            taker_buy_quote_volume=obj_in.taker_buy_quote_volume,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, symbol: str, id: int) -> Optional[BtcUsdtKline]:
        """根据ID获取K线数据"""
        try:
            app_logger.debug(f"Getting kline record for symbol: {symbol}, id: {id}")
            model = self.get_model(symbol)
            result = db.query(model).filter(model.id == id).first()
            if result:
                app_logger.debug(f"Successfully fetched kline record with id: {id}")
            else:
                app_logger.warning(f"Kline record not found for id: {id}")
            return result
        except Exception as e:
            app_logger.error(f"Error getting kline record: {str(e)}", exc_info=True)
            raise

    def get_by_timestamp(self, db: Session, *, symbol: str, timestamp: int) -> Optional[BtcUsdtKline]:
        """根据时间戳获取K线数据"""
        try:
            app_logger.debug(f"Getting kline record for symbol: {symbol}, timestamp: {timestamp}")
            model = self.get_model(symbol)
            dt = datetime.fromtimestamp(timestamp / 1000)  # 转换毫秒时间戳为datetime
            result = db.query(model).filter(
                model.open_time <= dt,
                model.close_time > dt
            ).first()
            if result:
                app_logger.debug(f"Successfully fetched kline record with timestamp: {timestamp}")
            else:
                app_logger.warning(f"Kline record not found for timestamp: {timestamp}")
            return result
        except Exception as e:
            app_logger.error(f"Error getting kline record by timestamp: {str(e)}", exc_info=True)
            raise

    def get_count(self, db: Session, *, symbol: str) -> int:
        """获取指定交易品种的K线数据总数"""
        try:
            app_logger.debug(f"Getting count for symbol: {symbol}")
            model = self.get_model(symbol)
            count = db.query(model).count()
            app_logger.debug(f"Count for {symbol}: {count}")
            return count
        except Exception as e:
            app_logger.error(f"Error getting count for symbol {symbol}: {str(e)}", exc_info=True)
            return 0

    def get_multi(
        self, db: Session, *, symbol: str, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        """获取多条K线数据"""
        try:
            app_logger.debug(f"Getting multiple kline records for symbol: {symbol}, skip: {skip}, limit: {limit}")
            model = self.get_model(symbol)
            # 使用ORM查询，更安全且支持多表
            query_result = db.query(model).order_by(model.open_time.desc()).offset(skip).limit(limit).all()
            
            # 将查询结果转换为字典列表
            klines = []
            for kline in query_result:
                kline_dict = {
                    "id": kline.id,
                    "timestamp": kline.timestamp,
                    "open_time": kline.open_time.isoformat(),
                    "close_time": kline.close_time.isoformat(),
                    "open_price": str(kline.open_price),
                    "high_price": str(kline.high_price),
                    "low_price": str(kline.low_price),
                    "close_price": str(kline.close_price),
                    "volume": str(kline.volume),
                    "quote_volume": str(kline.quote_volume),
                    "trades_count": kline.trades_count,
                    "taker_buy_volume": str(kline.taker_buy_volume),
                    "taker_buy_quote_volume": str(kline.taker_buy_quote_volume),
                    "created_at": kline.created_at.isoformat(),
                    "updated_at": kline.updated_at.isoformat()
                }
                klines.append(kline_dict)
            
            app_logger.debug(f"Successfully fetched {len(klines)} kline records")
            return klines
        except Exception as e:
            app_logger.error(f"Error getting multiple kline records: {str(e)}", exc_info=True)
            raise

    def get_by_time_range(
        self, db: Session, *, symbol: str, start_time: datetime, end_time: datetime
    ) -> List[BtcUsdtKline]:
        """获取指定时间范围内的K线数据"""
        try:
            app_logger.debug(f"Getting kline records for symbol: {symbol}, time range: {start_time} to {end_time}")
            model = self.get_model(symbol)
            result = db.query(model).filter(
                model.open_time >= start_time,
                model.close_time <= end_time
            ).order_by(model.open_time.asc()).all()
            app_logger.debug(f"Successfully fetched {len(result)} kline records in time range")
            return result
        except Exception as e:
            app_logger.error(f"Error getting kline records by time range: {str(e)}", exc_info=True)
            raise

    def update(
        self, db: Session, *, symbol: str, db_obj: BtcUsdtKline, obj_in: BtcUsdtKlineCreate
    ) -> BtcUsdtKline:
        """更新K线数据"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, symbol: str, id: int) -> BtcUsdtKline:
        """删除K线数据"""
        model = self.get_model(symbol)
        obj = db.query(model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def bulk_create(
        self, db: Session, *, symbol: str, obj_in_list: List[BtcUsdtKlineCreate]
    ) -> List[BtcUsdtKline]:
        """批量创建K线数据"""
        model = self.get_model(symbol)
        db_objs = []
        for obj_in in obj_in_list:
            db_obj = model(
                open_time=obj_in.open_time,
                close_time=obj_in.close_time,
                open_price=obj_in.open_price,
                high_price=obj_in.high_price,
                low_price=obj_in.low_price,
                close_price=obj_in.close_price,
                volume=obj_in.volume,
                quote_volume=obj_in.quote_volume,
                trades_count=obj_in.trades_count,
                taker_buy_volume=obj_in.taker_buy_volume,
                taker_buy_quote_volume=obj_in.taker_buy_quote_volume,
            )
            db_objs.append(db_obj)
        db.bulk_save_objects(db_objs)
        db.commit()
        return db_objs

    def get_kline_data(
        self, 
        db: Session, 
        *, 
        symbol: str = "btc_usdt",
        interval_minutes: int = 1,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 1000
    ) -> List[dict]:
        """获取K线数据 - 优化版本，支持不同时间间隔和时间范围查询"""
        try:
            app_logger.debug(f"Getting kline data for symbol: {symbol}, interval: {interval_minutes} minutes")
            model = self.get_model(symbol)
            
            # 构建基础查询
            query = db.query(model)
            
            # 添加时间范围过滤
            if start_time:
                query = query.filter(model.open_time >= start_time)
            if end_time:
                query = query.filter(model.open_time < end_time)
            
            # 对于所有时间间隔，都使用简化的查询逻辑
            # 直接获取原始数据，在应用层进行聚合（更快）
            query_result = query.order_by(model.open_time.desc()).limit(limit * 10).all()
            
            # 转换为字典格式
            klines = []
            for kline in query_result:
                kline_dict = {
                    "timestamp": kline.timestamp,
                    "open_time": kline.open_time.isoformat(),
                    "close_time": kline.close_time.isoformat(),
                    "open_price": float(kline.open_price),
                    "high_price": float(kline.high_price),
                    "low_price": float(kline.low_price),
                    "close_price": float(kline.close_price),
                    "volume": float(kline.volume),
                    "quote_volume": float(kline.quote_volume),
                    "trades_count": kline.trades_count,
                    "taker_buy_volume": float(kline.taker_buy_volume),
                    "taker_buy_quote_volume": float(kline.taker_buy_quote_volume)
                }
                klines.append(kline_dict)
            
            # 如果需要聚合（非1分钟数据），在这里进行简单聚合
            if interval_minutes > 1:
                klines = self._aggregate_klines(klines, interval_minutes, limit)
            else:
                klines = klines[:limit]  # 限制返回数量
            
            app_logger.debug(f"Successfully fetched {len(klines)} aggregated kline records")
            return klines
            
        except Exception as e:
            app_logger.error(f"Error getting kline data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get kline data: {str(e)}")
    
    def _aggregate_klines(self, klines: List[dict], interval_minutes: int, limit: int) -> List[dict]:
        """在应用层进行K线数据聚合，比数据库聚合更快"""
        from datetime import datetime, timedelta
        
        if not klines:
            return []
        
        # 按时间间隔分组
        grouped_data = {}
        
        for kline in klines:
            # 解析时间
            open_time = datetime.fromisoformat(kline['open_time'].replace('Z', '+00:00'))
            
            # 计算时间桶
            if interval_minutes == 60:  # 1小时
                bucket_time = open_time.replace(minute=0, second=0, microsecond=0)
            elif interval_minutes == 240:  # 4小时
                hour_bucket = (open_time.hour // 4) * 4
                bucket_time = open_time.replace(hour=hour_bucket, minute=0, second=0, microsecond=0)
            elif interval_minutes == 1440:  # 1天
                bucket_time = open_time.replace(hour=0, minute=0, second=0, microsecond=0)
            else:  # 其他间隔，简单按小时分组
                bucket_time = open_time.replace(minute=0, second=0, microsecond=0)
            
            bucket_key = bucket_time.isoformat()
            
            if bucket_key not in grouped_data:
                grouped_data[bucket_key] = {
                    'open_time': bucket_time,
                    'close_time': bucket_time + timedelta(minutes=interval_minutes),
                    'open_price': kline['open_price'],
                    'close_price': kline['close_price'],
                    'high_price': kline['high_price'],
                    'low_price': kline['low_price'],
                    'volume': 0,
                    'quote_volume': 0,
                    'trades_count': 0,
                    'taker_buy_volume': 0,
                    'taker_buy_quote_volume': 0,
                    'timestamp': int(bucket_time.timestamp() * 1000)
                }
            
            # 聚合数据
            group = grouped_data[bucket_key]
            group['high_price'] = max(group['high_price'], kline['high_price'])
            group['low_price'] = min(group['low_price'], kline['low_price'])
            group['volume'] += kline['volume']
            group['quote_volume'] += kline['quote_volume']
            group['trades_count'] += kline['trades_count']
            group['taker_buy_volume'] += kline['taker_buy_volume']
            group['taker_buy_quote_volume'] += kline['taker_buy_quote_volume']
            
            # 更新收盘价（最新的数据）
            if datetime.fromisoformat(kline['open_time'].replace('Z', '+00:00')) >= open_time:
                group['close_price'] = kline['close_price']
        
        # 转换为列表并排序
        result = []
        for bucket_key in sorted(grouped_data.keys(), reverse=True):
            group = grouped_data[bucket_key]
            result.append({
                'timestamp': group['timestamp'],
                'open_time': group['open_time'].isoformat(),
                'close_time': group['close_time'].isoformat(),
                'open_price': group['open_price'],
                'high_price': group['high_price'],
                'low_price': group['low_price'],
                'close_price': group['close_price'],
                'volume': group['volume'],
                'quote_volume': group['quote_volume'],
                'trades_count': group['trades_count'],
                'taker_buy_volume': group['taker_buy_volume'],
                'taker_buy_quote_volume': group['taker_buy_quote_volume']
            })
        
        return result[:limit]

kline = CRUDKline()