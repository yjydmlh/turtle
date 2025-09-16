import ssl
import ccxt
import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3 import poolmanager
import pandas as pd
from datetime import datetime, timedelta
import time
import ssl
from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.logger import app_logger
from app.models.kline import BtcUsdtKline


def create_ssl_context():
    """创建SSL上下文"""
    context = ssl.create_default_context()
    # 使用 certifi 提供的 CA 文件
    context.load_verify_locations(certifi.where())
    return context


class CustomSslAdapter(HTTPAdapter):
    """自定义SSL适配器"""

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
            **kwargs
        )


def create_session_with_ssl_context(context: ssl.SSLContext) -> requests.Session:
    """创建带SSL上下文的会话"""
    session = requests.Session()
    adapter = CustomSslAdapter(ssl_context=context)
    session.mount("https://", adapter)
    return session


class SimpleBinanceDataFetcher:
    """简化的币安数据获取器"""

    def __init__(self):
        # 初始化币安交易所
        try:
            # 创建SSL上下文和会话
            ssl_ctx = create_ssl_context()
            my_session = create_session_with_ssl_context(ssl_ctx)

            self.exchange = ccxt.binance({
                'session': my_session,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'  # 现货交易
                }
            })
            app_logger.info("✅ 币安数据获取器初始化成功")
        except Exception as e:
            app_logger.error(f"❌ 币安数据获取器初始化失败: {str(e)}")
            raise

    def fetch_recent_data(self, symbol: str = 'BTC/USDT', hours: int = 24) -> bool:
        """
        获取最近的数据

        Args:
            symbol: 交易对符号，默认BTC/USDT
            hours: 获取最近几小时的数据，默认24小时

        Returns:
            bool: 获取是否成功
        """
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)

            app_logger.info(f"🔄 开始获取 {symbol} 最近 {hours} 小时的1分钟K线数据")
            app_logger.info(f"📅 时间范围: {start_time} 到 {end_time}")

            # 转换时间戳
            since = self.exchange.parse8601(start_time.isoformat())

            db = SessionLocal()
            try:
                all_klines = []
                current_since = since
                batch_count = 0

                while current_since < self.exchange.milliseconds():
                    try:
                        # 获取K线数据
                        klines = self.exchange.fetch_ohlcv(
                            symbol,
                            timeframe='1m',
                            since=current_since,
                            limit=1000  # 币安API限制每次最多1000条数据
                        )

                        if not klines:
                            app_logger.info("📊 没有更多数据，获取完成")
                            break

                        all_klines.extend(klines)
                        batch_count += 1

                        # 更新当前时间戳为最后一条数据的时间戳
                        current_since = klines[-1][0] + 60000  # 加一分钟

                        app_logger.info(f"📈 批次 {batch_count}: 获取 {len(klines)} 条数据，累计 {len(all_klines)} 条")

                        # 避免触发API限制
                        time.sleep(0.1)

                        # 如果已经获取到当前时间，停止
                        if current_since >= self.exchange.milliseconds():
                            break

                    except Exception as e:
                        app_logger.error(f"❌ 获取数据批次失败: {str(e)}")
                        time.sleep(1)  # 发生错误时等待1秒
                        continue

                if all_klines:
                    # 保存数据到数据库
                    saved_count = self.save_klines_to_db(db, all_klines)
                    app_logger.info(f"✅ 数据获取完成！总共获取 {len(all_klines)} 条，成功保存 {saved_count} 条")
                    return True
                else:
                    app_logger.warning("⚠️ 没有获取到任何数据")
                    return False

            finally:
                db.close()

        except Exception as e:
            app_logger.error(f"❌ 获取数据过程中发生错误: {str(e)}")
            return False

    def save_klines_to_db(self, db: Session, klines_data: list) -> int:
        """
        保存K线数据到数据库

        Args:
            db: 数据库会话
            klines_data: K线数据列表 [timestamp, open, high, low, close, volume]

        Returns:
            int: 成功保存的数据条数
        """
        saved_count = 0
        skipped_count = 0
        error_count = 0

        app_logger.info(f"💾 开始保存 {len(klines_data)} 条K线数据到数据库...")

        # 批量处理，每批1000条
        batch_size = 1000
        total_batches = (len(klines_data) + batch_size - 1) // batch_size

        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(klines_data))
            batch_data = klines_data[start_idx:end_idx]

            app_logger.info(f"📦 处理批次 {batch_idx + 1}/{total_batches}: {len(batch_data)} 条数据")

            for kline in batch_data:
                try:
                    timestamp = kline[0]

                    # 检查数据是否已存在（避免重复）
                    existing = db.query(BtcUsdtKline).filter(
                        BtcUsdtKline.timestamp == timestamp
                    ).first()

                    if existing:
                        skipped_count += 1
                        continue

                    # 验证数据完整性
                    if not self._validate_kline_data(kline):
                        app_logger.warning(f"⚠️ 数据验证失败，跳过: {kline}")
                        error_count += 1
                        continue

                    # 创建新的K线记录
                    kline_obj = BtcUsdtKline(
                        timestamp=timestamp,
                        open_time=datetime.fromtimestamp(timestamp / 1000),
                        close_time=datetime.fromtimestamp(timestamp / 1000) + timedelta(minutes=1),
                        open_price=Decimal(str(kline[1])),
                        high_price=Decimal(str(kline[2])),
                        low_price=Decimal(str(kline[3])),
                        close_price=Decimal(str(kline[4])),
                        volume=Decimal(str(kline[5])),
                        quote_volume=Decimal(str(kline[5] * kline[4])),  # 计算成交额
                        trades_count=0,  # 1分钟数据不包含此字段，设为0
                        taker_buy_volume=Decimal(str(kline[5] * 0.5)),  # 估算值
                        taker_buy_quote_volume=Decimal(str(kline[5] * kline[4] * 0.5)),  # 估算值
                    )

                    db.add(kline_obj)
                    saved_count += 1

                except Exception as e:
                    app_logger.error(f"❌ 保存单条数据失败: {str(e)}")
                    error_count += 1
                    continue

            # 每批次提交一次
            try:
                db.commit()
                app_logger.info(f"✅ 批次 {batch_idx + 1} 提交成功")
            except Exception as e:
                app_logger.error(f"❌ 批次 {batch_idx + 1} 提交失败: {str(e)}")
                db.rollback()
                continue

        # 最终统计
        app_logger.info(f"📊 数据保存完成:")
        app_logger.info(f"   ✅ 成功保存: {saved_count} 条")
        app_logger.info(f"   ⏭️ 跳过重复: {skipped_count} 条")
        app_logger.info(f"   ❌ 保存失败: {error_count} 条")

        return saved_count

    def _validate_kline_data(self, kline: list) -> bool:
        """验证K线数据的有效性"""
        try:
            if len(kline) < 6:
                return False

            timestamp, open_price, high_price, low_price, close_price, volume = kline[:6]

            # 检查时间戳
            if not isinstance(timestamp, (int, float)) or timestamp <= 0:
                return False

            # 检查价格数据
            prices = [open_price, high_price, low_price, close_price]
            for price in prices:
                if not isinstance(price, (int, float)) or price <= 0:
                    return False

            # 检查价格逻辑关系
            if high_price < low_price:
                return False

            if not (low_price <= open_price <= high_price):
                return False

            if not (low_price <= close_price <= high_price):
                return False

            # 检查成交量
            if not isinstance(volume, (int, float)) or volume < 0:
                return False

            return True

        except Exception:
            return False

    def get_market_info(self, symbol: str = 'BTC/USDT') -> dict:
        """获取市场信息"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last_price': ticker['last'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'volume_24h': ticker['baseVolume'],
                'change_24h': ticker['change'],
                'change_percent_24h': ticker['percentage'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            app_logger.error(f"❌ 获取市场信息失败: {str(e)}")
            return {}

    def test_connection(self) -> bool:
        """测试连接"""
        try:
            # 测试API连接
            exchange_info = self.exchange.load_markets()
            app_logger.info(f"✅ 币安API连接测试成功，支持 {len(exchange_info)} 个交易对")
            return True
        except Exception as e:
            app_logger.error(f"❌ 币安API连接测试失败: {str(e)}")
            return False


def fetch_historical_data(days: int = 30) -> bool:
    """
    获取历史数据

    Args:
        days: 获取最近几天的数据

    Returns:
        bool: 是否成功
    """
    try:
        fetcher = SimpleBinanceDataFetcher()

        # 测试连接
        if not fetcher.test_connection():
            app_logger.error("❌ 币安API连接失败")
            return False

        # 按天分批获取，避免一次获取过多数据
        success_count = 0

        for day in range(days):
            start_day = days - day - 1  # 从最早的一天开始
            app_logger.info(f"📅 获取第 {day + 1}/{days} 天的数据...")

            success = fetcher.fetch_recent_data(hours=24)  # 每次获取24小时
            if success:
                success_count += 1

            # 休息一下，避免API限制
            if day < days - 1:  # 不是最后一天
                time.sleep(2)

        app_logger.info(f"🎉 历史数据获取完成！成功获取 {success_count}/{days} 天的数据")
        return success_count > 0

    except Exception as e:
        app_logger.error(f"❌ 获取历史数据失败: {str(e)}")
        return False


# 主函数 - 可以直接运行此脚本
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='币安数据获取器')
    parser.add_argument('--hours', type=int, default=24, help='获取最近几小时的数据')
    parser.add_argument('--days', type=int, help='获取最近几天的历史数据')
    parser.add_argument('--symbol', type=str, default='BTC/USDT', help='交易对符号')
    parser.add_argument('--test', action='store_true', help='仅测试连接')

    args = parser.parse_args()

    try:
        fetcher = SimpleBinanceDataFetcher()

        if args.test:
            # 仅测试连接
            if fetcher.test_connection():
                print("✅ 连接测试成功")
            else:
                print("❌ 连接测试失败")

        elif args.days:
            # 获取历史数据
            print(f"🔄 开始获取最近 {args.days} 天的历史数据...")
            success = fetch_historical_data(args.days)
            if success:
                print("✅ 历史数据获取成功")
            else:
                print("❌ 历史数据获取失败")

        else:
            # 获取最近数据
            print(f"🔄 开始获取最近 {args.hours} 小时的数据...")
            success = fetcher.fetch_recent_data(symbol=args.symbol, hours=args.hours)
            if success:
                print("✅ 数据获取成功")
            else:
                print("❌ 数据获取失败")

    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")

    print("🔚 程序结束")