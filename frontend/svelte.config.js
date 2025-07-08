import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/kit/vite';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://kit.svelte.dev/docs/integrations#preprocessors
  // for more information about preprocessors
  preprocess: vitePreprocess(),

  kit: {
    // adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
    // If your environment is not supported or you settled on a specific environment, switch out the adapter.
    // See https://kit.svelte.dev/docs/adapters for more information about adapters.
    adapter: adapter(),

    // 别名配置，方便导入
    alias: {
      '$components': 'src/lib/components',
      '$stores': 'src/lib/stores.js',
      '$utils': 'src/lib/utils.js',
      '$api': 'src/lib/api.js'
    },

    // 预渲染设置
    prerender: {
      handleHttpError: 'warn'
    },

    // CSP设置（生产环境安全）
    csp: {
      mode: 'auto',
      directives: {
        'script-src': ['self']
      }
    }
  }
};

export default config;