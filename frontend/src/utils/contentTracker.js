import { contentAnalyticsAPI } from '@/api'

let sessionId = localStorage.getItem('content_session_id')
if (!sessionId) {
  sessionId = `${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`
  localStorage.setItem('content_session_id', sessionId)
}

const sentScrollBuckets = new Set()

export function trackEvent(eventType, { websiteId, contentType, objectId, metadata = {} } = {}) {
  if (!websiteId || !contentType || !objectId) return

  contentAnalyticsAPI
    .trackEvent({
      website: websiteId,
      session_id: sessionId,
      // ContentType identifier will be resolved on the backend;
      // for now we send a simple label in metadata and let backend map it if needed.
      // Alternatively, send explicit content_type id if you have it.
      metadata: { ...metadata, content_type_label: contentType },
      object_id: objectId,
      event_type: eventType,
      path: window.location.pathname + window.location.search,
      referrer: document.referrer || null,
    })
    .catch(() => {
      // Analytics failures should never block UX
    })
}

export function initPageTracking({ websiteId, contentType, objectId }) {
  // Initial view
  trackEvent('view', { websiteId, contentType, objectId })

  const onScroll = () => {
    const doc = document.documentElement
    const scrollTop = window.scrollY || doc.scrollTop
    const height = doc.scrollHeight - doc.clientHeight
    if (height <= 0) return
    const percent = Math.round((scrollTop / height) * 100)

    const buckets = [25, 50, 75, 90]
    for (const bucket of buckets) {
      if (percent >= bucket && !sentScrollBuckets.has(bucket)) {
        sentScrollBuckets.add(bucket)
        trackEvent('scroll_depth', {
          websiteId,
          contentType,
          objectId,
          metadata: { scroll_percent: bucket },
        })
      }
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true })

  return () => {
    window.removeEventListener('scroll', onScroll)
    sentScrollBuckets.clear()
  }
}

export function trackClick(args, extra = {}) {
  trackEvent('click', { ...args, metadata: extra })
}

export function trackCTA(args, extra = {}) {
  trackEvent('cta', { ...args, metadata: extra })
}

export function trackLike(args) {
  trackEvent('like', args)
}

export function trackDislike(args) {
  trackEvent('dislike', args)
}


