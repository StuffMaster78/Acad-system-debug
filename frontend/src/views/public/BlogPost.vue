<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center min-h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-4xl mx-auto px-4 py-16">
      <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <h1 class="text-2xl font-bold text-red-900 mb-2">Error Loading Blog Post</h1>
        <p class="text-red-700">{{ error }}</p>
        <button
          @click="$router.push('/')"
          class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Go Home
        </button>
      </div>
    </div>

    <!-- Blog Post Content -->
    <article v-else-if="blogPost" class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <header class="mb-8">
        <div v-if="blogPost.category" class="mb-4">
          <span class="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            {{ blogPost.category.name }}
          </span>
        </div>
        
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          {{ blogPost.title }}
        </h1>

        <!-- Meta Info -->
        <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-6">
          <span v-if="blogPost.publish_date">
            {{ formatDate(blogPost.publish_date) }}
          </span>
          <span v-if="blogPost.read_time">• {{ blogPost.read_time }} min read</span>
        </div>

        <!-- Featured Image -->
        <img
          v-if="blogPost.featured_image"
          :src="blogPost.featured_image"
          :alt="blogPost.title"
          class="w-full h-auto rounded-lg mb-8 object-cover"
        />
      </header>

      <!-- Author Strip -->
      <AuthorStrip v-if="blogPost.authors && blogPost.authors.length > 0" :authors="blogPost.authors" />

      <!-- Table of Contents -->
      <TableOfContents v-if="blogPost.toc && Array.isArray(blogPost.toc) && blogPost.toc.length > 0" :toc="blogPost.toc" />

      <!-- Top CTAs -->
      <div v-if="topCTAs.length > 0" class="mb-8 space-y-4">
        <CTABlock
          v-for="cta in topCTAs"
          :key="cta.id"
          :cta="cta"
          :placement-id="cta.placement_id"
          :website-id="websiteId"
          :blog-id="blogPost.id"
        />
      </div>

      <!-- Content -->
      <div class="prose prose-lg max-w-none mb-12">
        <SafeHtml :content="blogPost.content" container-class="prose prose-lg max-w-none" />
        
        <!-- Middle/Inline CTAs (shown after content for now) -->
        <div v-if="inlineCTAs.length > 0" class="mt-8 space-y-4">
          <CTABlock
            v-for="cta in inlineCTAs"
            :key="`inline-${cta.id}`"
            :cta="cta"
            :placement-id="cta.placement_id"
            :website-id="websiteId"
            :blog-id="blogPost.id"
          />
        </div>
      </div>

      <!-- Bottom CTAs -->
      <div v-if="bottomCTAs.length > 0" class="mt-8 space-y-4">
        <CTABlock
          v-for="cta in bottomCTAs"
          :key="cta.id"
          :cta="cta"
          :placement-id="cta.placement_id"
          :website-id="websiteId"
          :blog-id="blogPost.id"
        />
      </div>

      <!-- Engagement Section -->
      <div class="border-t border-b border-gray-200 py-6 my-8">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <!-- Engagement Stats -->
          <EngagementStats
            :view-count="blogPost.view_count"
            :avg-scroll-percent="blogPost.avg_scroll_percent"
            :cta-clicks="blogPost.primary_cta_clicks"
          />

          <!-- Like/Dislike Buttons -->
          <LikeDislikeButtons
            v-if="websiteId"
            :website-id="websiteId"
            content-type="blogpost"
            :object-id="blogPost.id"
            :initial-like-count="blogPost.like_count || 0"
            :initial-dislike-count="blogPost.dislike_count || 0"
          />
        </div>
      </div>

      <!-- Tags -->
      <div v-if="blogPost.tags && blogPost.tags.length > 0" class="mb-8">
        <div class="flex flex-wrap gap-2">
          <span
            v-for="tag in blogPost.tags"
            :key="tag.id"
            class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 cursor-pointer"
          >
            #{{ tag.name }}
          </span>
        </div>
      </div>

      <!-- Related Content -->
      <RelatedContentWidget
        v-if="websiteId"
        :post-id="blogPost.id"
        :website-id="websiteId"
        content-type="blog"
        :limit="5"
        title="Related Posts"
      />
    </article>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import blogPagesAPI from '@/api/blog-pages'
import { initPageTracking } from '@/utils/contentTracker'
import AuthorStrip from '@/components/blog/AuthorStrip.vue'
import LikeDislikeButtons from '@/components/engagement/LikeDislikeButtons.vue'
import EngagementStats from '@/components/engagement/EngagementStats.vue'
import RelatedContentWidget from '@/components/blog/RelatedContentWidget.vue'
import SafeHtml from '@/components/common/SafeHtml.vue'
import TableOfContents from '@/components/blog/TableOfContents.vue'
import CTABlock from '@/components/blog/CTABlock.vue'
import { computed } from 'vue'

const route = useRoute()
const blogPost = ref(null)
const websiteId = ref(null)
const loading = ref(true)
const error = ref(null)
const ctas = ref([])
let cleanupTracking = null

const topCTAs = computed(() => {
  return ctas.value.filter(cta => 
    cta.placement_type === 'auto_top' || 
    cta.placement_type === 'manual' && cta.position === 0
  )
})

const inlineCTAs = computed(() => {
  return ctas.value.filter(cta => 
    cta.placement_type === 'after_paragraph' || 
    cta.placement_type === 'after_heading' ||
    cta.placement_type === 'auto_middle'
  )
})

const bottomCTAs = computed(() => {
  return ctas.value.filter(cta => 
    cta.placement_type === 'auto_bottom'
  )
})

const loadBlogPost = async () => {
  loading.value = true
  error.value = null
  
  try {
    const slug = route.params.slug
    const response = await blogPagesAPI.listBlogs({ slug, is_published: true })
    
    if (response.data?.results?.length > 0) {
      blogPost.value = response.data.results[0]
      websiteId.value = blogPost.value.website?.id || blogPost.value.website_id
      
      // Initialize engagement tracking
      if (websiteId.value) {
        cleanupTracking = initPageTracking({
          websiteId: websiteId.value,
          contentType: 'blogpost',
          objectId: blogPost.value.id
        })
      }
      
      // Update page title and meta
      if (blogPost.value.meta_title) {
        document.title = blogPost.value.meta_title
      }
      if (blogPost.value.meta_description) {
        const metaDesc = document.querySelector('meta[name="description"]')
        if (metaDesc) {
          metaDesc.setAttribute('content', blogPost.value.meta_description)
        } else {
          const meta = document.createElement('meta')
          meta.name = 'description'
          meta.content = blogPost.value.meta_description
          document.head.appendChild(meta)
        }
      }

      // Load CTAs for this blog post
      await loadCTAs(blogPost.value.id)
    } else {
      error.value = 'Blog post not found'
    }
  } catch (e) {
    console.error('Failed to load blog post:', e)
    error.value = e.response?.data?.detail || 'Failed to load blog post'
  } finally {
    loading.value = false
  }
}

const loadCTAs = async (blogId) => {
  if (!blogId) return
  
  try {
    const response = await blogPagesAPI.getBlogCTAs(blogId)
    ctas.value = response.data || []
  } catch (error) {
    console.warn('Failed to load CTAs:', error)
    ctas.value = []
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

onMounted(() => {
  loadBlogPost()
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

