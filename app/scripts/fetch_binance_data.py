import ssl
import ccxt
import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3 import poolmanager
import pandas as pd
from datetime import datetime, timedelta
import time
from decimal import Decimal
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.logger import app_logger
from app.crud import kline
from app.schemas.kline import BtcUsdtKlineCreate
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

def get_binance_data():
    """从币安获取BTC/USDT的历史K线数据"""
    try:
        # 创建SSL上下文和会话
        ssl_ctx = create_ssl_context()
        my_session = create_session_with_ssl_context(ssl_ctx)

        # 初始化币安交易所
        exchange = ccxt.binance({
            'session': my_session,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'  # 现货交易
            }
        })

        # 计算5年前的时间戳
        end_time = datetime.now()
        start_time = end_time - timedelta(days=5*365)
        
        # 转换为ISO 8601格式的时间字符串
        start_timestamp = exchange.parse8601(f'{start_time.strftime("%Y-%m-%d")}T00:00:00Z')
        end_timestamp = exchange.parse8601(f'{end_time.strftime("%Y-%m-%d")}T23:59:59Z')

        app_logger.info(f"开始获取BTC/USDT从 {start_time} 到 {end_time} 的1分钟K线数据")

        # 创建数据库会话
        db = SessionLocal()
        try:
            all_klines = []
            current_timestamp = start_timestamp
            batch_size = 1000  # 每批处理的数据量

            while current_timestamp < end_timestamp:
                try:
                    # 获取K线数据
                    klines = exchange.fetch_ohlcv(
                        'BTC/USDT',
                        timeframe='1m',
                        since=current_timestamp,
                        limit=1000  # 币安API限制每次最多1000条数据
                    )

                    if not klines:
                        break

                    # 添加数据到列表
                    all_klines.extend(klines)
                    
                    # 更新当前时间戳为最后一条数据的时间戳
                    current_timestamp = klines[-1][0] + 60000  # 加一分钟
                    
                    app_logger.info(f"已获取 {len(all_klines)} 条K线数据，当前时间: {datetime.fromtimestamp(current_timestamp/1000)}")
                    
                    # 当累积的数据达到批处理大小时，写入数据库
                    if len(all_klines) >= batch_size:
                        save_klines_to_db(db, all_klines[:batch_size])
                        all_klines = all_klines[batch_size:]
                    
                    # 避免触发API限制
                    time.sleep(exchange.rateLimit / 1000)
                    
                except Exception as e:
                    app_logger.error(f"获取数据时发生错误: {str(e)}")
                    time.sleep(5)  # 发生错误时等待5秒
                    continue

            # 处理剩余的数据
            if all_klines:
                save_klines_to_db(db, all_klines)
            
            app_logger.info("数据获取和保存完成")
            return True

        finally:
            db.close()

    except Exception as e:
        app_logger.error(f"获取数据过程中发生错误: {str(e)}")
        return False

def save_klines_to_db(db, klines_data, interval_minutes=1):
    """将K线数据保存到数据库
    
    Args:
        db: 数据库会话
        klines_data: K线数据列表
        interval_minutes: K线周期（分钟）
    """
    try:
        # 转换为DataFrame
        df = pd.DataFrame(klines_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # 数据验证
        if df.empty:
            app_logger.warning("没有数据需要保存")
            return
            
        # 验证时间戳
        current_time = int(datetime.now().timestamp() * 1000)
        if df['timestamp'].max() > current_time:
            app_logger.warning("存在未来的时间戳数据")
            
        # 验证价格
        if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
            raise ValueError("存在非正数价格")
            
        # 验证成交量
        if (df['volume'] < 0).any():
            raise ValueError("存在负数成交量")
        
        # 转换时间戳为datetime
        df['open_time'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = df['open_time'] + pd.Timedelta(minutes=interval_minutes)
        
        # 计算其他字段
        df['quote_volume'] = df['volume'] * df['close']
        df['trades_count'] = 0  # 由于1分钟K线数据不包含成交笔数，设为0
        df['taker_buy_volume'] = df['volume'] * 0.5  # 估算值
        df['taker_buy_quote_volume'] = df['taker_buy_volume'] * df['close']

        # 重命名列以匹配数据库表结构
        df = df.rename(columns={
            'open': 'open_price',
            'high': 'high_price',
            'low': 'low_price',
            'close': 'close_price'
        })

        # 选择需要的列
        columns = [
            'timestamp', 'open_time', 'close_time', 'open_price', 'high_price',
            'low_price', 'close_price', 'volume', 'quote_volume', 'trades_count',
            'taker_buy_volume', 'taker_buy_quote_volume'
        ]
        df = df[columns]

        # 批量处理大小
        BATCH_SIZE = 1000
        
        # 将DataFrame转换为K线对象列表并分批处理
        total_saved = 0
        for i in range(0, len(df), BATCH_SIZE):
            batch_df = df.iloc[i:i+BATCH_SIZE]
            kline_objects = []
            
            for _, row in batch_df.iterrows():
                try:
                    kline_obj = BtcUsdtKlineCreate(
                        timestamp=int(row['timestamp']),
                        open_time=row['open_time'],
                        close_time=row['close_time'],
                        open_price=Decimal(str(row['open_price'])),
                        high_price=Decimal(str(row['high_price'])),
                        low_price=Decimal(str(row['low_price'])),
                        close_price=Decimal(str(row['close_price'])),
                        volume=Decimal(str(row['volume'])),
                        quote_volume=Decimal(str(row['quote_volume'])),
                        trades_count=int(row['trades_count']),
                        taker_buy_volume=Decimal(str(row['taker_buy_volume'])),
                        taker_buy_quote_volume=Decimal(str(row['taker_buy_quote_volume']))
                    )
                    kline_objects.append(kline_obj)
                except Exception as e:
                    app_logger.error(f"处理行数据时发生错误: {str(e)}")
                    app_logger.error(f"问题数据: {row.to_dict()}")
                    continue
            
            if kline_objects:
                try:
                    kline.bulk_create(db, symbol='btc_usdt', obj_in_list=kline_objects)
                    total_saved += len(kline_objects)
                    app_logger.info(f"成功写入 {len(kline_objects)} 条K线数据到数据库")
                except Exception as e:
                    app_logger.error(f"批量保存数据时发生错误: {str(e)}")
                    # 继续处理下一批数据
                    continue
        
        app_logger.info(f"总共成功写入 {total_saved} 条K线数据到数据库")
        
    except Exception as e:
        app_logger.error(f"保存数据到数据库时发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    get_binance_data() 