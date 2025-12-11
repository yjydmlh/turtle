"""
SOL/USDT K线数据实体类
"""
from sqlalchemy import Column, BigInteger, Integer, Numeric
from common.model.kline_base import KlineBase


class SolUsdtKline(KlineBase):
    """SOL/USDT K线数据实体"""
    __tablename__ = "sol_usdt"
    
    # 额外字段（不在基类中的字段）
    timestamp = Column(
        BigInteger,
        nullable=False,
        index=True,
        comment="Unix时间戳(毫秒)"
    )
    
    quote_volume = Column(
        Numeric(30, 8),
        nullable=False,
        comment="成交额(USDT)"
    )
    
    trades_count = Column(
        Integer,
        nullable=False,
        comment="成交笔数"
    )
    
    taker_buy_volume = Column(
        Numeric(30, 8),
        nullable=False,
        comment="主动买入成交量(Taker)"
    )
    
    taker_buy_quote_volume = Column(
        Numeric(30, 8),
        nullable=False,
        comment="主动买入成交额(Taker)"
    )

