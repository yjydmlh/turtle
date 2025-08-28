// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE_URL}/api/v1`;

// 请求超时时间（毫秒）
const REQUEST_TIMEOUT = 30000;

// =============================================================================
// HTTP请求工具函数
// =============================================================================

class ApiError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

// 基础请求函数
async function request(url, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            },
            signal: controller.signal
        };

        const response = await fetch(url, config);
        clearTimeout(timeoutId);

        // 检查响应状态
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            let errorData = null;

            try {
                errorData = await response.json();
                errorMessage = errorData.message || errorMessage;
            } catch {
                errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            }

            throw new ApiError(errorMessage, response.status, errorData);
        }

        // 解析响应
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }

        return await response.text();

    } catch (error) {
        clearTimeout(timeoutId);

        if (error.name === 'AbortError') {
            throw new ApiError('请求超时', 408);
        }

        if (error instanceof ApiError) {
            throw error;
        }

        // 网络错误
        throw new ApiError(`网络错误: ${error.message}`, 0);
    }
}

// GET请求
async function get(endpoint, params = {}) {
    const url = new URL(endpoint, API_V1);

    // 添加查询参数
    Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
            url.searchParams.append(key, value);
        }
    });

    return await request(url.toString(), {
        method: 'GET'
    });
}

// POST请求
async function post(endpoint, data = {}) {
    return await request(`${API_V1}${endpoint}`, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// PUT请求
async function put(endpoint, data = {}) {
    return await request(`${API_V1}${endpoint}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// DELETE请求
async function del(endpoint) {
    return await request(`${API_V1}${endpoint}`, {
        method: 'DELETE'
    });
}

// =============================================================================
// K线数据相关API
// =============================================================================

// 获取支持的时间周期
export async function getTimeframes() {
    return await get('/simple/timeframes');
}

// 获取K线数据
export async function getKlines(timeframe = '1h', limit = 200, startTime = null, endTime = null) {
    const params = {
        timeframe,
        limit
    };

    if (startTime) params.start_time = startTime;
    if (endTime) params.end_time = endTime;

    return await get('/simple/klines', params);
}

// 获取最新K线数据
export async function getLatestKlines(timeframe = '1h', count = 100) {
    return await get('/simple/latest', {
        timeframe,
        count
    });
}

// 获取数据统计信息
export async function getDataStatistics() {
    return await get('/simple/stats');
}

// 手动获取新数据
export async function fetchNewData() {
    return await post('/simple/fetch-data');
}

// 健康检查 - K线API
export async function checkKlineHealth() {
    return await get('/simple/health');
}

// =============================================================================
// 缠论分析相关API
// =============================================================================

// 获取Chan模块信息
export async function getChanModuleInfo() {
    return await get('/chan/info');
}

// 执行缠论分析
export async function analyzeChan(timeframe = '1h', limit = 200) {
    return await get('/chan/analyze', {
        timeframe,
        limit
    });
}

// 获取图表数据（包含分析结果）
export async function loadChartData(timeframe = '1h', limit = 100, includeAnalysis = true) {
    return await get('/chan/chart-data', {
        timeframe,
        limit,
        include_analysis: includeAnalysis
    });
}

// 获取分析摘要
export async function getAnalysisSummary(timeframe = '1h') {
    return await get('/chan/summary', {
        timeframe
    });
}

// 仅获取分型数据
export async function getFenxingsOnly(timeframe = '1h', limit = 200) {
    return await get('/chan/fenxings', {
        timeframe,
        limit
    });
}

// 健康检查 - 缠论分析
export async function checkChanHealth() {
    return await get('/chan/health');
}

// =============================================================================
// 系统状态API
// =============================================================================

// 系统健康检查
export async function checkSystemHealth() {
    return await request(`${API_BASE_URL}/health`, {
        method: 'GET'
    });
}

// 获取系统信息
export async function getSystemInfo() {
    return await request(`${API_BASE_URL}/`, {
        method: 'GET'
    });
}

// =============================================================================
// 数据处理和缓存
// =============================================================================

// 内存缓存
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5分钟

// 缓存键生成
function getCacheKey(endpoint, params) {
    const paramStr = Object.entries(params || {})
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => `${k}=${v}`)
        .join('&');
    return `${endpoint}?${paramStr}`;
}

// 带缓存的GET请求
export async function getCached(endpoint, params = {}, cacheDuration = CACHE_DURATION) {
    const cacheKey = getCacheKey(endpoint, params);
    const cached = cache.get(cacheKey);

    // 检查缓存是否有效
    if (cached && (Date.now() - cached.timestamp) < cacheDuration) {
        return cached.data;
    }

    // 获取新数据
    const data = await get(endpoint, params);

    // 缓存数据
    cache.set(cacheKey, {
        data,
        timestamp: Date.now()
    });

    return data;
}

// 清除缓存
export function clearCache(pattern = null) {
    if (!pattern) {
        cache.clear();
        return;
    }

    // 按模式清除
    for (const key of cache.keys()) {
        if (key.includes(pattern)) {
            cache.delete(key);
        }
    }
}

// =============================================================================
// 批量操作和组合API
// =============================================================================

// 加载完整的市场数据（K线 + 分析）
export async function loadCompleteMarketData(timeframe = '1h', limit = 200) {
    try {
        // 并行请求多个API
        const [klineResponse, analysisResponse, summaryResponse] = await Promise.allSettled([
            getKlines(timeframe, limit),
            analyzeChan(timeframe, limit),
            getAnalysisSummary(timeframe)
        ]);

        const result = {
            success: true,
            data: {}
        };

        // 处理K线数据
        if (klineResponse.status === 'fulfilled' && klineResponse.value.success) {
            result.data.klines = klineResponse.value.data.klines;
            result.data.metadata = klineResponse.value.data.metadata;
        }

        // 处理分析数据
        if (analysisResponse.status === 'fulfilled' && analysisResponse.value.success) {
            result.data.analysis = analysisResponse.value.data.analysis;
        }

        // 处理摘要数据
        if (summaryResponse.status === 'fulfilled' && summaryResponse.value.success) {
            result.data.summary = summaryResponse.value.data;
        }

        // 检查关键数据是否存在
        if (!result.data.klines) {
            result.success = false;
            result.error = '无法获取K线数据';
        }

        return result;

    } catch (error) {
        return {
            success: false,
            error: error.message,
            data: {}
        };
    }
}

// 批量健康检查
export async function performHealthCheck() {
    try {
        const [systemHealth, klineHealth, chanHealth] = await Promise.allSettled([
            checkSystemHealth(),
            checkKlineHealth(),
            checkChanHealth()
        ]);

        return {
            system: systemHealth.status === 'fulfilled' ? systemHealth.value : { status: 'error' },
            klineApi: klineHealth.status === 'fulfilled' ? klineHealth.value : { status: 'error' },
            chanAnalysis: chanHealth.status === 'fulfilled' ? chanHealth.value : { status: 'error' },
            timestamp: new Date().toISOString()
        };

    } catch (error) {
        return {
            error: error.message,
            timestamp: new Date().toISOString()
        };
    }
}

// =============================================================================
// 实时数据更新
// =============================================================================

// WebSocket连接管理
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.listeners = new Map();
    }

    connect(url = null) {
        const wsUrl = url || `ws://localhost:8001/ws`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket连接已建立');
                this.reconnectAttempts = 0;
                this.emit('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.emit('data', data);
                } catch (error) {
                    console.error('WebSocket消息解析错误:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this.emit('error', error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket连接已关闭');
                this.emit('disconnected');
                this.attemptReconnect();
            };

        } catch (error) {
            console.error('WebSocket连接失败:', error);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    emit(event, data) {
        const callbacks = this.listeners.get(event);
        if (callbacks) {
            callbacks.forEach(callback => callback(data));
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }
}

// 创建WebSocket管理器实例
export const wsManager = new WebSocketManager();

// =============================================================================
// 错误处理和重试机制
// =============================================================================

// 带重试的请求
export async function requestWithRetry(requestFn, maxRetries = 3, retryDelay = 1000) {
    let lastError;

    for (let i = 0; i <= maxRetries; i++) {
        try {
            return await requestFn();
        } catch (error) {
            lastError = error;

            // 最后一次尝试，不再重试
            if (i === maxRetries) {
                break;
            }

            // 某些错误不需要重试
            if (error.status >= 400 && error.status < 500) {
                break;
            }

            console.warn(`请求失败，${retryDelay}ms后重试 (${i + 1}/${maxRetries}):`, error.message);
            await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, i)));
        }
    }

    throw lastError;
}

// =============================================================================
// 数据验证和转换
// =============================================================================

// 验证API响应格式
export function validateApiResponse(response) {
    if (!response || typeof response !== 'object') {
        throw new ApiError('无效的响应格式');
    }

    if (!response.hasOwnProperty('success')) {
        throw new ApiError('响应缺少success字段');
    }

    if (!response.success && !response.message) {
        throw new ApiError('API请求失败');
    }

    if (!response.success) {
        throw new ApiError(response.message);
    }

    return response;
}

// K线数据格式转换
export function formatKlineData(klines) {
    if (!Array.isArray(klines)) {
        return [];
    }

    return klines.map(kline => {
        if (Array.isArray(kline)) {
            // [timestamp, open, high, low, close, volume] 格式
            return kline;
        } else if (typeof kline === 'object') {
            // 对象格式转换为数组格式
            return [
                kline.timestamp,
                parseFloat(kline.open_price || kline.open),
                parseFloat(kline.high_price || kline.high),
                parseFloat(kline.low_price || kline.low),
                parseFloat(kline.close_price || kline.close),
                parseFloat(kline.volume)
            ];
        }
        return null;
    }).filter(Boolean);
}

// =============================================================================
// 导出配置和实用函数
// =============================================================================

export const config = {
    API_BASE_URL,
    API_V1,
    REQUEST_TIMEOUT,
    CACHE_DURATION
};

export {
    ApiError,
    request,
    get,
    post,
    put,
    del
};