<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Orders</h1>
      <div class="flex items-center gap-2">
        <ExportButton
          v-if="authStore.isAdmin || authStore.isSuperAdmin"
          :export-function="exportOrders"
          :export-params="exportParams"
          filename="orders"
          @exported="handleExportSuccess"
          @error="handleExportError"
        />
        <button
          v-if="canCreateOrder"
          @click="createOrder"
          class="btn btn-primary"
        >
          Create Order
        </button>
      </div>
    </div>

    <!-- Filter Panel -->
    <FilterPanel
      v-model:filters="filters"
      :status-options="statusOptions"
      :show-search="true"
      :show-date-range="true"
      :filter-labels="filterLabels"
      @filter-change="handleFilterChange"
    />

    <div class="card p-4 space-y-3">
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="group in quickStatusGroups"
            :key="group.key"
            type="button"
            class="px-3 py-1.5 rounded-full border text-sm transition"
            :class="isStatusGroupActive(group.key) ? 'bg-primary-600 text-white border-primary-600' : 'border-gray-300 text-gray-600 hover:border-primary-300'"
            @click="toggleStatusGroup(group.key)"
          >
            {{ group.label }}
          </button>
        </div>
        <div class="ml-auto flex items-center gap-2 relative" ref="savedFiltersMenuRef">
          <button
            type="button"
            class="px-3 py-2 rounded-lg border border-gray-300 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
            @click.stop="toggleSavedFiltersMenu"
          >
            <span>Saved Filters</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <div
            v-if="savedFiltersMenuOpen"
            class="absolute right-0 top-full mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-30"
          >
            <div v-if="!savedFilters.length" class="text-xs text-gray-500">
              No saved filters yet.
            </div>
            <ul v-else class="space-y-1 max-h-40 overflow-y-auto">
              <li
                v-for="item in savedFilters"
                :key="item.id"
                class="flex items-center gap-2 text-sm"
              >
                <button
                  type="button"
                  class="flex-1 text-left text-gray-700 hover:text-primary-600"
                  @click="applySavedFilter(item)"
                >
                  {{ item.name }}
                </button>
                <button
                  type="button"
                  class="text-gray-400 hover:text-red-500"
                  @click="deleteSavedFilter(item.id)"
                >
                  ✕
                </button>
              </li>
            </ul>
            <div class="mt-3 space-y-2">
              <input
                v-model="newSavedFilterName"
                type="text"
                placeholder="Filter name"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              />
              <button
                type="button"
                class="w-full px-3 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 text-sm disabled:opacity-50"
                :disabled="!newSavedFilterName.trim()"
                @click="saveCurrentFilters"
              >
                Save Current
              </button>
            </div>
          </div>
          <button
            type="button"
            class="px-3 py-2 rounded-lg border border-primary-600 text-primary-600 hover:bg-primary-50 text-sm"
            @click="openAdvancedFilters = true"
          >
            Advanced Filters
          </button>
          <button
            type="button"
            class="px-3 py-2 rounded-lg text-sm text-gray-500 hover:text-gray-700"
            @click="clearAllFilters"
          >
            Clear
          </button>
        </div>
      </div>
      <div v-if="activeFilterChips.length" class="flex flex-wrap gap-2">
        <span
          v-for="chip in activeFilterChips"
          :key="chip.key"
          class="inline-flex items-center gap-2 bg-gray-100 text-gray-700 rounded-full px-3 py-1 text-sm"
        >
          {{ chip.label }}
          <button
            type="button"
            class="text-gray-500 hover:text-gray-700"
            @click="removeFilterChip(chip.key)"
          >
            ✕
          </button>
        </span>
      </div>
    </div>

    <!-- Bulk Actions (Admin Only) -->
    <div v-if="(authStore.isAdmin || authStore.isSuperAdmin) && selectedOrders.length > 0" class="card p-4 bg-blue-50 border border-blue-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sm font-medium text-blue-900">
            {{ selectedOrders.length }} order(s) selected
          </span>
          <button
            @click="selectedOrders = []"
            class="text-sm text-blue-600 hover:text-blue-700"
          >
            Clear Selection
          </button>
        </div>
        <div class="flex gap-2">
          <select
            v-model="bulkAction"
            class="border rounded px-3 py-2 text-sm"
            @change="handleBulkAction"
          >
            <option value="">Bulk Actions...</option>
            <option value="assign">Assign to Writer</option>
            <option value="cancel">Cancel Orders</option>
            <option value="archive">Archive Orders</option>
            <option value="on_hold">Put on Hold</option>
          </select>
        </div>
      </div>
    </div>

    <div class="card p-4 space-y-4">

      <!-- Results -->
      <div v-if="loading" class="text-sm text-gray-500">Loading...</div>
      <div v-else>
        <div v-if="!orders.length" class="text-sm text-gray-500">No orders found.</div>
        <div v-else class="space-y-2">
          <!-- Select All (Admin Only) -->
          <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="flex items-center gap-2 pb-2 border-b">
            <input
              type="checkbox"
              :checked="selectedOrders.length === orders.length && orders.length > 0"
              @change="toggleSelectAll"
              class="rounded border-gray-300"
            />
            <span class="text-sm text-gray-600">Select All</span>
          </div>
          
          <ul class="divide-y divide-gray-200">
            <li v-for="o in orders" :key="o.id" class="py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors">
              <!-- Checkbox (Admin Only) -->
              <input
                v-if="authStore.isAdmin || authStore.isSuperAdmin"
                type="checkbox"
                :value="o.id"
                v-model="selectedOrders"
                class="rounded border-gray-300"
                @click.stop
              />
              
              <div class="flex-1 cursor-pointer" @click="router.push(`/orders/${o.id}`)">
                <div class="font-medium">#{{ o.id }} · {{ o.topic }}</div>
                <div class="text-xs text-gray-500">
                  <span :class="badgeClass(o.status)" class="inline-block px-2 py-0.5 rounded mr-2">{{ o.status }}</span>
                  <span v-if="o.is_paid" class="inline-block px-2 py-0.5 rounded bg-green-100 text-green-700 mr-2">Paid</span>
                  <span v-else class="inline-block px-2 py-0.5 rounded bg-yellow-100 text-yellow-700 mr-2">Unpaid</span>
                  Created: {{ toDT(o.created_at) }}
                </div>
              </div>
              <div class="flex items-center gap-2" @click.stop>
                <router-link
                  :to="`/orders/${o.id}/messages`"
                  class="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm flex items-center gap-1"
                  title="View Messages"
                  @click.stop
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  Messages
                </router-link>
                <router-link 
                  :to="`/orders/${o.id}`" 
                  class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
                  @click.stop
                >
                  Open
                </router-link>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Pagination - Only show if we have more items than can fit on one page -->
    <Pagination
      v-if="pagination.totalItems > pagination.itemsPerPage"
      :current-page="pagination.currentPage"
      :total-items="pagination.totalItems"
      :items-per-page="pagination.itemsPerPage"
      @page-change="handlePageChange"
    />
    
    <!-- Show total count when all orders are loaded -->
    <div v-if="!loading && orders.length > 0" class="text-sm text-gray-500 text-center py-2">
      Showing {{ orders.length }} of {{ pagination.totalItems }} order(s)
    </div>

    <!-- Bulk Assign Modal -->
    <Modal
      :visible="showBulkAssignModal"
      title="Bulk Assign Orders"
      size="md"
      @update:visible="showBulkAssignModal = $event"
    >
      <div class="space-y-4">
        <div>
          <p class="text-sm text-gray-600 mb-3">
            Assigning <strong>{{ selectedOrders.length }}</strong> order(s) to a writer
          </p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Select Writer <span class="text-red-500">*</span>
          </label>
          <select
            v-model="bulkAssignForm.writer_id"
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            required
          >
            <option value="">Select a writer...</option>
            <option v-for="writer in writers" :key="writer.id" :value="writer.id">
              {{ formatWriterName(writer) }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason (Optional)
          </label>
          <textarea
            v-model="bulkAssignForm.reason"
            rows="3"
            placeholder="Reason for bulk assignment..."
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          ></textarea>
        </div>
      </div>

      <template #footer>
        <button
          @click="showBulkAssignModal = false"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="submitBulkAssign"
          :disabled="processingBulk || !bulkAssignForm.writer_id"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ processingBulk ? 'Assigning...' : 'Assign Orders' }}
        </button>
      </template>
    </Modal>

    <!-- Bulk Action Modal -->
    <Modal
      :visible="showBulkActionModal"
      :title="`Bulk ${bulkActionForm.action ? bulkActionForm.action.charAt(0).toUpperCase() + bulkActionForm.action.slice(1).replace('_', ' ') : 'Action'} Orders`"
      size="md"
      @update:visible="showBulkActionModal = $event"
    >
      <div class="space-y-4">
        <div>
          <p class="text-sm text-gray-600 mb-3">
            Performing <strong>{{ bulkActionForm.action }}</strong> on <strong>{{ selectedOrders.length }}</strong> order(s)
          </p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notes (Optional)
          </label>
          <textarea
            v-model="bulkActionForm.notes"
            rows="3"
            placeholder="Add notes about this bulk action..."
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          ></textarea>
        </div>
        <div v-if="bulkActionForm.action === 'cancel'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p class="text-sm text-yellow-800">
            ⚠️ <strong>Warning:</strong> Canceling orders cannot be undone. Make sure this is the intended action.
          </p>
        </div>
      </div>

      <template #footer>
        <button
          @click="showBulkActionModal = false"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="submitBulkAction"
          :disabled="processingBulk"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ processingBulk ? 'Processing...' : 'Confirm Action' }}
        </button>
      </template>
    </Modal>

    <!-- Message Toast -->
    <div
      v-if="message"
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50"
      :class="messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { hasPermission } from '@/utils/permissions'
import ordersAPI from '@/api/orders'
import FilterPanel from '@/components/common/FilterPanel.vue'
import Pagination from '@/components/common/Pagination.vue'
import Modal from '@/components/common/Modal.vue'
import ExportButton from '@/components/common/ExportButton.vue'
import { formatWriterName } from '@/utils/formatDisplay'
import adminOrdersAPI from '@/api/admin-orders'
import usersAPI from '@/api/users'
import exportsAPI from '@/api/exports'
import orderConfigsAPI from '@/api/orderConfigs'
import AdvancedFiltersDrawer from '@/components/orders/AdvancedFiltersDrawer.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const loading = ref(false)
const orders = ref([])
const selectedOrders = ref([])
const bulkAction = ref('')
const showBulkAssignModal = ref(false)
const showBulkActionModal = ref(false)
const bulkAssignForm = ref({
  writer_id: null,
  reason: ''
})
const bulkActionForm = ref({
  action: '',
  notes: ''
})
const writers = ref([])
const processingBulk = ref(false)
const cloneFilters = (value) => JSON.parse(JSON.stringify(value || {}))

const DEFAULT_FILTERS = {
  search: route.query.search || '',
  status: route.query.status || '',
  is_paid: route.query.is_paid || '',
  date_from: route.query.date_from || '',
  date_to: route.query.date_to || '',
  status_group: route.query.status_group ? route.query.status_group.split(',').filter(Boolean) : [],
  created_from: route.query.created_from || '',
  created_to: route.query.created_to || '',
  deadline_from: route.query.deadline_from || '',
  deadline_to: route.query.deadline_to || '',
  price_min: route.query.price_min || '',
  price_max: route.query.price_max || '',
  pages_min: route.query.pages_min || '',
  pages_max: route.query.pages_max || '',
  writer_query: route.query.writer_query || '',
  client_query: route.query.client_query || '',
  subject_id: route.query.subject_id || '',
  paper_type_id: route.query.paper_type_id || '',
  academic_level_id: route.query.academic_level_id || '',
  type_of_work_id: route.query.type_of_work_id || '',
  flags: route.query.flags ? route.query.flags.split(',').filter(Boolean) : [],
  include_archived: route.query.include_archived === '1',
  only_archived: route.query.only_archived === '1'
}

const filters = ref(cloneFilters(DEFAULT_FILTERS))

const filterMetadata = ref({
  status_groups: [],
  flags: []
})

const subjectOptions = ref([])
const paperTypes = ref([])
const academicLevels = ref([])
const typesOfWork = ref([])

const quickStatusGroups = computed(() => {
  if (!filterMetadata.value.status_groups?.length) {
    return [
      { key: 'active', label: 'Active' },
      { key: 'pending', label: 'Pending' },
      { key: 'needs_attention', label: 'Needs Attention' },
      { key: 'completed', label: 'Completed' },
      { key: 'archived', label: 'Archived' }
    ]
  }
  return filterMetadata.value.status_groups.map((group) => ({
    key: group.key,
    label: group.label || group.key
  }))
})

const openAdvancedFilters = ref(false)
const savedFilters = ref([])
const savedFiltersMenuOpen = ref(false)
const newSavedFilterName = ref('')
const savedFiltersMenuRef = ref(null)

const pagination = ref({
  currentPage: 1,
  totalItems: 0,
  totalPages: 0,
  itemsPerPage: 100  // Default page size (backend uses 100, max 500)
})

// All order statuses organized by category
const statusOptions = [
  // Initial States
  { value: 'created', label: 'Created' },
  { value: 'pending', label: 'Pending' },
  { value: 'unpaid', label: 'Unpaid' },
  { value: 'paid', label: 'Paid' },
  
  // Assignment & Availability
  { value: 'pending_writer_assignment', label: 'Pending Assignment' },
  { value: 'available', label: 'Available' },
  { value: 'reassigned', label: 'Reassigned' },
  
  // Active Work
  { value: 'in_progress', label: 'In Progress' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'submitted', label: 'Submitted' },
  
  // Review & Rating
  { value: 'reviewed', label: 'Reviewed' },
  { value: 'rated', label: 'Rated' },
  { value: 'approved', label: 'Approved' },
  { value: 'completed', label: 'Completed' },
  
  // Revisions
  { value: 'revision_requested', label: 'Revision Requested' },
  { value: 'revision_in_progress', label: 'Revision In Progress' },
  { value: 'revised', label: 'Revised' },
  { value: 'on_revision', label: 'On Revision' },
  
  // Editing
  { value: 'under_editing', label: 'Under Editing' },
  
  // Issues
  { value: 'disputed', label: 'Disputed' },
  { value: 'late', label: 'Late' },
  
  // Final States
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'reopened', label: 'Reopened' },
  { value: 'refunded', label: 'Refunded' },
  { value: 'archived', label: 'Archived' },
  { value: 'closed', label: 'Closed' },
]


const filterLabels = {
  search: 'Search',
  status: 'Status',
  is_paid: 'Payment Status',
  date_from: 'Date From',
  date_to: 'Date To'
}

const statusGroupLookup = computed(() => {
  const map = {}
  filterMetadata.value.status_groups?.forEach((group) => {
    map[group.key] = group
  })
  return map
})

const flagLookup = computed(() => {
  const map = {}
  filterMetadata.value.flags?.forEach((flag) => {
    map[flag.value] = flag.label || flag.value
  })
  return map
})

const optionToLookup = (collection) => {
  const map = {}
  collection.forEach((item) => {
    map[item.id] = item.name || item.label || item.title || `#${item.id}`
  })
  return map
}

const subjectLookup = computed(() => optionToLookup(subjectOptions.value))
const paperTypeLookup = computed(() => optionToLookup(paperTypes.value))
const academicLevelLookup = computed(() => optionToLookup(academicLevels.value))
const typeOfWorkLookup = computed(() => optionToLookup(typesOfWork.value))

const activeFilterChips = computed(() => {
  const chips = []
  if (filters.value.status_group?.length) {
    const labels = filters.value.status_group.map((key) => statusGroupLookup.value[key]?.label || key)
    chips.push({ key: 'status_group', label: `Group: ${labels.join(', ')}` })
  }
  if (filters.value.created_from || filters.value.created_to) {
    chips.push({
      key: 'created_range',
      label: `Created ${filters.value.created_from || '...' } → ${filters.value.created_to || '...' }`
    })
  }
  if (filters.value.deadline_from || filters.value.deadline_to) {
    chips.push({
      key: 'deadline_range',
      label: `Deadline ${filters.value.deadline_from || '...' } → ${filters.value.deadline_to || '...' }`
    })
  }
  if (filters.value.price_min || filters.value.price_max) {
    chips.push({
      key: 'price_range',
      label: `Price ${filters.value.price_min || '0'} - ${filters.value.price_max || '∞'}`
    })
  }
  if (filters.value.pages_min || filters.value.pages_max) {
    chips.push({
      key: 'pages_range',
      label: `Pages ${filters.value.pages_min || '0'} - ${filters.value.pages_max || '∞'}`
    })
  }
  if (filters.value.subject_id) {
    chips.push({ key: 'subject_id', label: `Subject: ${subjectLookup.value[filters.value.subject_id] || filters.value.subject_id}` })
  }
  if (filters.value.paper_type_id) {
    chips.push({ key: 'paper_type_id', label: `Paper: ${paperTypeLookup.value[filters.value.paper_type_id] || filters.value.paper_type_id}` })
  }
  if (filters.value.academic_level_id) {
    chips.push({ key: 'academic_level_id', label: `Level: ${academicLevelLookup.value[filters.value.academic_level_id] || filters.value.academic_level_id}` })
  }
  if (filters.value.type_of_work_id) {
    chips.push({ key: 'type_of_work_id', label: `Work: ${typeOfWorkLookup.value[filters.value.type_of_work_id] || filters.value.type_of_work_id}` })
  }
  if (filters.value.writer_query) {
    chips.push({ key: 'writer_query', label: `Writer: ${filters.value.writer_query}` })
  }
  if (filters.value.client_query) {
    chips.push({ key: 'client_query', label: `Client: ${filters.value.client_query}` })
  }
  if (filters.value.flags?.length) {
    const labels = filters.value.flags.map((flag) => flagLookup.value[flag] || flag)
    chips.push({ key: 'flags', label: `Flags: ${labels.join(', ')}` })
  }
  if (filters.value.include_archived && !filters.value.only_archived) {
    chips.push({ key: 'include_archived', label: 'Including archived' })
  }
  if (filters.value.only_archived) {
    chips.push({ key: 'only_archived', label: 'Only archived' })
  }
  return chips
})

const ADVANCED_FILTER_KEYS = Object.keys(DEFAULT_FILTERS).filter((key) => !['search', 'status', 'is_paid', 'date_from', 'date_to'].includes(key))

const statusGroupLabel = (key) => statusGroupLookup.value[key]?.label || key
const isStatusGroupActive = (key) => filters.value.status_group.includes(key)

const toggleStatusGroup = (key) => {
  const current = new Set(filters.value.status_group)
  if (current.has(key)) {
    current.delete(key)
  } else {
    current.add(key)
  }
  filters.value.status_group = Array.from(current)
  pagination.value.currentPage = 1
  handleFilterChange()
}

const savedFilterStorageKey = 'orders:savedFilters'

const loadSavedFilters = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(savedFilterStorageKey))
    if (Array.isArray(stored)) {
      savedFilters.value = stored
    }
  } catch (error) {
    console.warn('Failed to load saved filters:', error)
    savedFilters.value = []
  }
}

const persistSavedFilters = () => {
  localStorage.setItem(savedFilterStorageKey, JSON.stringify(savedFilters.value))
}

const toggleSavedFiltersMenu = () => {
  savedFiltersMenuOpen.value = !savedFiltersMenuOpen.value
}

const saveCurrentFilters = () => {
  if (!newSavedFilterName.value.trim()) return
  const entry = {
    id: Date.now().toString(),
    name: newSavedFilterName.value.trim(),
    filters: cloneFilters(filters.value),
    created_at: new Date().toISOString()
  }
  savedFilters.value = [entry, ...savedFilters.value].slice(0, 25)
  persistSavedFilters()
  newSavedFilterName.value = ''
  savedFiltersMenuOpen.value = false
}

const applySavedFilter = (entry) => {
  filters.value = cloneFilters({ ...DEFAULT_FILTERS, ...entry.filters })
  pagination.value.currentPage = 1
  handleFilterChange()
  savedFiltersMenuOpen.value = false
}

const deleteSavedFilter = (id) => {
  savedFilters.value = savedFilters.value.filter((item) => item.id !== id)
  persistSavedFilters()
}

const clearAllFilters = () => {
  filters.value = cloneFilters(DEFAULT_FILTERS)
  pagination.value.currentPage = 1
  handleFilterChange()
}

const removeFilterChip = (key) => {
  switch (key) {
    case 'status_group':
      filters.value.status_group = []
      break
    case 'created_range':
      filters.value.created_from = ''
      filters.value.created_to = ''
      break
    case 'deadline_range':
      filters.value.deadline_from = ''
      filters.value.deadline_to = ''
      break
    case 'price_range':
      filters.value.price_min = ''
      filters.value.price_max = ''
      break
    case 'pages_range':
      filters.value.pages_min = ''
      filters.value.pages_max = ''
      break
    case 'subject_id':
    case 'paper_type_id':
    case 'academic_level_id':
    case 'type_of_work_id':
      filters.value[key] = ''
      break
    case 'writer_query':
      filters.value.writer_query = ''
      break
    case 'client_query':
      filters.value.client_query = ''
      break
    case 'flags':
      filters.value.flags = []
      break
    case 'include_archived':
      filters.value.include_archived = false
      break
    case 'only_archived':
      filters.value.only_archived = false
      break
  }
  pagination.value.currentPage = 1
  handleFilterChange()
}

const handleAdvancedApply = (advancedFilters) => {
  filters.value = { ...filters.value, ...advancedFilters }
  pagination.value.currentPage = 1
  openAdvancedFilters.value = false
  handleFilterChange()
}

const resetAdvancedFilters = () => {
  const defaults = cloneFilters(DEFAULT_FILTERS)
  ADVANCED_FILTER_KEYS.forEach((key) => {
    filters.value[key] = cloneFilters(defaults[key])
  })
  pagination.value.currentPage = 1
  handleFilterChange()
}

const canCreateOrder = computed(() => {
  // Allow clients to create orders via wizard
  return authStore.isClient || hasPermission(authStore.userRole, 'CREATE_ORDER')
})

const createOrder = () => {
  if (authStore.isClient) {
    router.push('/orders/wizard')
  } else if (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) {
    // For admins, superadmins, and support, use the new admin order creation wizard
    router.push('/admin/orders/create')
  } else {
    // For writers and editors, use special order creation
    router.push('/orders/special/new')
  }
}

const toDT = (v) => (v ? new Date(v).toLocaleString() : '')
const badgeClass = (status) => {
  const statusClasses = {
    // Initial States
    'created': 'bg-gray-100 text-gray-700',
    'pending': 'bg-yellow-100 text-yellow-700',
    'unpaid': 'bg-orange-100 text-orange-700',
    'paid': 'bg-green-100 text-green-700',
    
    // Assignment & Availability
    'pending_writer_assignment': 'bg-indigo-100 text-indigo-700',
    'available': 'bg-blue-100 text-blue-700',
    'reassigned': 'bg-cyan-100 text-cyan-700',
    
    // Active Work
    'in_progress': 'bg-blue-100 text-blue-700',
    'on_hold': 'bg-gray-100 text-gray-700',
    'submitted': 'bg-purple-100 text-purple-700',
    
    // Review & Rating
    'reviewed': 'bg-teal-100 text-teal-700',
    'rated': 'bg-amber-100 text-amber-700',
    'approved': 'bg-green-100 text-green-700',
    'completed': 'bg-emerald-100 text-emerald-700',
    
    // Revisions
    'revision_requested': 'bg-yellow-100 text-yellow-700',
    'revision_in_progress': 'bg-orange-100 text-orange-700',
    'revised': 'bg-lime-100 text-lime-700',
    'on_revision': 'bg-yellow-100 text-yellow-700',
    
    // Editing
    'under_editing': 'bg-purple-100 text-purple-700',
    
    // Issues
    'disputed': 'bg-red-100 text-red-700',
    'late': 'bg-red-100 text-red-700',
    
    // Final States
    'cancelled': 'bg-gray-100 text-gray-700',
    'reopened': 'bg-blue-100 text-blue-700',
    'refunded': 'bg-pink-100 text-pink-700',
    'archived': 'bg-gray-100 text-gray-700',
    'closed': 'bg-slate-100 text-slate-700',
  }
  
  return statusClasses[status] || 'bg-gray-100 text-gray-700'
}

const buildQueryParams = () => {
  const params = {
    page: pagination.value.currentPage,
    page_size: pagination.value.itemsPerPage
  }
  const assignIfValue = (key, value) => {
    if (value !== undefined && value !== null && value !== '') {
      params[key] = value
    }
  }
  assignIfValue('search', filters.value.search)
  assignIfValue('status', filters.value.status)
  assignIfValue('is_paid', filters.value.is_paid)
  assignIfValue('date_from', filters.value.date_from)
  assignIfValue('date_to', filters.value.date_to)
  assignIfValue('created_from', filters.value.created_from)
  assignIfValue('created_to', filters.value.created_to)
  assignIfValue('deadline_from', filters.value.deadline_from)
  assignIfValue('deadline_to', filters.value.deadline_to)
  assignIfValue('price_min', filters.value.price_min)
  assignIfValue('price_max', filters.value.price_max)
  assignIfValue('pages_min', filters.value.pages_min)
  assignIfValue('pages_max', filters.value.pages_max)
  assignIfValue('writer_query', filters.value.writer_query)
  assignIfValue('client_query', filters.value.client_query)
  assignIfValue('subject_id', filters.value.subject_id)
  assignIfValue('paper_type_id', filters.value.paper_type_id)
  assignIfValue('academic_level_id', filters.value.academic_level_id)
  assignIfValue('type_of_work_id', filters.value.type_of_work_id)
  if (filters.value.status_group?.length) {
    params.status_group = filters.value.status_group.join(',')
  }
  if (filters.value.flags?.length) {
    params.flags = filters.value.flags.join(',')
  }
  if (filters.value.include_archived) {
    params.include_archived = 1
  }
  if (filters.value.only_archived) {
    params.only_archived = 1
  }
  return params
}

let skipNextRouteSync = false

const buildRouteQuery = () => {
  const params = buildQueryParams()
  const query = {}
  const simpleKeys = [
    'search',
    'status',
    'is_paid',
    'date_from',
    'date_to',
    'created_from',
    'created_to',
    'deadline_from',
    'deadline_to',
    'price_min',
    'price_max',
    'pages_min',
    'pages_max',
    'writer_query',
    'client_query',
    'subject_id',
    'paper_type_id',
    'academic_level_id',
    'type_of_work_id'
  ]
  simpleKeys.forEach((key) => {
    if (params[key]) {
      query[key] = params[key]
    }
  })
  if (filters.value.status_group?.length) {
    query.status_group = filters.value.status_group.join(',')
  }
  if (filters.value.flags?.length) {
    query.flags = filters.value.flags.join(',')
  }
  if (filters.value.include_archived) {
    query.include_archived = '1'
  }
  if (filters.value.only_archived) {
    query.only_archived = '1'
  }
  query.page = String(pagination.value.currentPage)
  if (pagination.value.itemsPerPage !== 100) {
    query.page_size = String(pagination.value.itemsPerPage)
  }
  return query
}

const syncFiltersToRoute = () => {
  skipNextRouteSync = true
  router.replace({ query: buildRouteQuery() }).catch(() => {
    skipNextRouteSync = false
  })
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await ordersAPI.list(buildQueryParams())
    
    // Handle paginated response (backend uses LimitedPagination)
    if (res.data?.results) {
      // Paginated response with metadata
      orders.value = res.data.results
      pagination.value.totalItems = res.data.count || 0
      pagination.value.currentPage = res.data.current_page || pagination.value.currentPage
      pagination.value.totalPages = res.data.total_pages || 1
    } else if (Array.isArray(res.data)) {
      // Fallback: Non-paginated response (legacy support)
      orders.value = res.data
      pagination.value.totalItems = res.data.length
      pagination.value.currentPage = 1
      pagination.value.totalPages = 1
    } else {
      orders.value = []
      pagination.value.totalItems = 0
      pagination.value.totalPages = 0
    }
    
    // Debug logging (can be removed in production)
    console.log(`Fetched ${orders.value.length} orders (page ${pagination.value.currentPage}/${pagination.value.totalPages}, total: ${pagination.value.totalItems})`)
  } catch (error) {
    console.error('Error fetching orders:', error)
    orders.value = []
    pagination.value.totalItems = 0
    pagination.value.totalPages = 0
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.value.currentPage = 1
  syncFiltersToRoute()
  fetchOrders()
}

const handlePageChange = (page) => {
  pagination.value.currentPage = page
  syncFiltersToRoute()
  fetchOrders()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(
  () => route.query,
  (q) => {
    if (skipNextRouteSync) {
      skipNextRouteSync = false
      return
    }
    filters.value.search = q.search || ''
    filters.value.status = q.status || ''
    filters.value.is_paid = q.is_paid || ''
    filters.value.date_from = q.date_from || ''
    filters.value.date_to = q.date_to || ''
    filters.value.created_from = q.created_from || ''
    filters.value.created_to = q.created_to || ''
    filters.value.deadline_from = q.deadline_from || ''
    filters.value.deadline_to = q.deadline_to || ''
    filters.value.price_min = q.price_min || ''
    filters.value.price_max = q.price_max || ''
    filters.value.pages_min = q.pages_min || ''
    filters.value.pages_max = q.pages_max || ''
    filters.value.writer_query = q.writer_query || ''
    filters.value.client_query = q.client_query || ''
    filters.value.subject_id = q.subject_id || ''
    filters.value.paper_type_id = q.paper_type_id || ''
    filters.value.academic_level_id = q.academic_level_id || ''
    filters.value.type_of_work_id = q.type_of_work_id || ''
    filters.value.status_group = q.status_group ? q.status_group.split(',').filter(Boolean) : []
    filters.value.flags = q.flags ? q.flags.split(',').filter(Boolean) : []
    filters.value.include_archived = q.include_archived === '1'
    filters.value.only_archived = q.only_archived === '1'
    pagination.value.currentPage = q.page ? parseInt(q.page, 10) || 1 : 1
    if (q.page_size) {
      const size = parseInt(q.page_size, 10)
      if (!Number.isNaN(size) && size > 0) {
        pagination.value.itemsPerPage = size
      }
    }
    fetchOrders()
  },
  { deep: true }
)

const toggleSelectAll = () => {
  if (selectedOrders.value.length === orders.value.length) {
    selectedOrders.value = []
  } else {
    selectedOrders.value = orders.value.map(o => o.id)
  }
}

const handleBulkAction = async () => {
  if (!bulkAction.value || selectedOrders.value.length === 0) return

  if (bulkAction.value === 'assign') {
    await loadWriters()
    showBulkAssignModal.value = true
  } else {
    bulkActionForm.value.action = bulkAction.value
    showBulkActionModal.value = true
  }
  
  bulkAction.value = ''
}

const loadWriters = async () => {
  try {
    const res = await usersAPI.list({ role: 'writer' })
    writers.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('Failed to load writers:', error)
  }
}

const submitBulkAssign = async () => {
  if (!bulkAssignForm.value.writer_id || selectedOrders.value.length === 0) return

  processingBulk.value = true
  try {
    const res = await adminOrdersAPI.bulkAssign({
      order_ids: selectedOrders.value,
      writer_id: bulkAssignForm.value.writer_id,
      reason: bulkAssignForm.value.reason
    })
    
    showMessage(res.data?.detail || 'Orders assigned successfully', true)
    selectedOrders.value = []
    bulkAssignForm.value = { writer_id: null, reason: '' }
    showBulkAssignModal.value = false
    await fetchOrders()
  } catch (error) {
    showMessage('Failed to assign orders: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    processingBulk.value = false
  }
}

const submitBulkAction = async () => {
  if (!bulkActionForm.value.action || selectedOrders.value.length === 0) return

  processingBulk.value = true
  try {
    const res = await adminOrdersAPI.bulkAction({
      order_ids: selectedOrders.value,
      action: bulkActionForm.value.action,
      notes: bulkActionForm.value.notes
    })
    
    showMessage(res.data?.detail || 'Bulk action completed successfully', true)
    selectedOrders.value = []
    bulkActionForm.value = { action: '', notes: '' }
    showBulkActionModal.value = false
    await fetchOrders()
  } catch (error) {
    showMessage('Failed to perform bulk action: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    processingBulk.value = false
  }
}

const message = ref('')
const messageSuccess = ref(false)

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

const extractResults = (res) => res.data?.results || res.data || []

const loadFilterMetadata = async () => {
  try {
    const res = await ordersAPI.getFilterMetadata()
    filterMetadata.value = res.data || {}
  } catch (error) {
    console.warn('Failed to load filter metadata:', error)
  }
}

const loadOrderConfigOptions = async () => {
  try {
    const [subjectsRes, papersRes, levelsRes, workRes] = await Promise.all([
      orderConfigsAPI.getSubjects(),
      orderConfigsAPI.getPaperTypes(),
      orderConfigsAPI.getAcademicLevels(),
      orderConfigsAPI.getTypesOfWork()
    ])
    subjectOptions.value = extractResults(subjectsRes)
    paperTypes.value = extractResults(papersRes)
    academicLevels.value = extractResults(levelsRes)
    typesOfWork.value = extractResults(workRes)
  } catch (error) {
    console.warn('Failed to load order config options:', error)
  }
}

const handleDocumentClick = (event) => {
  if (
    savedFiltersMenuOpen.value &&
    savedFiltersMenuRef.value &&
    !savedFiltersMenuRef.value.contains(event.target)
  ) {
    savedFiltersMenuOpen.value = false
  }
}

// Export functionality
const exportParams = computed(() => {
  const params = buildQueryParams()
  delete params.page
  delete params.page_size
  return params
})

const exportOrders = exportsAPI.exportOrders

const handleExportSuccess = (data) => {
  showMessage(`Successfully exported ${data.filename}`, true)
}

const handleExportError = (error) => {
  showMessage('Failed to export: ' + (error.response?.data?.error || error.message), false)
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  loadSavedFilters()
  loadFilterMetadata()
  loadOrderConfigOptions()
  if (authStore.isAdmin || authStore.isSuperAdmin) {
    loadWriters()
  }
  fetchOrders()
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

