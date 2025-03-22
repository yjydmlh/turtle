from typing import List, Optional, Type
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.kline import Kline, SYMBOL_TO_MODEL
from app.schemas.kline import KlineCreate, KlineUpdate
from app.core.logger import app_logger

class CRUDKline:
    def get_model(self, symbol: str) -> Type[Kline]:
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

    def create(self, db: Session, *, symbol: str, obj_in: KlineCreate) -> Kline:
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
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, symbol: str, id: int) -> Optional[Kline]:
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

    def get_by_timestamp(self, db: Session, *, symbol: str, timestamp: int) -> Optional[Kline]:
        """根据时间戳获取K线数据"""
        try:
            app_logger.debug(f"Getting kline record for symbol: {symbol}, timestamp: {timestamp}")
            model = self.get_model(symbol)
            result = db.query(model).filter(model.timestamp == timestamp).first()
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
    ) -> List[Kline]:
        """获取多条K线数据"""
        try:
            app_logger.debug(f"Getting multiple kline records for symbol: {symbol}, skip: {skip}, limit: {limit}")
            model = self.get_model(symbol)
            result = db.query(model).offset(skip).limit(limit).all()
            app_logger.debug(f"Successfully fetched {len(result)} kline records")
            return result
        except Exception as e:
            app_logger.error(f"Error getting multiple kline records: {str(e)}", exc_info=True)
            raise

    def get_by_time_range(
        self, db: Session, *, symbol: str, start_time: datetime, end_time: datetime
    ) -> List[Kline]:
        """获取指定时间范围内的K线数据"""
        try:
            app_logger.debug(f"Getting kline records for symbol: {symbol}, time range: {start_time} to {end_time}")
            model = self.get_model(symbol)
            result = db.query(model).filter(
                model.open_time >= start_time,
                model.close_time <= end_time
            ).all()
            app_logger.debug(f"Successfully fetched {len(result)} kline records in time range")
            return result
        except Exception as e:
            app_logger.error(f"Error getting kline records by time range: {str(e)}", exc_info=True)
            raise

    def update(
        self, db: Session, *, symbol: str, db_obj: Kline, obj_in: KlineUpdate
    ) -> Kline:
        """更新K线数据"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db_obj.updated_at = datetime.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, symbol: str, id: int) -> Kline:
        """删除K线数据"""
        model = self.get_model(symbol)
        obj = db.query(model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def bulk_create(
        self, db: Session, *, symbol: str, obj_in_list: List[KlineCreate]
    ) -> List[Kline]:
        """批量创建K线数据"""
        model = self.get_model(symbol)
        db_objs = []
        for obj_in in obj_in_list:
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
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db_objs.append(db_obj)
        db.bulk_save_objects(db_objs)
        db.commit()
        return db_objs

kline = CRUDKline() 