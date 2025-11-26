<template>
  <div class="space-y-6 p-6">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Writer Profile Settings</h1>
      <p class="mt-2 text-gray-600">Manage your pen name and profile visibility</p>
    </div>

    <!-- Pen Name Management Link -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-semibold mb-4">Pen Name</h2>
      <p class="text-sm text-gray-600 mb-4">
        Your pen name is what clients will see instead of your real name. 
        This helps maintain privacy while working with clients.
      </p>
      
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <p class="text-sm text-blue-800 mb-3">
          <strong>Privacy Note:</strong> Clients will only see your pen name (or registration ID) and will not have access to your real name, email, or other personal information.
        </p>
        <router-link
          to="/writer/pen-name"
          class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
        >
          Manage Pen Name →
        </router-link>
      </div>

      <!-- Current Display Info -->
      <div class="space-y-3">
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <span class="text-sm font-medium text-gray-600">Display Name:</span>
          <span class="font-mono font-semibold">{{ displayName }}</span>
        </div>
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <span class="text-sm font-medium text-gray-600">Registration ID:</span>
          <span class="font-mono">{{ registrationId }}</span>
        </div>
      </div>
    </div>

    <!-- Writer Hierarchy Information -->
    <div v-if="writerProfile?.writer_level_details" class="bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50 rounded-lg shadow-sm p-6 border-2 border-indigo-200">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-bold text-gray-900">Writer Hierarchy</h2>
          <p class="text-sm text-gray-600 mt-1">Your current level and earning structure</p>
        </div>
        <span class="text-3xl">📊</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <!-- Current Level Badge -->
        <div class="bg-white rounded-lg p-4 border-2 border-indigo-300 text-center">
          <p class="text-xs text-gray-600 mb-1">Current Level</p>
          <p class="text-2xl font-bold text-indigo-700">{{ writerProfile.writer_level_details?.name || 'Not Assigned' }}</p>
          <p v-if="writerProfile.writer_level_details?.description" class="text-xs text-gray-500 mt-2 line-clamp-2">
            {{ writerProfile.writer_level_details.description }}
          </p>
        </div>
        
        <!-- Earning Summary -->
        <div class="bg-white rounded-lg p-4 border-2 border-green-300 text-center">
          <p class="text-xs text-gray-600 mb-1">Earning Rate</p>
          <div v-if="writerProfile.writer_level_details?.earning_mode === 'fixed_per_page'">
            <p class="text-xl font-bold text-green-700">${{ parseFloat(writerProfile.writer_level_details.base_pay_per_page || 0).toFixed(2) }}/page</p>
            <p v-if="writerProfile.writer_level_details.base_pay_per_slide > 0" class="text-xs text-gray-600 mt-1">
              ${{ parseFloat(writerProfile.writer_level_details.base_pay_per_slide || 0).toFixed(2) }}/slide
            </p>
          </div>
          <div v-else-if="writerProfile.writer_level_details?.earning_mode === 'percentage_of_order_cost'">
            <p class="text-xl font-bold text-green-700">{{ parseFloat(writerProfile.writer_level_details.earnings_percentage_of_cost || 0).toFixed(1) }}%</p>
            <p class="text-xs text-gray-600 mt-1">of order cost</p>
          </div>
          <div v-else-if="writerProfile.writer_level_details?.earning_mode === 'percentage_of_order_total'">
            <p class="text-xl font-bold text-green-700">{{ parseFloat(writerProfile.writer_level_details.earnings_percentage_of_total || 0).toFixed(1) }}%</p>
            <p class="text-xs text-gray-600 mt-1">of order total</p>
          </div>
          <p v-else class="text-sm text-gray-500">Not configured</p>
        </div>
        
        <!-- Capacity Status -->
        <div class="bg-white rounded-lg p-4 border-2 border-purple-300 text-center">
          <p class="text-xs text-gray-600 mb-1">Order Capacity</p>
          <p class="text-xl font-bold text-purple-700">
            {{ writerProfile.active_orders || 0 }} / {{ writerProfile.writer_level_details?.max_orders || 0 }}
          </p>
          <div class="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              class="h-2 rounded-full transition-all"
              :class="{
                'bg-green-500': (writerProfile.active_orders || 0) < (writerProfile.writer_level_details?.max_orders || 1) * 0.7,
                'bg-yellow-500': (writerProfile.active_orders || 0) >= (writerProfile.writer_level_details?.max_orders || 1) * 0.7 && (writerProfile.active_orders || 0) < (writerProfile.writer_level_details?.max_orders || 1) * 0.9,
                'bg-red-500': (writerProfile.active_orders || 0) >= (writerProfile.writer_level_details?.max_orders || 1) * 0.9
              }"
              :style="{ width: `${Math.min(((writerProfile.active_orders || 0) / (writerProfile.writer_level_details?.max_orders || 1)) * 100, 100)}%` }"
            ></div>
          </div>
          <p class="text-xs text-gray-500 mt-1">Current takes / Max allowed</p>
        </div>
      </div>

      <!-- Quick Reference -->
      <div class="bg-white rounded-lg p-4 border border-indigo-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Quick Reference</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div>
            <p class="text-gray-500">Urgency Hours:</p>
            <p class="font-semibold">{{ writerProfile.writer_level_details?.urgent_order_deadline_hours || 0 }}h</p>
          </div>
          <div>
            <p class="text-gray-500">Urgency Bonus:</p>
            <p class="font-semibold">+{{ parseFloat(writerProfile.writer_level_details?.urgency_percentage_increase || 0).toFixed(0) }}%</p>
          </div>
          <div>
            <p class="text-gray-500">Technical Bonus:</p>
            <p class="font-semibold">+${{ parseFloat(writerProfile.writer_level_details?.technical_order_adjustment_per_page || 0).toFixed(2) }}/page</p>
          </div>
          <div>
            <p class="text-gray-500">Tips Share:</p>
            <p class="font-semibold">{{ parseFloat(writerProfile.writer_level_details?.tips_percentage || 0).toFixed(0) }}%</p>
          </div>
        </div>
      </div>

      <!-- Next Level Progress -->
      <div v-if="writerProfile.next_level_info" class="mt-4 bg-white rounded-lg p-4 border border-purple-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Next Level: {{ writerProfile.next_level_info.next_level?.name || 'N/A' }}</h3>
        <div v-if="writerProfile.next_level_info.is_eligible" class="p-2 bg-green-100 border border-green-300 rounded">
          <p class="text-xs font-medium text-green-800">✅ You're eligible for this level!</p>
        </div>
        <div v-else class="space-y-2">
          <div v-if="writerProfile.next_level_info.requirements" class="text-xs space-y-1">
            <div v-if="writerProfile.next_level_info.requirements.min_orders" class="flex justify-between">
              <span class="text-gray-600">Orders:</span>
              <span class="font-medium">{{ writerProfile.completed_orders || 0 }}/{{ writerProfile.next_level_info.requirements.min_orders }}</span>
            </div>
            <div v-if="writerProfile.next_level_info.requirements.min_rating" class="flex justify-between">
              <span class="text-gray-600">Rating:</span>
              <span class="font-medium">{{ parseFloat(writerProfile.average_rating || 0).toFixed(1) }}/{{ parseFloat(writerProfile.next_level_info.requirements.min_rating).toFixed(1) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Toast -->
    <div
      v-if="message"
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50"
      :class="messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'

const authStore = useAuthStore()

const writerProfile = ref(null)
const loading = ref(false)
const saving = ref(false)
const penNameForm = ref({
  pen_name: ''
})

const registrationId = computed(() => {
  return writerProfile.value?.registration_id || 'N/A'
})

const displayName = computed(() => {
  if (writerProfile.value?.pen_name) {
    return writerProfile.value.pen_name
  }
  return registrationId.value
})

const loadProfile = async () => {
  loading.value = true
  try {
    // Use the my_profile endpoint which includes hierarchy details
    const response = await apiClient.get('/writer-management/writers/my_profile/')
    writerProfile.value = response.data
    penNameForm.value.pen_name = response.data.pen_name || ''
  } catch (error) {
    // Fallback to old method if my_profile doesn't exist
    try {
      const profileResponse = await apiClient.get('/users/users/profile/')
      const profileData = profileResponse.data
      
      // Extract writer profile data
      if (profileData.pen_name !== undefined) {
        writerProfile.value = profileData
        penNameForm.value.pen_name = profileData.pen_name || ''
      } else if (profileData.user && profileData.user.writer_profile) {
        // Try to get from nested structure
        const writerProfileId = profileData.user.writer_profile
        const writerResponse = await apiClient.get(`/writer-management/writers/${writerProfileId}/`)
        writerProfile.value = writerResponse.data
        penNameForm.value.pen_name = writerResponse.data.pen_name || ''
      } else {
        // Fallback: try to get writer profile directly
        const writerResponse = await apiClient.get('/writer-management/writers/')
        if (writerResponse.data.results && writerResponse.data.results.length > 0) {
          writerProfile.value = writerResponse.data.results[0]
          penNameForm.value.pen_name = writerResponse.data.results[0].pen_name || ''
        } else if (writerResponse.data.length > 0) {
          writerProfile.value = writerResponse.data[0]
          penNameForm.value.pen_name = writerResponse.data[0].pen_name || ''
        }
      }
    } catch (fallbackError) {
      showMessage('Failed to load profile: ' + (fallbackError.response?.data?.detail || fallbackError.message), false)
    }
  } finally {
    loading.value = false
  }
}

// Pen name management moved to dedicated page

const message = ref('')
const messageSuccess = ref(false)

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(() => {
  loadProfile()
})
</script>

