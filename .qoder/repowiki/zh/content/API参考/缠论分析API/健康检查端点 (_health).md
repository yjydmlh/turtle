# 健康检查端点 (/health)

<cite>
**本文档中引用的文件**   
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py)
- [chan_adapter.py](file://app/services/chan_adapter.py)
</cite>

## 目录
1. [简介](#简介)
2. [端点详情](#端点详情)
3. [健康状态数据结构](#健康状态数据结构)
4. [响应JSON Schema示例](#响应json-schema示例)
5. [系统监控与运维](#系统监控与运维)
6. [curl命令行示例](#curl命令行示例)
7. [Prometheus监控集成](#prometheus监控集成)

## 简介
`/api/v1/chan/health` 端点用于检查缠论分析模块的运行状态和可用性。该端点是系统监控和运维的关键组成部分，通过返回详细的健康状态信息，帮助运维人员快速判断缠论模块是否正确加载和可用。此端点通过调用 `chan_adapter.get_chan_info()` 方法获取模块信息，并根据 `is_available` 标志判断服务的整体状态。

## 端点详情
- **HTTP方法**: GET
- **完整URL路径**: `/api/v1/chan/health`
- **功能**: 检查缠论分析模块的健康状态
- **用途**: 系统监控、服务可用性检查、运维诊断

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L392-L420)

## 健康状态数据结构
健康检查端点返回一个包含多个维度信息的JSON对象，详细描述了系统的整体状态。

### 整体状态
- `status`: 字符串，表示整体健康状态。可能值为 `"healthy"`（健康）或 `"degraded"`（降级）。当 `chan_adapter.is_available` 为 `True` 时，状态为 `"healthy"`；否则为 `"degraded"`。

### 组件状态
- `components`: 对象，描述各个组件的状态。
  - `chan_adapter`: 字符串，值为 `"ready"`，表示适配器已准备就绪。
  - `chan_module`: 字符串，值为 `"loaded"`（已加载）或 `"missing"`（缺失），根据 `chan_info["module_loaded"]` 的值确定。
  - `analysis_capability`: 字符串，值为 `"full"`（完整）或 `"fallback"`（后备），根据 `chan_info["is_available"]` 的值确定。

### 功能可用性
- `features`: 对象，描述各项缠论分析功能的可用性。
  - `fenxing_recognition`: 布尔值，始终为 `True`，表示分型识别功能存在。
  - `bi_construction`: 布尔值，根据 `chan_info["is_available"]` 的值确定，表示笔构建功能是否可用。
  - `xianduan_analysis`: 布尔值，根据 `chan_info["is_available"]` 的值确定，表示线段分析功能是否可用。
  - `buy_sell_points`: 布尔值，根据 `chan_info["is_available"]` 的值确定，表示买卖点识别功能是否可用。

### 性能建议
- `performance`: 对象，提供性能相关的建议和信息。
  - `analysis_mode`: 字符串，值为 `"chan_module"`（使用完整模块）或 `"fallback"`（使用后备模式），根据 `chan_info["is_available"]` 的值确定。
  - `recommended_data_size`: 字符串，建议的K线数据量，值为 `"200+ K线获得最佳效果"`。
  - `supported_timeframes`: 数组，由 `kline_aggregator.get_available_timeframes()` 方法返回，列出所有支持的时间周期。

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L392-L420)
- [chan_adapter.py](file://app/services/chan_adapter.py#L205-L239)

## 响应JSON Schema示例
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
      "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    }
  }
}
```

## 系统监控与运维
该端点主要用于系统监控和运维，通过定期调用可以检查缠论模块是否正确加载和可用。其工作原理如下：

1. **获取模块信息**: 调用 `chan_adapter.get_chan_info()` 方法获取Chan模块的详细信息。
2. **判断服务状态**: 根据返回信息中的 `is_available` 标志来判断服务的整体状态。
3. **返回健康状态**: 构建并返回一个包含整体状态、组件状态、功能可用性和性能建议的JSON对象。

如果Chan模块不可用，系统将自动切换到简化分析模式，确保服务的可用性。

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L392-L420)
- [chan_adapter.py](file://app/services/chan_adapter.py#L205-L239)

## curl命令行示例
```bash
curl -X GET "http://localhost:8000/api/v1/chan/health"
```

## Prometheus监控集成
可以将此健康检查端点集成到Prometheus监控体系中，用于系统告警。建议的集成方式如下：

1. **创建Prometheus Job**: 在Prometheus配置文件中添加一个新的job，定期抓取 `/api/v1/chan/health` 端点。
2. **定义告警规则**: 基于返回的 `status` 字段定义告警规则。例如，当 `status` 为 `"degraded"` 时触发告警。
3. **集成到告警体系**: 将告警规则与Alertmanager集成，实现邮件、短信等多渠道告警通知。

通过这种方式，可以实时监控缠论分析模块的健康状态，及时发现并处理潜在问题。

**Section sources**
- [chan_analysis.py](file://app/api/v1/endpoints/chan_analysis.py#L392-L420)
- [chan_adapter.py](file://app/services/chan_adapter.py#L205-L239)