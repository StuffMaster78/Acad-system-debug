import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'
import crypto from 'crypto'
import { createHash } from 'crypto'

// Polyfill for crypto.hash (used by @vitejs/plugin-vue)
// Node.js crypto module doesn't have crypto.hash, so we polyfill it
if (typeof crypto.hash === 'undefined') {
  crypto.hash = async (algorithm, data) => {
    // Convert Web Crypto algorithm names to Node.js hash algorithm names
    const algoMap = {
      'sha-256': 'sha256',
      'sha-1': 'sha1',
      'md5': 'md5'
    }
    const nodeAlgo = algoMap[algorithm?.toLowerCase()] || algorithm?.replace(/-/g, '').toLowerCase() || 'sha256'
    const hash = createHash(nodeAlgo)
    // Handle both Buffer and Uint8Array
    if (data instanceof Uint8Array) {
      hash.update(Buffer.from(data))
    } else if (Buffer.isBuffer(data)) {
      hash.update(data)
    } else {
      hash.update(Buffer.from(data))
    }
    return hash.digest()
  }
}

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [vue()],
  test: {
    // Test environment
    environment: 'jsdom',
    globals: true,
    
    // Test file patterns
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
    
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.config.{js,ts}',
        '**/coverage/**',
        '**/*.d.ts',
        '**/__tests__/**',
        '**/__mocks__/**',
        '**/router/index.js',
        '**/main.js',
        '**/App.vue'
      ],
      thresholds: {
        lines: 0,
        functions: 0,
        branches: 0,
        statements: 0
      },
      reportsDirectory: './coverage'
    },
    
    // Setup files
    setupFiles: ['./tests/setup.js'],
    
    // Test timeout
    testTimeout: 10000,
    
    // Reporter configuration
    reporters: ['verbose', 'junit'],
    outputFile: {
      junit: './coverage/junit.xml'
    },
    
    // Global test configuration
    globalSetup: undefined,
    
    // Mock configuration
    mockReset: true,
    restoreMocks: true,
    
    // Threads configuration
    threads: true,
    maxThreads: 4,
    minThreads: 1
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})

