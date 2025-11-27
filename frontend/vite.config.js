import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // 流式响应配置
        configure: (proxy, options) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            // 禁用响应缓冲以支持流式传输
            if (req.url.includes('/api/chat')) {
              proxyRes.headers['x-accel-buffering'] = 'no'
            }
          })
        }
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  }
})
