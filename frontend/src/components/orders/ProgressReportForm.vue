<template>
  <div class="space-y-4">
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Progress Percentage
      </label>
      <div class="space-y-2">
        <input
          v-model.number="localProgress"
          type="range"
          min="0"
          max="100"
          step="1"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <div class="flex items-center justify-between text-sm text-gray-600">
          <span>0%</span>
          <span class="text-lg font-bold text-primary-600">{{ localProgress }}%</span>
          <span>100%</span>
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

const submitProgress = async () => {
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

