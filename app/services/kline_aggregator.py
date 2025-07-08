from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_
import pandas as pd

from app.models.kline import BtcUsdtKline
from app.core.logger import app_logger


class KlineAggregator:
    """K线数据聚合器 - 将1分钟K线聚合为不同时间周期"""

    # 支持的时间周期（分钟）
    TIMEFRAMES = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '4h': 240,
        '1d': 1440
    }

    def __init__(self):
        app_logger.info("🔄 K线聚合器初始化完成")

    def aggregate_klines(
            self,
            db: Session,
            timeframe: str,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            limit: int = 200
    ) -> List[Dict]:
        """
        聚合K线数据

        Args:
            db: 数据库会话
            timeframe: 目标时间周期 (1m, 5m, 15m, 30m, 1h, 4h, 1d)
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数据条数限制

        Returns:
            List[Dict]: 聚合后的K线数据
        """
        try:
            if timeframe not in self.TIMEFRAMES:
                raise ValueError(f"不支持的时间周期: {timeframe}")

            # 如果是1分钟，直接返回原始数据
            if timeframe == '1m':
                return self._get_raw_klines(db, start_time, end_time, limit)

            # 获取聚合间隔（分钟）
            interval_minutes = self.TIMEFRAMES[timeframe]

            # 设置默认时间范围
            if not end_time:
                end_time = datetime.now()
            if not start_time:
                # 根据需要的数据量和时间周期计算开始时间
                total_minutes = limit * interval_minutes
                start_time = end_time - timedelta(minutes=total_minutes * 2)  # 多取一些数据确保足够

            app_logger.info(f"🔄 聚合 {timeframe} K线数据，时间范围: {start_time} 到 {end_time}")

            # 获取1分钟原始数据
            raw_klines = db.query(BtcUsdtKline).filter(
                and_(
                    BtcUsdtKline.open_time >= start_time,
                    BtcUsdtKline.open_time < end_time
                )
            ).order_by(BtcUsdtKline.open_time).all()

            if not raw_klines:
                app_logger.warning("没有找到原始K线数据")
                return []

            # 转换为DataFrame进行聚合
            df = self._klines_to_dataframe(raw_klines)
            aggregated_df = self._aggregate_dataframe(df, interval_minutes)

            # 转换回字典格式
            result = self._dataframe_to_dict_list(aggregated_df)

            # 限制返回数量
            result = result[-limit:] if len(result) > limit else result

            app_logger.info(f"✅ 成功聚合生成 {len(result)} 条 {timeframe} K线数据")
            return result

        except Exception as e:
            app_logger.error(f"❌ K线聚合失败: {str(e)}")
            raise

    def _get_raw_klines(
            self,
            db: Session,
            start_time: Optional[datetime],
            end_time: Optional[datetime],
            limit: int
    ) -> List[Dict]:
        """获取原始1分钟K线数据"""
        query = db.query(BtcUsdtKline)

        if start_time:
            query = query.filter(BtcUsdtKline.open_time >= start_time)
        if end_time:
            query = query.filter(BtcUsdtKline.open_time < end_time)

        klines = query.order_by(BtcUsdtKline.open_time.desc()).limit(limit).all()
        klines.reverse()  # 按时间正序

        return [self._kline_to_dict(kline) for kline in klines]

    def _klines_to_dataframe(self, klines: List[BtcUsdtKline]) -> pd.DataFrame:
        """将K线数据转换为DataFrame"""
        data = []
        for kline in klines:
            data.append({
                'timestamp': kline.timestamp,
                'open_time': kline.open_time,
                'open': float(kline.open_price),
                'high': float(kline.high_price),
                'low': float(kline.low_price),
                'close': float(kline.close_price),
                'volume': float(kline.volume),
                'quote_volume': float(kline.quote_volume),
                'trades_count': kline.trades_count,
                'taker_buy_volume': float(kline.taker_buy_volume),
                'taker_buy_quote_volume': float(kline.taker_buy_quote_volume)
            })

        df = pd.DataFrame(data)
        df['open_time'] = pd.to_datetime(df['open_time'])
        df.set_index('open_time', inplace=True)
        return df

    def _aggregate_dataframe(self, df: pd.DataFrame, interval_minutes: int) -> pd.DataFrame:
        """聚合DataFrame数据"""
        # 使用pandas的resample功能进行聚合
        aggregated = df.resample(f'{interval_minutes}T').agg({
            'timestamp': 'first',  # 使用第一个时间戳
            'open': 'first',  # 开盘价：第一个
            'high': 'max',  # 最高价：最大值
            'low': 'min',  # 最低价：最小值
            'close': 'last',  # 收盘价：最后一个
            'volume': 'sum',  # 成交量：求和
            'quote_volume': 'sum',  # 成交额：求和
            'trades_count': 'sum',  # 交易笔数：求和
            'taker_buy_volume': 'sum',
            'taker_buy_quote_volume': 'sum'
        }).dropna()

        # 重新计算时间戳
        aggregated['timestamp'] = (aggregated.index.astype('int64') // 10 ** 6).astype('int64')
        aggregated['close_time'] = aggregated.index + pd.Timedelta(minutes=interval_minutes)

        return aggregated

    def _dataframe_to_dict_list(self, df: pd.DataFrame) -> List[Dict]:
        """将DataFrame转换为字典列表"""
        result = []
        for index, row in df.iterrows():
            kline_dict = {
                'timestamp': int(row['timestamp']),
                'open_time': index.isoformat(),
                'close_time': row['close_time'].isoformat(),
                'open_price': str(round(row['open'], 8)),
                'high_price': str(round(row['high'], 8)),
                'low_price': str(round(row['low'], 8)),
                'close_price': str(round(row['close'], 8)),
                'volume': str(round(row['volume'], 8)),
                'quote_volume': str(round(row['quote_volume'], 8)),
                'trades_count': int(row['trades_count']),
                'taker_buy_volume': str(round(row['taker_buy_volume'], 8)),
                'taker_buy_quote_volume': str(round(row['taker_buy_quote_volume'], 8))
            }
            result.append(kline_dict)

        return result

    def _kline_to_dict(self, kline: BtcUsdtKline) -> Dict:
        """将K线对象转换为字典"""
        return {
            'timestamp': kline.timestamp,
            'open_time': kline.open_time.isoformat(),
            'close_time': kline.close_time.isoformat(),
            'open_price': str(kline.open_price),
            'high_price': str(kline.high_price),
            'low_price': str(kline.low_price),
            'close_price': str(kline.close_price),
            'volume': str(kline.volume),
            'quote_volume': str(kline.quote_volume),
            'trades_count': kline.trades_count,
            'taker_buy_volume': str(kline.taker_buy_volume),
            'taker_buy_quote_volume': str(kline.taker_buy_quote_volume)
        }

    def get_available_timeframes(self) -> List[str]:
        """获取支持的时间周期列表"""
        return list(self.TIMEFRAMES.keys())

    def get_latest_timestamp(self, db: Session) -> Optional[int]:
        """获取最新的K线时间戳"""
        latest = db.query(BtcUsdtKline.timestamp).order_by(
            BtcUsdtKline.timestamp.desc()
        ).first()
        return latest[0] if latest else None

    def get_data_statistics(self, db: Session) -> Dict:
        """获取数据统计信息"""
        try:
            total_count = db.query(BtcUsdtKline).count()

            if total_count == 0:
                return {
                    "total_klines": 0,
                    "date_range": None,
                    "latest_price": None
                }

            earliest = db.query(BtcUsdtKline.open_time).order_by(
                BtcUsdtKline.open_time.asc()
            ).first()

            latest = db.query(BtcUsdtKline).order_by(
                BtcUsdtKline.open_time.desc()
            ).first()

            return {
                "total_klines": total_count,
                "date_range": {
                    "start": earliest[0].isoformat() if earliest else None,
                    "end": latest.open_time.isoformat() if latest else None
                },
                "latest_price": float(latest.close_price) if latest else None,
                "data_coverage": f"{total_count // 1440:.1f} 天" if total_count > 1440 else f"{total_count} 条记录"
            }

        except Exception as e:
            app_logger.error(f"获取数据统计失败: {str(e)}")
            return {"error": str(e)}


# 创建全局实例
kline_aggregator = KlineAggregator()