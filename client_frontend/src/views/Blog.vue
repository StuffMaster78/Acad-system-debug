<template>
  <Layout>
    <div class="section-padding bg-white">
      <div class="container-custom">
        <h1 class="text-4xl font-bold mb-4">Blog</h1>
        <p class="text-xl text-gray-600 mb-12">Latest articles and writing tips</p>

        <div v-if="loading" class="text-center py-12">
          <p class="text-gray-600">Loading posts...</p>
        </div>

        <div v-else-if="posts.length === 0" class="text-center py-12">
          <p class="text-gray-600">No blog posts available yet.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <article 
            v-for="post in posts" 
            :key="post.id"
            class="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition"
          >
            <div v-if="post.featured_image" class="h-48 bg-gray-200">
              <img :src="post.featured_image" :alt="post.title" class="w-full h-full object-cover" />
            </div>
            <div class="p-6">
              <div class="text-sm text-gray-500 mb-2">
                {{ formatDate(post.published_date || post.created_at) }}
              </div>
              <h2 class="text-xl font-semibold mb-2">
                <router-link :to="`/blog/${post.slug}`" class="hover:text-primary-600">
                  {{ post.title }}
                </router-link>
              </h2>
              <p class="text-gray-600 mb-4 line-clamp-3">
                {{ post.excerpt || post.content?.substring(0, 150) + '...' }}
              </p>
              <router-link 
                :to="`/blog/${post.slug}`" 
                class="text-primary-600 hover:underline font-semibold"
              >
                Read more →
              </router-link>
            </div>
          </article>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import servicesAPI from '@/api/services'
import { useWebsiteStore } from '@/stores/website'

const websiteStore = useWebsiteStore()
const posts = ref([])
const loading = ref(true)

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const fetchPosts = async () => {
  loading.value = true
  try {
    const response = await servicesAPI.getBlogPosts({
      is_published: true,
      page_size: 12
    })
    posts.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to fetch blog posts:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  websiteStore.detectWebsite()
  fetchPosts()
})
</script>

