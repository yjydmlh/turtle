import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],

  server: {
    port: 3000,
    host: true,
    // 性能优化
    hmr: {
      overlay: false, // 减少错误覆盖层的性能影响
      port: 3001 // 使用独立端口提升HMR性能
    },
    fs: {
      // 允许访问工作区根目录
      allow: ['..', '..']
    },
    // 开启缓存以提升重新加载速度
    force: true,
    // 预热常用文件
    warmup: {
      clientFiles: ['./src/lib/components/*.svelte', './src/routes/*.svelte']
    },
    proxy: {
      // 代理API请求到后端
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // 启用代理缓存
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 添加缓存头
            if (req.method === 'GET') {
              proxyReq.setHeader('Cache-Control', 'public, max-age=300');
            }
          });
        }
      }
    }
  },

  build: {
    target: 'es2020',
    // 启用源码映射以便调试
    sourcemap: false,
    // 压缩选项
    minify: 'esbuild',
    // 代码分割阈值
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        // 优化代码分割策略
        manualChunks(id) {
          // 将大型依赖单独打包
          if (id.includes('klinecharts')) {
            return 'charts';
          }
          if (id.includes('lucide-svelte')) {
            return 'icons';
          }
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        },
        // 文件命名策略
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },

  optimizeDeps: {
    include: ['klinecharts', '@klinecharts/pro', 'lucide-svelte', 'clsx', 'tailwind-merge'],
    // 强制预构建依赖以提升性能
    force: true,
    // 预构建排除项
    exclude: []
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