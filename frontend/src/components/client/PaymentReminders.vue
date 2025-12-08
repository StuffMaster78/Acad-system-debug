<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Payment Reminders</h2>
        <p class="text-sm text-gray-600 mt-1">Manage reminders for unpaid orders</p>
      </div>
      <button
        @click="refreshReminders"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm disabled:opacity-50"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-red-800">{{ error }}</span>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="remindersData" class="space-y-6">
      <!-- Summary -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="card bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div class="text-sm text-gray-600 mb-1">Unpaid Orders</div>
          <div class="text-3xl font-bold text-blue-600">{{ remindersData.total_unpaid_orders || 0 }}</div>
        </div>
        <div class="card bg-green-50 rounded-lg p-4 border border-green-200">
          <div class="text-sm text-gray-600 mb-1">Reminders Sent</div>
          <div class="text-3xl font-bold text-green-600">{{ remindersData.total_reminders_sent || 0 }}</div>
        </div>
        <div class="card bg-yellow-50 rounded-lg p-4 border border-yellow-200">
          <div class="text-sm text-gray-600 mb-1">Pending Reminders</div>
          <div class="text-3xl font-bold text-yellow-600">
            {{ (remindersData.unpaid_orders || []).filter(o => o.next_reminder).length }}
          </div>
        </div>
      </div>

      <!-- Sent Reminders -->
      <div v-if="remindersData.reminders?.length" class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Sent Reminders</h3>
        <div class="space-y-3">
          <div
            v-for="reminder in remindersData.reminders"
            :key="reminder.id"
            class="p-4 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span class="px-3 py-1 bg-primary-100 text-primary-700 rounded-lg text-sm font-semibold">
                    {{ reminder.reminder_name }}
                  </span>
                  <span class="text-sm text-gray-600">Order #{{ reminder.order_id }}</span>
                </div>
                <div class="text-sm text-gray-900 mb-1">{{ reminder.order_topic }}</div>
                <div class="text-xs text-gray-500 mb-2">{{ reminder.message }}</div>
                <div class="flex items-center gap-4 text-xs text-gray-500">
                  <span>Sent: {{ formatDateTime(reminder.sent_at) }}</span>
                  <span v-if="reminder.sent_as_notification" class="text-green-600">📱 Notification</span>
                  <span v-if="reminder.sent_as_email" class="text-blue-600">📧 Email</span>
                </div>
              </div>
              <button
                @click="editReminder(reminder)"
                class="px-3 py-1 text-sm text-primary-600 hover:text-primary-700 border border-primary-200 rounded-lg hover:bg-primary-50"
              >
                Edit
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Unpaid Orders -->
      <div v-if="remindersData.unpaid_orders?.length" class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Unpaid Orders</h3>
        <div class="space-y-4">
          <div
            v-for="order in remindersData.unpaid_orders"
            :key="order.order_id"
            class="p-4 bg-gray-50 rounded-lg border border-gray-200"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span class="font-semibold text-gray-900">Order #{{ order.order_id }}</span>
                  <span class="text-sm text-gray-600">{{ order.type_of_work }}</span>
                </div>
                <div class="text-sm text-gray-900 mb-2">{{ order.order_topic }}</div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div class="text-gray-600">Total Price</div>
                    <div class="font-semibold text-gray-900">${{ formatCurrency(order.total_price) }}</div>
                  </div>
                  <div>
                    <div class="text-gray-600">Deadline</div>
                    <div class="font-semibold text-gray-900">{{ formatDate(order.client_deadline) }}</div>
                  </div>
                  <div>
                    <div class="text-gray-600">Progress</div>
                    <div class="font-semibold text-gray-900">
                      {{ order.deadline_percentage ? `${order.deadline_percentage}%` : 'N/A' }}
                    </div>
                  </div>
                  <div>
                    <div class="text-gray-600">Reminders Sent</div>
                    <div class="font-semibold text-gray-900">{{ order.reminders_sent?.length || 0 }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Next Reminder -->
            <div v-if="order.next_reminder" class="mt-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-sm font-semibold text-yellow-800">Next Reminder Available</div>
                  <div class="text-xs text-yellow-600 mt-1">{{ order.next_reminder.name }} ({{ order.next_reminder.deadline_percentage }}%)</div>
                  <div class="text-xs text-yellow-600">{{ order.next_reminder.message }}</div>
                </div>
                <button
                  @click="createReminder(order)"
                  class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm"
                >
                  Schedule Reminder
                </button>
              </div>
            </div>

            <!-- No Next Reminder -->
            <div v-else class="mt-3 p-3 bg-gray-100 rounded-lg">
              <div class="text-sm text-gray-600">All reminders have been sent for this order.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <div class="text-4xl mb-4">✅</div>
        <p class="text-gray-600">No unpaid orders found.</p>
      </div>
    </div>

    <!-- Edit Reminder Modal -->
    <div
      v-if="editingReminder"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeEditModal"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Edit Reminder Preference</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Send as Notification</label>
            <label class="flex items-center gap-2">
              <input
                type="checkbox"
                v-model="editForm.send_as_notification"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm text-gray-600">Send in-app notification</span>
            </label>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Send as Email</label>
            <label class="flex items-center gap-2">
              <input
                type="checkbox"
                v-model="editForm.send_as_email"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm text-gray-600">Send email notification</span>
            </label>
          </div>
          <div class="flex gap-3 pt-4">
            <button
              @click="saveReminder"
              :disabled="saving"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
            <button
              @click="closeEditModal"
              class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import clientDashboardAPI from '@/api/client-dashboard'

const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const remindersData = ref(null)
const editingReminder = ref(null)
const editForm = ref({
  send_as_notification: true,
  send_as_email: true
})

const fetchReminders = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await clientDashboardAPI.getPaymentReminders()
    remindersData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch payment reminders:', err)
    error.value = err.response?.data?.detail || 'Failed to load payment reminders'
    remindersData.value = null
  } finally {
    loading.value = false
  }
}

const refreshReminders = () => {
  fetchReminders()
}

const createReminder = async (order) => {
  saving.value = true
  try {
    await clientDashboardAPI.createPaymentReminder({
      order_id: order.order_id,
      reminder_config_id: order.next_reminder?.id
    })
    await fetchReminders()
  } catch (err) {
    console.error('Failed to create reminder:', err)
    error.value = err.response?.data?.detail || 'Failed to create reminder'
  } finally {
    saving.value = false
  }
}

const editReminder = (reminder) => {
  editingReminder.value = reminder
  editForm.value = {
    send_as_notification: reminder.sent_as_notification,
    send_as_email: reminder.sent_as_email
  }
}

const saveReminder = async () => {
  if (!editingReminder.value) return
  
  saving.value = true
  try {
    await clientDashboardAPI.updatePaymentReminder(editingReminder.value.id, editForm.value)
    await fetchReminders()
    closeEditModal()
  } catch (err) {
    console.error('Failed to update reminder:', err)
    error.value = err.response?.data?.detail || 'Failed to update reminder'
  } finally {
    saving.value = false
  }
}

const closeEditModal = () => {
  editingReminder.value = null
  editForm.value = {
    send_as_notification: true,
    send_as_email: true
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

onMounted(() => {
  fetchReminders()
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}
</style>

