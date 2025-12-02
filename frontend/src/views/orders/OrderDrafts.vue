<template>
  <div class="order-drafts">
    <div class="header">
      <h1>Order Drafts</h1>
      <div class="actions">
        <button 
          @click="showCreateModal = true"
          class="btn btn-primary"
        >
          <i class="fas fa-plus"></i> Create Draft
        </button>
        <button 
          @click="loadDrafts"
          class="btn btn-secondary"
          :disabled="loading"
        >
          <i class="fas fa-sync-alt"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Status:</label>
        <select v-model="filters.status" @change="loadDrafts">
          <option value="">All</option>
          <option value="draft">Draft</option>
          <option value="quoted">Quoted</option>
          <option value="converted">Converted</option>
        </select>
      </div>
      <div class="filter-group">
        <label>
          <input 
            type="checkbox" 
            v-model="filters.saved_only"
            @change="loadDrafts"
          />
          Saved Only
        </label>
      </div>
    </div>

    <!-- Drafts List -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> Loading drafts...
    </div>

    <div v-else-if="drafts.length === 0" class="empty-state">
      <i class="fas fa-file-alt"></i>
      <p>No drafts found. Create your first draft to get started.</p>
      <button @click="showCreateModal = true" class="btn btn-primary">
        Create Draft
      </button>
    </div>

    <div v-else class="drafts-grid">
      <div 
        v-for="draft in drafts" 
        :key="draft.id"
        class="draft-card"
        @click="viewDraft(draft)"
      >
        <div class="draft-header">
          <h3>{{ draft.title || 'Untitled Draft' }}</h3>
          <span :class="['status-badge', `status-${draft.status}`]">
            {{ draft.status }}
          </span>
        </div>
        <div class="draft-info">
          <div class="info-item">
            <label>Type:</label>
            <span>{{ draft.order_type || 'Standard' }}</span>
          </div>
          <div class="info-item">
            <label>Pages:</label>
            <span>{{ draft.pages || 0 }}</span>
          </div>
          <div class="info-item">
            <label>Deadline:</label>
            <span>{{ formatDate(draft.deadline) || 'Not set' }}</span>
          </div>
          <div v-if="draft.estimated_price" class="info-item">
            <label>Estimated Price:</label>
            <span class="price">${{ formatCurrency(draft.estimated_price) }}</span>
          </div>
        </div>
        <div class="draft-actions">
          <button 
            @click.stop="editDraft(draft)"
            class="btn btn-sm btn-secondary"
          >
            <i class="fas fa-edit"></i> Edit
          </button>
          <button 
            v-if="draft.status === 'draft'"
            @click.stop="getQuote(draft)"
            class="btn btn-sm btn-primary"
            :disabled="gettingQuote === draft.id"
          >
            <i class="fas fa-calculator"></i> Get Quote
          </button>
          <button 
            v-if="draft.status === 'quoted'"
            @click.stop="convertToOrder(draft)"
            class="btn btn-sm btn-success"
            :disabled="converting === draft.id"
          >
            <i class="fas fa-check"></i> Convert to Order
          </button>
          <button 
            @click.stop="deleteDraft(draft)"
            class="btn btn-sm btn-danger"
            :disabled="deleting === draft.id"
          >
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Draft Modal -->
    <Modal
      v-if="showCreateModal || editingDraft"
      :show="showCreateModal || !!editingDraft"
      @close="closeModal"
      :title="editingDraft ? 'Edit Draft' : 'Create Draft'"
      size="large"
    >
      <OrderDraftForm
        :draft="editingDraft"
        @save="handleSaveDraft"
        @cancel="closeModal"
      />
    </Modal>

    <!-- Draft Detail Modal -->
    <Modal
      v-if="selectedDraft"
      :show="!!selectedDraft"
      @close="selectedDraft = null"
      :title="selectedDraft?.title || 'Draft Details'"
      size="large"
    >
      <OrderDraftDetail
        :draft="selectedDraft"
        @edit="editDraft"
        @get-quote="getQuote"
        @convert="convertToOrder"
        @close="selectedDraft = null"
      />
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { orderDraftsAPI } from '@/api'
import Modal from '@/components/common/Modal.vue'
import OrderDraftForm from '@/components/orders/OrderDraftForm.vue'
import OrderDraftDetail from '@/components/orders/OrderDraftDetail.vue'

const { showToast } = useToast()

// State
const loading = ref(false)
const showCreateModal = ref(false)
const editingDraft = ref(null)
const selectedDraft = ref(null)
const gettingQuote = ref(null)
const converting = ref(null)
const deleting = ref(null)

const drafts = ref([])

const filters = ref({
  status: '',
  saved_only: false
})

// Methods
const loadDrafts = async () => {
  loading.value = true
  try {
    const params = {
      ...filters.value,
      saved_only: filters.value.saved_only ? 'true' : undefined
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const response = await orderDraftsAPI.list(params)
    drafts.value = response.data
  } catch (error) {
    showToast('Failed to load drafts', 'error')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const viewDraft = (draft) => {
  selectedDraft.value = draft
}

const editDraft = (draft) => {
  editingDraft.value = draft
  selectedDraft.value = null
}

const getQuote = async (draft) => {
  gettingQuote.value = draft.id
  try {
    const response = await orderDraftsAPI.getQuote(draft.id)
    showToast(`Quote generated: $${parseFloat(response.data.estimated_price).toFixed(2)}`, 'success')
    await loadDrafts()
    if (selectedDraft.value?.id === draft.id) {
      // Reload the draft to get updated estimated_price
      const updatedDraft = await orderDraftsAPI.get(draft.id)
      selectedDraft.value = updatedDraft.data
    }
  } catch (error) {
    showToast(error.response?.data?.error || 'Failed to get quote', 'error')
    console.error(error)
  } finally {
    gettingQuote.value = null
  }
}

const convertToOrder = async (draft) => {
  if (!confirm('Are you sure you want to convert this draft to an order?')) {
    return
  }
  
  converting.value = draft.id
  try {
    const response = await orderDraftsAPI.convertToOrder(draft.id)
    showToast('Draft converted to order successfully', 'success')
    await loadDrafts()
    // Navigate to the new order
    if (response.data.order_id) {
      window.location.href = `/orders/${response.data.order_id}`
    }
  } catch (error) {
    showToast('Failed to convert draft', 'error')
    console.error(error)
  } finally {
    converting.value = null
  }
}

const deleteDraft = async (draft) => {
  if (!confirm('Are you sure you want to delete this draft?')) {
    return
  }
  
  deleting.value = draft.id
  try {
    await orderDraftsAPI.delete(draft.id)
    showToast('Draft deleted successfully', 'success')
    await loadDrafts()
  } catch (error) {
    showToast('Failed to delete draft', 'error')
    console.error(error)
  } finally {
    deleting.value = null
  }
}

const handleSaveDraft = async (data) => {
  try {
    if (editingDraft.value) {
      await orderDraftsAPI.update(editingDraft.value.id, data)
      showToast('Draft updated successfully', 'success')
    } else {
      await orderDraftsAPI.create(data)
      showToast('Draft created successfully', 'success')
    }
    closeModal()
    await loadDrafts()
  } catch (error) {
    showToast('Failed to save draft', 'error')
    console.error(error)
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingDraft.value = null
}

const formatDate = (date) => {
  if (!date) return null
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

// Lifecycle
onMounted(() => {
  loadDrafts()
})
</script>

<style scoped>
.order-drafts {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 0.75rem;
}

.filters {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  font-size: 0.875rem;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
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

.drafts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.draft-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.draft-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.draft-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.draft-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  flex: 1;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-draft { background: #d1d5db; color: #374151; }
.status-quoted { background: #dbeafe; color: #1e40af; }
.status-converted { background: #d1fae5; color: #065f46; }

.draft-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.info-item span {
  font-size: 0.875rem;
  color: #111827;
}

.info-item .price {
  font-weight: 600;
  color: #10b981;
}

.draft-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}
</style>

