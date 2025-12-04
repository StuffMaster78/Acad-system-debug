<template>
  <div class="like-dislike-buttons flex items-center gap-4">
    <!-- Like Button -->
    <button
      @click="handleLike"
      :disabled="loading"
      :class="[
        'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
        isLiked
          ? 'bg-green-50 text-green-700 border-2 border-green-300'
          : 'bg-gray-50 text-gray-700 border-2 border-gray-200 hover:bg-gray-100'
      ]"
      aria-label="Like this content"
    >
      <svg
        class="w-5 h-5"
        :class="isLiked ? 'fill-green-600' : 'fill-none'"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
        />
      </svg>
      <span class="font-medium">{{ likeCount }}</span>
    </button>

    <!-- Dislike Button -->
    <button
      @click="handleDislike"
      :disabled="loading"
      :class="[
        'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
        isDisliked
          ? 'bg-red-50 text-red-700 border-2 border-red-300'
          : 'bg-gray-50 text-gray-700 border-2 border-gray-200 hover:bg-gray-100'
      ]"
      aria-label="Dislike this content"
    >
      <svg
        class="w-5 h-5"
        :class="isDisliked ? 'fill-red-600' : 'fill-none'"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5"
        />
      </svg>
      <span class="font-medium">{{ dislikeCount }}</span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { trackLike, trackDislike } from '@/utils/contentTracker'

const props = defineProps({
  websiteId: {
    type: Number,
    required: true
  },
  contentType: {
    type: String,
    required: true,
    default: 'blogpost' // 'blogpost' or 'seopage'
  },
  objectId: {
    type: Number,
    required: true
  },
  initialLikeCount: {
    type: Number,
    default: 0
  },
  initialDislikeCount: {
    type: Number,
    default: 0
  },
  initialUserReaction: {
    type: String,
    default: null, // 'like', 'dislike', or null
    validator: (value) => !value || ['like', 'dislike'].includes(value)
  }
})

const emit = defineEmits(['reaction-changed'])

const likeCount = ref(props.initialLikeCount)
const dislikeCount = ref(props.initialDislikeCount)
const userReaction = ref(props.initialUserReaction)
const loading = ref(false)

const isLiked = computed(() => userReaction.value === 'like')
const isDisliked = computed(() => userReaction.value === 'dislike')

const handleLike = async () => {
  if (loading.value) return

  loading.value = true
  try {
    // If already liked, remove like
    if (isLiked.value) {
      userReaction.value = null
      likeCount.value = Math.max(0, likeCount.value - 1)
    } else {
      // If was disliked, switch to like
      if (isDisliked.value) {
        dislikeCount.value = Math.max(0, dislikeCount.value - 1)
      }
      userReaction.value = 'like'
      likeCount.value += 1
      
      // Track the like event
      trackLike({
        websiteId: props.websiteId,
        contentType: props.contentType,
        objectId: props.objectId
      })
    }
    
    emit('reaction-changed', {
      reaction: userReaction.value,
      likeCount: likeCount.value,
      dislikeCount: dislikeCount.value
    })
  } catch (error) {
    console.error('Failed to handle like:', error)
    // Revert on error
    userReaction.value = props.initialUserReaction
    likeCount.value = props.initialLikeCount
    dislikeCount.value = props.initialDislikeCount
  } finally {
    loading.value = false
  }
}

const handleDislike = async () => {
  if (loading.value) return

  loading.value = true
  try {
    // If already disliked, remove dislike
    if (isDisliked.value) {
      userReaction.value = null
      dislikeCount.value = Math.max(0, dislikeCount.value - 1)
    } else {
      // If was liked, switch to dislike
      if (isLiked.value) {
        likeCount.value = Math.max(0, likeCount.value - 1)
      }
      userReaction.value = 'dislike'
      dislikeCount.value += 1
      
      // Track the dislike event
      trackDislike({
        websiteId: props.websiteId,
        contentType: props.contentType,
        objectId: props.objectId
      })
    }
    
    emit('reaction-changed', {
      reaction: userReaction.value,
      likeCount: likeCount.value,
      dislikeCount: dislikeCount.value
    })
  } catch (error) {
    console.error('Failed to handle dislike:', error)
    // Revert on error
    userReaction.value = props.initialUserReaction
    likeCount.value = props.initialLikeCount
    dislikeCount.value = props.initialDislikeCount
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.like-dislike-buttons button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

