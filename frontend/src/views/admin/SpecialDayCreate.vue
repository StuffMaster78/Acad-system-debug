<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Breadcrumb Navigation -->
      <nav class="mb-6" aria-label="Breadcrumb">
        <ol class="flex items-center space-x-2 text-sm">
          <li>
            <router-link
              to="/admin/holidays"
              class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
            >
              Holidays
            </router-link>
          </li>
          <li>
            <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </li>
          <li class="text-gray-900 dark:text-white font-medium">
            {{ editingSpecialDay ? 'Edit' : 'Create' }}
          </li>
        </ol>
      </nav>

      <!-- Header Section -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <div>
              <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
                {{ editingSpecialDay ? 'Edit Special Day' : 'Create Special Day' }}
              </h1>
              <p class="text-base text-gray-600 dark:text-gray-400">
                {{ editingSpecialDay ? 'Update special day details and settings' : 'Add a new special day, holiday, or marketing campaign' }}
              </p>
            </div>
          </div>
          <button
            @click="goBack"
            class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all shadow-sm hover:shadow-md"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to List
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-12">
        <div class="flex flex-col items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
          <p class="text-gray-600 dark:text-gray-400">Loading special day details...</p>
        </div>
      </div>

      <!-- Form Card -->
      <div v-else class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <!-- Card Header -->
        <div class="bg-gradient-to-r from-primary-50 to-primary-100 dark:from-gray-700 dark:to-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Special Day Information</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400">Fill in the details below to create or update a special day</p>
            </div>
          </div>
        </div>

        <!-- Form Content -->
        <div class="p-6 md:p-8">
          <SpecialDayForm
            :special-day="editingSpecialDay"
            @save="handleSave"
            @cancel="goBack"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SpecialDayForm from '@/components/holidays/SpecialDayForm.vue'
import { holidaysAPI } from '@/api'

const route = useRoute()
const router = useRouter()

const editingSpecialDay = ref(null)
const loading = ref(false)

onMounted(async () => {
  // Check if we're editing an existing special day
  const specialDayId = route.params.id
  if (specialDayId) {
    loading.value = true
    try {
      const response = await holidaysAPI.specialDays.get(specialDayId)
      editingSpecialDay.value = response.data
    } catch (error) {
      console.error('Failed to load special day:', error)
      router.push('/admin/holidays')
    } finally {
      loading.value = false
    }
  }
})

const handleSave = async (data) => {
  try {
    if (editingSpecialDay.value) {
      await holidaysAPI.specialDays.update(editingSpecialDay.value.id, data)
    } else {
      await holidaysAPI.specialDays.create(data)
    }
    // Navigate back to holidays page
    router.push('/admin/holidays')
  } catch (error) {
    console.error('Failed to save special day:', error)
    // Error handling will be done by the form component
    throw error
  }
}

const goBack = () => {
  router.push('/admin/holidays')
}
</script>

