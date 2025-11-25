<template>
  <div class="space-y-4">
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-2 text-sm text-gray-600">Loading progress history...</p>
    </div>

    <div v-else-if="progressReports.length === 0" class="text-center py-8 text-gray-500">
      <p>No progress reports yet.</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="report in progressReports"
        :key="report.id"
        class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        :class="{
          'bg-red-50 border-red-200': report.is_withdrawn,
          'bg-yellow-50 border-yellow-200': report.contains_screened_words && !report.is_withdrawn
        }"
      >
        <div class="flex items-start justify-between mb-2">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <div class="flex items-center gap-2">
                <div class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-blue-500 rounded-full"
                    :style="{ width: `${report.progress_percentage}%` }"
                  ></div>
                </div>
                <span class="text-sm font-semibold text-gray-900">
                  {{ report.progress_percentage }}%
                </span>
              </div>
              <span
                v-if="report.is_withdrawn"
                class="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800"
              >
                Withdrawn
              </span>
              <span
                v-else-if="report.contains_screened_words"
                class="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800"
              >
                Contains Screened Words
              </span>
            </div>
            
            <p v-if="report.notes && !report.is_withdrawn" class="text-sm text-gray-700 mt-2">
              {{ report.notes }}
            </p>
            <p v-else-if="report.is_withdrawn" class="text-sm text-red-600 italic mt-2">
              This report was withdrawn: {{ report.withdrawal_reason || 'Policy violation detected' }}
            </p>
            
            <p class="text-xs text-gray-500 mt-2">
              {{ formatDateTime(report.timestamp) }}
            </p>
          </div>
          
          <div v-if="canWithdraw && !report.is_withdrawn" class="ml-4">
            <button
              @click="withdrawReport(report.id)"
              :disabled="withdrawing"
              class="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors disabled:opacity-50"
            >
              {{ withdrawing ? 'Withdrawing...' : 'Withdraw' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import progressAPI from '@/api/progress'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

const authStore = useAuthStore()
const progressReports = ref([])
const loading = ref(false)
const withdrawing = ref(false)

const canWithdraw = computed(() => {
  return authStore.isAdmin || authStore.isSuperAdmin
})

const loadProgressHistory = async () => {
  try {
    loading.value = true
    const response = await progressAPI.getOrderProgress(props.orderId)
    progressReports.value = response.data.reports || []
  } catch (error) {
    console.error('Failed to load progress history:', error)
    progressReports.value = []
  } finally {
    loading.value = false
  }
}

const withdrawReport = async (reportId) => {
  if (!confirm('Are you sure you want to withdraw this progress report?')) {
    return
  }

  try {
    withdrawing.value = true
    await progressAPI.withdraw(reportId, 'Policy violation detected')
    await loadProgressHistory()
    emit('updated')
  } catch (error) {
    console.error('Failed to withdraw report:', error)
    alert('Failed to withdraw report: ' + (error.response?.data?.error || error.message))
  } finally {
    withdrawing.value = false
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadProgressHistory()
})

defineExpose({
  refresh: loadProgressHistory
})
</script>

