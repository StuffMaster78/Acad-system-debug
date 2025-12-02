<template>
  <div class="template-preview">
    <div class="preview-header">
      <h3>{{ template.name }}</h3>
      <div v-if="template.description" class="description">
        {{ template.description }}
      </div>
    </div>

    <div class="preview-content">
      <div class="section">
        <h4>Order Details</h4>
        <div class="details-grid">
          <div class="detail-item">
            <span class="label">Topic:</span>
            <span class="value">{{ template.topic }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Paper Type:</span>
            <span class="value">{{ template.paper_type_name || 'Not specified' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Academic Level:</span>
            <span class="value">{{ template.academic_level_name || 'Not specified' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Subject:</span>
            <span class="value">{{ template.subject_name || 'Not specified' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Number of Pages:</span>
            <span class="value">{{ template.number_of_pages }}</span>
          </div>
          <div v-if="template.preferred_deadline_days" class="detail-item">
            <span class="label">Default Deadline:</span>
            <span class="value">{{ template.preferred_deadline_days }} days from now</span>
          </div>
        </div>
      </div>

      <div class="section">
        <h4>Instructions</h4>
        <div class="instructions">
          {{ template.order_instructions || 'No instructions provided' }}
        </div>
      </div>

      <div v-if="template.additional_services && template.additional_services.length > 0" class="section">
        <h4>Additional Services</h4>
        <div class="services-list">
          <span
            v-for="service in template.additional_services"
            :key="service"
            class="service-tag"
          >
            {{ service }}
          </span>
        </div>
      </div>

      <div class="section">
        <h4>Usage Statistics</h4>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-label">Times Used:</span>
            <span class="stat-value">{{ template.usage_count || 0 }}</span>
          </div>
          <div v-if="template.last_used_at" class="stat-item">
            <span class="stat-label">Last Used:</span>
            <span class="stat-value">{{ formatDate(template.last_used_at) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Created:</span>
            <span class="stat-value">{{ formatDate(template.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="preview-actions">
      <button @click="$emit('close')" class="btn-secondary">
        Close
      </button>
      <button @click="handleUse" class="btn-primary">
        <i class="fas fa-check"></i> Use This Template
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  template: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['use', 'close'])

const handleUse = () => {
  emit('use', props.template)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.template-preview {
  padding: 1rem;
}

.preview-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.preview-header h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.description {
  color: #6b7280;
  font-size: 0.875rem;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.section h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item .label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.detail-item .value {
  font-size: 0.875rem;
  color: #111827;
}

.instructions {
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  white-space: pre-wrap;
  color: #374151;
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
}

.services-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.service-tag {
  padding: 0.5rem 1rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.preview-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary,
.btn-primary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}
</style>

