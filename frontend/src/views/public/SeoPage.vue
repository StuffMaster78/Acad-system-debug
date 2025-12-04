<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-4xl mx-auto px-4 py-16">
      <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <h1 class="text-2xl font-bold text-red-900 mb-2">Error Loading Page</h1>
        <p class="text-red-700">{{ error }}</p>
        <button
          @click="$router.push('/')"
          class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Go Home
        </button>
      </div>
    </div>

    <!-- SEO Page Content -->
    <article v-else-if="seoPage" class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <header class="mb-8">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          {{ seoPage.title }}
        </h1>

        <!-- Meta Info -->
        <div v-if="seoPage.publish_date" class="text-sm text-gray-600 mb-6">
          Published {{ formatDate(seoPage.publish_date) }}
        </div>
      </header>

      <!-- Blocks Content -->
      <div class="prose prose-lg max-w-none mb-12">
        <div v-for="(block, index) in seoPage.blocks" :key="index" class="mb-6">
          <!-- Paragraph Block -->
          <div v-if="block.type === 'paragraph'" class="mb-4">
            <p class="text-gray-700 leading-relaxed">{{ block.content }}</p>
          </div>

          <!-- Heading Block -->
          <div v-else-if="block.type === 'heading'">
            <component
              :is="`h${block.level || 2}`"
              :class="[
                'font-bold text-gray-900 mb-4',
                block.level === 1 ? 'text-3xl' : block.level === 2 ? 'text-2xl' : 'text-xl'
              ]"
            >
              {{ block.content }}
            </component>
          </div>

          <!-- Image Block -->
          <div v-else-if="block.type === 'image'" class="my-6">
            <img
              :src="block.url"
              :alt="block.alt || ''"
              class="w-full h-auto rounded-lg"
            />
            <p v-if="block.caption" class="text-sm text-gray-600 text-center mt-2">
              {{ block.caption }}
            </p>
          </div>

          <!-- CTA Block -->
          <div v-else-if="block.type === 'cta'" class="my-8 p-6 bg-blue-50 border border-blue-200 rounded-lg text-center">
            <h3 v-if="block.title" class="text-xl font-semibold text-gray-900 mb-2">
              {{ block.title }}
            </h3>
            <p v-if="block.description" class="text-gray-700 mb-4">
              {{ block.description }}
            </p>
            <a
              v-if="block.button_text && block.button_url"
              :href="block.button_url"
              class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              @click="handleCTAClick(block)"
            >
              {{ block.button_text }}
            </a>
          </div>

          <!-- List Block -->
          <div v-else-if="block.type === 'list'" class="my-4">
            <ul v-if="block.style === 'unordered'" class="list-disc list-inside space-y-2">
              <li v-for="(item, i) in block.items" :key="i" class="text-gray-700">
                {{ item }}
              </li>
            </ul>
            <ol v-else class="list-decimal list-inside space-y-2">
              <li v-for="(item, i) in block.items" :key="i" class="text-gray-700">
                {{ item }}
              </li>
            </ol>
          </div>
        </div>
      </div>

      <!-- Engagement Section -->
      <div v-if="websiteId" class="border-t border-b border-gray-200 py-6 my-8">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <!-- Engagement Stats -->
          <EngagementStats
            :view-count="null"
            :avg-scroll-percent="null"
            :cta-clicks="null"
          />

          <!-- Like/Dislike Buttons -->
          <LikeDislikeButtons
            :website-id="websiteId"
            content-type="seopage"
            :object-id="seoPage.id"
            :initial-like-count="0"
            :initial-dislike-count="0"
          />
        </div>
      </div>
    </article>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import seoPagesAPI from '@/api/seo-pages'
import { initPageTracking, trackCTA } from '@/utils/contentTracker'
import LikeDislikeButtons from '@/components/engagement/LikeDislikeButtons.vue'
import EngagementStats from '@/components/engagement/EngagementStats.vue'

const route = useRoute()
const seoPage = ref(null)
const websiteId = ref(null)
const loading = ref(true)
const error = ref(null)
let cleanupTracking = null

const loadSeoPage = async () => {
  loading.value = true
  error.value = null
  
  try {
    const slug = route.params.slug
    const websiteIdParam = route.query.website_id
    
    const response = await seoPagesAPI.getBySlug(slug, websiteIdParam ? { website_id: websiteIdParam } : {})
    
    if (response.data) {
      seoPage.value = response.data
      websiteId.value = seoPage.value.website?.id || websiteIdParam
      
      // Initialize engagement tracking
      if (websiteId.value) {
        cleanupTracking = initPageTracking({
          websiteId: websiteId.value,
          contentType: 'seopage',
          objectId: seoPage.value.id
        })
      }
      
      // Update page title and meta
      const metaTitle = seoPage.value.meta_title || seoPage.value.title
      if (metaTitle) {
        document.title = metaTitle
      }
      if (seoPage.value.meta_description) {
        const metaDesc = document.querySelector('meta[name="description"]')
        if (metaDesc) {
          metaDesc.setAttribute('content', seoPage.value.meta_description)
        } else {
          const meta = document.createElement('meta')
          meta.name = 'description'
          meta.content = seoPage.value.meta_description
          document.head.appendChild(meta)
        }
      }
    } else {
      error.value = 'Page not found'
    }
  } catch (e) {
    console.error('Failed to load SEO page:', e)
    error.value = e.response?.data?.detail || 'Failed to load page'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const handleCTAClick = (block) => {
  if (websiteId.value) {
    trackCTA({
      websiteId: websiteId.value,
      contentType: 'seopage',
      objectId: seoPage.value.id,
      metadata: { cta_id: block.id || block.title }
    })
  }
}

onMounted(() => {
  loadSeoPage()
})

onUnmounted(() => {
  if (cleanupTracking) {
    cleanupTracking()
  }
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

