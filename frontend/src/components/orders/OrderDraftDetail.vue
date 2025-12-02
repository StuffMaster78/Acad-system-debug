<template>
  <div class="order-draft-detail">
    <div class="detail-header">
      <div>
        <h2>{{ draft.title || 'Untitled Draft' }}</h2>
        <span :class="['status-badge', `status-${draft.status}`]">
          {{ draft.status }}
        </span>
      </div>
    </div>

    <div class="detail-info">
      <div class="info-grid">
        <div class="info-item">
          <label>Order Type:</label>
          <span>{{ formatOrderType(draft.order_type) }}</span>
        </div>
        <div class="info-item">
          <label>Academic Level:</label>
          <span>{{ formatAcademicLevel(draft.academic_level) }}</span>
        </div>
        <div class="info-item">
          <label>Pages:</label>
          <span>{{ draft.pages }}</span>
        </div>
        <div class="info-item">
          <label>Deadline:</label>
          <span>{{ formatDate(draft.deadline) || 'Not set' }}</span>
        </div>
        <div v-if="draft.subject" class="info-item">
          <label>Subject:</label>
          <span>{{ draft.subject }}</span>
        </div>
        <div v-if="draft.citation_style" class="info-item">
          <label>Citation Style:</label>
          <span>{{ draft.citation_style }}</span>
        </div>
        <div v-if="draft.sources_required" class="info-item">
          <label>Sources Required:</label>
          <span>{{ draft.sources_required }}</span>
        </div>
        <div v-if="draft.estimated_price" class="info-item">
          <label>Estimated Price:</label>
          <span class="price">${{ formatCurrency(draft.estimated_price) }}</span>
        </div>
      </div>
    </div>

    <div v-if="draft.instructions" class="instructions-section">
      <h3>Instructions</h3>
      <div class="instructions-content">
        {{ draft.instructions }}
      </div>
    </div>

    <div class="features-section">
      <h3>Features</h3>
      <div class="features-list">
        <span v-if="draft.requires_plagiarism_report" class="feature-tag">
          <i class="fas fa-check"></i> Plagiarism Report
        </span>
        <span v-if="draft.requires_progress_updates" class="feature-tag">
          <i class="fas fa-check"></i> Progress Updates
        </span>
      </div>
    </div>

    <div class="actions">
      <button @click="$emit('edit')" class="btn btn-primary">
        <i class="fas fa-edit"></i> Edit
      </button>
      <button 
        v-if="draft.status === 'draft'"
        @click="handleGetQuote"
        class="btn btn-success"
        :disabled="gettingQuote"
      >
        <i class="fas fa-calculator"></i> Get Quote
      </button>
      <button 
        v-if="draft.status === 'quoted'"
        @click="handleConvert"
        class="btn btn-success"
        :disabled="converting"
      >
        <i class="fas fa-check"></i> Convert to Order
      </button>
      <button @click="$emit('close')" class="btn btn-secondary">
        Close
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  draft: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'get-quote', 'convert', 'close'])

const gettingQuote = ref(false)
const converting = ref(false)

const formatOrderType = (type) => {
  const types = {
    'essay': 'Essay',
    'research_paper': 'Research Paper',
    'dissertation': 'Dissertation',
    'thesis': 'Thesis',
    'case_study': 'Case Study',
    'book_report': 'Book Report',
    'article': 'Article',
    'other': 'Other'
  }
  return types[type] || type
}

const formatAcademicLevel = (level) => {
  const levels = {
    'high_school': 'High School',
    'undergraduate': 'Undergraduate',
    'masters': 'Masters',
    'phd': 'PhD'
  }
  return levels[level] || level
}

const formatDate = (date) => {
  if (!date) return null
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const handleGetQuote = () => {
  emit('get-quote', props.draft)
}

const handleConvert = () => {
  emit('convert', props.draft)
}
</script>

<style scoped>
.order-draft-detail {
  padding: 1rem;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.detail-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
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

.detail-info {
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-weight: 500;
  font-size: 0.875rem;
  color: #6b7280;
}

.info-item span {
  font-size: 1rem;
  color: #111827;
}

.info-item .price {
  font-weight: 600;
  color: #10b981;
}

.instructions-section,
.features-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.instructions-section h3,
.features-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.instructions-content {
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  white-space: pre-wrap;
  color: #374151;
}

.features-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.feature-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #d1fae5;
  color: #065f46;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}
</style>

