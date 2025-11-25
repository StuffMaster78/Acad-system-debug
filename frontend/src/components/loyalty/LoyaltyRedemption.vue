<template>
  <div class="loyalty-redemption">
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2">Redeem Loyalty Points</h3>
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-blue-900">Your Points Balance:</span>
          <span class="text-2xl font-bold text-blue-900">{{ formatNumber(pointsBalance) }} points</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>

    <!-- Redemption Items Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="item in redemptionItems"
        :key="item.id"
        class="border rounded-lg p-4 hover:shadow-md transition-shadow"
        :class="{
          'border-green-300 bg-green-50': canAfford(item),
          'border-gray-200 bg-white': !canAfford(item),
          'opacity-50': !canAfford(item)
        }"
      >
        <div class="flex items-start justify-between mb-2">
          <h4 class="font-semibold text-gray-900">{{ item.name }}</h4>
          <span
            class="px-2 py-1 rounded-full text-xs font-medium"
            :class="item.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
          >
            {{ item.is_available ? 'Available' : 'Unavailable' }}
          </span>
        </div>
        
        <p v-if="item.description" class="text-sm text-gray-600 mb-3 line-clamp-2">
          {{ item.description }}
        </p>

        <div class="flex items-center justify-between mb-3">
          <div>
            <div class="text-lg font-bold text-primary-600">
              {{ formatNumber(item.points_required) }} points
            </div>
            <div v-if="item.cash_value" class="text-xs text-gray-500">
              ≈ ${{ formatCurrency(item.cash_value) }}
            </div>
          </div>
          <div v-if="item.image_url" class="w-16 h-16 rounded-lg overflow-hidden bg-gray-100">
            <img :src="item.image_url" :alt="item.name" class="w-full h-full object-cover" />
          </div>
        </div>

        <button
          @click="requestRedemption(item)"
          :disabled="!canAfford(item) || !item.is_available || processing"
          class="w-full px-4 py-2 rounded-lg font-medium transition-colors"
          :class="canAfford(item) && item.is_available
            ? 'bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50'
            : 'bg-gray-200 text-gray-500 cursor-not-allowed'"
        >
          {{ processing ? 'Processing...' : 'Redeem' }}
        </button>

        <div v-if="!canAfford(item)" class="mt-2 text-xs text-red-600 text-center">
          Need {{ formatNumber(item.points_required - pointsBalance) }} more points
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !error && redemptionItems.length === 0" class="text-center py-12">
      <div class="text-4xl mb-4">🎁</div>
      <p class="text-gray-500">No redemption items available at this time.</p>
    </div>

    <!-- Redemption Request Modal -->
    <Modal
      v-model:visible="showRequestModal"
      title="Confirm Redemption"
      size="md"
    >
      <div v-if="selectedItem" class="space-y-4">
        <div class="bg-gray-50 rounded-lg p-4">
          <h4 class="font-semibold mb-2">{{ selectedItem.name }}</h4>
          <p v-if="selectedItem.description" class="text-sm text-gray-600 mb-3">
            {{ selectedItem.description }}
          </p>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Points Required:</span>
            <span class="text-lg font-bold text-primary-600">
              {{ formatNumber(selectedItem.points_required) }} points
            </span>
          </div>
          <div class="flex items-center justify-between mt-2">
            <span class="text-sm text-gray-600">Your Balance:</span>
            <span class="text-lg font-bold">
              {{ formatNumber(pointsBalance) }} points
            </span>
          </div>
          <div class="flex items-center justify-between mt-2 pt-2 border-t border-gray-300">
            <span class="text-sm font-medium text-gray-900">Remaining Balance:</span>
            <span class="text-lg font-bold text-green-600">
              {{ formatNumber(pointsBalance - selectedItem.points_required) }} points
            </span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Additional Notes (Optional)
          </label>
          <textarea
            v-model="redemptionNotes"
            rows="3"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Any special instructions or notes..."
          ></textarea>
        </div>

        <div class="flex gap-3">
          <button
            @click="confirmRedemption"
            :disabled="processing"
            class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {{ processing ? 'Processing...' : 'Confirm Redemption' }}
          </button>
          <button
            @click="showRequestModal = false"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import loyaltyAPI from '@/api/loyalty-management'
import Modal from '@/components/common/Modal.vue'

const props = defineProps({
  pointsBalance: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['redemption-success', 'points-updated'])

const redemptionItems = ref([])
const loading = ref(true)
const error = ref('')
const processing = ref(false)
const showRequestModal = ref(false)
const selectedItem = ref(null)
const redemptionNotes = ref('')

const canAfford = (item) => {
  return props.pointsBalance >= item.points_required
}

const loadRedemptionItems = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await loyaltyAPI.getRedemptionItems()
    redemptionItems.value = Array.isArray(response.data?.results) 
      ? response.data.results 
      : (Array.isArray(response.data) ? response.data : [])
  } catch (err) {
    error.value = err.response?.data?.detail || 
                  err.response?.data?.message || 
                  'Failed to load redemption items'
    redemptionItems.value = []
  } finally {
    loading.value = false
  }
}

const requestRedemption = (item) => {
  if (!canAfford(item) || !item.is_available) return
  selectedItem.value = item
  redemptionNotes.value = ''
  showRequestModal.value = true
}

const confirmRedemption = async () => {
  if (!selectedItem.value) return
  
  processing.value = true
  error.value = ''
  
  try {
    const requestData = {
      redemption_item: selectedItem.value.id,
      notes: redemptionNotes.value || undefined
    }
    
    const response = await loyaltyAPI.createRedemptionRequest(requestData)
    
    emit('redemption-success', response.data)
    emit('points-updated', props.pointsBalance - selectedItem.value.points_required)
    
    showRequestModal.value = false
    selectedItem.value = null
    redemptionNotes.value = ''
    
    // Reload items to reflect availability changes
    await loadRedemptionItems()
  } catch (err) {
    error.value = err.response?.data?.detail || 
                  err.response?.data?.message || 
                  'Failed to submit redemption request'
  } finally {
    processing.value = false
  }
}

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US').format(num || 0)
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

onMounted(() => {
  loadRedemptionItems()
})
</script>

<style scoped>
.loyalty-redemption {
  width: 100%;
}
</style>

