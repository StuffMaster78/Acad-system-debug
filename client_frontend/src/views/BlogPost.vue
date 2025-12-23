<template>
  <Layout>
    <div class="section-padding bg-white">
      <div class="container-custom max-w-4xl">
        <div v-if="loading" class="text-center py-12">
          <p class="text-gray-600">Loading...</p>
        </div>

        <article v-else-if="post">
          <div class="mb-8">
            <div class="text-sm text-gray-500 mb-4">
              {{ formatDate(post.published_date || post.created_at) }}
            </div>
            <h1 class="text-4xl md:text-5xl font-bold mb-4">{{ post.title }}</h1>
            <div v-if="post.featured_image" class="mb-8">
              <img :src="post.featured_image" :alt="post.title" class="w-full rounded-lg" />
            </div>
          </div>

          <div class="prose max-w-none" v-html="post.content"></div>

          <div class="mt-12 pt-8 border-t">
            <router-link to="/blog" class="text-primary-600 hover:underline">
              ← Back to Blog
            </router-link>
          </div>
        </article>

        <div v-else class="text-center py-12">
          <p class="text-gray-600">Post not found.</p>
          <router-link to="/blog" class="text-primary-600 hover:underline mt-4 inline-block">
            Back to Blog
          </router-link>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'
import servicesAPI from '@/api/services'
import { useWebsiteStore } from '@/stores/website'

const route = useRoute()
const websiteStore = useWebsiteStore()
const post = ref(null)
const loading = ref(true)

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const fetchPost = async () => {
  loading.value = true
  try {
    const response = await servicesAPI.getBlogPost(route.params.slug)
    post.value = response.data
  } catch (error) {
    console.error('Failed to fetch blog post:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  websiteStore.detectWebsite()
  fetchPost()
})
</script>

