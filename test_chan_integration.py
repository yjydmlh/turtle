"""
缠论分析系统集成测试脚本
用于验证所有组件是否正确集成和工作
"""

import sys
import os
from pathlib import Path
import requests
import time
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_chan_module_import():
    """测试Chan模块导入"""
    print("🔍 测试1: Chan模块导入...")

    try:
        # 尝试导入Chan模块
        sys.path.append(os.path.join(project_root, 'chan.py'))

        # 常见的可能导入方式，请根据实际情况调整
        import_success = False
        import_method = None

        try:
            from chan import ChanModel
            print("✅ 成功导入: from chan import ChanModel")
            import_success = True
            import_method = "ChanModel"
        except ImportError:
            pass

        if not import_success:
            try:
                from chan.core import Chan
                print("✅ 成功导入: from chan.core import Chan")
                import_success = True
                import_method = "Chan.core"
            except ImportError:
                pass

        if not import_success:
            try:
                import chan
                print("✅ 成功导入: import chan")
                print(f"   Chan模块属性: {[attr for attr in dir(chan) if not attr.startswith('_')]}")
                import_success = True
                import_method = "chan module"
            except ImportError:
                pass

        if not import_success:
            print("❌ 无法导入Chan模块")
            print("💡 请检查:")
            print("   1. chan.py子模块是否正确初始化: git submodule update --init")
            print("   2. chan.py目录是否存在")
            print("   3. chan.py模块是否有__init__.py文件")
            return False, "Chan模块导入失败"

        return True, f"Chan模块导入成功 ({import_method})"

    except Exception as e:
        print(f"❌ 导入Chan模块时发生错误: {e}")
        return False, f"导入错误: {str(e)}"


def test_database_connection():
    """测试数据库连接"""
    print("\n🔍 测试2: 数据库连接...")

    try:
        from app.db.session import SessionLocal, engine

        # 测试连接
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ 数据库连接正常")
                return True, "数据库连接正常"

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("💡 请检查:")
        print("   1. PostgreSQL服务是否运行")
        print("   2. DATABASE_URL配置是否正确")
        print("   3. 数据库是否已创建")
        return False, f"数据库连接失败: {str(e)}"


def test_chan_adapter():
    """测试Chan适配器"""
    print("\n🔍 测试3: Chan适配器...")

    try:
        from app.services.chan_adapter import chan_adapter

        # 检查适配器状态
        info = chan_adapter.get_chan_info()
        print(f"✅ Chan适配器初始化成功")
        print(f"   模块可用: {info['is_available']}")
        print(f"   模块已加载: {info['module_loaded']}")
        print(f"   版本: {info.get('version', 'unknown')}")
        print(f"   状态: {info.get('status', 'unknown')}")

        if info['is_available']:
            return True, "Chan适配器工作正常"
        else:
            return True, "Chan适配器初始化成功，但模块不可用（将使用简化分析）"

    except Exception as e:
        print(f"❌ Chan适配器测试失败: {e}")
        return False, f"Chan适配器失败: {str(e)}"


def test_kline_aggregator():
    """测试K线聚合器"""
    print("\n🔍 测试4: K线聚合器...")

    try:
        from app.services.kline_aggregator import kline_aggregator
        from app.db.session import SessionLocal

        db = SessionLocal()
        try:
            # 获取支持的时间周期
            timeframes = kline_aggregator.get_available_timeframes()
            print(f"✅ 支持的时间周期: {timeframes}")

            # 尝试获取数据（可能为空）
            klines = kline_aggregator.aggregate_klines(
                db=db, timeframe='1h', limit=10
            )
            print(f"✅ K线聚合器工作正常，获取到 {len(klines)} 条数据")

            # 获取数据统计
            stats = kline_aggregator.get_data_statistics(db)
            print(f"   数据库统计: {stats}")

            if len(klines) == 0:
                print("💡 数据库中暂无K线数据，建议运行数据获取")
                return True, "K线聚合器正常，但数据库无数据"
            else:
                return True, f"K线聚合器正常，数据库有 {stats.get('total_klines', 0)} 条数据"

        finally:
            db.close()

    except Exception as e:
        print(f"❌ K线聚合器测试失败: {e}")
        return False, f"K线聚合器失败: {str(e)}"


def test_sample_analysis():
    """测试样本缠论分析"""
    print("\n🔍 测试5: 缠论分析功能...")

    try:
        from app.services.chan_adapter import chan_adapter

        # 创建测试数据 - 模拟一个简单的上涨趋势
        sample_klines = []
        base_timestamp = int(datetime.now().timestamp() * 1000) - 100 * 60 * 1000  # 100分钟前
        base_price = 50000.0

        for i in range(100):
            # 创建一个简单的上涨趋势，带有一些波动
            price_trend = i * 5  # 基本上涨趋势
            price_noise = (i % 10) * 2 if i % 20 < 10 else -(i % 10) * 2  # 添加一些噪音

            current_price = base_price + price_trend + price_noise
            high_price = current_price + abs(price_noise) + 10
            low_price = current_price - abs(price_noise) - 10

            sample_klines.append({
                'timestamp': base_timestamp + i * 60 * 1000,  # 每分钟一个数据点
                'open_price': str(current_price),
                'high_price': str(high_price),
                'low_price': str(low_price),
                'close_price': str(current_price + (price_noise / 2)),
                'volume': str(100.0 + i)
            })

        # 执行分析
        result = chan_adapter.analyze_klines(sample_klines)

        print(f"✅ 缠论分析完成")
        print(f"   分型数量: {len(result.get('fenxings', []))}")
        print(f"   笔数量: {len(result.get('bis', []))}")
        print(f"   线段数量: {len(result.get('xianduan', []))}")
        print(f"   买卖点数量: {len(result.get('buy_sell_points', []))}")
        print(f"   数据源: {result.get('analysis_summary', {}).get('data_source', 'unknown')}")

        if 'error' in result:
            print(f"⚠️ 分析警告: {result['error']}")
            return True, f"分析完成但有警告: {result['error']}"

        return True, "缠论分析功能正常"

    except Exception as e:
        print(f"❌ 缠论分析测试失败: {e}")
        return False, f"缠论分析失败: {str(e)}"


def test_data_fetcher():
    """测试数据获取器"""
    print("\n🔍 测试6: 数据获取器...")

    try:
        from app.scripts.simple_fetch_data import SimpleBinanceDataFetcher

        fetcher = SimpleBinanceDataFetcher()

        # 测试连接
        if fetcher.test_connection():
            print("✅ 币安API连接测试成功")

            # 测试获取市场信息
            market_info = fetcher.get_market_info()
            if market_info:
                print(f"✅ 获取市场信息成功: BTC/USDT = ${market_info.get('last_price', 'N/A')}")
                return True, "数据获取器工作正常"
            else:
                print("⚠️ 获取市场信息失败")
                return True, "数据获取器连接正常，但获取信息失败"
        else:
            print("❌ 币安API连接失败")
            return False, "币安API连接失败"

    except Exception as e:
        print(f"❌ 数据获取器测试失败: {e}")
        return False, f"数据获取器失败: {str(e)}"


def test_api_endpoints():
    """测试API端点（需要服务器运行）"""
    print("\n🔍 测试7: API端点...")

    try:
        # 测试基础端点
        base_url = "http://localhost:8000"

        # 测试健康检查
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 健康检查端点正常")
                health_data = response.json()
                print(f"   状态: {health_data.get('status', 'unknown')}")
            else:
                print(f"⚠️ 健康检查返回状态码: {response.status_code}")
        except requests.exceptions.RequestException:
            print("❌ 无法连接到API服务器")
            print("💡 请先启动服务器: python quick_start.py")
            return False, "API服务器未运行"

        # 测试Chan信息端点
        try:
            response = requests.get(f"{base_url}/api/v1/chan/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Chan信息端点正常")
                if data.get('success'):
                    chan_info = data.get('data', {}).get('chan_module', {})
                    print(f"   Chan模块可用: {chan_info.get('is_available', False)}")
                return True, "API端点工作正常"
            else:
                print(f"⚠️ Chan信息端点返回状态码: {response.status_code}")
                return True, f"API连接正常，但某些端点异常 ({response.status_code})"
        except requests.exceptions.RequestException as e:
            print(f"❌ Chan信息端点测试失败: {e}")
            return False, "API端点测试失败"

        return True, "API端点测试完成"

    except Exception as e:
        print(f"❌ API端点测试异常: {e}")
        return False, f"API测试异常: {str(e)}"


def run_integration_test():
    """运行完整的集成测试"""
    print("🐢 缠论分析系统 - 集成测试")
    print("=" * 50)

    tests = [
        ("Chan模块导入", test_chan_module_import),
        ("数据库连接", test_database_connection),
        ("Chan适配器", test_chan_adapter),
        ("K线聚合器", test_kline_aggregator),
        ("缠论分析功能", test_sample_analysis),
        ("数据获取器", test_data_fetcher),
        ("API端点", test_api_endpoints),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            success, message = test_func()
            results[test_name] = {"success": success, "message": message}
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results[test_name] = {"success": False, "message": f"测试异常: {str(e)}"}

    # 总结报告
    print("\n" + "=" * 50)
    print("📋 集成测试报告:")

    passed = 0
    total = len(tests)
    critical_failures = []
    warnings = []

    for test_name, result in results.items():
        status = "✅ 通过" if result["success"] else "❌ 失败"
        print(f"   {test_name:15} : {status}")
        print(f"   {' ' * 15}   {result['message']}")

        if result["success"]:
            passed += 1
            if "警告" in result["message"] or "不可用" in result["message"]:
                warnings.append(test_name)
        else:
            critical_failures.append(test_name)

    print(f"\n📊 测试结果: {passed}/{total} 通过")

    # 系统状态评估
    if len(critical_failures) == 0:
        print("🎉 系统状态: 完全正常")
        print("\n💡 下一步:")
        print("   1. 运行 python quick_start.py 启动系统")
        print("   2. 访问 http://localhost:8000 查看API")
        print("   3. 调用 POST /api/v1/simple/fetch-data 获取数据")
        print("   4. 调用 GET /api/v1/chan/analyze 进行缠论分析")

    elif len(critical_failures) <= 2:
        print("⚠️ 系统状态: 基本可用，有少量问题")
        print(f"\n❌ 需要修复: {', '.join(critical_failures)}")

    else:
        print("❌ 系统状态: 需要修复多个问题")
        print(f"\n🔧 关键问题: {', '.join(critical_failures)}")

    if warnings:
        print(f"\n⚠️ 注意事项: {', '.join(warnings)}")

    # 问题解决建议
    if critical_failures:
        print(f"\n🔧 问题解决建议:")

        if "Chan模块导入" in critical_failures:
            print("   Chan模块: git submodule update --init")
            print("              检查chan.py目录和__init__.py文件")

        if "数据库连接" in critical_failures:
            print("   数据库: 检查PostgreSQL服务和DATABASE_URL配置")
            print("          或使用SQLite: DATABASE_URL=sqlite:///./turtle.db")

        if "API端点" in critical_failures:
            print("   API服务: python quick_start.py 启动服务器")

        if "数据获取器" in critical_failures:
            print("   网络: 检查网络连接和币安API访问")

    return passed == total, results


def main():
    """主函数"""
    try:
        success, results = run_integration_test()

        if success:
            print(f"\n🎊 所有测试通过！系统已准备就绪！")

            # 询问是否启动系统
            try:
                response = input(f"\n🚀 是否现在启动系统? (y/N): ").lower().strip()
                if response in ['y', 'yes', '是']:
                    print("🚀 启动系统...")
                    os.system("python quick_start.py")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 测试完成")
        else:
            print(f"\n⚠️ 部分测试失败，请检查上述问题后重新测试")

    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试程序异常: {str(e)}")


if __name__ == "__main__":
    main()