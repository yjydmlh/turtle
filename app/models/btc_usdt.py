from sqlalchemy import Column, Integer, Float, DateTime, BigInteger, String, text, Numeric
from app.db.base_class import Base

class BtcUsdt(Base):
    """BTC/USDT K线数据表"""
    __tablename__ = "btc_usdt"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(BigInteger, nullable=False, index=True)  # 时间戳
    open_time = Column(DateTime(timezone=True), nullable=False)  # 开盘时间
    close_time = Column(DateTime(timezone=True), nullable=False)  # 收盘时间
    open_price = Column(Numeric(20, 8), nullable=False)  # 开盘价
    high_price = Column(Numeric(20, 8), nullable=False)  # 最高价
    low_price = Column(Numeric(20, 8), nullable=False)  # 最低价
    close_price = Column(Numeric(20, 8), nullable=False)  # 收盘价
    volume = Column(Numeric(30, 8), nullable=False)  # 成交量
    quote_volume = Column(Numeric(30, 8), nullable=False)  # 成交额
    trades_count = Column(BigInteger, nullable=False)  # 成交笔数
    taker_buy_volume = Column(Numeric(30, 8), nullable=False)  # 主动买入成交量
    taker_buy_quote_volume = Column(Numeric(30, 8), nullable=False)  # 主动买入成交额
    created_at = Column(DateTime(timezone=True), nullable=False)  # 创建时间
    updated_at = Column(DateTime(timezone=True), nullable=False)  # 更新时间

    # TimescaleDB 超表配置
    __table_args__ = (
        text("""
            CREATE TABLE IF NOT EXISTS btc_usdt (
                id SERIAL,
                timestamp BIGINT NOT NULL,
                open_time TIMESTAMPTZ NOT NULL,
                close_time TIMESTAMPTZ NOT NULL,
                open_price NUMERIC(20, 8) NOT NULL,
                high_price NUMERIC(20, 8) NOT NULL,
                low_price NUMERIC(20, 8) NOT NULL,
                close_price NUMERIC(20, 8) NOT NULL,
                volume NUMERIC(30, 8) NOT NULL,
                quote_volume NUMERIC(30, 8) NOT NULL,
                trades_count BIGINT NOT NULL,
                taker_buy_volume NUMERIC(30, 8) NOT NULL,
                taker_buy_quote_volume NUMERIC(30, 8) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            );

            -- 创建超表
            SELECT create_hypertable('btc_usdt', 'open_time', if_not_exists => TRUE);

            -- 创建索引
            CREATE INDEX IF NOT EXISTS idx_btc_usdt_timestamp ON btc_usdt (timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_btc_usdt_open_time ON btc_usdt (open_time DESC);
            CREATE INDEX IF NOT EXISTS idx_btc_usdt_close_time ON btc_usdt (close_time DESC);
        """),
    ) 