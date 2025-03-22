from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.btc_usdt import BtcUsdt
from app.schemas.btc_usdt import BtcUsdtCreate, BtcUsdtUpdate

class CRUDBtcUsdt:
    def create(self, db: Session, *, obj_in: BtcUsdtCreate) -> BtcUsdt:
        """创建新的K线数据"""
        db_obj = BtcUsdt(
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

    def get(self, db: Session, id: int) -> Optional[BtcUsdt]:
        """根据ID获取K线数据"""
        return db.query(BtcUsdt).filter(BtcUsdt.id == id).first()

    def get_by_timestamp(self, db: Session, timestamp: int) -> Optional[BtcUsdt]:
        """根据时间戳获取K线数据"""
        return db.query(BtcUsdt).filter(BtcUsdt.timestamp == timestamp).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[BtcUsdt]:
        """获取多条K线数据"""
        return db.query(BtcUsdt).offset(skip).limit(limit).all()

    def get_by_time_range(
        self, db: Session, *, start_time: datetime, end_time: datetime
    ) -> List[BtcUsdt]:
        """获取指定时间范围内的K线数据"""
        return db.query(BtcUsdt).filter(
            BtcUsdt.open_time >= start_time,
            BtcUsdt.close_time <= end_time
        ).all()

    def update(
        self, db: Session, *, db_obj: BtcUsdt, obj_in: BtcUsdtUpdate
    ) -> BtcUsdt:
        """更新K线数据"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db_obj.updated_at = datetime.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> BtcUsdt:
        """删除K线数据"""
        obj = db.query(BtcUsdt).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def bulk_create(
        self, db: Session, *, obj_in_list: List[BtcUsdtCreate]
    ) -> List[BtcUsdt]:
        """批量创建K线数据"""
        db_objs = []
        for obj_in in obj_in_list:
            db_obj = BtcUsdt(
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

btc_usdt = CRUDBtcUsdt() 