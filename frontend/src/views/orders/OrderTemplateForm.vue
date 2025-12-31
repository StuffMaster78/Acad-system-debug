<template>
  <div class="order-template-form max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">
    <!-- Header Section -->
    <div class="mb-6">
      <button
        @click="goBack"
        class="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors mb-4 group"
      >
        <svg class="w-5 h-5 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="font-medium">Back to Templates</span>
      </button>
      
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {{ editingTemplate ? 'Edit Template' : 'Create Order Template' }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          {{ editingTemplate ? 'Update your order template settings' : 'Save and reuse your order configurations for quick reordering' }}
        </p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="mb-6 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 p-4 rounded-lg flex items-start gap-3">
      <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
      </svg>
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-12 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading template...</p>
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="saveTemplate" class="space-y-8">
      <!-- Template Information Section -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 sm:p-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
            <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Template Information</h2>
        </div>
        
        <div class="space-y-6">
          <!-- Template Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Template Name <span class="text-red-500">*</span>
            </label>
            <input
              id="field-name"
              v-model="formData.name"
              type="text"
              name="name"
              placeholder="e.g., Standard Essay Template, Research Paper Template"
              maxlength="100"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              :class="{ 'border-red-500 focus:ring-red-500': formErrors.name }"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Choose a descriptive name that helps you identify this template quickly ({{ formData.name.length }}/100 characters)
            </p>
            <div v-if="formErrors.name" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ formErrors.name }}
            </div>
          </div>
          
          <!-- Description -->
          <div>
            <label 
              for="field-description"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Description
            </label>
            <textarea
              id="field-description"
              v-model="formData.description"
              name="description"
              rows="4"
              placeholder="e.g., Use this template for standard 5-page essays with APA formatting"
              maxlength="500"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-y"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Optional: Add a brief description to help you remember when to use this template ({{ formData.description.length }}/500 characters)
            </p>
            <div v-if="formErrors.description" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ formErrors.description }}
            </div>
          </div>
        </div>
      </div>

      <!-- Order Details Section -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 sm:p-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Order Details</h2>
        </div>
        
        <div class="space-y-6">
          <!-- Topic/Title -->
          <div>
            <label 
              for="field-topic"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Topic/Title <span class="text-red-500">*</span>
            </label>
            <textarea
              id="field-topic"
              v-model="formData.topic"
              name="topic"
              rows="3"
              placeholder="e.g., Analysis of Climate Change Impacts"
              maxlength="200"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-y"
              :class="{ 'border-red-500 focus:ring-red-500': formErrors.topic }"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              The default topic for orders created from this template ({{ formData.topic.length }}/200 characters)
            </p>
            <div v-if="formErrors.topic" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ formErrors.topic }}
            </div>
          </div>
      
          <!-- Paper Type and Pages -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Paper Type
              </label>
              <select
                id="field-paper_type"
                v-model="formData.paper_type_id"
                name="paper_type"
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select paper type</option>
                <option v-for="pt in paperTypes" :key="pt.id" :value="pt.id">
                  {{ pt.name }}
                </option>
              </select>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Select the type of paper (e.g., Essay, Research Paper, Thesis)
              </p>
              <div v-if="formErrors.paper_type_id" class="mt-1 text-sm text-red-600 dark:text-red-400">
                {{ formErrors.paper_type_id }}
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Number of Pages <span class="text-red-500">*</span>
              </label>
              <input
                id="field-number_of_pages"
                v-model.number="formData.number_of_pages"
                type="number"
                name="number_of_pages"
                min="1"
                max="1000"
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                :class="{ 'border-red-500 focus:ring-red-500': formErrors.number_of_pages }"
              />
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Default number of pages for orders created from this template
              </p>
              <div v-if="formErrors.number_of_pages" class="mt-1 text-sm text-red-600 dark:text-red-400">
                {{ formErrors.number_of_pages }}
              </div>
            </div>
          </div>
          
          <!-- Academic Level and Subject -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Academic Level
              </label>
              <select
                id="field-academic_level"
                v-model="formData.academic_level_id"
                name="academic_level"
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select academic level</option>
                <option v-for="level in academicLevels" :key="level.id" :value="level.id">
                  {{ level.name }}
                </option>
              </select>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Select the academic level (e.g., High School, Undergraduate, Graduate)
              </p>
              <div v-if="formErrors.academic_level_id" class="mt-1 text-sm text-red-600 dark:text-red-400">
                {{ formErrors.academic_level_id }}
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Subject
              </label>
              <select
                id="field-subject"
                v-model="formData.subject_id"
                name="subject"
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select subject</option>
                <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                  {{ subject.name }}
                </option>
              </select>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Select the subject area for this template
              </p>
              <div v-if="formErrors.subject_id" class="mt-1 text-sm text-red-600 dark:text-red-400">
                {{ formErrors.subject_id }}
              </div>
            </div>
          </div>
          
          <!-- Preferred Deadline -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Preferred Deadline (days)
            </label>
            <input
              id="field-preferred_deadline_days"
              v-model.number="formData.preferred_deadline_days"
              type="number"
              name="preferred_deadline_days"
              min="1"
              placeholder="e.g., 7"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Default number of days from now for the deadline (optional)
            </p>
            <div v-if="formErrors.preferred_deadline_days" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ formErrors.preferred_deadline_days }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Instructions Section -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 sm:p-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
            <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Order Instructions</h2>
        </div>
        
        <div>
          <label 
            for="field-order_instructions"
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Detailed Instructions <span class="text-red-600">*</span>
          </label>
          <RichTextEditor
            v-model="formData.order_instructions"
            :required="true"
            placeholder="Enter detailed instructions for the writer...&#10;&#10;Example:&#10;- Use APA 7th edition formatting&#10;- Include at least 5 peer-reviewed sources&#10;- Focus on recent research (last 5 years)&#10;- Include an abstract and conclusion"
            toolbar="full"
            height="350px"
            :allow-images="true"
            :error="formErrors.order_instructions"
            help-text="Provide detailed instructions that will be used for all orders created from this template. Include specific requirements, formatting guidelines, and any other important details."
            :show-char-count="true"
          />
          <p v-if="!formErrors.order_instructions" class="mt-2 text-xs text-gray-500 dark:text-gray-400">
            The more detailed your instructions, the better the writer can meet your expectations
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-3">
          <button
            type="button"
            @click="goBack"
            class="px-6 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-all font-medium shadow-sm hover:shadow"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="saving || loading"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm hover:shadow-md flex items-center justify-center gap-2 min-w-[140px]"
          >
            <svg v-if="saving" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ saving ? 'Saving...' : (editingTemplate ? 'Update Template' : 'Create Template') }}</span>
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useFormValidation } from '@/composables/useFormValidation'
import { orderTemplatesAPI } from '@/api'
import orderConfigsAPI from '@/api/orderConfigs'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import { getErrorMessage } from '@/utils/errorHandler'

const router = useRouter()
const route = useRoute()
const { success, error: showError } = useToast()
const { errors: formErrors, setErrors, clearAllErrors, validateRequired, validateNumberRange } = useFormValidation()

const loading = ref(false)
const error = ref(null)
const saving = ref(false)
const editingTemplate = ref(null)

// Form data
const formData = ref({
  name: '',
  description: '',
  topic: '',
  paper_type_id: '',
  academic_level_id: '',
  subject_id: '',
  number_of_pages: 1,
  order_instructions: '',
  preferred_deadline_days: null,
})

// Options data
const paperTypes = ref([])
const academicLevels = ref([])
const subjects = ref([])

const loadTemplate = async () => {
  const templateId = route.params.id
  if (!templateId) return
  
  loading.value = true
  error.value = null
  try {
    const response = await orderTemplatesAPI.get(templateId)
    const template = response.data
    editingTemplate.value = template
    formData.value = {
      name: template.name,
      description: template.description || '',
      topic: template.topic,
      paper_type_id: template.paper_type || '',
      academic_level_id: template.academic_level || '',
      subject_id: template.subject || '',
      number_of_pages: template.number_of_pages,
      order_instructions: template.order_instructions,
      preferred_deadline_days: template.preferred_deadline_days,
    }
  } catch (err) {
    error.value = getErrorMessage(err, 'Failed to load template')
    showError(error.value)
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [paperTypesRes, academicLevelsRes, subjectsRes] = await Promise.all([
      orderConfigsAPI.getPaperTypes(),
      orderConfigsAPI.getAcademicLevels(),
      orderConfigsAPI.getSubjects()
    ])
    
    paperTypes.value = paperTypesRes.data?.results || paperTypesRes.data || []
    academicLevels.value = academicLevelsRes.data?.results || academicLevelsRes.data || []
    subjects.value = subjectsRes.data?.results || subjectsRes.data || []
  } catch (err) {
    console.error('Failed to load options:', err)
  }
}

const saveTemplate = async () => {
  clearAllErrors()
  
  // Validate required fields
  let hasErrors = false
  
  if (!formData.value.name || formData.value.name.trim() === '') {
    setErrors({ name: 'Template name is required' })
    hasErrors = true
  }
  
  if (!formData.value.topic || formData.value.topic.trim() === '') {
    setErrors({ topic: 'Topic is required' })
    hasErrors = true
  }
  
  // Check if order_instructions is empty (strip HTML tags for validation)
  const instructionsText = formData.value.order_instructions 
    ? formData.value.order_instructions.replace(/<[^>]*>/g, '').trim()
    : ''
  
  if (!instructionsText || instructionsText === '') {
    setErrors({ order_instructions: 'Order instructions are required' })
    hasErrors = true
  }
  
  if (!formData.value.number_of_pages || formData.value.number_of_pages < 1 || formData.value.number_of_pages > 1000) {
    setErrors({ number_of_pages: 'Number of pages must be between 1 and 1000' })
    hasErrors = true
  }
  
  if (hasErrors) {
    showError('Please fix the errors in the form')
    // Scroll to first error
    await nextTick()
    const firstError = document.querySelector('.border-red-500, [class*="error"]')
    if (firstError) {
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
      firstError.focus()
    }
    return
  }
  
  saving.value = true
  try {
    // Prepare data for submission
    const submitData = {
      name: formData.value.name.trim(),
      description: formData.value.description?.trim() || '',
      topic: formData.value.topic.trim(),
      paper_type_id: formData.value.paper_type_id || null,
      academic_level_id: formData.value.academic_level_id || null,
      subject_id: formData.value.subject_id || null,
      number_of_pages: parseInt(formData.value.number_of_pages),
      order_instructions: formData.value.order_instructions,
      preferred_deadline_days: formData.value.preferred_deadline_days ? parseInt(formData.value.preferred_deadline_days) : null,
    }
    
    if (editingTemplate.value) {
      await orderTemplatesAPI.update(editingTemplate.value.id, submitData)
      success('Template updated successfully')
    } else {
      await orderTemplatesAPI.create(submitData)
      success('Template created successfully')
    }
    
    // Small delay before navigation to show success message
    setTimeout(() => {
      router.push('/orders/templates')
    }, 500)
  } catch (err) {
    const errorData = err.response?.data || {}
    setErrors(errorData)
    
    // Handle field-specific errors
    if (errorData.non_field_errors) {
      showError(Array.isArray(errorData.non_field_errors) 
        ? errorData.non_field_errors.join(', ') 
        : errorData.non_field_errors)
    } else {
      showError(getErrorMessage(err, 'Failed to save template'))
    }
    
    // Scroll to first error
    await nextTick()
    const firstError = document.querySelector('.border-red-500, [class*="error"]')
    if (firstError) {
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.push('/orders/templates')
}

onMounted(async () => {
  await loadOptions()
  if (route.params.id) {
    await loadTemplate()
  }
})
</script>

