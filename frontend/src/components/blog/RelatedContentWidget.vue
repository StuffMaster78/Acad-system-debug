<template>
  <div class="related-content-widget">
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="relatedContent.length === 0" class="text-center py-8 text-gray-500">
      <p class="text-sm">No related content found</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in relatedContent"
        :key="item.id"
        class="related-item group bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
        @click="navigateToContent(item)"
      >
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0">
            <div
              :class="[
                'w-12 h-12 rounded-lg flex items-center justify-center text-white font-semibold text-sm',
                item.type === 'blog' ? 'bg-gradient-to-br from-purple-500 to-purple-600' : 'bg-gradient-to-br from-green-500 to-green-600'
              ]"
            >
              {{ item.type === 'blog' ? 'B' : 'P' }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="text-base font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors line-clamp-2">
              {{ item.title }}
            </h4>
            <p v-if="item.excerpt" class="text-sm text-gray-600 line-clamp-2 mb-2">
              {{ item.excerpt }}
            </p>
            <div class="flex items-center gap-3 text-xs text-gray-500">
              <span v-if="item.category" class="flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                {{ item.category }}
              </span>
              <span v-if="item.publish_date" class="flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ formatDate(item.publish_date) }}
              </span>
            </div>
          </div>
          <div class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import blogPagesAPI from '@/api/blog-pages'

const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  websiteId: {
    type: Number,
    required: true
  },
  contentType: {
    type: String,
    default: 'blog'
  },
  limit: {
    type: Number,
    default: 5
  },
  title: {
    type: String,
    default: 'Related Content'
  }
})

const router = useRouter()
const relatedContent = ref([])
const loading = ref(false)

const loadRelatedContent = async () => {
  loading.value = true
  try {
    const response = await blogPagesAPI.getRelatedContent(props.postId, {
      limit: props.limit
    })
    relatedContent.value = response.data.related_content || []
  } catch (error) {
    console.error('Failed to load related content:', error)
    relatedContent.value = []
  } finally {
    loading.value = false
  }
}

const navigateToContent = (item) => {
  if (item.url) {
    // External navigation
    window.location.href = item.url
  } else if (item.type === 'blog') {
    router.push(`/blog/${item.slug}`)
  } else {
    router.push(`/${item.slug}`)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadRelatedContent()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

