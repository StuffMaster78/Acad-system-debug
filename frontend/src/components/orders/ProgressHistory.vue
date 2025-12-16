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

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import progressAPI from '@/api/progress'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

const authStore = useAuthStore()
const { showToast } = useToast()
const confirm = useConfirmDialog()
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
    // Silently fail - don't show error toast for loading failures
    progressReports.value = []
  } finally {
    loading.value = false
  }
}

const withdrawReport = async (reportId) => {
  const report = progressReports.value.find(r => r.id === reportId)
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to withdraw this progress report?',
    'Withdraw Progress Report',
    {
      details: 'This action will mark the progress report as withdrawn. The reason will be recorded as "Policy violation detected". This action cannot be undone.',
      confirmText: 'Withdraw Report',
      cancelText: 'Cancel',
      icon: '⚠️'
    }
  )

  if (!confirmed) return

  try {
    withdrawing.value = true
    await progressAPI.withdraw(reportId, 'Policy violation detected')
    showToast('Progress report withdrawn successfully', 'success')
    await loadProgressHistory()
    emit('updated')
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message || 'Failed to withdraw report'
    showToast(errorMsg, 'error')
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

