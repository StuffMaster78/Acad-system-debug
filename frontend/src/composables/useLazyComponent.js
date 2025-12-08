/**
 * Composable for lazy loading Vue components.
 * Useful for code splitting and reducing initial bundle size.
 */

import { defineAsyncComponent, shallowRef } from 'vue'

/**
 * Creates a lazy-loaded component with loading and error states.
 * 
 * @param {Function} loader - Function that returns a Promise resolving to a component
 * @param {Object} options - Configuration options
 * @param {Object} options.loadingComponent - Component to show while loading
 * @param {Object} options.errorComponent - Component to show on error
 * @param {Number} options.delay - Delay before showing loading component (ms)
 * @param {Number} options.timeout - Timeout for loading (ms)
 * @param {Function} options.onError - Error handler function
 * @returns {Object} Async component
 */
export function useLazyComponent(loader, options = {}) {
  const {
    loadingComponent = null,
    errorComponent = null,
    delay = 200,
    timeout = 10000,
    onError = null
  } = options

  return defineAsyncComponent({
    loader,
    loadingComponent,
    errorComponent,
    delay,
    timeout,
    onError: onError || ((error) => {
      console.error('Failed to load component:', error)
    })
  })
}

/**
 * Creates a lazy-loaded component with a simple loading spinner.
 * 
 * @param {Function} loader - Function that returns a Promise resolving to a component
 * @returns {Object} Async component with spinner
 */
export function useLazyComponentWithSpinner(loader) {
  const LoadingSpinner = {
    template: `
      <div class="flex items-center justify-center p-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    `
  }

  return useLazyComponent(loader, {
    loadingComponent: LoadingSpinner
  })
}

/**
 * Creates a lazy-loaded component with error handling.
 * 
 * @param {Function} loader - Function that returns a Promise resolving to a component
 * @param {Function} retry - Optional retry function
 * @returns {Object} Async component with error handling
 */
export function useLazyComponentWithError(loader, retry = null) {
  const ErrorComponent = {
    props: ['error'],
    template: `
      <div class="flex flex-col items-center justify-center p-8 text-center">
        <div class="text-red-600 mb-4">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Failed to load component
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ error?.message || 'An error occurred while loading this component.' }}
        </p>
        <button
          v-if="retry"
          @click="retry"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      </div>
    `,
    setup(props) {
      return { retry }
    }
  }

  return useLazyComponent(loader, {
    errorComponent: ErrorComponent
  })
}

/**
 * Preloads a component for faster subsequent loads.
 * 
 * @param {Function} loader - Function that returns a Promise resolving to a component
 * @returns {Promise} Promise that resolves when component is loaded
 */
export function preloadComponent(loader) {
  return loader()
}

/**
 * Creates a lazy-loaded route component.
 * Useful for route-based code splitting.
 * 
 * @param {Function} importFn - Function that returns import() promise
 * @returns {Object} Async component
 */
export function useLazyRoute(importFn) {
  return useLazyComponentWithSpinner(importFn)
}

/**
 * Batch preloads multiple components.
 * 
 * @param {Array<Function>} loaders - Array of loader functions
 * @returns {Promise} Promise that resolves when all components are loaded
 */
export function preloadComponents(loaders) {
  return Promise.all(loaders.map(loader => loader()))
}

