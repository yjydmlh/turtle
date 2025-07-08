from typing import List, Dict, Optional, Any
import pandas as pd
from datetime import datetime
import sys
import os

# 添加chan.py模块到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'chan.py'))

try:
    # 导入Chan模块 - 请根据你的实际chan.py模块结构调整导入
    # 以下是常见的可能导入方式，请选择适合你项目的方式：

    # 方式1: 如果chan.py有主类
    from chan import ChanModel

    # 方式2: 如果chan.py有核心模块
    # from chan.core import Chan

    # 方式3: 如果chan.py有分析器
    # from chan.analyzer import ChanAnalyzer

    # 方式4: 如果是函数式API
    # from chan import analyze_klines, get_fenxings, get_bis

    CHAN_MODULE_AVAILABLE = True

except ImportError as e:
    print(f"⚠️ 无法导入Chan模块: {e}")
    print("💡 请检查chan.py子模块是否正确初始化")
    print("🔧 运行: git submodule update --init")
    ChanModel = None
    CHAN_MODULE_AVAILABLE = False

from app.core.logger import app_logger


class ChanAdapter:
    """Chan模块适配器 - 将你现有的Chan模块集成到系统中"""

    def __init__(self):
        self.chan_model = None
        self.is_available = False
        self._initialize_chan()

    def _initialize_chan(self):
        """初始化Chan模块"""
        try:
            if CHAN_MODULE_AVAILABLE and ChanModel is not None:
                # 根据你的实际Chan模块API调整初始化参数
                # 以下是常见的初始化方式：

                # 方式1: 无参数初始化
                self.chan_model = ChanModel()

                # 方式2: 带配置初始化
                # config = {
                #     'timeframe': '1h',
                #     'min_fenxing_distance': 3,
                #     'bi_min_length': 5
                # }
                # self.chan_model = ChanModel(config)

                # 方式3: 如果需要特定参数
                # self.chan_model = ChanModel(
                #     symbol='BTC/USDT',
                #     timeframe='1h'
                # )

                self.is_available = True
                app_logger.info("✅ Chan模块初始化成功")
            else:
                app_logger.warning("⚠️ Chan模块不可用，将使用简化分析")
                self.is_available = False
        except Exception as e:
            app_logger.error(f"❌ Chan模块初始化失败: {str(e)}")
            self.is_available = False

    def analyze_klines(self, klines: List[Dict]) -> Dict[str, Any]:
        """
        使用Chan模块分析K线数据

        Args:
            klines: K线数据列表，格式：
            [
                {
                    'timestamp': int,
                    'open_price': str,
                    'high_price': str,
                    'low_price': str,
                    'close_price': str,
                    'volume': str,
                    ...
                }
            ]

        Returns:
            Dict: 包含缠论分析结果的字典
        """
        if not self.is_available:
            return self._fallback_analysis(klines)

        try:
            app_logger.info(f"🔍 开始Chan模块分析，数据量: {len(klines)}")

            # 准备数据格式给Chan模块
            chan_data = self._prepare_data_for_chan(klines)

            # 调用Chan模块进行分析
            analysis_result = self._call_chan_analysis(chan_data)

            # 转换结果为标准格式
            standardized_result = self._standardize_chan_result(analysis_result)

            app_logger.info(f"✅ Chan模块分析完成")
            return standardized_result

        except Exception as e:
            app_logger.error(f"❌ Chan模块分析失败: {str(e)}")
            # 如果Chan模块分析失败，使用简化分析作为后备
            return self._fallback_analysis(klines)

    def _prepare_data_for_chan(self, klines: List[Dict]) -> Any:
        """
        将K线数据转换为Chan模块需要的格式
        请根据你的实际chan.py数据格式要求调整
        """
        try:
            # 方案1: 如果Chan模块接受DataFrame
            df_data = []
            for kline in klines:
                df_data.append({
                    'timestamp': kline['timestamp'],
                    'datetime': datetime.fromtimestamp(kline['timestamp'] / 1000),
                    'open': float(kline['open_price']),
                    'high': float(kline['high_price']),
                    'low': float(kline['low_price']),
                    'close': float(kline['close_price']),
                    'volume': float(kline['volume'])
                })

            df = pd.DataFrame(df_data)
            return df

            # 方案2: 如果Chan模块接受特定格式的列表
            # chan_data = []
            # for kline in klines:
            #     chan_data.append({
            #         'time': kline['timestamp'],
            #         'open': float(kline['open_price']),
            #         'high': float(kline['high_price']),
            #         'low': float(kline['low_price']),
            #         'close': float(kline['close_price']),
            #         'vol': float(kline['volume'])
            #     })
            # return chan_data

            # 方案3: 如果Chan模块需要特定的数据结构
            # return self.chan_model.create_data_structure(klines)

        except Exception as e:
            app_logger.error(f"❌ 数据格式转换失败: {str(e)}")
            raise

    def _call_chan_analysis(self, chan_data: Any) -> Any:
        """
        调用Chan模块的分析方法
        请根据你的实际chan.py API调整方法调用
        """
        try:
            # 常见的可能的API调用方式，请根据实际情况选择和调整：

            # 方案1: 如果有统一的分析方法
            if hasattr(self.chan_model, 'analyze'):
                return self.chan_model.analyze(chan_data)

            # 方案2: 如果需要分步骤调用
            elif hasattr(self.chan_model, 'load_data'):
                self.chan_model.load_data(chan_data)

                result = {}

                # 获取分型
                if hasattr(self.chan_model, 'get_fenxing'):
                    result['fenxings'] = self.chan_model.get_fenxing()
                elif hasattr(self.chan_model, 'fenxings'):
                    result['fenxings'] = self.chan_model.fenxings

                # 获取笔
                if hasattr(self.chan_model, 'get_bi'):
                    result['bis'] = self.chan_model.get_bi()
                elif hasattr(self.chan_model, 'bis'):
                    result['bis'] = self.chan_model.bis

                # 获取线段
                if hasattr(self.chan_model, 'get_xianduan'):
                    result['xianduan'] = self.chan_model.get_xianduan()
                elif hasattr(self.chan_model, 'xianduan'):
                    result['xianduan'] = self.chan_model.xianduan

                # 获取买卖点
                if hasattr(self.chan_model, 'get_buy_sell_points'):
                    result['buy_sell_points'] = self.chan_model.get_buy_sell_points()
                elif hasattr(self.chan_model, 'buy_sell_points'):
                    result['buy_sell_points'] = self.chan_model.buy_sell_points

                return result

            # 方案3: 如果是函数式API
            else:
                # 请根据实际的chan.py函数API调整
                from chan import analyze_klines  # 假设有这样的函数
                return analyze_klines(chan_data)

        except Exception as e:
            app_logger.error(f"❌ Chan模块分析调用失败: {str(e)}")
            raise

    def _standardize_chan_result(self, chan_result: Any) -> Dict[str, Any]:
        """
        将Chan模块的结果转换为标准格式
        """
        try:
            # 根据Chan模块的实际返回格式进行转换
            standardized = {
                'fenxings': [],
                'bis': [],
                'xianduan': [],
                'buy_sell_points': [],
                'trend': {'direction': 'neutral', 'strength': 0},
                'support_resistance': {'support_levels': [], 'resistance_levels': []},
                'analysis_summary': {}
            }

            # 转换分型数据
            if hasattr(chan_result, 'fenxings') or 'fenxings' in chan_result:
                fenxings_data = getattr(chan_result, 'fenxings', chan_result.get('fenxings', []))
                standardized['fenxings'] = self._convert_fenxings(fenxings_data)

            # 转换笔数据
            if hasattr(chan_result, 'bis') or 'bis' in chan_result:
                bis_data = getattr(chan_result, 'bis', chan_result.get('bis', []))
                standardized['bis'] = self._convert_bis(bis_data)

            # 转换线段数据
            if hasattr(chan_result, 'xianduan') or 'xianduan' in chan_result:
                xianduan_data = getattr(chan_result, 'xianduan', chan_result.get('xianduan', []))
                standardized['xianduan'] = self._convert_xianduan(xianduan_data)

            # 转换买卖点数据
            if hasattr(chan_result, 'buy_sell_points') or 'buy_sell_points' in chan_result:
                buy_sell_data = getattr(chan_result, 'buy_sell_points', chan_result.get('buy_sell_points', []))
                standardized['buy_sell_points'] = self._convert_buy_sell_points(buy_sell_data)

            # 生成分析摘要
            standardized['analysis_summary'] = self._generate_summary(standardized)

            # 分析趋势
            standardized['trend'] = self._analyze_trend(standardized['bis'])

            return standardized

        except Exception as e:
            app_logger.error(f"❌ 结果标准化失败: {str(e)}")
            # 返回基本结构，包含原始结果用于调试
            return {
                'fenxings': [],
                'bis': [],
                'xianduan': [],
                'buy_sell_points': [],
                'trend': {'direction': 'neutral', 'strength': 0},
                'support_resistance': {'support_levels': [], 'resistance_levels': []},
                'analysis_summary': {'error': '结果转换失败', 'data_source': 'chan_module'},
                'raw_result': str(chan_result)  # 保留原始结果用于调试
            }

    def _convert_fenxings(self, fenxings_data: Any) -> List[Dict]:
        """转换分型数据格式"""
        converted = []
        try:
            for fx in fenxings_data:
                fenxing_dict = {}

                if hasattr(fx, '__dict__'):  # 如果是对象
                    fenxing_dict = {
                        'index': getattr(fx, 'index', getattr(fx, 'idx', 0)),
                        'timestamp': getattr(fx, 'timestamp', getattr(fx, 'time', 0)),
                        'price': float(getattr(fx, 'price', getattr(fx, 'value', 0))),
                        'type': getattr(fx, 'type', getattr(fx, 'fx_type', 'unknown')),
                        'strength': float(getattr(fx, 'strength', getattr(fx, 'power', 1.0)))
                    }
                elif isinstance(fx, dict):  # 如果是字典
                    fenxing_dict = {
                        'index': fx.get('index', fx.get('idx', 0)),
                        'timestamp': fx.get('timestamp', fx.get('time', 0)),
                        'price': float(fx.get('price', fx.get('value', 0))),
                        'type': fx.get('type', fx.get('fx_type', 'unknown')),
                        'strength': float(fx.get('strength', fx.get('power', 1.0)))
                    }
                elif isinstance(fx, (list, tuple)) and len(fx) >= 4:  # 如果是列表或元组
                    fenxing_dict = {
                        'index': fx[0] if len(fx) > 0 else 0,
                        'timestamp': fx[1] if len(fx) > 1 else 0,
                        'price': float(fx[2]) if len(fx) > 2 else 0,
                        'type': fx[3] if len(fx) > 3 else 'unknown',
                        'strength': float(fx[4]) if len(fx) > 4 else 1.0
                    }

                # 标准化type字段
                if fenxing_dict.get('type') in ['顶', 'top', 'TOP', '1']:
                    fenxing_dict['type'] = 'top'
                elif fenxing_dict.get('type') in ['底', 'bottom', 'BOTTOM', '-1']:
                    fenxing_dict['type'] = 'bottom'

                converted.append(fenxing_dict)

        except Exception as e:
            app_logger.warning(f"分型数据转换警告: {str(e)}")

        return converted

    def _convert_bis(self, bis_data: Any) -> List[Dict]:
        """转换笔数据格式"""
        converted = []
        try:
            for bi in bis_data:
                bi_dict = {}

                if hasattr(bi, '__dict__'):
                    bi_dict = {
                        'start': self._extract_point_info(getattr(bi, 'start', None)),
                        'end': self._extract_point_info(getattr(bi, 'end', None)),
                        'direction': getattr(bi, 'direction', 'unknown'),
                        'length': float(getattr(bi, 'length', 0)),
                        'bars_count': getattr(bi, 'bars_count', getattr(bi, 'bar_count', 0))
                    }
                elif isinstance(bi, dict):
                    bi_dict = {
                        'start': self._extract_point_info(bi.get('start')),
                        'end': self._extract_point_info(bi.get('end')),
                        'direction': bi.get('direction', 'unknown'),
                        'length': float(bi.get('length', 0)),
                        'bars_count': bi.get('bars_count', bi.get('bar_count', 0))
                    }

                # 标准化direction字段
                if bi_dict.get('direction') in ['上', 'up', 'UP', '1']:
                    bi_dict['direction'] = 'up'
                elif bi_dict.get('direction') in ['下', 'down', 'DOWN', '-1']:
                    bi_dict['direction'] = 'down'

                converted.append(bi_dict)
        except Exception as e:
            app_logger.warning(f"笔数据转换警告: {str(e)}")

        return converted

    def _extract_point_info(self, point) -> Dict:
        """提取点位信息"""
        if not point:
            return {'timestamp': 0, 'price': 0, 'type': 'unknown'}

        if hasattr(point, '__dict__'):
            return {
                'timestamp': getattr(point, 'timestamp', getattr(point, 'time', 0)),
                'price': float(getattr(point, 'price', getattr(point, 'value', 0))),
                'type': getattr(point, 'type', 'unknown')
            }
        elif isinstance(point, dict):
            return {
                'timestamp': point.get('timestamp', point.get('time', 0)),
                'price': float(point.get('price', point.get('value', 0))),
                'type': point.get('type', 'unknown')
            }

        return {'timestamp': 0, 'price': 0, 'type': 'unknown'}

    def _convert_xianduan(self, xianduan_data: Any) -> List[Dict]:
        """转换线段数据格式"""
        converted = []
        try:
            for xd in xianduan_data:
                if hasattr(xd, '__dict__'):
                    converted.append({
                        'start': self._extract_point_info(getattr(xd, 'start', None)),
                        'end': self._extract_point_info(getattr(xd, 'end', None)),
                        'direction': getattr(xd, 'direction', 'unknown'),
                        'length': float(getattr(xd, 'length', 0))
                    })
                elif isinstance(xd, dict):
                    converted.append({
                        'start': self._extract_point_info(xd.get('start')),
                        'end': self._extract_point_info(xd.get('end')),
                        'direction': xd.get('direction', 'unknown'),
                        'length': float(xd.get('length', 0))
                    })
        except Exception as e:
            app_logger.warning(f"线段数据转换警告: {str(e)}")

        return converted

    def _convert_buy_sell_points(self, buy_sell_data: Any) -> List[Dict]:
        """转换买卖点数据格式"""
        converted = []
        try:
            for point in buy_sell_data:
                if hasattr(point, '__dict__'):
                    converted.append({
                        'type': getattr(point, 'type', 'unknown'),
                        'timestamp': getattr(point, 'timestamp', getattr(point, 'time', 0)),
                        'price': float(getattr(point, 'price', getattr(point, 'value', 0))),
                        'confidence': float(getattr(point, 'confidence', getattr(point, 'strength', 0.5)))
                    })
                elif isinstance(point, dict):
                    converted.append({
                        'type': point.get('type', 'unknown'),
                        'timestamp': point.get('timestamp', point.get('time', 0)),
                        'price': float(point.get('price', point.get('value', 0))),
                        'confidence': float(point.get('confidence', point.get('strength', 0.5)))
                    })
        except Exception as e:
            app_logger.warning(f"买卖点数据转换警告: {str(e)}")

        return converted

    def _analyze_trend(self, bis: List[Dict]) -> Dict:
        """分析趋势"""
        if not bis or len(bis) < 3:
            return {'direction': 'neutral', 'strength': 0}

        recent_bis = bis[-6:]  # 最近6笔
        up_count = sum(1 for bi in recent_bis if bi.get('direction') == 'up')
        down_count = sum(1 for bi in recent_bis if bi.get('direction') == 'down')

        if up_count > down_count * 1.5:
            direction = 'up'
            strength = (up_count - down_count) / len(recent_bis)
        elif down_count > up_count * 1.5:
            direction = 'down'
            strength = (down_count - up_count) / len(recent_bis)
        else:
            direction = 'neutral'
            strength = 0

        return {'direction': direction, 'strength': min(1.0, abs(strength))}

    def _generate_summary(self, data: Dict) -> Dict:
        """生成分析摘要"""
        fenxings = data.get('fenxings', [])
        bis = data.get('bis', [])
        trend = data.get('trend', {})

        # 生成操作建议
        direction = trend.get('direction', 'neutral')
        strength = trend.get('strength', 0)

        if direction == 'up' and strength > 0.6:
            suggestion = '趋势向上，可考虑逢低建仓，注意风险控制'
        elif direction == 'down' and strength > 0.6:
            suggestion = '趋势向下，建议观望等待，避免盲目抄底'
        else:
            suggestion = '趋势不明确，建议等待明确信号后操作'

        return {
            'trend_direction': direction,
            'trend_strength': strength,
            'total_fenxings': len(fenxings),
            'total_bis': len(bis),
            'suggestion': suggestion,
            'analysis_quality': 'good' if len(fenxings) >= 5 else 'limited',
            'data_source': 'chan_module'
        }

    def _fallback_analysis(self, klines: List[Dict]) -> Dict[str, Any]:
        """
        当Chan模块不可用时的简化分析
        """
        app_logger.info("🔄 使用简化分析模式")

        return {
            'fenxings': [],
            'bis': [],
            'xianduan': [],
            'buy_sell_points': [],
            'trend': {'direction': 'neutral', 'strength': 0},
            'support_resistance': {'support_levels': [], 'resistance_levels': []},
            'analysis_summary': {
                'trend_direction': 'neutral',
                'trend_strength': 0,
                'total_fenxings': 0,
                'total_bis': 0,
                'suggestion': 'Chan模块不可用，无法进行详细分析',
                'analysis_quality': 'limited',
                'data_source': 'fallback'
            },
            'error': 'Chan模块不可用，请检查chan.py子模块配置'
        }

    def get_chan_info(self) -> Dict[str, Any]:
        """获取Chan模块信息"""
        return {
            'is_available': self.is_available,
            'module_loaded': CHAN_MODULE_AVAILABLE,
            'version': getattr(self.chan_model, 'version', 'unknown') if self.chan_model else None,
            'supported_features': getattr(self.chan_model, 'features', []) if self.chan_model else [],
            'status': 'ready' if self.is_available else 'unavailable',
            'integration_guide': {
                'step1': '确保chan.py子模块已初始化: git submodule update --init',
                'step2': '检查chan.py模块的API接口',
                'step3': '根据实际API调整chan_adapter.py中的导入和调用',
                'step4': '运行test_chan_integration.py测试集成'
            }
        }


# 创建全局实例
chan_adapter = ChanAdapter()