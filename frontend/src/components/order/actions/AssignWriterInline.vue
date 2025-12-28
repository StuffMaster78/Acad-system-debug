<template>
  <div class="space-y-4">
    <!-- Order Summary -->
    <div v-if="order" class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <span class="text-gray-500 dark:text-gray-400">Pages:</span>
          <span class="ml-2 font-medium">{{ order.number_of_pages || 'N/A' }}</span>
        </div>
        <div>
          <span class="text-gray-500 dark:text-gray-400">Deadline:</span>
          <span class="ml-2 font-medium">{{ formatDate(order.client_deadline) }}</span>
        </div>
        <div>
          <span class="text-gray-500 dark:text-gray-400">Type:</span>
          <span class="ml-2 font-medium">{{ order.type_of_work?.name || 'N/A' }}</span>
        </div>
        <div>
          <span class="text-gray-500 dark:text-gray-400">Level:</span>
          <span class="ml-2 font-medium">{{ order.academic_level?.name || 'N/A' }}</span>
        </div>
      </div>
    </div>

    <!-- Payment Warning -->
    <div v-if="!order?.is_paid" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
      <div class="flex items-start gap-3">
        <span class="text-xl">⚠️</span>
        <div>
          <p class="font-semibold text-yellow-800 dark:text-yellow-200">Order Not Paid</p>
          <p class="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
            This order must be marked as paid before assigning a writer.
          </p>
        </div>
      </div>
    </div>

    <!-- Writer Search -->
    <div v-else>
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Search Writers
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            v-model="writerSearch"
            type="text"
            placeholder="Search by name, email, or level..."
            class="w-full pl-10 pr-4 py-2.5 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
      </div>

      <!-- Writers List -->
      <div v-if="loadingWriters" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading writers...</p>
      </div>

      <div v-else-if="filteredWriters.length === 0" class="text-center py-8 text-gray-500">
        <p>No writers found</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
        <div
          v-for="writer in filteredWriters"
          :key="writer.id"
          @click="selectWriter(writer.id)"
          :class="[
            'p-4 border-2 rounded-lg cursor-pointer transition-all',
            form.writerId === writer.id
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
              : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md'
          ]"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold">
                  {{ (writer.username || writer.email || 'W')[0].toUpperCase() }}
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 dark:text-white">{{ formatWriterName(writer) }}</h4>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ writer.email }}</p>
                </div>
              </div>
              <div class="flex flex-wrap gap-2 mt-2">
                <span v-if="writer.profile?.writer_level" class="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-full font-medium">
                  {{ writer.profile.writer_level.name || 'Level ' + (writer.profile.writer_level.level || 'N/A') }}
                </span>
                <span v-if="writer.workload" class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full font-medium">
                  {{ writer.workload.active_orders_count || 0 }}/{{ writer.workload.max_orders || 5 }} orders
                </span>
                <span v-if="writer.workload?.capacity !== undefined && writer.workload.capacity > 0" class="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                  {{ writer.workload.capacity }} slot{{ writer.workload.capacity !== 1 ? 's' : '' }} available
                </span>
                <span v-else-if="writer.workload?.capacity === 0" class="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-xs rounded-full">
                  Full
                </span>
                <span v-if="writer.profile?.rating" class="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs rounded-full">
                  ⭐ {{ writer.profile.rating.toFixed(1) }}
                </span>
              </div>
            </div>
            <div v-if="form.writerId === writer.id" class="shrink-0">
              <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reason Input -->
      <div v-if="form.writerId" class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Assignment Reason (Optional)
        </label>
        <textarea
          v-model="form.reason"
          placeholder="Add any notes or instructions for this assignment..."
          rows="3"
          class="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white resize-none"
        ></textarea>
      </div>

      <!-- Submit Button -->
      <div v-if="form.writerId" class="mt-6 flex gap-3">
        <button
          @click="handleCancel"
          class="flex-1 px-4 py-2.5 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="handleSubmit"
          :disabled="assigning"
          class="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <svg v-if="assigning" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ assigning ? 'Assigning...' : (isReassign ? 'Reassign Writer' : 'Assign Writer') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ordersAPI, usersAPI } from '@/api'
import { formatWriterName } from '@/utils/formatDisplay'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  order: {
    type: Object,
    required: true
  },
  isReassign: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['success', 'error'])

const { success: showSuccessToast, error: showErrorToast } = useToast()

const form = ref({
  writerId: '',
  reason: ''
})

const writerSearch = ref('')
const writers = ref([])
const loadingWriters = ref(false)
const assigning = ref(false)

const filteredWriters = computed(() => {
  if (!writerSearch.value) return writers.value
  const search = writerSearch.value.toLowerCase()
  return writers.value.filter(writer => {
    const name = formatWriterName(writer).toLowerCase()
    const email = (writer.email || '').toLowerCase()
    const level = (writer.profile?.writer_level?.name || writer.profile?.writer_level?.level || '').toLowerCase()
    return name.includes(search) || email.includes(search) || level.includes(search)
  })
})

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const loadWriters = async () => {
  loadingWriters.value = true
  try {
    const res = await usersAPI.list({ role: 'writer', page_size: 100 })
    const allWriters = res.data.results || res.data || []
    
    // Load workload for each writer
    const writersWithWorkload = await Promise.all(
      allWriters.map(async (writer) => {
        try {
          const workloadRes = await usersAPI.getWriterWorkload(writer.id)
          return { ...writer, workload: workloadRes.data }
        } catch {
          return { ...writer, workload: null }
        }
      })
    )
    
    writers.value = writersWithWorkload
  } catch (error) {
    console.error('Error loading writers:', error)
    showErrorToast('Failed to load writers')
  } finally {
    loadingWriters.value = false
  }
}

const selectWriter = (writerId) => {
  form.value.writerId = form.value.writerId === writerId ? '' : writerId
}

const handleSubmit = async () => {
  if (!form.value.writerId) return
  
  assigning.value = true
  try {
    const writer = writers.value.find(w => w.id === form.value.writerId)
    const writerName = writer ? formatWriterName(writer) : 'selected writer'
    
    if (props.isReassign) {
      await ordersAPI.reassignWriter(props.order.id, form.value.writerId, form.value.reason)
      showSuccessToast(`Order #${props.order.id} has been reassigned to ${writerName} successfully!`)
    } else {
      await ordersAPI.assignWriter(props.order.id, form.value.writerId, form.value.reason)
      showSuccessToast(`Order #${props.order.id} has been assigned to ${writerName} successfully!`)
    }
    
    emit('success', { action: props.isReassign ? 'reassign' : 'assign', writerId: form.value.writerId })
    
    // Reset form
    form.value = { writerId: '', reason: '' }
    writerSearch.value = ''
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to assign writer'
    showErrorToast(errorMsg)
    emit('error', error)
  } finally {
    assigning.value = false
  }
}

const handleCancel = () => {
  form.value = { writerId: '', reason: '' }
  writerSearch.value = ''
  emit('error', { cancelled: true })
}

onMounted(() => {
  if (props.order?.is_paid) {
    loadWriters()
  }
})
</script>

