/**
 * Format display names for dropdowns and lists
 * Prevents empty parentheses when optional fields are missing
 */

/**
 * Format a writer name with optional email
 * @param {Object} writer - Writer object
 * @returns {string} Formatted name
 */
export function formatWriterName(writer) {
  if (!writer) return 'Unknown'
  
  const username = writer.user?.username || writer.username || 'Unknown'
  const email = writer.user?.email || writer.email
  
  if (email) {
    return `${username} (${email})`
  }
  return username
}

/**
 * Format a website name with optional domain
 * @param {Object} website - Website object
 * @returns {string} Formatted name
 */
export function formatWebsiteName(website) {
  if (!website) return 'Unknown'
  
  const name = website.name || 'Unknown'
  const domain = website.domain
  
  if (domain) {
    return `${name} (${domain})`
  }
  return name
}

/**
 * Format a user name with optional email
 * @param {Object} user - User object
 * @returns {string} Formatted name
 */
export function formatUserName(user) {
  if (!user) return 'Unknown'
  
  const username = user.username || user.user?.username || 'Unknown'
  const email = user.email || user.user?.email
  
  if (email) {
    return `${username} (${email})`
  }
  return username
}

/**
 * Format a client name with optional email
 * @param {Object} client - Client object
 * @returns {string} Formatted name
 */
export function formatClientName(client) {
  return formatUserName(client)
}

/**
 * Format display text with optional secondary info in parentheses
 * @param {string} primary - Primary text
 * @param {string} secondary - Optional secondary text
 * @returns {string} Formatted text
 */
export function formatWithParentheses(primary, secondary) {
  if (!primary) return 'Unknown'
  if (secondary) {
    return `${primary} (${secondary})`
  }
  return primary
}

