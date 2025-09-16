<script>
    import { onMount, onDestroy } from 'svelte';
    import { createChart, ColorType, LineStyle, PriceScaleMode } from 'lightweight-charts';
    import { klineStore, analysisStore, chartSettingsStore, settingsStore } from '$lib/stores.js';
    import { formatPrice, formatVolume, formatTime } from '$lib/utils.js';

    // 图表相关变量
    let chartContainer;
    let chart;
    let candlestickSeries;
    let volumeSeries;
    let fenxingMarkers = [];
    let bisLines = [];
    let buySeekMarkers = [];

    // 响应式变量
    let containerWidth = 0;
    let containerHeight = 600;
    let isLoading = true;
    let error = null;

    // 计算自适应高度
    function calculateResponsiveHeight() {
        if (typeof window !== 'undefined') {
            // 获取窗口高度，减去头部导航和底部信息的高度
            const windowHeight = window.innerHeight;
            const headerHeight = 80; // 头部导航高度
            const footerHeight = 80; // 底部信息高度（减少了）
            const padding = 20; // 减少额外边距
            
            return Math.max(400, windowHeight - headerHeight - footerHeight - padding);
        }
        return 600;
    }

    // 图表配置
    let chartOptions = {
        width: 0,
        height: 600,
        layout: {
            background: { type: ColorType.Solid, color: '#ffffff' },
            textColor: '#333',
            fontSize: 12,
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
        },
        grid: {
            vertLines: { color: '#f0f0f0', style: LineStyle.Solid },
            horzLines: { color: '#f0f0f0', style: LineStyle.Solid }
        },
        crosshair: {
            mode: 0, // CrosshairMode.Normal
            vertLine: {
                width: 1,
                color: '#758695',
                style: LineStyle.Dashed
            },
            horzLine: {
                width: 1,
                color: '#758695',
                style: LineStyle.Dashed
            }
        },
        rightPriceScale: {
            borderColor: '#e0e0e0',
            scaleMargins: { top: 0.1, bottom: 0.1 }
        },
        timeScale: {
            borderColor: '#e0e0e0',
            timeVisible: true,
            secondsVisible: false,
            tickMarkFormatter: (time) => {
                const date = new Date(time * 1000);
                return date.toLocaleDateString('zh-CN', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            }
        },
        handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: true
        },
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true
        }
    };

    // 图表主题配置
    const themes = {
        light: {
            background: '#ffffff',
            textColor: '#333333',
            gridColor: '#f0f0f0',
            borderColor: '#e0e0e0'
        },
        dark: {
            background: '#1a1a1a',
            textColor: '#ffffff',
            gridColor: '#333333',
            borderColor: '#555555'
        }
    };

    onMount(async () => {
        // 设置初始自适应高度
        containerHeight = calculateResponsiveHeight();
        
        // 延迟初始化图表以提升页面加载速度
        await new Promise(resolve => setTimeout(resolve, 100));
        
        initializeChart();
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
                    chart.applyOptions({ height: containerHeight });
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
            chart.remove();
        }
    });

    // 初始化图表
    function initializeChart() {
        try {
            if (!chartContainer) return;

            // 创建图表实例
            chart = createChart(chartContainer, {
                ...chartOptions,
                width: containerWidth || chartContainer.clientWidth,
                height: containerHeight
            });

            // 创建K线序列
            candlestickSeries = chart.addCandlestickSeries({
                upColor: '#22c55e',
                downColor: '#ef4444',
                borderDownColor: '#ef4444',
                borderUpColor: '#22c55e',
                wickDownColor: '#ef4444',
                wickUpColor: '#22c55e',
                priceFormat: {
                    type: 'price',
                    precision: 2,
                    minMove: 0.01
                }
            });

            // 创建成交量序列
            volumeSeries = chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume'
                },
                priceScaleId: 'volume',
                scaleMargins: {
                    top: 0.7,
                    bottom: 0
                }
            });

            // 设置价格刻度
            chart.priceScale('volume').applyOptions({
                scaleMargins: {
                    top: 0.7,
                    bottom: 0
                }
            });

            // 添加图表事件监听
            setupChartEventListeners();

            isLoading = false;
        } catch (err) {
            console.error('图表初始化失败:', err);
            error = '图表初始化失败: ' + err.message;
            isLoading = false;
        }
    }

    // 设置图表事件监听器
    function setupChartEventListeners() {
        // 鼠标悬停事件
        chart.subscribeCrosshairMove((param) => {
            if (!param.time || !param.point) {
                return;
            }

            const candleData = param.seriesData.get(candlestickSeries);
            if (candleData) {
                // 可以在这里显示自定义的工具提示
                updateTooltip(param.time, candleData);
            }
        });

        // 点击事件
        chart.subscribeClick((param) => {
            if (!param.time || !param.point) {
                return;
            }

            // 检查是否点击了分型标记
            checkFenxingClick(param.time, param.point);
        });
    }

    // 更新工具提示
    function updateTooltip(time, candleData) {
        // 这里可以实现自定义工具提示逻辑
        // 目前使用默认的图表工具提示
    }

    // 检查分型点击
    function checkFenxingClick(time, point) {
        // 查找点击位置附近的分型
        const analysis = $analysisStore;
        if (!analysis.fenxings) return;

        const clickTime = time;
        const threshold = 5 * 60 * 1000; // 5分钟阈值

        const nearbyFenxing = analysis.fenxings.find(fx => {
            return Math.abs(fx.timestamp - clickTime * 1000) < threshold;
        });

        if (nearbyFenxing) {
            // 触发分型选择事件
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
        if (!chart || !candlestickSeries || !volumeSeries) return;
        if (!klines || klines.length === 0) return;

        try {
            // 转换K线数据格式
            const candleData = klines.map(kline => ({
                time: Math.floor(kline[0] / 1000), // 转换为秒级时间戳
                open: parseFloat(kline[1]),
                high: parseFloat(kline[2]),
                low: parseFloat(kline[3]),
                close: parseFloat(kline[4])
            }));

            // 转换成交量数据格式
            const volumeData = klines.map(kline => ({
                time: Math.floor(kline[0] / 1000),
                value: parseFloat(kline[5] || 0),
                color: parseFloat(kline[4]) >= parseFloat(kline[1]) ? '#22c55e' : '#ef4444'
            }));

            // 设置数据
            candlestickSeries.setData(candleData);
            volumeSeries.setData(volumeData);

            // 自动调整视图
            chart.timeScale().fitContent();

        } catch (err) {
            console.error('更新图表数据失败:', err);
            error = '数据更新失败: ' + err.message;
        }
    }

    // 更新缠论分析覆盖层
    function updateAnalysisOverlay(analysis) {
        if (!chart || !candlestickSeries) return;

        try {
            // 清除现有标记
            clearAnalysisOverlay();

            if (!analysis) return;

            // 添加分型标记
            if (analysis.fenxings && $settingsStore.showFenxings) {
                addFenxingMarkers(analysis.fenxings);
            }

            // 添加笔的连线
            if (analysis.bis && $settingsStore.showBis) {
                addBisLines(analysis.bis);
            }

            // 添加买卖点标记
            if (analysis.buy_sell_points && $settingsStore.showBuySellPoints) {
                addBuySellMarkers(analysis.buy_sell_points);
            }

        } catch (err) {
            console.error('更新缠论分析覆盖层失败:', err);
        }
    }

    // 清除分析覆盖层
    function clearAnalysisOverlay() {
        // 清除分型标记
        if (fenxingMarkers.length > 0) {
            candlestickSeries.setMarkers([]);
            fenxingMarkers = [];
        }

        // 清除笔的连线
        if (bisLines.length > 0) {
            bisLines.forEach(line => {
                if (line.remove) {
                    line.remove();
                }
            });
            bisLines = [];
        }

        // 清除买卖点标记
        buySeekMarkers = [];
    }

    // 添加分型标记
    function addFenxingMarkers(fenxings) {
        const markers = fenxings.map(fx => ({
            time: Math.floor(fx.timestamp / 1000),
            position: fx.type === 'top' ? 'aboveBar' : 'belowBar',
            color: fx.type === 'top' ? '#ef4444' : '#22c55e',
            shape: fx.type === 'top' ? 'arrowDown' : 'arrowUp',
            text: fx.type === 'top' ? '🔺' : '🔻',
            size: 1
        }));

        candlestickSeries.setMarkers(markers);
        fenxingMarkers = markers;
    }

    // 添加笔的连线
    function addBisLines(bis) {
        // 注意：lightweight-charts不直接支持画线，这里使用标记点模拟
        // 实际项目中可能需要使用其他方法或库来画线
        bis.forEach(bi => {
            if (bi.start && bi.end) {
                // 可以在这里实现笔的可视化逻辑
                // 例如使用price line或者其他方式
            }
        });
    }

    // 添加买卖点标记
    function addBuySellMarkers(buySeelPoints) {
        const markers = buySeelPoints.map(point => ({
            time: Math.floor(point.timestamp / 1000),
            position: point.type.includes('买') ? 'belowBar' : 'aboveBar',
            color: point.type.includes('买') ? '#22c55e' : '#ef4444',
            shape: point.type.includes('买') ? 'arrowUp' : 'arrowDown',
            text: point.type.includes('买') ? 'B' : 'S',
            size: 2
        }));

        // 合并分型标记和买卖点标记
        const allMarkers = [...fenxingMarkers, ...markers];
        candlestickSeries.setMarkers(allMarkers);
        buySeekMarkers = markers;
    }

    // 更新图表设置
    function updateChartSettings(settings) {
        if (!chart) return;

        // 更新高度
        if (settings.height !== containerHeight) {
            containerHeight = settings.height;
            chart.applyOptions({ height: containerHeight });
        }

        // 更新成交量显示
        if (volumeSeries) {
            volumeSeries.applyOptions({
                visible: settings.showVolume
            });
        }

        // 更新网格显示
        chart.applyOptions({
            grid: {
                vertLines: { visible: settings.showGrid },
                horzLines: { visible: settings.showGrid }
            }
        });

        // 更新十字线显示
        chart.applyOptions({
            crosshair: {
                vertLine: { visible: settings.showCrosshair },
                horzLine: { visible: settings.showCrosshair }
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
                    chart.applyOptions({
                        width: width,
                        height: containerHeight
                    });
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
            const canvas = chart.takeScreenshot();
            return canvas;
        } catch (err) {
            console.error('导出图表失败:', err);
            return null;
        }
    }

    // 缩放到指定时间范围
    export function zoomToTimeRange(startTime, endTime) {
        if (!chart) return;

        try {
            chart.timeScale().setVisibleRange({
                from: Math.floor(startTime / 1000),
                to: Math.floor(endTime / 1000)
            });
        } catch (err) {
            console.error('缩放时间范围失败:', err);
        }
    }

    // 自适应视图
    export function fitContent() {
        if (!chart) return;

        try {
            chart.timeScale().fitContent();
        } catch (err) {
            console.error('自适应视图失败:', err);
        }
    }

    // 切换主题
    export function toggleTheme(theme = 'light') {
        if (!chart) return;

        const themeConfig = themes[theme] || themes.light;

        chart.applyOptions({
            layout: {
                background: { type: ColorType.Solid, color: themeConfig.background },
                textColor: themeConfig.textColor
            },
            grid: {
                vertLines: { color: themeConfig.gridColor },
                horzLines: { color: themeConfig.gridColor }
            },
            rightPriceScale: {
                borderColor: themeConfig.borderColor
            },
            timeScale: {
                borderColor: themeConfig.borderColor
            }
        });
    }
</script>

<!-- 图表容器 -->
<div class="relative w-full">
    <!-- 加载状态 -->
    {#if isLoading}
        <div class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10">
            <div class="text-center">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-chan-600 mx-auto mb-2"></div>
                <p class="text-sm text-gray-600">加载图表中...</p>
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
        <button
            on:click={fitContent}
            class="bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 text-xs px-2 py-1 rounded shadow-sm border border-gray-200 transition-all"
            title="自适应视图"
        >
            📐
        </button>

        <button
            on:click={() => {
                const canvas = exportChart();
                if (canvas) {
                    // 触发下载
                    if (typeof document !== 'undefined') {
                        const link = document.createElement('a');
                        link.download = `chart-${new Date().getTime()}.png`;
                        link.href = canvas.toDataURL();
                        link.click();
                    }
                }
            }}
            class="bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 text-xs px-2 py-1 rounded shadow-sm border border-gray-200 transition-all"
            title="导出图片"
        >
            📷
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
    <div class="mt-2 flex flex-wrap items-center justify-between text-xs text-gray-600">
        <div class="flex items-center space-x-4">
            <span>数据源: 币安API</span>
            <span>时间周期: {$settingsStore.timeframe}</span>
            <span>数据量: {$klineStore.length} 条</span>
        </div>

        <div class="flex items-center space-x-2">
            {#if $settingsStore.showFenxings}
                <span class="flex items-center">
                    <span class="w-2 h-2 bg-bull-500 rounded-full mr-1"></span>
                    分型
                </span>
            {/if}

            {#if $settingsStore.showBis}
                <span class="flex items-center">
                    <span class="w-2 h-2 bg-purple-500 rounded-full mr-1"></span>
                    笔
                </span>
            {/if}

            {#if $settingsStore.showBuySellPoints}
                <span class="flex items-center">
                    <span class="w-2 h-2 bg-yellow-500 rounded-full mr-1"></span>
                    买卖点
                </span>
            {/if}
        </div>
    </div>
</div>

<style>
    /* 图表容器样式 */
    :global(.tv-lightweight-charts) {
        border-radius: 0.5rem;
    }

    /* 响应式调整 */
    @media (max-width: 768px) {
        :global(.tv-lightweight-charts canvas) {
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
</style>