#!/usr/bin/env python3
"""
优化的3年BTC/USDT历史K线数据获取脚本

使用项目现有的CRUD类和数据模型，高效获取并插入3年历史数据
"""

import sys
import os
from datetime import datetime, timedelta
import time
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.crud.kline import CRUDKline
from app.schemas.kline import BtcUsdtKlineCreate
from app.core.logger import app_logger
from app.scripts.simple_fetch_data import SimpleBinanceDataFetcher


class OptimizedBtcDataFetcher:
    """优化的BTC数据获取器"""
    
    def __init__(self):
        self.fetcher = SimpleBinanceDataFetcher()
        self.crud = CRUDKline()
        self.symbol = "btc_usdt"
        
    def fetch_and_save_3year_data(self, test_mode: bool = False):
        """
        获取并保存3年BTC/USDT历史数据
        
        Args:
            test_mode: 测试模式，只获取少量数据
        """
        try:
            app_logger.info("🚀 开始获取3年BTC/USDT历史K线数据")
            
            # 测试连接
            if not self.fetcher.test_connection():
                app_logger.error("❌ 币安API连接失败")
                return False
            
            # 计算时间范围
            if test_mode:
                # 测试模式：只获取最近1天的数据
                total_days = 1
                app_logger.info("🧪 测试模式：获取最近1天数据")
            else:
                # 正式模式：获取3年数据
                total_days = 365 * 3
                app_logger.info(f"📅 正式模式：获取最近{total_days}天数据")
            
            # 分批获取，每批7天
            batch_days = 7 if not test_mode else 1
            total_batches = (total_days + batch_days - 1) // batch_days
            
            success_count = 0
            total_saved = 0
            
            app_logger.info(f"📦 将分{total_batches}批次获取，每批{batch_days}天")
            
            db = SessionLocal()
            try:
                for batch_num in range(total_batches):
                    start_day = batch_num * batch_days
                    end_day = min(start_day + batch_days, total_days)
                    
                    app_logger.info(f"📊 批次 {batch_num + 1}/{total_batches}")
                    
                    # 计算这一批的时间范围
                    batch_end_time = datetime.now() - timedelta(days=start_day)
                    batch_start_time = batch_end_time - timedelta(days=batch_days)
                    
                    app_logger.info(f"  📅 时间范围: {batch_start_time.strftime('%Y-%m-%d')} 到 {batch_end_time.strftime('%Y-%m-%d')}")
                    
                    # 获取这一批的数据
                    batch_data = self._fetch_batch_data(batch_start_time, batch_end_time)
                    
                    if batch_data:
                        # 使用CRUD类保存数据
                        saved_count = self._save_batch_with_crud(db, batch_data)
                        total_saved += saved_count
                        success_count += 1
                        
                        app_logger.info(f"  ✅ 批次完成：保存 {saved_count} 条数据")
                    else:
                        app_logger.warning(f"  ⚠️ 批次 {batch_num + 1} 未获取到数据")
                    
                    # 批次间休息
                    if batch_num < total_batches - 1:
                        app_logger.info("  ⏳ 休息2秒...")
                        time.sleep(2)
                
                # 最终统计
                success_rate = (success_count / total_batches) * 100
                app_logger.info(f"🎉 数据获取完成！")
                app_logger.info(f"📊 成功批次: {success_count}/{total_batches} ({success_rate:.1f}%)")
                app_logger.info(f"💾 总计保存: {total_saved} 条数据")
                
                return total_saved > 0
                
            finally:
                db.close()
                
        except Exception as e:
            app_logger.error(f"❌ 获取数据失败: {str(e)}")
            return False
    
    def _fetch_batch_data(self, start_time: datetime, end_time: datetime) -> list:
        """获取一批数据"""
        try:
            # 转换时间戳
            since = self.fetcher.exchange.parse8601(start_time.isoformat())
            end_timestamp = self.fetcher.exchange.parse8601(end_time.isoformat())
            
            all_klines = []
            current_since = since
            
            while current_since < end_timestamp:
                try:
                    # 获取K线数据
                    klines = self.fetcher.exchange.fetch_ohlcv(
                        'BTC/USDT',
                        timeframe='1m',
                        since=current_since,
                        limit=1000
                    )
                    
                    if not klines:
                        break
                    
                    # 过滤时间范围内的数据
                    filtered_klines = [k for k in klines if since <= k[0] < end_timestamp]
                    all_klines.extend(filtered_klines)
                    
                    # 更新时间戳
                    current_since = klines[-1][0] + 60000  # 加1分钟
                    
                    # 如果已经超过结束时间，停止
                    if current_since >= end_timestamp:
                        break
                    
                    # 避免API限制
                    time.sleep(0.1)
                    
                except Exception as e:
                    app_logger.error(f"  ❌ 获取数据失败: {str(e)}")
                    time.sleep(1)
                    continue
            
            app_logger.info(f"  📈 获取到 {len(all_klines)} 条原始数据")
            return all_klines
            
        except Exception as e:
            app_logger.error(f"❌ 批次数据获取失败: {str(e)}")
            return []
    
    def _save_batch_with_crud(self, db, klines_data: list) -> int:
        """使用CRUD类保存批次数据"""
        saved_count = 0
        skipped_count = 0
        
        app_logger.info(f"  💾 开始保存 {len(klines_data)} 条数据...")
        
        for kline in klines_data:
            try:
                timestamp = kline[0]
                
                # 检查是否已存在（通过时间戳查询）
                from app.models.kline import BtcUsdtKline
                existing = db.query(BtcUsdtKline).filter(
                    BtcUsdtKline.timestamp == timestamp
                ).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # 创建K线数据对象
                kline_create = BtcUsdtKlineCreate(
                    timestamp=timestamp,
                    open_time=datetime.fromtimestamp(timestamp / 1000),
                    close_time=datetime.fromtimestamp(timestamp / 1000) + timedelta(minutes=1),
                    open_price=Decimal(str(kline[1])),
                    high_price=Decimal(str(kline[2])),
                    low_price=Decimal(str(kline[3])),
                    close_price=Decimal(str(kline[4])),
                    volume=Decimal(str(kline[5])),
                    quote_volume=Decimal(str(kline[5] * kline[4])),
                    trades_count=0,
                    taker_buy_volume=Decimal(str(kline[5] * 0.5)),
                    taker_buy_quote_volume=Decimal(str(kline[5] * kline[4] * 0.5)),
                )
                
                # 使用CRUD创建数据
                self.crud.create(db, symbol=self.symbol, obj_in=kline_create)
                saved_count += 1
                
            except Exception as e:
                app_logger.error(f"  ❌ 保存单条数据失败: {str(e)}")
                continue
        
        app_logger.info(f"  📊 保存结果: 新增 {saved_count} 条，跳过 {skipped_count} 条")
        return saved_count


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='优化的3年BTC数据获取器')
    parser.add_argument('--test', action='store_true', help='测试模式，只获取少量数据')
    
    args = parser.parse_args()
    
    print("=" * 60, flush=True)
    print("🪙 优化的BTC/USDT 3年历史数据获取器", flush=True)
    print("=" * 60, flush=True)
    
    start_time = datetime.now()
    
    try:
        fetcher = OptimizedBtcDataFetcher()
        success = fetcher.fetch_and_save_3year_data(test_mode=args.test)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 数据获取任务完成！")
        else:
            print("❌ 数据获取任务失败！")
        
        print(f"⏱️ 总耗时: {duration}")
        print("=" * 60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)