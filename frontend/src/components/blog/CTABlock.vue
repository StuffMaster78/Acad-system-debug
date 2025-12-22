<template>
  <div
    :class="[
      'cta-block',
      `cta-${cta.type}`,
      `cta-${cta.style || 'primary'}`,
      getContainerClass()
    ]"
  >
    <!-- Button CTA -->
    <div v-if="cta.type === 'button'" class="cta-button-container">
      <div v-if="cta.title" class="cta-title text-xl font-bold mb-2">
        {{ cta.title }}
      </div>
      <div v-if="cta.description" class="cta-description mb-4 text-gray-700 dark:text-gray-300">
        {{ cta.description }}
      </div>
      <a
        v-if="cta.button_text && cta.button_url"
        :href="cta.button_url"
        @click="handleClick"
        :class="getButtonClass()"
        :target="isExternalUrl(cta.button_url) ? '_blank' : '_self'"
        :rel="isExternalUrl(cta.button_url) ? 'noopener noreferrer' : ''"
      >
        {{ cta.button_text }}
      </a>
    </div>

    <!-- Banner CTA -->
    <div v-else-if="cta.type === 'banner'" class="cta-banner-container">
      <div class="flex flex-col md:flex-row items-center gap-4">
        <img
          v-if="cta.image"
          :src="cta.image"
          :alt="cta.title || 'CTA Image'"
          class="w-full md:w-1/3 h-auto rounded-lg object-cover"
        />
        <div class="flex-1 text-center md:text-left">
          <div v-if="cta.title" class="cta-title text-2xl font-bold mb-2">
            {{ cta.title }}
          </div>
          <div v-if="cta.description" class="cta-description mb-4 text-gray-700 dark:text-gray-300">
            {{ cta.description }}
          </div>
          <a
            v-if="cta.button_text && cta.button_url"
            :href="cta.button_url"
            @click="handleClick"
            :class="getButtonClass()"
            :target="isExternalUrl(cta.button_url) ? '_blank' : '_self'"
            :rel="isExternalUrl(cta.button_url) ? 'noopener noreferrer' : ''"
          >
            {{ cta.button_text }}
          </a>
        </div>
      </div>
    </div>

    <!-- Inline Text CTA -->
    <div v-else-if="cta.type === 'inline'" class="cta-inline-container">
      <span v-if="cta.description" class="cta-description mr-2">
        {{ cta.description }}
      </span>
      <a
        v-if="cta.button_text && cta.button_url"
        :href="cta.button_url"
        @click="handleClick"
        :class="getInlineLinkClass()"
        :target="isExternalUrl(cta.button_url) ? '_blank' : '_self'"
        :rel="isExternalUrl(cta.button_url) ? 'noopener noreferrer' : ''"
      >
        {{ cta.button_text }}
      </a>
    </div>

    <!-- Form CTA -->
    <div v-else-if="cta.type === 'form'" class="cta-form-container">
      <div v-if="cta.title" class="cta-title text-xl font-bold mb-2">
        {{ cta.title }}
      </div>
      <div v-if="cta.description" class="cta-description mb-4 text-gray-700 dark:text-gray-300">
        {{ cta.description }}
      </div>
      <form
        v-if="cta.button_url"
        :action="cta.button_url"
        method="get"
        @submit="handleClick"
        class="flex flex-col sm:flex-row gap-2"
      >
        <input
          type="email"
          placeholder="Enter your email"
          required
          class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100"
        />
        <button
          type="submit"
          :class="getButtonClass()"
        >
          {{ cta.button_text || 'Submit' }}
        </button>
      </form>
    </div>

    <!-- Download CTA -->
    <div v-else-if="cta.type === 'download'" class="cta-download-container">
      <div class="flex items-center gap-4">
        <div class="shrink-0">
          <svg class="w-12 h-12 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="flex-1">
          <div v-if="cta.title" class="cta-title text-xl font-bold mb-2">
            {{ cta.title }}
          </div>
          <div v-if="cta.description" class="cta-description mb-4 text-gray-700 dark:text-gray-300">
            {{ cta.description }}
          </div>
          <a
            v-if="cta.button_text && cta.button_url"
            :href="cta.button_url"
            @click="handleClick"
            :class="getButtonClass()"
            :target="isExternalUrl(cta.button_url) ? '_blank' : '_self'"
            :rel="isExternalUrl(cta.button_url) ? 'noopener noreferrer' : ''"
            download
          >
            {{ cta.button_text }}
          </a>
        </div>
      </div>
    </div>

    <!-- Custom HTML CTA -->
    <div
      v-else-if="cta.type === 'custom' && cta.html"
      class="cta-custom-container"
      v-html="cta.html"
      @click="handleClick"
    ></div>

    <!-- Default/Generic CTA -->
    <div v-else class="cta-default-container">
      <div v-if="cta.title" class="cta-title text-xl font-bold mb-2">
        {{ cta.title }}
      </div>
      <div v-if="cta.description" class="cta-description mb-4 text-gray-700 dark:text-gray-300">
        {{ cta.description }}
      </div>
      <a
        v-if="cta.button_text && cta.button_url"
        :href="cta.button_url"
        @click="handleClick"
        :class="getButtonClass()"
        :target="isExternalUrl(cta.button_url) ? '_blank' : '_self'"
        :rel="isExternalUrl(cta.button_url) ? 'noopener noreferrer' : ''"
      >
        {{ cta.button_text }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { trackCTA } from '@/utils/contentTracker'

const props = defineProps({
  cta: {
    type: Object,
    required: true
  },
  placementId: {
    type: Number,
    default: null
  },
  websiteId: {
    type: Number,
    default: null
  },
  blogId: {
    type: Number,
    default: null
  }
})

const getContainerClass = () => {
  const baseClasses = 'rounded-lg p-6 transition-all duration-200'
  
  // Style-based classes
  const styleClasses = {
    'primary': 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800',
    'secondary': 'bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
    'success': 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800',
    'warning': 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800',
    'danger': 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800',
    'info': 'bg-cyan-50 dark:bg-cyan-900/20 border border-cyan-200 dark:border-cyan-800',
    'light': 'bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600',
    'dark': 'bg-gray-800 dark:bg-gray-900 border border-gray-700 dark:border-gray-600 text-white'
  }
  
  return `${baseClasses} ${styleClasses[props.cta.style] || styleClasses.primary}`
}

const getButtonClass = () => {
  const baseClasses = 'inline-block px-6 py-3 rounded-lg font-semibold text-center transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-95'
  
  const styleClasses = {
    'primary': 'bg-blue-600 text-white hover:bg-blue-700',
    'secondary': 'bg-gray-600 text-white hover:bg-gray-700',
    'success': 'bg-green-600 text-white hover:bg-green-700',
    'warning': 'bg-yellow-600 text-white hover:bg-yellow-700',
    'danger': 'bg-red-600 text-white hover:bg-red-700',
    'info': 'bg-cyan-600 text-white hover:bg-cyan-700',
    'light': 'bg-white text-gray-900 border-2 border-gray-300 hover:bg-gray-50',
    'dark': 'bg-gray-900 text-white hover:bg-gray-800'
  }
  
  return `${baseClasses} ${styleClasses[props.cta.style] || styleClasses.primary}`
}

const getInlineLinkClass = () => {
  const baseClasses = 'font-semibold underline hover:no-underline transition-all duration-200'
  
  const styleClasses = {
    'primary': 'text-blue-600 hover:text-blue-700',
    'secondary': 'text-gray-600 hover:text-gray-700',
    'success': 'text-green-600 hover:text-green-700',
    'warning': 'text-yellow-600 hover:text-yellow-700',
    'danger': 'text-red-600 hover:text-red-700',
    'info': 'text-cyan-600 hover:text-cyan-700',
    'light': 'text-gray-700 hover:text-gray-900',
    'dark': 'text-gray-900 hover:text-gray-700'
  }
  
  return `${baseClasses} ${styleClasses[props.cta.style] || styleClasses.primary}`
}

const isExternalUrl = (url) => {
  if (!url) return false
  try {
    const urlObj = new URL(url, window.location.origin)
    return urlObj.origin !== window.location.origin
  } catch {
    return false
  }
}

const handleClick = async (event) => {
  // Track CTA click via analytics API
  // The backend will process this event and update placement click counts
  if (props.websiteId && props.blogId) {
    trackCTA({
      websiteId: props.websiteId,
      contentType: 'blogpost',
      objectId: props.blogId,
      metadata: {
        cta_id: props.cta.id,
        cta_type: props.cta.type,
        cta_tracking_id: props.cta.tracking_id,
        placement_id: props.placementId,
        button_url: props.cta.button_url
      }
    })
  }
}
</script>

<style scoped>
.cta-block {
  margin: 2rem 0;
}

.cta-block a {
  text-decoration: none;
}

.cta-custom-container :deep(a) {
  text-decoration: none;
}
</style>

