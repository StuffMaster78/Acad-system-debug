<template>
  <Modal
    :visible="visible"
    :title="modalTitle"
    :size="actionForm.action === 'assign_order' || actionForm.action === 'reassign_order' ? 'xl' : 'md'"
    :scrollable="true"
    :max-height="actionForm.action === 'assign_order' || actionForm.action === 'reassign_order' ? '75vh' : '60vh'"
    @update:visible="$emit('update:visible', $event)"
  >
    <div class="space-y-4">
      <!-- Order Info -->
      <div v-if="order" class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-semibold text-gray-900">Order {{ formatOrderId(order.id) }}</h3>
            <p class="text-sm text-gray-600 mt-1">
              Current Status: <span class="font-medium capitalize">{{ order.status?.replace('_', ' ') }}</span>
            </p>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-600">Client</p>
            <p class="font-medium">{{ order.client_name || order.client?.email || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <!-- Action Selection (if not pre-selected) -->
      <div v-if="!selectedAction && availableActions.length > 0">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Select Action
        </label>
        <select
          v-model="actionForm.action"
          class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          @change="onActionChange"
        >
          <option value="">-- Select an action --</option>
          <option
            v-for="action in availableActions"
            :key="action.action"
            :value="action.action"
          >
            {{ action.label }}
          </option>
        </select>
      </div>

      <!-- Action Info (if pre-selected) -->
      <div v-else-if="selectedAction" class="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="text-sm font-medium text-blue-900">Action: {{ actionLabel }}</p>
            <p v-if="targetStatus" class="text-xs text-blue-700 mt-1">
              Will change status to: <span class="font-medium capitalize">{{ targetStatus.replace('_', ' ') }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Warning for Critical Actions -->
      <div
        v-if="isCriticalAction"
        class="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 dark:border-yellow-600 p-4 rounded"
      >
        <div class="flex">
          <div class="shrink-0">
            <svg class="h-5 w-5 text-yellow-400 dark:text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <p class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
              <strong>Warning:</strong> This action {{ criticalActionMessage }}.
            </p>
            <p v-if="order" class="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
              You are about to perform this action on Order #{{ order.id }} "{{ order.topic || 'Untitled' }}". Please confirm this is the intended action.
            </p>
          </div>
        </div>
      </div>

      <!-- Payment Reference Fields (for mark_paid action) -->
      <div v-if="actionForm.action === 'mark_paid'">
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
          <div class="flex items-center gap-2 mb-3">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <p class="text-sm font-medium text-blue-900 dark:text-blue-200">External Payment Information</p>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Payment Reference Number
                <span class="text-gray-500 text-xs font-normal">(Optional)</span>
              </label>
              <input
                v-model="actionForm.reference_id"
                type="text"
                placeholder="e.g., MPESA code, PayPal transaction ID, bank reference..."
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
                :class="{ 'border-red-300': errors.reference_id }"
              />
              <p v-if="errors.reference_id" class="mt-1 text-sm text-red-600">{{ errors.reference_id }}</p>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Enter the external payment reference if payment was made outside the system (MPESA, PayPal, bank transfer, etc.)
              </p>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Payment Method
                <span class="text-gray-500 text-xs font-normal">(Optional)</span>
              </label>
              <select
                v-model="actionForm.payment_method"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
                :class="{ 'border-red-300': errors.payment_method }"
              >
                <option value="">-- Select payment method --</option>
                <option value="mpesa">MPESA</option>
                <option value="paypal">PayPal</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="stripe">Stripe</option>
                <option value="manual">Manual/Cash</option>
                <option value="other">Other</option>
              </select>
              <p v-if="errors.payment_method" class="mt-1 text-sm text-red-600">{{ errors.payment_method }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Reason/Notes Field -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Reason / Notes
          <span class="text-gray-500 text-xs font-normal">(Optional, for audit trail)</span>
        </label>
        <textarea
          v-model="actionForm.reason"
          rows="3"
          placeholder="Enter reason or notes for this action..."
          class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          :class="{ 'border-red-300': errors.reason }"
        ></textarea>
        <p v-if="errors.reason" class="mt-1 text-sm text-red-600">{{ errors.reason }}</p>
      </div>

      <!-- Additional Fields (e.g., writer_id for assign) -->
      <div v-if="actionForm.action === 'assign_order' || actionForm.action === 'reassign_order'">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Select Writer
        </label>
        <select
          v-model="actionForm.writer_id"
          @change="onWriterSelected"
          class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          :class="{ 'border-red-300': errors.writer_id }"
        >
          <option value="">-- Select a writer --</option>
          <option
            v-for="writer in availableWriters"
            :key="writer.id"
            :value="writer.id"
          >
            {{ writer.writer_id || `WRTR${writer.id.toString().padStart(6, '0')}` }} - {{ formatWriterName(writer) }} 
            (Rating: {{ writer.profile?.rating || 0 }}, Active: {{ writer.workload?.active_orders_count || 0 }})
          </option>
        </select>
        <p v-if="errors.writer_id" class="mt-1 text-sm text-red-600">{{ errors.writer_id }}</p>

        <!-- Writer Details Panel -->
        <div v-if="selectedWriterDetails" class="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-gray-900 dark:text-white truncate">{{ selectedWriterDetails.username || selectedWriterDetails.email || 'N/A' }}</h4>
              <p class="text-sm text-gray-600 dark:text-gray-400 truncate">{{ selectedWriterDetails.email || 'N/A' }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                ID: {{ selectedWriterDetails.writer_id || `WRTR${selectedWriterDetails.id?.toString().padStart(6, '0') || 'N/A'}` }}
              </p>
            </div>
            <div class="text-right ml-4 shrink-0">
              <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{{ selectedWriterDetails.profile?.rating || selectedWriterDetails.rating || 0 }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">Rating</div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-3">
            <div>
              <div class="text-sm font-medium text-gray-700 dark:text-gray-300">Active Orders</div>
              <div class="text-lg font-semibold text-gray-900 dark:text-white">{{ selectedWriterDetails.workload?.active_orders_count || selectedWriterDetails.active_orders_count || 0 }}</div>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-700 dark:text-gray-300">Completed</div>
              <div class="text-lg font-semibold text-gray-900 dark:text-white">{{ selectedWriterDetails.stats?.total_completed || selectedWriterDetails.completed_orders_count || 0 }}</div>
            </div>
          </div>

          <!-- Current Orders in Progress -->
          <div v-if="selectedWriterDetails.workload?.active_orders && selectedWriterDetails.workload.active_orders.length > 0" class="mt-3">
            <div class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Current Orders in Progress:</div>
            <div class="space-y-2 max-h-40 overflow-y-auto pr-1">
              <div
                v-for="activeOrder in selectedWriterDetails.workload.active_orders"
                :key="activeOrder.id"
                class="bg-white dark:bg-gray-800 rounded p-2 text-xs border border-gray-200 dark:border-gray-700"
              >
                <div class="flex items-center justify-between">
                  <span class="font-medium text-gray-900 dark:text-white">{{ formatOrderId(activeOrder.id) }}</span>
                  <span class="text-gray-500 dark:text-gray-400 capitalize">{{ activeOrder.status?.replace('_', ' ') || 'N/A' }}</span>
                </div>
                <div class="text-gray-600 dark:text-gray-400 mt-1 truncate">{{ activeOrder.topic || 'Untitled' }}</div>
                <div class="flex items-center gap-2 mt-1 text-gray-500 dark:text-gray-500">
                  <span>{{ activeOrder.pages || 0 }} pages</span>
                  <span>•</span>
                  <span v-if="activeOrder.deadline">{{ formatDate(activeOrder.deadline) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-sm text-gray-500 dark:text-gray-400 italic">No active orders</div>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
        <div v-if="errorDetails" class="mt-2 text-xs text-red-600">
          <p v-if="errorDetails.available_actions">
            Available actions: {{ errorDetails.available_actions.join(', ') }}
          </p>
        </div>
      </div>
      
      <!-- Processing Indicator -->
      <div v-if="loading" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div class="flex items-center gap-3">
          <svg class="animate-spin h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 0 4 12zm8 0a8 8 0 100-16v8z"></path>
          </svg>
          <div>
            <p class="text-sm font-medium text-blue-900 dark:text-blue-200">Processing action...</p>
            <p class="text-xs text-blue-700 dark:text-blue-300 mt-1">Please wait while we execute this action on the order.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirmShow"
      :title="confirmTitle"
      :message="confirmMessage"
      :details="confirmDetails"
      :variant="confirmVariant"
      :icon="confirmIcon"
      :confirm-text="confirmConfirmText"
      :cancel-text="confirmCancelText"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />

    <template #footer>
      <button
        @click="$emit('update:visible', false)"
        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        :disabled="loading"
      >
        Cancel
      </button>
      <button
        @click="handleSubmit"
        :disabled="loading || !canSubmit"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="loading" class="flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 0 4 12zm8 0a8 8 0 100-16v8z"></path>
          </svg>
          Processing...
        </span>
        <span v-else>{{ submitButtonText }}</span>
      </button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed, watch, unref } from 'vue'
import Modal from '@/components/common/Modal.vue'
import { ordersAPI } from '@/api'
import writerAssignmentAPI from '@/api/writer-assignment'
import { getErrorMessage } from '@/utils/errorHandler'
import { formatOrderId, formatUserId } from '@/utils/idFormatter'
import { formatWriterName } from '@/utils/formatDisplay'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  order: {
    type: Object,
    default: null
  },
  selectedAction: {
    type: String,
    default: null
  },
  availableActions: {
    type: Array,
    default: () => []
  },
  availableWriters: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'success', 'error'])

const loading = ref(false)
const error = ref(null)
const errorDetails = ref(null)
const loadingWriters = ref(false)
const selectedWriterDetails = ref(null)
const confirm = useConfirmDialog()

// Create local refs for v-model binding (Vue 3 v-model requires refs, not computed)
const confirmShow = ref(false)

// Computed properties to unwrap refs for ConfirmationDialog
const confirmTitle = computed(() => confirm.title.value)
const confirmMessage = computed(() => confirm.message.value)
const confirmDetails = computed(() => confirm.details.value)
const confirmVariant = computed(() => confirm.variant.value)
const confirmIcon = computed(() => confirm.icon.value)
const confirmConfirmText = computed(() => confirm.confirmText.value)
const confirmCancelText = computed(() => confirm.cancelText.value)

// Sync local refs with composable refs
watch(() => confirm.show.value, (newVal) => {
  confirmShow.value = newVal
}, { immediate: true })

watch(confirmShow, (newVal) => {
  if (confirm.show.value !== newVal) {
    confirm.show.value = newVal
  }
})

const actionForm = ref({
  action: props.selectedAction || '',
  reason: '',
  writer_id: null,
  reference_id: '',
  payment_method: ''
})

const errors = ref({})

// Computed properties
const modalTitle = computed(() => {
  if (props.selectedAction) {
    return `Confirm ${actionLabel.value}`
  }
  return 'Order Action'
})

const actionLabel = computed(() => {
  const action = props.availableActions.find(a => a.action === actionForm.value.action)
  return action?.label || actionForm.value.action?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Action'
})

const targetStatus = computed(() => {
  const action = props.availableActions.find(a => a.action === actionForm.value.action)
  return action?.target_status || null
})

const isCriticalAction = computed(() => {
  const criticalActions = ['cancel_order', 'refund_order', 'archive_order', 'close_order']
  return criticalActions.includes(actionForm.value.action)
})

const criticalActionMessage = computed(() => {
  const messages = {
    'cancel_order': 'cannot be undone',
    'refund_order': 'will process a refund',
    'archive_order': 'will archive this order',
    'close_order': 'will permanently close this order'
  }
  return messages[actionForm.value.action] || 'has significant impact'
})

const canSubmit = computed(() => {
  if (!actionForm.value.action) return false
  
  // Require writer_id for assign/reassign actions
  if ((actionForm.value.action === 'assign_order' || actionForm.value.action === 'reassign_order') && !actionForm.value.writer_id) {
    return false
  }
  
  return true
})

const submitButtonText = computed(() => {
  if (isCriticalAction.value) {
    return `Confirm ${actionLabel.value}`
  }
  return `Execute ${actionLabel.value}`
})

// Watch for selectedAction prop changes
watch(() => props.selectedAction, (newVal) => {
  if (newVal) {
    actionForm.value.action = newVal
  }
})

watch(() => props.visible, (newVal) => {
  if (!newVal) {
    // Reset form when modal closes
    actionForm.value = {
      action: props.selectedAction || '',
      reason: '',
      writer_id: null,
      reference_id: '',
      payment_method: ''
    }
    error.value = null
    errorDetails.value = null
    errors.value = {}
  }
})

const onActionChange = () => {
  error.value = null
  errorDetails.value = null
  errors.value = {}
  
  // Reset writer_id when action changes
  if (actionForm.value.action !== 'assign_order' && actionForm.value.action !== 'reassign_order') {
    actionForm.value.writer_id = null
    selectedWriterDetails.value = null
  }
  
  // Reset payment fields when action changes away from mark_paid
  if (actionForm.value.action !== 'mark_paid') {
    actionForm.value.reference_id = ''
    actionForm.value.payment_method = ''
  }
}

// Load available writers with workload
const loadAvailableWriters = async () => {
  if (!props.order) return
  
  loadingWriters.value = true
  try {
    const response = await writerAssignmentAPI.getAvailableWriters(props.order.id)
    // The parent component should handle updating availableWriters
    // But we can also use the response here to show details
    if (response.data && response.data.writers && actionForm.value.writer_id) {
      selectedWriterDetails.value = response.data.writers.find(
        w => w.id === actionForm.value.writer_id
      )
    }
  } catch (error) {
    console.error('Failed to load writer details:', error)
    // Don't show error to user, just log it
  } finally {
    loadingWriters.value = false
  }
}

// Handle writer selection change
const onWriterSelected = async () => {
  const writerId = actionForm.value.writer_id
  if (!writerId) {
    selectedWriterDetails.value = null
    return
  }
  
  // Find writer in availableWriters or fetch details
  const writer = props.availableWriters.find(w => w.id === writerId)
  if (writer && writer.workload) {
    selectedWriterDetails.value = writer
  } else {
    // Try to fetch from the API
    try {
      const response = await writerAssignmentAPI.getAvailableWriters(props.order?.id)
      if (response.data && response.data.writers) {
        selectedWriterDetails.value = response.data.writers.find(w => w.id === writerId)
      }
    } catch (error) {
      console.error('Failed to load writer details:', error)
    }
  }
}

// Format date helper
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const validateForm = () => {
  errors.value = {}
  
  if (!actionForm.value.action) {
    errors.value.action = 'Please select an action'
    return false
  }
  
  if ((actionForm.value.action === 'assign_order' || actionForm.value.action === 'reassign_order') && !actionForm.value.writer_id) {
    errors.value.writer_id = 'Please select a writer'
    return false
  }
  
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  // Build confirmation message based on action type
  const orderId = props.order?.id || 'this order'
  const orderTopic = props.order?.topic || 'Untitled'
  const actionName = actionLabel.value
  
  // Build details message
  let detailsMessage = `You are about to ${actionName.toLowerCase()} Order #${orderId} "${orderTopic}".`
  
  if (targetStatus.value) {
    detailsMessage += ` The order status will change to "${targetStatus.value.replace('_', ' ')}".`
  }
  
  if (actionForm.value.action === 'assign_order' || actionForm.value.action === 'reassign_order') {
    const writer = props.availableWriters.find(w => w.id === actionForm.value.writer_id)
    const writerName = writer ? formatWriterName(writer) : 'selected writer'
    if (actionForm.value.action === 'reassign_order') {
      const currentWriter = props.order?.assigned_writer?.username || props.order?.writer_username || 'current writer'
      detailsMessage += `\n\nThis will reassign the order from ${currentWriter} to ${writerName}. The current writer will be notified, and the new writer will receive the assignment.`
    } else {
      detailsMessage += `\n\nThe order will be assigned to ${writerName}, who will be notified and can start working on it.`
    }
  }
  
  if (actionForm.value.reason) {
    detailsMessage += `\n\nReason: ${actionForm.value.reason}`
  }
  
  // Show confirmation dialog
  let confirmed = false
  if (isCriticalAction.value) {
    confirmed = await confirm.showDestructive(
      `Are you sure you want to ${actionName.toLowerCase()} Order #${orderId}?`,
      `Confirm ${actionName}`,
      {
        details: detailsMessage + `\n\n⚠️ This action ${criticalActionMessage.value}.`,
        confirmText: `Confirm ${actionName}`,
        cancelText: 'Cancel',
        icon: '⚠️'
      }
    )
  } else {
    confirmed = await confirm.showDialog(
      `Are you sure you want to ${actionName.toLowerCase()} Order #${orderId}?`,
      `Confirm ${actionName}`,
      {
        details: detailsMessage,
        variant: 'default',
        confirmText: `Execute ${actionName}`,
        cancelText: 'Cancel',
        icon: '❓'
      }
    )
  }
  
  if (!confirmed) return
  
  loading.value = true
  error.value = null
  errorDetails.value = null
  
  try {
    // Actions that require executeAction (complex actions with additional logic)
    const complexActions = ['assign_order', 'reassign_order', 'refund_order', 'extend_deadline', 'mark_critical']
    const isComplexAction = complexActions.includes(actionForm.value.action)
    
    let response
    
    // Use transition endpoint for simple status transitions
    if (!isComplexAction && targetStatus.value) {
      // Simple status transition - use unified transition endpoint
      response = await ordersAPI.transition(
        props.order.id,
        targetStatus.value,
        actionForm.value.reason || '',
        {
          action: actionForm.value.action
        }
      )
      
      // Format response to match executeAction format for consistency
      const orderTopic = props.order?.topic || 'Untitled'
      const orderId = props.order?.id
      const actionName = actionLabel.value
      const statusChange = response.data.old_status && response.data.new_status
        ? `Status changed from "${response.data.old_status.replace('_', ' ')}" to "${response.data.new_status.replace('_', ' ')}"`
        : response.data.new_status
          ? `Status changed to "${response.data.new_status.replace('_', ' ')}"`
          : ''
      
      const successMessage = response.data.message || 
        `${actionName} completed successfully for Order #${orderId} "${orderTopic}". ${statusChange ? statusChange + '.' : ''}`
      
      emit('success', {
        order: response.data.order,
        message: successMessage,
        old_status: response.data.old_status,
        new_status: response.data.new_status,
        action: actionForm.value.action
      })
      emit('update:visible', false)
    } else {
      // Complex action - use executeAction endpoint
      const payload = {
        reason: actionForm.value.reason || undefined
      }
      
      // Add writer_id if needed
      if (actionForm.value.writer_id) {
        payload.writer_id = actionForm.value.writer_id
      }
      
      // Add payment reference fields for mark_paid action
      if (actionForm.value.action === 'mark_paid') {
        if (actionForm.value.reference_id) {
          payload.reference_id = actionForm.value.reference_id
        }
        if (actionForm.value.payment_method) {
          payload.payment_method = actionForm.value.payment_method
        }
      }
      
      response = await ordersAPI.executeAction(props.order.id, actionForm.value.action, payload)
      
      if (response.data.status === 'success') {
        // Create a detailed success message
        const orderTopic = props.order?.topic || 'Untitled'
        const orderId = props.order?.id
        const actionName = actionLabel.value || payload.action?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
        const statusChange = response.data.old_status && response.data.new_status
          ? `Status changed from "${response.data.old_status.replace('_', ' ')}" to "${response.data.new_status.replace('_', ' ')}"`
          : response.data.new_status
            ? `Status changed to "${response.data.new_status.replace('_', ' ')}"`
            : ''
        
        const successMessage = response.data.message || 
          `${actionName} completed successfully for Order #${orderId} "${orderTopic}". ${statusChange ? statusChange + '.' : ''}`
        
        emit('success', {
          order: response.data.order,
          message: successMessage,
          old_status: response.data.old_status,
          new_status: response.data.new_status,
          action: payload.action
        })
        emit('update:visible', false)
      } else {
        error.value = response.data.detail || 'Action failed'
        errorDetails.value = response.data
        emit('error', response.data)
      }
    }
  } catch (err) {
    const errorData = err.response?.data || {}
    
    // Use improved error handler for better messages
    const actionName = actionLabel.value || actionForm.value.action?.replace('_', ' ') || 'this action'
    error.value = getErrorMessage(err, `Failed to execute ${actionName}`, `Unable to ${actionName.toLowerCase()}`)
    errorDetails.value = errorData
    
    // Show available actions if provided
    if (errorData.available_actions) {
      errorDetails.value = {
        available_actions: errorData.available_actions
      }
    }
    
    emit('error', errorData)
  } finally {
    loading.value = false
  }
}
</script>

