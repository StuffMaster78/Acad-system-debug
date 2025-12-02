<template>
  <form @submit.prevent="handleSubmit" class="order-draft-form">
    <FormField
      label="Title"
      :error="errors.title"
    >
      <input
        v-model="formData.title"
        type="text"
        placeholder="e.g., Research Paper on Climate Change"
      />
    </FormField>

    <div class="form-row">
      <FormField
        label="Order Type *"
        :error="errors.order_type"
      >
        <select v-model="formData.order_type" required>
          <option value="essay">Essay</option>
          <option value="research_paper">Research Paper</option>
          <option value="dissertation">Dissertation</option>
          <option value="thesis">Thesis</option>
          <option value="case_study">Case Study</option>
          <option value="book_report">Book Report</option>
          <option value="article">Article</option>
          <option value="other">Other</option>
        </select>
      </FormField>

      <FormField
        label="Academic Level *"
        :error="errors.academic_level"
      >
        <select v-model="formData.academic_level" required>
          <option value="high_school">High School</option>
          <option value="undergraduate">Undergraduate</option>
          <option value="masters">Masters</option>
          <option value="phd">PhD</option>
        </select>
      </FormField>
    </div>

    <div class="form-row">
      <FormField
        label="Pages *"
        :error="errors.pages"
      >
        <input
          v-model.number="formData.pages"
          type="number"
          min="1"
          required
        />
      </FormField>

      <FormField
        label="Deadline"
        :error="errors.deadline"
      >
        <input
          v-model="formData.deadline"
          type="datetime-local"
        />
      </FormField>
    </div>

    <FormField
      label="Subject/Discipline"
      :error="errors.subject"
    >
      <input
        v-model="formData.subject"
        type="text"
        placeholder="e.g., Environmental Science"
      />
    </FormField>

    <FormField
      label="Instructions"
      :error="errors.instructions"
    >
      <textarea
        v-model="formData.instructions"
        rows="5"
        placeholder="Detailed instructions for the order..."
      />
    </FormField>

    <div class="form-row">
      <FormField
        label="Citation Style"
        :error="errors.citation_style"
      >
        <select v-model="formData.citation_style">
          <option value="">Select Style</option>
          <option value="APA">APA</option>
          <option value="MLA">MLA</option>
          <option value="Chicago">Chicago</option>
          <option value="Harvard">Harvard</option>
          <option value="IEEE">IEEE</option>
          <option value="Vancouver">Vancouver</option>
        </select>
      </FormField>

      <FormField
        label="Sources Required"
        :error="errors.sources_required"
      >
        <input
          v-model.number="formData.sources_required"
          type="number"
          min="0"
        />
      </FormField>
    </div>

    <div class="form-checkboxes">
      <label>
        <input
          type="checkbox"
          v-model="formData.is_saved"
        />
        Save as Draft
      </label>
      <label>
        <input
          type="checkbox"
          v-model="formData.requires_plagiarism_report"
        />
        Requires Plagiarism Report
      </label>
      <label>
        <input
          type="checkbox"
          v-model="formData.requires_progress_updates"
        />
        Requires Progress Updates
      </label>
    </div>

    <div class="form-actions">
      <button type="button" @click="$emit('cancel')" class="btn btn-secondary">
        Cancel
      </button>
      <button type="submit" class="btn btn-primary" :disabled="saving">
        {{ saving ? 'Saving...' : 'Save Draft' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue'
import FormField from '@/components/common/FormField.vue'

const props = defineProps({
  draft: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'cancel'])

const saving = ref(false)
const errors = ref({})

const formData = reactive({
  title: '',
  order_type: 'essay',
  academic_level: 'undergraduate',
  pages: 1,
  deadline: '',
  subject: '',
  instructions: '',
  citation_style: '',
  sources_required: 0,
  is_saved: true,
  requires_plagiarism_report: false,
  requires_progress_updates: false
})

// Initialize form if editing
if (props.draft) {
  Object.assign(formData, {
    title: props.draft.title || '',
    order_type: props.draft.order_type || 'essay',
    academic_level: props.draft.academic_level || 'undergraduate',
    pages: props.draft.pages || 1,
    deadline: props.draft.deadline ? new Date(props.draft.deadline).toISOString().slice(0, 16) : '',
    subject: props.draft.subject || '',
    instructions: props.draft.instructions || '',
    citation_style: props.draft.citation_style || '',
    sources_required: props.draft.sources_required || 0,
    is_saved: props.draft.is_saved ?? true,
    requires_plagiarism_report: props.draft.requires_plagiarism_report ?? false,
    requires_progress_updates: props.draft.requires_progress_updates ?? false
  })
}

const handleSubmit = () => {
  errors.value = {}
  
  // Validation
  if (!formData.order_type) {
    errors.value.order_type = 'Order type is required'
    return
  }
  
  if (!formData.academic_level) {
    errors.value.academic_level = 'Academic level is required'
    return
  }
  
  if (!formData.pages || formData.pages < 1) {
    errors.value.pages = 'Pages must be at least 1'
    return
  }
  
  saving.value = true
  emit('save', { ...formData })
  saving.value = false
}
</script>

<style scoped>
.order-draft-form {
  padding: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0;
}

.form-checkboxes label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
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

