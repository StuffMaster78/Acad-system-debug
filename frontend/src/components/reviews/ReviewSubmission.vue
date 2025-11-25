<template>
  <div class="review-submission">
    <h3 class="text-lg font-semibold mb-4">Submit Review</h3>
    
    <form @submit.prevent="submitReview" class="space-y-4">
      <!-- Rating -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Overall Rating *
        </label>
        <div class="flex items-center gap-2">
          <button
            v-for="star in 5"
            :key="star"
            type="button"
            @click="rating = star"
            class="text-3xl transition-colors"
            :class="star <= rating ? 'text-yellow-400' : 'text-gray-300'"
          >
            ★
          </button>
          <span class="ml-2 text-sm text-gray-600">{{ rating }}/5</span>
        </div>
      </div>

      <!-- Quality Rating -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Quality
        </label>
        <div class="flex items-center gap-2">
          <button
            v-for="star in 5"
            :key="star"
            type="button"
            @click="qualityRating = star"
            class="text-2xl transition-colors"
            :class="star <= qualityRating ? 'text-yellow-400' : 'text-gray-300'"
          >
            ★
          </button>
        </div>
      </div>

      <!-- Timeliness Rating -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Timeliness
        </label>
        <div class="flex items-center gap-2">
          <button
            v-for="star in 5"
            :key="star"
            type="button"
            @click="timelinessRating = star"
            class="text-2xl transition-colors"
            :class="star <= timelinessRating ? 'text-yellow-400' : 'text-gray-300'"
          >
            ★
          </button>
        </div>
      </div>

      <!-- Communication Rating -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Communication
        </label>
        <div class="flex items-center gap-2">
          <button
            v-for="star in 5"
            :key="star"
            type="button"
            @click="communicationRating = star"
            class="text-2xl transition-colors"
            :class="star <= communicationRating ? 'text-yellow-400' : 'text-gray-300'"
          >
            ★
          </button>
        </div>
      </div>

      <!-- Review Text -->
      <RichTextEditor
        v-model="reviewText"
        label="Your Review"
        :required="true"
        placeholder="Share your experience with this order..."
        toolbar="basic"
        height="200px"
        :max-length="500"
        :show-char-count="true"
        :error="error && error.includes('review') ? error : ''"
      />

      <!-- Anonymous Review -->
      <div class="flex items-center">
        <input
          v-model="isAnonymous"
          type="checkbox"
          id="anonymous"
          class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
        />
        <label for="anonymous" class="ml-2 text-sm text-gray-700">
          Submit as anonymous review
        </label>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
        <p class="text-sm text-red-600">{{ error }}</p>
      </div>

      <!-- Submit Button -->
      <div class="flex gap-3">
        <button
          type="submit"
          :disabled="!rating || !reviewText.trim() || submitting"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ submitting ? 'Submitting...' : 'Submit Review' }}
        </button>
        <button
          v-if="showCancel"
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import reviewsAPI from '@/api/reviews'
import RichTextEditor from '@/components/common/RichTextEditor.vue'

const props = defineProps({
  orderId: {
    type: [Number, String],
    required: true
  },
  writerId: {
    type: [Number, String],
    required: true
  },
  showCancel: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['success', 'cancel'])

const rating = ref(0)
const qualityRating = ref(0)
const timelinessRating = ref(0)
const communicationRating = ref(0)
const reviewText = ref('')
const isAnonymous = ref(false)
const submitting = ref(false)
const error = ref('')

const submitReview = async () => {
  if (!rating.value || !reviewText.value.trim()) {
    error.value = 'Please provide a rating and review text'
    return
  }

  if (reviewText.value.length > 500) {
    error.value = 'Review text must be 500 characters or less'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    const reviewData = {
      order: props.orderId,
      writer: props.writerId,
      rating: rating.value,
      review_text: reviewText.value,
      is_anonymous: isAnonymous.value,
    }

    // Add optional ratings
    if (qualityRating.value > 0) {
      reviewData.quality_rating = qualityRating.value
    }
    if (timelinessRating.value > 0) {
      reviewData.timeliness_rating = timelinessRating.value
    }
    if (communicationRating.value > 0) {
      reviewData.communication_rating = communicationRating.value
    }

    const response = await reviewsAPI.create(reviewData)
    emit('success', response.data)
    
    // Reset form
    rating.value = 0
    qualityRating.value = 0
    timelinessRating.value = 0
    communicationRating.value = 0
    reviewText.value = ''
    isAnonymous.value = false
  } catch (err) {
    error.value = err.response?.data?.detail || 
                  err.response?.data?.message || 
                  'Failed to submit review. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.review-submission {
  width: 100%;
}
</style>

