<script>
    import { onMount } from 'svelte';
    import TradingViewChart from '$lib/components/TradingViewChart.svelte';
    import ControlPanel from '$lib/components/ControlPanel.svelte';
    import MarketStatus from '$lib/components/MarketStatus.svelte';
    import FenxingList from '$lib/components/FenxingList.svelte';
    import TradingSuggestion from '$lib/components/TradingSuggestion.svelte';
    import FloatingToolbar from '$lib/components/FloatingToolbar.svelte';
    import DraggablePanel from '$lib/components/DraggablePanel.svelte';
    import { klineStore, analysisStore, settingsStore, loadingStore, errorStore } from '$lib/stores.js';
    import { loadChartData, fetchNewData, getChanModuleInfo, getDatabaseChartData } from '$lib/api.js';
    import { RefreshCw, Download, TrendingUp, Info, Activity, Database } from 'lucide-svelte';

    let loading = false;
    let error = null;
    let chanModuleInfo = null;
    let useDatabase = true; // 默认使用数据库数据
    let selectedSymbol = 'btc_usdt';
    let selectedTimeframe = '1h';
    
    // 面板显示状态
    let panels = {
        control: false,
        market: false,
        fenxing: false,
        trading: false
    };

    onMount(() => {
        // 优先加载关键数据
        loadData();
        
        // 延迟加载非关键数据
        setTimeout(() => {
            loadChanInfo();
        }, 500);
    });

    async function loadData() {
        loading = true;
        error = null;
        loadingStore.set(true);

        try {
            const timeframe = $settingsStore.timeframe;
            const limit = $settingsStore.dataCount;

            let data;
            if (useDatabase) {
                // 使用数据库API获取K线数据
                data = await getDatabaseChartData('btc_usdt', timeframe, limit);
                
                // 转换数据格式以兼容现有组件
                if (data.success && data.data) {
                    // 将数据库返回的对象格式转换为图表组件期望的数组格式
                    const convertedData = data.data.map(item => [
                        item.timestamp,           // 时间戳 (毫秒)
                        parseFloat(item.open_price),         // 开盘价
                        parseFloat(item.high_price),         // 最高价
                        parseFloat(item.low_price),          // 最低价
                        parseFloat(item.close_price),        // 收盘价
                        parseFloat(item.volume)              // 成交量
                    ]);
                    
                    // 按时间升序排序（TradingView要求数据必须按时间升序）
                    convertedData.sort((a, b) => a[0] - b[0]);
                    
                    klineStore.set(convertedData);
                    // 数据库API暂时不包含分析数据，设置默认结构避免null错误
                    analysisStore.set({
                        fenxings: [],
                        bis: [],
                        xianduan: [],
                        buy_sell_points: [],
                        trend: { direction: 'neutral', strength: 0 },
                        support_resistance: { support_levels: [], resistance_levels: [] },
                        analysis_summary: {}
                    });
                } else {
                    throw new Error(data.message || 'API返回错误');
                }
            } else {
                // 使用原有的缠论分析API
                data = await loadChartData(timeframe, limit, true);

                if (data.success) {
                    klineStore.set(data.data.chart_data.klines);
                    if (data.data.analysis) {
                        analysisStore.set(data.data.analysis);
                    }
                } else {
                    throw new Error('API返回错误');
                }
            }
        } catch (err) {
            error = err.message;
            errorStore.set(err.message);
            console.error('加载数据失败:', err);
        } finally {
            loading = false;
            loadingStore.set(false);
        }
    }

    async function loadChanInfo() {
        try {
            const info = await getChanModuleInfo();
            if (info.success) {
                chanModuleInfo = info.data;
            }
        } catch (err) {
            console.warn('获取Chan模块信息失败:', err);
        }
    }

    async function handleFetchNewData() {
        loading = true;
        try {
            await fetchNewData();
            // 等待2秒后重新加载数据
            setTimeout(loadData, 2000);
        } catch (err) {
            error = '获取新数据失败: ' + err.message;
            errorStore.set(error);
        } finally {
            loading = false;
        }
    }

    function handleTimeframeChange(event) {
        loadData();
    }

    function handlePanelToggle(event) {
        const { panel } = event.detail;
        panels[panel] = !panels[panel];
    }
</script>

<!-- 页面头部 -->
<svelte:head>
    <title>缠论分析系统 - 专业技术分析平台</title>
    <meta name="description" content="基于缠中说禅理论的专业技术分析系统，支持实时K线分析、分型识别、笔段构建" />
</svelte:head>

<div class="min-h-screen bg-gray-900 flex flex-col">
    <!-- 头部导航 -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <!-- Logo和标题 -->
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-gradient-to-r from-chan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                        <TrendingUp class="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 class="text-xl font-bold text-gray-900">缠论分析系统</h1>
                        <p class="text-sm text-gray-500 hidden sm:block">专业技术分析 · 实时数据 · 智能提醒</p>
                    </div>
                </div>

                <!-- 状态指示器和操作按钮 -->
                <div class="flex items-center space-x-4">
                    <!-- 系统状态 -->
                    <div class="hidden md:flex items-center space-x-2">
                        <div class="flex items-center space-x-1">
                            <div class="w-2 h-2 bg-bull-500 rounded-full animate-pulse"></div>
                            <span class="text-sm text-gray-600">实时连接</span>
                        </div>

                        {#if chanModuleInfo}
                            <div class="flex items-center space-x-1 ml-3">
                                <Activity class="w-4 h-4 {chanModuleInfo.chan_module.is_available ? 'text-bull-500' : 'text-yellow-500'}" />
                                <span class="text-sm text-gray-600">
                                    Chan模块: {chanModuleInfo.chan_module.is_available ? '正常' : '简化模式'}
                                </span>
                            </div>
                        {/if}
                    </div>

                    <!-- 操作按钮 -->
                    <div class="flex items-center space-x-2">
                        <!-- 数据源切换按钮 -->
                        <button
                            on:click={() => { useDatabase = !useDatabase; loadData(); }}
                            disabled={loading}
                            class="btn-secondary btn-sm {useDatabase ? 'bg-blue-100 text-blue-700 border-blue-300' : ''}"
                            title="{useDatabase ? '当前: 数据库数据' : '当前: 缠论分析数据'}"
                        >
                            <Database class="w-4 h-4 mr-1" />
                            <span class="hidden sm:inline">{useDatabase ? '数据库' : '缠论'}</span>
                        </button>

                        <button
                            on:click={loadData}
                            disabled={loading}
                            class="btn-secondary btn-sm"
                            title="刷新数据"
                        >
                            <RefreshCw class="w-4 h-4 mr-1 {loading ? 'animate-spin' : ''}" />
                            <span class="hidden sm:inline">{loading ? '加载中...' : '刷新'}</span>
                        </button>

                        <button
                            on:click={handleFetchNewData}
                            disabled={loading}
                            class="btn-primary btn-sm"
                            title="获取新数据"
                        >
                            <Download class="w-4 h-4 mr-1" />
                            <span class="hidden sm:inline">获取新数据</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- 主要内容区域 - 全屏K线图表 -->
    <main class="flex-1 relative overflow-hidden">
        <!-- 错误提示 -->
        {#if $errorStore}
            <div class="absolute top-4 left-1/2 transform -translate-x-1/2 z-50 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg max-w-md">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <h3 class="text-sm font-medium text-red-800">错误</h3>
                        <div class="mt-2 text-sm text-red-700">
                            <p>{$errorStore}</p>
                        </div>
                    </div>
                </div>
            </div>
        {/if}

        <!-- 全屏K线图表 -->
        <div class="absolute inset-0 bg-white">
            <TradingViewChart />
        </div>

        <!-- 浮动工具栏 -->
        <FloatingToolbar on:panelToggle={handlePanelToggle} />

        <!-- 弹出式面板 -->
        <DraggablePanel
            bind:isVisible={panels.control}
            title="控制面板"
            initialX={100}
            initialY={100}
            width={400}
            height={300}
            on:close={() => panels.control = false}
        >
            <div class="p-4">
                <ControlPanel 
                    bind:selectedSymbol 
                    bind:selectedTimeframe 
                    bind:useDatabase 
                    on:loadData={loadData}
                    on:fetchNewData={handleFetchNewData}
                    on:timeframeChange={handleTimeframeChange}
                />
            </div>
        </DraggablePanel>

        <DraggablePanel
            bind:isVisible={panels.market}
            title="市场状态"
            initialX={150}
            initialY={150}
            width={350}
            height={400}
            on:close={() => panels.market = false}
        >
            <div class="p-4">
                <MarketStatus />
            </div>
        </DraggablePanel>

        <DraggablePanel
            bind:isVisible={panels.fenxing}
            title="分型列表"
            initialX={200}
            initialY={200}
            width={450}
            height={500}
            on:close={() => panels.fenxing = false}
        >
            <div class="p-4">
                <FenxingList />
            </div>
        </DraggablePanel>

        <DraggablePanel
            bind:isVisible={panels.trading}
            title="交易建议"
            initialX={250}
            initialY={250}
            width={400}
            height={450}
            on:close={() => panels.trading = false}
        >
            <div class="p-4">
                <TradingSuggestion />
            </div>
        </DraggablePanel>
    </main>

    <!-- 底部信息栏 -->
    <footer class="bg-white border-t border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div class="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
                <div class="flex items-center space-x-4 text-sm text-gray-500">
                    <span>© 2024 缠论分析系统</span>
                    <span class="hidden sm:inline">·</span>
                    <span class="hidden sm:inline">专业技术分析工具</span>
                </div>

                <div class="flex items-center space-x-4 text-sm">
                    {#if chanModuleInfo}
                        <div class="flex items-center space-x-2">
                            <span class="text-gray-500">Chan模块:</span>
                            <span class="badge {chanModuleInfo.chan_module.is_available ? 'badge-success' : 'badge-warning'}">
                                {chanModuleInfo.chan_module.is_available ? '已集成' : '简化模式'}
                            </span>
                        </div>
                    {/if}

                    <div class="flex items-center space-x-2">
                        <span class="text-gray-500">数据源:</span>
                        <span class="badge-neutral">币安API</span>
                    </div>
                </div>
            </div>
        </div>
    </footer>
</div>

<!-- 加载遮罩 -->
{#if $loadingStore}
    <div class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 shadow-xl">
            <div class="flex items-center space-x-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-chan-600"></div>
                <span class="text-gray-700">加载中...</span>
            </div>
        </div>
    </div>
{/if}

<style>
    /* 页面特定样式 */
    .page-transition {
        opacity: 0;
        animation: fadeInPage 0.5s ease-in-out forwards;
    }

    @keyframes fadeInPage {
        to {
            opacity: 1;
        }
    }

    /* 全屏布局样式 */
    main {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    }

    /* 头部导航优化 */
    header {
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.95);
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    /* 错误提示样式优化 */
    .error-notification {
        backdrop-filter: blur(10px);
        animation: slideInFromTop 0.3s ease-out;
    }

    @keyframes slideInFromTop {
        from {
            opacity: 0;
            transform: translate(-50%, -20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }

    /* 响应式调整 */
    @media (max-width: 1280px) {
        .xl\:col-span-3 {
            grid-column: span 1;
        }

        .xl\:col-span-1 {
            grid-column: span 1;
        }
    }

    @media (max-width: 768px) {
        header {
            padding: 0.75rem 1rem;
        }

        .logo-section h1 {
            font-size: 1.25rem;
        }

        .nav-actions {
            gap: 0.5rem;
        }

        .nav-actions button {
            padding: 0.5rem;
            font-size: 0.875rem;
        }
    }

    /* 加载状态 */
    .loading-overlay {
        backdrop-filter: blur(2px);
    }

    /* 深色主题适配 */
    @media (prefers-color-scheme: dark) {
        header {
            background: rgba(30, 41, 59, 0.95);
            border-bottom-color: rgba(255, 255, 255, 0.1);
        }

        .error-notification {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }
    }

    /* 高对比度模式 */
    @media (prefers-contrast: high) {
        header {
            background: white;
            border-bottom: 2px solid #000;
        }

        main {
            background: #000;
        }
    }

    /* 减少动画模式 */
    @media (prefers-reduced-motion: reduce) {
        .page-transition,
        .error-notification {
            animation: none;
        }

        * {
            transition: none !important;
        }
    }
</style>