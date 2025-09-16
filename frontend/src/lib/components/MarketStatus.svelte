<script>
    import { latestPrice, priceChange, trendStatus, marketStore } from '$lib/stores.js';
    import { formatPrice, formatPercentage, formatVolume, formatTime, getTrendIcon } from '$lib/utils.js';
    import { TrendingUp, TrendingDown, Minus, Activity, Clock } from 'lucide-svelte';

    // 响应式变量
    $: price = $latestPrice;
    $: change = $priceChange;
    $: trend = $trendStatus;
    $: market = $marketStore;

    // 计算变化方向
    $: changeDirection = change.direction;
    $: changeClass = changeDirection === 'up' ? 'text-bull-600' :
                     changeDirection === 'down' ? 'text-bear-600' : 'text-gray-600';
    $: changeBgClass = changeDirection === 'up' ? 'bg-bull-50' :
                       changeDirection === 'down' ? 'bg-bear-50' : 'bg-gray-50';

    // 趋势强度颜色
    $: strengthColor = trend.strength > 0.7 ? (trend.direction === 'up' ? 'bg-bull-500' : 'bg-bear-500') :
                       trend.strength > 0.4 ? (trend.direction === 'up' ? 'bg-bull-400' : 'bg-bear-400') :
                       'bg-gray-400';

    // 价格闪烁效果
    let priceElement;
    let previousPrice = 0;

    $: if (price !== previousPrice && priceElement) {
        const flashClass = price > previousPrice ? 'price-flash-up' : 'price-flash-down';
        priceElement.classList.add(flashClass);
        setTimeout(() => {
            priceElement.classList.remove(flashClass);
        }, 300);
        previousPrice = price;
    }
</script>

<!-- 市场状态卡片 -->
<div class="space-y-4">
    <!-- 主要价格信息 -->
    <div class="text-center">
        <!-- 当前价格 -->
        <div class="space-y-2">
            <div
                bind:this={priceElement}
                class="text-3xl font-bold text-gray-900 font-mono transition-all duration-300"
            >
                {formatPrice(price, 2)}
            </div>

            <!-- 价格变化 -->
            <div class="flex items-center justify-center space-x-2">
                <div class="flex items-center space-x-1 {changeClass}">
                    {#if changeDirection === 'up'}
                        <TrendingUp class="w-4 h-4" />
                    {:else if changeDirection === 'down'}
                        <TrendingDown class="w-4 h-4" />
                    {:else}
                        <Minus class="w-4 h-4" />
                    {/if}
                    <span class="font-semibold">
                        {change.absolute >= 0 ? '+' : ''}{formatPrice(change.absolute, 2, '')}
                    </span>
                </div>

                <div class="px-2 py-1 rounded-full text-xs font-medium {changeBgClass} {changeClass}">
                    {formatPercentage(change.percent)}
                </div>
            </div>
        </div>
    </div>

    <!-- 趋势状态 -->
    <div class="bg-gray-50 rounded-lg p-3">
        <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">市场趋势</span>
            <span class="text-lg">{trend.icon}</span>
        </div>

        <div class="space-y-2">
            <!-- 趋势描述 -->
            <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">状态</span>
                <span class="text-sm font-medium {trend.color === 'green' ? 'text-bull-600' :
                                                     trend.color === 'red' ? 'text-bear-600' : 'text-gray-600'}">
                    {trend.text}
                </span>
            </div>

            <!-- 趋势强度条 -->
            <div class="space-y-1">
                <div class="flex items-center justify-between">
                    <span class="text-xs text-gray-500">强度</span>
                    <span class="text-xs text-gray-700">{(trend.strength * 100).toFixed(0)}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                        class="h-2 rounded-full transition-all duration-500 {strengthColor}"
                        style="width: {trend.strength * 100}%"
                    ></div>
                </div>
            </div>
        </div>
    </div>

    <!-- 24小时统计 -->
    {#if market.high24h || market.low24h || market.volume24h}
        <div class="space-y-3">
            <h4 class="text-sm font-medium text-gray-700 flex items-center">
                <Activity class="w-4 h-4 mr-1" />
                24小时统计
            </h4>

            <div class="grid grid-cols-2 gap-3 text-sm">
                <!-- 最高价 -->
                {#if market.high24h}
                    <div class="space-y-1">
                        <div class="text-xs text-gray-500">最高</div>
                        <div class="font-mono font-semibold text-gray-900">
                            {formatPrice(market.high24h, 2)}
                        </div>
                    </div>
                {/if}

                <!-- 最低价 -->
                {#if market.low24h}
                    <div class="space-y-1">
                        <div class="text-xs text-gray-500">最低</div>
                        <div class="font-mono font-semibold text-gray-900">
                            {formatPrice(market.low24h, 2)}
                        </div>
                    </div>
                {/if}

                <!-- 成交量 -->
                {#if market.volume24h}
                    <div class="space-y-1 col-span-2">
                        <div class="text-xs text-gray-500">成交量</div>
                        <div class="font-mono font-semibold text-gray-900">
                            {formatVolume(market.volume24h)} BTC
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    {/if}

    <!-- 价格区间指示器 -->
    <div class="space-y-2">
        <h4 class="text-sm font-medium text-gray-700">价格区间</h4>

        <!-- 价格区间条 -->
        {#if market.high24h && market.low24h}
            {@const range = market.high24h - market.low24h}
            {@const position = range > 0 ? ((price - market.low24h) / range) * 100 : 50}

            <div class="relative">
                <div class="w-full bg-gradient-to-r from-bear-200 via-gray-200 to-bull-200 rounded-full h-3">
                    <div
                        class="absolute top-0 w-2 h-3 bg-gray-800 rounded-full transform -translate-x-1/2 transition-all duration-500"
                        style="left: {Math.max(4, Math.min(96, position))}%"
                    ></div>
                </div>

                <div class="flex justify-between mt-1 text-xs text-gray-500">
                    <span>{formatPrice(market.low24h, 2)}</span>
                    <span>{formatPrice(market.high24h, 2)}</span>
                </div>
            </div>
        {:else}
            <div class="text-xs text-gray-500 text-center py-2">
                暂无24小时数据
            </div>
        {/if}
    </div>

    <!-- 支撑和阻力位 -->
    <div class="space-y-2">
        <h4 class="text-sm font-medium text-gray-700">关键价位</h4>

        <div class="space-y-2">
            <!-- 阻力位 -->
            <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">阻力位</span>
                <span class="font-mono text-bear-600">
                    {market.high24h ? formatPrice(market.high24h * 1.02, 2) : '计算中...'}
                </span>
            </div>

            <!-- 支撑位 -->
            <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">支撑位</span>
                <span class="font-mono text-bull-600">
                    {market.low24h ? formatPrice(market.low24h * 0.98, 2) : '计算中...'}
                </span>
            </div>
        </div>
    </div>

    <!-- 最后更新时间 -->
    <div class="pt-2 border-t border-gray-200">
        <div class="flex items-center justify-center space-x-1 text-xs text-gray-500">
            <Clock class="w-3 h-3" />
            <span>
                {#if market.lastUpdate}
                    更新: {formatTime(market.lastUpdate)}
                {:else}
                    等待数据更新...
                {/if}
            </span>
        </div>
    </div>

    <!-- 快速操作 -->
    <div class="grid grid-cols-2 gap-2">
        <button
            class="btn-sm bg-bull-50 text-bull-700 border-bull-200 hover:bg-bull-100 transition-colors"
            on:click={() => {
                // 触发买入提醒或操作
                const event = new CustomEvent('quickAction', {
                    detail: { action: 'buy', price }
                });
                
                // 只在浏览器环境中触发事件
                if (typeof document !== 'undefined') {
                    document.dispatchEvent(event);
                }
            }}
        >
            关注买点
        </button>

        <button
            class="btn-sm bg-bear-50 text-bear-700 border-bear-200 hover:bg-bear-100 transition-colors"
            on:click={() => {
                // 触发卖出提醒或操作
                const event = new CustomEvent('quickAction', {
                    detail: { action: 'sell', price }
                });
                
                // 只在浏览器环境中触发事件
                if (typeof document !== 'undefined') {
                    document.dispatchEvent(event);
                }
            }}
        >
            关注卖点
        </button>
    </div>
</div>

<style>
    /* 价格闪烁动画 */
    @keyframes price-flash-up {
        0% { background-color: transparent; }
        50% { background-color: rgba(34, 197, 94, 0.2); }
        100% { background-color: transparent; }
    }

    @keyframes price-flash-down {
        0% { background-color: transparent; }
        50% { background-color: rgba(239, 68, 68, 0.2); }
        100% { background-color: transparent; }
    }

    :global(.price-flash-up) {
        animation: price-flash-up 0.3s ease-in-out;
    }

    :global(.price-flash-down) {
        animation: price-flash-down 0.3s ease-in-out;
    }

    /* 趋势强度条动画 */
    .transition-all {
        transition: width 0.5s ease-in-out, background-color 0.3s ease-in-out;
    }

    /* 价格区间指示器动画 */
    .transform {
        transition: left 0.5s ease-in-out;
    }

    /* 响应式调整 */
    @media (max-width: 640px) {
        .text-3xl {
            font-size: 1.875rem;
            line-height: 2.25rem;
        }

        .grid-cols-2 {
            grid-template-columns: 1fr;
        }

        .col-span-2 {
            grid-column: span 1;
        }
    }

    /* 高对比度模式 */
    @media (prefers-contrast: high) {
        .bg-gray-50 {
            background-color: #f9fafb;
            border: 1px solid #000;
        }

        .text-gray-600 {
            color: #000;
        }
    }

    /* 深色模式准备 */
    @media (prefers-color-scheme: dark) {
        .bg-gray-50 {
            background-color: #1f2937;
        }

        .text-gray-900 {
            color: #f9fafb;
        }

        .text-gray-600 {
            color: #d1d5db;
        }

        .text-gray-500 {
            color: #9ca3af;
        }
    }

    /* 打印样式 */
    @media print {
        .grid.grid-cols-2.gap-2 {
            display: none;
        }
    }

    /* 减少动画（用户偏好） */
    @media (prefers-reduced-motion: reduce) {
        .transition-all,
        .transform,
        :global(.price-flash-up),
        :global(.price-flash-down) {
            transition: none;
            animation: none;
        }
    }
</style>