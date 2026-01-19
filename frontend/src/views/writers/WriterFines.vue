<template>
  <div class="min-h-dvh bg-gray-50 page-shell space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="page-title text-gray-900">Fines & Appeals</h1>
        <p class="mt-2 text-gray-600">
          Track fines that impact your payouts and submit appeals when something looks off.
        </p>
      </div>
      <button
        @click="loadFines"
        :disabled="loading"
        class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 w-full sm:w-auto"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 border border-gray-100">
        <p class="text-sm font-medium text-gray-600 mb-1">Total Fines</p>
        <p class="text-3xl font-bold text-gray-900">
          ${{ formatCurrency(stats.total_amount) }}
        </p>
        <p class="text-xs text-gray-500 mt-1">{{ fines.length }} records</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 border border-yellow-100">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending / Active</p>
        <p class="text-3xl font-bold text-yellow-900">${{ formatCurrency(stats.active_amount) }}</p>
        <p class="text-xs text-yellow-600 mt-1">{{ stats.active_count }} fines affecting payouts</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 border border-blue-100">
        <p class="text-sm font-medium text-blue-700 mb-1">Appeals in Progress</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.appealed_count }}</p>
        <p class="text-xs text-blue-600 mt-1">Awaiting review</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 border border-green-100">
        <p class="text-sm font-medium text-green-700 mb-1">Waived / Resolved</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.resolved_count }}</p>
        <p class="text-xs text-green-600 mt-1">No longer impacting payouts</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filterStatus"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All statuses</option>
            <option value="issued">Issued</option>
            <option value="appealed">Appealed</option>
            <option value="disputed">Disputed</option>
            <option value="resolved">Resolved</option>
            <option value="waived">Waived</option>
            <option value="voided">Voided</option>
          </select>
        </div>
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by order ID or reason..."
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
    </div>

    <!-- Fines Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else-if="filteredFines.length === 0" class="text-center py-12">
        <div class="text-4xl mb-3">🎉</div>
        <p class="text-gray-600 text-lg">No fines on your record</p>
        <p class="text-sm text-gray-400 mt-1">
          Stay on-time and responsive to keep fines off your payout history.
        </p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Order</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Reason</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Imposed</th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="fine in filteredFines" :key="fine.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="text-sm font-semibold text-gray-900">#{{ fine.order }}</div>
                <router-link
                  :to="`/orders/${fine.order}`"
                  class="text-xs text-primary-600 hover:text-primary-800"
                >
                  View Order
                </router-link>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900 font-medium">
                  {{ fine.fine_type_display || fine.fine_type_config?.name || 'Fine' }}
                </div>
                <p v-if="fine.fine_type_config?.description" class="text-xs text-gray-500">
                  {{ fine.fine_type_config.description }}
                </p>
              </td>
              <td class="px-6 py-4 text-sm font-semibold text-gray-900">
                ${{ formatCurrency(fine.amount) }}
              </td>
              <td class="px-6 py-4">
                <span
                  :class="getStatusBadgeClass(fine.status)"
                  class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold"
                >
                  {{ formatStatus(fine.status) }}
                </span>
                <div v-if="fine.appeal" class="mt-1 text-xs text-blue-600">
                  Appeal: {{ formatAppealStatus(fine.appeal) }}
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-700 max-w-md">
                {{ fine.reason }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ formatDateTime(fine.imposed_at) }}
              </td>
              <td class="px-6 py-4 text-right text-sm font-medium space-y-2">
                <button
                  v-if="canAppeal(fine)"
                  @click="openAppealModal(fine)"
                  class="text-primary-600 hover:text-primary-800 w-full text-left"
                >
                  Appeal Fine
                </button>
                <button
                  v-if="fine.appeal"
                  @click="openAppealDetails(fine)"
                  class="text-blue-600 hover:text-blue-800 w-full text-left"
                >
                  View Appeal
                </button>
                <div v-if="fine.appeal" class="text-xs text-gray-500">
                  Submitted {{ formatDateTime(fine.appeal.created_at) }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Appeal Modal -->
    <div
      v-if="showAppealModal"
      class="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4"
      @click.self="closeAppealModal"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <h2 class="text-2xl font-bold text-gray-900">Appeal Fine #{{ selectedFine?.id }}</h2>
          <p class="text-sm text-gray-600 mt-1">
            Explain why this fine should be reviewed or removed. Appeals notify admins and pause escalation.
          </p>
        </div>
        <div class="p-6 space-y-4">
          <div class="bg-gray-50 border border-gray-100 rounded-lg p-4 text-sm text-gray-700">
            <p class="font-semibold text-gray-900">Fine Summary</p>
            <ul class="mt-2 space-y-1">
              <li>Order: #{{ selectedFine?.order }}</li>
              <li>Amount: ${{ formatCurrency(selectedFine?.amount) }}</li>
              <li>Reason: {{ selectedFine?.reason }}</li>
            </ul>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Appeal Reason *</label>
            <textarea
              v-model="appealReason"
              rows="5"
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Describe what happened, provide context, and mention any supporting evidence."
            ></textarea>
          </div>
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Attach Evidence (optional)</label>
            <input
              type="file"
              multiple
              :accept="evidenceAccepts"
              @change="handleInitialEvidenceChange"
              class="block w-full text-sm text-gray-600 file:mr-3 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
            />
            <textarea
              v-model="initialEvidenceDescription"
              rows="2"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              placeholder="Add context for the files you’re uploading (optional)."
            ></textarea>
            <ul v-if="initialEvidenceFiles.length" class="text-sm text-gray-600 space-y-1">
              <li v-for="file in initialEvidenceFiles" :key="file.name" class="flex items-center gap-2">
                <span>• {{ file.name }}</span>
              </li>
            </ul>
            <p class="text-xs text-gray-500">Supported formats: PDF, DOC(X), images, TXT, ZIP</p>
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
            @click="submitAppeal"
            :disabled="appealSubmitting || !appealReason.trim()"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            {{ appealSubmitting ? 'Submitting...' : 'Submit Appeal' }}
          </button>
        </div>
      </div>
    <!-- Appeal Details Drawer -->
    <div
    v-if="showAppealDetails"
    class="fixed inset-0 z-40 bg-black bg-opacity-50 flex justify-end"
    @click.self="closeAppealDetails"
    >
      <div class="bg-white w-full max-w-3xl h-full shadow-2xl flex flex-col">
        <div class="p-6 border-b flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">
              Appeal Timeline
            </h2>
            <p class="text-sm text-gray-500 mt-1">
              Fine #{{ activeAppealFine?.id }} • Order #{{ activeAppealFine?.order }}
            </p>
          </div>
          <button
            class="text-gray-500 hover:text-gray-700"
            @click="closeAppealDetails"
          >
            ✕
          </button>
        </div>
        <div class="p-6 overflow-y-auto space-y-6 flex-1">
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-100">
            <p class="text-sm text-gray-600">Fine Summary</p>
            <div class="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-xs text-gray-500 uppercase">Amount</p>
                <p class="font-semibold text-gray-900">${{ formatCurrency(activeAppealFine?.amount) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 uppercase">Status</p>
                <p class="font-semibold text-gray-900">{{ formatStatus(activeAppealFine?.status) }}</p>
              </div>
              <div class="sm:col-span-2">
                <p class="text-xs text-gray-500 uppercase">Reason</p>
                <p class="text-gray-800">{{ activeAppealFine?.reason }}</p>
              </div>
            </div>
          </div>

        <section>
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold text-gray-900">Timeline</h3>
            <button
              class="text-sm text-primary-600 hover:text-primary-800"
              @click="loadAppealTimeline(activeAppeal?.id)"
              :disabled="timelineLoading"
            >
              Refresh
            </button>
          </div>
          <div v-if="timelineLoading" class="flex items-center justify-center py-6">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
          <div v-else-if="timelineError" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-4">
            {{ timelineError }}
          </div>
          <div v-else-if="appealTimeline.length === 0" class="text-sm text-gray-500 border border-dashed border-gray-200 rounded-lg p-6 text-center">
            No updates yet. Use the forms below to post a message or add evidence.
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="event in appealTimeline"
              :key="event.id"
              class="border border-gray-200 rounded-lg p-4 shadow-sm"
            >
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-semibold text-gray-900">{{ formatEventType(event.event_type) }}</p>
                  <p class="text-xs text-gray-500">
                    {{ event.actor?.email || 'System' }} • {{ event.actor_role || 'system' }}
                  </p>
                </div>
                <p class="text-xs text-gray-500">
                  {{ formatDateTime(event.created_at) }}
                </p>
              </div>
              <p v-if="event.message" class="text-sm text-gray-800 mt-3 whitespace-pre-line">
                {{ event.message }}
              </p>
              <div v-if="event.attachments?.length" class="mt-3 space-y-2">
                <div
                  v-for="attachment in event.attachments"
                  :key="attachment.id"
                  class="text-sm flex items-center gap-2"
                >
                  <span class="text-gray-500">📎</span>
                  <a
                    :href="attachment.file_url"
                    target="_blank"
                    rel="noopener"
                    class="text-primary-600 hover:underline"
                  >
                    {{ attachment.file_name || 'Download evidence' }}
                  </a>
                  <span v-if="attachment.description" class="text-xs text-gray-500">
                    • {{ attachment.description }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-base font-semibold text-gray-900 mb-2">Post an Update</h3>
            <textarea
              v-model="timelineComment"
              rows="4"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              placeholder="Share new context or respond to admin questions."
            ></textarea>
            <button
              class="mt-3 w-full bg-primary-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-primary-700 disabled:opacity-50"
              :disabled="timelineSubmitting || !timelineComment.trim()"
              @click="submitTimelineUpdate"
            >
              {{ timelineSubmitting ? 'Posting...' : 'Post Update' }}
            </button>
          </div>
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-base font-semibold text-gray-900 mb-2">Upload Evidence</h3>
            <input
              type="file"
              multiple
              :accept="evidenceAccepts"
              @change="handleTimelineEvidenceChange"
              class="block w-full text-sm text-gray-600 file:mr-3 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
            />
            <textarea
              v-model="timelineEvidenceDescription"
              rows="2"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm mt-2"
              placeholder="Describe the files you’re uploading (optional)."
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">
              {{ timelineEvidenceFiles.length }} file(s) selected
            </p>
            <button
              class="mt-3 w-full bg-blue-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-blue-700 disabled:opacity-50"
              :disabled="timelineEvidenceUploading || !timelineEvidenceFiles.length"
              @click="uploadTimelineEvidence"
            >
              {{ timelineEvidenceUploading ? 'Uploading...' : 'Upload Evidence' }}
            </button>
          </div>
        </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import finesAPI from '@/api/fines'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError, success: showSuccess } = useToast()

const loading = ref(false)
const fines = ref([])
const filterStatus = ref('')
const searchQuery = ref('')
const showAppealModal = ref(false)
const selectedFine = ref(null)
const appealReason = ref('')
const appealSubmitting = ref(false)
const initialEvidenceFiles = ref([])
const initialEvidenceDescription = ref('')
const showAppealDetails = ref(false)
const activeAppeal = ref(null)
const activeAppealFine = ref(null)
const appealTimeline = ref([])
const timelineLoading = ref(false)
const timelineError = ref(null)
const timelineComment = ref('')
const timelineSubmitting = ref(false)
const timelineEvidenceFiles = ref([])
const timelineEvidenceDescription = ref('')
const timelineEvidenceUploading = ref(false)
const evidenceAccepts = '.pdf,.doc,.docx,.png,.jpg,.jpeg,.txt,.zip'

const stats = computed(() => {
  let total = 0
  let activeAmount = 0
  let activeCount = 0
  let appealed = 0
  let resolved = 0

  fines.value.forEach(fine => {
    total += Number(fine.amount || 0)
    const status = (fine.status || '').toLowerCase()
    if (['issued', 'appealed', 'disputed'].includes(status)) {
      activeAmount += Number(fine.amount || 0)
      activeCount += 1
    }
    if (status === 'appealed' || status === 'disputed') {
      appealed += 1
    }
    if (['waived', 'voided', 'resolved'].includes(status)) {
      resolved += 1
    }
  })

  return {
    total_amount: total,
    active_amount: activeAmount,
    active_count: activeCount,
    appealed_count: appealed,
    resolved_count: resolved,
  }
})

const filteredFines = computed(() => {
  let list = [...fines.value]
  if (filterStatus.value) {
    list = list.filter(f => (f.status || '').toLowerCase() === filterStatus.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(f =>
      String(f.order).includes(q) ||
      (f.reason || '').toLowerCase().includes(q) ||
      (f.fine_type_display || '').toLowerCase().includes(q)
    )
  }
  return list
})

const loadFines = async () => {
  loading.value = true
  try {
    const response = await finesAPI.listFines({ ordering: '-imposed_at' })
    fines.value = response.data.results || response.data || []
    if (activeAppealFine.value) {
      refreshActiveAppeal(activeAppealFine.value.id)
      if (!activeAppeal.value) {
        closeAppealDetails()
      }
    }
  } catch (error) {
    console.error('Failed to load fines:', error)
    showError(getErrorMessage(error, 'Failed to load fines'))
  } finally {
    loading.value = false
  }
}

const formatCurrency = (value) => Number(value || 0).toFixed(2)

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

const formatStatus = (status) => {
  if (!status) return 'Unknown'
  const map = {
    issued: 'Issued',
    appealed: 'Appealed',
    disputed: 'Disputed',
    escalated: 'Escalated',
    resolved: 'Resolved',
    waived: 'Waived',
    voided: 'Voided',
  }
  return map[status.toLowerCase()] || status
}

const formatAppealStatus = (appeal) => {
  if (!appeal) return ''
  if (appeal.accepted === true) return 'Accepted'
  if (appeal.accepted === false) return 'Rejected'
  if (appeal.escalated) return 'Escalated'
  return 'Pending review'
}

const getStatusBadgeClass = (status) => {
  const normalized = (status || '').toLowerCase()
  if (normalized === 'waived' || normalized === 'voided' || normalized === 'resolved') {
    return 'bg-green-100 text-green-800'
  }
  if (normalized === 'appealed' || normalized === 'disputed' || normalized === 'escalated') {
    return 'bg-blue-100 text-blue-800'
  }
  return 'bg-yellow-100 text-yellow-800'
}

const canAppeal = (fine) => {
  const status = (fine.status || '').toLowerCase()
  return ['issued', 'appealed', 'disputed'].includes(status) && !fine.appeal
}

const openAppealModal = (fine) => {
  selectedFine.value = fine
  appealReason.value = ''
  showAppealModal.value = true
}

const closeAppealModal = () => {
  showAppealModal.value = false
  selectedFine.value = null
  appealReason.value = ''
  initialEvidenceFiles.value = []
  initialEvidenceDescription.value = ''
}

const handleInitialEvidenceChange = (event) => {
  const files = Array.from(event.target?.files || [])
  initialEvidenceFiles.value = files
}

const openAppealDetails = (fine) => {
  if (!fine?.appeal) {
    showError('This fine does not have an appeal yet.')
    return
  }
  activeAppealFine.value = fine
  activeAppeal.value = fine.appeal
  showAppealDetails.value = true
  loadAppealTimeline(fine.appeal.id)
}

const closeAppealDetails = () => {
  showAppealDetails.value = false
  activeAppeal.value = null
  activeAppealFine.value = null
  appealTimeline.value = []
  timelineComment.value = ''
  timelineEvidenceFiles.value = []
  timelineEvidenceDescription.value = ''
  timelineError.value = null
}

const loadAppealTimeline = async (appealId) => {
  if (!appealId) return
  timelineLoading.value = true
  timelineError.value = null
  try {
    const response = await finesAPI.getAppealTimeline(appealId)
    appealTimeline.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Failed to load appeal timeline:', error)
    timelineError.value = getErrorMessage(error, 'Unable to load timeline')
    showError(timelineError.value)
  } finally {
    timelineLoading.value = false
  }
}

const submitTimelineUpdate = async () => {
  if (!activeAppeal.value?.id || !timelineComment.value.trim()) {
    showError('Please enter a message before posting.')
    return
  }
  timelineSubmitting.value = true
  try {
    await finesAPI.postAppealComment(activeAppeal.value.id, {
      message: timelineComment.value.trim(),
    })
    timelineComment.value = ''
    await loadAppealTimeline(activeAppeal.value.id)
    await loadFines()
    showSuccess('Update posted to appeal timeline.')
  } catch (error) {
    console.error('Failed to post appeal update:', error)
    showError(getErrorMessage(error, 'Unable to post update'))
  } finally {
    timelineSubmitting.value = false
  }
}

const handleTimelineEvidenceChange = (event) => {
  timelineEvidenceFiles.value = Array.from(event.target?.files || [])
}

const uploadTimelineEvidence = async () => {
  if (!activeAppeal.value?.id || !timelineEvidenceFiles.value.length) {
    showError('Select at least one file to upload.')
    return
  }
  timelineEvidenceUploading.value = true
  try {
    for (const file of timelineEvidenceFiles.value) {
      const formData = new FormData()
      formData.append('file', file)
      if (timelineEvidenceDescription.value.trim()) {
        formData.append('description', timelineEvidenceDescription.value.trim())
      }
      await finesAPI.uploadAppealEvidence(activeAppeal.value.id, formData)
    }
    timelineEvidenceFiles.value = []
    timelineEvidenceDescription.value = ''
    await loadAppealTimeline(activeAppeal.value.id)
    await loadFines()
    showSuccess('Evidence uploaded successfully.')
  } catch (error) {
    console.error('Failed to upload evidence:', error)
    showError(getErrorMessage(error, 'Unable to upload evidence'))
  } finally {
    timelineEvidenceUploading.value = false
  }
}

const formatEventType = (type) => {
  const labels = {
    appeal_submitted: 'Appeal Submitted',
    writer_update: 'Writer Update',
    evidence_added: 'Evidence Added',
    admin_response: 'Admin Response',
    status_change: 'Status Update',
    system: 'System Notice',
  }
  return labels[type] || type
}

const refreshActiveAppeal = (fineId) => {
  if (!fineId) return
  const refreshedFine = fines.value.find((f) => f.id === fineId)
  if (refreshedFine?.appeal) {
    activeAppealFine.value = refreshedFine
    activeAppeal.value = refreshedFine.appeal
  }
}

const submitAppeal = async () => {
  if (!selectedFine.value || !appealReason.value.trim()) {
    showError('Please provide an appeal reason.')
    return
  }
  const fineId = selectedFine.value.id
  appealSubmitting.value = true
  try {
    const attachments = [...initialEvidenceFiles.value]
    const disputeResponse = await finesAPI.disputeFine(fineId, { reason: appealReason.value.trim() })
    const appealId = disputeResponse.data?.id

    if (appealId && attachments.length) {
      for (const file of attachments) {
        const formData = new FormData()
        formData.append('file', file)
        if (initialEvidenceDescription.value.trim()) {
          formData.append('description', initialEvidenceDescription.value.trim())
        }
        await finesAPI.uploadAppealEvidence(appealId, formData)
      }
    }

    showSuccess('Appeal submitted successfully. We’ll notify you once reviewed.')
    closeAppealModal()
    await loadFines()
    const updatedFine = fines.value.find(f => f.id === fineId)
    if (updatedFine?.appeal) {
      openAppealDetails(updatedFine)
    }
  } catch (error) {
    console.error('Failed to submit appeal:', error)
    showError(getErrorMessage(error, 'Unable to submit appeal'))
  } finally {
    appealSubmitting.value = false
  }
}

onMounted(() => {
  loadFines()
})
</script>

