<template>
  <div class="space-y-4">
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Progress Percentage
      </label>
      
      <!-- Direct Input + Slider Combination -->
      <div class="space-y-3">
        <div class="flex items-center gap-4">
          <!-- Direct percentage input -->
          <div class="flex items-center gap-2">
            <input
              v-model.number="localProgress"
              type="number"
              min="0"
              max="100"
              step="1"
              class="w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-center font-semibold text-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:text-gray-100"
              @input="validateProgress"
            />
            <span class="text-lg font-semibold text-gray-700 dark:text-gray-300">%</span>
          </div>
          
          <!-- Quick buttons -->
          <div class="flex items-center gap-2">
            <button
              v-for="quickValue in [0, 25, 50, 75, 100]"
              :key="quickValue"
              @click="localProgress = quickValue"
              :class="[
                'px-3 py-1 text-xs font-medium rounded-lg transition-colors',
                localProgress === quickValue
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              ]"
            >
              {{ quickValue }}%
            </button>
          </div>
        </div>
        
        <!-- Visual progress bar -->
        <div class="relative">
          <input
            v-model.number="localProgress"
            type="range"
            min="0"
            max="100"
            step="1"
            class="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer progress-slider"
            :style="getSliderStyle()"
          />
          <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mt-1 px-1">
            <span>0%</span>
            <span>25%</span>
            <span>50%</span>
            <span>75%</span>
            <span>100%</span>
          </div>
        </div>
        
        <!-- Current progress display -->
        <div class="flex items-center justify-center">
          <div class="px-4 py-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
            <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">{{ localProgress }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Notes (Optional)
      </label>
      <textarea
        v-model="localNotes"
        rows="4"
        placeholder="Add any notes about your progress..."
        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
        :class="{ 'border-red-500': hasScreenedWords }"
      ></textarea>
      <p v-if="hasScreenedWords" class="mt-1 text-sm text-red-600">
        ⚠️ Your notes contain words that may violate our policies. Please revise.
      </p>
      <p v-else class="mt-1 text-xs text-gray-500">
        Share updates about your work progress with the client.
      </p>
    </div>

    <div class="flex items-center gap-2">
      <button
        @click="submitProgress"
        :disabled="submitting || localProgress < 0 || localProgress > 100"
        class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {{ submitting ? 'Submitting...' : 'Submit Progress Report' }}
      </button>
      <button
        v-if="showCancel"
        @click="$emit('cancel')"
        class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
      >
        Cancel
      </button>
    </div>

    <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg">
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import progressAPI from '@/api/progress'

const props = defineProps({
  orderId: {
    type: Number,
    required: true
  },
  initialProgress: {
    type: Number,
    default: 0
  },
  showCancel: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['success', 'cancel', 'error'])

const localProgress = ref(props.initialProgress)
const localNotes = ref('')
const submitting = ref(false)
const error = ref('')
const hasScreenedWords = ref(false)

// Check for screened words (this would ideally be done on the backend)
// For now, we'll just show a warning if certain patterns are detected
watch(localNotes, (newValue) => {
  // Basic client-side check - backend will do the real validation
  const suspiciousPatterns = [
    /\b(contact|email|phone|whatsapp|telegram)\s*(me|directly|outside)\b/i,
    /\b(skip|bypass|ignore)\s*(the|this)\s*(system|platform)\b/i
  ]
  
  hasScreenedWords.value = suspiciousPatterns.some(pattern => pattern.test(newValue))
})

const validateProgress = () => {
  if (localProgress.value < 0) localProgress.value = 0
  if (localProgress.value > 100) localProgress.value = 100
}

const getSliderStyle = () => {
  const percentage = localProgress.value
  const color = percentage < 25 ? '#ef4444' : percentage < 50 ? '#f97316' : percentage < 75 ? '#3b82f6' : percentage < 100 ? '#6366f1' : '#10b981'
  return {
    background: `linear-gradient(to right, ${color} 0%, ${color} ${percentage}%, #e5e7eb ${percentage}%, #e5e7eb 100%)`
  }
}

const submitProgress = async () => {
  validateProgress()
  
  if (localProgress.value < 0 || localProgress.value > 100) {
    error.value = 'Progress must be between 0 and 100.'
    return
  }

  try {
    submitting.value = true
    error.value = ''

    const response = await progressAPI.createProgress({
      order: props.orderId,
      progress_percentage: localProgress.value,
      notes: localNotes.value || null
    })

    emit('success', response.data)
    
    // Reset form
    localNotes.value = ''
    hasScreenedWords.value = false
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to submit progress report.'
    emit('error', err)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.progress-slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 3px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.progress-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 3px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>

