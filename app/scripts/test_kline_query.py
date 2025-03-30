from datetime import datetime, timedelta

import psycopg2

from app.db.session import SessionLocal
from app.crud import kline
from app.core.logger import app_logger


def test_kline_query(symbol: str = "btc_usdt", days: int = 7) -> None:
    """
    测试K线数据查询功能
    
    Args:
        symbol: 交易对符号，默认为 "btc_usdt"
        days: 查询天数，默认为7天
    """
    with SessionLocal() as db:
        try:
            # 设置查询参数
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            app_logger.info({
                "message": "开始查询K线数据",
                "symbol": symbol,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                }
            })

            # 查询数据
            klines = kline.get_by_time_range(db, symbol=symbol, start_time=start_time, end_time=end_time)

            # 验证结果
            assert klines is not None, "查询结果不应为None"

            if klines:
                app_logger.info({
                    "message": "成功查询到K线数据",
                    "count": len(klines)
                })

                # 验证数据完整性
                for k in klines[:10]:
                    # 基本数据验证
                    assert k.open_time <= k.close_time, "开盘时间应早于或等于收盘时间"
                    assert k.high_price >= k.low_price, "最高价应大于或等于最低价"
                    assert k.volume >= 0, "成交量不应为负数"
                    assert k.quote_volume >= 0, "成交额不应为负数"

                    # 使用结构化的日志输出
                    app_logger.info({
                        "kline_data": {
                            "id": k.id,
                            "time_range": {
                                "open": k.open_time.isoformat(),
                                "close": k.close_time.isoformat()
                            },
                            "prices": {
                                "open": k.open_price,
                                "high": k.high_price,
                                "low": k.low_price,
                                "close": k.close_price
                            },
                            "volume": {
                                "amount": k.volume,
                                "quote": k.quote_volume
                            },
                            "trades": {
                                "count": k.trades_count,
                                "taker_buy": {
                                    "volume": k.taker_buy_volume,
                                    "quote": k.taker_buy_quote_volume
                                }
                            }
                        }
                    })
            else:
                app_logger.warning({
                    "message": "未查询到数据",
                    "symbol": symbol,
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    }
                })

        except AssertionError as e:
            app_logger.error({
                "message": "数据验证失败",
                "error": str(e),
                "symbol": symbol
            })
            raise
        except Exception as e:
            app_logger.error({
                "message": "测试过程中发生错误",
                "error": str(e),
                "error_type": type(e).__name__,
                "symbol": symbol
            }, exc_info=True)
            raise


def test_multiple_symbols() -> None:
    """测试多个交易对的K线数据查询"""
    symbols = ["btc_usdt", "eth_usdt"]
    for symbol in symbols:
        try:
            test_kline_query(symbol=symbol, days=1)
        except Exception as e:
            app_logger.error({
                "message": f"测试{symbol}失败",
                "error": str(e)
            })
            continue


def test_time_ranges() -> None:
    """测试不同时间范围的K线数据查询"""
    time_ranges = [1, 7, 30]  # 测试1天、7天和30天的数据
    for days in time_ranges:
        try:
            test_kline_query(days=days)
        except Exception as e:
            app_logger.error({
                "message": f"测试{days}天数据失败",
                "error": str(e)
            })
            continue


import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DatabaseError
from app.db.session import engine
from app.core.config import settings

if __name__ == "__main__":
    # engine = create_engine("postgresql://postgres:123456@127.0.0.1:5532/postgres")
    engine = create_engine(
        settings.DATABASE_URL
        , pool_pre_ping=True  # 自动检测连接是否有效
        , pool_size=5  # 连接池大小
        , max_overflow=10  # 最大溢出连接数
        , pool_timeout=30  # 连接池超时时间
        , pool_recycle=1800  # 连接回收时间（秒）
        , echo=settings.DEBUG  # 在调试模式下打印SQL语句
    )
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM btc_usdt_copy1 limit 10"))
            for idx, row in enumerate(result):
                try:
                    # 强制将每个字段转为字符串（触发解码）
                    print(f"Row {idx}: {[str(cell) for cell in row]}")
                except UnicodeDecodeError as e:
                    print(f"解码错误行号: {idx}, 错误信息: {e}")
                    print("原始数据:", row)
    except DatabaseError as e:
        print("数据库错误:", e)

    # # 运行基本测试
    # test_kline_query()
    #
    # # 运行多交易对测试
    # test_multiple_symbols()
    #
    # # 运行不同时间范围测试
    # test_time_ranges()
