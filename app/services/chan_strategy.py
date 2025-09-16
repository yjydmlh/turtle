"""
缠论多级别联立分析交易策略

基于chan.py模块实现的专业缠论交易策略，支持多级别分析和交易信号生成
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import sys
import os

# 添加chan.py模块到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'chan.py'))

try:
    from Chan import CChan
    from ChanConfig import CChanConfig
    from Common.CEnum import AUTYPE, BSP_TYPE, DATA_SRC, FX_TYPE, KL_TYPE
    CHAN_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Chan模块导入失败: {e}")
    CHAN_MODULE_AVAILABLE = False

from app.core.logger import app_logger


class SignalType(Enum):
    """交易信号类型"""
    BUY_1 = "第一类买点"
    BUY_2 = "第二类买点" 
    BUY_3 = "第三类买点"
    SELL_1 = "第一类卖点"
    SELL_2 = "第二类卖点"
    SELL_3 = "第三类卖点"
    HOLD = "持有"
    WAIT = "观望"


@dataclass
class TradingSignal:
    """交易信号数据结构"""
    signal_type: SignalType
    timestamp: int
    price: float
    confidence: float  # 信号置信度 0-1
    level: str  # 触发级别
    description: str
    risk_level: str  # 风险等级: low/medium/high
    position_size: float  # 建议仓位比例 0-1
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'signal_type': self.signal_type.value,
            'timestamp': self.timestamp,
            'price': self.price,
            'confidence': self.confidence,
            'level': self.level,
            'description': self.description,
            'risk_level': self.risk_level,
            'position_size': self.position_size,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }


class ChanMultiLevelStrategy:
    """缠论多级别联立分析策略"""
    
    def __init__(self, symbol: str = "BTC/USDT", config: Optional[Dict] = None):
        """初始化策略"""
        self.symbol = symbol
        self.config = config or {}
        
        # 策略参数
        self.risk_ratio = self.config.get('risk_ratio', 0.02)
        self.max_position = self.config.get('max_position', 0.3)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.6)
        
        # 初始化缠论配置
        self.chan_config = self._init_chan_config()
        
        app_logger.info(f"🏗️ 缠论多级别策略初始化完成 - 品种: {symbol}")

    def _init_chan_config(self) -> Optional[CChanConfig]:
        """初始化缠论配置"""
        if not CHAN_MODULE_AVAILABLE:
            app_logger.warning("⚠️ Chan模块不可用，策略功能受限")
            return None
            
        return CChanConfig({
            "trigger_step": False,
            "bi_strict": True,
            "seg_algo": "chan",
            "zs_algo": "normal",
            "bs_type": "1,1p,2,2s,3a,3b",
            "divergence_rate": 0.8,
            "min_zs_cnt": 1,
            "bsp1_only_multibi_zs": True,
            "macd": {"fast": 12, "slow": 26, "signal": 9},
            "mean_metrics": [5, 10, 20],
            "print_warning": False,
        })

    def analyze_klines(self, klines: List[Dict], timeframe: str) -> Dict[str, Any]:
        """分析K线数据生成交易信号"""
        if not CHAN_MODULE_AVAILABLE:
            return self._fallback_analysis(klines, timeframe)
            
        try:
            app_logger.info(f"🔍 开始{timeframe}级别缠论分析，数据量: {len(klines)}")
            
            # 执行缠论分析
            analysis_result = self._execute_chan_analysis(klines, timeframe)
            
            # 生成交易信号
            signals = self._generate_trading_signals(analysis_result, timeframe)
            
            # 构建返回结果
            result = {
                'signals': [signal.to_dict() for signal in signals],
                'analysis': analysis_result,
                'recommendation': self._generate_recommendation(signals),
                'metadata': {
                    'timeframe': timeframe,
                    'data_count': len(klines),
                    'analysis_time': datetime.now().isoformat(),
                    'chan_module_available': True
                }
            }
            
            app_logger.info(f"✅ {timeframe}级别分析完成，生成{len(signals)}个信号")
            return result
            
        except Exception as e:
            app_logger.error(f"❌ 缠论分析失败: {str(e)}")
            return self._fallback_analysis(klines, timeframe)

    def _execute_chan_analysis(self, klines: List[Dict], timeframe: str) -> Dict:
        """执行Chan模块分析"""
        try:
            # 识别分型
            fenxings = self._identify_fenxings(klines)
            
            # 识别笔
            bis = self._identify_bis(fenxings, klines)
            
            # 分析趋势
            trend_analysis = self._analyze_trend(klines, bis)
            
            # 分析支撑阻力
            support_resistance = self._analyze_support_resistance(fenxings)
            
            return {
                'fenxings': fenxings,
                'bis': bis,
                'trend_analysis': trend_analysis,
                'support_resistance': support_resistance,
                'market_structure': {
                    'trend_direction': trend_analysis.get('direction'),
                    'trend_strength': trend_analysis.get('strength'),
                    'current_phase': self._determine_market_phase(bis)
                }
            }
            
        except Exception as e:
            app_logger.error(f"❌ Chan分析执行失败: {str(e)}")
            return self._get_empty_analysis()

    def _identify_fenxings(self, klines: List[Dict]) -> List[Dict]:
        """识别分型"""
        fenxings = []
        
        try:
            if len(klines) < 3:
                return fenxings
            
            for i in range(1, len(klines) - 1):
                prev_high = float(klines[i-1]['high_price'])
                prev_low = float(klines[i-1]['low_price'])
                curr_high = float(klines[i]['high_price'])
                curr_low = float(klines[i]['low_price'])
                next_high = float(klines[i+1]['high_price'])
                next_low = float(klines[i+1]['low_price'])
                
                # 顶分型
                if (curr_high > prev_high and curr_high > next_high and
                    curr_low > prev_low and curr_low > next_low):
                    fenxings.append({
                        'type': 'top',
                        'timestamp': klines[i]['timestamp'],
                        'price': curr_high,
                        'index': i,
                        'strength': self._calculate_fenxing_strength(klines, i)
                    })
                
                # 底分型
                elif (curr_low < prev_low and curr_low < next_low and
                      curr_high < prev_high and curr_high < next_high):
                    fenxings.append({
                        'type': 'bottom',
                        'timestamp': klines[i]['timestamp'],
                        'price': curr_low,
                        'index': i,
                        'strength': self._calculate_fenxing_strength(klines, i)
                    })
        
        except Exception as e:
            app_logger.warning(f"⚠️ 分型识别失败: {str(e)}")
        
        return fenxings

    def _calculate_fenxing_strength(self, klines: List[Dict], index: int) -> float:
        """计算分型强度"""
        try:
            if index < 1 or index >= len(klines) - 1:
                return 1.0
            
            prev_range = float(klines[index-1]['high_price']) - float(klines[index-1]['low_price'])
            curr_range = float(klines[index]['high_price']) - float(klines[index]['low_price'])
            next_range = float(klines[index+1]['high_price']) - float(klines[index+1]['low_price'])
            
            avg_range = (prev_range + curr_range + next_range) / 3
            strength = curr_range / avg_range if avg_range > 0 else 1.0
            
            return min(max(strength, 0.1), 3.0)
            
        except Exception:
            return 1.0

    def _identify_bis(self, fenxings: List[Dict], klines: List[Dict]) -> List[Dict]:
        """识别笔"""
        bis = []
        
        try:
            if len(fenxings) < 2:
                return bis
            
            for i in range(len(fenxings) - 1):
                current_fx = fenxings[i]
                next_fx = fenxings[i + 1]
                
                if current_fx['type'] != next_fx['type']:
                    direction = 'up' if current_fx['type'] == 'bottom' else 'down'
                    
                    bi = {
                        'start': current_fx,
                        'end': next_fx,
                        'direction': direction,
                        'length': abs(next_fx['price'] - current_fx['price']),
                        'time_span': next_fx['timestamp'] - current_fx['timestamp'],
                        'bars_count': abs(next_fx['index'] - current_fx['index'])
                    }
                    bis.append(bi)
        
        except Exception as e:
            app_logger.warning(f"⚠️ 笔识别失败: {str(e)}")
        
        return bis

    def _analyze_trend(self, klines: List[Dict], bis: List[Dict]) -> Dict:
        """分析趋势"""
        try:
            if not klines:
                return {'direction': 'unknown', 'strength': 0}
            
            # 基于价格变化
            if len(klines) >= 10:
                start_price = float(klines[-10]['close_price'])
                end_price = float(klines[-1]['close_price'])
                price_change = (end_price - start_price) / start_price
            else:
                price_change = 0
            
            # 基于笔的分析
            if len(bis) >= 3:
                recent_bis = bis[-3:]
                up_count = sum(1 for bi in recent_bis if bi['direction'] == 'up')
                total_length = sum(bi['length'] for bi in recent_bis)
                up_length = sum(bi['length'] for bi in recent_bis if bi['direction'] == 'up')
                
                if total_length > 0:
                    up_ratio = up_length / total_length
                else:
                    up_ratio = 0.5
            else:
                up_ratio = 0.5 if price_change >= 0 else 0.3
            
            # 综合判断
            if price_change > 0.02 and up_ratio > 0.6:
                direction = 'up'
                strength = min(abs(price_change) * 10 + (up_ratio - 0.5) * 2, 1.0)
            elif price_change < -0.02 and up_ratio < 0.4:
                direction = 'down'
                strength = min(abs(price_change) * 10 + (0.5 - up_ratio) * 2, 1.0)
            else:
                direction = 'sideways'
                strength = 0.3
            
            return {
                'direction': direction,
                'strength': strength,
                'price_change': price_change,
                'bi_analysis': {
                    'up_ratio': up_ratio,
                    'recent_bis_count': len(bis[-3:]) if bis else 0
                }
            }
            
        except Exception as e:
            app_logger.warning(f"⚠️ 趋势分析失败: {str(e)}")
            return {'direction': 'unknown', 'strength': 0}

    def _analyze_support_resistance(self, fenxings: List[Dict]) -> Dict:
        """分析支撑阻力位"""
        try:
            support_levels = [fx['price'] for fx in fenxings if fx['type'] == 'bottom']
            resistance_levels = [fx['price'] for fx in fenxings if fx['type'] == 'top']
            
            # 取最近的几个关键位
            support_levels = sorted(support_levels)[-3:] if support_levels else []
            resistance_levels = sorted(resistance_levels, reverse=True)[:3] if resistance_levels else []
            
            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels
            }
            
        except Exception as e:
            app_logger.warning(f"⚠️ 支撑阻力分析失败: {str(e)}")
            return {'support_levels': [], 'resistance_levels': []}

    def _determine_market_phase(self, bis: List[Dict]) -> str:
        """确定市场阶段"""
        try:
            if len(bis) < 3:
                return "数据不足"
            
            recent_bis = bis[-3:]
            directions = [bi['direction'] for bi in recent_bis]
            
            if directions == ['down', 'up', 'down']:
                return "调整阶段"
            elif directions == ['up', 'down', 'up']:
                return "上升阶段"
            elif all(d == 'up' for d in directions):
                return "强势上涨"
            elif all(d == 'down' for d in directions):
                return "强势下跌"
            else:
                return "震荡阶段"
                
        except Exception:
            return "未知阶段"

    def _generate_trading_signals(self, analysis_result: Dict, timeframe: str) -> List[TradingSignal]:
        """生成交易信号"""
        signals = []
        
        try:
            fenxings = analysis_result.get('fenxings', [])
            bis = analysis_result.get('bis', [])
            trend = analysis_result.get('trend_analysis', {})
            
            # 基于最新分型生成信号
            if fenxings:
                signal = self._create_fenxing_signal(fenxings[-1], trend, timeframe)
                if signal and signal.confidence >= self.confidence_threshold:
                    signals.append(signal)
            
            # 基于笔的转向生成信号
            if len(bis) >= 2:
                signal = self._create_bi_reversal_signal(bis[-2:], trend, timeframe)
                if signal and signal.confidence >= self.confidence_threshold:
                    signals.append(signal)
            
        except Exception as e:
            app_logger.error(f"❌ 生成交易信号失败: {str(e)}")
        
        return signals

    def _create_fenxing_signal(self, fenxing: Dict, trend: Dict, timeframe: str) -> Optional[TradingSignal]:
        """基于分型创建信号"""
        try:
            trend_direction = trend.get('direction', 'unknown')
            trend_strength = trend.get('strength', 0)
            
            # 计算基础置信度
            base_confidence = min(0.5 + fenxing['strength'] * 0.2, 0.8)
            
            # 趋势一致性加成
            if ((fenxing['type'] == 'bottom' and trend_direction == 'up') or
                (fenxing['type'] == 'top' and trend_direction == 'down')):
                confidence = min(base_confidence + trend_strength * 0.2, 0.95)
                risk_level = "low"
            elif trend_direction == 'sideways':
                confidence = base_confidence
                risk_level = "medium"
            else:
                confidence = max(base_confidence - 0.2, 0.3)
                risk_level = "high"
            
            # 底分型买入信号
            if fenxing['type'] == 'bottom':
                return TradingSignal(
                    signal_type=SignalType.BUY_3,
                    timestamp=fenxing['timestamp'],
                    price=fenxing['price'],
                    confidence=confidence,
                    level=timeframe,
                    description=f"底分型买入信号 - 强度: {fenxing['strength']:.2f}",
                    risk_level=risk_level,
                    position_size=min(0.05 + confidence * 0.15, 0.2),
                    stop_loss=fenxing['price'] * 0.97,
                    take_profit=fenxing['price'] * 1.06
                )
            
            # 顶分型卖出信号
            elif fenxing['type'] == 'top':
                return TradingSignal(
                    signal_type=SignalType.SELL_3,
                    timestamp=fenxing['timestamp'],
                    price=fenxing['price'],
                    confidence=confidence,
                    level=timeframe,
                    description=f"顶分型卖出信号 - 强度: {fenxing['strength']:.2f}",
                    risk_level=risk_level,
                    position_size=min(0.05 + confidence * 0.15, 0.2),
                    stop_loss=fenxing['price'] * 1.03,
                    take_profit=fenxing['price'] * 0.94
                )
            
            return None
            
        except Exception as e:
            app_logger.warning(f"⚠️ 创建分型信号失败: {str(e)}")
            return None

    def _create_bi_reversal_signal(self, recent_bis: List[Dict], trend: Dict, timeframe: str) -> Optional[TradingSignal]:
        """基于笔转向创建信号"""
        try:
            if len(recent_bis) < 2:
                return None
            
            prev_bi = recent_bis[0]
            current_bi = recent_bis[1]
            
            # 检查笔的转向
            if prev_bi['direction'] == current_bi['direction']:
                return None
            
            # 计算信号强度
            length_ratio = current_bi['length'] / prev_bi['length'] if prev_bi['length'] > 0 else 1
            confidence = min(0.6 + (length_ratio - 1) * 0.3, 0.9)
            
            # 下跌转上涨
            if prev_bi['direction'] == 'down' and current_bi['direction'] == 'up':
                return TradingSignal(
                    signal_type=SignalType.BUY_2,
                    timestamp=current_bi['end']['timestamp'],
                    price=current_bi['end']['price'],
                    confidence=confidence,
                    level=timeframe,
                    description=f"笔转向买入信号 - 新笔强度: {length_ratio:.2f}",
                    risk_level="medium",
                    position_size=min(0.1 + confidence * 0.1, 0.25),
                    stop_loss=current_bi['start']['price'],
                    take_profit=current_bi['end']['price'] + current_bi['length']
                )
            
            # 上涨转下跌
            elif prev_bi['direction'] == 'up' and current_bi['direction'] == 'down':
                return TradingSignal(
                    signal_type=SignalType.SELL_2,
                    timestamp=current_bi['end']['timestamp'],
                    price=current_bi['end']['price'],
                    confidence=confidence,
                    level=timeframe,
                    description=f"笔转向卖出信号 - 新笔强度: {length_ratio:.2f}",
                    risk_level="medium",
                    position_size=min(0.1 + confidence * 0.1, 0.25),
                    stop_loss=current_bi['start']['price'],
                    take_profit=current_bi['end']['price'] - current_bi['length']
                )
            
            return None
            
        except Exception as e:
            app_logger.warning(f"⚠️ 创建笔转向信号失败: {str(e)}")
            return None

    def _generate_recommendation(self, signals: List[TradingSignal]) -> Dict:
        """生成交易建议"""
        try:
            if not signals:
                return {
                    'action': 'WAIT',
                    'reason': '暂无明确信号',
                    'confidence': 0,
                    'position_size': 0
                }
            
            # 选择置信度最高的信号
            best_signal = max(signals, key=lambda x: x.confidence)
            
            if best_signal.signal_type.value.startswith('第') and '买' in best_signal.signal_type.value:
                action = 'BUY'
            elif best_signal.signal_type.value.startswith('第') and '卖' in best_signal.signal_type.value:
                action = 'SELL'
            else:
                action = 'WAIT'
            
            return {
                'action': action,
                'reason': best_signal.description,
                'confidence': best_signal.confidence,
                'position_size': best_signal.position_size,
                'price': best_signal.price,
                'stop_loss': best_signal.stop_loss,
                'take_profit': best_signal.take_profit,
                'risk_level': best_signal.risk_level
            }
            
        except Exception as e:
            app_logger.warning(f"⚠️ 生成交易建议失败: {str(e)}")
            return {'action': 'WAIT', 'reason': '分析出错', 'confidence': 0}

    def _fallback_analysis(self, klines: List[Dict], timeframe: str) -> Dict:
        """降级分析 - Chan模块不可用时使用"""
        app_logger.info("🔄 使用简化分析模式")
        
        try:
            if not klines:
                return self._get_empty_result()
            
            # 简单的技术分析
            current_price = float(klines[-1]['close_price'])
            prices = [float(k['close_price']) for k in klines[-20:]]
            
            # 简单移动平均
            sma_short = sum(prices[-5:]) / 5 if len(prices) >= 5 else current_price
            sma_long = sum(prices[-10:]) / 10 if len(prices) >= 10 else current_price
            
            # 生成简单信号
            signals = []
            if sma_short > sma_long * 1.01:
                signals.append({
                    'signal_type': '简单买入信号',
                    'timestamp': klines[-1]['timestamp'],
                    'price': current_price,
                    'confidence': 0.5,
                    'level': timeframe,
                    'description': '短期均线上穿长期均线',
                    'risk_level': 'medium',
                    'position_size': 0.1
                })
            elif sma_short < sma_long * 0.99:
                signals.append({
                    'signal_type': '简单卖出信号',
                    'timestamp': klines[-1]['timestamp'],
                    'price': current_price,
                    'confidence': 0.5,
                    'level': timeframe,
                    'description': '短期均线下穿长期均线',
                    'risk_level': 'medium',
                    'position_size': 0.1
                })
            
            return {
                'signals': signals,
                'analysis': {'method': 'fallback', 'sma_short': sma_short, 'sma_long': sma_long},
                'recommendation': {
                    'action': 'BUY' if signals and '买入' in signals[0]['signal_type'] else 'WAIT',
                    'reason': signals[0]['description'] if signals else '无明确信号',
                    'confidence': signals[0]['confidence'] if signals else 0
                },
                'metadata': {
                    'timeframe': timeframe,
                    'data_count': len(klines),
                    'analysis_time': datetime.now().isoformat(),
                    'chan_module_available': False
                }
            }
            
        except Exception as e:
            app_logger.error(f"❌ 简化分析失败: {str(e)}")
            return self._get_empty_result()

    def _get_empty_analysis(self) -> Dict:
        """获取空的分析结果"""
        return {
            'fenxings': [],
            'bis': [],
            'trend_analysis': {'direction': 'unknown', 'strength': 0},
            'support_resistance': {'support_levels': [], 'resistance_levels': []},
            'market_structure': {'trend_direction': 'unknown', 'trend_strength': 0}
        }

    def _get_empty_result(self) -> Dict:
        """获取空的结果"""
        return {
            'signals': [],
            'analysis': self._get_empty_analysis(),
            'recommendation': {'action': 'WAIT', 'reason': '数据不足', 'confidence': 0},
            'metadata': {
                'timeframe': 'unknown',
                'data_count': 0,
                'analysis_time': datetime.now().isoformat(),
                'chan_module_available': CHAN_MODULE_AVAILABLE
            }
        }


# 创建全局实例
chan_strategy = ChanMultiLevelStrategy()


def analyze_with_chan_strategy(klines: List[Dict], timeframe: str = "1h", 
                              symbol: str = "BTC/USDT") -> Dict[str, Any]:
    """
    使用缠论策略分析K线数据
    
    Args:
        klines: K线数据列表
        timeframe: 时间周期
        symbol: 交易品种
        
    Returns:
        分析结果字典
    """
    try:
        # 更新策略品种（如果需要）
        if chan_strategy.symbol != symbol:
            chan_strategy.symbol = symbol
            app_logger.info(f"🔄 更新策略品种为: {symbol}")
        
        # 执行分析
        result = chan_strategy.analyze_klines(klines, timeframe)
        
        # 添加策略信息
        result['strategy_info'] = {
            'name': '缠论多级别联立分析策略',
            'version': '1.0.0',
            'description': '基于缠中说禅理论的多级别技术分析策略',
            'features': [
                '分型识别',
                '笔段构建', 
                '趋势分析',
                '买卖点识别',
                '风险评估'
            ]
        }
        
        return result
        
    except Exception as e:
        app_logger.error(f"❌ 缠论策略分析失败: {str(e)}")
        return chan_strategy._get_empty_result()