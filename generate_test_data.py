#!/usr/bin/env python3
"""
生成测试K线数据到数据库
用于在无法连接币安API时测试策略接口
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from decimal import Decimal
import random
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.kline import BtcUsdtKline
from app.core.logger import app_logger


def generate_realistic_kline(base_price: float, timestamp: int) -> dict:
    """生成逼真的K线数据"""
    # 随机波动幅度 0.1% - 2%
    volatility = random.uniform(0.001, 0.02)
    
    # 价格变化
    price_change = random.uniform(-volatility, volatility)
    open_price = base_price * (1 + price_change)
    
    # 生成最高价和最低价
    high_change = random.uniform(0, volatility * 0.5)
    low_change = random.uniform(0, volatility * 0.5)
    
    high_price = open_price * (1 + high_change)
    low_price = open_price * (1 - low_change)
    
    # 收盘价在开盘价附近波动
    close_change = random.uniform(-volatility * 0.3, volatility * 0.3)
    close_price = open_price * (1 + close_change)
    
    # 确保价格逻辑正确
    high_price = max(high_price, open_price, close_price)
    low_price = min(low_price, open_price, close_price)
    
    # 生成成交量 (10-1000 BTC)
    volume = random.uniform(10, 1000)
    
    return {
        'timestamp': timestamp,
        'open': round(open_price, 2),
        'high': round(high_price, 2),
        'low': round(low_price, 2),
        'close': round(close_price, 2),
        'volume': round(volume, 4)
    }


def generate_test_data(hours: int = 48, base_price: float = 60000.0) -> bool:
    """
    生成测试K线数据
    
    Args:
        hours: 生成多少小时的数据
        base_price: 基础价格
    
    Returns:
        bool: 是否成功
    """
    try:
        db = SessionLocal()
        
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        app_logger.info(f"🔄 开始生成 {hours} 小时的测试K线数据...")
        app_logger.info(f"📅 时间范围: {start_time} 到 {end_time}")
        app_logger.info(f"💰 基础价格: ${base_price:,.2f}")
        
        # 检查数据库中是否已有数据
        existing_count = db.query(BtcUsdtKline).count()
        if existing_count > 0:
            app_logger.info(f"📊 数据库中已有 {existing_count} 条数据，将跳过生成")
            return True
        
        saved_count = 0
        current_price = base_price
        
        # 生成每分钟的K线数据
        for i in range(hours * 60):  # 每小时60分钟
            current_time = start_time + timedelta(minutes=i)
            timestamp = int(current_time.timestamp() * 1000)
            
            # 生成K线数据
            kline_data = generate_realistic_kline(current_price, timestamp)
            
            # 更新当前价格为收盘价，用于下一根K线
            current_price = kline_data['close']
            
            try:
                # 创建K线记录
                kline_obj = BtcUsdtKline(
                    timestamp=timestamp,
                    open_time=current_time,
                    close_time=current_time + timedelta(minutes=1),
                    open_price=Decimal(str(kline_data['open'])),
                    high_price=Decimal(str(kline_data['high'])),
                    low_price=Decimal(str(kline_data['low'])),
                    close_price=Decimal(str(kline_data['close'])),
                    volume=Decimal(str(kline_data['volume'])),
                    quote_volume=Decimal(str(kline_data['volume'] * kline_data['close'])),
                    trades_count=random.randint(50, 500),
                    taker_buy_volume=Decimal(str(kline_data['volume'] * random.uniform(0.4, 0.6))),
                    taker_buy_quote_volume=Decimal(str(kline_data['volume'] * kline_data['close'] * random.uniform(0.4, 0.6))),
                    created_at=current_time,
                    updated_at=current_time,
                )
                
                db.add(kline_obj)
                saved_count += 1
                
                # 每1000条提交一次
                if saved_count % 1000 == 0:
                    db.commit()
                    app_logger.info(f"📦 已生成 {saved_count} 条数据...")
                    
            except Exception as e:
                app_logger.error(f"❌ 生成第 {i+1} 条数据失败: {str(e)}")
                continue
        
        # 最终提交
        db.commit()
        db.close()
        
        app_logger.info(f"✅ 测试数据生成完成！")
        app_logger.info(f"📊 总共生成 {saved_count} 条K线数据")
        app_logger.info(f"💰 价格范围: ${min(current_price, base_price):,.2f} - ${max(current_price, base_price):,.2f}")
        
        return True
        
    except Exception as e:
        app_logger.error(f"❌ 生成测试数据失败: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='生成测试K线数据')
    parser.add_argument('--hours', type=int, default=48, help='生成多少小时的数据，默认48小时')
    parser.add_argument('--price', type=float, default=60000.0, help='基础价格，默认60000')
    
    args = parser.parse_args()
    
    print(f"🚀 开始生成测试数据...")
    print(f"⏰ 时间长度: {args.hours} 小时")
    print(f"💰 基础价格: ${args.price:,.2f}")
    
    try:
        success = generate_test_data(hours=args.hours, base_price=args.price)
        if success:
            print("✅ 测试数据生成成功！")
            print("\n🔧 现在可以测试策略接口:")
            print("curl \"http://localhost:8000/api/v1/strategy/analyze?timeframe=1h&limit=50\"")
        else:
            print("❌ 测试数据生成失败！")
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")