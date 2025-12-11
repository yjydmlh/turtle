"""
K线数据基类实体
只包含指定的公共字段：id, open_time, close_time, open_price, high_price, low_price, close_price, volume
"""
from sqlalchemy import Column, Integer, DateTime, Numeric, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class KlineBase(Base):

    __abstract__ = True  # 抽象基类，不会创建表
    
    # 主键ID
    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )
    
    # 时间字段
    open_time = Column(
        DateTime,
        nullable=False,
        index=True,
        comment="开盘时间"
    )
    
    close_time = Column(
        DateTime,
        nullable=False,
        comment="收盘时间"
    )
    
    # 价格字段
    open_price = Column(
        Numeric(30, 18),
        nullable=False,
        comment="开盘价"
    )
    
    high_price = Column(
        Numeric(30, 18),
        nullable=False,
        comment="最高价"
    )
    
    low_price = Column(
        Numeric(30, 18),
        nullable=False,
        comment="最低价"
    )
    
    close_price = Column(
        Numeric(30, 18),
        nullable=False,
        comment="收盘价"
    )
    
    # 成交量字段
    volume = Column(
        Numeric(30, 8),
        nullable=False,
        comment="成交量"
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, open_time={self.open_time})>"

