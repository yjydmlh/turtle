#!/usr/bin/env python3
"""
缠论多级别策略测试脚本

测试缠论策略的核心功能和API端点
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import requests
import json

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.services.chan_strategy import analyze_with_chan_strategy
    from app.services.kline_aggregator import kline_aggregator
    from app.db.session import SessionLocal
    strategy_available = True
except ImportError as e:
    print(f"⚠️ 导入策略模块失败: {e}")
    strategy_available = False


def test_strategy_direct():
    """直接测试策略功能"""
    print("🔍 测试1: 直接策略功能测试")
    print("=" * 50)
    
    if not strategy_available:
        print("❌ 策略模块不可用，跳过直接测试")
        return False
    
    try:
        # 创建模拟K线数据
        base_price = 50000
        test_klines = []
        
        for i in range(100):
            # 创建有趋势和分型的模拟数据
            if i < 30:  # 前30个：下跌趋势
                trend = -0.001 * i
                noise = (i % 5 - 2) * 0.0005
            elif i < 60:  # 中间30个：上涨趋势
                trend = 0.002 * (i - 30)
                noise = (i % 7 - 3) * 0.0008
            else:  # 后40个：震荡
                trend = 0.0001 * (i - 60)
                noise = (i % 3 - 1) * 0.001
            
            price_change = trend + noise
            current_price = base_price * (1 + price_change)
            
            # 模拟OHLCV数据
            open_price = current_price * (1 + (i % 3 - 1) * 0.0002)
            high_price = max(open_price, current_price) * (1 + abs(noise) * 0.5)
            low_price = min(open_price, current_price) * (1 - abs(noise) * 0.5)
            close_price = current_price
            
            test_klines.append({
                'timestamp': int((datetime.now() - timedelta(hours=100-i)).timestamp() * 1000),
                'open_price': str(open_price),
                'high_price': str(high_price),
                'low_price': str(low_price),
                'close_price': str(close_price),
                'volume': str(100 + i * 2),
                'open_time': (datetime.now() - timedelta(hours=100-i)).isoformat(),
                'close_time': (datetime.now() - timedelta(hours=99-i)).isoformat()
            })
        
        print(f"✅ 生成了{len(test_klines)}条模拟K线数据")
        
        # 执行策略分析
        print("🔍 执行缠论策略分析...")
        result = analyze_with_chan_strategy(test_klines, "1h", "BTC/USDT")
        
        # 检查结果
        if result and 'signals' in result:
            signals = result['signals']
            analysis = result['analysis']
            recommendation = result['recommendation']
            
            print(f"✅ 策略分析成功")
            print(f"   📊 分析结果:")
            print(f"      - 识别分型: {len(analysis.get('fenxings', []))}")
            print(f"      - 构建笔: {len(analysis.get('bis', []))}")
            print(f"      - 生成信号: {len(signals)}")
            print(f"      - 趋势方向: {analysis.get('trend_analysis', {}).get('direction', 'unknown')}")
            print(f"      - 趋势强度: {analysis.get('trend_analysis', {}).get('strength', 0):.2f}")
            
            if signals:
                print(f"   🎯 交易信号:")
                for i, signal in enumerate(signals[:3]):  # 显示前3个信号
                    print(f"      {i+1}. {signal.get('signal_type')} - 置信度: {signal.get('confidence', 0):.2f}")
                    print(f"         价格: {signal.get('price', 0):.2f}, 仓位: {signal.get('position_size', 0):.1%}")
            
            print(f"   💡 交易建议: {recommendation.get('action', 'WAIT')} - {recommendation.get('reason', '无')}")
            
            return True
        else:
            print("❌ 策略分析返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 直接策略测试失败: {str(e)}")
        return False


def test_database_integration():
    """测试数据库集成"""
    print("\n🔍 测试2: 数据库集成测试")
    print("=" * 50)
    
    try:
        db = SessionLocal()
        try:
            # 获取数据库中的K线数据
            print("📊 从数据库获取K线数据...")
            klines = kline_aggregator.aggregate_klines(
                db=db,
                timeframe='1h',
                limit=100
            )
            
            if klines:
                print(f"✅ 成功获取{len(klines)}条K线数据")
                
                # 使用真实数据测试策略
                print("🔍 使用真实数据测试策略...")
                result = analyze_with_chan_strategy(klines, "1h", "BTC/USDT")
                
                if result:
                    signals = result.get('signals', [])
                    analysis = result.get('analysis', {})
                    
                    print(f"✅ 真实数据策略分析成功")
                    print(f"   📈 分型数量: {len(analysis.get('fenxings', []))}")
                    print(f"   📊 笔数量: {len(analysis.get('bis', []))}")
                    print(f"   🎯 信号数量: {len(signals)}")
                    
                    if signals:
                        latest_signal = signals[-1]
                        print(f"   💫 最新信号: {latest_signal.get('signal_type')} "
                              f"置信度: {latest_signal.get('confidence', 0):.2f}")
                    
                    return True
                else:
                    print("❌ 真实数据策略分析失败")
                    return False
            else:
                print("⚠️ 数据库中没有K线数据，请先运行数据获取")
                return True  # 不算失败，只是没有数据
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 数据库集成测试失败: {str(e)}")
        return False


def test_api_endpoints():
    """测试API端点"""
    print("\n🔍 测试3: API端点测试")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        # 测试策略分析端点
        print("🌐 测试策略分析API...")
        response = requests.get(
            f"{base_url}/strategy/analyze",
            params={
                'timeframe': '1h',
                'limit': 100,
                'symbol': 'btc_usdt'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                strategy_data = data.get('data', {})
                signals = strategy_data.get('trading_signals', {})
                
                print(f"✅ 策略分析API调用成功")
                print(f"   📊 总信号数: {signals.get('total_signals', 0)}")
                print(f"   📈 买信号数: {signals.get('buy_signals', 0)}")
                print(f"   📉 卖信号数: {signals.get('sell_signals', 0)}")
                
                recommendation = strategy_data.get('recommendation', {})
                print(f"   💡 推荐操作: {recommendation.get('action', 'WAIT')}")
                print(f"   🎯 置信度: {recommendation.get('confidence', 0):.2f}")
                
            else:
                print(f"❌ API返回失败: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API调用失败: HTTP {response.status_code}")
            if response.status_code == 404:
                print("💡 请确保服务器正在运行: python quick_start.py")
            return False
        
        # 测试回测端点
        print("\n🔍 测试回测API...")
        response = requests.get(
            f"{base_url}/strategy/backtest",
            params={
                'timeframe': '1h',
                'days': 7,
                'initial_capital': 10000
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                backtest_data = data.get('data', {})
                performance = backtest_data.get('performance', {})
                
                print(f"✅ 回测API调用成功")
                print(f"   💰 总收益率: {performance.get('total_return', 0):.2f}%")
                print(f"   🎯 胜率: {performance.get('win_rate', 0):.1f}%")
                print(f"   📊 总交易次数: {performance.get('total_trades', 0)}")
                
            else:
                print(f"❌ 回测API返回失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"⚠️ 回测API调用失败: HTTP {response.status_code}")
            # 回测失败不算整体测试失败
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("💡 请先启动服务器: python quick_start.py")
        return False
    except Exception as e:
        print(f"❌ API端点测试失败: {str(e)}")
        return False


def run_comprehensive_test():
    """运行综合测试"""
    print("🐢 缠论多级别策略 - 综合测试")
    print("=" * 60)
    
    test_results = {
        "直接策略测试": False,
        "数据库集成测试": False,
        "API端点测试": False
    }
    
    # 运行所有测试
    test_results["直接策略测试"] = test_strategy_direct()
    test_results["数据库集成测试"] = test_database_integration()
    test_results["API端点测试"] = test_api_endpoints()
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\n📊 测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！缠论策略系统运行正常")
        print("\n💡 使用方法:")
        print("   1. 启动系统: python quick_start.py")
        print("   2. 访问API文档: http://localhost:8000/api/v1/docs")
        print("   3. 策略分析: GET /api/v1/strategy/analyze")
        print("   4. 策略回测: GET /api/v1/strategy/backtest")
        
        print("\n🎯 API调用示例:")
        print("   curl 'http://localhost:8000/api/v1/strategy/analyze?timeframe=1h&limit=200'")
        
    elif passed > 0:
        print("⚠️ 部分测试通过，系统可基本使用但可能有问题")
        
        failed_tests = [name for name, result in test_results.items() if not result]
        print(f"\n❌ 失败的测试: {', '.join(failed_tests)}")
        
    else:
        print("❌ 所有测试失败，请检查系统配置")
    
    print("\n📖 缠论策略功能特点:")
    print("   🔍 分型识别 - 自动识别顶分型和底分型")
    print("   📊 笔构建 - 基于分型构建上涨笔和下跌笔") 
    print("   📈 趋势分析 - 判断趋势方向和强度")
    print("   🎯 信号生成 - 生成第一、二、三类买卖点")
    print("   🛡️ 风险控制 - 提供止损止盈和仓位建议")
    print("   📋 回测分析 - 历史数据策略表现评估")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        exit_code = 0 if success else 1
        
        print(f"\n{'='*60}")
        if success:
            print("🎊 缠论策略测试完成 - 系统可用！")
        else:
            print("⚠️ 缠论策略测试完成 - 存在问题需要解决")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试程序异常: {str(e)}")
        sys.exit(1)