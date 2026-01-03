/**
 * Utility functions for processing message content
 */

import communicationsAPI from '@/api/communications'

/**
 * Loads unread message count for a specific order
 * @param {number} orderId - The order ID
 * @returns {Promise<number>} The unread message count
 */
export async function loadUnreadMessageCount(orderId) {
  if (!orderId) return 0
  
  try {
    // Fetch threads for this order
    const response = await communicationsAPI.listThreads({ order: orderId })
    const threads = response.data.results || response.data || []
    
    // Sum up unread counts from all threads
    const totalUnread = threads.reduce((sum, thread) => {
      return sum + (thread.unread_count || 0)
    }, 0)
    
    return totalUnread
  } catch (error) {
    // Silently handle errors - return 0 on failure
    if (import.meta.env.DEV) {
      console.warn('Failed to load unread message count:', error)
    }
    return 0
  }
}

/**
 * Converts "place order" text patterns to clickable router-links
 * @param {string} text - The message text
 * @returns {Array} Array of text segments and link objects
 */
export function parseMessageLinks(text) {
  if (!text) return []
  
  // Pattern to match "place order" variations (case insensitive)
  const placeOrderPattern = /\b(place\s+(?:a\s+)?(?:new\s+)?order|place\s+order|order\s+wizard)\b/gi
  
  const segments = []
  let lastIndex = 0
  let match
  
  while ((match = placeOrderPattern.exec(text)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      segments.push({
        type: 'text',
        content: text.substring(lastIndex, match.index)
      })
    }
    
    // Add the link
    segments.push({
      type: 'link',
      content: match[0],
      to: '/orders/wizard'
    })
    
    lastIndex = match.index + match[0].length
  }
  
  // Add remaining text
  if (lastIndex < text.length) {
    segments.push({
      type: 'text',
      content: text.substring(lastIndex)
    })
  }
  
  // If no matches, return the whole text as a single segment
  if (segments.length === 0) {
    segments.push({
      type: 'text',
      content: text
    })
  }
  
  return segments
}

/**
 * Checks if text contains "place order" patterns
 * @param {string} text - The message text
 * @returns {boolean} True if text contains place order patterns
 */
export function hasPlaceOrderLink(text) {
  if (!text) return false
  const pattern = /\b(place\s+(?:a\s+)?(?:new\s+)?order|place\s+order|order\s+wizard)\b/gi
  return pattern.test(text)
}
