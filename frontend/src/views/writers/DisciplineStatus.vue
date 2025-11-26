<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Discipline Status</h1>
        <p class="mt-2 text-gray-600">View your account status, strikes, and disciplinary actions</p>
      </div>
      <button
        @click="loadStatus"
        :disabled="loading"
        class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <!-- Status Content -->
    <div v-else-if="status" class="space-y-6">
      <!-- Overall Status -->
      <div
        :class="[
          'rounded-lg shadow-sm p-6 border-2',
          status.is_active && !status.is_suspended && !status.is_on_probation
            ? 'bg-green-50 border-green-200'
            : status.is_suspended
            ? 'bg-red-50 border-red-200'
            : 'bg-yellow-50 border-yellow-200'
        ]"
      >
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-gray-900 mb-2">Account Status</h2>
            <div class="flex items-center gap-3">
              <span
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  status.is_active && !status.is_suspended && !status.is_on_probation
                    ? 'bg-green-100 text-green-700'
                    : status.is_suspended
                    ? 'bg-red-100 text-red-700'
                    : 'bg-yellow-100 text-yellow-700'
                ]"
              >
                {{ getStatusLabel() }}
              </span>
            </div>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-600">Last Updated</p>
            <p class="text-sm font-medium text-gray-900">
              {{ formatDateTime(status.last_updated) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Clean Slate -->
      <div v-if="!hasIssues" class="bg-green-50 border border-green-200 rounded-lg p-6 flex items-start gap-4">
        <span class="text-3xl">🌟</span>
        <div>
          <h3 class="text-lg font-semibold text-green-900">You’re in great standing</h3>
          <p class="text-sm text-green-800 mt-1">
            No strikes, warnings, or active discipline items were found on your account.
          </p>
          <p class="text-xs text-green-700 mt-2">
            Continue submitting high-quality, on-time work to maintain this status.
          </p>
        </div>
      </div>

      <!-- Clean Record -->
      <div
        v-if="!hasIssues"
        class="bg-green-50 border border-green-200 rounded-lg p-6 flex items-start gap-4"
      >
        <span class="text-3xl">🌟</span>
        <div>
          <h3 class="text-lg font-semibold text-green-900">Your record is spotless</h3>
          <p class="text-sm text-green-800 mt-1">
            No strikes, warnings, suspensions, or probation flags exist on your account.
          </p>
          <p class="text-xs text-green-700 mt-2">
            Continue submitting high-quality, on-time work to keep this badge of honor.
          </p>
        </div>
      </div>

      <!-- Status Flags -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-if="status.is_suspended"
          class="bg-red-50 border border-red-200 rounded-lg p-6"
        >
          <div class="flex items-center gap-3 mb-3">
            <span class="text-2xl">🚫</span>
            <h3 class="text-lg font-semibold text-red-900">Account Suspended</h3>
          </div>
          <p class="text-sm text-red-700 mb-3">
            Your account has been suspended. Please contact support for more information.
          </p>
          <router-link
            to="/writer/tickets"
            class="inline-block px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
          >
            Contact Support
          </router-link>
        </div>

        <div
          v-if="status.is_on_probation"
          class="bg-yellow-50 border border-yellow-200 rounded-lg p-6"
        >
          <div class="flex items-center gap-3 mb-3">
            <span class="text-2xl">⚠️</span>
            <h3 class="text-lg font-semibold text-yellow-900">On Probation</h3>
          </div>
          <p class="text-sm text-yellow-700 mb-3">
            Your account is currently on probation. Please review your performance and ensure compliance with platform guidelines.
          </p>
          <router-link
            to="/writer/performance"
            class="inline-block px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm font-medium"
          >
            View Performance
          </router-link>
        </div>

        <div
          v-if="status.is_blacklisted"
          class="bg-red-50 border border-red-200 rounded-lg p-6"
        >
          <div class="flex items-center gap-3 mb-3">
            <span class="text-2xl">⛔</span>
            <h3 class="text-lg font-semibold text-red-900">Blacklisted</h3>
          </div>
          <p class="text-sm text-red-700">
            Your account has been blacklisted. Please contact support immediately.
          </p>
        </div>
      </div>

      <!-- Strikes -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>⚡</span> Strikes ({{ strikes.length }})
        </h2>
        <div v-if="strikes.length === 0" class="text-center py-8">
          <p class="text-gray-500">No strikes on your account. Keep up the good work! 🎉</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="strike in strikes"
            :key="strike.id"
            class="border rounded-lg p-4"
            :class="strike.is_active ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-gray-50'"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span
                    :class="[
                      'px-2 py-1 rounded text-xs font-medium',
                      strike.is_active ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
                    ]"
                  >
                    {{ strike.is_active ? 'Active' : 'Revoked' }}
                  </span>
                  <span class="text-sm text-gray-600">
                    Issued: {{ formatDateTime(strike.issued_at) }}
                  </span>
                </div>
                <p class="font-medium text-gray-900 mb-1">{{ strike.reason || 'No reason provided' }}</p>
                <p v-if="strike.description" class="text-sm text-gray-600">{{ strike.description }}</p>
                <div v-if="strike.revoked_at" class="mt-2 text-xs text-gray-500">
                  Revoked: {{ formatDateTime(strike.revoked_at) }}
                  <span v-if="strike.revoked_reason"> - {{ strike.revoked_reason }}</span>
                </div>
                <button
                  v-if="strike.is_active"
                  @click="openAppealModal('strike', strike)"
                  class="mt-3 text-xs font-semibold text-primary-600 hover:text-primary-800"
                >
                  Appeal this strike →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Suspensions -->
      <div v-if="suspensions && suspensions.length > 0" class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>🚫</span> Suspension History
        </h2>
        <div class="space-y-4">
          <div
            v-for="suspension in suspensions"
            :key="suspension.id"
            class="border border-red-200 rounded-lg p-4 bg-red-50"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span
                    :class="[
                      'px-2 py-1 rounded text-xs font-medium',
                      suspension.is_active ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
                    ]"
                  >
                    {{ suspension.is_active ? 'Active' : 'Lifted' }}
                  </span>
                  <span class="text-sm text-gray-600">
                    {{ suspension.is_active ? 'Suspended' : 'Suspension Lifted' }}: {{ formatDateTime(suspension.suspended_at || suspension.lifted_at) }}
                  </span>
                </div>
                <p class="font-medium text-gray-900 mb-1">{{ suspension.reason || 'No reason provided' }}</p>
                <p v-if="suspension.description" class="text-sm text-gray-600">{{ suspension.description }}</p>
                <div v-if="suspension.lifted_at" class="mt-2 text-xs text-gray-500">
                  Lifted: {{ formatDateTime(suspension.lifted_at) }}
                  <span v-if="suspension.lifted_reason"> - {{ suspension.lifted_reason }}</span>
                </div>
                <button
                  @click="openAppealModal('suspension', suspension)"
                  class="mt-3 text-xs font-semibold text-primary-600 hover:text-primary-800"
                >
                  Appeal suspension →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="warnings && warnings.length > 0" class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>⚠️</span> Warnings ({{ warnings.length }})
        </h2>
        <div class="space-y-4">
          <div
            v-for="warning in warnings"
            :key="warning.id"
            class="border border-yellow-200 rounded-lg p-4 bg-yellow-50"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span
                    :class="[
                      'px-2 py-1 rounded text-xs font-medium',
                      warning.is_active ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'
                    ]"
                  >
                    {{ warning.is_active ? 'Active' : 'Resolved' }}
                  </span>
                  <span class="text-sm text-gray-600">
                    Issued: {{ formatDateTime(warning.issued_at) }}
                  </span>
                </div>
                <p class="font-medium text-gray-900 mb-1">{{ warning.reason || 'No reason provided' }}</p>
                <p v-if="warning.description" class="text-sm text-gray-600">{{ warning.description }}</p>
                <button
                  v-if="warning.is_active"
                  @click="openAppealModal('warning', warning)"
                  class="mt-3 text-xs font-semibold text-primary-600 hover:text-primary-800"
                >
                  Appeal warning →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Help Section -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-blue-900 mb-2">Need Help?</h3>
        <p class="text-sm text-blue-700 mb-4">
          If you have questions about your account status or would like to appeal a decision, please contact our support team.
        </p>
        <div class="flex gap-3">
          <router-link
            to="/writer/tickets"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Contact Support
          </router-link>
          <router-link
            to="/writer/performance"
            class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm font-medium"
          >
            View Performance
          </router-link>
        </div>
      </div>

      <!-- Discipline Framework -->
      <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">How Discipline Works</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="guideline in violationGuidelines"
            :key="guideline.title"
            class="border border-gray-100 rounded-lg p-4 bg-gray-50"
          >
            <div class="flex items-center gap-3 mb-2">
              <span class="text-2xl">{{ guideline.icon }}</span>
              <p class="font-semibold text-gray-900">{{ guideline.title }}</p>
            </div>
            <p class="text-sm text-gray-600">{{ guideline.description }}</p>
            <p class="text-xs text-gray-500 mt-2 italic">
              Recovery: {{ guideline.recovery }}
            </p>
          </div>
        </div>
      </div>

      <!-- Appeal Modal -->
      <div
        v-if="showAppealModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        @click.self="closeAppealModal"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b">
            <h2 class="text-2xl font-bold text-gray-900">{{ appealForm.title || 'Submit Appeal' }}</h2>
            <p class="text-sm text-gray-600 mt-1">
              Appeals create a support ticket so our compliance team can review the situation.
            </p>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select v-model="appealForm.category" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="account">Account / Discipline</option>
                <option value="order">Order Issue</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select v-model="appealForm.priority" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Details *</label>
              <textarea
                v-model="appealForm.description"
                rows="6"
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              ></textarea>
            </div>
          </div>
          <div class="p-6 border-t flex justify-end gap-3">
            <button
              type="button"
              @click="closeAppealModal"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="submitDisciplineAppeal"
              :disabled="appealSubmitting || !appealForm.description.trim()"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {{ appealSubmitting ? 'Submitting...' : 'Submit Appeal' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import writerManagementAPI from '@/api/writer-management'
import ticketsAPI from '@/api/tickets'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError, success: showSuccess } = useToast()

const loading = ref(false)
const status = ref(null)
const strikes = ref([])
const suspensions = ref([])
const warnings = ref([])
const showAppealModal = ref(false)
const appealSubmitting = ref(false)
const appealContext = ref(null)
const appealForm = ref({
  title: '',
  category: 'account',
  priority: 'medium',
  description: '',
})
const violationGuidelines = [
  {
    icon: '⚡',
    title: 'Strikes',
    description: 'Issued for policy violations such as plagiarism, poor communication, or repeated late submissions.',
    recovery: 'Strikes expire or can be appealed once the underlying issue is resolved.'
  },
  {
    icon: '🚫',
    title: 'Suspensions',
    description: 'Temporary removal from the platform while serious issues are reviewed (e.g., fraud, harassment).',
    recovery: 'Requires formal review; contact support with documentation to appeal.'
  },
  {
    icon: '⚠️',
    title: 'Probation & Warnings',
    description: 'Used to flag elevated risk due to revision spikes, disputes, or QA failures.',
    recovery: 'Improve metrics (completion rate, revisions, ratings) over the next review window.'
  }
]

const hasIssues = computed(() => {
  if (!status.value) return false
  return Boolean(
    status.value.is_suspended ||
    status.value.is_blacklisted ||
    status.value.is_on_probation ||
    strikes.value.length ||
    warnings.value.length ||
    suspensions.value.some(s => s.is_active)
  )
})

const loadStatus = async () => {
  loading.value = true
  try {
    // Get writer profile to get writer ID
    const profileResponse = await writerManagementAPI.getMyProfile()
    const writerId = profileResponse.data.id || profileResponse.data.user
    
    // Load all discipline data
    await Promise.all([
      loadWriterStatus(writerId),
      loadStrikes(writerId),
      loadSuspensions(writerId),
      loadWarnings(writerId),
    ])
  } catch (error) {
    console.error('Failed to load discipline status:', error)
    showError(getErrorMessage(error, 'Failed to load discipline status'))
  } finally {
    loading.value = false
  }
}

const loadWriterStatus = async (writerId) => {
  try {
    const response = await writerManagementAPI.getWriterStatus(writerId)
    status.value = response.data
  } catch (error) {
    console.error('Failed to load writer status:', error)
    // Try alternative endpoint
    try {
      const response = await writerManagementAPI.listWriterStatuses({ writer: writerId })
      if (response.data.results && response.data.results.length > 0) {
        status.value = response.data.results[0]
      }
    } catch (err) {
      console.error('Failed to load status from alternative endpoint:', err)
    }
  }
}

const loadStrikes = async (writerId) => {
  try {
    const response = await writerManagementAPI.getStrikesByWriter(writerId)
    strikes.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load strikes:', error)
    strikes.value = []
  }
}

const loadSuspensions = async (writerId) => {
  try {
    const response = await writerManagementAPI.listSuspensions({ writer: writerId })
    suspensions.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load suspensions:', error)
    suspensions.value = []
  }
}

const loadWarnings = async (writerId) => {
  try {
    const response = await writerManagementAPI.listWarnings({ writer: writerId })
    warnings.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load warnings:', error)
    warnings.value = []
  }
}

const getStatusLabel = () => {
  if (!status.value) return 'Unknown'
  if (status.value.is_suspended) return 'Suspended'
  if (status.value.is_on_probation) return 'On Probation'
  if (status.value.is_blacklisted) return 'Blacklisted'
  if (status.value.is_active) return 'Active'
  return 'Inactive'
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const openAppealModal = (type, entity) => {
  appealContext.value = { type, entity }
  const identifier =
    type === 'strike'
      ? `Strike #${entity.id}`
      : type === 'suspension'
      ? `Suspension ${entity.id ? `#${entity.id}` : ''}`.trim()
      : `Warning #${entity.id}`
  appealForm.value = {
    title: `Appeal ${identifier}`,
    category: 'account',
    priority: type === 'suspension' ? 'high' : 'medium',
    description: `I'd like to appeal ${identifier}.\n\nReason issued: ${entity.reason || 'N/A'}\nDetails: ${entity.description || 'N/A'}\n\nMy appeal: `,
  }
  showAppealModal.value = true
}

const closeAppealModal = () => {
  showAppealModal.value = false
  appealContext.value = null
  appealForm.value = {
    title: '',
    category: 'account',
    priority: 'medium',
    description: '',
  }
}

const submitDisciplineAppeal = async () => {
  if (!appealForm.value.title || !appealForm.value.description.trim()) {
    showError('Please provide details for your appeal.')
    return
  }
  appealSubmitting.value = true
  try {
    await ticketsAPI.create({
      title: appealForm.value.title,
      category: appealForm.value.category,
      priority: appealForm.value.priority,
      description: appealForm.value.description,
    })
    showSuccess('Appeal submitted. Support will follow up via tickets.')
    closeAppealModal()
  } catch (error) {
    console.error('Failed to submit appeal:', error)
    showError(getErrorMessage(error, 'Unable to submit appeal'))
  } finally {
    appealSubmitting.value = false
  }
}

onMounted(() => {
  loadStatus()
})
</script>

