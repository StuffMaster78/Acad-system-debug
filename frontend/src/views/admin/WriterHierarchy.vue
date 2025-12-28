<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Writer Hierarchy</h1>
        <p class="mt-2 text-gray-600">Manage writer levels, earning structures, and progression requirements</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <span class="mr-2">➕</span>
        Create Level
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <div class="p-4">
          <p class="text-sm font-medium text-gray-600">Total Levels</p>
          <p class="text-3xl font-bold text-blue-700 mt-1">{{ levels.length }}</p>
        </div>
      </div>
      <div class="card bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <div class="p-4">
          <p class="text-sm font-medium text-gray-600">Active Levels</p>
          <p class="text-3xl font-bold text-green-700 mt-1">{{ activeLevelsCount }}</p>
        </div>
      </div>
      <div class="card bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <div class="p-4">
          <p class="text-sm font-medium text-gray-600">Total Writers</p>
          <p class="text-3xl font-bold text-purple-700 mt-1">{{ totalWriters }}</p>
        </div>
      </div>
      <div class="card bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <div class="p-4">
          <p class="text-sm font-medium text-gray-600">Earning Modes</p>
          <p class="text-3xl font-bold text-yellow-700 mt-1">{{ uniqueEarningModes }}</p>
        </div>
      </div>
    </div>

    <!-- Levels Table -->
    <div class="card">
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-gray-600">Loading levels...</p>
      </div>
      <div v-else-if="levels.length" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gradient-to-r from-gray-50 to-gray-100">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Level</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Earning Mode</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Earnings</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Writers</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Max Orders</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="level in sortedLevels" :key="level.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="text-sm font-bold text-gray-900">{{ level.name }}</div>
                  <div v-if="level.description" class="text-xs text-gray-500 mt-1 line-clamp-1">{{ level.description }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full"
                      :class="getEarningModeClass(level.earning_mode)">
                  {{ formatEarningMode(level.earning_mode) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm">
                  <div v-if="level.earning_mode === 'fixed_per_page'" class="font-medium text-green-700">
                    ${{ parseFloat(level.base_pay_per_page || 0).toFixed(2) }}/page
                  </div>
                  <div v-else-if="level.earning_mode === 'percentage_of_order_cost'" class="font-medium text-green-700">
                    {{ parseFloat(level.earnings_percentage_of_cost || 0).toFixed(1) }}% of cost
                  </div>
                  <div v-else-if="level.earning_mode === 'percentage_of_order_total'" class="font-medium text-green-700">
                    {{ parseFloat(level.earnings_percentage_of_total || 0).toFixed(1) }}% of total
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-medium text-gray-900">{{ level.writers_count || 0 }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-600">{{ level.max_orders || 0 }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="level.is_active 
                  ? 'px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800'
                  : 'px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800'">
                  {{ level.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="viewLevel(level)" class="text-blue-600 hover:text-blue-900 mr-3">View</button>
                <button @click="editLevel(level)" class="text-indigo-600 hover:text-indigo-900 mr-3">Edit</button>
                <button @click="testEarnings(level)" class="text-green-600 hover:text-green-900 mr-3">Test</button>
                <button @click="deleteLevel(level.id)" class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-12 text-gray-500">
        <div class="text-4xl mb-2">📊</div>
        <p>No writer levels found.</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create First Level</button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingLevel" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ editingLevel ? 'Edit Level' : 'Create New Level' }}
          </h2>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="p-6 space-y-6">
          <!-- Basic Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Level Name *</label>
              <input v-model="levelForm.name" type="text" class="input" placeholder="e.g., Novice, Intermediate, Expert" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Display Order *</label>
              <input v-model.number="levelForm.display_order" type="number" class="input" placeholder="Lower = higher level" />
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="levelForm.description" rows="2" class="input" placeholder="Description of this level and its benefits"></textarea>
          </div>

          <!-- Earning Mode -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Earning Mode *</label>
            <select v-model="levelForm.earning_mode" class="input">
              <option value="fixed_per_page">Fixed Per Page/Slide</option>
              <option value="percentage_of_order_cost">Percentage of Order Cost</option>
              <option value="percentage_of_order_total">Percentage of Order Total</option>
            </select>
          </div>

          <!-- Earning Configuration -->
          <div v-if="levelForm.earning_mode === 'fixed_per_page'" class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Base Pay Per Page ($) *</label>
              <input v-model.number="levelForm.base_pay_per_page" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Base Pay Per Slide ($)</label>
              <input v-model.number="levelForm.base_pay_per_slide" type="number" step="0.01" class="input" />
            </div>
          </div>

          <div v-else-if="levelForm.earning_mode === 'percentage_of_order_cost'" class="p-4 bg-green-50 rounded-lg border border-green-200">
            <label class="block text-sm font-medium text-gray-700 mb-1">Earnings Percentage of Cost (%) *</label>
            <input v-model.number="levelForm.earnings_percentage_of_cost" type="number" step="0.01" class="input" />
            <p class="text-xs text-gray-600 mt-1">Percentage of order cost (before discounts) writer earns</p>
          </div>

          <div v-else-if="levelForm.earning_mode === 'percentage_of_order_total'" class="p-4 bg-green-50 rounded-lg border border-green-200">
            <label class="block text-sm font-medium text-gray-700 mb-1">Earnings Percentage of Total (%) *</label>
            <input v-model.number="levelForm.earnings_percentage_of_total" type="number" step="0.01" class="input" />
            <p class="text-xs text-gray-600 mt-1">Percentage of order total (after discounts) writer earns</p>
          </div>

          <!-- Urgency & Technical Adjustments -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Urgency % Increase</label>
              <input v-model.number="levelForm.urgency_percentage_increase" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Urgency Additional Per Page ($)</label>
              <input v-model.number="levelForm.urgency_additional_per_page" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Urgent Deadline Hours</label>
              <input v-model.number="levelForm.urgent_order_deadline_hours" type="number" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Technical Adjustment Per Page ($)</label>
              <input v-model.number="levelForm.technical_order_adjustment_per_page" type="number" step="0.01" class="input" />
            </div>
          </div>

          <!-- Bonuses -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Bonus Per Order Completed ($)</label>
              <input v-model.number="levelForm.bonus_per_order_completed" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Bonus Per Rating Above Threshold ($)</label>
              <input v-model.number="levelForm.bonus_per_rating_above_threshold" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Rating Threshold for Bonus</label>
              <input v-model.number="levelForm.rating_threshold_for_bonus" type="number" step="0.01" class="input" />
            </div>
          </div>

          <!-- Progression Requirements -->
          <div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Progression Requirements</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Min Orders to Attain</label>
                <input v-model.number="levelForm.min_orders_to_attain" type="number" class="input" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Min Rating to Attain</label>
                <input v-model.number="levelForm.min_rating_to_attain" type="number" step="0.01" class="input" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Min Takes to Attain</label>
                <input v-model.number="levelForm.min_takes_to_attain" type="number" class="input" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Min Completion Rate (%)</label>
                <input v-model.number="levelForm.min_completion_rate" type="number" step="0.01" class="input" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Max Revision Rate (%)</label>
                <input v-model.number="levelForm.max_revision_rate" type="number" step="0.01" class="input" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Max Lateness Rate (%)</label>
                <input v-model.number="levelForm.max_lateness_rate" type="number" step="0.01" class="input" />
              </div>
            </div>
          </div>

          <!-- Other Settings -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Max Orders</label>
              <input v-model.number="levelForm.max_orders" type="number" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Deadline Percentage (%)</label>
              <input v-model.number="levelForm.deadline_percentage" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tips Percentage (%)</label>
              <input v-model.number="levelForm.tips_percentage" type="number" step="0.01" class="input" />
            </div>
            <div class="flex items-center">
              <input v-model="levelForm.is_active" type="checkbox" id="is_active" class="mr-2" />
              <label for="is_active" class="text-sm font-medium text-gray-700">Active</label>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button @click="saveLevel" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingLevel ? 'Update' : 'Create') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Test Earnings Modal -->
    <div v-if="showTestModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900">Test Earnings Calculation</h2>
          <button @click="showTestModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Pages</label>
              <input v-model.number="testParams.pages" type="number" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Slides</label>
              <input v-model.number="testParams.slides" type="number" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Order Total ($)</label>
              <input v-model.number="testParams.order_total" type="number" step="0.01" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Order Cost ($)</label>
              <input v-model.number="testParams.order_cost" type="number" step="0.01" class="input" />
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input v-model="testParams.is_urgent" type="checkbox" class="mr-2" />
              <span class="text-sm text-gray-700">Urgent Order</span>
            </label>
            <label class="flex items-center">
              <input v-model="testParams.is_technical" type="checkbox" class="mr-2" />
              <span class="text-sm text-gray-700">Technical Order</span>
            </label>
          </div>
          <button @click="calculateTestEarnings" class="btn btn-primary w-full">Calculate Earnings</button>
          
          <div v-if="testResults" class="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 class="font-semibold text-gray-900 mb-2">Results:</h3>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Base Earnings:</span>
                <span class="font-medium">${{ testResults.base_earnings?.toFixed(2) || '0.00' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Urgency Bonus:</span>
                <span class="font-medium">${{ testResults.urgency_bonus?.toFixed(2) || '0.00' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Technical Bonus:</span>
                <span class="font-medium">${{ testResults.technical_bonus?.toFixed(2) || '0.00' }}</span>
              </div>
              <div class="flex justify-between pt-2 border-t border-green-200">
                <span class="font-bold text-gray-900">Total Earnings:</span>
                <span class="font-bold text-green-700 text-lg">${{ testResults.total_earnings?.toFixed(2) || '0.00' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'
import apiClient from '@/api/client'

const { success, error } = useToast()

const loading = ref(false)
const saving = ref(false)
const levels = ref([])
const showCreateModal = ref(false)
const editingLevel = ref(null)
const showTestModal = ref(false)
const testParams = ref({
  pages: 10,
  slides: 0,
  order_total: 100,
  order_cost: 100,
  is_urgent: false,
  is_technical: false
})
const testResults = ref(null)

const levelForm = ref({
  name: '',
  description: '',
  earning_mode: 'fixed_per_page',
  base_pay_per_page: 0,
  base_pay_per_slide: 0,
  earnings_percentage_of_cost: 0,
  earnings_percentage_of_total: 0,
  urgency_percentage_increase: 0,
  urgency_additional_per_page: 0,
  urgent_order_deadline_hours: 8,
  technical_order_adjustment_per_page: 0,
  technical_order_adjustment_per_slide: 0,
  deadline_percentage: 80,
  tips_percentage: 100,
  min_orders_to_attain: 0,
  min_rating_to_attain: 0,
  min_takes_to_attain: 0,
  min_completion_rate: 0,
  max_revision_rate: null,
  max_lateness_rate: null,
  bonus_per_order_completed: 0,
  bonus_per_rating_above_threshold: 0,
  rating_threshold_for_bonus: 4.5,
  max_orders: 10,
  display_order: 0,
  is_active: true,
  website: null
})

const activeLevelsCount = computed(() => levels.value.filter(l => l.is_active).length)
const totalWriters = computed(() => levels.value.reduce((sum, l) => sum + (l.writers_count || 0), 0))
const uniqueEarningModes = computed(() => new Set(levels.value.map(l => l.earning_mode)).size)
const sortedLevels = computed(() => [...levels.value].sort((a, b) => (a.display_order || 0) - (b.display_order || 0)))

const loadLevels = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/writer-management/writer-levels/')
    levels.value = response.data.results || response.data
  } catch (err) {
    error(getErrorMessage(err))
  } finally {
    loading.value = false
  }
}

const saveLevel = async () => {
  saving.value = true
  try {
    if (editingLevel.value) {
      await apiClient.put(`/writer-management/writer-levels/${editingLevel.value.id}/`, levelForm.value)
      success('Level updated successfully')
    } else {
      await apiClient.post('/writer-management/writer-levels/', levelForm.value)
      success('Level created successfully')
    }
    closeModal()
    loadLevels()
  } catch (err) {
    error(getErrorMessage(err))
  } finally {
    saving.value = false
  }
}

const editLevel = (level) => {
  editingLevel.value = level
  Object.assign(levelForm.value, level)
  showCreateModal.value = true
}

const viewLevel = (level) => {
  // Could open a detailed view modal
  editLevel(level)
}

const deleteLevel = async (id) => {
  if (!confirm('Are you sure you want to delete this level?')) return
  try {
    await apiClient.delete(`/writer-management/writer-levels/${id}/`)
    success('Level deleted successfully')
    loadLevels()
  } catch (err) {
    error(getErrorMessage(err))
  }
}

const testEarnings = (level) => {
  editingLevel.value = level
  showTestModal.value = true
}

const calculateTestEarnings = async () => {
  if (!editingLevel.value) return
  try {
    const params = {
      pages: testParams.value.pages || 0,
      slides: testParams.value.slides || 0,
      is_urgent: testParams.value.is_urgent,
      is_technical: testParams.value.is_technical
    }
    if (testParams.value.order_total) params.order_total = testParams.value.order_total
    if (testParams.value.order_cost) params.order_cost = testParams.value.order_cost
    
    const response = await apiClient.post(
      `/writer-management/writer-levels/${editingLevel.value.id}/calculate_sample_earnings/`,
      params
    )
    testResults.value = response.data.earnings
  } catch (err) {
    error(getErrorMessage(err))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingLevel.value = null
  Object.assign(levelForm.value, {
    name: '',
    description: '',
    earning_mode: 'fixed_per_page',
    base_pay_per_page: 0,
    base_pay_per_slide: 0,
    earnings_percentage_of_cost: 0,
    earnings_percentage_of_total: 0,
    urgency_percentage_increase: 0,
    urgency_additional_per_page: 0,
    urgent_order_deadline_hours: 8,
    technical_order_adjustment_per_page: 0,
    technical_order_adjustment_per_slide: 0,
    deadline_percentage: 80,
    tips_percentage: 100,
    min_orders_to_attain: 0,
    min_rating_to_attain: 0,
    min_takes_to_attain: 0,
    min_completion_rate: 0,
    max_revision_rate: null,
    max_lateness_rate: null,
    bonus_per_order_completed: 0,
    bonus_per_rating_above_threshold: 0,
    rating_threshold_for_bonus: 4.5,
    max_orders: 10,
    display_order: 0,
    is_active: true,
    website: null
  })
}

const formatEarningMode = (mode) => {
  const modes = {
    'fixed_per_page': 'Fixed Per Page',
    'percentage_of_order_cost': '% of Cost',
    'percentage_of_order_total': '% of Total'
  }
  return modes[mode] || mode
}

const getEarningModeClass = (mode) => {
  const classes = {
    'fixed_per_page': 'bg-blue-100 text-blue-800',
    'percentage_of_order_cost': 'bg-green-100 text-green-800',
    'percentage_of_order_total': 'bg-purple-100 text-purple-800'
  }
  return classes[mode] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  loadLevels()
})
</script>

