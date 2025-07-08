/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        // 缠论分析专用颜色
        'chan': {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a'
        },

        // 金融专用颜色
        'bull': {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d'
        },

        'bear': {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d'
        },

        // 中性色
        'neutral-warm': {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917'
        }
      },

      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', 'monospace'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'display': ['Inter', 'system-ui', 'sans-serif']
      },

      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },

      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem'
      },

      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem'
      },

      boxShadow: {
        'inner-lg': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
        'colored': '0 10px 15px -3px rgba(59, 130, 246, 0.1), 0 4px 6px -2px rgba(59, 130, 246, 0.05)'
      },

      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'bounce-slow': 'bounce 2s infinite',
        'spin-slow': 'spin 2s linear infinite',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
        'fadeIn': 'fadeIn 0.5s ease-in-out',
        'slideUp': 'slideUp 0.3s ease-out',
        'slideDown': 'slideDown 0.3s ease-out'
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      },

      // 图表相关的尺寸
      height: {
        'chart': '600px',
        'chart-sm': '400px',
        'chart-lg': '800px'
      },

      // 响应式断点扩展
      screens: {
        'xs': '475px',
        '3xl': '1600px'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),

    // 自定义插件 - 缠论专用工具类
    function({ addUtilities }) {
      const newUtilities = {
        // 分型标记样式
        '.fenxing-top': {
          '@apply text-bear-600 bg-bear-50 border-bear-200': {}
        },
        '.fenxing-bottom': {
          '@apply text-bull-600 bg-bull-50 border-bull-200': {}
        },

        // 趋势指示器
        '.trend-up': {
          '@apply text-bull-600 bg-bull-50': {}
        },
        '.trend-down': {
          '@apply text-bear-600 bg-bear-50': {}
        },
        '.trend-neutral': {
          '@apply text-neutral-600 bg-neutral-50': {}
        },

        // 价格变化样式
        '.price-up': {
          '@apply text-bull-600 font-semibold': {}
        },
        '.price-down': {
          '@apply text-bear-600 font-semibold': {}
        },
        '.price-neutral': {
          '@apply text-neutral-600': {}
        },

        // 卡片样式
        '.card': {
          '@apply bg-white rounded-xl shadow-sm border border-gray-200': {}
        },
        '.card-hover': {
          '@apply hover:shadow-md hover:border-gray-300 transition-all duration-200': {}
        },

        // 渐变文字
        '.gradient-text': {
          '@apply bg-gradient-to-r from-chan-600 to-blue-600 bg-clip-text text-transparent': {}
        },

        // 玻璃形态效果
        '.glass': {
          '@apply bg-white/80 backdrop-blur-sm border border-white/20': {}
        },

        // 数据表格样式
        '.data-table': {
          '@apply min-w-full divide-y divide-gray-200': {}
        },
        '.data-table th': {
          '@apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider': {}
        },
        '.data-table td': {
          '@apply px-6 py-4 whitespace-nowrap text-sm text-gray-900': {}
        }
      }

      addUtilities(newUtilities)
    }
  ]
};