<template>
  <div
    ref="el"
    :class="[
      'lazy-image-container',
      containerClass,
      { 'lazy-image-loading': isLoading, 'lazy-image-loaded': isLoaded }
    ]"
    :style="containerStyle"
  >
    <!-- Placeholder/Skeleton -->
    <div
      v-if="!isLoaded"
      :class="[
        'lazy-image-placeholder',
        'bg-gray-200 dark:bg-gray-700',
        'flex items-center justify-center',
        placeholderClass
      ]"
      :style="placeholderStyle"
    >
      <div v-if="showPlaceholderIcon" class="text-gray-400">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <div v-if="showSpinner" class="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-400"></div>
    </div>

    <!-- Actual Image -->
    <img
      v-show="isLoaded"
      :src="imageSrc"
      :srcset="srcset"
      :sizes="sizes"
      :alt="alt"
      :class="[
        'lazy-image',
        imageClass,
        { 'lazy-image-fade-in': fadeIn }
      ]"
      :style="imageStyle"
      @load="handleLoad"
      @error="handleError"
      :loading="eager ? 'eager' : 'lazy'"
      :decoding="decoding"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  // Responsive image support
  srcset: {
    type: String,
    default: null
  },
  sizes: {
    type: String,
    default: null
  },
  // Styling
  imageClass: {
    type: String,
    default: ''
  },
  containerClass: {
    type: String,
    default: ''
  },
  placeholderClass: {
    type: String,
    default: ''
  },
  containerStyle: {
    type: [String, Object],
    default: () => ({})
  },
  placeholderStyle: {
    type: [String, Object],
    default: () => ({})
  },
  imageStyle: {
    type: [String, Object],
    default: () => ({})
  },
  // Behavior
  eager: {
    type: Boolean,
    default: false // If true, load immediately (above the fold)
  },
  rootMargin: {
    type: String,
    default: '50px' // Start loading 50px before image enters viewport
  },
  threshold: {
    type: Number,
    default: 0.01 // Load when 1% of image is visible
  },
  fadeIn: {
    type: Boolean,
    default: true // Fade in animation when loaded
  },
  showPlaceholderIcon: {
    type: Boolean,
    default: false
  },
  showSpinner: {
    type: Boolean,
    default: false
  },
  decoding: {
    type: String,
    default: 'async', // 'async', 'sync', or 'auto'
    validator: (value) => ['async', 'sync', 'auto'].includes(value)
  },
  // Aspect ratio for placeholder
  aspectRatio: {
    type: String,
    default: null // e.g., '16/9', '4/3', '1/1'
  }
})

const emit = defineEmits(['load', 'error'])

const isLoading = ref(false)
const isLoaded = ref(false)
const hasError = ref(false)
const observer = ref(null)
const el = ref(null)

const imageSrc = ref(props.eager ? props.src : '')

const placeholderStyleComputed = computed(() => {
  const style = { ...props.placeholderStyle }
  if (props.aspectRatio) {
    style.aspectRatio = props.aspectRatio
  }
  return style
})

const handleLoad = (event) => {
  isLoaded.value = true
  isLoading.value = false
  emit('load', event)
}

const handleError = (event) => {
  hasError.value = true
  isLoading.value = false
  emit('error', event)
}

const loadImage = () => {
  if (isLoaded.value || isLoading.value || hasError.value) {
    return
  }

  isLoading.value = true
  // Set src immediately - the browser will load it
  // The @load event on the img element will handle success
  imageSrc.value = props.src
}

const setupIntersectionObserver = () => {
  if (props.eager) {
    // Load immediately if eager
    loadImage()
    return
  }

  // Check if IntersectionObserver is supported
  if (typeof IntersectionObserver === 'undefined') {
    // Fallback: load immediately
    loadImage()
    return
  }

  // Create observer
  observer.value = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          loadImage()
          // Stop observing once we start loading
          if (observer.value) {
            observer.value.unobserve(entry.target)
          }
        }
      })
    },
    {
      rootMargin: props.rootMargin,
      threshold: props.threshold
    }
  )

  // Observe the container element
  onMounted(() => {
    if (props.eager) {
      // Load immediately if eager
      loadImage()
      return
    }
    
    nextTick(() => {
      // Observe the container element
      if (el.value && observer.value) {
        observer.value.observe(el.value)
      }
    })
  })
}

// Watch for src changes
watch(() => props.src, (newSrc) => {
  if (newSrc && (props.eager || isLoaded.value)) {
    // Reload if src changes and we're already loaded
    isLoaded.value = false
    hasError.value = false
    loadImage()
  }
})

onMounted(() => {
  setupIntersectionObserver()
})

onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect()
    observer.value = null
  }
})
</script>

<style scoped>
.lazy-image-container {
  position: relative;
  overflow: hidden;
}

.lazy-image-placeholder {
  width: 100%;
  height: 100%;
  min-height: 100px;
}

.lazy-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.lazy-image-fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.lazy-image-loading .lazy-image {
  opacity: 0;
}

.lazy-image-loaded .lazy-image {
  opacity: 1;
}
</style>

