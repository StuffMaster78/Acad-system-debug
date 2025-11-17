import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 30000, // 30 seconds timeout
        proxyTimeout: 30000,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
        // Handle connection resets gracefully
        ws: true, // Enable websocket proxying
      }
    }
  },
  build: {
    outDir: (() => {
      // Determine output directory based on mode
      const mode = process.env.MODE || 'default'
      if (mode === 'writers') return 'dist/writers'
      if (mode === 'clients') return 'dist/clients'
      if (mode === 'staff') return 'dist/staff'
      return 'dist'
    })(),
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        // Ensure consistent naming for cache busting
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]'
      }
    }
  }
})

