/**
 * Simple helper for working with the browser timezone.
 */

export function getBrowserTimezone() {
  try {
    if (typeof Intl !== 'undefined' && Intl.DateTimeFormat) {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone
      if (tz && typeof tz === 'string') {
        return tz
      }
    }
  } catch (e) {
    // Ignore and fallback to null
  }
  return null
}

export async function detectAndStoreTimezone() {
  const timezone = getBrowserTimezone()
  if (!timezone) return null

  const previous = localStorage.getItem('timezone')
  if (previous === timezone) {
    return timezone
  }

  localStorage.setItem('timezone', timezone)
  return timezone
}


