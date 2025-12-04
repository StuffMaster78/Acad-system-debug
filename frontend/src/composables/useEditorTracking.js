/**
 * Composable for editor usage tracking.
 * Provides easy-to-use methods for tracking editor actions.
 */
import { ref } from 'vue'
import blogPagesAPI from '@/api/blog-pages'

export function useEditorTracking(websiteId, contentType, contentId) {
  const sessionId = ref(null)
  const isTracking = ref(false)

  const startTracking = async () => {
    if (!websiteId.value || !contentId.value) return

    try {
      const res = await blogPagesAPI.startEditorSession({
        website_id: websiteId.value,
        content_type: contentType.value,
        content_id: contentId.value
      })
      sessionId.value = res.data.id
      isTracking.value = true
      return res.data
    } catch (e) {
      console.error('Failed to start editor session:', e)
      return null
    }
  }

  const stopTracking = async () => {
    if (!sessionId.value) return

    try {
      await blogPagesAPI.endEditorSession(sessionId.value)
      sessionId.value = null
      isTracking.value = false
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
    } catch (e) {
      console.error('Failed to track action:', e)
    }
  }

  // Convenience methods
  const trackTemplateUse = (templateId) => {
    trackAction('template_use', { template_id: templateId })
  }

  const trackSnippetUse = (snippetId) => {
    trackAction('snippet_use', { snippet_id: snippetId })
  }

  const trackBlockUse = (blockId) => {
    trackAction('block_use', { block_id: blockId })
  }

  const trackHealthCheck = (score) => {
    trackAction('health_check', { score })
  }

  const trackSave = (isAutoSave = false) => {
    trackAction(isAutoSave ? 'auto_save' : 'save', {})
  }

  return {
    sessionId,
    isTracking,
    startTracking,
    stopTracking,
    trackAction,
    trackTemplateUse,
    trackSnippetUse,
    trackBlockUse,
    trackHealthCheck,
    trackSave
  }
}

