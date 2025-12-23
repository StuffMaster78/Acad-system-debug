<template>
  <Layout>
    <div class="section-padding bg-white">
      <div class="container-custom">
        <div class="text-center mb-12">
          <h1 class="text-4xl md:text-5xl font-bold mb-4">Our Services</h1>
          <p class="text-xl text-gray-600">Comprehensive writing solutions for all your needs</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div 
            v-for="service in services" 
            :key="service.name"
            class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition"
          >
            <div class="text-4xl mb-4">{{ service.icon }}</div>
            <h3 class="text-xl font-semibold mb-2">{{ service.name }}</h3>
            <p class="text-gray-600 mb-4">{{ service.description }}</p>
            <ul class="space-y-2 mb-6">
              <li v-for="feature in service.features" :key="feature" class="flex items-start text-sm">
                <span class="text-green-500 mr-2">✓</span>
                <span>{{ feature }}</span>
              </li>
            </ul>
            <router-link to="/order" class="btn btn-primary w-full">
              Order Now
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { useWebsiteStore } from '@/stores/website'

const websiteStore = useWebsiteStore()

const services = ref([
  {
    name: 'Essays',
    icon: '📝',
    description: 'Custom essays on any topic, any academic level',
    features: [
      '100% original content',
      'Free revisions',
      'On-time delivery',
      'Expert writers'
    ]
  },
  {
    name: 'Research Papers',
    icon: '📊',
    description: 'In-depth research papers with proper citations',
    features: [
      'Thorough research',
      'Proper citations',
      'Academic formatting',
      'Quality guarantee'
    ]
  },
  {
    name: 'Dissertations',
    icon: '🎓',
    description: 'Comprehensive dissertation writing services',
    features: [
      'PhD-level writers',
      'Extensive research',
      'Multiple revisions',
      'Full support'
    ]
  },
  {
    name: 'Thesis',
    icon: '📚',
    description: 'Professional thesis writing and editing',
    features: [
      'Expert guidance',
      'Research support',
      'Formatting help',
      'Quality assurance'
    ]
  },
  {
    name: 'Case Studies',
    icon: '🔍',
    description: 'Detailed case study analysis and writing',
    features: [
      'Real-world examples',
      'In-depth analysis',
      'Professional format',
      'Timely delivery'
    ]
  },
  {
    name: 'Editing & Proofreading',
    icon: '✏️',
    description: 'Professional editing and proofreading services',
    features: [
      'Grammar check',
      'Style improvement',
      'Fast turnaround',
      'Quality enhancement'
    ]
  },
])

onMounted(() => {
  websiteStore.detectWebsite()
})
</script>

