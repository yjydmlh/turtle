<script>
    import { createEventDispatcher } from 'svelte';
    import { settingsStore, loadingStore, connectionStore } from '$lib/stores.js';
    import { getTimeframeText } from '$lib/utils.js';
    import { Settings, RefreshCw, TrendingUp, BarChart, Eye, EyeOff, Download } from 'lucide-svelte';

    const dispatch = createEventDispatcher();

    // 时间周期选项
    const timeframeOptions = [
        { value: '1m', label: '1分钟', description: '短期波动' },
        { value: '5m', label: '5分钟', description: '精确分析' },
        { value: '15m', label: '15分钟', description: '短期趋势' },
        { value: '30m', label: '30分钟', description: '中短期' },
        { value: '1h', label: '1小时', description: '标准分析' },
        { value: '4h', label: '4小时', description: '中期趋势' },
        { value: '1d', label: '1天', description: '长期趋势' }
    ];

    // 数据量选项
    const dataCountOptions = [
        { value: 100, label: '100条', description: '快速' },
        { value: 200, label: '200条', description: '标准' },
        { value: 300, label: '300条', description: '详细' },
        { value: 500, label: '500条', description: '深度' }
    ];

    // 本地状态
    let isSettingsOpen = false;
    let isAdvancedOpen = false;

    // 响应式变量
    $: currentTimeframe = $settingsStore.timeframe;
    $: currentDataCount = $settingsStore.dataCount;
    $: isLoading = $loadingStore;
    $: connectionStatus = $connectionStore;

    // 处理时间周期变化
    function handleTimeframeChange(newTimeframe) {
        if (newTimeframe !== currentTimeframe) {
            settingsStore.update(settings => ({
                ...settings,
                timeframe: newTimeframe
            }));

            dispatch('change', {
                type: 'timeframe',
                value: newTimeframe
            });
        }
    }

    // 处理数据量变化
    function handleDataCountChange(newCount) {
        if (newCount !== currentDataCount) {
            settingsStore.update(settings => ({
                ...settings,
                dataCount: newCount
            }));

            dispatch('change', {
                type: 'dataCount',
                value: newCount
            });
        }
    }

    // 切换显示选项
    function toggleDisplayOption(option) {
        settingsStore.update(settings => ({
            ...settings,
            [option]: !settings[option]
        }));

        dispatch('change', {
            type: 'display',
            option,
            value: !$settingsStore[option]
        });
    }

    // 刷新数据
    function handleRefresh() {
        dispatch('refresh');
    }

    // 获取数据
    function handleFetchData() {
        dispatch('fetchData');
    }

    // 重置设置
    function resetSettings() {
        settingsStore.update(settings => ({
            ...settings,
            timeframe: '1h',
            dataCount: 200,
            showFenxings: true,
            showBis: true,
            showBuySellPoints: true
        }));

        dispatch('change', {
            type: 'reset'
        });
    }

    // 键盘快捷键
    function handleKeydown(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'r':
                    event.preventDefault();
                    handleRefresh();
                    break;
                case 'd':
                    event.preventDefault();
                    handleFetchData();
                    break;
                case ',':
                    event.preventDefault();
                    isSettingsOpen = !isSettingsOpen;
                    break;
            }
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- 控制面板容器 -->
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
    <!-- 主控制行 -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0 lg:space-x-4">

        <!-- 左侧：时间周期和数据量 -->
        <div class="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">

            <!-- 时间周期选择 -->
            <div class="flex flex-col space-y-1">
                <label class="text-sm font-medium text-gray-700">时间周期</label>
                <div class="flex flex-wrap gap-1">
                    {#each timeframeOptions as option}
                        <button
                            on:click={() => handleTimeframeChange(option.value)}
                            class="px-3 py-1.5 text-xs font-medium rounded-lg border transition-all {
                                currentTimeframe === option.value
                                    ? 'bg-chan-600 text-white border-chan-600 shadow-sm'
                                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                            }"
                            disabled={isLoading}
                            title={option.description}
                        >
                            {option.label}
                        </button>
                    {/each}
                </div>
            </div>

            <!-- 数据量选择 -->
            <div class="flex flex-col space-y-1">
                <label class="text-sm font-medium text-gray-700">数据量</label>
                <select
                    bind:value={currentDataCount}
                    on:change={(e) => handleDataCountChange(parseInt(e.target.value))}
                    disabled={isLoading}
                    class="form-select text-sm py-1.5 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chan-500 focus:border-chan-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {#each dataCountOptions as option}
                        <option value={option.value}>{option.label}</option>
                    {/each}
                </select>
            </div>
        </div>

        <!-- 中间：显示选项 -->
        <div class="flex flex-wrap items-center gap-2 lg:gap-3">
            <div class="hidden sm:block text-sm font-medium text-gray-700">显示：</div>

            <!-- 分型显示 -->
            <button
                on:click={() => toggleDisplayOption('showFenxings')}
                class="flex items-center space-x-1 px-2 py-1 text-xs font-medium rounded-md border transition-all {
                    $settingsStore.showFenxings
                        ? 'bg-bull-50 text-bull-700 border-bull-200'
                        : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
                }"
                title="显示/隐藏分型标记"
            >
                {#if $settingsStore.showFenxings}
                    <Eye class="w-3 h-3" />
                {:else}
                    <EyeOff class="w-3 h-3" />
                {/if}
                <span>分型</span>
            </button>

            <!-- 笔显示 -->
            <button
                on:click={() => toggleDisplayOption('showBis')}
                class="flex items-center space-x-1 px-2 py-1 text-xs font-medium rounded-md border transition-all {
                    $settingsStore.showBis
                        ? 'bg-purple-50 text-purple-700 border-purple-200'
                        : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
                }"
                title="显示/隐藏笔的连线"
            >
                {#if $settingsStore.showBis}
                    <Eye class="w-3 h-3" />
                {:else}
                    <EyeOff class="w-3 h-3" />
                {/if}
                <span>笔</span>
            </button>

            <!-- 买卖点显示 -->
            <button
                on:click={() => toggleDisplayOption('showBuySellPoints')}
                class="flex items-center space-x-1 px-2 py-1 text-xs font-medium rounded-md border transition-all {
                    $settingsStore.showBuySellPoints
                        ? 'bg-yellow-50 text-yellow-700 border-yellow-200'
                        : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
                }"
                title="显示/隐藏买卖点标记"
            >
                {#if $settingsStore.showBuySellPoints}
                    <Eye class="w-3 h-3" />
                {:else}
                    <EyeOff class="w-3 h-3" />
                {/if}
                <span>买卖点</span>
            </button>
        </div>

        <!-- 右侧：操作按钮 -->
        <div class="flex items-center space-x-2">
            <!-- 刷新按钮 -->
            <button
                on:click={handleRefresh}
                disabled={isLoading}
                class="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                title="刷新数据 (Ctrl+R)"
            >
                <RefreshCw class="w-4 h-4 {isLoading ? 'animate-spin' : ''}" />
                <span class="hidden sm:inline">刷新</span>
            </button>

            <!-- 获取新数据按钮 -->
            <button
                on:click={handleFetchData}
                disabled={isLoading}
                class="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-white bg-chan-600 border border-chan-600 rounded-lg hover:bg-chan-700 hover:border-chan-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                title="从币安获取新数据 (Ctrl+D)"
            >
                <Download class="w-4 h-4" />
                <span>获取数据</span>
            </button>

            <!-- 设置按钮 -->
            <button
                on:click={() => isSettingsOpen = !isSettingsOpen}
                class="flex items-center justify-center w-9 h-9 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 transition-all"
                title="打开设置 (Ctrl+,)"
            >
                <Settings class="w-4 h-4" />
            </button>
        </div>
    </div>

    <!-- 连接状态指示器 -->
    <div class="mt-3 flex items-center justify-between">
        <div class="flex items-center space-x-4 text-xs text-gray-600">
            <!-- API连接状态 -->
            <div class="flex items-center space-x-1">
                <div class="w-2 h-2 rounded-full {
                    connectionStatus.apiStatus === 'online' ? 'bg-bull-500 animate-pulse' :
                    connectionStatus.apiStatus === 'error' ? 'bg-bear-500' :
                    'bg-yellow-500'
                }"></div>
                <span>API: {
                    connectionStatus.apiStatus === 'online' ? '在线' :
                    connectionStatus.apiStatus === 'error' ? '错误' :
                    '未知'
                }</span>
            </div>

            <!-- 网络状态 -->
            <div class="flex items-center space-x-1">
                <div class="w-2 h-2 rounded-full {connectionStatus.isOnline ? 'bg-bull-500' : 'bg-bear-500'}"></div>
                <span>网络: {connectionStatus.isOnline ? '已连接' : '断开'}</span>
            </div>

            <!-- 最后更新时间 -->
            {#if connectionStatus.lastPing}
                <span>更新: {new Date(connectionStatus.lastPing).toLocaleTimeString('zh-CN')}</span>
            {/if}
        </div>

        <!-- 当前配置摘要 -->
        <div class="text-xs text-gray-500">
            {getTimeframeText(currentTimeframe)} · {currentDataCount}条数据
        </div>
    </div>

    <!-- 设置面板 -->
    {#if isSettingsOpen}
        <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold text-gray-900">高级设置</h3>
                <button
                    on:click={() => isSettingsOpen = false}
                    class="text-gray-400 hover:text-gray-600 transition-colors"
                >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- 自动刷新设置 -->
                <div class="space-y-2">
                    <label class="flex items-center space-x-2">
                        <input
                            type="checkbox"
                            bind:checked={$settingsStore.autoRefresh}
                            on:change={(e) => {
                                settingsStore.update(s => ({...s, autoRefresh: e.target.checked}));
                                dispatch('change', { type: 'autoRefresh', value: e.target.checked });
                            }}
                            class="rounded border-gray-300 text-chan-600 focus:ring-chan-500"
                        />
                        <span class="text-sm text-gray-700">自动刷新</span>
                    </label>

                    {#if $settingsStore.autoRefresh}
                        <div class="ml-6">
                            <label class="block text-xs text-gray-600 mb-1">刷新间隔（秒）</label>
                            <select
                                bind:value={$settingsStore.refreshInterval}
                                on:change={(e) => {
                                    settingsStore.update(s => ({...s, refreshInterval: parseInt(e.target.value)}));
                                    dispatch('change', { type: 'refreshInterval', value: parseInt(e.target.value) });
                                }}
                                class="form-select text-xs w-full"
                            >
                                <option value={10000}>10秒</option>
                                <option value={30000}>30秒</option>
                                <option value={60000}>1分钟</option>
                                <option value={300000}>5分钟</option>
                            </select>
                        </div>
                    {/if}
                </div>

                <!-- 声音提醒设置 -->
                <div class="space-y-2">
                    <label class="flex items-center space-x-2">
                        <input
                            type="checkbox"
                            bind:checked={$settingsStore.soundAlerts}
                            on:change={(e) => {
                                settingsStore.update(s => ({...s, soundAlerts: e.target.checked}));
                                dispatch('change', { type: 'soundAlerts', value: e.target.checked });
                            }}
                            class="rounded border-gray-300 text-chan-600 focus:ring-chan-500"
                        />
                        <span class="text-sm text-gray-700">声音提醒</span>
                    </label>

                    <p class="text-xs text-gray-500 ml-6">
                        在发现重要信号时播放提示音
                    </p>
                </div>
            </div>

            <!-- 快捷键说明 -->
            <div class="mt-4 p-3 bg-white rounded border border-gray-200">
                <h4 class="text-xs font-semibold text-gray-700 mb-2">快捷键</h4>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-gray-600">
                    <div><kbd class="bg-gray-100 px-1 rounded">Ctrl+R</kbd> 刷新数据</div>
                    <div><kbd class="bg-gray-100 px-1 rounded">Ctrl+D</kbd> 获取新数据</div>
                    <div><kbd class="bg-gray-100 px-1 rounded">Ctrl+,</kbd> 打开设置</div>
                    <div><kbd class="bg-gray-100 px-1 rounded">Esc</kbd> 关闭面板</div>
                </div>
            </div>

            <!-- 重置按钮 -->
            <div class="mt-4 flex justify-end">
                <button
                    on:click={resetSettings}
                    class="text-xs text-gray-600 hover:text-gray-800 underline transition-colors"
                >
                    重置所有设置
                </button>
            </div>
        </div>
    {/if}
</div>

<style>
    /* 自定义样式 */
    kbd {
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 0.75rem;
        padding: 0.125rem 0.25rem;
        border-radius: 0.25rem;
        background-color: #f3f4f6;
        border: 1px solid #d1d5db;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    /* 响应式调整 */
    @media (max-width: 640px) {
        .grid.grid-cols-1.sm\\:grid-cols-2 {
            grid-template-columns: 1fr;
        }
    }

    /* 聚焦样式 */
    button:focus-visible {
        outline: 2px solid #2563eb;
        outline-offset: 2px;
    }

    /* 禁用状态 */
    button:disabled {
        cursor: not-allowed;
        opacity: 0.6;
    }

    /* 动画效果 */
    .transition-all {
        transition-property: all;
        transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
        transition-duration: 150ms;
    }

    /* 高对比度模式支持 */
    @media (prefers-contrast: high) {
        .border-gray-200 {
            border-color: #000;
            border-width: 2px;
        }

        .bg-white {
            background-color: #fff;
            color: #000;
        }
    }
</style>