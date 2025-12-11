import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'

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

