<template>
  <div
    class="discount-card"
    :class="{
      'card-personal': isPersonal,
      'card-stackable': isStackable,
      'card-expired': isExpired,
      'card-inactive': !discount.is_active
    }"
  >
    <!-- Header -->
    <div class="card-header">
      <div class="code-section">
        <div class="code-display">
          <span class="code">{{ discount.code || discount.discount_code }}</span>
          <button
            @click="$emit('copy', discount.code || discount.discount_code)"
            class="copy-btn"
            title="Copy code"
          >
            <i class="fas fa-copy"></i>
          </button>
        </div>
        <div class="badges">
          <span v-if="isPersonal" class="badge badge-personal">
            <i class="fas fa-star"></i> Personal
          </span>
          <span v-if="isStackable" class="badge badge-stackable">
            <i class="fas fa-layer-group"></i> Stackable
          </span>
          <span
            :class="discount.discount_type === 'percent' ? 'badge badge-percent' : 'badge badge-fixed'"
          >
            {{ discount.discount_type === 'percent' ? 'Percentage' : 'Fixed' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Discount Value -->
    <div class="discount-value">
      <span v-if="discount.discount_type === 'percent'">
        {{ discount.value || discount.discount_value }}% OFF
      </span>
      <span v-else>
        ${{ parseFloat(discount.value || discount.discount_value || 0).toFixed(2) }} OFF
      </span>
    </div>

    <!-- Description -->
    <div v-if="discount.description" class="description">
      {{ discount.description }}
    </div>

    <!-- Details -->
    <div class="details">
      <div v-if="discount.min_order_value" class="detail-item">
        <i class="fas fa-shopping-cart"></i>
        <span>Min order: ${{ parseFloat(discount.min_order_value).toFixed(2) }}</span>
      </div>
      <div v-if="discount.end_date || discount.expiry_date" class="detail-item">
        <i class="fas fa-clock"></i>
        <span>Expires: {{ formatDate(discount.end_date || discount.expiry_date) }}</span>
      </div>
      <div v-if="discount.usage_limit || discount.max_uses" class="detail-item">
        <i class="fas fa-chart-bar"></i>
        <span>
          {{ discount.used_count || 0 }} / {{ discount.usage_limit || discount.max_uses }} uses
        </span>
      </div>
      <div v-if="discount.applies_to_first_order_only" class="detail-item highlight">
        <i class="fas fa-gift"></i>
        <span>First order only</span>
      </div>
      <div v-if="discount.promotional_campaign_name" class="detail-item">
        <i class="fas fa-bullhorn"></i>
        <span>{{ discount.promotional_campaign_name }}</span>
      </div>
    </div>

    <!-- Stackable Info -->
    <div v-if="isStackable" class="stackable-info">
      <i class="fas fa-info-circle"></i>
      <span>Can be combined with other stackable discounts</span>
    </div>

    <!-- Status -->
    <div class="card-footer">
      <span :class="getStatusClass()" class="status-badge">
        {{ getStatusText() }}
      </span>
      <button
        @click="$emit('copy', discount.code || discount.discount_code)"
        class="btn-copy"
      >
        <i class="fas fa-copy"></i> Copy Code
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  discount: {
    type: Object,
    required: true
  },
  isPersonal: {
    type: Boolean,
    default: false
  },
  isStackable: {
    type: Boolean,
    default: false
  }
})

defineEmits(['copy'])

const isExpired = computed(() => {
  if (!props.discount.end_date && !props.discount.expiry_date) return false
  const expiry = props.discount.end_date || props.discount.expiry_date
  return new Date(expiry) < new Date()
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const getStatusClass = () => {
  if (isExpired.value) return 'status-expired'
  if (!props.discount.is_active) return 'status-inactive'
  return 'status-active'
}

const getStatusText = () => {
  if (isExpired.value) return 'Expired'
  if (!props.discount.is_active) return 'Inactive'
  return 'Active'
}
</script>

<style scoped>
.discount-card {
  background: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.discount-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-personal {
  border-color: #fbbf24;
  background: linear-gradient(to bottom, #fffbeb 0%, #ffffff 20%);
}

.card-stackable {
  border-color: #3b82f6;
  background: linear-gradient(to bottom, #eff6ff 0%, #ffffff 20%);
}

.card-expired {
  opacity: 0.6;
  border-color: #d1d5db;
}

.card-inactive {
  opacity: 0.7;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.code-section {
  flex: 1;
}

.code-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.code {
  font-family: 'Courier New', monospace;
  font-size: 1.5rem;
  font-weight: 700;
  color: #3b82f6;
  letter-spacing: 0.05em;
}

.copy-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: #f3f4f6;
  color: #3b82f6;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.badge-personal {
  background: #fef3c7;
  color: #92400e;
}

.badge-stackable {
  background: #dbeafe;
  color: #1e40af;
}

.badge-percent {
  background: #dbeafe;
  color: #1e40af;
}

.badge-fixed {
  background: #e9d5ff;
  color: #6b21a8;
}

.discount-value {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0.5rem 0;
}

.description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #4b5563;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.detail-item i {
  width: 16px;
  color: #6b7280;
}

.detail-item.highlight {
  color: #f59e0b;
  font-weight: 500;
}

.stackable-info {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.375rem;
  padding: 0.75rem;
  font-size: 0.875rem;
  color: #1e40af;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  margin-top: auto;
}

.status-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
}

.status-inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-expired {
  background: #f3f4f6;
  color: #4b5563;
}

.btn-copy {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-copy:hover {
  background: #2563eb;
}
</style>

