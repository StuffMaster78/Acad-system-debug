<template>
  <Layout>
    <!-- Hero Section -->
    <section class="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
      <div class="container-custom section-padding">
        <div class="max-w-3xl mx-auto text-center">
          <h1 class="text-5xl md:text-6xl font-bold mb-6">
            Professional Writing Services
          </h1>
          <p class="text-xl md:text-2xl mb-8 text-primary-100">
            Get high-quality essays, research papers, and academic writing from expert writers
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link to="/order" class="btn bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-4">
              Order Now
            </router-link>
            <router-link to="/pricing" class="btn btn-outline border-white text-white hover:bg-white/10 text-lg px-8 py-4">
              View Pricing
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="section-padding bg-white">
      <div class="container-custom">
        <h2 class="text-3xl md:text-4xl font-bold text-center mb-12">
          Why Choose Us?
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="feature in features" :key="feature.title" class="text-center p-6">
            <div class="text-4xl mb-4">{{ feature.icon }}</div>
            <h3 class="text-xl font-semibold mb-2">{{ feature.title }}</h3>
            <p class="text-gray-600">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Services Preview -->
    <section class="section-padding bg-gray-50">
      <div class="container-custom">
        <h2 class="text-3xl md:text-4xl font-bold text-center mb-12">
          Our Services
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="service in services" :key="service.name" class="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition">
            <h3 class="text-lg font-semibold mb-2">{{ service.name }}</h3>
            <p class="text-gray-600 text-sm">{{ service.description }}</p>
          </div>
        </div>
        <div class="text-center mt-8">
          <router-link to="/services" class="btn btn-primary">
            View All Services
          </router-link>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="section-padding bg-primary-600 text-white">
      <div class="container-custom text-center">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">
          Ready to Get Started?
        </h2>
        <p class="text-xl mb-8 text-primary-100">
          Place your order today and get professional writing delivered on time
        </p>
        <router-link to="/order" class="btn bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-4">
          Place Your Order
        </router-link>
      </div>
    </section>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { useWebsiteStore } from '@/stores/website'

const websiteStore = useWebsiteStore()

const features = ref([
  {
    icon: '✍️',
    title: 'Expert Writers',
    description: 'Professional writers with advanced degrees and years of experience'
  },
  {
    icon: '⏰',
    title: 'On-Time Delivery',
    description: 'We guarantee timely delivery of all orders, no matter how urgent'
  },
  {
    icon: '✅',
    title: 'Quality Guaranteed',
    description: '100% original content with free revisions until you\'re satisfied'
  },
])

const services = ref([
  { name: 'Essays', description: 'Custom essays on any topic' },
  { name: 'Research Papers', description: 'In-depth research and analysis' },
  { name: 'Dissertations', description: 'Comprehensive dissertation writing' },
  { name: 'Thesis', description: 'Professional thesis writing services' },
])

onMounted(() => {
  websiteStore.detectWebsite()
})
</script>

