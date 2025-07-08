"""
数据库表创建脚本
运行此脚本来创建缠论分析系统所需的数据库表
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def create_tables():
    """创建数据库表"""
    try:
        print("🐢 缠论分析系统 - 数据库初始化")
        print("=" * 40)

        # 导入必要的模块
        from app.db.session import engine
        from app.db.base_class import Base
        from app.models.kline import BtcUsdtKline, EthUsdtKline
        from app.core.config import settings
        from app.core.logger import app_logger

        print(f"📋 数据库连接: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")

        # 测试数据库连接
        print("🔍 测试数据库连接...")
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            print("\n💡 请检查:")
            print("   1. 数据库服务是否运行")
            print("   2. DATABASE_URL配置是否正确")
            print("   3. 数据库是否已创建")
            return False

        # 创建所有表
        print("🏗️ 创建数据库表...")
        Base.metadata.create_all(bind=engine)

        # 验证表创建
        print("🔍 验证表创建...")

        with engine.connect() as conn:
            # 检查BTC/USDT表
            try:
                result = conn.execute("SELECT COUNT(*) FROM btc_usdt")
                btc_count = result.fetchone()[0]
                print(f"✅ btc_usdt表: 存在 ({btc_count} 条记录)")
            except Exception as e:
                print(f"⚠️ btc_usdt表检查失败: {e}")

            # 检查ETH/USDT表（如果存在）
            try:
                result = conn.execute("SELECT COUNT(*) FROM eth_usdt")
                eth_count = result.fetchone()[0]
                print(f"✅ eth_usdt表: 存在 ({eth_count} 条记录)")
            except Exception:
                print("ℹ️ eth_usdt表: 未创建（正常，当前只使用BTC/USDT）")

        print("\n📊 表结构信息:")
        print("   🔹 btc_usdt: BTC/USDT 1分钟K线数据")
        print("     - timestamp: 时间戳(毫秒)")
        print("     - open_time/close_time: 开盘/收盘时间")
        print("     - open_price/high_price/low_price/close_price: OHLC价格")
        print("     - volume/quote_volume: 成交量和成交额")
        print("     - trades_count: 成交笔数")
        print("     - taker_buy_volume/taker_buy_quote_volume: 主动买入量")
        print("     - created_at/updated_at: 创建/更新时间")

        print("\n✅ 数据库表创建成功！")

        # 提供下一步指导
        print("\n📍 下一步操作:")
        print("   1. python quick_start.py                    # 启动系统")
        print("   2. POST /api/v1/simple/fetch-data           # 获取K线数据")
        print("   3. GET /api/v1/simple/klines?timeframe=1h   # 查看聚合数据")
        print("   4. GET /api/v1/chan/analyze?timeframe=1h    # 缠论分析")

        return True

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保已安装所有依赖: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        print("\n💡 常见问题解决:")
        print("   1. PostgreSQL未启动: sudo service postgresql start")
        print("   2. 数据库不存在: CREATE DATABASE turtle;")
        print("   3. 权限问题: 检查数据库用户权限")
        print("   4. 连接配置错误: 检查.env文件中的DATABASE_URL")
        return False


def check_database_status():
    """检查数据库状态"""
    try:
        from app.db.session import engine
        from app.services.kline_aggregator import kline_aggregator
        from app.db.session import SessionLocal

        print("\n🔍 数据库状态检查:")

        db = SessionLocal()
        try:
            # 获取数据统计
            stats = kline_aggregator.get_data_statistics(db)

            if stats.get("total_klines", 0) > 0:
                print(f"✅ 数据状态: {stats['total_klines']} 条K线记录")
                print(
                    f"   📅 数据范围: {stats.get('date_range', {}).get('start', 'N/A')} ~ {stats.get('date_range', {}).get('end', 'N/A')}")
                print(f"   💰 最新价格: ${stats.get('latest_price', 'N/A')}")
                print(f"   📊 数据覆盖: {stats.get('data_coverage', 'N/A')}")
            else:
                print("ℹ️ 数据状态: 数据库为空，需要获取数据")
                print("💡 运行以下命令获取数据:")
                print(
                    "   python -c \"from app.scripts.simple_fetch_data import *; SimpleBinanceDataFetcher().fetch_recent_data()\"")

        finally:
            db.close()

    except Exception as e:
        print(f"⚠️ 状态检查失败: {e}")


def reset_database():
    """重置数据库（危险操作）"""
    try:
        response = input("⚠️ 警告: 这将删除所有数据！确认重置数据库? (输入 'RESET' 确认): ")
        if response != "RESET":
            print("❌ 取消重置操作")
            return False

        from app.db.session import engine
        from app.db.base_class import Base

        print("🗑️ 删除所有表...")
        Base.metadata.drop_all(bind=engine)

        print("🏗️ 重新创建表...")
        Base.metadata.create_all(bind=engine)

        print("✅ 数据库重置完成")
        return True

    except Exception as e:
        print(f"❌ 数据库重置失败: {e}")
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='缠论分析系统数据库管理')
    parser.add_argument('--check', action='store_true', help='检查数据库状态')
    parser.add_argument('--reset', action='store_true', help='重置数据库（危险）')

    args = parser.parse_args()

    try:
        if args.check:
            # 仅检查状态
            check_database_status()
        elif args.reset:
            # 重置数据库
            if reset_database():
                check_database_status()
        else:
            # 默认创建表
            if create_tables():
                check_database_status()

    except KeyboardInterrupt:
        print("\n⏹️ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {str(e)}")


if __name__ == "__main__":
    main()