from sqlalchemy import Column, Integer, Float, DateTime, BigInteger, String
from app.db.base_class import Base

class Kline(Base):
    """K线数据基础模型"""
    
    __abstract__ = True  # 设置为抽象基类
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    timestamp = Column(BigInteger, nullable=False, index=True, comment="K线开始时间戳(毫秒)")
    open_time = Column(DateTime, nullable=False, comment="K线开始时间")
    close_time = Column(DateTime, nullable=False, comment="K线结束时间")
    open_price = Column(Float, nullable=False, comment="开盘价")
    high_price = Column(Float, nullable=False, comment="最高价")
    low_price = Column(Float, nullable=False, comment="最低价")
    close_price = Column(Float, nullable=False, comment="收盘价")
    volume = Column(Float, nullable=False, comment="成交量")
    quote_volume = Column(Float, nullable=False, comment="成交额(计价货币)")
    trades_count = Column(Integer, nullable=False, comment="成交笔数")
    taker_buy_volume = Column(Float, nullable=False, comment="主动买入成交量")
    taker_buy_quote_volume = Column(Float, nullable=False, comment="主动买入成交额")
    created_at = Column(DateTime, nullable=False, comment="数据创建时间")
    updated_at = Column(DateTime, nullable=False, comment="数据更新时间")

class BtcUsdtKline(Kline):
    """BTC/USDT K线数据表"""
    __tablename__ = "btc_usdt"

class EthUsdtKline(Kline):
    """ETH/USDT K线数据表"""
    __tablename__ = "eth_usdt"

# 交易品种映射表
SYMBOL_TO_MODEL = {
    "btc_usdt": BtcUsdtKline,
    "eth_usdt": EthUsdtKline,
    # 可以继续添加其他交易品种
} 