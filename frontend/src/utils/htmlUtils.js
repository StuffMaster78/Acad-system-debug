/**
 * HTML utility functions for sanitizing and stripping HTML
 */

/**
 * Strips HTML tags from a string, leaving only the text content
 * @param {string} html - HTML string to strip
 * @returns {string} Plain text without HTML tags
 */
export function stripHtml(html) {
  if (!html) return ''
  
  // Create a temporary DOM element to parse HTML
  const tmp = document.createElement('DIV')
  tmp.innerHTML = html
  
  // Get text content and preserve line breaks
  let text = tmp.textContent || tmp.innerText || ''
  
  // Replace <br> and <p> tags with newlines
  text = text.replace(/\n\s*\n/g, '\n') // Remove multiple newlines
  
  return text.trim()
}

/**
 * Sanitizes HTML by removing potentially dangerous tags and attributes
 * This is a basic sanitizer - for production, consider using DOMPurify
 * @param {string} html - HTML string to sanitize
 * @returns {string} Sanitized HTML
 */
export function sanitizeHtml(html) {
  if (!html) return ''
  
  // Create a temporary DOM element
  const tmp = document.createElement('DIV')
  tmp.innerHTML = html
  
  // Allowed tags for rich text content
  const allowedTags = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'strike',
    'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'a', 'img', 'span', 'div'
  ]
  
  // Allowed attributes
  const allowedAttributes = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'span': ['style'],
    'div': ['style'],
    'p': ['style']
  }
  
  // Remove script tags and event handlers
  const scripts = tmp.querySelectorAll('script, style, iframe, object, embed')
  scripts.forEach(el => el.remove())
  
  // Remove dangerous attributes
  const allElements = tmp.querySelectorAll('*')
  allElements.forEach(el => {
    // Remove if tag is not allowed
    if (!allowedTags.includes(el.tagName.toLowerCase())) {
      el.outerHTML = el.innerHTML
      return
    }
    
    // Remove dangerous attributes
    Array.from(el.attributes).forEach(attr => {
      const tagName = el.tagName.toLowerCase()
      const attrName = attr.name.toLowerCase()
      
      // Remove event handlers
      if (attrName.startsWith('on')) {
        el.removeAttribute(attr.name)
        return
      }
      
      // Remove if attribute not allowed
      if (!allowedAttributes[tagName] || !allowedAttributes[tagName].includes(attrName)) {
        // Allow style for certain tags
        if (attrName === 'style' && ['span', 'div', 'p'].includes(tagName)) {
          // Sanitize style attribute (remove dangerous properties)
          const style = attr.value
          const safeStyle = style.replace(/javascript:|expression\(|on\w+\s*=/gi, '')
          el.setAttribute('style', safeStyle)
        } else {
          el.removeAttribute(attr.name)
        }
      }
      
      // Sanitize href to prevent javascript: and data: URLs
      if (attrName === 'href') {
        const href = attr.value
        if (href.startsWith('javascript:') || href.startsWith('data:')) {
          el.removeAttribute('href')
        }
      }
      
      // Sanitize img src
      if (attrName === 'src') {
        const src = attr.value
        if (src.startsWith('javascript:') || src.startsWith('data:text/html')) {
          el.removeAttribute('src')
        }
      }
    })
  })
  
  return tmp.innerHTML
}

/**
 * Checks if a string contains HTML tags
 * @param {string} str - String to check
 * @returns {boolean} True if string contains HTML tags
 */
export function containsHtml(str) {
  if (!str) return false
  return /<[a-z][\s\S]*>/i.test(str)
}

