<script>
    import { createEventDispatcher } from 'svelte';
    import { Settings, BarChart3, TrendingUp, Target, RefreshCw, Database, Move, ChevronLeft, ChevronRight } from 'lucide-svelte';

    const dispatch = createEventDispatcher();

    // 工具栏按钮配置
    const toolbarButtons = [
        {
            id: 'control',
            icon: Settings,
            label: '控制面板',
            description: '交易对选择、时间周期设置'
        },
        {
            id: 'market',
            icon: BarChart3,
            label: '市场状态',
            description: '实时价格、涨跌幅、成交量'
        },
        {
            id: 'fenxing',
            icon: TrendingUp,
            label: '分型列表',
            description: '缠论分型识别结果'
        },
        {
            id: 'trading',
            icon: Target,
            label: '交易建议',
            description: '基于缠论的交易策略建议'
        }
    ];

    let activeTooltip = null;
    let tooltipTimeout = null;
    let isCollapsed = false;
    
    // 拖拽相关变量
    let isDragging = false;
    let toolbarX = 0; // 初始化为0，在客户端设置
    let toolbarY = 0; // 初始化为0，在客户端设置
    let dragStartX = 0;
    let dragStartY = 0;
    let animationFrameId = null;
    let lastDragTime = 0;
    const DRAG_THROTTLE_MS = 16; // 约60fps

    // 客户端初始化位置
    import { onMount } from 'svelte';
    onMount(() => {
        toolbarX = window.innerWidth - 100;
        toolbarY = window.innerHeight / 2 - 120;
    });

    // 拖拽功能
    function startDrag(event) {
        if (event.target.closest('.toolbar-button') || event.target.closest('.collapse-button')) {
            return; // 如果点击的是按钮，不启动拖拽
        }
        
        isDragging = true;
        dragStartX = event.clientX - toolbarX;
        dragStartY = event.clientY - toolbarY;
        
        // 添加拖拽状态类
        const toolbar = event.currentTarget;
        toolbar.classList.add('dragging');
        
        // 只在浏览器环境中添加事件监听器
        if (typeof document !== 'undefined') {
            document.addEventListener('mousemove', handleDragThrottled, { passive: true });
            document.addEventListener('mouseup', stopDrag, { passive: true });
        }
        event.preventDefault();
    }

    // 节流处理的拖拽函数
    function handleDragThrottled(event) {
        if (!isDragging) return;
        
        const now = performance.now();
        if (now - lastDragTime < DRAG_THROTTLE_MS) {
            return;
        }
        lastDragTime = now;
        
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        
        animationFrameId = requestAnimationFrame(() => {
            handleDrag(event);
            animationFrameId = null;
        });
    }

    function handleDrag(event) {
        if (!isDragging) return;
        
        const newX = event.clientX - dragStartX;
        const newY = event.clientY - dragStartY;
        
        // 边界检查
        const toolbarWidth = isCollapsed ? 60 : 80;
        const toolbarHeight = isCollapsed ? 60 : (toolbarButtons.length * 60 + 80);
        
        toolbarX = Math.max(0, Math.min(newX, window.innerWidth - toolbarWidth));
        toolbarY = Math.max(0, Math.min(newY, window.innerHeight - toolbarHeight));
    }

    function stopDrag() {
        isDragging = false;
        
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
        
        // 移除拖拽状态类
        if (typeof document !== 'undefined') {
            const toolbar = document.querySelector('.floating-toolbar');
            if (toolbar) {
                toolbar.classList.remove('dragging');
            }
            
            document.removeEventListener('mousemove', handleDragThrottled);
            document.removeEventListener('mouseup', stopDrag);
        }
    }

    function handleButtonClick(buttonId) {
        // 隐藏tooltip
        hideTooltip();
        
        // 分发面板切换事件
        dispatch('panelToggle', {
            panelType: buttonId
        });
    }

    function showTooltip(buttonId) {
        if (tooltipTimeout) {
            clearTimeout(tooltipTimeout);
        }
        tooltipTimeout = setTimeout(() => {
            activeTooltip = buttonId;
        }, 500);
    }

    function hideTooltip() {
        if (tooltipTimeout) {
            clearTimeout(tooltipTimeout);
        }
        activeTooltip = null;
    }

    function toggleCollapse() {
        isCollapsed = !isCollapsed;
        hideTooltip(); // 收缩时隐藏tooltip
    }

    // 响应式调整
    function handleWindowResize() {
        const toolbarWidth = isCollapsed ? 60 : 80;
        const toolbarHeight = isCollapsed ? 60 : (toolbarButtons.length * 60 + 80);
        
        toolbarX = Math.max(0, Math.min(toolbarX, window.innerWidth - toolbarWidth));
        toolbarY = Math.max(0, Math.min(toolbarY, window.innerHeight - toolbarHeight));
    }

    // 生命周期
    $: if (typeof window !== 'undefined') {
        window.addEventListener('resize', handleWindowResize);
    }
</script>

<!-- 浮动工具栏 -->
<div
    class="floating-toolbar {isCollapsed ? 'collapsed' : ''} {isDragging ? 'dragging' : ''}"
    style="left: {toolbarX}px; top: {toolbarY}px;"
    on:mousedown={startDrag}
>
    <!-- 拖拽手柄 -->
    <div class="drag-handle">
        <Move class="w-4 h-4 text-gray-400" />
    </div>

    <!-- 展开/收缩按钮 -->
    <button class="collapse-button" on:click={toggleCollapse} title={isCollapsed ? '展开工具栏' : '收缩工具栏'}>
        {#if isCollapsed}
            <ChevronLeft class="w-4 h-4" />
        {:else}
            <ChevronRight class="w-4 h-4" />
        {/if}
    </button>

    <!-- 工具栏按钮 -->
    {#if !isCollapsed}
        {#each toolbarButtons as button}
            <div class="toolbar-button-container">
                <button
                    class="toolbar-button"
                    on:click={() => handleButtonClick(button.id)}
                    on:mouseenter={() => showTooltip(button.id)}
                    on:mouseleave={hideTooltip}
                    title={button.label}
                >
                    <svelte:component this={button.icon} class="w-5 h-5" />
                </button>
                
                <!-- Tooltip -->
                {#if activeTooltip === button.id}
                    <div class="tooltip">
                        <div class="tooltip-title">{button.label}</div>
                        <div class="tooltip-description">{button.description}</div>
                    </div>
                {/if}
            </div>
        {/each}
    {/if}
</div>

<style>
    .floating-toolbar {
        position: fixed;
        z-index: 100;
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.2);
        cursor: move;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        user-select: none;
        min-width: 72px;
        /* 硬件加速优化 */
        will-change: transform;
        transform: translate3d(0, 0, 0);
    }

    .floating-toolbar.collapsed {
        padding: 8px;
        min-width: 48px;
    }

    .floating-toolbar.dragging {
        cursor: grabbing;
        transform: scale(1.02) translate3d(0, 0, 0);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        /* 拖拽时禁用过渡动画 */
        transition: none;
    }

    .drag-handle {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 24px;
        border-radius: 8px;
        background: rgba(0, 0, 0, 0.05);
        cursor: grab;
        transition: background 0.2s ease;
    }

    .drag-handle:hover {
        background: rgba(0, 0, 0, 0.1);
    }

    .drag-handle:active {
        cursor: grabbing;
    }

    .collapse-button {
        width: 32px;
        height: 32px;
        border: none;
        border-radius: 8px;
        background: rgba(0, 0, 0, 0.05);
        color: #6b7280;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 4px;
    }

    .collapse-button:hover {
        background: rgba(0, 0, 0, 0.1);
        color: #374151;
    }

    .toolbar-button-container {
        position: relative;
    }

    .toolbar-button {
        width: 48px;
        height: 48px;
        border: none;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transform: translateZ(0); /* 启用硬件加速 */
    }

    .toolbar-button:hover {
        transform: translateY(-2px) scale(1.05) translateZ(0);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }

    .toolbar-button:active {
        transform: translateY(0) scale(0.98) translateZ(0);
    }

    .tooltip {
        position: absolute;
        left: -200px;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 13px;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        animation: tooltipFadeIn 0.2s ease;
        pointer-events: none;
        min-width: 180px;
        z-index: 1001;
    }

    .tooltip::after {
        content: '';
        position: absolute;
        right: -6px;
        top: 50%;
        transform: translateY(-50%);
        border: 6px solid transparent;
        border-left-color: rgba(0, 0, 0, 0.9);
    }

    .tooltip-title {
        font-weight: 600;
        margin-bottom: 4px;
        color: #ffffff;
    }

    .tooltip-description {
        font-size: 12px;
        color: #d1d5db;
        line-height: 1.4;
    }

    @keyframes tooltipFadeIn {
        from {
            opacity: 0;
            transform: translateY(-50%) translateX(10px);
        }
        to {
            opacity: 1;
            transform: translateY(-50%) translateX(0);
        }
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .floating-toolbar {
            padding: 8px;
            gap: 6px;
            min-width: 56px;
        }

        .floating-toolbar.collapsed {
            padding: 6px;
            min-width: 40px;
        }

        .toolbar-button {
            width: 40px;
            height: 40px;
            border-radius: 10px;
        }

        .collapse-button {
            width: 28px;
            height: 28px;
        }

        .tooltip {
            left: -160px;
            min-width: 140px;
            padding: 10px 12px;
            font-size: 12px;
        }

        .tooltip-description {
            font-size: 11px;
        }
    }

    /* 高对比度模式 */
    @media (prefers-contrast: high) {
        .floating-toolbar {
            background: white;
            border: 2px solid #000;
        }

        .toolbar-button {
            background: #000;
            color: white;
            border: 1px solid #333;
        }

        .toolbar-button:hover {
            background: #333;
        }

        .drag-handle,
        .collapse-button {
            background: #f0f0f0;
            border: 1px solid #ccc;
        }
    }

    /* 减少动画模式 */
    @media (prefers-reduced-motion: reduce) {
        .floating-toolbar,
        .toolbar-button,
        .collapse-button {
            transition: none;
        }

        .toolbar-button:hover {
            transform: none;
        }

        .tooltip {
            animation: none;
        }
    }
</style>