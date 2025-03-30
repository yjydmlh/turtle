from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class BtcUsdtKlineBase(BaseModel):
    timestamp: int
    open_time: datetime
    close_time: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    quote_volume: Decimal
    trades_count: int
    taker_buy_volume: Decimal
    taker_buy_quote_volume: Decimal

class BtcUsdtKlineCreate(BtcUsdtKlineBase):
    pass

class BtcUsdtKline(BtcUsdtKlineBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 