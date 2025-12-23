<template>
  <Layout>
    <div class="section-padding bg-white">
      <div class="container-custom">
        <div class="text-center mb-12">
          <h1 class="text-4xl md:text-5xl font-bold mb-4">Pricing</h1>
          <p class="text-xl text-gray-600">Transparent pricing for all your writing needs</p>
        </div>

        <!-- Pricing Calculator -->
        <div class="max-w-4xl mx-auto bg-gray-50 rounded-lg p-8 mb-12">
          <h2 class="text-2xl font-semibold mb-6">Calculate Your Price</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Paper Type *
              </label>
              <select 
                v-model="calculator.paper_type" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                @change="calculatePrice"
              >
                <option value="">Select type</option>
                <option value="essay">Essay</option>
                <option value="research_paper">Research Paper</option>
                <option value="dissertation">Dissertation</option>
                <option value="thesis">Thesis</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Academic Level *
              </label>
              <select 
                v-model="calculator.academic_level" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                @change="calculatePrice"
              >
                <option value="">Select level</option>
                <option value="high_school">High School</option>
                <option value="undergraduate">Undergraduate</option>
                <option value="masters">Masters</option>
                <option value="phd">PhD</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Number of Pages *
              </label>
              <input 
                v-model.number="calculator.pages" 
                type="number" 
                min="1"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                @input="calculatePrice"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Deadline (days) *
              </label>
              <select 
                v-model="calculator.deadline_days" 
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                @change="calculatePrice"
              >
                <option value="">Select deadline</option>
                <option value="1">1 day (Rush)</option>
                <option value="3">3 days</option>
                <option value="7">7 days</option>
                <option value="14">14 days</option>
                <option value="30">30 days</option>
              </select>
            </div>
          </div>

          <div v-if="priceResult" class="bg-white p-6 rounded-lg border-2 border-primary-200">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-gray-600">Estimated Price</p>
                <p class="text-3xl font-bold text-primary-600">
                  ${{ priceResult.total_price?.toFixed(2) || '0.00' }}
                </p>
              </div>
              <router-link to="/order" class="btn btn-primary">
                Place Order
              </router-link>
            </div>
          </div>
        </div>

        <!-- Pricing Table -->
        <div class="max-w-6xl mx-auto">
          <h2 class="text-3xl font-bold text-center mb-8">Standard Pricing</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div 
              v-for="tier in pricingTiers" 
              :key="tier.name"
              class="bg-white border-2 rounded-lg p-8 hover:shadow-lg transition"
              :class="tier.featured ? 'border-primary-500' : 'border-gray-200'"
            >
              <div v-if="tier.featured" class="text-center mb-4">
                <span class="bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </span>
              </div>
              <h3 class="text-2xl font-bold mb-4">{{ tier.name }}</h3>
              <p class="text-4xl font-bold mb-2">{{ tier.price }}</p>
              <p class="text-gray-600 mb-6">{{ tier.description }}</p>
              <ul class="space-y-3 mb-8">
                <li v-for="feature in tier.features" :key="feature" class="flex items-start">
                  <span class="text-green-500 mr-2">✓</span>
                  <span>{{ feature }}</span>
                </li>
              </ul>
              <router-link 
                to="/order" 
                class="btn w-full"
                :class="tier.featured ? 'btn-primary' : 'btn-outline'"
              >
                Get Started
              </router-link>
            </div>
          </div>
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

const calculator = ref({
  paper_type: '',
  academic_level: '',
  pages: 1,
  deadline_days: '',
})

const priceResult = ref(null)

const pricingTiers = ref([
  {
    name: 'Standard',
    price: 'From $10/page',
    description: 'Perfect for regular assignments',
    features: [
      'Professional writers',
      'On-time delivery',
      'Free revisions',
      '24/7 support'
    ],
    featured: false
  },
  {
    name: 'Premium',
    price: 'From $15/page',
    description: 'For important projects',
    features: [
      'Expert writers',
      'Priority support',
      'Unlimited revisions',
      'Quality guarantee'
    ],
    featured: true
  },
  {
    name: 'VIP',
    price: 'From $20/page',
    description: 'Top-tier service',
    features: [
      'PhD writers',
      'Dedicated support',
      'Rush delivery available',
      'Money-back guarantee'
    ],
    featured: false
  },
])

const calculatePrice = async () => {
  if (!calculator.value.paper_type || !calculator.value.academic_level || 
      !calculator.value.pages || !calculator.value.deadline_days) {
    priceResult.value = null
    return
  }

  try {
    // Calculate deadline date
    const deadline = new Date()
    deadline.setDate(deadline.getDate() + parseInt(calculator.value.deadline_days))
    
    const response = await servicesAPI.getQuote({
      paper_type: calculator.value.paper_type,
      academic_level: calculator.value.academic_level,
      pages: calculator.value.pages,
      deadline: deadline.toISOString(),
    })
    priceResult.value = response.data
  } catch (error) {
    console.error('Price calculation error:', error)
  }
}

onMounted(() => {
  websiteStore.detectWebsite()
})
</script>

