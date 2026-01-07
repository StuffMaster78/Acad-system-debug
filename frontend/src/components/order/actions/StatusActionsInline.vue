<template>
  <div class="space-y-4">
    <!-- Filter to only show available and valid actions -->
    <div v-if="filteredActions.length === 0" class="text-center py-8 text-gray-500">
      <p>No status actions available for this order</p>
      <p v-if="order?.status" class="text-xs mt-2">Current status: {{ order.status }}</p>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <button
        v-for="action in filteredActions"
        :key="action.action"
        @click="executeAction(action)"
        :disabled="processing || !action.can_transition"
        :class="[
          'p-4 border-2 rounded-lg text-left transition-all',
          getActionClass(action.action),
          (processing || !action.can_transition) ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md cursor-pointer',
          action.restricted ? 'border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20' : ''
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h4 class="font-semibold">{{ action.label }}</h4>
            <p v-if="action.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {{ action.description }}
            </p>
            <p v-if="action.reason" class="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
              ⚠️ {{ action.reason }}
            </p>
            <p v-if="action.restricted" class="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
              ⚠️ Restricted action
            </p>
          </div>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </button>
    </div>

    <!-- Action Form (shown when action is selected) -->
    <div v-if="selectedAction" class="mt-6 pt-6 border-t">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Reason / Notes (Optional)
          </label>
          <textarea
            v-model="actionReason"
            rows="3"
            placeholder="Enter reason for this action..."
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          ></textarea>
        </div>
        <div class="flex gap-3">
          <button
            @click="cancelAction"
            class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            Cancel
          </button>
          <button
            @click="confirmAction"
            :disabled="processing"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {{ processing ? 'Processing...' : 'Confirm Action' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ordersAPI } from '@/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  order: {
    type: Object,
    required: true
  },
  availableActions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['success', 'error'])

const { success: showSuccessToast, error: showErrorToast } = useToast()

const selectedAction = ref(null)
const actionReason = ref('')
const processing = ref(false)

// Filter actions to only show those that are available and can transition
const filteredActions = computed(() => {
  if (!props.availableActions || props.availableActions.length === 0) {
    return []
  }
  
  return props.availableActions.filter(action => {
    // Only show actions that are available and can transition
    if (!action.available || !action.can_transition) {
      return false
    }
    
    // Exclude assign/reassign/edit actions (handled in separate sections)
    if (['assign_order', 'reassign_order', 'edit_order', 'update_order'].includes(action.action)) {
      return false
    }
    
    return true
  })
})

const getActionClass = (action) => {
  const critical = ['cancel_order', 'refund_order', 'archive_order']
  if (critical.includes(action)) {
    return 'border-red-300 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'
  }
  return 'border-blue-300 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
}

const executeAction = (action) => {
  selectedAction.value = action
}

const confirmAction = async () => {
  if (!selectedAction.value) return
  
  processing.value = true
  try {
    await ordersAPI.executeAction(props.order.id, {
      action: selectedAction.value.action,
      reason: actionReason.value
    })
    showSuccessToast(`Action "${selectedAction.value.label}" executed successfully!`)
    emit('success', { action: selectedAction.value.action })
    selectedAction.value = null
    actionReason.value = ''
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to execute action'
    showErrorToast(errorMsg)
    emit('error', error)
  } finally {
    processing.value = false
  }
}

const cancelAction = () => {
  selectedAction.value = null
  actionReason.value = ''
}
</script>

