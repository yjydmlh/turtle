from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BtcUsdtBase(BaseModel):
    timestamp: int
    open_time: datetime
    close_time: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    quote_volume: float
    trades_count: int
    taker_buy_volume: float
    taker_buy_quote_volume: float

class BtcUsdtCreate(BtcUsdtBase):
    pass

class BtcUsdtUpdate(BtcUsdtBase):
    pass

class BtcUsdtInDB(BtcUsdtBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 