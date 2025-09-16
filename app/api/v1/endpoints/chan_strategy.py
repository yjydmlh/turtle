"""
缠论策略分析API端点

提供基于缠论的多级别联立分析交易策略接口
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.api.deps import get_db
from app.services.kline_aggregator import kline_aggregator
from app.services.chan_strategy import analyze_with_chan_strategy
from app.core.exceptions import create_success_response
from app.core.logger import app_logger

router = APIRouter()


@router.get("/analyze")
def chan_strategy_analysis(
    timeframe: str = Query("1h", description="时间周期 (1m,5m,15m,30m,1h,4h,1d)"),
    limit: int = Query(200, ge=50, le=500, description="分析的K线数量"),
    symbol: str = Query("btc_usdt", description="交易品种"),
    db: Session = Depends(get_db)
):
    """
    缠论策略分析 - 多级别联立分析生成交易信号
    
    特点：
    - 🔍 基于缠中说禅理论的专业技术分析
    - 📊 自动识别分型、笔、线段结构
    - 🎯 生成第一、二、三类买卖点信号
    - 📈 多级别趋势联立验证
    - 🛡️ 完整的风险控制建议
    - 💡 智能仓位管理
    
    分析内容：
    - 分型识别（顶分型🔺、底分型🔻）
    - 笔的构建和方向判断
    - 趋势强度和方向分析
    - 支撑阻力位识别
    - 交易信号生成和评级
    
    Args:
        timeframe: 分析时间周期
        limit: K线数据量，建议200以上获得更准确分析
        symbol: 交易品种代码
    """
    try:
        app_logger.info(f"🎯 缠论策略分析 - {symbol} {timeframe} 数据量: {limit}")
        
        # 获取K线数据
        klines = kline_aggregator.aggregate_klines(
            db=db,
            timeframe=timeframe,
            limit=limit
        )
        
        if not klines:
            raise HTTPException(
                status_code=404, 
                detail="没有找到K线数据，请先调用 /api/v1/simple/fetch-data 获取数据"
            )
        
        # 执行缠论策略分析
        strategy_result = analyze_with_chan_strategy(
            klines=klines,
            timeframe=timeframe,
            symbol=symbol.upper().replace("_", "/")  # 转换为标准格式
        )
        
        # 统计分析结果
        signals = strategy_result.get('signals', [])
        analysis = strategy_result.get('analysis', {})
        recommendation = strategy_result.get('recommendation', {})
        
        # 计算统计信息
        fenxings_count = len(analysis.get('fenxings', []))
        bis_count = len(analysis.get('bis', []))
        buy_signals = [s for s in signals if '买' in s.get('signal_type', '')]
        sell_signals = [s for s in signals if '卖' in s.get('signal_type', '')]
        
        app_logger.info(
            f"✅ 缠论策略分析完成 - 分型: {fenxings_count}, 笔: {bis_count}, "
            f"买信号: {len(buy_signals)}, 卖信号: {len(sell_signals)}"
        )
        
        return create_success_response(data={
            "strategy_analysis": strategy_result,
            "trading_signals": {
                "total_signals": len(signals),
                "buy_signals": len(buy_signals),
                "sell_signals": len(sell_signals),
                "signals": signals
            },
            "market_analysis": {
                "fenxings_identified": fenxings_count,
                "bis_constructed": bis_count,
                "trend_analysis": analysis.get('trend_analysis', {}),
                "support_resistance": analysis.get('support_resistance', {}),
                "market_structure": analysis.get('market_structure', {})
            },
            "recommendation": recommendation,
            "metadata": {
                "symbol": symbol,
                "timeframe": timeframe,
                "klines_analyzed": len(klines),
                "latest_price": klines[-1]["close_price"] if klines else None,
                "analysis_timestamp": strategy_result.get('metadata', {}).get('analysis_time'),
                "strategy_info": strategy_result.get('strategy_info', {}),
                "performance_metrics": {
                    "analysis_coverage": min(100, (fenxings_count / max(limit // 10, 1)) * 100),
                    "signal_quality": recommendation.get('confidence', 0) * 100,
                    "data_completeness": (len(klines) / limit) * 100
                }
            },
            "usage_guide": {
                "signal_interpretation": {
                    "第一类买卖点": "趋势转折点，风险相对较高，但收益潜力大",
                    "第二类买卖点": "趋势确认点，风险适中，胜率较高",
                    "第三类买卖点": "趋势延续点，风险较低，适合跟趋势"
                },
                "risk_management": {
                    "position_size": "建议仓位已根据信号强度计算",
                    "stop_loss": "严格执行止损，控制单次损失",
                    "take_profit": "合理设置止盈，保护利润"
                },
                "strategy_tips": [
                    "多级别分析：结合更高级别确认趋势方向",
                    "等待确认：分型形成后等待笔的确认",
                    "资金管理：单次风险不超过总资金的2%",
                    "心理控制：严格按信号执行，避免情绪化交易"
                ]
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ 缠论策略分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="策略分析服务暂时不可用")


@router.get("/signals/history")
def get_strategy_signals_history(
    timeframe: str = Query("1h", description="时间周期"),
    days: int = Query(7, ge=1, le=30, description="历史天数"),
    signal_type: Optional[str] = Query(None, description="信号类型过滤"),
    db: Session = Depends(get_db)
):
    """
    获取缠论策略历史信号
    
    用于回测分析和策略优化
    """
    try:
        app_logger.info(f"📊 获取{days}天内的策略信号历史")
        
        # 计算需要的K线数量（基于天数和时间周期）
        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }
        
        minutes_per_period = timeframe_minutes.get(timeframe, 60)
        total_periods = (days * 24 * 60) // minutes_per_period
        limit = min(total_periods, 500)  # 限制最大数量
        
        # 获取历史K线数据
        klines = kline_aggregator.aggregate_klines(
            db=db,
            timeframe=timeframe,
            limit=limit
        )
        
        if not klines:
            return create_success_response(data={
                "signals": [],
                "statistics": {
                    "total_signals": 0,
                    "buy_signals": 0,
                    "sell_signals": 0
                },
                "message": "没有找到历史数据"
            })
        
        # 分批分析历史数据以生成信号序列
        all_signals = []
        batch_size = 100
        analysis_window = 50  # 每次分析的窗口大小
        
        for i in range(analysis_window, len(klines), batch_size):
            batch_klines = klines[max(0, i-analysis_window):i+1]
            
            if len(batch_klines) >= analysis_window:
                result = analyze_with_chan_strategy(batch_klines, timeframe)
                batch_signals = result.get('signals', [])
                
                # 只保留最新的信号（避免重复）
                if batch_signals:
                    latest_signal = batch_signals[-1]
                    latest_signal['batch_index'] = i
                    all_signals.append(latest_signal)
        
        # 过滤信号类型
        if signal_type:
            all_signals = [s for s in all_signals if signal_type.lower() in s.get('signal_type', '').lower()]
        
        # 计算统计信息
        buy_signals = [s for s in all_signals if '买' in s.get('signal_type', '')]
        sell_signals = [s for s in all_signals if '卖' in s.get('signal_type', '')]
        
        # 计算信号胜率（简化版本）
        signal_performance = _calculate_signal_performance(all_signals, klines)
        
        return create_success_response(data={
            "signals": all_signals[-50:],  # 返回最近50个信号
            "statistics": {
                "total_signals": len(all_signals),
                "buy_signals": len(buy_signals),
                "sell_signals": len(sell_signals),
                "average_confidence": sum(s.get('confidence', 0) for s in all_signals) / max(len(all_signals), 1),
                "signal_frequency": len(all_signals) / max(days, 1)  # 每天平均信号数
            },
            "performance": signal_performance,
            "metadata": {
                "timeframe": timeframe,
                "days_analyzed": days,
                "klines_processed": len(klines),
                "analysis_batches": len(all_signals)
            }
        })
        
    except Exception as e:
        app_logger.error(f"❌ 获取策略信号历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取历史信号失败")


@router.get("/backtest")
def chan_strategy_backtest(
    timeframe: str = Query("1h", description="时间周期"),
    days: int = Query(30, ge=7, le=90, description="回测天数"),
    initial_capital: float = Query(10000, ge=1000, description="初始资金"),
    db: Session = Depends(get_db)
):
    """
    缠论策略回测分析
    
    模拟历史交易表现，评估策略效果
    """
    try:
        app_logger.info(f"🔍 开始{days}天缠论策略回测")
        
        # 计算回测所需的K线数量
        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }
        
        minutes_per_period = timeframe_minutes.get(timeframe, 60)
        total_periods = (days * 24 * 60) // minutes_per_period
        limit = min(total_periods, 1000)
        
        # 获取历史数据
        klines = kline_aggregator.aggregate_klines(
            db=db,
            timeframe=timeframe,
            limit=limit
        )
        
        if len(klines) < 100:
            raise HTTPException(status_code=400, detail="历史数据不足，无法进行有效回测")
        
        # 执行回测
        backtest_result = _run_strategy_backtest(klines, timeframe, initial_capital)
        
        app_logger.info(
            f"✅ 回测完成 - 总收益率: {backtest_result['performance']['total_return']:.2f}%, "
            f"胜率: {backtest_result['performance']['win_rate']:.1f}%"
        )
        
        return create_success_response(data=backtest_result)
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ 策略回测失败: {str(e)}")
        raise HTTPException(status_code=500, detail="回测服务暂时不可用")


def _calculate_signal_performance(signals: list, klines: list) -> Dict[str, Any]:
    """计算信号表现（简化版本）"""
    try:
        if not signals or not klines:
            return {"win_rate": 0, "average_return": 0, "total_signals": 0}
        
        # 简化的信号表现计算
        # 实际应用中需要更复杂的逻辑来跟踪信号到平仓的完整过程
        
        wins = 0
        total_return = 0
        
        for signal in signals:
            # 模拟简单的信号跟踪
            signal_price = signal.get('price', 0)
            is_buy = '买' in signal.get('signal_type', '')
            
            # 寻找信号后的价格变化（简化处理）
            future_prices = [float(k['close_price']) for k in klines[-10:]]
            if future_prices and signal_price > 0:
                avg_future_price = sum(future_prices) / len(future_prices)
                
                if is_buy:
                    return_rate = (avg_future_price - signal_price) / signal_price
                else:
                    return_rate = (signal_price - avg_future_price) / signal_price
                
                if return_rate > 0:
                    wins += 1
                total_return += return_rate
        
        return {
            "win_rate": (wins / len(signals)) * 100 if signals else 0,
            "average_return": (total_return / len(signals)) * 100 if signals else 0,
            "total_signals": len(signals),
            "profitable_signals": wins
        }
        
    except Exception:
        return {"win_rate": 0, "average_return": 0, "total_signals": 0}


def _run_strategy_backtest(klines: list, timeframe: str, initial_capital: float) -> Dict[str, Any]:
    """运行策略回测"""
    try:
        # 简化的回测逻辑
        # 实际应用中需要更完整的回测框架
        
        capital = initial_capital
        positions = []
        trades = []
        analysis_window = 100
        
        for i in range(analysis_window, len(klines), 10):  # 每10个周期分析一次
            window_klines = klines[i-analysis_window:i]
            
            if len(window_klines) >= analysis_window:
                result = analyze_with_chan_strategy(window_klines, timeframe)
                signals = result.get('signals', [])
                
                if signals:
                    signal = signals[-1]  # 最新信号
                    current_price = float(klines[i-1]['close_price'])
                    
                    # 简化的交易逻辑
                    if '买' in signal.get('signal_type', '') and not positions:
                        # 开多仓
                        position_size = capital * signal.get('position_size', 0.1)
                        shares = position_size / current_price
                        positions.append({
                            'type': 'long',
                            'entry_price': current_price,
                            'shares': shares,
                            'entry_time': i,
                            'signal': signal
                        })
                        capital -= position_size
                        
                    elif '卖' in signal.get('signal_type', '') and positions:
                        # 平仓
                        for pos in positions[:]:
                            exit_value = pos['shares'] * current_price
                            profit = exit_value - (pos['shares'] * pos['entry_price'])
                            capital += exit_value
                            
                            trades.append({
                                'entry_price': pos['entry_price'],
                                'exit_price': current_price,
                                'profit': profit,
                                'return_rate': profit / (pos['shares'] * pos['entry_price'])
                            })
                            positions.remove(pos)
        
        # 平掉剩余仓位
        if positions:
            final_price = float(klines[-1]['close_price'])
            for pos in positions:
                exit_value = pos['shares'] * final_price
                profit = exit_value - (pos['shares'] * pos['entry_price'])
                capital += exit_value
                
                trades.append({
                    'entry_price': pos['entry_price'],
                    'exit_price': final_price,
                    'profit': profit,
                    'return_rate': profit / (pos['shares'] * pos['entry_price'])
                })
        
        # 计算回测指标
        total_return = ((capital - initial_capital) / initial_capital) * 100
        win_trades = [t for t in trades if t['profit'] > 0]
        win_rate = (len(win_trades) / len(trades)) * 100 if trades else 0
        
        avg_win = sum(t['profit'] for t in win_trades) / len(win_trades) if win_trades else 0
        loss_trades = [t for t in trades if t['profit'] <= 0]
        avg_loss = sum(t['profit'] for t in loss_trades) / len(loss_trades) if loss_trades else 0
        
        return {
            "performance": {
                "initial_capital": initial_capital,
                "final_capital": capital,
                "total_return": total_return,
                "total_trades": len(trades),
                "win_rate": win_rate,
                "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
                "average_win": avg_win,
                "average_loss": avg_loss
            },
            "trades": trades[-20:],  # 最近20笔交易
            "summary": {
                "profitable_trades": len(win_trades),
                "losing_trades": len(loss_trades),
                "largest_win": max((t['profit'] for t in trades), default=0),
                "largest_loss": min((t['profit'] for t in trades), default=0),
                "average_return_per_trade": sum(t['return_rate'] for t in trades) / len(trades) if trades else 0
            },
            "metadata": {
                "backtest_period": f"{len(klines)} {timeframe} periods",
                "strategy": "缠论多级别联立分析",
                "timeframe": timeframe
            }
        }
        
    except Exception as e:
        app_logger.error(f"❌ 回测执行失败: {str(e)}")
        return {
            "performance": {"total_return": 0, "win_rate": 0},
            "trades": [],
            "summary": {},
            "error": str(e)
        }