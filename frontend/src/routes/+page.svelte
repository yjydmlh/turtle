<script>
	// 使用动态导入优化组件加载
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	
	// 核心组件 - 立即导入
	import FloatingToolbar from '$lib/components/FloatingToolbar.svelte';
	import DraggablePanel from '$lib/components/DraggablePanel.svelte';
	import LazyLoader from '$lib/components/LazyLoader.svelte';
	
	// 图标 - 按需导入
	let TrendingUp, Activity, Database, RefreshCw, Download;
	let iconsLoaded = false;
	
	// 异步加载图标
	async function loadIcons() {
		if (iconsLoaded || typeof window === 'undefined') return;
		try {
			const icons = await import('lucide-svelte');
			TrendingUp = icons.TrendingUp;
			Activity = icons.Activity;
			Database = icons.Database;
			RefreshCw = icons.RefreshCw;
			Download = icons.Download;
			iconsLoaded = true;
		} catch (error) {
			console.error('Failed to load icons:', error);
		}
	}
	
	// 临时组件占位符
	const ControlPanel = 'div';
	const MarketStatus = 'div';
	const FenxingAnalysis = 'div';
	const TradingPanel = 'div';
	const FenxingList = 'div';
	const TradingSuggestion = 'div';
	
	// 临时store占位符 - 修复订阅问题
	const loadingStore = writable(false);
	const errorStore = writable(null);
	
	// 面板状态管理
	let panels = {
		control: false,
		market: false,
		fenxing: false,
		trading: false
	};
	
	// 其他状态变量
	let chanModuleInfo = null;
	let useDatabase = false;
	let loading = false;
	let selectedSymbol = 'BTCUSDT';
	let selectedTimeframe = '1h';
	
	// 面板切换处理函数
	function handlePanelToggle(event) {
		const { panelType } = event.detail;
		panels[panelType] = !panels[panelType];
	}
	
	// 数据加载函数
	function loadData() {
		loading = true;
		// TODO: 实现数据加载逻辑
		setTimeout(() => {
			loading = false;
		}, 1000);
	}
	
	// 获取新数据函数
	function handleFetchNewData() {
		loading = true;
		// TODO: 实现获取新数据逻辑
		setTimeout(() => {
			loading = false;
		}, 1000);
	}
	
	// 组件初始化
	onMount(async () => {
		// 加载图标
		await loadIcons();
	});
	function handleTimeframeChange() {
		// TODO: 实现时间框架变化逻辑
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
                        {#if TrendingUp}
                            <TrendingUp class="w-6 h-6 text-white" />
                        {:else}
                            <!-- SSR 兼容的占位符 -->
                            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                            </svg>
                        {/if}
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
                                {#if Activity}
                                    <Activity class="w-4 h-4 {chanModuleInfo.chan_module.is_available ? 'text-bull-500' : 'text-yellow-500'}" />
                                {:else}
                                    <svg class="w-4 h-4 {chanModuleInfo.chan_module.is_available ? 'text-bull-500' : 'text-yellow-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                                    </svg>
                                {/if}
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
                            {#if Database}
                                <Database class="w-4 h-4 mr-1" />
                            {:else}
                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/>
                                </svg>
                            {/if}
                            <span class="hidden sm:inline">{useDatabase ? '数据库' : '缠论'}</span>
                        </button>

                        <button
                            on:click={loadData}
                            disabled={loading}
                            class="btn-secondary btn-sm"
                            title="刷新数据"
                        >
                            {#if RefreshCw}
                                <RefreshCw class="w-4 h-4 mr-1 {loading ? 'animate-spin' : ''}" />
                            {:else}
                                <svg class="w-4 h-4 mr-1 {loading ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                                </svg>
                            {/if}
                            <span class="hidden sm:inline">刷新</span>
                        </button>

                        <button
                            on:click={handleFetchNewData}
                            disabled={loading}
                            class="btn-primary btn-sm"
                            title="获取新数据"
                        >
                            {#if Download}
                                <Download class="w-4 h-4 mr-1" />
                            {:else}
                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                                </svg>
                            {/if}
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

        <!-- K线图表区域 -->
        <div class="flex-1 relative">
            <LazyLoader 
                component={() => import('$lib/components/KLineChart.svelte')}
                loadingText="加载K线图表中..."
            />
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
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold">控制面板</h3>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium mb-1">交易对</label>
                            <select bind:value={selectedSymbol} class="w-full p-2 border rounded">
                                <option value="BTCUSDT">BTC/USDT</option>
                                <option value="ETHUSDT">ETH/USDT</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-1">时间周期</label>
                            <select bind:value={selectedTimeframe} class="w-full p-2 border rounded">
                                <option value="1h">1小时</option>
                                <option value="4h">4小时</option>
                                <option value="1d">1天</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <input type="checkbox" bind:checked={useDatabase} id="useDb" />
                        <label for="useDb" class="text-sm">使用数据库</label>
                    </div>
                    <div class="flex space-x-2">
                        <button on:click={loadData} class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                            加载数据
                        </button>
                        <button on:click={handleFetchNewData} class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
                            获取新数据
                        </button>
                    </div>
                </div>
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
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold">市场状态</h3>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-green-100 p-3 rounded">
                            <div class="text-sm text-gray-600">BTC价格</div>
                            <div class="text-lg font-bold text-green-600">$45,230</div>
                        </div>
                        <div class="bg-blue-100 p-3 rounded">
                            <div class="text-sm text-gray-600">24h变化</div>
                            <div class="text-lg font-bold text-blue-600">+2.34%</div>
                        </div>
                    </div>
                    <div class="text-sm text-gray-500">
                        最后更新: {new Date().toLocaleTimeString()}
                    </div>
                </div>
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
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold">分型列表</h3>
                    <div class="space-y-2">
                        <div class="border rounded p-3">
                            <div class="flex justify-between items-center">
                                <span class="font-medium">顶分型</span>
                                <span class="text-red-500">45,500</span>
                            </div>
                            <div class="text-sm text-gray-500">2024-01-15 14:30</div>
                        </div>
                        <div class="border rounded p-3">
                            <div class="flex justify-between items-center">
                                <span class="font-medium">底分型</span>
                                <span class="text-green-500">44,200</span>
                            </div>
                            <div class="text-sm text-gray-500">2024-01-15 12:15</div>
                        </div>
                        <div class="border rounded p-3">
                            <div class="flex justify-between items-center">
                                <span class="font-medium">顶分型</span>
                                <span class="text-red-500">44,800</span>
                            </div>
                            <div class="text-sm text-gray-500">2024-01-15 10:45</div>
                        </div>
                    </div>
                </div>
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
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold">交易建议</h3>
                    <div class="space-y-3">
                        <div class="bg-green-50 border border-green-200 rounded p-3">
                            <div class="flex items-center justify-between">
                                <span class="font-medium text-green-800">买入信号</span>
                                <span class="text-sm text-green-600">强度: 85%</span>
                            </div>
                            <div class="text-sm text-green-700 mt-1">
                                价格突破关键阻力位，建议在44,500附近买入
                            </div>
                        </div>
                        <div class="bg-yellow-50 border border-yellow-200 rounded p-3">
                            <div class="flex items-center justify-between">
                                <span class="font-medium text-yellow-800">观望</span>
                                <span class="text-sm text-yellow-600">强度: 60%</span>
                            </div>
                            <div class="text-sm text-yellow-700 mt-1">
                                当前处于震荡区间，等待明确方向
                            </div>
                        </div>
                        <div class="bg-blue-50 border border-blue-200 rounded p-3">
                            <div class="text-sm text-blue-700">
                                <strong>风险提示:</strong> 请注意仓位管理，设置止损位
                            </div>
                        </div>
                    </div>
                </div>
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