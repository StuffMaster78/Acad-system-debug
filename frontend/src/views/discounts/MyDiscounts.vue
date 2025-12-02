<template>
  <div class="my-discounts">
    <div class="header">
      <div>
        <h1>My Discounts</h1>
        <p class="subtitle">Your available discount codes and special offers</p>
      </div>
      <div class="stats">
        <div class="stat-item">
          <span class="stat-value">{{ availableCount }}</span>
          <span class="stat-label">Available</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stackableCount }}</span>
          <span class="stat-label">Stackable</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ personalCount }}</span>
          <span class="stat-label">Personal</span>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button 
        :class="['tab', { active: activeTab === 'all' }]"
        @click="activeTab = 'all'"
      >
        All Discounts
      </button>
      <button 
        :class="['tab', { active: activeTab === 'stackable' }]"
        @click="activeTab = 'stackable'"
      >
        Stackable <span v-if="stackableCount > 0" class="badge">{{ stackableCount }}</span>
      </button>
      <button 
        :class="['tab', { active: activeTab === 'personal' }]"
        @click="activeTab = 'personal'"
      >
        My Personal Codes <span v-if="personalCount > 0" class="badge">{{ personalCount }}</span>
      </button>
      <button 
        :class="['tab', { active: activeTab === 'used' }]"
        @click="activeTab = 'used'"
      >
        Usage History
      </button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Search:</label>
        <input
          v-model="filters.search"
          type="text"
          placeholder="Search by code or description..."
          @input="debouncedSearch"
        />
      </div>
      <div class="filter-group">
        <label>Type:</label>
        <select v-model="filters.discount_type" @change="loadDiscounts">
          <option value="">All Types</option>
          <option value="percent">Percentage</option>
          <option value="fixed">Fixed Amount</option>
        </select>
      </div>
      <div class="filter-group">
        <label>
          <input 
            type="checkbox" 
            v-model="filters.show_expired"
            @change="loadDiscounts"
          />
          Show Expired
        </label>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading discounts...
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredDiscounts.length === 0" class="empty-state">
      <i class="fas fa-tag"></i>
      <p>No discounts found matching your criteria.</p>
      <button @click="resetFilters" class="btn btn-secondary">
        Reset Filters
      </button>
    </div>

    <!-- Discounts Grid -->
    <div v-else class="discounts-grid">
      <!-- Personal/Assigned Discounts Section -->
      <div v-if="activeTab === 'all' && personalDiscounts.length > 0" class="section">
        <h2 class="section-title">
          <i class="fas fa-star"></i> Your Personal Discounts
        </h2>
        <div class="discounts-row">
          <DiscountCard
            v-for="discount in personalDiscounts"
            :key="discount.id"
            :discount="discount"
            :is-personal="true"
            @copy="copyCode"
          />
        </div>
      </div>

      <!-- Stackable Discounts Section -->
      <div v-if="(activeTab === 'all' || activeTab === 'stackable') && stackableDiscounts.length > 0" class="section">
        <h2 class="section-title">
          <i class="fas fa-layer-group"></i> Stackable Discounts
          <span class="info-tooltip" title="These discounts can be combined with other codes">
            <i class="fas fa-info-circle"></i>
          </span>
        </h2>
        <div class="stackable-info">
          <p>
            <i class="fas fa-lightbulb"></i>
            You can use multiple stackable discounts together for maximum savings!
          </p>
        </div>
        <div class="discounts-row">
          <DiscountCard
            v-for="discount in stackableDiscounts"
            :key="discount.id"
            :discount="discount"
            :is-stackable="true"
            @copy="copyCode"
          />
        </div>
      </div>

      <!-- General Discounts Section -->
      <div v-if="activeTab === 'all' && generalDiscounts.length > 0" class="section">
        <h2 class="section-title">
          <i class="fas fa-gift"></i> General Discounts
        </h2>
        <div class="discounts-row">
          <DiscountCard
            v-for="discount in generalDiscounts"
            :key="discount.id"
            :discount="discount"
            @copy="copyCode"
          />
        </div>
      </div>

      <!-- Tab-specific views -->
      <div v-if="activeTab === 'stackable'" class="discounts-row">
        <DiscountCard
          v-for="discount in stackableDiscounts"
          :key="discount.id"
          :discount="discount"
          :is-stackable="true"
          @copy="copyCode"
        />
      </div>

      <div v-if="activeTab === 'personal'" class="discounts-row">
        <DiscountCard
          v-for="discount in personalDiscounts"
          :key="discount.id"
          :discount="discount"
          :is-personal="true"
          @copy="copyCode"
        />
      </div>

      <!-- Usage History -->
      <div v-if="activeTab === 'used'" class="usage-history">
        <div v-if="usageHistory.length === 0" class="empty-state">
          <i class="fas fa-history"></i>
          <p>No usage history yet.</p>
        </div>
        <div v-else class="history-list">
          <div
            v-for="usage in usageHistory"
            :key="usage.id"
            class="history-item"
          >
            <div class="history-code">
              <span class="code">{{ usage.discount_code }}</span>
              <span class="amount">-{{ formatDiscount(usage) }}</span>
            </div>
            <div class="history-details">
              <span class="order">Order #{{ usage.order_id }}</span>
              <span class="date">{{ formatDate(usage.used_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      class="toast"
      :class="toastSuccess ? 'toast-success' : 'toast-error'"
    >
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { discountsAPI } from '@/api'
import DiscountCard from '@/components/discounts/DiscountCard.vue'

const { showToast } = useToast()

// State
const loading = ref(false)
const activeTab = ref('all')
const discounts = ref([])
const usageHistory = ref([])

const filters = ref({
  search: '',
  discount_type: '',
  show_expired: false
})

const toastMessage = ref('')
const toastSuccess = ref(false)

const showToastMessage = (message, success) => {
  toastMessage.value = message
  toastSuccess.value = success
  setTimeout(() => {
    toastMessage.value = ''
  }, 3000)
}

// Computed
const availableDiscounts = computed(() => {
  return discounts.value.filter(d => !isExpired(d) && d.is_active)
})

const personalDiscounts = computed(() => {
  return availableDiscounts.value.filter(d => 
    d.assigned_to_client || d.assigned_to_users?.length > 0
  )
})

const stackableDiscounts = computed(() => {
  return availableDiscounts.value.filter(d => d.stackable)
})

const generalDiscounts = computed(() => {
  return availableDiscounts.value.filter(d => 
    !d.stackable && 
    !d.assigned_to_client && 
    (!d.assigned_to_users || d.assigned_to_users.length === 0)
  )
})

const filteredDiscounts = computed(() => {
  let filtered = []

  if (activeTab.value === 'stackable') {
    filtered = stackableDiscounts.value
  } else if (activeTab.value === 'personal') {
    filtered = personalDiscounts.value
  } else if (activeTab.value === 'all') {
    filtered = [...personalDiscounts.value, ...stackableDiscounts.value, ...generalDiscounts.value]
  } else {
    filtered = []
  }

  // Apply filters
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(d => 
      (d.code || d.discount_code || '').toLowerCase().includes(search) ||
      (d.description || '').toLowerCase().includes(search)
    )
  }

  if (filters.value.discount_type) {
    filtered = filtered.filter(d => d.discount_type === filters.value.discount_type)
  }

  if (!filters.value.show_expired) {
    filtered = filtered.filter(d => !isExpired(d))
  }

  return filtered
})

const availableCount = computed(() => availableDiscounts.value.length)
const stackableCount = computed(() => stackableDiscounts.value.length)
const personalCount = computed(() => personalDiscounts.value.length)

// Methods
const loadDiscounts = async () => {
  loading.value = true
  try {
    // Use the my_discounts endpoint for clients
    const response = await discountsAPI.myDiscounts()
    discounts.value = response.data.results || response.data || []
    
    // Load usage history
    await loadUsageHistory()
  } catch (error) {
    // Fallback to regular list if my_discounts endpoint doesn't exist
    try {
      const params = {
        is_active: true
      }
      const fallbackResponse = await discountsAPI.list(params)
      discounts.value = fallbackResponse.data.results || fallbackResponse.data || []
    } catch (fallbackError) {
      showToast('Failed to load discounts', 'error')
      console.error(error)
    }
  } finally {
    loading.value = false
  }
}

const loadUsageHistory = async () => {
  try {
    const response = await discountsAPI.listUsage({ user: 'me' })
    usageHistory.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load usage history', error)
  }
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    showToastMessage(`Discount code "${code}" copied to clipboard!`, true)
  }).catch(() => {
    showToastMessage('Failed to copy code', false)
  })
}

const isExpired = (discount) => {
  if (!discount.end_date && !discount.expiry_date) return false
  const expiry = discount.end_date || discount.expiry_date
  return new Date(expiry) < new Date()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDiscount = (usage) => {
  if (usage.discount_type === 'percent') {
    return `${usage.discount_value}%`
  }
  return `$${parseFloat(usage.discount_value || usage.amount || 0).toFixed(2)}`
}

const resetFilters = () => {
  filters.value = {
    search: '',
    discount_type: '',
    show_expired: false
  }
  loadDiscounts()
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // Filtering is handled by computed property
  }, 500)
}

// Lifecycle
onMounted(() => {
  loadDiscounts()
})
</script>

<style scoped>
.my-discounts {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 600;
}

.subtitle {
  color: #6b7280;
  margin: 0;
}

.stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  min-width: 80px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #3b82f6;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.2s;
  position: relative;
}

.tab:hover {
  color: #374151;
}

.tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab .badge {
  margin-left: 0.5rem;
  padding: 0.125rem 0.5rem;
  background: #3b82f6;
  color: white;
  border-radius: 0.75rem;
  font-size: 0.75rem;
}

.filters {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  font-size: 0.875rem;
  white-space: nowrap;
}

.filter-group input[type="text"],
.filter-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  min-width: 200px;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.section {
  margin-bottom: 2rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.info-tooltip {
  color: #6b7280;
  cursor: help;
  font-size: 0.875rem;
}

.stackable-info {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  color: #1e40af;
  font-size: 0.875rem;
}

.stackable-info i {
  margin-right: 0.5rem;
}

.discounts-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.usage-history {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.history-code {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.history-code .code {
  font-family: monospace;
  font-weight: 600;
  color: #3b82f6;
  font-size: 1.125rem;
}

.history-code .amount {
  font-weight: 600;
  color: #10b981;
  font-size: 1rem;
}

.history-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.toast-success {
  background: #10b981;
  color: white;
}

.toast-error {
  background: #ef4444;
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>

