<docs>
# 缠论分析API

<cite>
**本文档引用的文件**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py)
- [chan_adapter.py](file://app/services/chan_adapter.py)
- [Chan.py](file://chan.py/Chan.py)
- [kline.py](file://app/schemas/kline.py)
- [chan_strategy.py](file://app/api/v1/endpoints/chan_strategy.py) - *新增于最近提交*
- [api.py](file://app/api/v1/api.py) - *已修改*
</cite>

## 更新摘要
**变更内容**   
- 新增了缠论策略分析API端点，包括`/strategy/analyze`、`/strategy/signals/history`和`/strategy/backtest`
- 在API路由中添加了新的策略模块，与原有分析模块并列
- 更新了调用关系图，增加了新的策略分析路径
- 添加了新的客户端使用示例，展示策略API的调用方法

## 目录
1. [简介](#简介)
2. [API端点参考](#api端点参考)
3. [认证与速率限制](#认证与速率限制)
4. [API版本控制](#api版本控制)
5. [调用关系与数据流](#调用关系与数据流)
6. [客户端使用示例](#客户端使用示例)

## 简介
缠论分析API提供了一套完整的缠论技术分析功能，集成于交易系统后端。该模块通过适配外部`chan.py`子模块，实现了分型、笔、线段、买卖点等核心缠论概念的自动识别与分析。API设计遵循RESTful原则，所有端点均位于`/api/v1/chan`路径下，返回统一的JSON响应格式。

系统具备容错机制：当外部`chan.py`模块不可用时，会自动降级为简化分析模式，确保服务可用性。API与FastAPI自动生成的Swagger UI保持一致，并提供了更丰富的文档说明和使用示例。

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L1-L420)
- [chan_adapter.py](file://app/services/chan_adapter.py#L1-L516)

## API端点参考

### 获取模块信息
获取缠论模块的当前状态和集成信息。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/chan/info`

**请求参数**
- 无

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "chan_module": {
      "is_available": true,
      "module_loaded": true,
      "version": "unknown",
      "supported_features": [],
      "status": "ready",
      "integration_guide": {
        "step1": "确保chan.py子模块已初始化: git submodule update --init",
        "step2": "检查chan.py模块的API接口",
        "step3": "根据实际API调整chan_adapter.py中的导入和调用",
        "step4": "运行test_chan_integration.py测试集成"
      }
    },
    "system_info": {
      "integration_status": "ready",
      "data_flow": [
        "1. 获取K线数据 (kline_aggregator)",
        "2. 调用Chan模块分析 (chan_adapter)",
        "3. 标准化结果格式",
        "4. 返回缠论分析结果"
      ],
      "supported_analysis": [
        "分型识别 (顶分型、底分型)",
        "笔的构建 (上涨笔、下跌笔)",
        "线段分析",
        "买卖点识别",
        "趋势方向判断"
      ]
    }
  }
}
```

**HTTP状态码**
- `200 OK`: 成功获取模块信息
- `500 Internal Server Error`: 获取模块信息失败

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L4-L33)

### 缠论技术分析
执行完整的缠论技术分析。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/chan/analyze`

**请求参数**
| 参数名 | 类型 | 位置 | 必需 | 约束 | 描述 |
|-------|------|------|------|------|------|
| `timeframe` | 字符串 | 查询参数 | 否 | 默认值: `"1h"` | 时间周期 (1m, 5m, 15m, 30m, 1h, 4h, 1d) |
| `limit` | 整数 | 查询参数 | 否 | 范围: 50-500, 默认值: `200` | 分析的K线数量 |

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "analysis": {
      "fenxings": [
        {
          "index": 15,
          "timestamp": 1700000000000,
          "price": 35000.5,
          "type": "top",
          "strength": 0.8
        }
      ],
      "bis": [
        {
          "start": {
            "timestamp": 1700000000000,
            "price": 35000.5
          },
          "end": {
            "timestamp": 1700003600000,
            "price": 36000.0
          },
          "direction": "up",
          "length": 999.5,
          "bars_count": 6
        }
      ],
      "xianduan": [],
      "buy_sell_points": [],
      "trend": {
        "direction": "up",
        "strength": 0.6
      },
      "support_resistance": {
        "support_levels": [],
        "resistance_levels": []
      },
      "analysis_summary": {
        "trend_direction": "up",
        "trend_strength": 0.6,
        "total_fenxings": 1,
        "total_bis": 1,
        "suggestion": "趋势向上，可考虑逢低建仓，注意风险控制",
        "analysis_quality": "good",
        "data_source": "chan_module"
      }
    },
    "metadata": {
      "klines_analyzed": 200,
      "timeframe": "1h",
      "analysis_time": 1700003600000,
      "latest_price": 36000.0,
      "chan_module_available": true,
      "data_source": "chan_module",
      "statistics": {
        "fenxings": 1,
        "bis": 1,
        "xianduan": 0,
        "buy_sell_points": 0
      }
    },
    "usage_tips": {
      "fenxings": "🔺红色标记为顶分型，🔻绿色标记为底分型",
      "bis": "连接相邻分型形成的笔，显示价格运动方向",
      "trend": "基于最近几笔的方向和强度判断趋势",
      "suggestion": "根据缠论理论生成的操作建议，仅供参考"
    }
  }
}
```

**HTTP状态码**
- `200 OK`: 分析成功
- `404 Not Found`: 没有找到K线数据
- `500 Internal Server Error`: 分析服务暂时不可用

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L34-L138)

### 获取图表数据
获取为前端图表优化的数据，包含K线和缠论分析标记。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/chan/chart-data`

**请求参数**
| 参数名 | 类型 | 位置 | 必需 | 约束 | 描述 |
|-------|------|------|------|------|------|
| `timeframe` | 字符串 | 查询参数 | 否 | 默认值: `"1h"` | 时间周期 (1m, 5m, 15m, 30m, 1h, 4h, 1d) |
| `limit` | 整数 | 查询参数 | 否 | 范围: 20-300, 默认值: `100` | 图表数据量 |
| `include_analysis` | 布尔值 | 查询参数 | 否 | 默认值: `true` | 是否包含分析结果 |

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "chart_data": {
      "klines": [
        [1700000000000, 34000.0, 35000.5, 33900.0, 35000.5],
        [1700003600000, 35000.5, 36000.0, 34900.0, 36000.0]
      ],
      "volume": [
        [1700000000000, 1000.5],
        [1700003600000, 1200.3]
      ],
      "timestamps": [1700000000000, 1700003600000]
    },
    "analysis": {
      "fenxings": [
        {
          "index": 15,
          "timestamp": 1700000000000,
          "price": 35000.5,
          "type": "top",
          "strength": 0.8
        }
      ],
      "bis": [
        {
          "start": {
            "timestamp": 1700000000000,
            "price": 35000.5
          },
          "end": {
            "timestamp": 1700003600000,
            "price": 36000.0
          },
          "direction": "up",
          "length": 999.5,
          "bars_count": 6
        }
      ],
      "trend": {
        "direction": "up",
        "strength": 0.6
      },
      "analysis_summary": {
        "trend_direction": "up",
        "trend_strength": 0.6,
        "total_fenxings": 1,
        "total_bis": 1,
        "suggestion": "趋势向上，可考虑逢低建仓，注意风险控制",
        "analysis_quality": "good",
        "data_source": "chan_module"
      }
    },
    "chart_markers": {
      "fenxings": [
        {
          "timestamp": 1700000000000,
          "price": 35000.5,
          "type": "top",
          "strength": 0.8,
          "symbol": "🔺",
          "color": "#ef4444"
        }
      ],
      "bis_lines": [
        {
          "start": {
            "timestamp": 1700000000000,
            "price": 35000.5
          },
          "end": {
            "timestamp": 1700003600000,
            "price": 36000.0
          },
          "direction": "up",
          "color": "#22c55e",
          "width": 2
        }
      ],
      "buy_sell_points": []
    },
    "metadata": {
      "timeframe": "1h",
      "data_count": 100,
      "price_range": {
        "high": 36000.0,
        "low": 33900.0
      },
      "time_range": {
        "start": 1700000000000,
        "end": 1700003600000
      },
      "analysis_included": true,
      "chan_module_status": true
    }
  }
}
```

**HTTP状态码**
- `200 OK`: 数据获取成功
- `404 Not Found`: 没有找到K线数据
- `500 Internal Server Error`: 获取图表数据失败

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L140-L285)

### 获取分析摘要
获取简化的市场状态摘要，适合快速查看。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/chan/summary`

**请求参数**
| 参数名 | 类型 | 位置 | 必需 | 约束 | 描述 |
|-------|------|------|------|------|------|
| `timeframe` | 字符串 | 查询参数 | 否 | 默认值: `"1h"` | 时间周期 (1m, 5m, 15m, 30m, 1h, 4h, 1d) |

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "market_status": {
      "current_price": 36000.0,
      "trend_direction": "up",
      "trend_strength": 0.6,
      "trend_description": "📈 上涨趋势"
    },
    "chan_analysis": {
      "fenxings_count": 1,
      "bis_count": 1,
      "analysis_quality": "good",
      "data_source": "chan_module"
    },
    "trading_suggestion": {
      "suggestion": "趋势向上，可考虑逢低建仓，注意风险控制",
      "confidence": "high",
      "risk_level": "low"
    },
    "metadata": {
      "timeframe": "1h",
      "last_update": 1700003600000,
      "data_points": 100,
      "chan_module_available": true
    }
  }
}
```

**HTTP状态码**
- `200 OK`: 摘要获取成功
- `500 Internal Server Error`: 获取摘要失败

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L287-L375)

### 获取分型数据
仅获取分型识别结果，轻量级分析接口。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/chan/fenxings`

**请求参数**
| 参数名 | 类型 | 位置 | 必需 | 约束 | 描述 |
|-------|------|------|------|------|------|
| `timeframe` | 字符串 | 查询参数 | 否 | 默认值: `"1h"` | 时间周期 (1m, 5m, 15m, 30m, 1h, 4h, 1d) |
| `limit` | 整数 | 查询参数 | 否 | 范围: 50-500, 默认值: `200` | 分析的K线数量 |

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "fenxings": {
      "all": [
        {
          "index": 15,
          "timestamp": 1700000000000,
          "price": 35000.5,
          "type": "top",
          "strength": 0.8
        }
      ],
      "tops": [
        {
          "index": 15,
          "timestamp": 1700000000000,
          "price": 35000.5,
          "type": "top",
          "strength": 0.8
        }
      ],
      "bottoms": []
    },
    "statistics": {
      "total": 1,
      "tops_count": 1,
      "bottoms_count": 0,
      "average_strength": 0.8
    },
    "metadata": {
      "timeframe": "1h",
      "klines_analyzed": 200,
      "analysis_type": "fenxings_only"
    }
  }
}
```

**HTTP状态码**
- `200 OK`: 分型数据获取成功
- `404 Not Found`: 没有找到K线数据
- `500 Internal Server Error`: 获取分型数据失败

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L377-L420)

### 健康检查
检查缠论分析模块的健康状态。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/chan/health`

**请求参数**
- 无

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "components": {
      "chan_adapter": "ready",
      "chan_module": "loaded",
      "analysis_capability": "full"
    },
    "features": {
      "fenxing_recognition": true,
      "bi_construction": true,
      "xianduan_analysis": true,
      "buy_sell_points": true
    },
    "performance": {
      "analysis_mode": "chan_module",
      "recommended_data_size": "200+ K线获得最佳效果",
      "supported_timeframes": [
        "1m",
        "5m",
        "15m",
        "30m",
        "1h",
        "4h",
        "1d"
      ]
    }
  }
}
```

**HTTP状态码**
- `200 OK`: 健康检查成功
- `500 Internal Server Error`: 健康检查失败

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L422-L460)

### 缠论策略分析
执行基于缠论的多级别联立分析，生成交易信号。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/strategy/analyze`

**请求参数**
| 参数名 | 类型 | 位置 | 必需 | 约束 | 描述 |
|-------|------|------|------|------|------|
| `timeframe` | 字符串 | 查询参数 | 否 | 默认值: `"1h"` | 时间周期 (1m,5m,15m,30m,1h,4h,1d) |
| `limit` | 整数 | 查询参数 | 否 | 范围: 50-500, 默认值: `200` | 分析的K线数量 |
| `symbol` | 字符串 | 查询参数 | 否 | 默认值: `"btc_usdt"` | 交易品种 |

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "strategy_analysis": {
      "signals": [
        {
          "signal_type": "第三类买点",
          "timestamp": 1700000000000,
          "price": 35000.5,
          "confidence": 0.85,
          "level": "1h",
          "description": "底分型买入信号 - 强度: 0.80",
          "risk_level": "low",
          "position_size": 0.15,
          "stop_loss": 33950.485,
          "take_profit": 37100.53
        }
      ],
      "analysis": {
        "fenxings": [
          {
            "type": "bottom",
            "timestamp": 1700000000000,
            "price": 35000.5,
            "index": 15,
            "strength": 0.8
          }
        ],
        "bis": [
          {
            "start": {
              "type": "top",
              "timestamp": 1699996400000,
              "price": 36000.0,
              "index": 14
            },
            "end": {
              "type": "bottom",
              "timestamp": 1700000000000,
              "price": 35000.5,
              "index": 15
            },
            "direction": "down",
            "length": 999.5,
            "time_span": 3600000,
            "bars_count": 6
          }
        ],
        "trend_analysis": {
          "direction": "up",
          "strength": 0.6,
          "price_change": 0.03,
          "bi_analysis": {
            "up_ratio": 0.67,
            "recent_bis_count": 3
          }
        },
        "support_resistance": {
          "support_levels": [34500.0, 34000.0],
          "resistance_levels": [36000.0, 36500.0]
        },
        "market_structure": {
          "trend_direction": "up",
          "trend_strength": 0.6,
          "current_phase": "上升阶段"
        }
      },
      "recommendation": {
        "action": "BUY",
        "reason": "底分型买入信号 - 强度: 0.80",
        "confidence": 0.85,
        "position_size": 0.15,
        "price": 35000.5,
        "stop_loss": 33950.485,
        "take_profit": 37100.53,
        "risk_level": "low"
      },
      "metadata": {
        "timeframe": "1h",
        "data_count": 200,
        "analysis_time": "2023-11-15T10:00:00",
        "chan_module_available": true
      }
    },
    "trading_signals": {
      "total_signals": 1,
      "buy_signals": 1,
      "sell_signals": 0,
      "signals": [
        {
          "signal_type": "第三类买点",
          "timestamp": 1700000000000,
          "price": 35000.5,
          "confidence": 0.85,
          "level": "1h",
          "description": "底分型买入信号 - 强度: 0.80",
          "risk_level": "low",
          "position_size": 0.15,
          "stop_loss": 33950.485,
          "take_profit": 37100.53
        }
      ]
    },
    "market_analysis": {
      "fenxings_identified": 1,
      "bis_constructed": 1,
      "trend_analysis": {
        "direction": "up",
        "strength": 0.6,
        "price_change": 0.03,
        "bi_analysis": {
          "up_ratio": 0.67,
          "recent_bis_count": 3
        }
      },
      "support_resistance": {
        "support_levels": [34500.0, 34000.0],
        "resistance_levels": [36000.0, 36500.0]
      },
      "market_structure": {
        "trend_direction": "up",
        "trend_strength": 0.6,
        "current_phase": "上升阶段"
      }
    },
    "recommendation": {
      "action": "BUY",
      "reason": "底分型买入信号 - 强度: 0.80",
      "confidence": 0.85,
      "position_size": 0.15,
      "price": 35000.5,
      "stop_loss": 33950.485,
      "take_profit": 37100.53,
      "risk_level": "low"
    },
    "metadata": {
      "symbol": "btc_usdt",
      "timeframe": "1h",
      "klines_analyzed": 200,
      "latest_price": 36000.0,
      "analysis_timestamp": "2023-11-15T10:00:00",
      "strategy_info": {
        "name": "缠论多级别联立分析策略",
        "version": "1.0.0",
        "description": "基于缠中说禅理论的多级别技术分析策略",
        "features": [
          "分型识别",
          "笔段构建",
          "趋势分析",
          "买卖点识别",
          "风险评估"
        ]
      },
      "performance_metrics": {
        "analysis_coverage": 75.0,
        "signal_quality": 85.0,
        "data_completeness": 100.0
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
  }
}
```

**HTTP状态码**
- `200 OK`: 分析成功
- `404 Not Found`: 没有找到K线数据
- `500 Internal Server Error`: 策略分析服务暂时不可用

**Section sources**
- [chan_strategy.py](file://app/api/v1/endpoints/chan_strategy.py#L20-L141)

### 获取策略信号历史
获取缠论策略的历史信号，用于回测分析和策略优化。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/strategy/signals/history`

**请求参数**
| 参数名 | 类型 | 位置 | 必需 | 约束 | 描述 |
|-------|------|------|------|------|------|
| `timeframe` | 字符串 | 查询参数 | 否 | 默认值: `"1h"` | 时间周期 |
| `days` | 整数 | 查询参数 | 否 | 范围: 1-30, 默认值: `7` | 历史天数 |
| `signal_type` | 字符串 | 查询参数 | 否 | 可选值: "买", "卖" | 信号类型过滤 |

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "signals": [
      {
        "signal_type": "第三类买点",
        "timestamp": 1700000000000,
        "price": 35000.5,
        "confidence": 0.85,
        "level": "1h",
        "description": "底分型买入信号 - 强度: 0.80",
        "risk_level": "low",
        "position_size": 0.15,
        "stop_loss": 33950.485,
        "take_profit": 37100.53,
        "batch_index": 100
      }
    ],
    "statistics": {
      "total_signals": 1,
      "buy_signals": 1,
      "sell_signals": 0,
      "average_confidence": 0.85,
      "signal_frequency": 0.14
    },
    "performance": {
      "win_rate": 75.0,
      "average_return": 2.5,
      "total_signals": 1
    },
    "metadata": {
      "timeframe": "1h",
      "days_analyzed": 7,
      "klines_processed": 168,
      "analysis_batches": 1
    }
  }
}
```

**HTTP状态码**
- `200 OK`: 获取历史信号成功
- `500 Internal Server Error`: 获取历史信号失败

**Section sources**
- [chan_strategy.py](file://app/api/v1/endpoints/chan_strategy.py#L145-L236)

### 缠论策略回测
执行缠论策略的回测分析，模拟历史交易表现。

**HTTP方法**  
`GET`

**URL路径**  
`/api/v1/strategy/backtest`

**请求参数**
| 参数名 | 类型 | 位置 | 必需 | 约束 | 描述 |
|-------|------|------|------|------|------|
| `timeframe` | 字符串 | 查询参数 | 否 | 默认值: `"1h"` | 时间周期 |
| `days` | 整数 | 查询参数 | 否 | 范围: 7-90, 默认值: `30` | 回测天数 |
| `initial_capital` | 浮点数 | 查询参数 | 否 | 范围: 1000+, 默认值: `10000` | 初始资金 |

**成功响应示例**
```json
{
  "success": true,
  "data": {
    "performance": {
      "initial_capital": 10000,
      "final_capital": 12500,
      "total_return": 25.0,
      "total_trades": 15,
      "win_rate": 66.7,
      "profit_factor": 2.5,
      "average_win": 150.0,
      "average_loss": 60.0
    },
    "trades": [
      {
        "entry_price": 35000.5,
        "exit_price": 36000.0,
        "profit": 1000.0,
        "return_rate": 0.0286
      }
    ],
    "summary": {
      "profitable_trades": 10,
      "losing_trades": 5,
      "largest_win": 2000.0,
      "largest_loss": 150.0,
      "average_return_per_trade": 0.0167
    },
    "metadata": {
      "backtest_period": "720 1h periods",
      "strategy": "缠论多级别联立分析",
      "timeframe": "1h"
    }
  }
}
```

**HTTP状态码**
- `200 OK`: 回测成功
- `400 Bad Request`: 历史数据不足
- `500 Internal Server Error`: 回测服务暂时不可用

**Section sources**
- [chan_strategy.py](file://app/api/v1/endpoints/chan_strategy.py#L240-L288)

## 认证与速率限制
当前版本的缠论分析API**未实现认证机制**，所有端点均为公开访问。这适用于内部网络或受信任环境。

**速率限制策略**：
- **默认策略**：未配置全局速率限制。
- **建议**：在生产环境中，建议通过反向代理（如Nginx）或API网关（如Kong）实现速率限制，例如：
  - 每个IP地址每分钟最多100次请求
  - 高频分析端点（如`/analyze`）每分钟最多10次请求

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L1-L460)

## API版本控制
系统采用**URI路径版本控制**策略，所有缠论分析API均位于`/api/{version}/chan`前缀下。

**策略说明**：
- **路径结构**：`/api/{version}/chan/{endpoint}`
- **当前版本**：`v1`
- **向后兼容**：`v1`版本承诺在不破坏现有客户端的情况下进行功能增强和错误修复。
- **未来规划**：当需要进行不兼容的变更时，将引入`v2`版本，同时保持`v1`版本的维护。

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L1-L460)

## 调用关系与数据流
缠论分析模块的端点之间存在明确的调用关系和数据流依赖。

```mermaid
flowchart TD
A[/api/v1/chan/analyze] --> B[获取K线数据]
C[/api/v1/chan/chart-data] --> B
D[/api/v1/chan/summary] --> B
E[/api/v1/chan/fenxings] --> B
B --> F[调用Chan模块分析]
F --> G[标准化结果]
G --> H[返回响应]
I[/api/v1/strategy/analyze] --> B
J[/api/v1/strategy/signals/history] --> B
K[/api/v1/strategy/backtest] --> B
subgraph "数据准备"
B
end
subgraph "核心分析"
F
G
end
subgraph "前端优化"
C
end
subgraph "轻量级接口"
D
E
end
subgraph "策略分析"
I
J
K
end
style A fill:#4CAF50,stroke:#388E3C
style C fill:#2196F3,stroke:#1976D2
style D fill:#FF9800,stroke:#F57C00
style E fill:#FF9800,stroke:#F57C00
style I fill:#9C27B0,stroke:#7B1FA2
style J fill:#9C27B0,stroke:#7B1FA2
style K fill:#9C27B0,stroke:#7B1FA2
```

**Diagram sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L34-L460)
- [chan_adapter.py](file://app/services/chan_adapter.py#L1-L516)
- [chan_strategy.py](file://app/api/v1/endpoints/chan_strategy.py#L20-L288)

**关键说明**：
1. **`/chan/analyze`**：核心端点，依赖K线数据准备和Chan模块分析，返回完整结果。
2. **`/chan/chart-data`**：专为前端设计，复用`/analyze`的分析逻辑，但将数据结构优化为图表库友好的格式。
3. **`/chan/summary`** 和 **`/chan/fenxings`**：轻量级端点，用于快速获取关键信息，减少前端处理负担。
4. **`/chan/health`** 和 **`/chan/info`**：元数据端点，不依赖K线数据，用于系统监控和诊断。
5. **`/strategy/analyze`**：新的策略分析端点，提供多级别联立分析和交易信号生成。
6. **`/strategy/signals/history`** 和 **`/strategy/backtest`**：策略历史信号和回测端点，用于策略优化和性能评估。

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L1-L460)
- [chan_adapter.py](file://app/services/chan_adapter.py#L1-L516)
- [chan_strategy.py](file://app/api/v1/endpoints/chan_strategy.py#L20-L288)

## 客户端使用示例

### curl命令行示例
```bash
# 获取模块信息
curl -X GET "http://localhost:8000/api/v1/chan/info"

# 执行缠论分析 (1小时周期，200根K线)
curl -X GET "http://localhost:8000/api/v1/chan/analyze?timeframe=1h&limit=200"

# 获取图表数据 (包含分析结果)
curl -X GET "http://localhost:8000/api/v1/chan/chart-data?timeframe=1h&limit=100&include_analysis=true"

# 获取分析摘要
curl -X GET "http://localhost:8000/api/v1/chan/summary?timeframe=4h"

# 获取分型数据
curl -X GET "http://localhost:8000/api/v1/chan/fenxings?timeframe=15m&limit=100"

# 健康检查
curl -X GET "http://localhost:8000/api/v1/chan/health"

# 执行缠论策略分析
curl -X GET "http://localhost:8000/api/v1/strategy/analyze?timeframe=1h&limit=200&symbol=btc_usdt"

# 获取策略信号历史
curl -X GET "http://localhost:8000/api/v1/strategy/signals/history?timeframe=1h&days=7"

# 执行策略回测
curl -X GET "http://localhost:8000/api/v1/strategy/backtest?timeframe=1h&days=30&initial_capital=10000"
```

### Python客户端代码片段
```python
import requests
import json

# 基础URL
