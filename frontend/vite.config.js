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
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 30000, // 30 seconds timeout
        proxyTimeout: 30000,
        // Handle connection errors gracefully
        configure: (proxy, _options) => {
          proxy.on('error', (err, req, res) => {
            // Suppress ECONNRESET errors from excessive session management requests
            if (err.code === 'ECONNRESET' && req.url?.includes('session-management')) {
              // Silently ignore - these are from the external sessionManager.js
              return;
            }
            // Only log non-ECONNRESET errors
            if (err.code !== 'ECONNRESET') {
              console.error('Proxy error:', err.code, req.url);
            }
          });
          // Suppress verbose logging for session management endpoints
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            if (!req.url?.includes('session-management')) {
            console.log('Sending Request to the Target:', req.method, req.url);
            }
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            if (!req.url?.includes('session-management')) {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
            }
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
    sourcemap: process.env.NODE_ENV === 'development',
    minify: process.env.NODE_ENV === 'production' ? 'esbuild' : false,
    // Production optimizations
    ...(process.env.NODE_ENV === 'production' && {
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.trace']
        }
      }
    }),
    rollupOptions: {
      output: {
        // Ensure consistent naming for cache busting
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `assets/images/[name].[hash].[ext]`
          }
          if (/woff2?|eot|ttf|otf/i.test(ext)) {
            return `assets/fonts/[name].[hash].[ext]`
          }
          return `assets/[name].[hash].[ext]`
        },
        // Manual chunk splitting for better code splitting
        manualChunks: (id) => {
          // Split vendor chunks more granularly
          if (id.includes('node_modules')) {
            // Core Vue ecosystem
            if (id.includes('vue') && !id.includes('vue-router') && !id.includes('pinia')) {
              return 'vendor-vue-core'
            }
            if (id.includes('vue-router')) {
              return 'vendor-vue-router'
            }
            if (id.includes('pinia')) {
              return 'vendor-pinia'
            }
            // HTTP client
            if (id.includes('axios')) {
              return 'vendor-http'
            }
            // Rich text editor
            if (id.includes('quill')) {
              return 'vendor-quill'
            }
            // Charts
            if (id.includes('apexcharts')) {
              return 'vendor-charts'
            }
            // Form validation
            if (id.includes('vee-validate') || id.includes('yup')) {
              return 'vendor-forms'
            }
            // UI libraries
            if (id.includes('@headlessui') || id.includes('@heroicons')) {
              return 'vendor-ui'
            }
            // Other vendor code
            return 'vendor-other'
          }
          // Split by feature/route groups
          if (id.includes('/views/admin/')) {
            return 'chunk-admin'
          }
          if (id.includes('/views/writers/')) {
            return 'chunk-writers'
          }
          if (id.includes('/views/clients/') || id.includes('/views/orders/')) {
            return 'chunk-client'
          }
          if (id.includes('/views/editor/')) {
            return 'chunk-editor'
          }
          if (id.includes('/views/support/')) {
            return 'chunk-support'
          }
          if (id.includes('/views/public/')) {
            return 'chunk-public'
          }
          // Large components
          if (id.includes('/components/editor/') || id.includes('/components/blog/')) {
            return 'chunk-editor-components'
          }
          if (id.includes('/components/media/')) {
            return 'chunk-media-components'
          }
        }
      },
      // Enhanced tree shaking
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false
      }
    },
    // Chunk size warnings threshold (increased for better splitting)
    chunkSizeWarningLimit: 500,
    // Target modern browsers for smaller bundles
    target: 'es2015',
    // CSS code splitting
    cssCodeSplit: true,
    // Report compressed size
    reportCompressedSize: true,
    // Reduce chunk size warnings
    commonjsOptions: {
      include: [/node_modules/],
      transformMixedEsModules: true
    }
  }
})

