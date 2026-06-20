import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        // SSE 流式报告生成可能需要几分钟（大 prompt + 8K tokens 输出）
        // 不设超时，避免代理在 LLM 首 token 延迟期间断开连接
        timeout: 0,
        proxyTimeout: 0,
      },
    },
  },
})
