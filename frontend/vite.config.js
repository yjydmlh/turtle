import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],

  server: {
    port: 3000,
    host: true,
    // 性能优化
    hmr: {
      overlay: false // 减少错误覆盖层的性能影响
    },
    fs: {
      // 允许访问工作区根目录
      allow: ['..', '..']
    },
    proxy: {
      // 代理API请求到后端
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
        // 移除详细日志以提升性能
      }
    }
  },

  build: {
    target: 'es2020',
    rollupOptions: {
      output: {
        // 自动代码分割
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    }
  },

  optimizeDeps: {
    include: ['lightweight-charts', 'lucide-svelte', 'clsx', 'tailwind-merge'],
    // 强制预构建依赖以提升性能
    force: false
  },

  // 性能优化
  esbuild: {
    // 在开发模式下保持快速构建
    target: 'es2020'
  },

  define: {
    // 在构建时注入环境变量
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString())
  }
});