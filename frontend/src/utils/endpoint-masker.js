/**
 * Endpoint Masking Service
 * 
 * Masks API endpoints from writers and clients by mapping generic endpoint names
 * to actual backend endpoints. This provides security through obscurity and
 * prevents users from discovering admin/internal endpoints.
 * 
 * Different roles see different endpoint mappings:
 * - Clients: Only see client-related endpoints
 * - Writers: Only see writer-related endpoints  
 * - Admins/Superadmins: See all endpoints (no masking)
 */

// Role-based endpoint mappings
// Format: { actual_endpoint: masked_endpoint }
// This maps the actual backend endpoints to masked/generic ones
const ENDPOINT_MAPPINGS = {
  // Client role mappings - actual -> masked
  client: {
    // Orders
    '/orders/orders/': '/client/orders/',
    '/orders/orders': '/client/orders/',
    
    // Payments
    '/order-payments/order-payments/client-payments/': '/client/payments/',
    '/invoices/client-invoices/': '/client/invoices/',
    
    // Referrals
    '/referrals/referral-codes/my-code/': '/client/referrals/code/',
    '/referrals/referrals/stats/': '/client/referrals/stats/',
    
    // Profile
    '/users/users/profile/': '/client/profile/',
    
    // Support
    '/support-management/tickets/': '/client/support/',
    
    // Notifications
    '/notifications_system/notifications/feed/': '/client/notifications/',
    
    // Admin endpoints should be hidden (will return 404 if accessed)
    '/admin-management/': '/client/restricted/',
    '/superadmin-management/': '/client/restricted/',
  },
  
  // Writer role mappings - actual -> masked
  writer: {
    // Orders
    '/writer-management/writer-orders/': '/writer/orders/',
    '/writer-management/writer-order-requests/': '/writer/requests/',
    '/writer-management/writer-order-takes/': '/writer/takes/',
    
    // Payments
    '/writer-management/writer-payments/': '/writer/payments/',
    '/writer-wallet/writer-payments/': '/writer/wallet/',
    
    // Performance
    '/writer-management/writer-performance/': '/writer/performance/',
    '/writer-management/writer-dashboard/': '/writer/dashboard/',
    
    // Requests
    '/writer-management/writer-order-hold-requests/': '/writer/hold-requests/',
    '/writer-management/writer-deadline-extension-requests/': '/writer/extensions/',
    
    // Profile
    '/writer-management/writer-profiles/me/': '/writer/profile/',
    
    // Support
    '/support-management/tickets/': '/writer/support/',
    
    // Admin endpoints should be hidden
    '/admin-management/': '/writer/restricted/',
    '/superadmin-management/': '/writer/restricted/',
    '/orders/orders/': '/writer/restricted/', // Clients' orders endpoint
  },
  
  // Admin/Superadmin see all endpoints (no masking)
  admin: {},
  superadmin: {},
}

// Reverse mapping for response handling (if needed)
const REVERSE_MAPPINGS = {}

// Build reverse mappings
Object.keys(ENDPOINT_MAPPINGS).forEach(role => {
  REVERSE_MAPPINGS[role] = {}
  Object.entries(ENDPOINT_MAPPINGS[role]).forEach(([masked, actual]) => {
    REVERSE_MAPPINGS[role][actual] = masked
  })
})

/**
 * Get user role from localStorage or return null
 */
function getUserRole() {
  if (typeof window === 'undefined') return null
  
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      return user?.role || null
    }
  } catch (e) {
    // Ignore parse errors
  }
  
  return null
}

/**
 * Mask an endpoint based on user role
 * @param {string} endpoint - The actual endpoint URL
 * @param {string} role - User role (optional, will be fetched if not provided)
 * @returns {string} - Masked endpoint or original if no mapping exists
 */
export function maskEndpoint(endpoint, role = null) {
  // Admins and superadmins see all endpoints unmasked
  const userRole = role || getUserRole()
  if (!userRole || userRole === 'admin' || userRole === 'superadmin') {
    return endpoint
  }
  
  // Get mappings for this role (actual -> masked)
  const mappings = ENDPOINT_MAPPINGS[userRole] || {}
  
  // Try to find a matching masked endpoint
  // Check for exact matches first
  if (mappings[endpoint]) {
    return mappings[endpoint]
  }
  
  // Check for partial matches (endpoints with IDs, actions, or query params)
  for (const [actual, masked] of Object.entries(mappings)) {
    // Handle endpoints with IDs: /orders/orders/123/ -> /client/orders/123/
    if (endpoint.startsWith(actual)) {
      const remaining = endpoint.slice(actual.length)
      // Preserve ID, action, or query params
      return masked + remaining
    }
  }
  
  // Check if endpoint should be blocked (admin-only endpoints)
  const shouldBlock = endpoint.includes('/admin-management/') || 
                     endpoint.includes('/superadmin-management/') ||
                     (userRole === 'writer' && endpoint.startsWith('/orders/orders/'))
  
  if (shouldBlock) {
    // Return a masked restricted endpoint (backend will handle 403)
    return `/restricted/${userRole}/blocked/`
  }
  
  // No mapping found, return original (for endpoints not in mapping)
  // This allows unmapped endpoints to work normally
  return endpoint
}

/**
 * Unmask an endpoint (convert masked back to actual)
 * Useful for debugging or if backend needs actual endpoint
 * @param {string} maskedEndpoint - The masked endpoint
 * @param {string} role - User role
 * @returns {string} - Actual endpoint or original if no reverse mapping
 */
export function unmaskEndpoint(maskedEndpoint, role = null) {
  const userRole = role || getUserRole()
  if (!userRole || userRole === 'admin' || userRole === 'superadmin') {
    return maskedEndpoint
  }
  
  const mappings = ENDPOINT_MAPPINGS[userRole] || {}
  
  // Build reverse mapping (masked -> actual)
  const reverseMappings = {}
  Object.entries(mappings).forEach(([actual, masked]) => {
    reverseMappings[masked] = actual
  })
  
  // Try exact match first
  if (reverseMappings[maskedEndpoint]) {
    return reverseMappings[maskedEndpoint]
  }
  
  // Try partial match
  for (const [masked, actual] of Object.entries(reverseMappings)) {
    if (maskedEndpoint.startsWith(masked)) {
      const remaining = maskedEndpoint.slice(masked.length)
      return actual + remaining
    }
  }
  
  return maskedEndpoint
}

/**
 * Check if an endpoint should be masked for the current user
 * @param {string} endpoint - The endpoint to check
 * @returns {boolean} - True if endpoint should be masked
 */
export function shouldMaskEndpoint(endpoint) {
  const role = getUserRole()
  if (!role || role === 'admin' || role === 'superadmin') {
    return false
  }
  
  // Check if endpoint is in the mapping for this role
  const mappings = ENDPOINT_MAPPINGS[role] || {}
  return Object.values(mappings).some(actual => endpoint.startsWith(actual))
}

/**
 * Get all masked endpoints for a role (for debugging)
 * @param {string} role - User role
 * @returns {object} - Object mapping masked -> actual endpoints
 */
export function getMappingsForRole(role) {
  return ENDPOINT_MAPPINGS[role] || {}
}

// Export getUserRole for use in API client
export { getUserRole }

export default {
  maskEndpoint,
  unmaskEndpoint,
  shouldMaskEndpoint,
  getMappingsForRole,
  getUserRole,
}

