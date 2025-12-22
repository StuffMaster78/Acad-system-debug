<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Invoice Management</h1>
        <p class="mt-2 text-gray-600">Create, manage, and track invoices</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="openCreateModal"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create Invoice
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Invoices</p>
        <p class="text-3xl font-bold text-blue-900">{{ statistics?.total_invoices || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Paid</p>
        <p class="text-3xl font-bold text-green-900">{{ statistics?.paid_invoices || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Unpaid</p>
        <p class="text-3xl font-bold text-yellow-900">{{ statistics?.unpaid_invoices || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Overdue</p>
        <p class="text-3xl font-bold text-red-900">{{ statistics?.overdue_invoices || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Amount</p>
        <p class="text-3xl font-bold text-purple-900">${{ formatCurrency(statistics?.total_amount || 0) }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Reference ID, email, title..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadInvoices" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="paid">Paid</option>
            <option value="unpaid">Unpaid</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Client</label>
          <input
            v-model="filters.client_id"
            @input="debouncedSearch"
            type="number"
            placeholder="Client ID..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <input
            v-model="filters.website_id"
            @input="debouncedSearch"
            type="number"
            placeholder="Website ID..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Invoices Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reference ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="invoices.length === 0">
              <td colspan="8" class="px-6 py-8 text-center text-gray-500">
                No invoices found
              </td>
            </tr>
            <tr
              v-for="invoice in invoices"
              :key="invoice.id"
              class="hover:bg-gray-50 cursor-pointer"
              @click="viewInvoice(invoice)"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="font-mono text-sm font-medium text-gray-900">{{ invoice.reference_id }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="text-sm font-medium text-gray-900">{{ invoice.client?.full_name || invoice.client?.email || 'N/A' }}</div>
                  <div class="text-sm text-gray-500">{{ invoice.recipient_email }}</div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900">{{ invoice.title }}</div>
                <div v-if="invoice.description" class="text-xs text-gray-500 truncate max-w-xs">{{ invoice.description }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-semibold text-gray-900">${{ formatCurrency(invoice.amount) }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(invoice)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ getStatusLabel(invoice) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(invoice.due_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(invoice.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium" @click.stop>
                <div class="flex items-center gap-2">
                  <button
                    @click="viewInvoice(invoice)"
                    class="text-blue-600 hover:text-blue-900"
                    title="View Details"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    v-if="!invoice.is_paid"
                    @click="sendInvoiceEmail(invoice)"
                    class="text-green-600 hover:text-green-900"
                    title="Send Email"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </button>
                <button
                  @click.stop="openActionMenu(invoice, $event)"
                  class="text-gray-600 hover:text-gray-900"
                  title="More Actions"
                >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="!loading && invoices.length > 0" class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          Showing {{ invoices.length }} invoice(s)
        </div>
        <div class="flex gap-2">
          <button
            @click="loadInvoices(page - 1)"
            :disabled="page <= 1"
            class="px-4 py-2 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="loadInvoices(page + 1)"
            :disabled="invoices.length < 50"
            class="px-4 py-2 border rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Invoice Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="closeCreateModal"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingInvoice ? 'Edit Invoice' : 'Create Invoice' }}
            </h2>
            <button @click="closeCreateModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveInvoice" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Client *</label>
              <input
                v-model="invoiceForm.client_id"
                type="number"
                required
                placeholder="Client ID"
                class="w-full border rounded px-3 py-2"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Recipient Email *</label>
              <input
                v-model="invoiceForm.recipient_email"
                type="email"
                required
                placeholder="client@example.com"
                class="w-full border rounded px-3 py-2"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input
                v-model="invoiceForm.title"
                type="text"
                required
                placeholder="Invoice Title"
                class="w-full border rounded px-3 py-2"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="invoiceForm.description"
                rows="3"
                placeholder="Invoice description..."
                class="w-full border rounded px-3 py-2"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Amount *</label>
                <input
                  v-model.number="invoiceForm.amount"
                  type="number"
                  step="0.01"
                  required
                  min="0"
                  placeholder="0.00"
                  class="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Due Date *</label>
                <input
                  v-model="invoiceForm.due_date"
                  type="date"
                  required
                  class="w-full border rounded px-3 py-2"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Website ID</label>
              <input
                v-model.number="invoiceForm.website_id"
                type="number"
                placeholder="Auto-assigned if not provided"
                class="w-full border rounded px-3 py-2"
              />
            </div>

            <div class="flex items-center gap-2">
              <input
                v-model="invoiceForm.send_email"
                type="checkbox"
                id="send_email"
                class="rounded"
              />
              <label for="send_email" class="text-sm text-gray-700">Send invoice email immediately</label>
            </div>

            <div class="flex justify-end gap-3 pt-4">
              <button
                type="button"
                @click="closeCreateModal"
                class="px-6 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : (editingInvoice ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- View Invoice Modal -->
    <div
      v-if="viewingInvoice"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="viewingInvoice = null"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900">Invoice Details</h2>
            <button @click="viewingInvoice = null" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm font-medium text-gray-600">Reference ID</p>
                <p class="text-lg font-mono font-semibold">{{ viewingInvoice.reference_id }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-600">Status</p>
                <span :class="getStatusClass(viewingInvoice)" class="px-3 py-1 text-sm font-medium rounded-full">
                  {{ getStatusLabel(viewingInvoice) }}
                </span>
              </div>
            </div>

            <div>
              <p class="text-sm font-medium text-gray-600">Title</p>
              <p class="text-lg">{{ viewingInvoice.title }}</p>
            </div>

            <div v-if="viewingInvoice.description">
              <p class="text-sm font-medium text-gray-600">Description</p>
              <p class="text-gray-900">{{ viewingInvoice.description }}</p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm font-medium text-gray-600">Amount</p>
                <p class="text-2xl font-bold text-gray-900">${{ formatCurrency(viewingInvoice.amount) }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-600">Due Date</p>
                <p class="text-lg">{{ formatDate(viewingInvoice.due_date) }}</p>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm font-medium text-gray-600">Client</p>
                <p class="text-gray-900">{{ viewingInvoice.client?.full_name || viewingInvoice.client?.email || 'N/A' }}</p>
                <p class="text-sm text-gray-500">{{ viewingInvoice.recipient_email }}</p>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-600">Issued By</p>
                <p class="text-gray-900">{{ viewingInvoice.issued_by?.full_name || viewingInvoice.issued_by?.email || 'N/A' }}</p>
              </div>
            </div>

            <div v-if="viewingInvoice.payment_link">
              <p class="text-sm font-medium text-gray-600">Payment Link</p>
              <div class="flex items-center gap-2">
                <input
                  :value="viewingInvoice.payment_link"
                  readonly
                  class="flex-1 border rounded px-3 py-2 bg-gray-50 text-sm"
                />
                <button
                  @click="copyPaymentLink(viewingInvoice.payment_link)"
                  class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 text-sm"
                >
                  Copy
                </button>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4 text-sm">
              <div><span class="font-medium text-gray-600">Created:</span> {{ formatDateTime(viewingInvoice.created_at) }}</div>
              <div><span class="font-medium text-gray-600">Updated:</span> {{ formatDateTime(viewingInvoice.updated_at) }}</div>
            </div>

            <div class="flex gap-3 pt-4 border-t">
              <button
                v-if="!viewingInvoice.is_paid"
                @click="sendInvoiceEmail(viewingInvoice)"
                class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Send Email
              </button>
              <button
                v-if="!viewingInvoice.is_paid"
                @click="regeneratePaymentLink(viewingInvoice)"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Regenerate Link
              </button>
              <button
                @click="viewingInvoice = null"
                class="px-6 py-2 border rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Menu Dropdown -->
    <div
      v-if="actionMenuInvoice"
      class="fixed z-50 bg-white border rounded-lg shadow-lg p-2 min-w-[200px]"
      :style="{ top: actionMenuPosition.y + 'px', left: actionMenuPosition.x + 'px' }"
      @click.stop
    >
      <button
        @click="viewInvoice(actionMenuInvoice)"
        class="w-full text-left px-4 py-2 hover:bg-gray-100 rounded text-sm"
      >
        View Details
      </button>
      <button
        v-if="!actionMenuInvoice.is_paid"
        @click="sendInvoiceEmail(actionMenuInvoice)"
        class="w-full text-left px-4 py-2 hover:bg-gray-100 rounded text-sm"
      >
        Send Email
      </button>
      <button
        v-if="!actionMenuInvoice.is_paid"
        @click="regeneratePaymentLink(actionMenuInvoice)"
        class="w-full text-left px-4 py-2 hover:bg-gray-100 rounded text-sm"
      >
        Regenerate Payment Link
      </button>
      <button
        @click="editInvoice(actionMenuInvoice)"
        class="w-full text-left px-4 py-2 hover:bg-gray-100 rounded text-sm"
      >
        Edit Invoice
      </button>
      <button
        @click="deleteInvoice(actionMenuInvoice)"
        class="w-full text-left px-4 py-2 hover:bg-red-100 text-red-600 rounded text-sm"
      >
        Delete Invoice
      </button>
      <button
        @click="actionMenuInvoice = null"
        class="w-full text-left px-4 py-2 hover:bg-gray-100 rounded text-sm"
      >
        Cancel
      </button>
    </div>

    <!-- Message Toast -->
    <div
      v-if="message"
      :class="[
        'fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50',
        messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]"
    >
      {{ message }}
    </div>
  </div>

  <!-- Loading State -->
  <div v-if="initialLoading" class="flex items-center justify-center min-h-screen">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>

  <!-- Error State -->
  <div v-if="componentError" class="flex items-center justify-center min-h-screen">
    <div class="text-center">
      <p class="text-red-600 text-lg mb-4">{{ componentError }}</p>
      <button @click="loadData" class="px-6 py-2 bg-primary-600 text-white rounded-lg">
        Retry
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import invoicesAPI from '@/api/invoices'

const initialLoading = ref(true)
const componentError = ref(null)
const loading = ref(false)
const invoices = ref([])
const statistics = ref({})
const page = ref(1)
const message = ref('')
const messageSuccess = ref(true)

const filters = ref({
  search: '',
  status: '',
  client_id: '',
  website_id: '',
})

const showCreateModal = ref(false)
const editingInvoice = ref(null)
const saving = ref(false)
const viewingInvoice = ref(null)
const actionMenuInvoice = ref(null)
const actionMenuPosition = ref({ x: 0, y: 0 })

const invoiceForm = ref({
  client_id: '',
  recipient_email: '',
  title: '',
  description: '',
  amount: 0,
  due_date: '',
  website_id: '',
  send_email: true,
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadInvoices()
  }, 500)
}

const loadData = async () => {
  try {
    initialLoading.value = true
    componentError.value = null
    await Promise.all([
      loadStatistics(),
      loadInvoices(),
    ])
  } catch (error) {
    componentError.value = error.response?.data?.detail || error.message || 'Failed to load data'
    console.error('Error loading data:', error)
  } finally {
    initialLoading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const response = await invoicesAPI.getStatistics()
    statistics.value = response.data || {}
  } catch (error) {
    // Only log if it's not a 404 (endpoint doesn't exist)
    if (error?.response?.status !== 404) {
      console.error('Error loading statistics:', error)
    }
    statistics.value = {}
  }
}

const loadInvoices = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      ...filters.value,
    }
    
    // Remove empty filters
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    
    const response = await invoicesAPI.list(params)
    invoices.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch (error) {
    showMessage('Failed to load invoices: ' + (error.response?.data?.detail || error.message), false)
    console.error('Error loading invoices:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: '',
    client_id: '',
    website_id: '',
  }
  loadInvoices()
}

const openCreateModal = () => {
  editingInvoice.value = null
  invoiceForm.value = {
    client_id: '',
    recipient_email: '',
    title: '',
    description: '',
    amount: 0,
    due_date: '',
    website_id: '',
    send_email: true,
  }
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  editingInvoice.value = null
}

const saveInvoice = async () => {
  try {
    saving.value = true
    
    const data = {
      ...invoiceForm.value,
      client_id: invoiceForm.value.client_id ? parseInt(invoiceForm.value.client_id) : null,
      website_id: invoiceForm.value.website_id ? parseInt(invoiceForm.value.website_id) : null,
    }
    
    if (editingInvoice.value) {
      await invoicesAPI.update(editingInvoice.value.id, data)
      showMessage('Invoice updated successfully', true)
    } else {
      await invoicesAPI.create(data)
      showMessage('Invoice created successfully', true)
    }
    
    closeCreateModal()
    await loadInvoices()
    await loadStatistics()
  } catch (error) {
    showMessage('Failed to save invoice: ' + (error.response?.data?.detail || error.message), false)
    console.error('Error saving invoice:', error)
  } finally {
    saving.value = false
  }
}

const viewInvoice = async (invoice) => {
  try {
    const response = await invoicesAPI.get(invoice.id)
    viewingInvoice.value = response.data
  } catch (error) {
    showMessage('Failed to load invoice details: ' + (error.response?.data?.detail || error.message), false)
    console.error('Error loading invoice:', error)
  }
}

const editInvoice = (invoice) => {
  editingInvoice.value = invoice
  invoiceForm.value = {
    client_id: invoice.client?.id || '',
    recipient_email: invoice.recipient_email || '',
    title: invoice.title || '',
    description: invoice.description || '',
    amount: invoice.amount || 0,
    due_date: invoice.due_date ? invoice.due_date.split('T')[0] : '',
    website_id: invoice.website?.id || '',
    send_email: false,
  }
  actionMenuInvoice.value = null
  showCreateModal.value = true
}

const deleteInvoice = async (invoice) => {
  if (!confirm(`Are you sure you want to delete invoice ${invoice.reference_id}?`)) return
  
  try {
    await invoicesAPI.delete(invoice.id)
    showMessage('Invoice deleted successfully', true)
    actionMenuInvoice.value = null
    await loadInvoices()
    await loadStatistics()
  } catch (error) {
    showMessage('Failed to delete invoice: ' + (error.response?.data?.detail || error.message), false)
    console.error('Error deleting invoice:', error)
  }
}

const sendInvoiceEmail = async (invoice) => {
  try {
    await invoicesAPI.sendEmail(invoice.id)
    showMessage('Invoice email sent successfully', true)
    if (viewingInvoice.value && viewingInvoice.value.id === invoice.id) {
      await viewInvoice(invoice)
    }
  } catch (error) {
    showMessage('Failed to send email: ' + (error.response?.data?.detail || error.message), false)
    console.error('Error sending email:', error)
  }
}

const regeneratePaymentLink = async (invoice) => {
  try {
    await invoicesAPI.regeneratePaymentLink(invoice.id)
    showMessage('Payment link regenerated successfully', true)
    if (viewingInvoice.value && viewingInvoice.value.id === invoice.id) {
      await viewInvoice(invoice)
    }
  } catch (error) {
    showMessage('Failed to regenerate link: ' + (error.response?.data?.detail || error.message), false)
    console.error('Error regenerating link:', error)
  }
}

const copyPaymentLink = (link) => {
  navigator.clipboard.writeText(link)
  showMessage('Payment link copied to clipboard', true)
}

const openActionMenu = (invoice, event) => {
  if (event) {
    actionMenuPosition.value = { x: event.clientX, y: event.clientY }
  } else {
    actionMenuPosition.value = { x: window.innerWidth / 2, y: window.innerHeight / 2 }
  }
  actionMenuInvoice.value = invoice
}

const getStatusClass = (invoice) => {
  if (invoice.is_paid) {
    return 'bg-green-100 text-green-800'
  }
  const dueDate = new Date(invoice.due_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  if (dueDate < today) {
    return 'bg-red-100 text-red-800'
  }
  return 'bg-yellow-100 text-yellow-800'
}

const getStatusLabel = (invoice) => {
  if (invoice.is_paid) {
    return 'Paid'
  }
  const dueDate = new Date(invoice.due_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  if (dueDate < today) {
    return 'Overdue'
  }
  return 'Unpaid'
}

const formatCurrency = (amount) => {
  return parseFloat(amount || 0).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* Component styles */
</style>

