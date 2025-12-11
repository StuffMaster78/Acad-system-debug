<template>
  <div class="space-y-6 p-6">
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Data Exports</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Export orders, payments, users, and financial data</p>
    </div>

    <!-- Export Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Orders Export -->
      <div class="card p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Export Orders</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Format</label>
            <select
              v-model="ordersExport.format"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            >
              <option value="csv">CSV</option>
              <option value="xlsx">Excel (XLSX)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status (comma-separated)</label>
            <input
              v-model="ordersExport.status"
              type="text"
              placeholder="e.g., completed, in_progress"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date From</label>
              <input
                v-model="ordersExport.date_from"
                type="date"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date To</label>
              <input
                v-model="ordersExport.date_to"
                type="date"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              />
            </div>
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input
                v-model="ordersExport.is_paid"
                type="checkbox"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Paid Orders Only</span>
            </label>
          </div>
          <button
            @click="exportOrders"
            :disabled="exporting.orders"
            class="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {{ exporting.orders ? 'Exporting...' : 'Export Orders' }}
          </button>
        </div>
      </div>

      <!-- Payments Export -->
      <div class="card p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Export Payments</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Format</label>
            <select
              v-model="paymentsExport.format"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            >
              <option value="csv">CSV</option>
              <option value="xlsx">Excel (XLSX)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
            <select
              v-model="paymentsExport.status"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            >
              <option value="">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date From</label>
              <input
                v-model="paymentsExport.date_from"
                type="date"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date To</label>
              <input
                v-model="paymentsExport.date_to"
                type="date"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              />
            </div>
          </div>
          <button
            @click="exportPayments"
            :disabled="exporting.payments"
            class="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {{ exporting.payments ? 'Exporting...' : 'Export Payments' }}
          </button>
        </div>
      </div>

      <!-- Users Export -->
      <div class="card p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Export Users</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Format</label>
            <select
              v-model="usersExport.format"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            >
              <option value="csv">CSV</option>
              <option value="xlsx">Excel (XLSX)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Role</label>
            <select
              v-model="usersExport.role"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            >
              <option value="">All Roles</option>
              <option value="client">Clients</option>
              <option value="writer">Writers</option>
              <option value="admin">Admins</option>
            </select>
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input
                v-model="usersExport.is_active"
                type="checkbox"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active Users Only</span>
            </label>
          </div>
          <button
            @click="exportUsers"
            :disabled="exporting.users"
            class="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {{ exporting.users ? 'Exporting...' : 'Export Users' }}
          </button>
        </div>
      </div>

      <!-- Financial Export -->
      <div class="card p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Export Financial Report</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Format</label>
            <select
              v-model="financialExport.format"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            >
              <option value="csv">CSV</option>
              <option value="xlsx">Excel (XLSX)</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date From</label>
              <input
                v-model="financialExport.date_from"
                type="date"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date To</label>
              <input
                v-model="financialExport.date_to"
                type="date"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              />
            </div>
          </div>
          <button
            @click="exportFinancial"
            :disabled="exporting.financial"
            class="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {{ exporting.financial ? 'Exporting...' : 'Export Financial Report' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'
import adminManagementAPI from '@/api/admin-management'

const { success: showSuccess, error: showError } = useToast()

const exporting = ref({
  orders: false,
  payments: false,
  users: false,
  financial: false,
})

const ordersExport = ref({
  format: 'csv',
  status: '',
  date_from: '',
  date_to: '',
  is_paid: false,
})

const paymentsExport = ref({
  format: 'csv',
  status: '',
  date_from: '',
  date_to: '',
})

const usersExport = ref({
  format: 'csv',
  role: '',
  is_active: false,
})

const financialExport = ref({
  format: 'csv',
  date_from: '',
  date_to: '',
})

const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

const exportOrders = async () => {
  exporting.value.orders = true
  try {
    const params = { format: ordersExport.value.format }
    if (ordersExport.value.status) params.status = ordersExport.value.status
    if (ordersExport.value.date_from) params.date_from = ordersExport.value.date_from
    if (ordersExport.value.date_to) params.date_to = ordersExport.value.date_to
    if (ordersExport.value.is_paid) params.is_paid = 'true'
    
    const response = await adminManagementAPI.exportOrders(params)
    const filename = `orders_export_${new Date().toISOString().split('T')[0]}.${ordersExport.value.format}`
    downloadFile(response.data, filename)
    showSuccess('Orders exported successfully')
  } catch (error) {
    showError('Failed to export orders')
    console.error('Error exporting orders:', error)
  } finally {
    exporting.value.orders = false
  }
}

const exportPayments = async () => {
  exporting.value.payments = true
  try {
    const params = { format: paymentsExport.value.format }
    if (paymentsExport.value.status) params.status = paymentsExport.value.status
    if (paymentsExport.value.date_from) params.date_from = paymentsExport.value.date_from
    if (paymentsExport.value.date_to) params.date_to = paymentsExport.value.date_to
    
    const response = await adminManagementAPI.exportPayments(params)
    const filename = `payments_export_${new Date().toISOString().split('T')[0]}.${paymentsExport.value.format}`
    downloadFile(response.data, filename)
    showSuccess('Payments exported successfully')
  } catch (error) {
    showError('Failed to export payments')
    console.error('Error exporting payments:', error)
  } finally {
    exporting.value.payments = false
  }
}

const exportUsers = async () => {
  exporting.value.users = true
  try {
    const params = { format: usersExport.value.format }
    if (usersExport.value.role) params.role = usersExport.value.role
    if (usersExport.value.is_active) params.is_active = 'true'
    
    const response = await adminManagementAPI.exportUsers(params)
    const filename = `users_export_${new Date().toISOString().split('T')[0]}.${usersExport.value.format}`
    downloadFile(response.data, filename)
    showSuccess('Users exported successfully')
  } catch (error) {
    showError('Failed to export users')
    console.error('Error exporting users:', error)
  } finally {
    exporting.value.users = false
  }
}

const exportFinancial = async () => {
  exporting.value.financial = true
  try {
    const params = { format: financialExport.value.format }
    if (financialExport.value.date_from) params.date_from = financialExport.value.date_from
    if (financialExport.value.date_to) params.date_to = financialExport.value.date_to
    
    const response = await adminManagementAPI.exportFinancial(params)
    const filename = `financial_report_${new Date().toISOString().split('T')[0]}.${financialExport.value.format}`
    downloadFile(response.data, filename)
    showSuccess('Financial report exported successfully')
  } catch (error) {
    showError('Failed to export financial report')
    console.error('Error exporting financial:', error)
  } finally {
    exporting.value.financial = false
  }
}
</script>

