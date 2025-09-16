# API参考

<cite>
**本文档中引用的文件**   
- [main.py](file://app/main.py)
- [api.py](file://app/api/v1/api.py)
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py)
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py)
- [kline.py](file://app/api/v1/endpoints/kline.py)
- [config.py](file://app/core/config.py)
- [exceptions.py](file://app/core/exceptions.py)
- [kline_aggregator.py](file://app/services/kline_aggregator.py)
</cite>

## 目录
1. [API版本控制](#api版本控制)
2. [认证与速率限制](#认证与速率限制)
3. [/chan/analyze - 缠论技术分析](#chananalyze---缠论技术分析)
4. [/simple/klines - 获取K线数据](#simpleklines---获取k线数据)
5. [/simple/fetch-data - 手动触发数据获取](#simplefetch-data---手动触发数据获取)
6. [/simple/timeframes - 获取支持的时间周期](#simpletimeframes---获取支持的时间周期)
7. [/simple/latest - 获取最新K线数据](#simplelatest---获取最新k线数据)
8. [/simple/stats - 获取数据库统计信息](#simplestats---获取数据库统计信息)
9. [/simple/health - 健康检查](#simplehealth---健康检查)
10. [错误响应格式](#错误响应格式)

## API版本控制
本系统采用基于URL路径的API版本控制策略，所有公共API端点均位于`/api/v1/`前缀下。该策略通过在`app/main.py`中配置FastAPI应用的`openapi_url`、`docs_url`和`redoc_url`参数实现，确保API文档、交互式文档界面与实际端点保持一致。此设计允许未来在不影响现有客户端的情况下引入`/api/v2/`等新版本。

**Section sources**
- [main.py](file://app/main.py#L15-L25)

## 认证与速率限制
当前API端点为公开访问，无需认证。系统已配置CORS中间件以支持前端开发，允许来自`http://localhost:3000`和`http://localhost:5173`等本地开发服务器的跨域请求。目前未实施速率限制策略，所有端点均可自由调用。

**Section sources**
- [main.py](file://app/main.py#L34-L44)

## /chan/analyze - 缠论技术分析
执行专业的缠论技术分析，自动识别分型、笔、线段和买卖点。

### 端点信息
- **HTTP方法**: `GET`
- **完整URL路径**: `/api/v1/chan/analyze`

### 请求参数
| 参数名 | 位置 | 类型 | 是否必需 | 约束 | 描述 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `timeframe` | 查询参数 | string | 否 | 枚举: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | 分析的时间周期，默认为`1h`。 |
| `limit` | 查询参数 | integer | 否 | 范围: `50` - `500` | 分析的K线数量，默认为`200`。建议200根以上以获得更好的分析效果。 |

### 请求示例
```bash
curl -X GET "http://localhost:8000/api/v1/chan/analyze?timeframe=1h&limit=200"
```

### 成功响应 (HTTP 200)
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "analysis": {
      "fenxings": [
        {
          "timestamp": 1700000000000,
          "price": 35000.5,
          "type": "top",
          "strength": 0.8,
          "confirmed": true
        }
      ],
      "bis": [
        {
          "start": { "timestamp": 1700000000000, "price": 35000.5 },
          "end": { "timestamp": 1700000060000, "price": 34800.0 },
          "direction": "down",
          "length": 60
        }
      ],
      "buy_sell_points": [
        {
          "timestamp": 1700000060000,
          "price": 34800.0,
          "type": "第一类买点",
          "confidence": 0.9
        }
      ],
      "trend": {
        "direction": "down",
        "strength": 0.75
      }
    },
    "metadata": {
      "klines_analyzed": 200,
      "timeframe": "1h",
      "analysis_time": 1700000060000,
      "latest_price": 34800.0,
      "chan_module_available": true,
      "statistics": {
        "fenxings": 15,
        "bis": 8,
        "xianduan": 3,
        "buy_sell_points": 2
      }
    },
    "usage_tips": {
      "fenxings": "🔺红色标记为顶分型，🔻绿色标记为底分型",
      "suggestion": "根据缠论理论生成的操作建议，仅供参考"
    }
  }
}
```

### 错误响应
| HTTP状态码 | 错误信息 | 触发条件 |
| :--- | :--- | :--- |
| `404` | `没有找到K线数据，请先调用 /api/v1/simple/fetch-data 获取数据` | 数据库中不存在指定时间周期的K线数据。 |
| `500` | `分析服务暂时不可用` | 服务器内部处理失败，例如Chan模块分析错误。 |

### Python客户端代码片段
```python
import requests

url = "http://localhost:8000/api/v1/chan/analyze"
params = {
    "timeframe": "1h",
    "limit": 200
}

response = requests.get(url, params=params)
if response.status_code == 200:
    result = response.json()
    analysis = result["data"]["analysis"]
    print(f"分析完成，识别出 {len(analysis['fenxings'])} 个分型")
else:
    print(f"请求失败: {response.json()['message']}")
```

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L34-L102)

## /simple/klines - 获取K线数据
获取聚合后的K线数据，支持多时间周期和时间范围查询。

### 端点信息
- **HTTP方法**: `GET`
- **完整URL路径**: `/api/v1/simple/klines`

### 请求参数
| 参数名 | 位置 | 类型 | 是否必需 | 约束 | 描述 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `timeframe` | 查询参数 | string | 否 | 枚举: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | 目标时间周期，默认为`1h`。 |
| `limit` | 查询参数 | integer | 否 | 范围: `1` - `1000` | 返回的数据条数，默认为`200`。 |
| `start_time` | 查询参数 | string | 否 | ISO 8601 格式 (e.g., `2024-01-01T00:00:00`) | 查询的开始时间。 |
| `end_time` | 查询参数 | string | 否 | ISO 8601 格式 (e.g., `2024-01-01T23:59:59`) | 查询的结束时间。 |

### 请求示例
```bash
curl -X GET "http://localhost:8000/api/v1/simple/klines?timeframe=4h&limit=50&start_time=2024-01-01T00:00:00&end_time=2024-01-07T23:59:59"
```

### 成功响应 (HTTP 200)
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "klines": [
      {
        "timestamp": 1700000000000,
        "open_time": "2023-11-15T00:00:00",
        "close_time": "2023-11-15T00:59:59.999",
        "open_price": "35000.50000000",
        "high_price": "35200.00000000",
        "low_price": "34800.00000000",
        "close_price": "34900.00000000",
        "volume": "100.50000000",
        "quote_volume": "3500000.00000000",
        "trades_count": 150,
        "taker_buy_volume": "55.25000000",
        "taker_buy_quote_volume": "1925000.00000000"
      }
    ],
    "metadata": {
      "count": 1,
      "timeframe": "1h",
      "request_params": {
        "limit": 200,
        "start_time": null,
        "end_time": null
      },
      "data_range": {
        "start": "2023-11-15T00:00:00",
        "end": "2023-11-15T00:59:59.999"
      }
    },
    "database_stats": {
      "total_klines": 10000,
      "date_range": {
        "start": "2023-01-01T00:00:00",
        "end": "2023-12-31T23:59:59"
      },
      "latest_price": 34900.0,
      "data_coverage": "6.9 天"
    }
  }
}
```

### 错误响应
| HTTP状态码 | 错误信息 | 触发条件 |
| :--- | :--- | :--- |
| `400` | `不支持的时间周期: {timeframe}，支持的周期: [1m, 5m, ...]` | `timeframe`参数值不在支持的列表中。 |
| `400` | `开始时间格式错误，请使用ISO格式` | `start_time`参数格式不正确。 |
| `400` | `结束时间格式错误，请使用ISO格式` | `end_time`参数格式不正确。 |
| `400` | `开始时间必须早于结束时间` | `start_time`晚于或等于`end_time`。 |
| `500` | `服务器内部错误` | 服务器在处理请求时发生未知错误。 |

### Python客户端代码片段
```python
import requests
from datetime import datetime

url = "http://localhost:8000/api/v1/simple/klines"
params = {
    "timeframe": "1d",
    "limit": 30,
    "start_time": datetime(2024, 1, 1).isoformat(),
    "end_time": datetime(2024, 1, 30).isoformat()
}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()["data"]
    klines = data["klines"]
    print(f"成功获取 {len(klines)} 条日K线数据")
else:
    print(f"请求失败: {response.json()['message']}")
```

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L40-L140)

## /simple/fetch-data - 手动触发数据获取
手动触发从币安API获取最新的K线数据。

### 端点信息
- **HTTP方法**: `POST`
- **完整URL路径**: `/api/v1/simple/fetch-data`

### 请求参数
无请求体参数。此端点为幂等操作，重复调用会获取相同时间范围内的最新数据。

### 请求示例
```bash
curl -X POST "http://localhost:8000/api/v1/simple/fetch-data"
```

### 成功响应 (HTTP 200)
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "status": "success",
    "hours_fetched": 2,
    "note": "数据已更新，建议等待2-3秒后重新查询K线数据",
    "next_steps": [
      "等待2-3秒让数据写入完成",
      "调用 /api/v1/simple/klines 查看新数据",
      "调用 /api/v1/chan/analyze 进行缠论分析"
    ]
  }
}
```

### 错误响应
| HTTP状态码 | 错误信息 | 触发条件 |
| :--- | :--- | :--- |
| `500` | `数据获取失败: {error_message}` | 从币安API获取数据失败或数据写入数据库时出错。 |

### Python客户端代码片段
```python
import requests
import time

url = "http://localhost:8000/api/v1/simple/fetch-data"

response = requests.post(url)
if response.status_code == 200:
    print("数据获取任务已成功触发")
    # 建议等待数据写入完成
    time.sleep(3)
else:
    print(f"数据获取失败: {response.json()['message']}")
```

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L142-L178)

## /simple/timeframes - 获取支持的时间周期
获取系统支持的所有K线时间周期列表。

### 端点信息
- **HTTP方法**: `GET`
- **完整URL路径**: `/api/v1/simple/timeframes`

### 请求参数
无。

### 请求示例
```bash
curl -X GET "http://localhost:8000/api/v1/simple/timeframes"
```

### 成功响应 (HTTP 200)
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
    "description": {
      "1m": "1分钟",
      "5m": "5分钟",
      "15m": "15分钟",
      "30m": "30分钟",
      "1h": "1小时",
      "4h": "4小时",
      "1d": "1天"
    },
    "note": "系统自动将1分钟K线聚合为其他时间周期"
  }
}
```

### 错误响应
| HTTP状态码 | 错误信息 | 触发条件 |
| :--- | :--- | :--- |
| `500` | `获取时间周期失败` | 服务器内部错误。 |

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L22-L38)

## /simple/latest - 获取最新K线数据
获取指定时间周期的最新K线数据。

### 端点信息
- **HTTP方法**: `GET`
- **完整URL路径**: `/api/v1/simple/latest`

### 请求参数
| 参数名 | 位置 | 类型 | 是否必需 | 约束 | 描述 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `timeframe` | 查询参数 | string | 否 | 枚举: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | 时间周期，默认为`1h`。 |
| `count` | 查询参数 | integer | 否 | 范围: `1` - `500` | 返回的最新数据条数，默认为`100`。 |

### 请求示例
```bash
curl -X GET "http://localhost:8000/api/v1/simple/latest?timeframe=15m&count=50"
```

### 成功响应 (HTTP 200)
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "klines": [...],
    "metadata": {
      "count": 50,
      "timeframe": "15m",
      "is_latest": true,
      "latest_timestamp": 1700000000000,
      "last_update": "2023-11-15T00:00:00"
    }
  }
}
```

### 错误响应
| HTTP状态码 | 错误信息 | 触发条件 |
| :--- | :--- | :--- |
| `500` | `获取最新数据失败` | 服务器内部错误。 |

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L180-L207)

## /simple/stats - 获取数据库统计信息
获取K线数据的数据库统计信息。

### 端点信息
- **HTTP方法**: `GET`
- **完整URL路径**: `/api/v1/simple/stats`

### 请求参数
无。

### 请求示例
```bash
curl -X GET "http://localhost:8000/api/v1/simple/stats"
```

### 成功响应 (HTTP 200)
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "statistics": {
      "total_klines": 10000,
      "date_range": {
        "start": "2023-01-01T00:00:00",
        "end": "2023-12-31T23:59:59"
      },
      "latest_price": 34900.0,
      "data_coverage": "6.9 天"
    },
    "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
    "aggregation_info": {
      "source": "1分钟K线数据",
      "method": "pandas.resample聚合",
      "supported_operations": ["开盘价(first)", "最高价(max)", "最低价(min)", "收盘价(last)", "成交量(sum)"]
    }
  }
}
```

### 错误响应
| HTTP状态码 | 错误信息 | 触发条件 |
| :--- | :--- | :--- |
| `500` | `获取统计信息失败` | 服务器内部错误。 |

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L209-L235)

## /simple/health - 健康检查
检查K线API和数据库的健康状态。

### 端点信息
- **HTTP方法**: `GET`
- **完整URL路径**: `/api/v1/simple/health`

### 请求参数
无。

### 请求示例
```bash
curl -X GET "http://localhost:8000/api/v1/simple/health"
```

### 成功响应 (HTTP 200)
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "status": "healthy",
    "components": {
      "database": "connected",
      "kline_aggregator": "ready",
      "data_available": true,
      "data_freshness": "fresh"
    },
    "statistics": {
      "total_klines": 10000,
      "date_range": {
        "start": "2023-01-01T00:00:00",
        "end": "2023-12-31T23:59:59"
      },
      "latest_price": 34900.0
    },
    "recommendations": "数据是最新的，可以进行分析"
  }
}
```

### 错误响应
| HTTP状态码 | 错误信息 | 触发条件 |
| :--- | :--- | :--- |
| `500` | `健康检查失败` | 服务器内部错误，例如数据库连接失败。 |

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L237-L259)

## 错误响应格式
所有API端点遵循统一的错误响应格式，便于客户端解析。

### 通用错误响应结构
```json
{
  "success": false,
  "code": <错误代码>,
  "message": "<错误信息>",
  "data": null
}
```

### 错误代码与信息
| 错误代码 | HTTP状态码 | 错误信息 | 说明 |
| :--- | :--- | :--- | :--- |
| `0` | `200` | `success` | 成功响应，非错误。 |
| `2001` | `400` | `不支持的交易品种: {symbol}` | 请求了不支持的交易对。 |
| `2002` | `404` | `K线数据不存在` | 根据ID或时间戳查询的数据不存在。 |
| `3000` | `422` | `数据验证失败` | Pydantic模型验证失败。 |
| `1001` | `500` | `数据库操作失败` | SQLAlchemy数据库操作异常。 |
| `1000` | `500` | `服务器内部错误` | 未捕获的通用异常。 |

**Section sources**
- [exceptions.py](file://app/core/exceptions.py#L67-L103)
- [exceptions.py](file://app/core/exceptions.py#L34-L69)
- [exceptions.py](file://app/core/exceptions.py#L0-L37)