<script>
    import { onMount } from 'svelte';
    import TradingViewChart from '$lib/components/TradingViewChart.svelte';
    import ControlPanel from '$lib/components/ControlPanel.svelte';
    import MarketStatus from '$lib/components/MarketStatus.svelte';
    import FenxingList from '$lib/components/FenxingList.svelte';
    import TradingSuggestion from '$lib/components/TradingSuggestion.svelte';
    import { klineStore, analysisStore, settingsStore, loadingStore, errorStore } from '$lib/stores.js';
    import { loadChartData, fetchNewData, getChanModuleInfo } from '$lib/api.js';
    import { RefreshCw, Download, TrendingUp, Info, Activity } from 'lucide-svelte';

    let loading = false;
    let error = null;
    let chanModuleInfo = null;

    onMount(() => {
        loadData();
        loadChanInfo();
    });

    async function loadData() {
        loading = true;
        error = null;
        loadingStore.set(true);

        try {
            const timeframe = $settingsStore.timeframe;
            const limit = $settingsStore.dataCount;

            const data = await loadChartData(timeframe, limit, true);

            if (data.success) {
                klineStore.set(data.data.chart_data.klines);
                if (data.data.analysis) {
                    analysisStore.set(data.data.analysis);
                }
            } else {
                throw new Error('API返回错误');
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
</script>

<!-- 页面头部 -->
<svelte:head>
    <title>缠论分析系统 - 专业技术分析平台</title>
    <meta name="description" content="基于缠中说禅理论的专业技术分析系统，支持实时K线分析、分型识别、笔段构建" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
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

    <!-- 控制面板 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ControlPanel on:change={handleTimeframeChange} />
    </div>

    <!-- 错误提示 -->
    {#if error}
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="bg-bear-50 border-l-4 border-bear-400 p-4 mb-4 rounded-r-lg">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <Info class="h-5 w-5 text-bear-400" />
                    </div>
                    <div class="ml-3">
                        <h3 class="text-sm font-medium text-bear-800">
                            数据加载失败
                        </h3>
                        <div class="mt-2 text-sm text-bear-700">
                            {error}
                        </div>
                        <div class="mt-3">
                            <button
                                on:click={loadData}
                                class="btn-sm bg-bear-100 text-bear-800 border-bear-200 hover:bg-bear-200"
                            >
                                重试
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <!-- 主要内容区域 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div class="grid grid-cols-1 xl:grid-cols-4 gap-6">
            <!-- 图表区域 -->
            <div class="xl:col-span-3">
                <div class="card">
                    <div class="card-header">
                        <div class="flex justify-between items-center">
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">BTC/USDT 专业图表</h3>
                                <p class="text-sm text-gray-500 mt-1">集成缠论分析 · TradingView专业图表</p>
                            </div>
                            <div class="flex items-center space-x-2 text-sm text-gray-500">
                                <span>时间周期:</span>
                                <span class="badge-primary">{$settingsStore.timeframe}</span>
                            </div>
                        </div>
                    </div>
                    <div class="p-0">
                        <TradingViewChart />
                    </div>
                </div>
            </div>

            <!-- 侧边栏 -->
            <div class="xl:col-span-1 space-y-6">
                <!-- 市场状态 -->
                <div class="card">
                    <div class="card-header bg-gradient-to-r from-bull-50 to-chan-50">
                        <h3 class="text-md font-semibold text-gray-900 flex items-center">
                            <Activity class="w-5 h-5 mr-2 text-bull-600" />
                            市场状态
                        </h3>
                    </div>
                    <div class="card-body">
                        <MarketStatus />
                    </div>
                </div>

                <!-- 分型列表 -->
                <div class="card">
                    <div class="card-header bg-gradient-to-r from-purple-50 to-pink-50">
                        <h3 class="text-md font-semibold text-gray-900 flex items-center">
                            <TrendingUp class="w-5 h-5 mr-2 text-purple-600" />
                            分型识别
                        </h3>
                    </div>
                    <div class="p-0">
                        <FenxingList />
                    </div>
                </div>

                <!-- 交易建议 -->
                <div class="card">
                    <div class="card-header bg-gradient-to-r from-yellow-50 to-orange-50">
                        <h3 class="text-md font-semibold text-gray-900 flex items-center">
                            <Info class="w-5 h-5 mr-2 text-yellow-600" />
                            交易建议
                        </h3>
                    </div>
                    <div class="card-body">
                        <TradingSuggestion />
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 底部信息栏 -->
    <footer class="bg-white border-t border-gray-200 mt-12">
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

    /* 响应式调整 */
    @media (max-width: 1280px) {
        .xl\:col-span-3 {
            grid-column: span 1;
        }

        .xl\:col-span-1 {
            grid-column: span 1;
        }
    }

    /* 卡片悬停效果 */
    .card {
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }

    .card:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }

    /* 加载状态 */
    .loading-overlay {
        backdrop-filter: blur(2px);
    }
</style>