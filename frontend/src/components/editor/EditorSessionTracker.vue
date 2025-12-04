<template>
  <!-- This component tracks editor sessions automatically -->
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'

const props = defineProps({
  websiteId: {
    type: [String, Number],
    required: true
  },
  contentType: {
    type: String,
    required: true // 'blog_post' or 'service_page'
  },
  contentId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['session-started', 'session-ended'])

const sessionId = ref(null)
const keystrokeCount = ref(0)
const actionCount = ref(0)
let keystrokeTimer = null
let heartbeatInterval = null

const startSession = async () => {
  try {
    const res = await blogPagesAPI.startEditorSession({
      website_id: props.websiteId,
      content_type: props.contentType,
      content_id: props.contentId
    })
    sessionId.value = res.data.id
    emit('session-started', res.data)
    
    // Start heartbeat
    heartbeatInterval = setInterval(() => {
      if (sessionId.value) {
        trackAction('heartbeat', {})
      }
    }, 30000) // Every 30 seconds
  } catch (e) {
    console.error('Failed to start editor session:', e)
  }
}

const endSession = async () => {
  if (!sessionId.value) return
  
  try {
    await blogPagesAPI.endEditorSession(sessionId.value)
    emit('session-ended')
    sessionId.value = null
    
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  } catch (e) {
    console.error('Failed to end editor session:', e)
  }
}

const trackAction = async (actionType, metadata = {}) => {
  if (!sessionId.value) return
  
  try {
    await blogPagesAPI.trackEditorAction(sessionId.value, {
      action_type: actionType,
      metadata
    })
    
    actionCount.value++
    
    // Batch keystrokes
    if (actionType === 'keystroke') {
      keystrokeCount.value++
      if (!keystrokeTimer) {
        keystrokeTimer = setTimeout(() => {
          // Track batched keystrokes
          if (keystrokeCount.value > 0) {
            trackAction('keystroke', {
              count: keystrokeCount.value,
              characters_added: metadata.characters_added || 0,
              characters_removed: metadata.characters_removed || 0
            })
            keystrokeCount.value = 0
          }
          keystrokeTimer = null
        }, 5000) // Batch every 5 seconds
      }
    }
  } catch (e) {
    console.error('Failed to track action:', e)
  }
}

// Expose methods for parent component
defineExpose({
  trackAction,
  startSession,
  endSession
})

watch(() => [props.websiteId, props.contentId], () => {
  if (props.websiteId && props.contentId) {
    startSession()
  }
}, { immediate: true })

onBeforeUnmount(() => {
  endSession()
  if (keystrokeTimer) {
    clearTimeout(keystrokeTimer)
  }
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
  }
})
</script>

