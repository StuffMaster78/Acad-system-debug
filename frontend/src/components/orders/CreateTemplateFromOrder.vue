<template>
  <div class="create-template-from-order">
    <button
      @click="showModal = true"
      class="btn-create-template"
      :disabled="!order"
    >
      <i class="fas fa-save"></i> Save as Template
    </button>

    <Modal
      v-if="showModal"
      :show="showModal"
      @close="closeModal"
      title="Create Template from Order"
      size="medium"
    >
      <form @submit.prevent="saveTemplate" class="template-form">
        <FormField
          label="Template Name *"
          :error="errors.name"
        >
          <input
            v-model="formData.name"
            type="text"
            placeholder="e.g., Standard Essay Template"
            required
          />
        </FormField>

        <FormField
          label="Description"
          :error="errors.description"
        >
          <textarea
            v-model="formData.description"
            rows="2"
            placeholder="Optional description for this template"
          />
        </FormField>

        <div class="order-preview">
          <h4>Template will include:</h4>
          <div class="preview-items">
            <div class="preview-item">
              <span class="label">Topic:</span>
              <span class="value">{{ order?.topic || 'N/A' }}</span>
            </div>
            <div class="preview-item">
              <span class="label">Paper Type:</span>
              <span class="value">{{ getPaperTypeName(order?.paper_type_id) || 'N/A' }}</span>
            </div>
            <div class="preview-item">
              <span class="label">Academic Level:</span>
              <span class="value">{{ getAcademicLevelName(order?.academic_level_id) || 'N/A' }}</span>
            </div>
            <div class="preview-item">
              <span class="label">Subject:</span>
              <span class="value">{{ getSubjectName(order?.subject_id) || 'N/A' }}</span>
            </div>
            <div class="preview-item">
              <span class="label">Pages:</span>
              <span class="value">{{ order?.number_of_pages || 0 }}</span>
            </div>
          </div>
        </div>

        <FormField
          label="Default Deadline (days from now)"
          :error="errors.preferred_deadline_days"
        >
          <input
            v-model.number="formData.preferred_deadline_days"
            type="number"
            min="1"
            max="365"
            placeholder="e.g., 7"
          />
          <small>Leave empty to not set a default deadline</small>
        </FormField>

        <div class="form-actions">
          <button
            type="button"
            @click="closeModal"
            class="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="saving"
          >
            {{ saving ? 'Creating...' : 'Create Template' }}
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useToast } from '@/composables/useToast'
import { orderTemplatesAPI } from '@/api'
import orderConfigsAPI from '@/api/orderConfigs'
import Modal from '@/components/common/Modal.vue'
import FormField from '@/components/common/FormField.vue'

const props = defineProps({
  order: {
    type: Object,
    required: true
  },
  paperTypes: {
    type: Array,
    default: () => []
  },
  academicLevels: {
    type: Array,
    default: () => []
  },
  subjects: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['template-created'])

const { showToast } = useToast()

const showModal = ref(false)
const saving = ref(false)
const errors = ref({})

const formData = reactive({
  name: '',
  description: '',
  preferred_deadline_days: null
})

const getPaperTypeName = (id) => {
  if (!id) return null
  const type = props.paperTypes.find(t => t.id === id)
  return type?.name || null
}

const getAcademicLevelName = (id) => {
  if (!id) return null
  const level = props.academicLevels.find(l => l.id === id)
  return level?.name || null
}

const getSubjectName = (id) => {
  if (!id) return null
  const subject = props.subjects.find(s => s.id === id)
  return subject?.name || null
}

const saveTemplate = async () => {
  errors.value = {}
  
  if (!formData.name.trim()) {
    errors.value.name = 'Template name is required'
    return
  }
  
  saving.value = true
  try {
    const templateData = {
      name: formData.name,
      description: formData.description || '',
      topic: props.order.topic,
      paper_type: props.order.paper_type_id,
      academic_level: props.order.academic_level_id,
      subject: props.order.subject_id,
      number_of_pages: props.order.number_of_pages,
      order_instructions: props.order.order_instructions || '',
      preferred_deadline_days: formData.preferred_deadline_days || null,
      preferred_writer_id: props.order.preferred_writer_id || null
    }
    
    await orderTemplatesAPI.create(templateData)
    showToast('Template created successfully!', 'success')
    closeModal()
    emit('template-created')
  } catch (error) {
    if (error.response?.data) {
      errors.value = error.response.data
    }
    showToast('Failed to create template', 'error')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  formData.name = ''
  formData.description = ''
  formData.preferred_deadline_days = null
  errors.value = {}
}
</script>

<style scoped>
.create-template-from-order {
  display: inline-block;
}

.btn-create-template {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-create-template:hover:not(:disabled) {
  background: #2563eb;
}

.btn-create-template:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.template-form {
  padding: 1rem;
}

.order-preview {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.order-preview h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.preview-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.preview-item .label {
  font-weight: 500;
  color: #6b7280;
  min-width: 120px;
}

.preview-item .value {
  color: #111827;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}
</style>

