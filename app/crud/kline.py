from typing import List, Optional, Type
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.kline import BtcUsdtKline, SYMBOL_TO_MODEL
from app.schemas.kline import BtcUsdtKlineCreate, BtcUsdtKline
from app.core.logger import app_logger
from sqlalchemy import text

class CRUDKline:
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

    def get_multi(
        self, db: Session, *, symbol: str, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        """获取多条K线数据"""
        try:
            app_logger.debug(f"Getting multiple kline records for symbol: {symbol}, skip: {skip}, limit: {limit}")
            model = self.get_model(symbol)
            # 使用text()函数包装查询，确保编码正确
            result = db.execute(
                text("SELECT * FROM btc_usdt ORDER BY open_time DESC LIMIT :limit OFFSET :skip"),
                {"limit": limit, "skip": skip}
            ).mappings().all()
            
            # 将查询结果转换为字典列表
            klines = []
            for row in result:
                kline_dict = {
                    "id": row['id'],
                    "open_time": row['open_time'].isoformat(),
                    "close_time": row['close_time'].isoformat(),
                    "open_price": str(row['open_price']),
                    "high_price": str(row['high_price']),
                    "low_price": str(row['low_price']),
                    "close_price": str(row['close_price']),
                    "volume": str(row['volume']),
                    "quote_volume": str(row['quote_volume']),
                    "trades_count": row['trades_count'],
                    "taker_buy_volume": str(row['taker_buy_volume']),
                    "taker_buy_quote_volume": str(row['taker_buy_quote_volume']),
                    "created_at": row['created_at'].isoformat(),
                    "updated_at": row['updated_at'].isoformat()
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
        interval_minutes: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[BtcUsdtKline]:
        """使用原生SQL查询获取聚合后的K线数据"""
        try:
            app_logger.debug(f"Getting aggregated kline data for interval: {interval_minutes} minutes")
            sql = text("""
                SELECT 
                    EXTRACT(EPOCH FROM time_bucket(:interval_minutes * '1 minute', k.open_time))::BIGINT * 1000 as timestamp,
                    time_bucket(:interval_minutes * '1 minute', k.open_time) as open_time,
                    time_bucket(:interval_minutes * '1 minute', k.open_time) + (:interval_minutes * '1 minute') as close_time,
                    FIRST(k.open_price, k.open_time) as open_price,
                    MAX(k.high_price) as high_price,
                    MIN(k.low_price) as low_price,
                    LAST(k.close_price, k.open_time) as close_price,
                    SUM(k.volume) as volume,
                    SUM(k.quote_volume) as quote_volume,
                    SUM(k.trades_count) as trades_count,
                    SUM(k.taker_buy_volume) as taker_buy_volume,
                    SUM(k.taker_buy_quote_volume) as taker_buy_quote_volume,
                    MAX(k.created_at) as created_at,
                    MAX(k.updated_at) as updated_at
                FROM btc_usdt k
                WHERE k.open_time >= :start_time AND k.open_time < :end_time
                GROUP BY time_bucket(:interval_minutes * '1 minute', k.open_time)
                ORDER BY time_bucket(:interval_minutes * '1 minute', k.open_time)
            """)
            
            result = db.execute(
                sql,
                {
                    "interval_minutes": interval_minutes,
                    "start_time": start_time,
                    "end_time": end_time
                }
            ).mappings().all()
            
            # 将查询结果转换为BtcUsdtKline模型对象
            klines = []
            for row in result:
                kline = BtcUsdtKline(
                    open_time=row['open_time'],
                    close_time=row['close_time'],
                    open_price=row['open_price'],
                    high_price=row['high_price'],
                    low_price=row['low_price'],
                    close_price=row['close_price'],
                    volume=row['volume'],
                    quote_volume=row['quote_volume'],
                    trades_count=row['trades_count'],
                    taker_buy_volume=row['taker_buy_volume'],
                    taker_buy_quote_volume=row['taker_buy_quote_volume'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                klines.append(kline)
            
            app_logger.debug(f"Successfully fetched {len(klines)} aggregated kline records")
            return klines
        except Exception as e:
            app_logger.error(f"Error getting aggregated kline data: {str(e)}", exc_info=True)
            raise

    def get_by_id_and_time(
        self, 
        db: Session, 
        *, 
        id: int,
        open_time: datetime
    ) -> Optional[BtcUsdtKline]:
        """根据ID和开盘时间获取K线数据"""
        try:
            app_logger.debug(f"Getting kline record for id: {id}, open_time: {open_time}")
            result = db.query(BtcUsdtKline).filter(
                BtcUsdtKline.id == id,
                BtcUsdtKline.open_time == open_time
            ).first()
            if result:
                app_logger.debug(f"Successfully fetched kline record with id: {id}")
            return result
        except Exception as e:
            app_logger.error(f"Error getting kline record: {str(e)}", exc_info=True)
            raise

    def get_by_timestamp(
        self, 
        db: Session, 
        *, 
        timestamp: int
    ) -> Optional[BtcUsdtKline]:
        """根据时间戳获取K线数据"""
        try:
            app_logger.debug(f"Getting kline record for timestamp: {timestamp}")
            result = db.query(BtcUsdtKline).filter(
                BtcUsdtKline.timestamp == timestamp
            ).first()
            if result:
                app_logger.debug(f"Successfully fetched kline record with timestamp: {timestamp}")
            return result
        except Exception as e:
            app_logger.error(f"Error getting kline record: {str(e)}", exc_info=True)
            raise

    def create(
        self, 
        db: Session, 
        *, 
        obj_in: BtcUsdtKlineCreate
    ) -> BtcUsdtKline:
        """创建新的K线数据"""
        try:
            app_logger.debug("Creating new kline record")
            db_obj = BtcUsdtKline(
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
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            app_logger.debug(f"Successfully created kline record with id: {db_obj.id}")
            return db_obj
        except Exception as e:
            app_logger.error(f"Error creating kline record: {str(e)}", exc_info=True)
            raise

    def bulk_create(
        self, 
        db: Session, 
        *, 
        obj_in_list: List[BtcUsdtKlineCreate]
    ) -> List[BtcUsdtKline]:
        """批量创建K线数据"""
        try:
            app_logger.debug(f"Creating {len(obj_in_list)} kline records")
            db_objs = []
            for obj_in in obj_in_list:
                db_obj = BtcUsdtKline(
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
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db_objs.append(db_obj)
            db.bulk_save_objects(db_objs)
            db.commit()
            app_logger.debug(f"Successfully created {len(db_objs)} kline records")
            return db_objs
        except Exception as e:
            app_logger.error(f"Error creating kline records: {str(e)}", exc_info=True)
            raise

kline = CRUDKline() 