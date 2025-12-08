/**
 * Vue directive for lazy loading images.
 * Usage: <img v-lazy-image="imageUrl" />
 * 
 * This directive provides a simpler alternative to the LazyImage component
 * for cases where you just need basic lazy loading.
 */

import { onMounted, onUnmounted } from 'vue'

let observer = null

function createObserver(options = {}) {
  if (typeof IntersectionObserver === 'undefined') {
    return null
  }

  return new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target
        const src = img.dataset.src
        const srcset = img.dataset.srcset
        
        if (src) {
          img.src = src
          img.removeAttribute('data-src')
        }
        
        if (srcset) {
          img.srcset = srcset
          img.removeAttribute('data-srcset')
        }
        
        img.classList.add('lazy-loaded')
        img.classList.remove('lazy-loading')
        
        observer.unobserve(img)
      }
    })
  }, {
    rootMargin: options.rootMargin || '50px',
    threshold: options.threshold || 0.01
  })
}

function initObserver() {
  if (!observer) {
    observer = createObserver()
  }
  return observer
}

export default {
  mounted(el, binding) {
    const src = binding.value
    if (!src) return

    // Store original src in data attribute
    el.dataset.src = src
    el.src = '' // Clear src to prevent immediate loading
    
    // Handle srcset if provided
    if (binding.arg === 'srcset') {
      el.dataset.srcset = binding.value
      el.removeAttribute('srcset')
    }

    // Add loading class
    el.classList.add('lazy-loading')
    
    // Set placeholder if provided
    if (binding.modifiers.placeholder) {
      el.style.backgroundColor = '#f3f4f6'
    }

    // If eager loading is requested, load immediately
    if (binding.modifiers.eager) {
      el.src = src
      el.classList.remove('lazy-loading')
      el.classList.add('lazy-loaded')
      return
    }

    // Observe element
    const obs = initObserver()
    if (obs) {
      obs.observe(el)
    } else {
      // Fallback: load immediately if IntersectionObserver not supported
      el.src = src
      el.classList.remove('lazy-loading')
      el.classList.add('lazy-loaded')
    }
  },

  updated(el, binding) {
    // If src changed, update
    if (binding.value !== el.dataset.src) {
      el.dataset.src = binding.value
      if (binding.modifiers.eager) {
        el.src = binding.value
      }
    }
  },

  unmounted(el) {
    // Clean up observer
    if (observer) {
      observer.unobserve(el)
    }
  }
}

