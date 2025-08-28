import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// =============================================================================
// CSS类名工具函数
// =============================================================================

/**
 * 合并CSS类名，支持条件类名和Tailwind冲突解决
 * @param {...any} inputs 类名输入
 * @returns {string} 合并后的类名
 */
export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

// =============================================================================
// 数字格式化工具
// =============================================================================

/**
 * 格式化价格显示
 * @param {number} price 价格
 * @param {number} decimals 小数位数
 * @param {string} currency 货币符号
 * @returns {string} 格式化后的价格
 */
export function formatPrice(price, decimals = 2, currency = '$') {
    if (typeof price !== 'number' || isNaN(price)) {
        return `${currency}0.${'0'.repeat(decimals)}`;
    }

    return `${currency}${price.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    })}`;
}

/**
 * 格式化百分比显示
 * @param {number} value 数值
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的百分比
 */
export function formatPercentage(value, decimals = 2) {
    if (typeof value !== 'number' || isNaN(value)) {
        return '0.00%';
    }

    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * 格式化成交量显示
 * @param {number} volume 成交量
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的成交量
 */
export function formatVolume(volume, decimals = 2) {
    if (typeof volume !== 'number' || isNaN(volume)) {
        return '0';
    }

    const units = [
        { value: 1e12, suffix: 'T' },
        { value: 1e9, suffix: 'B' },
        { value: 1e6, suffix: 'M' },
        { value: 1e3, suffix: 'K' }
    ];

    for (const unit of units) {
        if (volume >= unit.value) {
            return `${(volume / unit.value).toFixed(decimals)}${unit.suffix}`;
        }
    }

    return volume.toFixed(decimals);
}

/**
 * 格式化数字为紧凑格式
 * @param {number} num 数字
 * @returns {string} 紧凑格式的数字
 */
export function formatCompactNumber(num) {
    if (typeof num !== 'number' || isNaN(num)) {
        return '0';
    }

    return new Intl.NumberFormat('en', {
        notation: 'compact',
        maximumFractionDigits: 2
    }).format(num);
}

// =============================================================================
// 时间和日期工具
// =============================================================================

/**
 * 格式化时间戳为可读时间
 * @param {number|string} timestamp 时间戳（毫秒）
 * @param {string} locale 地区代码
 * @returns {string} 格式化后的时间
 */
export function formatTime(timestamp, locale = 'zh-CN') {
    if (!timestamp) return '';

    const date = new Date(typeof timestamp === 'string' ? parseInt(timestamp) : timestamp);

    if (isNaN(date.getTime())) {
        return '';
    }

    return date.toLocaleString(locale, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * 格式化时间为简短格式
 * @param {number|string} timestamp 时间戳
 * @returns {string} 简短时间格式
 */
export function formatShortTime(timestamp) {
    if (!timestamp) return '';

    const date = new Date(typeof timestamp === 'string' ? parseInt(timestamp) : timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    // 小于1分钟
    if (diff < 60000) {
        return '刚刚';
    }

    // 小于1小时
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes}分钟前`;
    }

    // 小于1天
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours}小时前`;
    }

    // 小于1周
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days}天前`;
    }

    // 显示具体日期
    return date.toLocaleDateString('zh-CN');
}

/**
 * 获取时间范围文本
 * @param {string} timeframe 时间周期
 * @returns {string} 时间范围描述
 */
export function getTimeframeText(timeframe) {
    const timeframes = {
        '1m': '1分钟',
        '5m': '5分钟',
        '15m': '15分钟',
        '30m': '30分钟',
        '1h': '1小时',
        '4h': '4小时',
        '1d': '1天',
        '1w': '1周',
        '1M': '1月'
    };

    return timeframes[timeframe] || timeframe;
}

// =============================================================================
// 颜色和主题工具
// =============================================================================

/**
 * 根据价格变化获取颜色类名
 * @param {number} change 价格变化
 * @returns {string} 颜色类名
 */
export function getPriceChangeColor(change) {
    if (change > 0) return 'text-bull-600';
    if (change < 0) return 'text-bear-600';
    return 'text-gray-600';
}

/**
 * 根据百分比获取背景颜色类名
 * @param {number} percentage 百分比
 * @returns {string} 背景颜色类名
 */
export function getPercentageBackgroundColor(percentage) {
    if (percentage > 0) return 'bg-bull-50 text-bull-800';
    if (percentage < 0) return 'bg-bear-50 text-bear-800';
    return 'bg-gray-50 text-gray-800';
}

/**
 * 根据趋势方向获取图标
 * @param {string} direction 趋势方向
 * @returns {string} 趋势图标
 */
export function getTrendIcon(direction) {
    const icons = {
        'up': '📈',
        'down': '📉',
        'neutral': '➡️',
        'strong_up': '🚀',
        'strong_down': '📉'
    };

    return icons[direction] || '➡️';
}

// =============================================================================
// 数据验证工具
// =============================================================================

/**
 * 验证是否为有效数字
 * @param {any} value 要验证的值
 * @returns {boolean} 是否为有效数字
 */
export function isValidNumber(value) {
    return typeof value === 'number' && !isNaN(value) && isFinite(value);
}

/**
 * 验证K线数据格式
 * @param {Array} klineData K线数据
 * @returns {boolean} 是否为有效格式
 */
export function validateKlineData(klineData) {
    if (!Array.isArray(klineData)) {
        return false;
    }

    return klineData.every(kline => {
        return Array.isArray(kline) &&
               kline.length >= 5 &&
               isValidNumber(kline[0]) && // timestamp
               isValidNumber(kline[1]) && // open
               isValidNumber(kline[2]) && // high
               isValidNumber(kline[3]) && // low
               isValidNumber(kline[4]);   // close
    });
}

/**
 * 验证分型数据格式
 * @param {Array} fenxingData 分型数据
 * @returns {boolean} 是否为有效格式
 */
export function validateFenxingData(fenxingData) {
    if (!Array.isArray(fenxingData)) {
        return false;
    }

    return fenxingData.every(fenxing => {
        return typeof fenxing === 'object' &&
               fenxing.hasOwnProperty('type') &&
               fenxing.hasOwnProperty('timestamp') &&
               fenxing.hasOwnProperty('price') &&
               ['top', 'bottom'].includes(fenxing.type);
    });
}

// =============================================================================
// 数组和对象工具
// =============================================================================

/**
 * 深度克隆对象
 * @param {any} obj 要克隆的对象
 * @returns {any} 克隆后的对象
 */
export function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }

    if (obj instanceof Date) {
        return new Date(obj.getTime());
    }

    if (obj instanceof Array) {
        return obj.map(item => deepClone(item));
    }

    if (typeof obj === 'object') {
        const cloned = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                cloned[key] = deepClone(obj[key]);
            }
        }
        return cloned;
    }

    return obj;
}

/**
 * 防抖函数
 * @param {Function} func 要防抖的函数
 * @param {number} wait 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * @param {Function} func 要节流的函数
 * @param {number} limit 限制时间（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 根据键路径获取对象值
 * @param {Object} obj 源对象
 * @param {string} path 键路径（如 'a.b.c'）
 * @param {any} defaultValue 默认值
 * @returns {any} 获取到的值
 */
export function getNestedValue(obj, path, defaultValue = undefined) {
    if (!obj || typeof obj !== 'object') {
        return defaultValue;
    }

    const keys = path.split('.');
    let current = obj;

    for (const key of keys) {
        if (current === null || current === undefined || !current.hasOwnProperty(key)) {
            return defaultValue;
        }
        current = current[key];
    }

    return current;
}

// =============================================================================
// 浏览器和设备工具
// =============================================================================

/**
 * 检测是否为移动设备
 * @returns {boolean} 是否为移动设备
 */
export function isMobile() {
    if (typeof window === 'undefined') {
        return false;
    }

    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
    );
}

/**
 * 检测是否支持触摸
 * @returns {boolean} 是否支持触摸
 */
export function isTouchDevice() {
    if (typeof window === 'undefined') {
        return false;
    }

    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

/**
 * 获取视口尺寸
 * @returns {Object} 视口宽度和高度
 */
export function getViewportSize() {
    if (typeof window === 'undefined') {
        return { width: 0, height: 0 };
    }

    return {
        width: window.innerWidth || document.documentElement.clientWidth,
        height: window.innerHeight || document.documentElement.clientHeight
    };
}

/**
 * 复制文本到剪贴板
 * @param {string} text 要复制的文本
 * @returns {Promise<boolean>} 是否复制成功
 */
export async function copyToClipboard(text) {
    if (typeof navigator === 'undefined') {
        return false;
    }

    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
            return true;
        }

        // 兼容旧版浏览器
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);

        return successful;
    } catch (error) {
        console.error('复制到剪贴板失败:', error);
        return false;
    }
}

// =============================================================================
// 本地存储工具
// =============================================================================

/**
 * 安全地设置localStorage
 * @param {string} key 键名
 * @param {any} value 值
 * @returns {boolean} 是否设置成功
 */
export function setLocalStorage(key, value) {
    if (typeof localStorage === 'undefined') {
        return false;
    }

    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.error('设置localStorage失败:', error);
        return false;
    }
}

/**
 * 安全地获取localStorage
 * @param {string} key 键名
 * @param {any} defaultValue 默认值
 * @returns {any} 获取到的值
 */
export function getLocalStorage(key, defaultValue = null) {
    if (typeof localStorage === 'undefined') {
        return defaultValue;
    }

    try {
        const item = localStorage.getItem(key);
        return item !== null ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('获取localStorage失败:', error);
        return defaultValue;
    }
}

/**
 * 安全地移除localStorage项
 * @param {string} key 键名
 * @returns {boolean} 是否移除成功
 */
export function removeLocalStorage(key) {
    if (typeof localStorage === 'undefined') {
        return false;
    }

    try {
        localStorage.removeItem(key);
        return true;
    } catch (error) {
        console.error('移除localStorage失败:', error);
        return false;
    }
}

// =============================================================================
// 数学和统计工具
// =============================================================================

/**
 * 计算数组的平均值
 * @param {Array<number>} numbers 数字数组
 * @returns {number} 平均值
 */
export function average(numbers) {
    if (!Array.isArray(numbers) || numbers.length === 0) {
        return 0;
    }

    const validNumbers = numbers.filter(isValidNumber);
    if (validNumbers.length === 0) {
        return 0;
    }

    return validNumbers.reduce((sum, num) => sum + num, 0) / validNumbers.length;
}

/**
 * 计算数组的标准差
 * @param {Array<number>} numbers 数字数组
 * @returns {number} 标准差
 */
export function standardDeviation(numbers) {
    if (!Array.isArray(numbers) || numbers.length <= 1) {
        return 0;
    }

    const validNumbers = numbers.filter(isValidNumber);
    if (validNumbers.length <= 1) {
        return 0;
    }

    const avg = average(validNumbers);
    const squaredDiffs = validNumbers.map(num => Math.pow(num - avg, 2));
    const avgSquaredDiff = average(squaredDiffs);

    return Math.sqrt(avgSquaredDiff);
}

/**
 * 计算最大回撤
 * @param {Array<number>} values 价值数组
 * @returns {Object} 最大回撤信息
 */
export function calculateMaxDrawdown(values) {
    if (!Array.isArray(values) || values.length === 0) {
        return { maxDrawdown: 0, peak: 0, trough: 0 };
    }

    let maxDrawdown = 0;
    let peak = values[0];
    let trough = values[0];
    let currentPeak = values[0];

    for (let i = 1; i < values.length; i++) {
        if (values[i] > currentPeak) {
            currentPeak = values[i];
        }

        const drawdown = (currentPeak - values[i]) / currentPeak;

        if (drawdown > maxDrawdown) {
            maxDrawdown = drawdown;
            peak = currentPeak;
            trough = values[i];
        }
    }

    return {
        maxDrawdown: maxDrawdown * 100, // 转换为百分比
        peak,
        trough
    };
}

// =============================================================================
// 缠论专用工具函数
// =============================================================================

/**
 * 获取分型类型的显示文本
 * @param {string} type 分型类型
 * @returns {string} 显示文本
 */
export function getFenxingTypeText(type) {
    const types = {
        'top': '顶分型',
        'bottom': '底分型',
        'unknown': '未知'
    };

    return types[type] || type;
}

/**
 * 获取分型类型的图标
 * @param {string} type 分型类型
 * @returns {string} 图标
 */
export function getFenxingIcon(type) {
    const icons = {
        'top': '🔺',
        'bottom': '🔻'
    };

    return icons[type] || '⚪';
}

/**
 * 计算笔的角度
 * @param {Object} startPoint 起点
 * @param {Object} endPoint 终点
 * @returns {number} 角度（度）
 */
export function calculateBiAngle(startPoint, endPoint) {
    if (!startPoint || !endPoint) {
        return 0;
    }

    const deltaY = endPoint.price - startPoint.price;
    const deltaX = endPoint.timestamp - startPoint.timestamp;

    if (deltaX === 0) {
        return 90;
    }

    const radians = Math.atan(deltaY / deltaX);
    const degrees = radians * (180 / Math.PI);

    return Math.abs(degrees);
}

/**
 * 判断趋势强度等级
 * @param {number} strength 趋势强度（0-1）
 * @returns {string} 强度等级
 */
export function getTrendStrengthLevel(strength) {
    if (strength >= 0.8) return '极强';
    if (strength >= 0.6) return '强';
    if (strength >= 0.4) return '中等';
    if (strength >= 0.2) return '弱';
    return '极弱';
}

// =============================================================================
// 导出所有工具函数
// =============================================================================

export default {
    // CSS工具
    cn,

    // 数字格式化
    formatPrice,
    formatPercentage,
    formatVolume,
    formatCompactNumber,

    // 时间工具
    formatTime,
    formatShortTime,
    getTimeframeText,

    // 颜色和主题
    getPriceChangeColor,
    getPercentageBackgroundColor,
    getTrendIcon,

    // 验证工具
    isValidNumber,
    validateKlineData,
    validateFenxingData,

    // 数组和对象
    deepClone,
    debounce,
    throttle,
    getNestedValue,

    // 浏览器工具
    isMobile,
    isTouchDevice,
    getViewportSize,
    copyToClipboard,

    // 本地存储
    setLocalStorage,
    getLocalStorage,
    removeLocalStorage,

    // 数学统计
    average,
    standardDeviation,
    calculateMaxDrawdown,

    // 缠论工具
    getFenxingTypeText,
    getFenxingIcon,
    calculateBiAngle,
    getTrendStrengthLevel
};