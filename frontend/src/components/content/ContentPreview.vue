<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="handleClose">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-7xl w-full h-[90dvh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Content Preview</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ contentType === 'blog' ? 'Blog Post' : 'SEO Page' }} Preview
              <span v-if="!isPublished" class="ml-2 px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-xs font-medium">
                Draft
              </span>
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="handleOpenInNewTab"
            class="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Open in New Tab
          </button>
          <button
            @click="handleClose"
            class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Preview Content -->
      <div class="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900">
        <div v-if="loading" class="flex items-center justify-center h-full">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p class="text-gray-600 dark:text-gray-400">Loading preview...</p>
          </div>
        </div>

        <div v-else-if="error" class="flex items-center justify-center h-full">
          <div class="text-center max-w-md mx-auto p-6">
            <div class="p-3 bg-red-100 dark:bg-red-900 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Error Loading Preview</h3>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
            <button
              @click="loadPreview"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>

        <!-- Blog Preview -->
        <div v-else-if="contentType === 'blog' && previewData?.blog" class="min-h-full">
          <BlogPostPreview :blog-post="previewData.blog" :is-preview="true" />
        </div>

        <!-- SEO Page Preview -->
        <div v-else-if="contentType === 'seo' && previewData?.page" class="min-h-full">
          <SeoPagePreview :seo-page="previewData.page" :is-preview="true" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import seoPagesAPI from '@/api/seo-pages'
import BlogPostPreview from '@/views/public/BlogPost.vue'
import SeoPagePreview from '@/views/public/SeoPage.vue'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  contentType: {
    type: String,
    required: true,
    validator: (value) => ['blog', 'seo'].includes(value)
  },
  contentId: {
    type: [Number, String],
    default: null
  },
  contentSlug: {
    type: String,
    default: null
  },
  websiteId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close', 'update:show'])

const { error: showError } = useToast()

const loading = ref(false)
const error = ref(null)
const previewData = ref(null)
const isPublished = ref(false)

const loadPreview = async () => {
  if (!props.contentId && !props.contentSlug) {
    error.value = 'Content ID or slug is required'
    return
  }

  loading.value = true
  error.value = null

  try {
    let response

    if (props.contentType === 'blog') {
      if (props.contentSlug) {
        const params = props.websiteId ? { website_id: props.websiteId } : {}
        response = await blogPagesAPI.previewBlogBySlug(props.contentSlug, params)
      } else {
        response = await blogPagesAPI.previewBlog(props.contentId)
      }
      previewData.value = { blog: response.data.blog }
      isPublished.value = response.data.is_published || false
    } else if (props.contentType === 'seo') {
      response = await seoPagesAPI.preview(props.contentId)
      previewData.value = { page: response.data.page }
      isPublished.value = response.data.is_published || false
    }
  } catch (e) {
    console.error('Failed to load preview:', e)
    error.value = e.response?.data?.error || e.response?.data?.detail || 'Failed to load preview'
    showError(error.value)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('close')
  emit('update:show', false)
  previewData.value = null
  error.value = null
}

const handleOpenInNewTab = () => {
  if (props.contentType === 'blog' && previewData.value?.blog) {
    const slug = previewData.value.blog.slug
    const url = `/blog/${slug}${props.websiteId ? `?website_id=${props.websiteId}` : ''}`
    window.open(url, '_blank')
  } else if (props.contentType === 'seo' && previewData.value?.page) {
    const slug = previewData.value.page.slug
    const url = `/seo/${slug}${props.websiteId ? `?website_id=${props.websiteId}` : ''}`
    window.open(url, '_blank')
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    loadPreview()
  }
})

// Close on Escape key
onMounted(() => {
  const handleEscape = (e) => {
    if (e.key === 'Escape' && props.show) {
      handleClose()
    }
  }
  document.addEventListener('keydown', handleEscape)
  
  return () => {
    document.removeEventListener('keydown', handleEscape)
  }
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

