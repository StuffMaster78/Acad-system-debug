<template>
  <div class="privacy-security-page">
    <div class="max-w-6xl mx-auto p-6">
      <div class="page-header mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Privacy & Security</h1>
        <p class="text-gray-600">Learn about our privacy practices and security measures</p>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 mb-6">
        <nav class="flex space-x-8" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-red-800">{{ error }}</p>
        <button 
          @click="loadTabData" 
          class="mt-2 text-red-600 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>

      <!-- Content -->
      <div v-else class="space-y-6">
        <!-- Privacy Policy Tab -->
        <div v-if="activeTab === 'privacy'" class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ privacyData?.title }}</h2>
            <p class="text-sm text-gray-500">
              Last updated: {{ formatDate(privacyData?.last_updated) }}
            </p>
          </div>
          <div v-for="(section, index) in privacyData?.sections" :key="index" class="mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ section.title }}</h3>
            <ul class="list-disc list-inside space-y-2 text-gray-700">
              <li v-for="(item, itemIndex) in section.content" :key="itemIndex">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Security Practices Tab -->
        <div v-if="activeTab === 'security'" class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ securityData?.title }}</h2>
            <p class="text-sm text-gray-500">
              Last updated: {{ formatDate(securityData?.last_updated) }}
            </p>
          </div>
          <div v-for="(section, index) in securityData?.sections" :key="index" class="mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ section.title }}</h3>
            <ul class="list-disc list-inside space-y-2 text-gray-700">
              <li v-for="(item, itemIndex) in section.content" :key="itemIndex">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Data Rights Tab -->
        <div v-if="activeTab === 'rights'" class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ rightsData?.title }}</h2>
            <p class="text-sm text-gray-500">
              Last updated: {{ formatDate(rightsData?.last_updated) }}
            </p>
          </div>
          <div class="space-y-6">
            <div
              v-for="(right, index) in rightsData?.rights"
              :key="index"
              class="border-l-4 border-blue-500 pl-4 py-2"
            >
              <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ right.name }}</h3>
              <p class="text-gray-700 mb-2">{{ right.description }}</p>
              <p class="text-sm text-gray-600">
                <strong>How to exercise:</strong> {{ right.how_to_exercise }}
              </p>
            </div>
          </div>
        </div>

        <!-- Cookie Policy Tab -->
        <div v-if="activeTab === 'cookies'" class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ cookieData?.title }}</h2>
            <p class="text-sm text-gray-500">
              Last updated: {{ formatDate(cookieData?.last_updated) }}
            </p>
          </div>
          <div v-for="(section, index) in cookieData?.sections" :key="index" class="mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ section.title }}</h3>
            <ul class="list-disc list-inside space-y-2 text-gray-700">
              <li v-for="(item, itemIndex) in section.content" :key="itemIndex">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Terms of Service Tab -->
        <div v-if="activeTab === 'terms'" class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ termsData?.title }}</h2>
            <p class="text-sm text-gray-500">
              Last updated: {{ formatDate(termsData?.last_updated) }}
            </p>
          </div>
          <div v-for="(section, index) in termsData?.sections" :key="index" class="mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ section.title }}</h3>
            <ul class="list-disc list-inside space-y-2 text-gray-700">
              <li v-for="(item, itemIndex) in section.content" :key="itemIndex">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Print/Export Button -->
      <div class="mt-8 flex justify-end">
        <button
          @click="printPage"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Print This Page
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import privacySecurityAPI from '@/api/privacy-security'

const { error: showError } = useToast()

const loading = ref(false)
const error = ref(null)
const activeTab = ref('privacy')

const tabs = [
  { id: 'privacy', label: 'Privacy Policy' },
  { id: 'security', label: 'Security Practices' },
  { id: 'rights', label: 'Your Data Rights' },
  { id: 'cookies', label: 'Cookie Policy' },
  { id: 'terms', label: 'Terms of Service' },
]

const privacyData = ref(null)
const securityData = ref(null)
const rightsData = ref(null)
const cookieData = ref(null)
const termsData = ref(null)

const loadTabData = async () => {
  loading.value = true
  error.value = null
  
  try {
    let response
    switch (activeTab.value) {
      case 'privacy':
        if (!privacyData.value) {
          response = await privacySecurityAPI.getPrivacyPolicy()
          privacyData.value = response.data
        }
        break
      case 'security':
        if (!securityData.value) {
          response = await privacySecurityAPI.getSecurityPractices()
          securityData.value = response.data
        }
        break
      case 'rights':
        if (!rightsData.value) {
          response = await privacySecurityAPI.getDataRights()
          rightsData.value = response.data
        }
        break
      case 'cookies':
        if (!cookieData.value) {
          response = await privacySecurityAPI.getCookiePolicy()
          cookieData.value = response.data
        }
        break
      case 'terms':
        if (!termsData.value) {
          response = await privacySecurityAPI.getTermsOfService()
          termsData.value = response.data
        }
        break
    }
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load information'
    showError(error.value)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const printPage = () => {
  window.print()
}

watch(activeTab, () => {
  loadTabData()
})

onMounted(() => {
  loadTabData()
})
</script>

<style scoped>
.privacy-security-page {
  min-height: calc(100vh - 4rem);
}

@media print {
  .privacy-security-page {
    padding: 0;
  }
  
  .page-header,
  .border-b,
  button {
    display: none;
  }
}
</style>

