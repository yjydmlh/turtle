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
    """优化的BTC数据获取器（支持断点续传）"""
    
    def __init__(self):
        self.fetcher = SimpleBinanceDataFetcher()
        self.crud = CRUDKline()
        self.symbol = "btc_usdt"
    

    
    def analyze_data_gaps(self):
        """分析数据库中的数据缺口"""
        db = SessionLocal()
        try:
            from app.models.kline import BtcUsdtKline
            from sqlalchemy import func
            
            # 查询数据库中的时间范围
            result = db.query(
                func.min(BtcUsdtKline.timestamp).label('min_timestamp'),
                func.max(BtcUsdtKline.timestamp).label('max_timestamp'),
                func.count(BtcUsdtKline.id).label('total_count')
            ).first()
            
            if not result or not result.min_timestamp:
                app_logger.info("📊 数据库为空，需要获取完整的3年数据")
                return self._get_full_range()
            
            # 计算3年前的时间戳
            three_years_ago = datetime.now() - timedelta(days=3*365)
            target_start_timestamp = int(three_years_ago.timestamp() * 1000)
            current_timestamp = int(datetime.now().timestamp() * 1000)
            
            gaps = []
            
            # 检查历史数据缺口
            if result.min_timestamp > target_start_timestamp:
                gaps.append({
                    'type': 'historical',
                    'start_timestamp': target_start_timestamp,
                    'end_timestamp': result.min_timestamp - 60000,  # 减1分钟避免重复
                    'description': f'历史数据缺口: {three_years_ago.strftime("%Y-%m-%d")} 到 {datetime.fromtimestamp(result.min_timestamp/1000).strftime("%Y-%m-%d")}'
                })
            
            # 检查最新数据缺口
            if result.max_timestamp < current_timestamp - 300000:  # 5分钟前
                gaps.append({
                    'type': 'recent',
                    'start_timestamp': result.max_timestamp + 60000,  # 加1分钟避免重复
                    'end_timestamp': current_timestamp,
                    'description': f'最新数据缺口: {datetime.fromtimestamp(result.max_timestamp/1000).strftime("%Y-%m-%d")} 到现在'
                })
            
            app_logger.info(f"📊 数据库状态: 共 {result.total_count} 条记录")
            app_logger.info(f"📅 时间范围: {datetime.fromtimestamp(result.min_timestamp/1000).strftime('%Y-%m-%d %H:%M')} 到 {datetime.fromtimestamp(result.max_timestamp/1000).strftime('%Y-%m-%d %H:%M')}")
            
            if gaps:
                app_logger.info(f"🔍 发现 {len(gaps)} 个数据缺口:")
                for i, gap in enumerate(gaps, 1):
                    app_logger.info(f"  {i}. {gap['description']}")
            else:
                app_logger.info("✅ 数据完整，无需补充")
            
            return gaps
            
        finally:
            db.close()
    
    def _get_full_range(self):
        """获取完整的3年数据范围"""
        three_years_ago = datetime.now() - timedelta(days=3*365)
        current_time = datetime.now()
        
        return [{
            'type': 'full',
            'start_timestamp': int(three_years_ago.timestamp() * 1000),
            'end_timestamp': int(current_time.timestamp() * 1000),
            'description': f'完整3年数据: {three_years_ago.strftime("%Y-%m-%d")} 到 {current_time.strftime("%Y-%m-%d")}'
        }]
        
    def fetch_specific_range(self, start_date: str, end_date: str, test_mode: bool = False) -> bool:
        """
        获取指定时间范围的数据
        
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            test_mode: 测试模式，只获取少量数据
        """
        try:
            # 解析日期
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            app_logger.info(f"🎯 开始获取指定时间范围的数据: {start_date} 到 {end_date}")
            
            # 测试连接
            if not self.fetcher.test_connection():
                app_logger.error("❌ 币安API连接失败")
                return False
            
            # 创建时间范围缺口
            gap = {
                'start_timestamp': int(start_dt.timestamp() * 1000),
                'end_timestamp': int(end_dt.timestamp() * 1000),
                'description': f'指定范围: {start_date} 到 {end_date}'
            }
            
            return self._fetch_missing_data([gap], test_mode)
            
        except ValueError as e:
            app_logger.error(f"❌ 日期格式错误: {str(e)}")
            return False
        except Exception as e:
            app_logger.error(f"❌ 获取指定范围数据失败: {str(e)}")
            return False

    def fetch_and_save_3year_data(self, test_mode: bool = False, resume_mode: bool = False):
        """
        获取并保存3年BTC/USDT历史数据（支持断点续传）
        
        Args:
            test_mode: 测试模式，只获取少量数据
            resume_mode: 断点续传模式，只获取缺失的数据
        """
        try:
            app_logger.info("🚀 开始获取3年BTC/USDT历史K线数据")
            
            # 测试连接
            if not self.fetcher.test_connection():
                app_logger.error("❌ 币安API连接失败")
                return False
            
            if resume_mode:
                # 断点续传模式：分析数据缺口
                app_logger.info("🔄 断点续传模式：分析数据缺口...")
                gaps = self.analyze_data_gaps()
                
                if not gaps:
                    app_logger.info("✅ 数据已完整，无需获取")
                    return True
                
                return self._fetch_missing_data(gaps, test_mode)
            else:
                # 原始模式：按时间顺序获取
                return self._fetch_sequential_data(test_mode)
                
        except Exception as e:
            app_logger.error(f"❌ 获取数据失败: {str(e)}")
            return False
    
    def _fetch_missing_data(self, gaps: list, test_mode: bool = False) -> bool:
        """获取缺失的数据"""
        try:
            if test_mode:
                app_logger.info("🧪 测试模式：只处理第一个缺口的部分数据")
                gaps = gaps[:1]  # 只处理第一个缺口
                # 限制测试数据量
                gap = gaps[0]
                test_end = gap['start_timestamp'] + 3600000  # 1小时
                gap['end_timestamp'] = min(gap['end_timestamp'], test_end)
            
            total_saved = 0
            
            for gap_index, gap in enumerate(gaps, 1):
                app_logger.info(f"📦 处理缺口 {gap_index}/{len(gaps)}: {gap['description']}")
                
                # 将缺口按天分批处理
                start_timestamp = gap['start_timestamp']
                end_timestamp = gap['end_timestamp']
                
                # 按7天为一批处理
                batch_size_ms = 7 * 24 * 60 * 60 * 1000  # 7天的毫秒数
                current_start = start_timestamp
                
                while current_start < end_timestamp:
                    current_end = min(current_start + batch_size_ms, end_timestamp)
                    
                    # 转换为datetime对象
                    batch_start_time = datetime.fromtimestamp(current_start / 1000)
                    batch_end_time = datetime.fromtimestamp(current_end / 1000)
                    
                    app_logger.info(f"  📅 处理时间段: {batch_start_time.strftime('%Y-%m-%d %H:%M')} 到 {batch_end_time.strftime('%Y-%m-%d %H:%M')}")
                    
                    # 获取这一批的数据
                    batch_data = self._fetch_batch_data(batch_start_time, batch_end_time)
                    
                    if batch_data:
                        db = SessionLocal()
                        try:
                            saved_count = self._save_batch_with_crud(db, batch_data)
                            total_saved += saved_count
                            app_logger.info(f"  ✅ 批次完成：保存 {saved_count} 条数据")
                        finally:
                            db.close()
                    else:
                        app_logger.warning(f"  ⚠️ 未获取到数据")
                    
                    current_start = current_end
                    
                    # 批次间休息
                    if current_start < end_timestamp:
                        app_logger.info("  ⏳ 休息2秒...")
                        time.sleep(2)
                
                app_logger.info(f"✅ 缺口 {gap_index} 完成")
                
                # 缺口间休息
                if gap_index < len(gaps):
                    app_logger.info("⏳ 休息5秒...")
                    time.sleep(5)
            
            app_logger.info(f"🎉 断点续传完成！总计保存 {total_saved} 条数据")
            return total_saved > 0
            
        except Exception as e:
            app_logger.error(f"❌ 断点续传失败: {str(e)}")
            return False
    
    def _fetch_sequential_data(self, test_mode: bool = False) -> bool:
        """按时间顺序获取数据（原始逻辑）"""
        try:
            
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
            # 直接使用时间戳，避免时区转换问题
            since = int(start_time.timestamp() * 1000)
            end_timestamp = int(end_time.timestamp() * 1000)
            
            app_logger.info(f"  🔍 获取时间范围: {datetime.fromtimestamp(since/1000)} 到 {datetime.fromtimestamp(end_timestamp/1000)}")
            
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
                        app_logger.info(f"  📊 没有更多数据，当前时间戳: {current_since}")
                        break
                    
                    # 过滤时间范围内的数据
                    filtered_klines = [k for k in klines if since <= k[0] < end_timestamp]
                    all_klines.extend(filtered_klines)
                    
                    app_logger.info(f"  📈 本批获取 {len(klines)} 条，过滤后 {len(filtered_klines)} 条，累计 {len(all_klines)} 条")
                    
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
    
    parser = argparse.ArgumentParser(description='优化的3年BTC数据获取器（支持断点续传）')
    parser.add_argument('--test', action='store_true', help='测试模式，只获取少量数据')
    parser.add_argument('--resume', action='store_true', help='断点续传模式，只获取缺失的数据')
    parser.add_argument('--analyze-only', action='store_true', help='仅分析数据缺口，不获取数据')
    parser.add_argument('--fetch-range', nargs=2, metavar=('START_DATE', 'END_DATE'), 
                       help='获取指定时间范围的数据，格式：YYYY-MM-DD YYYY-MM-DD')
    
    args = parser.parse_args()
    
    print("=" * 60, flush=True)
    print("🪙 优化的BTC/USDT 3年历史数据获取器（支持断点续传）", flush=True)
    print("=" * 60, flush=True)
    
    start_time = datetime.now()
    print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    
    try:
        fetcher = OptimizedBtcDataFetcher()
        
        if args.analyze_only:
            print("\n🔍 仅分析数据缺口模式", flush=True)
            gaps = fetcher.analyze_data_gaps()
            success = True
        elif args.fetch_range:
            print(f"\n🎯 获取指定时间范围数据模式: {args.fetch_range[0]} 到 {args.fetch_range[1]}", flush=True)
            success = fetcher.fetch_specific_range(
                start_date=args.fetch_range[0],
                end_date=args.fetch_range[1],
                test_mode=args.test
            )
        else:
            success = fetcher.fetch_and_save_3year_data(
                test_mode=args.test, 
                resume_mode=args.resume
            )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60, flush=True)
        print(f"⏰ 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print(f"⏱️ 总耗时: {duration}", flush=True)
        
        if success:
            print("✅ 任务完成！", flush=True)
        else:
            print("❌ 任务失败！", flush=True)
        
        print("=" * 60, flush=True)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作", flush=True)
        return 1
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}", flush=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)