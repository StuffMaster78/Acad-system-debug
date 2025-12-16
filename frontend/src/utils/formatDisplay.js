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
  
  // Try multiple possible paths for username
  const username = writer.username || writer.user?.username || writer.writer_profile?.user?.username || 'Unknown'
  const email = writer.email || writer.user?.email || writer.writer_profile?.user?.email
  
  // If username is still 'Unknown', try to get from email or ID
  if (username === 'Unknown') {
    if (email) {
      // Extract username from email (part before @)
      const emailUsername = email.split('@')[0]
      return emailUsername
    }
    if (writer.id) {
      return `Writer #${writer.id}`
    }
  }
  
  if (email && username !== email) {
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
  
  // Try multiple possible name fields
  const name = website.name || website.website_name || website.title || ''
  
  // If no name, try to extract from domain or use ID
  if (!name || name.trim() === '') {
    if (website.domain) {
      // Extract domain name from URL (e.g., "example.com" from "https://example.com")
      try {
        const url = new URL(website.domain)
        const domainName = url.hostname.replace('www.', '')
        return domainName
      } catch (e) {
        // If domain is not a valid URL, use it as-is
        return website.domain.replace(/^https?:\/\//, '').replace(/^www\./, '')
      }
    }
    // Last resort: use ID
    if (website.id) {
      return `Website #${website.id}`
    }
    return 'Unknown'
  }
  
  const domain = website.domain || website.website_domain
  
  if (domain) {
    // Clean up domain for display
    const cleanDomain = domain.replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/$/, '')
    return `${name} (${cleanDomain})`
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

