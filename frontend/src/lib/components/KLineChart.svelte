<script>
    import { onMount, onDestroy } from 'svelte';
    import { init, dispose } from 'klinecharts';
    import { klineStore, analysisStore, chartSettingsStore, settingsStore } from '$lib/stores.js';
    import { formatPrice, formatVolume, formatTime } from '$lib/utils.js';

    // 图表相关变量
    let chartContainer;
    let chart;
    let containerWidth = 0;
    let containerHeight = 600;
    let isLoading = true;
    let error = null;

    // 计算自适应高度
    function calculateResponsiveHeight() {
        if (typeof window !== 'undefined') {
            const windowHeight = window.innerHeight;
            const headerHeight = 80;
            const footerHeight = 80;
            const padding = 20;
            
            return Math.max(400, windowHeight - headerHeight - footerHeight - padding);
        }
        return 600;
    }

    // KLineCharts 配置选项
    const chartOptions = {
        // 基础配置
        grid: {
            show: true,
            horizontal: {
                show: true,
                size: 1,
                color: '#f0f0f0',
                style: 'solid'
            },
            vertical: {
                show: true,
                size: 1,
                color: '#f0f0f0',
                style: 'solid'
            }
        },
        
        // 十字线配置
        crosshair: {
            show: true,
            horizontal: {
                show: true,
                line: {
                    show: true,
                    style: 'dashed',
                    dashValue: [4, 2],
                    size: 1,
                    color: '#758695'
                },
                text: {
                    show: true,
                    color: '#ffffff',
                    backgroundColor: '#758695',
                    size: 12,
                    family: 'Inter, sans-serif',
                    weight: 'normal'
                }
            },
            vertical: {
                show: true,
                line: {
                    show: true,
                    style: 'dashed',
                    dashValue: [4, 2],
                    size: 1,
                    color: '#758695'
                },
                text: {
                    show: true,
                    color: '#ffffff',
                    backgroundColor: '#758695',
                    size: 12,
                    family: 'Inter, sans-serif',
                    weight: 'normal'
                }
            }
        },

        // 蜡烛图样式
        candle: {
            margin: {
                top: 0.2,
                bottom: 0.1
            },
            type: 'candle_solid',
            bar: {
                upColor: '#22c55e',
                downColor: '#ef4444',
                noChangeColor: '#888888'
            },
            tooltip: {
                showRule: 'always',
                showType: 'standard',
                labels: ['时间: ', '开: ', '高: ', '低: ', '收: ', '涨跌幅: '],
                values: null,
                defaultValue: 'n/a',
                rect: {
                    position: 'fixed',
                    paddingLeft: 0,
                    paddingRight: 0,
                    paddingTop: 0,
                    paddingBottom: 6,
                    offsetLeft: 8,
                    offsetTop: 8,
                    offsetRight: 8,
                    offsetBottom: 8,
                    borderRadius: 4,
                    borderSize: 1,
                    borderColor: '#e5e7eb',
                    backgroundColor: 'rgba(255, 255, 255, 0.98)'
                },
                text: {
                    size: 12,
                    family: 'Inter, sans-serif',
                    weight: 'normal',
                    color: '#333333',
                    marginLeft: 8,
                    marginTop: 6,
                    marginRight: 8,
                    marginBottom: 0
                }
            }
        },

        // X轴配置
        xAxis: {
            show: true,
            height: null,
            axisLine: {
                show: true,
                color: '#e0e0e0',
                size: 1
            },
            tickText: {
                show: true,
                color: '#666666',
                size: 12,
                family: 'Inter, sans-serif',
                weight: 'normal',
                marginStart: 4,
                marginEnd: 4
            },
            tickLine: {
                show: true,
                size: 1,
                length: 3,
                color: '#e0e0e0'
            }
        },

        // Y轴配置
        yAxis: {
            show: true,
            width: null,
            position: 'right',
            type: 'normal',
            inside: false,
            reverse: false,
            axisLine: {
                show: true,
                color: '#e0e0e0',
                size: 1
            },
            tickText: {
                show: true,
                color: '#666666',
                size: 12,
                family: 'Inter, sans-serif',
                weight: 'normal',
                marginStart: 4,
                marginEnd: 4
            },
            tickLine: {
                show: true,
                size: 1,
                length: 3,
                color: '#e0e0e0'
            }
        }
    };

    onMount(async () => {
        // 设置初始自适应高度
        containerHeight = calculateResponsiveHeight();
        
        // 延迟初始化图表
        await new Promise(resolve => setTimeout(resolve, 100));
        
        await initializeChart();
        setupResizeObserver();

        // 监听数据变化
        const unsubscribeKline = klineStore.subscribe(updateChartData);
        const unsubscribeAnalysis = analysisStore.subscribe(updateAnalysisOverlay);
        const unsubscribeSettings = chartSettingsStore.subscribe(updateChartSettings);

        // 监听窗口大小变化
        const handleWindowResize = () => {
            const newHeight = calculateResponsiveHeight();
            if (newHeight !== containerHeight) {
                containerHeight = newHeight;
                if (chart) {
                    chart.resize();
                }
            }
        };

        window.addEventListener('resize', handleWindowResize);

        return () => {
            unsubscribeKline();
            unsubscribeAnalysis();
            unsubscribeSettings();
            window.removeEventListener('resize', handleWindowResize);
        };
    });

    onDestroy(() => {
        if (chart) {
            dispose(chartContainer);
        }
    });

    // 初始化图表
    async function initializeChart() {
        try {
            if (!chartContainer) return;

            // 创建图表实例 - KLineCharts v9.8.12 API
            chart = init(chartContainer);

            // 设置图表样式
            chart.setStyles({
                layout: {
                    backgroundColor: '#ffffff',
                    textColor: '#333333'
                },
                grid: {
                    show: true,
                    horizontal: { show: true, size: 1, color: '#f0f0f0', style: 'solid' },
                    vertical: { show: true, size: 1, color: '#f0f0f0', style: 'solid' }
                },
                candle: {
                    margin: { top: 0.2, bottom: 0.1 },
                    type: 'candle_solid',
                    bar: { upColor: '#22c55e', downColor: '#ef4444', noChangeColor: '#888888' }
                },
                xAxis: {
                    axisLine: { color: '#e5e5e5' },
                    tickText: { color: '#666666' },
                    tickLine: { color: '#e5e5e5' }
                },
                yAxis: {
                    axisLine: { color: '#e5e5e5' },
                    tickText: { color: '#666666' },
                    tickLine: { color: '#e5e5e5' }
                },
                crosshair: {
                    show: true,
                    horizontal: {
                        show: true,
                        line: { show: true, style: 'dashed', dashValue: [4, 2], size: 1, color: '#758695' },
                        text: { show: true, color: '#ffffff', backgroundColor: '#758695', size: 12 }
                    },
                    vertical: {
                        show: true,
                        line: { show: true, style: 'dashed', dashValue: [4, 2], size: 1, color: '#758695' },
                        text: { show: true, color: '#ffffff', backgroundColor: '#758695', size: 12 }
                    }
                }
            });

            // 创建成交量副图
            chart.createIndicator('VOL', false, { 
                id: 'volume_pane',
                height: 100,
                styles: {
                    backgroundColor: '#ffffff'
                }
            });

            // 设置图表事件监听
            setupChartEventListeners();

            // 自动加载K线数据
            await loadKlineData();

            isLoading = false;
        } catch (err) {
            console.error('图表初始化失败:', err);
            error = '图表初始化失败: ' + err.message;
            isLoading = false;
        }
    }

    // 从后端API加载K线数据
    async function loadKlineData() {
        try {
            isLoading = true;
            error = null;
            
            const response = await fetch('/api/v1/kline_simple/klines?timeframe=1m&symbol=btc_usdt&limit=1000');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success && result.data && result.data.klines) {
                const klineData = result.data.klines.map(item => ({
                    timestamp: item.timestamp,
                    open: parseFloat(item.open_price),
                    high: parseFloat(item.high_price),
                    low: parseFloat(item.low_price),
                    close: parseFloat(item.close_price),
                    volume: parseFloat(item.volume)
                }));

                // 应用数据到图表
                if (chart && klineData.length > 0) {
                    chart.applyNewData(klineData);
                    // 自动缩放到合适的时间范围
                    chart.zoomAtTimestamp(klineData[klineData.length - 1].timestamp, 0.02);
                }
            } else {
                throw new Error(result.message || '获取数据失败');
            }
        } catch (err) {
            error = err.message;
            console.error('获取K线数据失败:', err);
        } finally {
            isLoading = false;
        }
    }

    // 设置图表事件监听器
    function setupChartEventListeners() {
        if (!chart) return;

        // 十字线事件
        chart.subscribeAction('onCrosshairChange', (data) => {
            if (data.kLineData) {
                updateTooltip(data.kLineData);
                // 更新十字线时间显示
                crosshairTime = formatCrosshairTime(data.kLineData.timestamp);
            } else {
                crosshairTime = '';
            }
        });

        // 点击事件
        chart.subscribeAction('onClickChart', (data) => {
            checkFenxingClick(data);
        });
    }

    // 更新工具提示
    function updateTooltip(klineData) {
        // KLineCharts 内置了工具提示，这里可以做额外处理
    }

    // 检查分型点击
    function checkFenxingClick(data) {
        const analysis = $analysisStore;
        if (!analysis.fenxings || !data.kLineData) return;

        const clickTime = data.kLineData.timestamp;
        const threshold = 5 * 60 * 1000; // 5分钟阈值

        const nearbyFenxing = analysis.fenxings.find(fx => {
            return Math.abs(fx.timestamp - clickTime) < threshold;
        });

        if (nearbyFenxing) {
            dispatchFenxingSelect(nearbyFenxing);
        }
    }

    // 分型选择事件
    function dispatchFenxingSelect(fenxing) {
        const event = new CustomEvent('fenxingSelect', {
            detail: fenxing
        });
        chartContainer.dispatchEvent(event);
    }

    // 更新图表数据
    function updateChartData(klines) {
        if (!chart || !klines || klines.length === 0) return;

        try {
            // 转换K线数据格式为 KLineCharts 格式
            const klineData = klines.map(kline => ({
                timestamp: kline[0], // 毫秒时间戳
                open: parseFloat(kline[1]),
                high: parseFloat(kline[2]),
                low: parseFloat(kline[3]),
                close: parseFloat(kline[4]),
                volume: parseFloat(kline[5] || 0)
            }));

            // 应用数据到图表
            chart.applyNewData(klineData);

            // 自动缩放到合适的时间范围
            chart.zoomAtTimestamp(klineData[klineData.length - 1].timestamp, 0.02);

        } catch (err) {
            console.error('更新图表数据失败:', err);
            error = '数据更新失败: ' + err.message;
        }
    }

    // 更新缠论分析覆盖层
    function updateAnalysisOverlay(analysis) {
        if (!chart) return;

        try {
            // 清除现有覆盖物
            chart.removeOverlay();

            if (!analysis) return;

            // 添加分型标记
            if (analysis.fenxings && $settingsStore.showFenxings) {
                addFenxingOverlays(analysis.fenxings);
            }

            // 添加笔的连线
            if (analysis.bis && $settingsStore.showBis) {
                addBisOverlays(analysis.bis);
            }

            // 添加买卖点标记
            if (analysis.buy_sell_points && $settingsStore.showBuySellPoints) {
                addBuySellOverlays(analysis.buy_sell_points);
            }

        } catch (err) {
            console.error('更新缠论分析覆盖层失败:', err);
        }
    }

    // 添加分型覆盖物
    function addFenxingOverlays(fenxings) {
        fenxings.forEach((fx, index) => {
            const overlayId = `fenxing_${index}`;
            
            chart.createOverlay({
                name: 'simpleAnnotation',
                id: overlayId,
                points: [
                    { timestamp: fx.timestamp, value: fx.price }
                ],
                styles: {
                    point: {
                        color: fx.type === 'top' ? '#ef4444' : '#22c55e',
                        radius: 6
                    },
                    text: {
                        color: fx.type === 'top' ? '#ef4444' : '#22c55e',
                        size: 12,
                        offset: [0, fx.type === 'top' ? 15 : -15]
                    }
                },
                extendData: fx.type === 'top' ? '🔺' : '🔻'
            });
        });
    }

    // 添加笔覆盖物
    function addBisOverlays(bis) {
        bis.forEach((bi, index) => {
            if (bi.start && bi.end) {
                const overlayId = `bi_${index}`;
                
                chart.createOverlay({
                    name: 'segment',
                    id: overlayId,
                    points: [
                        { timestamp: bi.start.timestamp, value: bi.start.price },
                        { timestamp: bi.end.timestamp, value: bi.end.price }
                    ],
                    styles: {
                        line: {
                            color: bi.direction === 'up' ? '#22c55e' : '#ef4444',
                            size: 2,
                            style: 'solid'
                        }
                    }
                });
            }
        });
    }

    // 添加买卖点覆盖物
    function addBuySellOverlays(buySeelPoints) {
        buySeelPoints.forEach((point, index) => {
            const overlayId = `bsp_${index}`;
            const isBuy = point.type.includes('买');
            
            chart.createOverlay({
                name: 'simpleAnnotation',
                id: overlayId,
                points: [
                    { timestamp: point.timestamp, value: point.price }
                ],
                styles: {
                    point: {
                        color: isBuy ? '#22c55e' : '#ef4444',
                        radius: 8
                    },
                    text: {
                        color: '#ffffff',
                        size: 14,
                        weight: 'bold',
                        backgroundColor: isBuy ? '#22c55e' : '#ef4444',
                        borderRadius: 3,
                        paddingLeft: 4,
                        paddingRight: 4,
                        paddingTop: 2,
                        paddingBottom: 2
                    }
                },
                extendData: isBuy ? 'B' : 'S'
            });
        });
    }

    // 更新图表设置
    function updateChartSettings(settings) {
        if (!chart) return;

        // 更新网格显示
        chart.setStyles({
            grid: {
                show: settings.showGrid
            }
        });

        // 更新十字线显示
        chart.setStyles({
            crosshair: {
                show: settings.showCrosshair
            }
        });
    }

    // 设置尺寸监听器
    function setupResizeObserver() {
        if (!chartContainer) return;

        const resizeObserver = new ResizeObserver(entries => {
            for (const entry of entries) {
                const { width, height } = entry.contentRect;
                containerWidth = width;

                if (chart) {
                    chart.resize();
                }
            }
        });

        resizeObserver.observe(chartContainer);

        return () => {
            resizeObserver.disconnect();
        };
    }

    // 导出图表图片
    export function exportChart() {
        if (!chart) return null;

        try {
            return chart.getConvertPictureUrl();
        } catch (err) {
            console.error('导出图表失败:', err);
            return null;
        }
    }

    // 缩放到指定时间范围
    export function zoomToTimeRange(startTime, endTime) {
        if (!chart) return;

        try {
            chart.zoomAtTimestamp(endTime, 0.1);
        } catch (err) {
            console.error('缩放时间范围失败:', err);
        }
    }

    // 自适应视图
    export function fitContent() {
        if (!chart) return;

        try {
            chart.zoomAtTimestamp(Date.now(), 0.02);
        } catch (err) {
            console.error('自适应视图失败:', err);
        }
    }

    // 自动调整价格范围
    export function autoScalePrice() {
        if (!chart) return;

        try {
            chart.zoomAtTimestamp(Date.now(), 0.02);
        } catch (err) {
            console.error('自动调整价格范围失败:', err);
        }
    }

    // 切换主题
    export function toggleTheme(theme = 'light') {
        if (!chart) return;

        const themes = {
            light: {
                grid: {
                    horizontal: { color: '#f0f0f0' },
                    vertical: { color: '#f0f0f0' }
                },
                candle: {
                    tooltip: {
                        rect: { backgroundColor: 'rgba(255, 255, 255, 0.98)', borderColor: '#e5e7eb' },
                        text: { color: '#333333' }
                    }
                },
                xAxis: {
                    axisLine: { color: '#e0e0e0' },
                    tickText: { color: '#666666' },
                    tickLine: { color: '#e0e0e0' }
                },
                yAxis: {
                    axisLine: { color: '#e0e0e0' },
                    tickText: { color: '#666666' },
                    tickLine: { color: '#e0e0e0' }
                }
            },
            dark: {
                grid: {
                    horizontal: { color: '#333333' },
                    vertical: { color: '#333333' }
                },
                candle: {
                    tooltip: {
                        rect: { backgroundColor: 'rgba(26, 26, 26, 0.98)', borderColor: '#555555' },
                        text: { color: '#ffffff' }
                    }
                },
                xAxis: {
                    axisLine: { color: '#555555' },
                    tickText: { color: '#cccccc' },
                    tickLine: { color: '#555555' }
                },
                yAxis: {
                    axisLine: { color: '#555555' },
                    tickText: { color: '#cccccc' },
                    tickLine: { color: '#555555' }
                }
            }
        };

        chart.setStyles(themes[theme] || themes.light);
    }

    // 添加技术指标
    export function addIndicator(type, isMain = false, options = {}) {
        if (!chart) return;

        try {
            return chart.createIndicator(type, isMain, options);
        } catch (err) {
            console.error('添加技术指标失败:', err);
            return null;
        }
    }

    // 移除技术指标
    export function removeIndicator(indicatorName, paneId) {
        if (!chart) return;

        try {
            chart.removeIndicator(paneId, indicatorName);
        } catch (err) {
            console.error('移除技术指标失败:', err);
        }
    }

    // 当前十字线时间显示
    let crosshairTime = '';

    // 格式化时间为 yyyy-MM-dd HH:mm:ss
    function formatCrosshairTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }).replace(/\//g, '-');
    }
</script>

<!-- 图表容器 -->
<div class="relative w-full">
    <!-- 加载状态 -->
    {#if isLoading}
        <div class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10">
            <div class="text-center">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-chan-600 mx-auto mb-2"></div>
                <p class="text-sm text-gray-600">加载KLineCharts Pro...</p>
            </div>
        </div>
    {/if}

    <!-- 错误状态 -->
    {#if error}
        <div class="absolute inset-0 flex items-center justify-center bg-red-50 z-10">
            <div class="text-center p-4">
                <div class="text-red-600 mb-2">
                    <svg class="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <p class="text-sm text-red-700 font-medium">图表加载失败</p>
                <p class="text-xs text-red-600 mt-1">{error}</p>
                <button
                    on:click={() => {
                        error = null;
                        isLoading = true;
                        initializeChart();
                    }}
                    class="mt-2 text-xs bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition-colors"
                >
                    重试
                </button>
            </div>
        </div>
    {/if}

    <!-- 图表工具栏 -->
    <div class="absolute top-2 right-2 z-20 flex space-x-1">
        <!-- 十字线时间显示 -->
        {#if crosshairTime}
            <div class="bg-blue-600 text-white text-xs px-3 py-1 rounded shadow-sm border border-blue-700 font-mono">
                {crosshairTime}
            </div>
        {/if}
        
        <button
            on:click={fitContent}
            class="bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 text-xs px-2 py-1 rounded shadow-sm border border-gray-200 transition-all"
            title="自适应视图"
        >
            📐
        </button>

        <button
            on:click={autoScalePrice}
            class="bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 text-xs px-2 py-1 rounded shadow-sm border border-gray-200 transition-all"
            title="自动调整价格范围"
        >
            📊
        </button>

        <button
            on:click={() => {
                const imageUrl = exportChart();
                if (imageUrl && typeof document !== 'undefined') {
                    const link = document.createElement('a');
                    link.download = `klinechart-${new Date().getTime()}.png`;
                    link.href = imageUrl;
                    link.click();
                }
            }}
            class="bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 text-xs px-2 py-1 rounded shadow-sm border border-gray-200 transition-all"
            title="导出图片"
        >
            📷
        </button>

        <!-- 技术指标按钮 -->
        <button
            on:click={() => addIndicator('MACD', false, { id: 'macd_pane', height: 100 })}
            class="bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 text-xs px-2 py-1 rounded shadow-sm border border-gray-200 transition-all"
            title="添加MACD"
        >
            MACD
        </button>

        <button
            on:click={() => addIndicator('RSI', false, { id: 'rsi_pane', height: 100 })}
            class="bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 text-xs px-2 py-1 rounded shadow-sm border border-gray-200 transition-all"
            title="添加RSI"
        >
            RSI
        </button>
    </div>

    <!-- 主图表区域 -->
    <div
        bind:this={chartContainer}
        class="w-full bg-white border border-gray-200 rounded-lg overflow-hidden"
        style="height: {containerHeight}px; min-height: 400px;"
    >
        <!-- 图表将在这里渲染 -->
    </div>

    <!-- 图表信息面板 -->
<!--    <div class="mt-2 flex flex-wrap items-center justify-between text-xs text-gray-600">-->
<!--        <div class="flex items-center space-x-4">-->
<!--            <span>数据源: 币安API</span>-->
<!--            <span>时间周期: {$settingsStore.timeframe}</span>-->
<!--            <span>数据量: {$klineStore.length} 条</span>-->
<!--        </div>-->

<!--        <div class="flex items-center space-x-2">-->
<!--            {#if $settingsStore.showFenxings}-->
<!--                <span class="flex items-center">-->
<!--                    <span class="w-2 h-2 bg-bull-500 rounded-full mr-1"></span>-->
<!--                    分型-->
<!--                </span>-->
<!--            {/if}-->

<!--            {#if $settingsStore.showBis}-->
<!--                <span class="flex items-center">-->
<!--                    <span class="w-2 h-2 bg-purple-500 rounded-full mr-1"></span>-->
<!--                    笔-->
<!--                </span>-->
<!--            {/if}-->

<!--            {#if $settingsStore.showBuySellPoints}-->
<!--                <span class="flex items-center">-->
<!--                    <span class="w-2 h-2 bg-yellow-500 rounded-full mr-1"></span>-->
<!--                    买卖点-->
<!--                </span>-->
<!--            {/if}-->
<!--        </div>-->
<!--    </div>-->
</div>

<style>
    /* KLineCharts 容器样式 */
    :global(.klinecharts) {
        border-radius: 0.5rem;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* 响应式调整 */
    @media (max-width: 768px) {
        :global(.klinecharts) {
            touch-action: pan-x pan-y;
        }
    }

    /* 高对比度模式支持 */
    @media (prefers-contrast: high) {
        .bg-white {
            border-width: 2px;
            border-color: #000;
        }
    }

    /* 打印模式隐藏工具栏 */
    @media print {
        .absolute.top-2.right-2 {
            display: none;
        }
    }

    /* 自定义滚动条样式 */
    :global(.klinecharts *::-webkit-scrollbar) {
        width: 6px;
        height: 6px;
    }

    :global(.klinecharts *::-webkit-scrollbar-track) {
        background: #f1f1f1;
        border-radius: 3px;
    }

    :global(.klinecharts *::-webkit-scrollbar-thumb) {
        background: #c1c1c1;
        border-radius: 3px;
    }

    :global(.klinecharts *::-webkit-scrollbar-thumb:hover) {
        background: #a1a1a1;
    }
</style>