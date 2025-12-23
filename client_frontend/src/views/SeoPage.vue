<template>
  <Layout>
    <div class="section-padding bg-white">
      <div class="container-custom max-w-4xl">
        <div v-if="loading" class="text-center py-12">
          <p class="text-gray-600">Loading...</p>
        </div>

        <div v-else-if="page">
          <h1 class="text-4xl md:text-5xl font-bold mb-6">{{ page.title }}</h1>
          
          <div v-if="page.blocks && page.blocks.length > 0" class="prose max-w-none">
            <div v-for="(block, index) in page.blocks" :key="index" class="mb-6">
              <component :is="getBlockComponent(block.type)" :block="block" />
            </div>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <p class="text-gray-600">Page not found.</p>
          <router-link to="/" class="text-primary-600 hover:underline mt-4 inline-block">
            Back to Home
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
const page = ref(null)
const loading = ref(true)

const getBlockComponent = (type) => {
  const components = {
    heading: 'h2',
    paragraph: 'p',
    image: 'img',
  }
  return components[type] || 'div'
}

const fetchPage = async () => {
  loading.value = true
  try {
    const response = await servicesAPI.getSeoPage(route.params.slug)
    page.value = response.data
  } catch (error) {
    console.error('Failed to fetch SEO page:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  websiteStore.detectWebsite()
  fetchPage()
})
</script>

