<template>
  <div class="privacy-security-page bg-gray-50 dark:bg-gray-900 min-h-screen">
    <div class="max-w-6xl mx-auto p-6">
      <div class="page-header mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Privacy & Security</h1>
            <p class="text-gray-600 dark:text-gray-400">Learn about our privacy practices and security measures</p>
          </div>
          <button
            v-if="isAdmin"
            @click="editingMode = !editingMode"
            class="px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200 flex items-center gap-2"
            :class="editingMode 
              ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600' 
              : 'bg-primary-600 text-white hover:bg-primary-700'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="editingMode ? 'M6 18L18 6M6 6l12 12' : 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z'" />
            </svg>
            {{ editingMode ? 'Cancel Editing' : 'Edit Content' }}
          </button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav class="flex space-x-8 overflow-x-auto" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-3 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap',
              activeTab === tab.id
                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
        <p class="text-red-800 dark:text-red-300">{{ error }}</p>
        <button 
          @click="loadTabData" 
          class="mt-2 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 underline"
        >
          Try again
        </button>
      </div>

      <!-- Content -->
      <div v-else class="space-y-6">
        <!-- Privacy Policy Tab -->
        <div v-if="activeTab === 'privacy'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm">
          <div v-if="!privacyData && !editingMode" class="p-6 text-center py-12 text-gray-500 dark:text-gray-400">
            <p>No privacy policy information available.</p>
          </div>
          
          <!-- Edit Mode -->
          <div v-else-if="editingMode && isAdmin" class="p-6">
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Title</label>
              <input
                v-model="editForm.title"
                type="text"
                class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                placeholder="Privacy Policy"
              />
            </div>
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Content</label>
              <RichTextEditor
                v-model="editForm.content"
                :height="'400px'"
                toolbar="full"
                placeholder="Enter privacy policy content here..."
              />
            </div>
            <div class="flex gap-3">
              <button
                @click="saveContent('privacy')"
                :disabled="saving"
                class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
              <button
                @click="cancelEdit"
                class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          </div>

          <!-- View Mode -->
          <div v-else class="p-6">
            <div class="mb-4">
              <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">{{ privacyData?.title || 'Privacy Policy' }}</h2>
              <p class="text-sm text-gray-500 dark:text-gray-400" v-if="privacyData?.last_updated">
                Last updated: {{ formatDate(privacyData?.last_updated) }}
              </p>
            </div>
            <div v-if="privacyData?.content" class="prose prose-sm max-w-none dark:prose-invert">
              <SafeHtml :content="privacyData.content" />
            </div>
            <div v-else-if="privacyData?.sections && privacyData.sections.length > 0">
              <div v-for="(section, index) in privacyData.sections" :key="index" class="mb-6">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">{{ section.title }}</h3>
                <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
                  <li v-for="(item, itemIndex) in section.content" :key="itemIndex">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>
            <div v-else class="text-gray-500 dark:text-gray-400">
              <p>Content will be available soon.</p>
            </div>
          </div>
        </div>

        <!-- Security Practices Tab -->
        <div v-if="activeTab === 'security'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 shadow-sm">
          <div v-if="!securityData" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <p>No security practices information available.</p>
          </div>
          <div v-else>
            <div class="mb-4">
              <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">{{ securityData?.title || 'Security Practices' }}</h2>
              <p class="text-sm text-gray-500 dark:text-gray-400" v-if="securityData?.last_updated">
                Last updated: {{ formatDate(securityData?.last_updated) }}
              </p>
            </div>
            <div v-if="securityData?.sections && securityData.sections.length > 0">
              <div v-for="(section, index) in securityData.sections" :key="index" class="mb-6">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">{{ section.title }}</h3>
                <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
                  <li v-for="(item, itemIndex) in section.content" :key="itemIndex">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>
            <div v-else class="text-gray-500 dark:text-gray-400">
              <p>Content will be available soon.</p>
            </div>
          </div>
        </div>

        <!-- Data Rights Tab -->
        <div v-if="activeTab === 'rights'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 shadow-sm">
          <div v-if="!rightsData" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <p>No data rights information available.</p>
          </div>
          <div v-else>
            <div class="mb-4">
              <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">{{ rightsData?.title || 'Your Data Rights' }}</h2>
              <p class="text-sm text-gray-500 dark:text-gray-400" v-if="rightsData?.last_updated">
                Last updated: {{ formatDate(rightsData?.last_updated) }}
              </p>
            </div>
            <div v-if="rightsData?.rights && rightsData.rights.length > 0" class="space-y-6">
              <div
                v-for="(right, index) in rightsData.rights"
                :key="index"
                class="border-l-4 border-primary-500 dark:border-primary-400 pl-4 py-2"
              >
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">{{ right.name }}</h3>
                <p class="text-gray-700 dark:text-gray-300 mb-2">{{ right.description }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  <strong>How to exercise:</strong> {{ right.how_to_exercise }}
                </p>
              </div>
            </div>
            <div v-else class="text-gray-500 dark:text-gray-400">
              <p>Content will be available soon.</p>
            </div>
          </div>
        </div>

        <!-- Cookie Policy Tab -->
        <div v-if="activeTab === 'cookies'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 shadow-sm">
          <div v-if="!cookieData" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <p>No cookie policy information available.</p>
          </div>
          <div v-else>
            <div class="mb-4">
              <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">{{ cookieData?.title || 'Cookie Policy' }}</h2>
              <p class="text-sm text-gray-500 dark:text-gray-400" v-if="cookieData?.last_updated">
                Last updated: {{ formatDate(cookieData?.last_updated) }}
              </p>
            </div>
            <div v-if="cookieData?.sections && cookieData.sections.length > 0">
              <div v-for="(section, index) in cookieData.sections" :key="index" class="mb-6">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">{{ section.title }}</h3>
                <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
                  <li v-for="(item, itemIndex) in section.content" :key="itemIndex">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>
            <div v-else class="text-gray-500 dark:text-gray-400">
              <p>Content will be available soon.</p>
            </div>
          </div>
        </div>

        <!-- Terms of Service Tab -->
        <div v-if="activeTab === 'terms'" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 shadow-sm">
          <div v-if="!termsData" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <p>No terms of service information available.</p>
          </div>
          <div v-else>
            <div class="mb-4">
              <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">{{ termsData?.title || 'Terms of Service' }}</h2>
              <p class="text-sm text-gray-500 dark:text-gray-400" v-if="termsData?.last_updated">
                Last updated: {{ formatDate(termsData?.last_updated) }}
              </p>
            </div>
            <div v-if="termsData?.sections && termsData.sections.length > 0">
              <div v-for="(section, index) in termsData.sections" :key="index" class="mb-6">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3">{{ section.title }}</h3>
                <ul class="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300">
                  <li v-for="(item, itemIndex) in section.content" :key="itemIndex">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>
            <div v-else class="text-gray-500 dark:text-gray-400">
              <p>Content will be available soon.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Print/Export Button -->
      <div class="mt-8 flex justify-end">
        <button
          @click="printPage"
          class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          Print This Page
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import privacySecurityAPI from '@/api/privacy-security'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import SafeHtml from '@/components/common/SafeHtml.vue'

const { success: showSuccess, error: showError } = useToast()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.isAdmin || authStore.isSuperAdmin)
const editingMode = ref(false)
const saving = ref(false)

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
    // Handle 404 errors gracefully - API endpoint might not exist yet
    if (err.response?.status === 404) {
      error.value = null // Don't show error for missing endpoints
      // Set empty data structure to show "Content will be available soon" message
      switch (activeTab.value) {
        case 'privacy':
          if (!privacyData.value) privacyData.value = { title: 'Privacy Policy' }
          break
        case 'security':
          if (!securityData.value) securityData.value = { title: 'Security Practices' }
          break
        case 'rights':
          if (!rightsData.value) rightsData.value = { title: 'Your Data Rights' }
          break
        case 'cookies':
          if (!cookieData.value) cookieData.value = { title: 'Cookie Policy' }
          break
        case 'terms':
          if (!termsData.value) termsData.value = { title: 'Terms of Service' }
          break
      }
    } else {
      error.value = err.response?.data?.detail || err.message || 'Failed to load information'
      showError(error.value)
    }
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

