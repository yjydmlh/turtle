# 简化K线操作API

<cite>
**本文档引用的文件**  
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py)
- [kline_aggregator.py](file://app/services/kline_aggregator.py)
- [simple_fetch_data.py](file://app/scripts/simple_fetch_data.py)
- [exceptions.py](file://app/core/exceptions.py)
- [kline.py](file://app/models/kline.py)
- [api.js](file://frontend/src/lib/api.js)
</cite>

## 目录
1. [简介](#简介)
2. [/simple/klines 端点](#simpleklines-端点)
3. [/simple/fetch-data 端点](#simplefetch-data-端点)
4. [/simple/health 端点](#simplehealth-端点)
5. [/simple/latest 端点](#simplelatest-端点)
6. [/simple/timeframes 端点](#simpletimeframes-端点)
7. [/simple/stats 端点](#simplestats-端点)
8. [请求示例](#请求示例)
9. [错误码说明](#错误码说明)
10. [数据新鲜度判断逻辑](#数据新鲜度判断逻辑)

## 简介
本API提供简化的K线数据访问接口，支持多时间周期聚合、手动数据拉取和系统健康检查。所有端点均位于 `/api/v1/simple` 路径下，基于1分钟原始K线数据通过聚合算法生成更长周期的K线。

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L1-L20)

## /simple/klines 端点

### 基本信息
- **HTTP方法**: `GET`
- **完整路径**: `/api/v1/simple/klines`

### 请求参数
| 参数名 | 类型 | 必填 | 描述 | 约束 |
|-------|------|------|------|------|
| `timeframe` | 字符串 | 是 | 时间周期 | 必须为 `1m,5m,15m,30m,1h,4h,1d` 之一 |
| `limit` | 整数 | 否 | 返回数据条数 | 范围：1-1000，默认200 |
| `start_time` | 字符串 | 否 | 开始时间 | ISO 8601格式，如 `2024-01-01T00:00:00` |
| `end_time` | 字符串 | 否 | 结束时间 | ISO 8601格式，如 `2024-01-01T23:59:59` |

### 请求示例
```http
GET /api/v1/simple/klines?timeframe=1h&limit=100&start_time=2024-01-01T00:00:00
```

### 成功响应JSON Schema
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "klines": [
      {
        "timestamp": 1704067200000,
        "open_time": "2024-01-01T00:00:00",
        "close_time": "2024-01-01T00:59:59",
        "open_price": "43000.00000000",
        "high_price": "43500.00000000",
        "low_price": "42800.00000000",
        "close_price": "43200.00000000",
        "volume": "100.50000000",
        "quote_volume": "4325000.00000000",
        "trades_count": 150,
        "taker_buy_volume": "55.25000000",
        "taker_buy_quote_volume": "2375000.00000000"
      }
    ],
    "metadata": {
      "count": 100,
      "timeframe": "1h",
      "request_params": {
        "limit": 100,
        "start_time": "2024-01-01T00:00:00",
        "end_time": null
      },
      "data_range": {
        "start": "2024-01-01T00:00:00",
        "end": "2024-01-05T03:59:59"
      }
    },
    "database_stats": {
      "total_klines": 50000,
      "date_range": {
        "start": "2023-12-01T00:00:00",
        "end": "2024-01-05T04:59:59"
      },
      "latest_price": 43200.0,
      "data_coverage": "35.0 天"
    }
  }
}
```

### 可能的HTTP状态码
- `200 OK`: 请求成功
- `400 Bad Request`: 参数错误（如无效时间周期、时间格式错误、开始时间不早于结束时间）
- `500 Internal Server Error`: 服务器内部错误

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L25-L135)

## /simple/fetch-data 端点

### 基本信息
- **HTTP方法**: `POST`
- **完整路径**: `/api/v1/simple/fetch-data`

### 请求参数
无请求体参数，通过调用触发数据拉取。

### 请求示例
```http
POST /api/v1/simple/fetch-data
```

### 成功响应JSON Schema
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

### 失败响应JSON Schema
```json
{
  "success": false,
  "code": 5001,
  "message": "数据获取失败",
  "data": null
}
```

### 可能的HTTP状态码
- `200 OK`: 数据获取任务已成功触发
- `500 Internal Server Error`: 数据获取失败

### 异步特性说明
该端点为异步操作：
1. 调用后立即返回结果，表示任务已提交
2. 实际数据拉取在后台执行，耗时约数秒
3. **强烈建议**调用后等待 **2-3秒** 再查询新数据
4. 可通过 `/simple/health` 或 `/simple/stats` 检查数据更新状态

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L137-L184)
- [simple_fetch_data.py](file://app/scripts/simple_fetch_data.py#L50-L150)

## /simple/health 端点

### 基本信息
- **HTTP方法**: `GET`
- **完整路径**: `/api/v1/simple/health`

### 请求参数
无

### 请求示例
```http
GET /api/v1/simple/health
```

### 成功响应JSON Schema
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
      "total_klines": 50000,
      "date_range": {
        "start": "2023-12-01T00:00:00",
        "end": "2024-01-05T04:59:59"
      },
      "latest_price": 43200.0,
      "data_coverage": "35.0 天"
    },
    "recommendations": "数据是最新的，可以进行分析"
  }
}
```

### `data_freshness` 状态说明
- `"fresh"`: 最新数据在1小时内
- `"recent"`: 最新数据在1-24小时内
- `"stale"`: 最新数据超过24小时
- `"unknown"`: 无任何数据

### 可能的HTTP状态码
- `200 OK`: 健康检查成功
- `500 Internal Server Error`: 健康检查失败（如数据库连接异常）

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L230-L259)

## /simple/latest 端点

### 基本信息
- **HTTP方法**: `GET`
- **完整路径**: `/api/v1/simple/latest`

### 请求参数
| 参数名 | 类型 | 必填 | 描述 | 约束 |
|-------|------|------|------|------|
| `timeframe` | 字符串 | 否 | 时间周期 | 同 `/klines`，默认 `1h` |
| `count` | 整数 | 否 | 返回最新数据条数 | 范围：1-500，默认100 |

### 成功响应JSON Schema
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "klines": [/* K线数据数组 */],
    "metadata": {
      "count": 100,
      "timeframe": "1h",
      "is_latest": true,
      "latest_timestamp": 1704451200000,
      "last_update": "2024-01-05T05:20:00"
    }
  }
}
```

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L186-L208)

## /simple/timeframes 端点

### 基本信息
- **HTTP方法**: `GET`
- **完整路径**: `/api/v1/simple/timeframes`

### 成功响应JSON Schema
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

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L1-L23)

## /simple/stats 端点

### 基本信息
- **HTTP方法**: `GET`
- **完整路径**: `/api/v1/simple/stats`

### 成功响应JSON Schema
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": {
    "statistics": {
      "total_klines": 50000,
      "date_range": {
        "start": "2023-12-01T00:00:00",
        "end": "2024-01-05T04:59:59"
      },
      "latest_price": 43200.0,
      "data_coverage": "35.0 天"
    },
    "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
    "aggregation_info": {
      "source": "1分钟K线数据",
      "method": "pandas.resample聚合",
      "supported_operations": [
        "开盘价(first)",
        "最高价(max)",
        "最低价(min)",
        "收盘价(last)",
        "成交量(sum)"
      ]
    }
  }
}
```

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L210-L228)

## 请求示例

### curl 命令行示例

#### 获取1小时K线数据
```bash
curl -X GET "http://localhost:8000/api/v1/simple/klines?timeframe=1h&limit=50"
```

#### 获取指定时间范围的30分钟K线
```bash
curl -X GET "http://localhost:8000/api/v1/simple/klines?timeframe=30m&limit=100&start_time=2024-01-01T00:00:00&end_time=2024-01-02T00:00:00"
```

#### 手动触发数据拉取
```bash
curl -X POST "http://localhost:8000/api/v1/simple/fetch-data"
```

#### 检查系统健康状态
```bash
curl -X GET "http://localhost:8000/api/v1/simple/health"
```

### Python 客户端代码片段

```python
import requests
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api/v1"

def get_klines(timeframe="1h", limit=200, start_time=None, end_time=None):
    """获取K线数据"""
    params = {
        "timeframe": timeframe,
        "limit": limit
    }
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    
    response = requests.get(f"{BASE_URL}/simple/klines", params=params)
    return response.json()

def fetch_new_data():
    """手动获取新数据"""
    response = requests.post(f"{BASE_URL}/simple/fetch-data")
    result = response.json()
    
    if result["success"]:
        print("数据获取成功，等待3秒...")
        time.sleep(3)  # 等待数据写入
        return True
    else:
        print(f"数据获取失败: {result['message']}")
        return False

def check_health():
    """检查系统健康状态"""
    response = requests.get(f"{BASE_URL}/simple/health")
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 1. 获取最新1小时K线
    klines_data = get_klines(timeframe="1h", limit=10)
    print(f"获取到 {len(klines_data['data']['klines'])} 条K线数据")

    # 2. 触发数据更新
    if fetch_new_data():
        # 3. 获取更新后的数据
        updated_data = get_klines(timeframe="1h", limit=10)
        print("数据已更新")

    # 4. 检查系统状态
    health = check_health()
    print(f"系统状态: {health['data']['status']}")
    print(f"数据新鲜度: {health['data']['components']['data_freshness']}")
    print(f"建议: {health['data']['recommendations']}")
```

**Section sources**
- [api.js](file://frontend/src/lib/api.js#L85-L176)
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py)

## 错误码说明

| HTTP状态码 | 错误码 | 错误信息 | 说明 |
|-----------|--------|---------|------|
| 400 | 2001 | 不支持的时间周期 | `timeframe` 参数值不在支持列表中 |
| 400 | - | 开始时间必须早于结束时间 | `start_time` >= `end_time` |
| 400 | - | 开始时间格式错误 | `start_time` 不符合ISO 8601格式 |
| 400 | - | 结束时间格式错误 | `end_time` 不符合ISO 8601格式 |
| 500 | 5001 | 数据获取失败 | `/fetch-data` 执行失败 |
| 500 | 1001 | 数据库操作失败 | 数据库连接或查询异常 |
| 500 | - | 服务器内部错误 | 其他未预期的服务器错误 |

**Section sources**
- [exceptions.py](file://app/core/exceptions.py#L0-L110)
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py)

## 数据新鲜度判断逻辑

系统通过以下逻辑判断数据新鲜度：

1. **获取最新K线时间戳**：查询数据库中最新的K线记录的时间戳
2. **计算时间差**：
   - 与当前时间比较，计算相差的秒数
3. **判断状态**：
   ```python
   if time_diff < 3600:       # 1小时内
       freshness = "fresh"
   elif time_diff < 86400:    # 24小时内
       freshness = "recent"
   else:                      # 超过24小时
       freshness = "stale"
   ```
4. **返回建议**：根据新鲜度状态返回相应的操作建议

此逻辑在 `/simple/health` 端点中实现，用于指导用户是否需要调用 `/fetch-data` 更新数据。

**Section sources**
- [kline_simple.py](file://app/api/v1/endpoints/kline_simple.py#L237-L259)
- [kline_aggregator.py](file://app/services/kline_aggregator.py#L230-L240)