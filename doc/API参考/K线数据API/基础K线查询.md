# 基础K线查询

<cite>
**本文档引用文件**  
- [kline.py](file://app/api/v1/endpoints/kline.py)
- [kline.py](file://app/crud/kline.py)
- [kline.py](file://app/models/kline.py)
- [kline.py](file://app/schemas/kline.py)
- [exceptions.py](file://app/core/exceptions.py)
- [logger.py](file://app/core/logger.py)
</cite>

## 目录
1. [简介](#简介)
2. [API端点概览](#api端点概览)
3. [端点详细说明](#端点详细说明)
4. [请求示例](#请求示例)
5. [响应结构](#响应结构)
6. [参数校验与错误处理](#参数校验与错误处理)
7. [分页与性能建议](#分页与性能建议)
8. [调试与日志](#调试与日志)

## 简介
本文档详细说明了交易系统中用于查询K线数据的基础API接口。这些接口提供非聚合型K线数据访问能力，支持按交易对、ID、时间戳和时间范围等多种方式查询。所有接口均基于FastAPI框架实现，具备统一的错误处理和日志记录机制。

## API端点概览
以下为支持的基础K线查询端点：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/kline/{symbol}/` | GET | 获取指定交易对的K线列表 |
| `/kline/{symbol}/{id}` | GET | 根据ID查询单条K线数据 |
| `/kline/{symbol}/timestamp/{timestamp}` | GET | 根据时间戳查询K线数据 |
| `/kline/{symbol}/time-range/` | GET | 查询指定时间范围内的K线数据 |

**Section sources**
- [kline.py](file://app/api/v1/endpoints/kline.py#L35-L194)

## 端点详细说明

### 获取K线列表
```http
GET /kline/{symbol}/
```
获取指定交易对的K线数据列表。

**路径参数**  
- `symbol`: 交易对标识符，如 `btc_usdt`、`eth_usdt`

**查询参数**  
- `skip`: 跳过的记录数，取值范围 ≥ 0，默认为 0
- `limit`: 返回记录数限制，取值范围 1-1000，默认为 100

**Section sources**
- [kline.py](file://app/api/v1/endpoints/kline.py#L35-L45)

### 按ID查询K线
```http
GET /kline/{symbol}/{id}
```
根据主键ID获取单条K线数据。

**路径参数**  
- `symbol`: 交易对标识符
- `id`: K线记录的唯一标识ID

**Section sources**
- [kline.py](file://app/api/v1/endpoints/kline.py#L47-L57)

### 按时间戳查询K线
```http
GET /kline/{symbol}/timestamp/{timestamp}
```
根据时间戳获取对应的K线数据。

**路径参数**  
- `symbol`: 交易对标识符
- `timestamp`: 时间戳（毫秒级）

**Section sources**
- [kline.py](file://app/api/v1/endpoints/kline.py#L59-L69)

### 按时间范围查询K线
```http
GET /kline/{symbol}/time-range/
```
获取指定时间范围内的K线数据。

**路径参数**  
- `symbol`: 交易对标识符

**查询参数**  
- `start_time`: 开始时间（ISO 8601格式）
- `end_time`: 结束时间（ISO 8601格式）

**Section sources**
- [kline.py](file://app/api/v1/endpoints/kline.py#L71-L81)

## 请求示例

### cURL 示例
```bash
# 获取BTC/USDT最近100条K线
curl -X GET "http://localhost:8000/kline/btc_usdt/?skip=0&limit=100"

# 按ID查询K线
curl -X GET "http://localhost:8000/kline/btc_usdt/12345"

# 按时间戳查询
curl -X GET "http://localhost:8000/kline/btc_usdt/timestamp/1700000000000"

# 按时间范围查询
curl -X GET "http://localhost:8000/kline/btc_usdt/time-range/?start_time=2024-01-01T00:00:00&end_time=2024-01-02T00:00:00"
```

### Python requests 示例
```python
import requests
from datetime import datetime

base_url = "http://localhost:8000/kline"

# 获取K线列表
response = requests.get(f"{base_url}/btc_usdt/", params={"skip": 0, "limit": 50})

# 按ID查询
response = requests.get(f"{base_url}/btc_usdt/12345")

# 按时间戳查询
response = requests.get(f"{base_url}/btc_usdt/timestamp/1700000000000")

# 按时间范围查询
start_time = datetime(2024, 1, 1)
end_time = datetime(2024, 1, 2)
response = requests.get(
    f"{base_url}/btc_usdt/time-range/",
    params={"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
)
```

**Section sources**
- [kline.py](file://app/api/v1/endpoints/kline.py#L35-L194)

## 响应结构
所有成功响应均遵循统一格式：
```json
{
  "success": true,
  "code": 0,
  "message": "success",
  "data": [...]
}
```

**K线数据字段说明**  
- `id`: 主键ID
- `timestamp`: K线开始时间戳（毫秒）
- `open_time`: 开盘时间
- `close_time`: 收盘时间
- `open_price`: 开盘价
- `high_price`: 最高价
- `low_price`: 最低价
- `close_price`: 收盘价
- `volume`: 成交量
- `quote_volume`: 成交额
- `trades_count`: 成交笔数
- `taker_buy_volume`: 主动买入成交量
- `taker_buy_quote_volume`: 主动买入成交额
- `created_at`: 数据创建时间
- `updated_at`: 数据更新时间

**Section sources**
- [kline.py](file://app/crud/kline.py#L86-L114)
- [kline.py](file://app/schemas/kline.py#L1-L30)

## 参数校验与错误处理

### symbol参数校验
系统通过 `SYMBOL_TO_MODEL` 映射表校验交易对支持情况：
```python
SYMBOL_TO_MODEL = {
    "btc_usdt": BtcUsdtKline,
    "eth_usdt": EthUsdtKline,
}
```
不支持的交易对将返回 `InvalidParameterException`。

### 错误处理机制
| 异常类型 | HTTP状态码 | 错误码 | 说明 |
|---------|-----------|--------|------|
| InvalidParameterException | 400 | 2001 | 参数无效（如symbol不支持） |
| ResourceNotFoundException | 404 | 2002 | 资源不存在（如ID或时间戳无匹配数据） |

**错误响应示例**  
```json
{
  "success": false,
  "code": 2001,
  "message": "不支持的交易品种: invalid_symbol",
  "data": null
}
```

**Section sources**
- [kline.py](file://app/api/v1/endpoints/kline.py#L39-L41)
- [exceptions.py](file://app/core/exceptions.py#L1-L111)

## 分页与性能建议

### 分页参数最佳实践
- `skip` 和 `limit` 参数用于实现分页
- 建议 `limit` 值不超过 500 以保证响应性能
- 大数据量查询应结合时间范围参数使用

### 时间范围查询性能
- 时间范围查询会扫描指定区间内所有记录
- 长时间跨度查询可能影响性能
- 建议：
  - 限制单次查询时间跨度不超过7天
  - 对历史数据使用异步导出接口
  - 频繁查询可考虑添加缓存层

**Section sources**
- [kline.py](file://app/crud/kline.py#L116-L134)
- [kline.py](file://app/api/v1/endpoints/kline.py#L71-L81)

## 调试与日志
系统使用 `app_logger` 记录所有K线查询操作：

**日志级别说明**  
- `DEBUG`: 记录查询参数和结果数量
- `INFO`: 记录重要操作（如聚合查询）
- `WARNING`: 记录未找到数据的情况
- `ERROR`: 记录异常和错误

**典型日志输出**  
```
DEBUG:app:Fetching kline data for symbol: btc_usdt, skip: 0, limit: 100
DEBUG:app:Successfully fetched 100 kline records
WARNING:app:Kline data not found for symbol: btc_usdt, id: 99999
```

开发者可通过查看 `logs/app.log` 文件进行问题排查。

**Section sources**
- [logger.py](file://app/core/logger.py#L1-L45)
- [kline.py](file://app/api/v1/endpoints/kline.py#L36-L194)