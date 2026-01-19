<template>
  <div class="class-creation-wizard max-w-4xl mx-auto">
    <!-- Step 1: Choose Class Type -->
    <div v-if="currentStep === 1" class="space-y-6">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Choose Your Class Type</h2>
        <p class="text-gray-600 dark:text-gray-400">Select the type of class service that best fits your needs</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Express Class Card -->
        <div
          @click="selectClassType('express')"
          :class="[
            'card p-6 cursor-pointer transition-all duration-300 hover:shadow-xl',
            selectedClassType === 'express'
              ? 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'hover:border-primary-300'
          ]"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white">Express Class</h3>
            </div>
            <div v-if="selectedClassType === 'express'" class="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            Fast, single-class service for immediate academic support. Perfect for urgent assignments, exams, or quick help.
          </p>

          <div class="space-y-2 mb-4">
            <div class="flex items-start space-x-2">
              <svg class="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm text-gray-700 dark:text-gray-300">Quick turnaround (typically 1-3 days)</span>
            </div>
            <div class="flex items-start space-x-2">
              <svg class="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm text-gray-700 dark:text-gray-300">Pay per class</span>
            </div>
            <div class="flex items-start space-x-2">
              <svg class="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm text-gray-700 dark:text-gray-300">Flexible payment options</span>
            </div>
            <div class="flex items-start space-x-2">
              <svg class="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm text-gray-700 dark:text-gray-300">Ideal for one-time help</span>
            </div>
          </div>

          <button
            @click.stop="selectClassType('express')"
            :class="[
              'w-full py-2 px-4 rounded-lg font-medium transition-colors',
              selectedClassType === 'express'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            ]"
          >
            {{ selectedClassType === 'express' ? 'Selected' : 'Select Express Class' }}
          </button>
        </div>

        <!-- Bundled Class Card -->
        <div
          @click="selectClassType('bundle')"
          :class="[
            'card p-6 cursor-pointer transition-all duration-300 hover:shadow-xl',
            selectedClassType === 'bundle'
              ? 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'hover:border-primary-300'
          ]"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white">Bundled Class</h3>
            </div>
            <div v-if="selectedClassType === 'bundle'" class="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            Comprehensive semester-long support with multiple classes. Best value for ongoing academic assistance.
          </p>

          <div class="space-y-2 mb-4">
            <div class="flex items-start space-x-2">
              <svg class="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm text-gray-700 dark:text-gray-300">Full semester coverage (15-16 weeks)</span>
            </div>
            <div class="flex items-start space-x-2">
              <svg class="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm text-gray-700 dark:text-gray-300">Bulk pricing discounts</span>
            </div>
            <div class="flex items-start space-x-2">
              <svg class="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm text-gray-700 dark:text-gray-300">Dedicated writer assignment</span>
            </div>
            <div class="flex items-start space-x-2">
              <svg class="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-sm text-gray-700 dark:text-gray-300">Installment payment plans available</span>
            </div>
          </div>

          <button
            @click.stop="selectClassType('bundle')"
            :class="[
              'w-full py-2 px-4 rounded-lg font-medium transition-colors',
              selectedClassType === 'bundle'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            ]"
          >
            {{ selectedClassType === 'bundle' ? 'Selected' : 'Select Bundled Class' }}
          </button>
        </div>
      </div>

      <!-- Help Link -->
      <div class="text-center mt-6">
        <button
          @click="showHelpModal = true"
          class="text-primary-600 dark:text-primary-400 hover:underline text-sm font-medium"
        >
          Need help deciding? Learn more about the differences →
        </button>
      </div>

      <!-- Navigation -->
      <div class="flex justify-end mt-8">
        <button
          @click="nextStep"
          :disabled="!selectedClassType"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          Continue →
        </button>
      </div>
    </div>

    <!-- Step 2: Class Details Form -->
    <div v-else-if="currentStep === 2" class="space-y-6">
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {{ selectedClassType === 'express' ? 'Express Class' : 'Bundled Class' }} Details
        </h2>
        <p class="text-gray-600 dark:text-gray-400">Fill in the details for your class request</p>
      </div>

      <form @submit.prevent="submitForm" class="space-y-6">
        <!-- Express Class Form -->
        <template v-if="selectedClassType === 'express'">
          <!-- Basic Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Start Date <span class="text-red-500">*</span>
              </label>
              <input
                v-model="expressForm.start_date"
                type="date"
                required
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                End Date <span class="text-red-500">*</span>
              </label>
              <input
                v-model="expressForm.end_date"
                type="date"
                required
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Discipline <span class="text-red-500">*</span>
              </label>
              <input
                v-model="expressForm.discipline"
                type="text"
                required
                placeholder="e.g., Mathematics, Nursing"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Institution <span class="text-red-500">*</span>
              </label>
              <input
                v-model="expressForm.institution"
                type="text"
                required
                placeholder="Your school/university name"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Course <span class="text-red-500">*</span>
              </label>
              <input
                v-model="expressForm.course"
                type="text"
                required
                placeholder="Course name or code"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Academic Level <span class="text-red-500">*</span>
              </label>
              <select
                v-model="expressForm.academic_level"
                required
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select level</option>
                <option value="Undergraduate">Undergraduate</option>
                <option value="Graduate">Graduate</option>
                <option value="Doctorate">Doctorate</option>
              </select>
            </div>
          </div>

          <!-- Budget Field -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Budget ($)
            </label>
            <input
              v-model.number="expressForm.budget"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Your budget for negotiation purposes (optional)</p>
          </div>

          <!-- Workload -->
          <div class="card p-4 bg-gray-50 dark:bg-gray-800">
            <h3 class="font-medium text-gray-900 dark:text-white mb-4">Expected Workload</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Discussion Posts</label>
                <input
                  v-model.number="expressForm.number_of_discussion_posts"
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Assignments</label>
                <input
                  v-model.number="expressForm.number_of_assignments"
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Exams</label>
                <input
                  v-model.number="expressForm.number_of_exams"
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">Quizzes</label>
                <input
                  v-model.number="expressForm.number_of_quizzes"
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          </div>

          <!-- Instructions -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Special Instructions
            </label>
            <textarea
              v-model="expressForm.instructions"
              rows="4"
              placeholder="Any special requirements or instructions..."
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>

          <!-- File Uploads -->
          <div class="card p-4 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Supporting Files (Optional)
            </label>
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
              Upload any relevant files such as course syllabus, assignment instructions, or reference materials
            </p>
            <FileUpload
              v-model="expressForm.inquiry_files"
              :multiple="true"
              accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
              upload-label="Upload Files"
              :max-size="10 * 1024 * 1024"
            />
          </div>
        </template>

        <!-- Bundled Class Form -->
        <template v-else>
          <div class="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p class="text-sm text-blue-800 dark:text-blue-300">
              Bundled class creation will be available soon. For now, please contact support or use Express Classes.
            </p>
          </div>
        </template>

        <!-- Navigation -->
        <div class="flex justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            @click="prevStep"
            class="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            ← Back
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {{ submitting ? 'Submitting...' : 'Submit Request' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Help Modal -->
    <div
      v-if="showHelpModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showHelpModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Understanding Class Types</h3>
            <button
              @click="showHelpModal = false"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="space-y-6">
            <div>
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Express Classes</h4>
              <p class="text-gray-600 dark:text-gray-400 mb-3">
                Express classes are designed for immediate, short-term academic support. They're perfect when you need quick help with specific assignments, exams, or urgent coursework.
              </p>
              <ul class="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400 ml-4">
                <li>Fast turnaround (typically 1-3 days)</li>
                <li>Pay per class basis</li>
                <li>Flexible payment options including installments</li>
                <li>Ideal for one-time or occasional help</li>
                <li>Quick pricing and assignment process</li>
              </ul>
            </div>

            <div>
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Bundled Classes</h4>
              <p class="text-gray-600 dark:text-gray-400 mb-3">
                Bundled classes provide comprehensive semester-long support. You get multiple classes bundled together at a discounted rate, with a dedicated writer assigned to your account.
              </p>
              <ul class="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400 ml-4">
                <li>Full semester coverage (typically 15-16 weeks)</li>
                <li>Bulk pricing with significant discounts</li>
                <li>Dedicated writer assignment for consistency</li>
                <li>Installment payment plans available</li>
                <li>Best value for ongoing academic support</li>
              </ul>
            </div>

            <div class="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
              <p class="text-sm text-yellow-800 dark:text-yellow-300">
                <strong>Not sure which to choose?</strong> If you need help right away or for a single assignment, choose Express. If you need ongoing support throughout the semester, choose Bundled.
              </p>
            </div>
          </div>

          <div class="mt-6 flex justify-end">
            <button
              @click="showHelpModal = false"
              class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Got it, thanks!
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import expressClassesAPI from '@/api/express-classes'
import { useToast } from '@/composables/useToast'
import FileUpload from '@/components/common/FileUpload.vue'

const router = useRouter()
const { showToast } = useToast()

const emit = defineEmits(['success', 'cancel'])

const currentStep = ref(1)
const selectedClassType = ref(null)
const showHelpModal = ref(false)
const submitting = ref(false)

const expressForm = ref({
  start_date: '',
  end_date: '',
  discipline: '',
  institution: '',
  course: '',
  academic_level: '',
  budget: null,
  number_of_discussion_posts: 0,
  number_of_discussion_posts_replies: 0,
  number_of_assignments: 0,
  number_of_exams: 0,
  number_of_quizzes: 0,
  number_of_projects: 0,
  number_of_presentations: 0,
  number_of_papers: 0,
  total_workload_in_pages: '',
  instructions: '',
  school_login_link: '',
  school_login_username: '',
  school_login_password: '',
  inquiry_files: []
})

const selectClassType = (type) => {
  selectedClassType.value = type
}

const nextStep = () => {
  if (selectedClassType.value) {
    currentStep.value = 2
  }
}

const prevStep = () => {
  currentStep.value = 1
}

const submitForm = async () => {
  if (selectedClassType.value !== 'express') {
    showToast('Bundled classes are coming soon!', 'info')
    return
  }

  submitting.value = true
  try {
    const payload = {
      ...expressForm.value,
      website: 1 // TODO: Get from auth store or context
    }

    // Remove empty budget if null
    if (!payload.budget) {
      delete payload.budget
    }

    // Remove inquiry_files from payload (will be uploaded separately)
    const files = payload.inquiry_files || []
    delete payload.inquiry_files

    const response = await expressClassesAPI.create(payload)
    
    // Upload files if any
    if (files.length > 0 && response.data?.id) {
      try {
        await Promise.all(
          files.map(file => {
            if (file instanceof File) {
              return expressClassesAPI.uploadInquiryFile({
                express_class: response.data.id,
                file: file,
                description: ''
              })
            }
            return Promise.resolve()
          })
        )
      } catch (fileError) {
        console.error('Error uploading files:', fileError)
        // Don't fail the whole request if file upload fails
        showToast('Class created but some files failed to upload', 'warning')
      }
    }

    showToast('Express class request submitted successfully!', 'success')
    emit('success', response.data)
    
    // Redirect to class detail or list
    if (response.data?.id) {
      router.push(`/classes/express/${response.data.id}`)
    }
  } catch (error) {
    console.error('Failed to create express class:', error)
    showToast(
      error?.response?.data?.detail || error?.response?.data?.error || 'Failed to submit request. Please try again.',
      'error'
    )
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.class-creation-wizard {
  min-height: 500px;
}
</style>
