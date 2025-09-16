<script>
    import { createEventDispatcher } from 'svelte';
    import { X, Maximize2, Minimize2, Move } from 'lucide-svelte';

    export let isVisible = false;
    export let title = '';
    export let panelId = '';
    export let initialX = 100;
    export let initialY = 100;
    export let width = 400;
    export let height = 300;

    const dispatch = createEventDispatcher();

    let panelElement;
    let isDragging = false;
    let isResizing = false;
    let isMaximized = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let resizeStartX = 0;
    let resizeStartY = 0;
    let panelX = initialX;
    let panelY = initialY;
    let panelWidth = width;
    let panelHeight = height;
    let savedPosition = { x: initialX, y: initialY, width: width, height: height };

    // 优化的拖拽处理 - 使用 requestAnimationFrame 和节流
    let animationFrameId = null;
    let lastUpdateTime = 0;
    const THROTTLE_DELAY = 16; // 约60fps

    function startDrag(event) {
        if (event.target.closest('.panel-controls')) return;
        
        isDragging = true;
        dragStartX = event.clientX - panelX;
        dragStartY = event.clientY - panelY;
        
        // 只在浏览器环境中添加事件监听器
        if (typeof document !== 'undefined') {
            document.addEventListener('mousemove', handleDragThrottled, { passive: true });
            document.addEventListener('mouseup', stopDrag, { passive: true });
        }
        event.preventDefault();
    }

    // 节流的拖拽处理函数
    function handleDragThrottled(event) {
        if (!isDragging) return;
        
        const now = performance.now();
        if (now - lastUpdateTime < THROTTLE_DELAY) return;
        
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        
        animationFrameId = requestAnimationFrame(() => {
            handleDrag(event);
            lastUpdateTime = now;
        });
    }

    function handleDrag(event) {
        if (!isDragging || isMaximized) return;
        
        const newX = event.clientX - dragStartX;
        const newY = event.clientY - dragStartY;
        
        // 边界检查 - 优化计算
        const maxX = window.innerWidth - panelWidth;
        const maxY = window.innerHeight - panelHeight;
        
        panelX = Math.max(0, Math.min(newX, maxX));
        panelY = Math.max(0, Math.min(newY, maxY));
    }

    function stopDrag() {
        isDragging = false;
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
        
        // 只在浏览器环境中移除事件监听器
        if (typeof document !== 'undefined') {
            document.removeEventListener('mousemove', handleDragThrottled);
            document.removeEventListener('mouseup', stopDrag);
        }
    }

    // 优化的调整大小处理
    let resizeAnimationFrameId = null;
    let lastResizeTime = 0;

    function startResize(event) {
        isResizing = true;
        resizeStartX = event.clientX;
        resizeStartY = event.clientY;
        
        // 只在浏览器环境中添加事件监听器
        if (typeof document !== 'undefined') {
            document.addEventListener('mousemove', handleResizeThrottled, { passive: true });
            document.addEventListener('mouseup', stopResize, { passive: true });
        }
        event.preventDefault();
        event.stopPropagation();
    }

    function handleResizeThrottled(event) {
        if (!isResizing) return;
        
        const now = performance.now();
        if (now - lastResizeTime < THROTTLE_DELAY) return;
        
        if (resizeAnimationFrameId) {
            cancelAnimationFrame(resizeAnimationFrameId);
        }
        
        resizeAnimationFrameId = requestAnimationFrame(() => {
            handleResize(event);
            lastResizeTime = now;
        });
    }

    function handleResize(event) {
        if (!isResizing || isMaximized) return;
        
        const deltaX = event.clientX - resizeStartX;
        const deltaY = event.clientY - resizeStartY;
        
        const newWidth = Math.max(300, panelWidth + deltaX);
        const newHeight = Math.max(200, panelHeight + deltaY);
        
        // 确保不超出屏幕边界
        const maxWidth = window.innerWidth - panelX;
        const maxHeight = window.innerHeight - panelY;
        
        panelWidth = Math.min(newWidth, maxWidth);
        panelHeight = Math.min(newHeight, maxHeight);
        
        resizeStartX = event.clientX;
        resizeStartY = event.clientY;
    }

    function stopResize() {
        isResizing = false;
        if (resizeAnimationFrameId) {
            cancelAnimationFrame(resizeAnimationFrameId);
            resizeAnimationFrameId = null;
        }
        
        // 只在浏览器环境中移除事件监听器
        if (typeof document !== 'undefined') {
            document.removeEventListener('mousemove', handleResizeThrottled);
            document.removeEventListener('mouseup', stopResize);
        }
    }

    function toggleMaximize() {
        if (isMaximized) {
            // 还原
            panelX = savedPosition.x;
            panelY = savedPosition.y;
            panelWidth = savedPosition.width;
            panelHeight = savedPosition.height;
            isMaximized = false;
        } else {
            // 保存当前位置和大小
            savedPosition = { x: panelX, y: panelY, width: panelWidth, height: panelHeight };
            // 最大化
            panelX = 0;
            panelY = 0;
            panelWidth = window.innerWidth;
            panelHeight = window.innerHeight;
            isMaximized = true;
        }
    }

    function closePanel() {
        dispatch('close', { panelId });
    }

    // 响应式调整 - 使用防抖
    let resizeTimeout;
    function handleWindowResize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (isMaximized) {
                panelWidth = window.innerWidth;
                panelHeight = window.innerHeight;
            } else {
                // 确保面板不超出新的窗口边界
                const maxX = window.innerWidth - panelWidth;
                const maxY = window.innerHeight - panelHeight;
                
                panelX = Math.max(0, Math.min(panelX, maxX));
                panelY = Math.max(0, Math.min(panelY, maxY));
            }
        }, 100);
    }

    // 生命周期管理
    $: if (typeof window !== 'undefined') {
        window.addEventListener('resize', handleWindowResize);
    }

    // 清理函数
    function cleanup() {
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        if (resizeAnimationFrameId) {
            cancelAnimationFrame(resizeAnimationFrameId);
        }
        clearTimeout(resizeTimeout);
        
        // 只在浏览器环境中执行document操作
        if (typeof document !== 'undefined') {
            document.removeEventListener('mousemove', handleDragThrottled);
            document.removeEventListener('mouseup', stopDrag);
            document.removeEventListener('mousemove', handleResizeThrottled);
            document.removeEventListener('mouseup', stopResize);
        }
    }

    // 组件销毁时清理
    import { onDestroy } from 'svelte';
    onDestroy(cleanup);
</script>

{#if isVisible}
    <!-- 遮罩层 -->
    <div class="panel-overlay" on:click={closePanel}></div>
    
    <!-- 可拖拽面板 -->
    <div
        bind:this={panelElement}
        class="draggable-panel {isMaximized ? 'maximized' : ''} {isDragging ? 'dragging' : ''} {isResizing ? 'resizing' : ''}"
        style="left: {panelX}px; top: {panelY}px; width: {panelWidth}px; height: {panelHeight}px;"
    >
        <!-- 面板头部 -->
        <div class="panel-header" on:mousedown={startDrag}>
            <div class="panel-title">
                <Move class="w-4 h-4 text-gray-500 mr-2" />
                {title}
            </div>
            <div class="panel-controls">
                <button class="control-button" on:click={toggleMaximize} title={isMaximized ? '还原' : '最大化'}>
                    {#if isMaximized}
                        <Minimize2 class="w-4 h-4" />
                    {:else}
                        <Maximize2 class="w-4 h-4" />
                    {/if}
                </button>
                <button class="control-button close-button" on:click={closePanel} title="关闭">
                    <X class="w-4 h-4" />
                </button>
            </div>
        </div>
        
        <!-- 面板内容 -->
        <div class="panel-content">
            <slot />
        </div>
        
        <!-- 调整大小手柄 -->
        {#if !isMaximized}
            <div class="resize-handle" on:mousedown={startResize}></div>
        {/if}
    </div>
{/if}

<style>
    .panel-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(2px);
        z-index: 999;
        animation: overlayFadeIn 0.2s ease;
    }

    .draggable-panel {
        position: fixed;
        z-index: 1000;
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        animation: panelSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        /* 启用硬件加速 */
        transform: translateZ(0);
        will-change: transform, width, height;
        /* 优化渲染性能 */
        contain: layout style paint;
    }

    .draggable-panel.maximized {
        border-radius: 0;
        animation: panelMaximize 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .draggable-panel.dragging {
        cursor: grabbing;
        user-select: none;
        /* 拖拽时减少阴影计算 */
        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.25);
    }

    .draggable-panel.resizing {
        user-select: none;
        /* 调整大小时优化性能 */
        pointer-events: auto;
    }

    .panel-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: grab;
        user-select: none;
        min-height: 48px;
        /* 优化拖拽性能 */
        transform: translateZ(0);
    }

    .panel-header:active {
        cursor: grabbing;
    }

    .panel-title {
        font-weight: 600;
        font-size: 14px;
        display: flex;
        align-items: center;
        flex: 1;
    }

    .panel-controls {
        display: flex;
        gap: 8px;
        pointer-events: auto;
    }

    .control-button {
        width: 32px;
        height: 32px;
        border: none;
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background 0.2s ease;
        /* 优化按钮性能 */
        transform: translateZ(0);
    }

    .control-button:hover {
        background: rgba(255, 255, 255, 0.3);
    }

    .close-button:hover {
        background: rgba(239, 68, 68, 0.8);
    }

    .panel-content {
        flex: 1;
        padding: 20px;
        overflow: auto;
        /* 优化滚动性能 */
        -webkit-overflow-scrolling: touch;
        transform: translateZ(0);
    }

    .resize-handle {
        position: absolute;
        bottom: 0;
        right: 0;
        width: 20px;
        height: 20px;
        cursor: nw-resize;
        background: linear-gradient(-45deg, transparent 0%, transparent 40%, #ccc 40%, #ccc 60%, transparent 60%);
        /* 优化手柄性能 */
        transform: translateZ(0);
    }

    .resize-handle:hover {
        background: linear-gradient(-45deg, transparent 0%, transparent 40%, #999 40%, #999 60%, transparent 60%);
    }

    /* 动画优化 */
    @keyframes overlayFadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    @keyframes panelSlideIn {
        from {
            opacity: 0;
            transform: translateY(-20px) scale(0.95) translateZ(0);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1) translateZ(0);
        }
    }

    @keyframes panelMaximize {
        from {
            border-radius: 12px;
        }
        to {
            border-radius: 0;
        }
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .draggable-panel {
            min-width: 280px;
            max-width: calc(100vw - 20px);
            max-height: calc(100vh - 20px);
        }

        .panel-header {
            padding: 10px 12px;
            min-height: 44px;
        }

        .panel-title {
            font-size: 13px;
        }

        .control-button {
            width: 28px;
            height: 28px;
        }

        .panel-content {
            padding: 16px;
        }

        .resize-handle {
            width: 24px;
            height: 24px;
        }
    }

    /* 高对比度模式 */
    @media (prefers-contrast: high) {
        .draggable-panel {
            border: 2px solid #000;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }

        .panel-header {
            background: #000;
            border-bottom: 1px solid #333;
        }

        .control-button {
            background: rgba(255, 255, 255, 0.9);
            color: #000;
            border: 1px solid #333;
        }
    }

    /* 减少动画模式 */
    @media (prefers-reduced-motion: reduce) {
        .draggable-panel,
        .panel-overlay,
        .control-button {
            animation: none;
            transition: none;
        }

        .draggable-panel {
            transform: none;
        }
    }

    /* 性能优化：GPU加速 */
    .draggable-panel,
    .panel-header,
    .control-button,
    .panel-content,
    .resize-handle {
        backface-visibility: hidden;
        perspective: 1000px;
    }
</style>