#!/usr/bin/env python3
"""
获取币安3年BTC/USDT历史K线数据的专用脚本

该脚本专门用于获取最近3年的BTC/USDT 1分钟K线数据
支持分批获取，避免API限制，并提供详细的进度信息
"""

import sys
import os
from datetime import datetime, timedelta
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scripts.simple_fetch_data import SimpleBinanceDataFetcher
from app.core.logger import app_logger


def fetch_3year_btc_data():
    """
    获取最近3年的BTC/USDT 1分钟K线数据
    
    Returns:
        bool: 是否成功获取数据
    """
    try:
        app_logger.info("🚀 开始获取最近3年的BTC/USDT历史K线数据")
        
        # 初始化数据获取器
        fetcher = SimpleBinanceDataFetcher()
        
        # 测试连接
        app_logger.info("🔗 测试币安API连接...")
        if not fetcher.test_connection():
            app_logger.error("❌ 币安API连接失败，无法继续")
            return False
        
        app_logger.info("✅ 币安API连接成功")
        
        # 计算3年的天数
        total_days = 365 * 3  # 3年约1095天
        app_logger.info(f"📅 将获取最近 {total_days} 天的数据")
        
        # 分批获取数据，每批30天，避免一次性获取过多数据
        batch_size = 30  # 每批30天
        total_batches = (total_days + batch_size - 1) // batch_size  # 向上取整
        
        success_count = 0
        total_processed = 0
        
        app_logger.info(f"📦 将分 {total_batches} 批次获取，每批 {batch_size} 天")
        
        for batch_num in range(total_batches):
            start_day = batch_num * batch_size
            end_day = min(start_day + batch_size, total_days)
            days_in_batch = end_day - start_day
            
            app_logger.info(f"📊 批次 {batch_num + 1}/{total_batches}: 获取第 {start_day + 1}-{end_day} 天的数据")
            
            # 获取这一批的数据
            batch_success = 0
            for day_offset in range(days_in_batch):
                current_day = start_day + day_offset
                
                # 计算当前天的时间范围
                end_time = datetime.now() - timedelta(days=current_day)
                start_time = end_time - timedelta(days=1)
                
                app_logger.info(f"  📅 第 {current_day + 1} 天: {start_time.strftime('%Y-%m-%d')} 到 {end_time.strftime('%Y-%m-%d')}")
                
                try:
                    # 获取24小时的数据
                    success = fetcher.fetch_recent_data(symbol='BTC/USDT', hours=24)
                    if success:
                        batch_success += 1
                        success_count += 1
                    
                    total_processed += 1
                    
                    # 显示进度
                    progress = (total_processed / total_days) * 100
                    app_logger.info(f"  ✅ 进度: {total_processed}/{total_days} ({progress:.1f}%)")
                    
                    # 避免API限制，每天之间休息一下
                    if day_offset < days_in_batch - 1:  # 不是批次中的最后一天
                        time.sleep(1)
                        
                except Exception as e:
                    app_logger.error(f"  ❌ 第 {current_day + 1} 天数据获取失败: {str(e)}")
                    continue
            
            app_logger.info(f"📈 批次 {batch_num + 1} 完成: 成功 {batch_success}/{days_in_batch} 天")
            
            # 批次之间休息更长时间
            if batch_num < total_batches - 1:  # 不是最后一批
                app_logger.info("⏳ 批次间休息 5 秒...")
                time.sleep(5)
        
        # 最终统计
        success_rate = (success_count / total_days) * 100
        app_logger.info(f"🎉 3年历史数据获取完成！")
        app_logger.info(f"📊 总计: 成功 {success_count}/{total_days} 天 ({success_rate:.1f}%)")
        
        return success_count > 0
        
    except KeyboardInterrupt:
        app_logger.info("⏹️ 用户中断操作")
        return False
    except Exception as e:
        app_logger.error(f"❌ 获取3年历史数据失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🪙 币安BTC/USDT 3年历史数据获取器")
    print("=" * 60)
    
    start_time = datetime.now()
    
    try:
        success = fetch_3year_btc_data()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 数据获取任务完成！")
        else:
            print("❌ 数据获取任务失败！")
        
        print(f"⏱️ 总耗时: {duration}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)