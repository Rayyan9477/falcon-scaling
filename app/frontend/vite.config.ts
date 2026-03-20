import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// API_PROXY_TARGET is set by the root main.py launcher.
// It is NOT prefixed with VITE_ so it stays server-side only (never leaks to browser).
// In dev, the frontend always uses relative /api paths which Vite proxies to the backend.
const proxyTarget = process.env.API_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
  },
})
