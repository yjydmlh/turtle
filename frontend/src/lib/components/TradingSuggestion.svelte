<script>
    import { tradingSuggestion, analysisStore, trendStatus, latestPrice } from '$lib/stores.js';
    import { formatPrice, formatTime } from '$lib/utils.js';
    import { AlertTriangle, TrendingUp, TrendingDown, Clock, Target, Shield, DollarSign } from 'lucide-svelte';

    // 响应式变量
    $: suggestion = $tradingSuggestion;
    $: analysis = $analysisStore;
    $: trend = $trendStatus;
    $: currentPrice = $latestPrice;

    // 获取建议类型的样式
    function getSuggestionStyle(action) {
        switch (action) {
            case 'buy':
                return {
                    bgColor: 'bg-bull-50',
                    textColor: 'text-bull-800',
                    borderColor: 'border-bull-200',
                    icon: TrendingUp,
                    iconColor: 'text-bull-600'
                };
            case 'sell':
                return {
                    bgColor: 'bg-bear-50',
                    textColor: 'text-bear-800',
                    borderColor: 'border-bear-200',
                    icon: TrendingDown,
                    iconColor: 'text-bear-600'
                };
            case 'wait':
            default:
                return {
                    bgColor: 'bg-yellow-50',
                    textColor: 'text-yellow-800',
                    borderColor: 'border-yellow-200',
                    icon: Clock,
                    iconColor: 'text-yellow-600'
                };
        }
    }

    // 获取信心度的样式
    function getConfidenceStyle(confidence) {
        switch (confidence) {
            case 'high':
                return {
                    color: 'text-bull-600',
                    bgColor: 'bg-bull-100',
                    text: '高'
                };
            case 'medium':
                return {
                    color: 'text-yellow-600',
                    bgColor: 'bg-yellow-100',
                    text: '中'
                };
            case 'low':
            default:
                return {
                    color: 'text-gray-600',
                    bgColor: 'bg-gray-100',
                    text: '低'
                };
        }
    }

    // 获取风险等级的样式
    function getRiskStyle(riskLevel) {
        switch (riskLevel) {
            case 'low':
                return {
                    color: 'text-bull-600',
                    bgColor: 'bg-bull-50',
                    text: '低风险'
                };
            case 'medium':
                return {
                    color: 'text-yellow-600',
                    bgColor: 'bg-yellow-50',
                    text: '中等风险'
                };
            case 'high':
            default:
                return {
                    color: 'text-bear-600',
                    bgColor: 'bg-bear-50',
                    text: '高风险'
                };
        }
    }

    // 计算建议的止损和止盈位
    function calculateLevels(action, price) {
        if (!price || action === 'wait') return null;

        const stopLossPercent = 0.02; // 2%止损
        const takeProfitPercent = 0.05; // 5%止盈

        if (action === 'buy') {
            return {
                stopLoss: price * (1 - stopLossPercent),
                takeProfit: price * (1 + takeProfitPercent)
            };
        } else if (action === 'sell') {
            return {
                stopLoss: price * (1 + stopLossPercent),
                takeProfit: price * (1 - takeProfitPercent)
            };
        }

        return null;
    }

    $: suggestionStyle = getSuggestionStyle(suggestion.action);
    $: confidenceStyle = getConfidenceStyle(suggestion.confidence);
    $: levels = calculateLevels(suggestion.action, currentPrice);

    // 处理建议操作
    function handleSuggestionAction(action) {
        // 触发自定义事件
        const event = new CustomEvent('tradingAction', {
            detail: {
                action,
                price: currentPrice,
                suggestion: suggestion,
                timestamp: new Date().toISOString()
            }
        });
        
        // 只在浏览器环境中触发事件
        if (typeof document !== 'undefined') {
            document.dispatchEvent(event);
        }
    }
</script>

<!-- 交易建议卡片 -->
<div class="space-y-4">
    <!-- 主要建议 -->
    <div class="border rounded-lg p-4 {suggestionStyle.bgColor} {suggestionStyle.borderColor}">
        <div class="flex items-start space-x-3">
            <!-- 建议图标 -->
            <div class="flex-shrink-0 mt-0.5">
                <svelte:component
                    this={suggestionStyle.icon}
                    class="w-5 h-5 {suggestionStyle.iconColor}"
                />
            </div>

            <!-- 建议内容 -->
            <div class="flex-1 space-y-2">
                <div class="flex items-center justify-between">
                    <h3 class="font-medium {suggestionStyle.textColor}">
                        {suggestion.action === 'buy' ? '买入建议' :
                         suggestion.action === 'sell' ? '卖出建议' : '等待建议'}
                    </h3>

                    <div class="flex items-center space-x-2">
                        <!-- 信心度 -->
                        <span class="px-2 py-1 text-xs font-medium rounded-full {confidenceStyle.bgColor} {confidenceStyle.color}">
                            {confidenceStyle.text}信心
                        </span>
                    </div>
                </div>

                <!-- 建议文本 -->
                <p class="text-sm {suggestionStyle.textColor}">
                    {suggestion.text}
                </p>

                <!-- 建议统计 -->
                <div class="flex items-center space-x-4 text-xs {suggestionStyle.textColor}">
                    {#if suggestion.buyPoints > 0}
                        <span class="flex items-center space-x-1">
                            <TrendingUp class="w-3 h-3" />
                            <span>{suggestion.buyPoints} 买点</span>
                        </span>
                    {/if}

                    {#if suggestion.sellPoints > 0}
                        <span class="flex items-center space-x-1">
                            <TrendingDown class="w-3 h-3" />
                            <span>{suggestion.sellPoints} 卖点</span>
                        </span>
                    {/if}

                    <span class="flex items-center space-x-1">
                        <Clock class="w-3 h-3" />
                        <span>{formatTime(suggestion.lastUpdate)}</span>
                    </span>
                </div>
            </div>
        </div>
    </div>

    <!-- 详细分析 -->
    <div class="space-y-3">
        <!-- 市场状态摘要 -->
        <div class="bg-gray-50 rounded-lg p-3">
            <h4 class="text-sm font-medium text-gray-900 mb-2">市场状态</h4>

            <div class="grid grid-cols-2 gap-3 text-sm">
                <!-- 趋势方向 -->
                <div class="space-y-1">
                    <div class="text-xs text-gray-600">趋势</div>
                    <div class="flex items-center space-x-1">
                        <span class="text-lg">{trend.icon}</span>
                        <span class="font-medium {
                            trend.direction === 'up' ? 'text-bull-600' :
                            trend.direction === 'down' ? 'text-bear-600' :
                            'text-gray-600'
                        }">
                            {trend.text}
                        </span>
                    </div>
                </div>

                <!-- 趋势强度 -->
                <div class="space-y-1">
                    <div class="text-xs text-gray-600">强度</div>
                    <div class="flex items-center space-x-2">
                        <div class="w-16 bg-gray-200 rounded-full h-2">
                            <div
                                class="h-2 rounded-full {
                                    trend.strength > 0.7 ? 'bg-bull-500' :
                                    trend.strength > 0.4 ? 'bg-yellow-500' :
                                    'bg-gray-400'
                                }"
                                style="width: {trend.strength * 100}%"
                            ></div>
                        </div>
                        <span class="text-xs font-medium">{(trend.strength * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 价格分析 -->
        {#if levels && suggestion.action !== 'wait'}
            <div class="bg-white border border-gray-200 rounded-lg p-3">
                <h4 class="text-sm font-medium text-gray-900 mb-2 flex items-center">
                    <Target class="w-4 h-4 mr-1" />
                    价格目标
                </h4>

                <div class="space-y-2">
                    <!-- 当前价格 -->
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-gray-600">当前价格</span>
                        <span class="font-mono font-semibold">{formatPrice(currentPrice, 2)}</span>
                    </div>

                    <!-- 止盈位 -->
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-gray-600">目标价位</span>
                        <span class="font-mono font-semibold text-bull-600">
                            {formatPrice(levels.takeProfit, 2)}
                        </span>
                    </div>

                    <!-- 止损位 -->
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-gray-600">止损价位</span>
                        <span class="font-mono font-semibold text-bear-600">
                            {formatPrice(levels.stopLoss, 2)}
                        </span>
                    </div>

                    <!-- 风险收益比 -->
                    <div class="pt-2 border-t border-gray-200">
                        <div class="flex items-center justify-between text-xs">
                            <span class="text-gray-500">风险收益比</span>
                            <span class="font-medium">1:2.5</span>
                        </div>
                    </div>
                </div>
            </div>
        {/if}

        <!-- 风险提示 -->
        <div class="bg-orange-50 border border-orange-200 rounded-lg p-3">
            <div class="flex items-start space-x-2">
                <AlertTriangle class="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
                <div class="space-y-1">
                    <h4 class="text-sm font-medium text-orange-900">风险提示</h4>
                    <ul class="text-xs text-orange-800 space-y-1">
                        <li>• 技术分析不能保证交易成功</li>
                        <li>• 请结合多种分析方法进行决策</li>
                        <li>• 建议设置止损，控制风险</li>
                        <li>• 不要投入超过承受能力的资金</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- 操作按钮 -->
        {#if suggestion.action !== 'wait'}
            <div class="grid grid-cols-2 gap-3">
                <button
                    on:click={() => handleSuggestionAction('accept')}
                    class="flex items-center justify-center space-x-2 py-2 px-4 text-sm font-medium rounded-lg {
                        suggestion.action === 'buy'
                            ? 'bg-bull-600 text-white hover:bg-bull-700'
                            : 'bg-bear-600 text-white hover:bg-bear-700'
                    } transition-colors"
                >
                    <DollarSign class="w-4 h-4" />
                    <span>
                        {suggestion.action === 'buy' ? '关注买入' : '关注卖出'}
                    </span>
                </button>

                <button
                    on:click={() => handleSuggestionAction('remind')}
                    class="flex items-center justify-center space-x-2 py-2 px-4 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                    <Clock class="w-4 h-4" />
                    <span>稍后提醒</span>
                </button>
            </div>
        {:else}
            <div class="text-center py-2">
                <button
                    on:click={() => handleSuggestionAction('refresh')}
                    class="text-sm text-gray-600 hover:text-gray-800 underline"
                >
                    刷新分析
                </button>
            </div>
        {/if}
    </div>

    <!-- 历史建议 -->
    <div class="border-t border-gray-200 pt-4">
        <h4 class="text-sm font-medium text-gray-900 mb-2">分析历史</h4>

        <div class="space-y-2 max-h-32 overflow-y-auto custom-scrollbar">
            <!-- 这里可以显示历史建议记录 -->
            <div class="text-xs text-gray-500 text-center py-4">
                暂无历史记录
            </div>
        </div>
    </div>

    <!-- 免责声明 -->
    <div class="text-xs text-gray-500 bg-gray-50 rounded p-2">
        <div class="flex items-start space-x-1">
            <Shield class="w-3 h-3 mt-0.5 flex-shrink-0" />
            <div>
                <strong>免责声明：</strong>
                本建议仅基于技术分析，不构成投资建议。
                投资有风险，入市需谨慎。请自行判断并承担投资风险。
            </div>
        </div>
    </div>
</div>

<style>
    /* 自定义滚动条 */
    .custom-scrollbar {
        scrollbar-width: thin;
        scrollbar-color: #cbd5e1 #f1f5f9;
    }

    .custom-scrollbar::-webkit-scrollbar {
        width: 4px;
    }

    .custom-scrollbar::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 2px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 2px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }

    /* 强度条动画 */
    .h-2 {
        transition: width 0.3s ease-in-out;
    }

    /* 按钮悬停效果 */
    button {
        transition: all 0.2s ease-in-out;
    }

    button:active {
        transform: translateY(0.5px);
    }

    /* 网格响应式调整 */
    @media (max-width: 640px) {
        .grid-cols-2 {
            grid-template-columns: 1fr;
            gap: 0.75rem;
        }
    }

    /* 聚焦样式 */
    button:focus-visible {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }

    /* 高对比度模式 */
    @media (prefers-contrast: high) {
        .border-gray-200 {
            border-color: #000;
            border-width: 2px;
        }

        .bg-gray-50 {
            background-color: #f9fafb;
            border: 1px solid #000;
        }
    }

    /* 打印样式 */
    @media print {
        .grid.grid-cols-2.gap-3,
        .border-t.border-gray-200.pt-4 {
            display: none;
        }

        .max-h-32 {
            max-height: none;
        }

        .overflow-y-auto {
            overflow: visible;
        }
    }

    /* 减少动画（用户偏好） */
    @media (prefers-reduced-motion: reduce) {
        .h-2,
        button {
            transition: none;
        }

        button:active {
            transform: none;
        }
    }
</style>