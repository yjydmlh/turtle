# 🐢 缠论多级别联立分析交易策略

## 📋 策略概述

基于缠中说禅理论实现的专业技术分析交易策略，支持多级别联立分析，自动生成交易信号。

### 🎯 核心功能

1. **分型识别** - 自动识别顶分型🔺和底分型🔻
2. **笔构建** - 基于分型构建上涨笔和下跌笔
3. **趋势分析** - 判断趋势方向和强度
4. **买卖点识别** - 生成第一、二、三类买卖点信号
5. **风险控制** - 提供止损止盈和仓位建议
6. **策略回测** - 历史数据策略表现评估

### 🔧 技术特点

- **多级别分析**: 支持1分钟到日线的多时间周期分析
- **智能信号**: 基于缠论理论的专业买卖点识别
- **风险管理**: 自动计算止损止盈和建议仓位
- **置信度评级**: 每个信号都有置信度评分
- **实时分析**: 支持实时K线数据分析

## 🚀 快速开始

### 1. 启动系统

```bash
# 启动后端服务
python quick_start.py

# 或手动启动
python run.py
```

### 2. 测试策略功能

```bash
# 运行策略测试
python test_chan_strategy.py
```

### 3. API调用示例

#### 获取交易信号
```bash
curl "http://localhost:8000/api/v1/strategy/analyze?timeframe=1h&limit=200"
```

#### 策略回测
```bash
curl "http://localhost:8000/api/v1/strategy/backtest?timeframe=1h&days=30&initial_capital=10000"
```

#### 获取信号历史
```bash
curl "http://localhost:8000/api/v1/strategy/signals/history?timeframe=1h&days=7"
```

## 📊 API接口详解

### 策略分析 `/api/v1/strategy/analyze`

**参数:**
- `timeframe`: 时间周期 (1m,5m,15m,30m,1h,4h,1d)
- `limit`: K线数量 (50-500，建议200+)
- `symbol`: 交易品种 (默认btc_usdt)

**返回示例:**
```json
{
  "success": true,
  "data": {
    "trading_signals": {
      "total_signals": 3,
      "buy_signals": 2,
      "sell_signals": 1,
      "signals": [
        {
          "signal_type": "第三类买点",
          "timestamp": 1703123456000,
          "price": 42500.0,
          "confidence": 0.75,
          "level": "1h",
          "description": "底分型买入信号 - 强度: 1.2",
          "risk_level": "medium",
          "position_size": 0.15,
          "stop_loss": 41175.0,
          "take_profit": 45050.0
        }
      ]
    },
    "market_analysis": {
      "fenxings_identified": 8,
      "bis_constructed": 5,
      "trend_analysis": {
        "direction": "up",
        "strength": 0.65,
        "price_change": 0.023
      }
    },
    "recommendation": {
      "action": "BUY",
      "reason": "底分型买入信号 - 强度: 1.2",
      "confidence": 0.75,
      "position_size": 0.15
    }
  }
}
```

### 策略回测 `/api/v1/strategy/backtest`

**参数:**
- `timeframe`: 时间周期
- `days`: 回测天数 (7-90)
- `initial_capital`: 初始资金

**返回示例:**
```json
{
  "success": true,
  "data": {
    "performance": {
      "initial_capital": 10000,
      "final_capital": 11250,
      "total_return": 12.5,
      "total_trades": 15,
      "win_rate": 66.7,
      "profit_factor": 2.3
    },
    "summary": {
      "profitable_trades": 10,
      "losing_trades": 5,
      "largest_win": 850.0,
      "largest_loss": -320.0
    }
  }
}
```

## 🎯 信号类型解释

### 第一类买卖点
- **特征**: 趋势转折点，风险相对较高
- **适用**: 底部买入，顶部卖出
- **策略**: 谨慎操作，小仓位试探

### 第二类买卖点  
- **特征**: 趋势确认点，胜率较高
- **适用**: 突破确认后的介入点
- **策略**: 中等仓位，跟随趋势

### 第三类买卖点
- **特征**: 趋势延续点，风险较低
- **适用**: 回调买入，反弹卖出
- **策略**: 相对安全的追涨杀跌点

## 🛡️ 风险管理

### 仓位控制
- **低风险信号**: 最大20%仓位
- **中风险信号**: 最大15%仓位  
- **高风险信号**: 最大10%仓位

### 止损策略
- **分型止损**: 跌破分型低点
- **百分比止损**: 固定2-3%止损
- **时间止损**: 持仓超过设定时间

### 止盈策略
- **目标止盈**: 达到预设收益目标
- **移动止盈**: 跟踪止盈保护利润
- **分批止盈**: 分批获利了结

## 📈 使用建议

### 多级别确认
1. **日线级别**: 确定主趋势方向
2. **4小时级别**: 确认中期趋势
3. **1小时级别**: 寻找具体入场点

### 信号过滤
- 只操作置信度≥0.6的信号
- 多级别趋势一致时加大仓位
- 避免在重要阻力支撑位盲目操作

### 资金管理
- 单次最大风险不超过总资金2%
- 总持仓不超过总资金30%
- 保持足够现金应对机会

## 🔧 配置参数

### 策略参数
```python
config = {
    'risk_ratio': 0.02,          # 单次风险比例2%
    'max_position': 0.3,         # 最大仓位30%
    'confidence_threshold': 0.6,  # 信号置信度阈值
}
```

### 缠论参数
```python
chan_config = {
    'bi_strict': True,           # 严格笔模式
    'seg_algo': 'chan',         # 缠论线段算法
    'divergence_rate': 0.8,     # 背驰比例
    'min_zs_cnt': 1,           # 最小中枢数量
}
```

## 🐛 故障排除

### 常见问题

1. **Chan模块不可用**
   ```bash
   git submodule update --init
   ```

2. **数据库连接失败**
   ```bash
   python create_tables.py
   ```

3. **API调用失败**
   ```bash
   python quick_start.py  # 确保服务器运行
   ```

### 日志查看
- 应用日志: `logs/app.log`
- 策略日志: 控制台输出
- 错误信息: API响应中的error字段

## 📚 进阶使用

### 自定义策略参数
```python
from app.services.chan_strategy import ChanMultiLevelStrategy

# 创建自定义配置的策略
custom_config = {
    'risk_ratio': 0.015,  # 更保守的风险控制
    'confidence_threshold': 0.7,  # 更高的信号要求
}

strategy = ChanMultiLevelStrategy('BTC/USDT', custom_config)
result = strategy.analyze_klines(klines, '1h')
```

### 批量分析
```python
symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
timeframes = ['1h', '4h', '1d']

for symbol in symbols:
    for tf in timeframes:
        result = analyze_with_chan_strategy(klines, tf, symbol)
        # 处理结果...
```

## 📞 技术支持

- **项目地址**: https://github.com/your-username/turtle
- **问题反馈**: 在GitHub Issues中提交
- **技术讨论**: 缠论交流群

---

**免责声明**: 本策略仅供学习和研究使用，不构成投资建议。实际交易有风险，请谨慎操作。