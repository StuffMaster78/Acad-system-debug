<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Express Classes Management</h1>
        <p class="mt-2 text-gray-600">Manage single express class requests, inquiries, scope reviews, and assignments</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Inquiry</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.inquiry || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Scope Review</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.scope_review || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Priced</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.priced || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
        <p class="text-sm font-medium text-indigo-700 mb-1">Assigned</p>
        <p class="text-3xl font-bold text-indigo-900">{{ stats.assigned || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.in_progress || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200">
        <p class="text-sm font-medium text-gray-700 mb-1">Completed</p>
        <p class="text-3xl font-bold text-gray-900">{{ stats.completed || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadExpressClasses" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="inquiry">Inquiry</option>
            <option value="scope_review">Scope Review</option>
            <option value="priced">Priced</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Class ID, client, course..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website" @change="loadExpressClasses" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Has Writer</label>
          <select v-model="filters.has_writer" @change="loadExpressClasses" class="w-full border rounded px-3 py-2">
            <option value="">All</option>
            <option value="true">Assigned</option>
            <option value="false">Unassigned</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Express Classes Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dates</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="expressClass in expressClasses" :key="expressClass.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ expressClass.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ expressClass.client_username || expressClass.client_email || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                <div class="flex flex-col">
                  <span class="font-medium">{{ expressClass.course || 'N/A' }}</span>
                  <span class="text-xs text-gray-500">{{ expressClass.discipline || 'N/A' }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span v-if="expressClass.assigned_writer_username">
                  {{ expressClass.assigned_writer_username }}
                </span>
                <span v-else class="text-gray-400 italic">Unassigned</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(expressClass.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ expressClass.status_display || expressClass.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span v-if="expressClass.price">
                  ${{ parseFloat(expressClass.price || 0).toFixed(2) }}
                  <span v-if="expressClass.installments_needed > 0" class="text-xs text-gray-500">
                    ({{ expressClass.installments_needed }} installments)
                  </span>
                </span>
                <span v-else class="text-gray-400 italic">Not priced</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex flex-col text-xs">
                  <span>Start: {{ formatDate(expressClass.start_date) }}</span>
                  <span>End: {{ formatDate(expressClass.end_date) }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button @click="viewExpressClass(expressClass)" class="text-blue-600 hover:underline">View</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!loading && expressClasses.length === 0" class="text-center py-12 text-gray-500">
        <p>No express classes found</p>
      </div>
    </div>

    <!-- Express Class Detail Modal -->
    <div v-if="viewingExpressClass" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold">Express Class #{{ viewingExpressClass.id }}</h2>
            <button @click="viewingExpressClass = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div class="grid grid-cols-2 gap-6 mb-6">
            <!-- Left Column -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Class Information</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Client:</span> {{ viewingExpressClass.client_username || viewingExpressClass.client_email || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Website:</span> {{ viewingExpressClass.website_name || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Status:</span> 
                  <span :class="getStatusClass(viewingExpressClass.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ viewingExpressClass.status_display || viewingExpressClass.status }}
                  </span>
                </div>
                <div><span class="font-medium text-gray-600">Institution:</span> {{ viewingExpressClass.institution || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Course:</span> {{ viewingExpressClass.course || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Discipline:</span> {{ viewingExpressClass.discipline || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Academic Level:</span> {{ viewingExpressClass.academic_level || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Start Date:</span> {{ formatDate(viewingExpressClass.start_date) }}</div>
                <div><span class="font-medium text-gray-600">End Date:</span> {{ formatDate(viewingExpressClass.end_date) }}</div>
              </div>

              <h3 class="text-lg font-semibold border-b pb-2 mt-4">Workload</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Discussion Posts:</span> {{ viewingExpressClass.number_of_discussion_posts || 0 }}</div>
                <div><span class="font-medium text-gray-600">Discussion Replies:</span> {{ viewingExpressClass.number_of_discussion_posts_replies || 0 }}</div>
                <div><span class="font-medium text-gray-600">Assignments:</span> {{ viewingExpressClass.number_of_assignments || 0 }}</div>
                <div><span class="font-medium text-gray-600">Exams:</span> {{ viewingExpressClass.number_of_exams || 0 }}</div>
                <div><span class="font-medium text-gray-600">Quizzes:</span> {{ viewingExpressClass.number_of_quizzes || 0 }}</div>
                <div><span class="font-medium text-gray-600">Projects:</span> {{ viewingExpressClass.number_of_projects || 0 }}</div>
                <div><span class="font-medium text-gray-600">Presentations:</span> {{ viewingExpressClass.number_of_presentations || 0 }}</div>
                <div><span class="font-medium text-gray-600">Papers:</span> {{ viewingExpressClass.number_of_papers || 0 }}</div>
                <div><span class="font-medium text-gray-600">Total Workload:</span> {{ viewingExpressClass.total_workload_in_pages || 'N/A' }}</div>
              </div>
            </div>

            <!-- Right Column -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Pricing & Assignment</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Price:</span> 
                  <span v-if="viewingExpressClass.price" class="font-bold text-green-600">
                    ${{ parseFloat(viewingExpressClass.price || 0).toFixed(2) }}
                  </span>
                  <span v-else class="text-gray-400 italic">Not set</span>
                </div>
                <div><span class="font-medium text-gray-600">Price Approved:</span> 
                  <span :class="viewingExpressClass.price_approved ? 'text-green-600' : 'text-yellow-600'">
                    {{ viewingExpressClass.price_approved ? 'Yes' : 'No' }}
                  </span>
                </div>
                <div><span class="font-medium text-gray-600">Installments:</span> 
                  {{ viewingExpressClass.installments_needed > 0 ? viewingExpressClass.installments_needed + ' installments' : 'Full payment' }}
                </div>
                <div><span class="font-medium text-gray-600">Assigned Writer:</span> 
                  <span v-if="viewingExpressClass.assigned_writer_username">
                    {{ viewingExpressClass.assigned_writer_username }}
                  </span>
                  <button v-else @click="openAssignWriterModal(viewingExpressClass)" class="text-blue-600 hover:underline text-xs">
                    Assign Writer
                  </button>
                </div>
                <div v-if="viewingExpressClass.reviewed_by_username">
                  <span class="font-medium text-gray-600">Reviewed By:</span> {{ viewingExpressClass.reviewed_by_username }}
                </div>
                <div v-if="viewingExpressClass.reviewed_at">
                  <span class="font-medium text-gray-600">Reviewed At:</span> {{ formatDateTime(viewingExpressClass.reviewed_at) }}
                </div>
              </div>

              <h3 class="text-lg font-semibold border-b pb-2 mt-4">School Login</h3>
              <div class="space-y-2 text-sm">
                <div v-if="viewingExpressClass.school_login_link">
                  <span class="font-medium text-gray-600">Login Link:</span>
                  <a :href="viewingExpressClass.school_login_link" target="_blank" class="text-blue-600 hover:underline ml-1">
                    {{ viewingExpressClass.school_login_link }}
                  </a>
                </div>
                <div v-if="viewingExpressClass.school_login_username">
                  <span class="font-medium text-gray-600">Username:</span> {{ viewingExpressClass.school_login_username }}
                </div>
                <div v-if="viewingExpressClass.school_login_password">
                  <span class="font-medium text-gray-600">Password:</span> 
                  <span class="font-mono bg-gray-100 px-2 py-1 rounded">{{ viewingExpressClass.school_login_password }}</span>
                </div>
                <div v-if="!viewingExpressClass.school_login_link && !viewingExpressClass.school_login_username">
                  <span class="text-gray-400 italic">No login credentials provided</span>
                </div>
              </div>

              <h3 class="text-lg font-semibold border-b pb-2 mt-4">Notes</h3>
              <div class="space-y-2 text-sm">
                <div v-if="viewingExpressClass.instructions">
                  <span class="font-medium text-gray-600">Instructions:</span>
                  <p class="mt-1 text-gray-700 whitespace-pre-wrap">{{ viewingExpressClass.instructions }}</p>
                </div>
                <div v-if="viewingExpressClass.scope_review_notes">
                  <span class="font-medium text-gray-600">Scope Review Notes:</span>
                  <p class="mt-1 text-gray-700 whitespace-pre-wrap">{{ viewingExpressClass.scope_review_notes }}</p>
                </div>
                <div v-if="viewingExpressClass.admin_notes">
                  <span class="font-medium text-gray-600">Admin Notes:</span>
                  <p class="mt-1 text-gray-700 whitespace-pre-wrap">{{ viewingExpressClass.admin_notes }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-4 border-t">
            <button 
              v-if="viewingExpressClass.status === 'inquiry' || viewingExpressClass.status === 'scope_review'" 
              @click="openScopeReviewModal(viewingExpressClass)" 
              class="btn btn-primary bg-orange-600 hover:bg-orange-700"
            >
              Review Scope & Set Price
            </button>
            <button 
              v-if="viewingExpressClass.status === 'priced' && !viewingExpressClass.assigned_writer" 
              @click="openAssignWriterModal(viewingExpressClass)" 
              class="btn btn-primary bg-indigo-600 hover:bg-indigo-700"
            >
              Assign Writer
            </button>
            <button 
              v-if="viewingExpressClass.status === 'assigned'" 
              @click="startProgress(viewingExpressClass)" 
              class="btn btn-primary bg-green-600 hover:bg-green-700"
            >
              Start Progress
            </button>
            <button 
              v-if="viewingExpressClass.status === 'in_progress'" 
              @click="completeExpressClass(viewingExpressClass)" 
              class="btn btn-primary bg-purple-600 hover:bg-purple-700"
            >
              Mark Complete
            </button>
            <button @click="showThreadsModal = true" class="btn btn-primary bg-blue-600 hover:bg-blue-700">
              💬 View Messages
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Scope Review Modal -->
    <div v-if="showScopeReviewModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Review Scope & Set Price</h3>
          <button @click="closeScopeReviewModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Scope Review Notes *</label>
            <textarea 
              v-model="scopeReviewForm.scope_review_notes" 
              rows="5" 
              class="w-full border rounded px-3 py-2"
              placeholder="Enter your scope review notes..."
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Price *</label>
            <input 
              v-model.number="scopeReviewForm.price" 
              type="number" 
              step="0.01" 
              class="w-full border rounded px-3 py-2"
              placeholder="0.00"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Installments Needed</label>
            <input 
              v-model.number="scopeReviewForm.installments_needed" 
              type="number" 
              min="0" 
              class="w-full border rounded px-3 py-2"
              placeholder="0 for full payment"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Admin Notes (optional)</label>
            <textarea 
              v-model="scopeReviewForm.admin_notes" 
              rows="3" 
              class="w-full border rounded px-3 py-2"
              placeholder="Optional admin notes..."
            ></textarea>
          </div>
          <div class="flex gap-2 pt-4">
            <button @click="saveScopeReview" class="btn btn-primary flex-1">Save Review</button>
            <button @click="closeScopeReviewModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign Writer Modal -->
    <div v-if="showAssignWriterModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Assign Writer</h3>
          <button @click="closeAssignWriterModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Writer *</label>
            <select v-model.number="assignWriterForm.writer_id" class="w-full border rounded px-3 py-2">
              <option value="">Select writer...</option>
              <option v-for="writer in writers" :key="writer.id" :value="writer.id">
                {{ formatWriterName(writer) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Admin Notes (optional)</label>
            <textarea 
              v-model="assignWriterForm.admin_notes" 
              rows="3" 
              class="w-full border rounded px-3 py-2"
              placeholder="Optional notes..."
            ></textarea>
          </div>
          <div class="flex gap-2 pt-4">
            <button @click="saveAssignWriter" class="btn btn-primary flex-1">Assign Writer</button>
            <button @click="closeAssignWriterModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Threads Modal -->
    <ClassMessageThreads
      v-if="viewingExpressClass"
      :show="showThreadsModal"
      :class-id="viewingExpressClass.id"
      class-type="express"
      @close="showThreadsModal = false"
    />

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Loading State -->
  <div v-else-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { expressClassesAPI, usersAPI } from '@/api'
import apiClient from '@/api/client'
import { formatWriterName } from '@/utils/formatDisplay'
import ClassMessageThreads from '@/components/classes/ClassMessageThreads.vue'

const componentError = ref(null)
const initialLoading = ref(true)
const loading = ref(false)
const expressClasses = ref([])
const websites = ref([])
const writers = ref([])
const viewingExpressClass = ref(null)
const showScopeReviewModal = ref(false)
const showAssignWriterModal = ref(false)
const showThreadsModal = ref(false)
const currentExpressClassForAction = ref(null)

const filters = ref({
  status: '',
  search: '',
  website: '',
  has_writer: '',
})

const stats = ref({
  total: 0,
  inquiry: 0,
  scope_review: 0,
  priced: 0,
  assigned: 0,
  in_progress: 0,
  completed: 0,
})

const scopeReviewForm = ref({
  scope_review_notes: '',
  price: 0,
  installments_needed: 0,
  admin_notes: '',
})

const assignWriterForm = ref({
  writer_id: '',
  admin_notes: '',
})

const message = ref('')
const messageSuccess = ref(false)

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadExpressClasses()
  }, 500)
}

const loadExpressClasses = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website
    if (filters.value.has_writer !== '') {
      if (filters.value.has_writer === 'true') {
        params.assigned_writer__isnull = false
      } else {
        params.assigned_writer__isnull = true
      }
    }

    const res = await expressClassesAPI.list(params)
    expressClasses.value = res.data.results || res.data || []
    
    // Calculate stats
    stats.value.total = expressClasses.value.length
    stats.value.inquiry = expressClasses.value.filter(c => c.status === 'inquiry').length
    stats.value.scope_review = expressClasses.value.filter(c => c.status === 'scope_review').length
    stats.value.priced = expressClasses.value.filter(c => c.status === 'priced').length
    stats.value.assigned = expressClasses.value.filter(c => c.status === 'assigned').length
    stats.value.in_progress = expressClasses.value.filter(c => c.status === 'in_progress').length
    stats.value.completed = expressClasses.value.filter(c => c.status === 'completed').length
  } catch (error) {
    console.error('Error loading express classes:', error)
    showMessage('Failed to load express classes: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading websites:', error)
  }
}

const loadWriters = async () => {
  try {
    const res = await usersAPI.list({ role: 'writer' })
    writers.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading writers:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    search: '',
    website: '',
    has_writer: '',
  }
  loadExpressClasses()
}

const viewExpressClass = async (expressClass) => {
  try {
    const res = await expressClassesAPI.get(expressClass.id)
    viewingExpressClass.value = res.data
  } catch (error) {
    console.error('Error loading express class:', error)
    showMessage('Failed to load express class details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openScopeReviewModal = (expressClass) => {
  currentExpressClassForAction.value = expressClass
  scopeReviewForm.value = {
    scope_review_notes: expressClass.scope_review_notes || '',
    price: expressClass.price || 0,
    installments_needed: expressClass.installments_needed || 0,
    admin_notes: expressClass.admin_notes || '',
  }
  showScopeReviewModal.value = true
}

const closeScopeReviewModal = () => {
  showScopeReviewModal.value = false
  currentExpressClassForAction.value = null
  scopeReviewForm.value = {
    scope_review_notes: '',
    price: 0,
    installments_needed: 0,
    admin_notes: '',
  }
}

const saveScopeReview = async () => {
  if (!currentExpressClassForAction.value) return
  
  try {
    await expressClassesAPI.reviewScope(currentExpressClassForAction.value.id, scopeReviewForm.value)
    showMessage('Scope reviewed and price set successfully', true)
    closeScopeReviewModal()
    if (viewingExpressClass.value && viewingExpressClass.value.id === currentExpressClassForAction.value.id) {
      await viewExpressClass(currentExpressClassForAction.value)
    }
    loadExpressClasses()
  } catch (error) {
    showMessage('Failed to review scope: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openAssignWriterModal = (expressClass) => {
  currentExpressClassForAction.value = expressClass
  assignWriterForm.value = {
    writer_id: expressClass.assigned_writer || '',
    admin_notes: '',
  }
  showAssignWriterModal.value = true
}

const closeAssignWriterModal = () => {
  showAssignWriterModal.value = false
  currentExpressClassForAction.value = null
  assignWriterForm.value = {
    writer_id: '',
    admin_notes: '',
  }
}

const saveAssignWriter = async () => {
  if (!currentExpressClassForAction.value) return
  
  try {
    await expressClassesAPI.assignWriter(currentExpressClassForAction.value.id, assignWriterForm.value)
    showMessage('Writer assigned successfully', true)
    closeAssignWriterModal()
    if (viewingExpressClass.value && viewingExpressClass.value.id === currentExpressClassForAction.value.id) {
      await viewExpressClass(currentExpressClassForAction.value)
    }
    loadExpressClasses()
  } catch (error) {
    showMessage('Failed to assign writer: ' + (error.response?.data?.detail || error.message), false)
  }
}

const startProgress = async (expressClass) => {
  try {
    await expressClassesAPI.startProgress(expressClass.id)
    showMessage('Progress started successfully', true)
    if (viewingExpressClass.value && viewingExpressClass.value.id === expressClass.id) {
      await viewExpressClass(expressClass)
    }
    loadExpressClasses()
  } catch (error) {
    showMessage('Failed to start progress: ' + (error.response?.data?.detail || error.message), false)
  }
}

const completeExpressClass = async (expressClass) => {
  if (!confirm('Are you sure you want to mark this express class as completed?')) return
  
  try {
    await expressClassesAPI.complete(expressClass.id)
    showMessage('Express class marked as completed', true)
    if (viewingExpressClass.value && viewingExpressClass.value.id === expressClass.id) {
      await viewExpressClass(expressClass)
    }
    loadExpressClasses()
  } catch (error) {
    showMessage('Failed to complete express class: ' + (error.response?.data?.detail || error.message), false)
  }
}

const getStatusClass = (status) => {
  const classes = {
    'inquiry': 'bg-yellow-100 text-yellow-800',
    'scope_review': 'bg-orange-100 text-orange-800',
    'priced': 'bg-purple-100 text-purple-800',
    'assigned': 'bg-indigo-100 text-indigo-800',
    'in_progress': 'bg-green-100 text-green-800',
    'completed': 'bg-gray-100 text-gray-800',
    'cancelled': 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

// Threads are now handled by ClassMessageThreads component

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(async () => {
  try {
    await Promise.all([
      loadExpressClasses(),
      loadWebsites(),
      loadWriters()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing ExpressClassesManagement:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

