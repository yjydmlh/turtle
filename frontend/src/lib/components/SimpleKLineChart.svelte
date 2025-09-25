<script>
    import { onMount, onDestroy } from 'svelte';
    import { init, dispose } from 'klinecharts';

    // 图表相关变量
    let chartContainer;
    let chart;
    let isLoading = true;
    let error = null;

    // 从后端获取K线数据
    async function fetchKlineData() {
        try {
            isLoading = true;
            error = null;
            
            const response = await fetch('/api/v1/kline_simple/klines?timeframe=1m&symbol=btc_usdt&limit=200');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success && result.data && result.data.klines) {
                return result.data.klines.map(item => ({
                    timestamp: item.timestamp,
                    open: parseFloat(item.open_price),
                    high: parseFloat(item.high_price),
                    low: parseFloat(item.low_price),
                    close: parseFloat(item.close_price),
                    volume: parseFloat(item.volume)
                }));
            } else {
                throw new Error(result.message || '获取数据失败');
            }
        } catch (err) {
            error = err.message;
            console.error('获取K线数据失败:', err);
            return [];
        } finally {
            isLoading = false;
        }
    }

    // 初始化图表
    async function initChart() {
        if (!chartContainer) return;

        // 创建图表实例
        chart = init(chartContainer);
        
        // 获取并设置数据
        const klineData = await fetchKlineData();
        if (klineData.length > 0) {
            chart.applyNewData(klineData);
        }
    }

    // 组件挂载时初始化图表
    onMount(() => {
        initChart();
    });

    // 组件销毁时清理图表
    onDestroy(() => {
        if (chart) {
            dispose(chartContainer);
        }
    });

    // 刷新数据
    async function refreshData() {
        if (!chart) return;
        
        const klineData = await fetchKlineData();
        if (klineData.length > 0) {
            chart.applyNewData(klineData);
        }
    }
</script>

<div class="kline-chart-container">
    <!-- 工具栏 -->
    <div class="toolbar">
        <h2>K线图表</h2>
        <button on:click={refreshData} disabled={isLoading}>
            {isLoading ? '加载中...' : '刷新数据'}
        </button>
    </div>

    <!-- 错误提示 -->
    {#if error}
        <div class="error-message">
            <p>❌ 错误: {error}</p>
            <button on:click={refreshData}>重试</button>
        </div>
    {/if}

    <!-- 加载提示 -->
    {#if isLoading}
        <div class="loading">
            <p>📊 正在加载K线数据...</p>
        </div>
    {/if}

    <!-- 图表容器 -->
    <div 
        bind:this={chartContainer} 
        class="chart-container"
        style="height: 600px; width: 100%;"
    ></div>
</div>

<style>
    .kline-chart-container {
        width: 100%;
        padding: 20px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e5e7eb;
    }

    .toolbar h2 {
        margin: 0;
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
    }

    .toolbar button {
        padding: 8px 16px;
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.2s;
    }

    .toolbar button:hover:not(:disabled) {
        background: #2563eb;
    }

    .toolbar button:disabled {
        background: #9ca3af;
        cursor: not-allowed;
    }

    .error-message {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 20px;
        color: #dc2626;
    }

    .error-message button {
        margin-top: 8px;
        padding: 6px 12px;
        background: #dc2626;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
    }

    .loading {
        text-align: center;
        padding: 40px;
        color: #6b7280;
        font-size: 16px;
    }

    .chart-container {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        background: #ffffff;
    }
</style>