import { writable, derived } from 'svelte/store';

// =============================================================================
// 基础数据存储
// =============================================================================

// K线数据存储
export const klineStore = writable([]);

// 缠论分析结果存储
export const analysisStore = writable({
    fenxings: [],
    bis: [],
    xianduan: [],
    buy_sell_points: [],
    trend: { direction: 'neutral', strength: 0 },
    support_resistance: { support_levels: [], resistance_levels: [] },
    analysis_summary: {}
});

// 用户设置存储
export const settingsStore = writable({
    timeframe: '1h',
    dataCount: 200,
    showFenxings: true,
    showBis: true,
    showBuySellPoints: true,
    chartTheme: 'light',
    autoRefresh: false,
    refreshInterval: 30000, // 30秒
    soundAlerts: false
});

// =============================================================================
// 系统状态存储
// =============================================================================

// 加载状态
export const loadingStore = writable(false);

// 错误状态
export const errorStore = writable(null);

// 网络连接状态
export const connectionStore = writable({
    isOnline: true,
    lastPing: null,
    apiStatus: 'unknown' // 'online', 'offline', 'error'
});

// 市场数据状态
export const marketStore = writable({
    currentPrice: 0,
    change24h: 0,
    changePercent24h: 0,
    high24h: 0,
    low24h: 0,
    volume24h: 0,
    lastUpdate: null
});

// =============================================================================
// UI状态存储
// =============================================================================

// 当前选中的分型
export const selectedFenxingStore = writable(null);

// 图表设置
export const chartSettingsStore = writable({
    height: 600,
    showVolume: true,
    showGrid: true,
    showCrosshair: true,
    priceScale: 'normal', // 'normal', 'logarithmic'
    timeScale: 'auto'
});

// 侧边栏状态
export const sidebarStore = writable({
    isCollapsed: false,
    activeTab: 'fenxings' // 'fenxings', 'analysis', 'settings'
});

// 通知系统
export const notificationStore = writable([]);

// =============================================================================
// 数据处理和衍生状态
// =============================================================================

// 最新价格（从K线数据衍生）
export const latestPrice = derived(
    klineStore,
    ($klines) => {
        if ($klines && $klines.length > 0) {
            const latest = $klines[$klines.length - 1];
            return parseFloat(latest[4]); // 收盘价
        }
        return 0;
    }
);

// 价格变化（从K线数据衍生）
export const priceChange = derived(
    klineStore,
    ($klines) => {
        if ($klines && $klines.length >= 2) {
            const current = parseFloat($klines[$klines.length - 1][4]);
            const previous = parseFloat($klines[$klines.length - 2][4]);
            const change = current - previous;
            const changePercent = (change / previous) * 100;

            return {
                absolute: change,
                percent: changePercent,
                direction: change > 0 ? 'up' : change < 0 ? 'down' : 'neutral'
            };
        }
        return {
            absolute: 0,
            percent: 0,
            direction: 'neutral'
        };
    }
);

// 分型统计（从分析结果衍生）
export const fenxingStats = derived(
    analysisStore,
    ($analysis) => {
        const fenxings = $analysis.fenxings || [];
        const topCount = fenxings.filter(f => f.type === 'top').length;
        const bottomCount = fenxings.filter(f => f.type === 'bottom').length;

        return {
            total: fenxings.length,
            tops: topCount,
            bottoms: bottomCount,
            ratio: topCount > 0 ? (bottomCount / topCount).toFixed(2) : 0
        };
    }
);

// 趋势状态（从分析结果衍生）
export const trendStatus = derived(
    analysisStore,
    ($analysis) => {
        const trend = $analysis.trend || { direction: 'neutral', strength: 0 };

        let status = 'neutral';
        let color = 'gray';
        let icon = '➡️';

        if (trend.direction === 'up' && trend.strength > 0.6) {
            status = '强势上涨';
            color = 'green';
            icon = '🚀';
        } else if (trend.direction === 'up' && trend.strength > 0.3) {
            status = '上涨趋势';
            color = 'green';
            icon = '📈';
        } else if (trend.direction === 'down' && trend.strength > 0.6) {
            status = '强势下跌';
            color = 'red';
            icon = '📉';
        } else if (trend.direction === 'down' && trend.strength > 0.3) {
            status = '下跌趋势';
            color = 'red';
            icon = '📉';
        } else {
            status = '震荡整理';
            color = 'gray';
            icon = '➡️';
        }

        return {
            text: status,
            color,
            icon,
            strength: trend.strength,
            direction: trend.direction
        };
    }
);

// 交易建议（从分析结果和趋势衍生）
export const tradingSuggestion = derived(
    [analysisStore, trendStatus],
    ([$analysis, $trendStatus]) => {
        const summary = $analysis.analysis_summary || {};
        const buyPoints = ($analysis.buy_sell_points || []).filter(p => p.type.includes('买'));
        const sellPoints = ($analysis.buy_sell_points || []).filter(p => p.type.includes('卖'));

        let suggestion = summary.suggestion || '等待更多数据';
        let confidence = 'medium';
        let action = 'wait';

        // 根据趋势和买卖点生成建议
        if ($trendStatus.direction === 'up' && $trendStatus.strength > 0.7) {
            if (buyPoints.length > 0) {
                suggestion = '趋势向上且有买点信号，可考虑适量建仓';
                confidence = 'high';
                action = 'buy';
            } else {
                suggestion = '上涨趋势强劲，但暂无明确买点，等待回调';
                confidence = 'medium';
                action = 'wait';
            }
        } else if ($trendStatus.direction === 'down' && $trendStatus.strength > 0.7) {
            if (sellPoints.length > 0) {
                suggestion = '下跌趋势明显且有卖点信号，建议减仓观望';
                confidence = 'high';
                action = 'sell';
            } else {
                suggestion = '下跌趋势强劲，建议观望等待止跌信号';
                confidence = 'medium';
                action = 'wait';
            }
        } else {
            suggestion = '趋势不明确，建议等待突破信号';
            confidence = 'low';
            action = 'wait';
        }

        return {
            text: suggestion,
            action, // 'buy', 'sell', 'wait'
            confidence, // 'high', 'medium', 'low'
            buyPoints: buyPoints.length,
            sellPoints: sellPoints.length,
            lastUpdate: new Date().toISOString()
        };
    }
);

// =============================================================================
// 存储操作函数
// =============================================================================

// 添加通知
export function addNotification(notification) {
    notificationStore.update(notifications => [
        ...notifications,
        {
            id: Date.now(),
            timestamp: new Date(),
            ...notification
        }
    ]);
}

// 移除通知
export function removeNotification(id) {
    notificationStore.update(notifications =>
        notifications.filter(n => n.id !== id)
    );
}

// 更新设置
export function updateSettings(newSettings) {
    settingsStore.update(settings => ({
        ...settings,
        ...newSettings
    }));
}

// 重置所有数据
export function resetAllData() {
    klineStore.set([]);
    analysisStore.set({
        fenxings: [],
        bis: [],
        xianduan: [],
        buy_sell_points: [],
        trend: { direction: 'neutral', strength: 0 },
        support_resistance: { support_levels: [], resistance_levels: [] },
        analysis_summary: {}
    });
    errorStore.set(null);
    selectedFenxingStore.set(null);
}

// 更新市场数据
export function updateMarketData(data) {
    marketStore.update(market => ({
        ...market,
        ...data,
        lastUpdate: new Date().toISOString()
    }));
}

// 检查连接状态
export function checkConnection() {
    connectionStore.update(conn => ({
        ...conn,
        lastPing: new Date().toISOString()
    }));
}

// =============================================================================
// 本地存储同步
// =============================================================================

// 从本地存储加载设置
export function loadSettingsFromStorage() {
    if (typeof localStorage !== 'undefined') {
        try {
            const saved = localStorage.getItem('chan-analysis-settings');
            if (saved) {
                const settings = JSON.parse(saved);
                settingsStore.set(settings);
            }
        } catch (error) {
            console.warn('加载设置失败:', error);
        }
    }
}

// 保存设置到本地存储
export function saveSettingsToStorage() {
    if (typeof localStorage !== 'undefined') {
        settingsStore.subscribe(settings => {
            try {
                localStorage.setItem('chan-analysis-settings', JSON.stringify(settings));
            } catch (error) {
                console.warn('保存设置失败:', error);
            }
        });
    }
}

// 从本地存储加载图表设置
export function loadChartSettingsFromStorage() {
    if (typeof localStorage !== 'undefined') {
        try {
            const saved = localStorage.getItem('chan-analysis-chart-settings');
            if (saved) {
                const settings = JSON.parse(saved);
                chartSettingsStore.set(settings);
            }
        } catch (error) {
            console.warn('加载图表设置失败:', error);
        }
    }
}

// 保存图表设置到本地存储
export function saveChartSettingsToStorage() {
    if (typeof localStorage !== 'undefined') {
        chartSettingsStore.subscribe(settings => {
            try {
                localStorage.setItem('chan-analysis-chart-settings', JSON.stringify(settings));
            } catch (error) {
                console.warn('保存图表设置失败:', error);
            }
        });
    }
}

// =============================================================================
// 数据验证函数
// =============================================================================

// 验证K线数据格式
export function validateKlineData(klines) {
    if (!Array.isArray(klines)) {
        return false;
    }

    return klines.every(kline => {
        return Array.isArray(kline) &&
               kline.length >= 5 &&
               !isNaN(parseFloat(kline[1])) && // open
               !isNaN(parseFloat(kline[2])) && // high
               !isNaN(parseFloat(kline[3])) && // low
               !isNaN(parseFloat(kline[4])); // close
    });
}

// 验证分析数据格式
export function validateAnalysisData(analysis) {
    return analysis &&
           typeof analysis === 'object' &&
           Array.isArray(analysis.fenxings) &&
           Array.isArray(analysis.bis);
}

// =============================================================================
// 数据格式化函数
// =============================================================================

// 格式化价格显示
export function formatPrice(price, decimals = 2) {
    if (typeof price !== 'number' || isNaN(price)) {
        return '0.00';
    }
    return price.toFixed(decimals);
}

// 格式化百分比显示
export function formatPercentage(value, decimals = 2) {
    if (typeof value !== 'number' || isNaN(value)) {
        return '0.00%';
    }
    return `${value.toFixed(decimals)}%`;
}

// 格式化成交量显示
export function formatVolume(volume) {
    if (typeof volume !== 'number' || isNaN(volume)) {
        return '0';
    }

    if (volume >= 1e9) {
        return `${(volume / 1e9).toFixed(2)}B`;
    } else if (volume >= 1e6) {
        return `${(volume / 1e6).toFixed(2)}M`;
    } else if (volume >= 1e3) {
        return `${(volume / 1e3).toFixed(2)}K`;
    }

    return volume.toFixed(2);
}

// 格式化时间显示
export function formatTime(timestamp) {
    if (!timestamp) return '';

    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// =============================================================================
// 所有 store 和函数已在上面定义并导出
// =============================================================================