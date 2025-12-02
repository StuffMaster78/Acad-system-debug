<template>
  <div class="template-selector">
    <div class="selector-header">
      <h3>Start from a Template</h3>
      <p class="subtitle">Save time by using a saved template</p>
      <button
        v-if="!showTemplates"
        @click="showTemplates = true"
        class="btn-toggle"
      >
        <i class="fas fa-chevron-down"></i> Browse Templates
      </button>
      <button
        v-else
        @click="showTemplates = false"
        class="btn-toggle"
      >
        <i class="fas fa-chevron-up"></i> Hide Templates
      </button>
    </div>

    <div v-if="showTemplates" class="templates-section">
      <!-- Quick Filters -->
      <div class="quick-filters">
        <button
          v-for="filter in quickFilters"
          :key="filter.key"
          @click="activeFilter = filter.key"
          :class="['filter-btn', { active: activeFilter === filter.key }]"
        >
          {{ filter.label }}
          <span v-if="filter.count" class="count">{{ filter.count }}</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i> Loading templates...
      </div>

      <!-- Templates Grid -->
      <div v-else-if="filteredTemplates.length > 0" class="templates-grid">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
          :class="{ selected: selectedTemplate?.id === template.id }"
          @click="selectTemplate(template)"
        >
          <div class="card-header">
            <h4>{{ template.name }}</h4>
            <div class="badges">
              <span v-if="template.usage_count > 0" class="badge usage">
                Used {{ template.usage_count }}x
              </span>
              <span v-if="template.last_used_at" class="badge recent">
                Recent
              </span>
            </div>
          </div>
          <div class="card-body">
            <div class="template-preview">
              <div class="preview-item">
                <span class="label">Topic:</span>
                <span class="value">{{ truncate(template.topic, 50) }}</span>
              </div>
              <div class="preview-item">
                <span class="label">Type:</span>
                <span class="value">{{ template.paper_type_name || 'N/A' }}</span>
              </div>
              <div class="preview-item">
                <span class="label">Level:</span>
                <span class="value">{{ template.academic_level_name || 'N/A' }}</span>
              </div>
              <div class="preview-item">
                <span class="label">Pages:</span>
                <span class="value">{{ template.number_of_pages }}</span>
              </div>
            </div>
            <div v-if="template.description" class="description">
              {{ truncate(template.description, 100) }}
            </div>
          </div>
          <div class="card-footer">
            <button
              @click.stop="previewTemplate(template)"
              class="btn-preview"
            >
              <i class="fas fa-eye"></i> Preview
            </button>
            <button
              @click.stop="selectTemplate(template)"
              class="btn-select"
            >
              <i class="fas fa-check"></i> Use Template
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <i class="fas fa-file-alt"></i>
        <p>No templates found</p>
        <button @click="$emit('create-template')" class="btn-create">
          Create Your First Template
        </button>
      </div>
    </div>

    <!-- Selected Template Summary -->
    <div v-if="selectedTemplate" class="selected-template">
      <div class="summary-header">
        <h4>Selected Template: {{ selectedTemplate.name }}</h4>
        <button @click="clearSelection" class="btn-clear">
          <i class="fas fa-times"></i> Clear
        </button>
      </div>
      <div class="summary-content">
        <div class="summary-item">
          <span class="label">Topic:</span>
          <span class="value">{{ selectedTemplate.topic }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Type:</span>
          <span class="value">{{ selectedTemplate.paper_type_name || 'N/A' }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Level:</span>
          <span class="value">{{ selectedTemplate.academic_level_name || 'N/A' }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Pages:</span>
          <span class="value">{{ selectedTemplate.number_of_pages }}</span>
        </div>
        <div v-if="selectedTemplate.preferred_deadline_days" class="summary-item">
          <span class="label">Default Deadline:</span>
          <span class="value">{{ selectedTemplate.preferred_deadline_days }} days</span>
        </div>
      </div>
      <div class="summary-actions">
        <button @click="previewTemplate(selectedTemplate)" class="btn-secondary">
          <i class="fas fa-eye"></i> Preview Details
        </button>
        <button @click="applyTemplate" class="btn-primary">
          <i class="fas fa-magic"></i> Apply to Form
        </button>
      </div>
    </div>

    <!-- Template Preview Modal -->
    <Modal
      v-if="previewingTemplate"
      :show="!!previewingTemplate"
      @close="previewingTemplate = null"
      title="Template Preview"
      size="large"
    >
      <TemplatePreview
        :template="previewingTemplate"
        @use="selectTemplate"
        @close="previewingTemplate = null"
      />
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { orderTemplatesAPI } from '@/api'
import Modal from '@/components/common/Modal.vue'
import TemplatePreview from '@/components/orders/TemplatePreview.vue'

const props = defineProps({
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['template-selected', 'create-template'])

// State
const loading = ref(false)
const showTemplates = ref(false)
const templates = ref([])
const selectedTemplate = ref(null)
const previewingTemplate = ref(null)
const activeFilter = ref('all')

// Quick filters
const quickFilters = computed(() => {
  const mostUsed = templates.value.filter(t => t.usage_count > 0).length
  const recent = templates.value.filter(t => t.last_used_at).length
  
  return [
    { key: 'all', label: 'All', count: templates.value.length },
    { key: 'most-used', label: 'Most Used', count: mostUsed },
    { key: 'recent', label: 'Recent', count: recent }
  ]
})

// Filtered templates
const filteredTemplates = computed(() => {
  let filtered = templates.value

  if (activeFilter.value === 'most-used') {
    filtered = filtered.filter(t => t.usage_count > 0)
      .sort((a, b) => b.usage_count - a.usage_count)
  } else if (activeFilter.value === 'recent') {
    filtered = filtered.filter(t => t.last_used_at)
      .sort((a, b) => new Date(b.last_used_at) - new Date(a.last_used_at))
  }

  return filtered
})

// Methods
const loadTemplates = async () => {
  loading.value = true
  try {
    const response = await orderTemplatesAPI.list()
    templates.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load templates', error)
  } finally {
    loading.value = false
  }
}

const selectTemplate = (template) => {
  selectedTemplate.value = template
  emit('template-selected', template)
}

const clearSelection = () => {
  selectedTemplate.value = null
  emit('template-selected', null)
}

const previewTemplate = (template) => {
  previewingTemplate.value = template
}

const applyTemplate = () => {
  if (selectedTemplate.value) {
    emit('template-selected', selectedTemplate.value)
  }
}

const truncate = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

// Watch for template selection changes
watch(selectedTemplate, (newTemplate) => {
  if (newTemplate) {
    showTemplates.value = false
  }
})

// Lifecycle
onMounted(() => {
  if (props.autoLoad) {
    loadTemplates()
  }
})

// Expose methods
defineExpose({
  loadTemplates,
  clearSelection
})
</script>

<style scoped>
.template-selector {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.selector-header h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.subtitle {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.btn-toggle {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
  transition: all 0.2s;
}

.btn-toggle:hover {
  background: #e5e7eb;
}

.templates-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.quick-filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #6b7280;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-btn:hover {
  background: #f3f4f6;
}

.filter-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.filter-btn .count {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
}

.loading-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.template-card {
  background: #ffffff;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.template-card.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.card-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.badges {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge.usage {
  background: #dbeafe;
  color: #1e40af;
}

.badge.recent {
  background: #d1fae5;
  color: #065f46;
}

.card-body {
  margin-bottom: 1rem;
}

.template-preview {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #4b5563;
}

.preview-item {
  display: flex;
  gap: 0.5rem;
}

.preview-item .label {
  font-weight: 500;
  color: #6b7280;
  min-width: 60px;
}

.preview-item .value {
  color: #111827;
}

.description {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
  font-size: 0.875rem;
  color: #6b7280;
  font-style: italic;
}

.card-footer {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.btn-preview,
.btn-select {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-preview {
  background: #f3f4f6;
  color: #374151;
}

.btn-preview:hover {
  background: #e5e7eb;
}

.btn-select {
  background: #3b82f6;
  color: white;
}

.btn-select:hover {
  background: #2563eb;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.btn-create {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.btn-create:hover {
  background: #2563eb;
}

.selected-template {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: #eff6ff;
  border: 2px solid #3b82f6;
  border-radius: 0.5rem;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.summary-header h4 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e40af;
}

.btn-clear {
  padding: 0.375rem 0.75rem;
  background: #ffffff;
  border: 1px solid #3b82f6;
  border-radius: 0.375rem;
  color: #3b82f6;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-clear:hover {
  background: #dbeafe;
}

.summary-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.summary-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.summary-item .label {
  font-weight: 500;
  color: #6b7280;
}

.summary-item .value {
  color: #111827;
}

.summary-actions {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #bfdbfe;
}

.btn-secondary,
.btn-primary {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-secondary {
  background: #ffffff;
  color: #3b82f6;
  border: 1px solid #3b82f6;
}

.btn-secondary:hover {
  background: #dbeafe;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}
</style>

