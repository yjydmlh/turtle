<script>
    import '../app.css';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { errorStore } from '$lib/stores.js';

    // 错误显示状态
    let showError = false;
    let errorMessage = '';

    // 订阅错误状态
    errorStore.subscribe(error => {
        if (error) {
            errorMessage = error;
            showError = true;
            // 5秒后自动隐藏错误
            setTimeout(() => {
                showError = false;
                errorStore.set(null);
            }, 5000);
        }
    });

    onMount(() => {
        console.log('🐢 缠论分析系统前端启动');
        console.log('📍 当前页面:', $page.url.pathname);

        // 检查浏览器兼容性
        checkBrowserCompatibility();

        // 设置全局错误处理
        window.addEventListener('unhandledrejection', handleUnhandledRejection);

        return () => {
            window.removeEventListener('unhandledrejection', handleUnhandledRejection);
        };
    });

    function checkBrowserCompatibility() {
        const requiredFeatures = [
            'fetch',
            'Promise',
            'localStorage',
            'sessionStorage'
        ];

        const missingFeatures = requiredFeatures.filter(feature => !(feature in window));

        if (missingFeatures.length > 0) {
            console.warn('浏览器兼容性警告:', missingFeatures);
            errorStore.set(`浏览器不支持某些功能: ${missingFeatures.join(', ')}`);
        }
    }

    function handleUnhandledRejection(event) {
        console.error('未处理的Promise拒绝:', event.reason);
        errorStore.set(`网络或系统错误: ${event.reason?.message || '未知错误'}`);
    }

    function dismissError() {
        showError = false;
        errorStore.set(null);
    }
</script>

<!-- 全局SEO设置 -->
<svelte:head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#2563eb">
</svelte:head>

<!-- 全局错误提示 -->
{#if showError}
    <div class="fixed top-4 right-4 z-50 max-w-md animate-slideDown">
        <div class="bg-bear-50 border-l-4 border-bear-400 p-4 rounded-lg shadow-lg">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-bear-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3 flex-1">
                    <p class="text-sm text-bear-700 font-medium">
                        系统提示
                    </p>
                    <p class="text-sm text-bear-600 mt-1">
                        {errorMessage}
                    </p>
                </div>
                <div class="ml-4 flex-shrink-0">
                    <button
                        type="button"
                        class="text-bear-400 hover:text-bear-600 focus:outline-none"
                        on:click={dismissError}
                    >
                        <span class="sr-only">关闭</span>
                        <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- 主要内容区域 -->
<main class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
    <slot />
</main>

<!-- 全局样式 -->
<style>
    :global(body) {
        margin: 0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* 全局过渡动画 */
    :global(.page-transition) {
        transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
    }

    /* 全局加载状态 */
    :global(.global-loading) {
        pointer-events: none;
        opacity: 0.7;
    }

    /* 响应式字体大小调整 */
    @media (max-width: 640px) {
        :global(html) {
            font-size: 14px;
        }
    }

    /* 高对比度模式 */
    @media (prefers-contrast: high) {
        :global(.card) {
            border-width: 2px;
            border-color: #000;
        }
    }

    /* 打印样式 */
    @media print {
        :global(.no-print) {
            display: none !important;
        }

        :global(body) {
            background: white !important;
            color: black !important;
        }
    }
</style>