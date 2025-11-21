/**
 * Utility functions for formatting IDs with prefixes and longer formats
 */

/**
 * Format user ID with role-based prefix
 * @param {number|string} userId - The user ID
 * @param {string} role - The user role (writer, editor, admin, superadmin, client, support)
 * @returns {string} Formatted ID (e.g., WRTR000123, EDTR000456)
 */
export function formatUserId(userId, role) {
  if (!userId) return 'N/A'
  
  const id = typeof userId === 'string' ? parseInt(userId, 10) : userId
  if (isNaN(id)) return userId.toString()
  
  const prefixes = {
    writer: 'WRTR',
    editor: 'EDTR',
    admin: 'ADMN',
    superadmin: 'SPAD',
    client: 'CLNT',
    support: 'SPRT',
  }
  
  const prefix = prefixes[role?.toLowerCase()] || 'USER'
  return `${prefix}${id.toString().padStart(6, '0')}`
}

/**
 * Format order ID with longer format
 * @param {number|string} orderId - The order ID
 * @returns {string} Formatted order ID (e.g., #1000278)
 */
export function formatOrderId(orderId) {
  if (!orderId) return 'N/A'
  
  const id = typeof orderId === 'string' ? parseInt(orderId, 10) : orderId
  if (isNaN(id)) return `#${orderId}`
  
  return `#${id.toString().padStart(7, '0')}`
}

/**
 * Format any ID with a custom prefix
 * @param {number|string} id - The ID to format
 * @param {string} prefix - The prefix to use
 * @param {number} padding - Number of digits to pad (default: 6)
 * @returns {string} Formatted ID
 */
export function formatId(id, prefix = '', padding = 6) {
  if (!id) return 'N/A'
  
  const numId = typeof id === 'string' ? parseInt(id, 10) : id
  if (isNaN(numId)) return prefix ? `${prefix}${id}` : id.toString()
  
  const padded = numId.toString().padStart(padding, '0')
  return prefix ? `${prefix}${padded}` : padded
}

/**
 * Extract numeric ID from formatted ID
 * @param {string} formattedId - Formatted ID (e.g., WRTR000123, #1000278)
 * @returns {number|null} Numeric ID or null if invalid
 */
export function extractId(formattedId) {
  if (!formattedId) return null
  
  // Remove prefix and # symbol, then extract number
  const cleaned = formattedId.replace(/^[A-Z]+/, '').replace(/^#/, '').trim()
  const num = parseInt(cleaned, 10)
  
  return isNaN(num) ? null : num
}

/**
 * Get role from formatted user ID
 * @param {string} formattedId - Formatted user ID (e.g., WRTR000123)
 * @returns {string|null} Role or null if not found
 */
export function getRoleFromId(formattedId) {
  if (!formattedId) return null
  
  const roleMap = {
    'WRTR': 'writer',
    'EDTR': 'editor',
    'ADMN': 'admin',
    'SPAD': 'superadmin',
    'CLNT': 'client',
    'SPRT': 'support',
  }
  
  const prefix = formattedId.substring(0, 4)
  return roleMap[prefix] || null
}

