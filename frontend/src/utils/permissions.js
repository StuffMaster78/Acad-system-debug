/**
 * Role-based permissions and access control utilities
 */

export const ROLES = {
  SUPERADMIN: 'superadmin',
  ADMIN: 'admin',
  CLIENT: 'client',
  WRITER: 'writer',
  EDITOR: 'editor',
  SUPPORT: 'support',
}

export const PERMISSIONS = {
  // Dashboard access
  VIEW_DASHBOARD: {
    roles: [ROLES.SUPERADMIN, ROLES.ADMIN, ROLES.CLIENT, ROLES.WRITER, ROLES.EDITOR, ROLES.SUPPORT],
  },
  
  // Order management
  CREATE_ORDER: {
    roles: [ROLES.CLIENT, ROLES.ADMIN, ROLES.SUPERADMIN],
  },
  VIEW_ALL_ORDERS: {
    roles: [ROLES.ADMIN, ROLES.SUPERADMIN, ROLES.SUPPORT],
  },
  VIEW_OWN_ORDERS: {
    roles: [ROLES.CLIENT, ROLES.WRITER, ROLES.EDITOR],
  },
  EDIT_ORDER: {
    roles: [ROLES.ADMIN, ROLES.SUPERADMIN, ROLES.WRITER, ROLES.EDITOR],
  },
  
  // User management
  VIEW_USERS: {
    roles: [ROLES.ADMIN, ROLES.SUPERADMIN],
  },
  MANAGE_USERS: {
    roles: [ROLES.ADMIN, ROLES.SUPERADMIN],
  },
  IMPERSONATE: {
    roles: [ROLES.ADMIN, ROLES.SUPERADMIN],
  },
  
  // Financial
  VIEW_FINANCIALS: {
    roles: [ROLES.ADMIN, ROLES.SUPERADMIN, ROLES.WRITER, ROLES.CLIENT],
  },
  MANAGE_PAYMENTS: {
    roles: [ROLES.ADMIN, ROLES.SUPERADMIN],
  },
  
  // Settings
  MANAGE_SETTINGS: {
    roles: [ROLES.ADMIN, ROLES.SUPERADMIN],
  },
}

/**
 * Check if user has permission
 */
export function hasPermission(userRole, permission) {
  if (!userRole || !permission) return false
  return PERMISSIONS[permission]?.roles?.includes(userRole) || false
}

/**
 * Check if user has any of the specified roles
 */
export function hasRole(userRole, roles) {
  if (!userRole || !roles) return false
  return Array.isArray(roles) ? roles.includes(userRole) : roles === userRole
}

/**
 * Get accessible routes for a role
 */
export function getAccessibleRoutes(role) {
  const routes = {
    [ROLES.SUPERADMIN]: [
      'dashboard', 'orders', 'users', 'writers', 'clients', 'settings',
      'analytics', 'payments', 'fines', 'tickets', 'communications',
    ],
    [ROLES.ADMIN]: [
      'dashboard', 'orders', 'users', 'writers', 'clients', 'settings',
      'analytics', 'payments', 'fines', 'tickets', 'communications',
    ],
    [ROLES.CLIENT]: [
      'dashboard', 'orders', 'profile', 'payments', 'tickets', 'communications',
    ],
    [ROLES.WRITER]: [
      'dashboard', 'orders', 'profile', 'earnings', 'tickets', 'communications',
    ],
    [ROLES.EDITOR]: [
      'dashboard', 'orders', 'profile', 'tickets', 'communications',
    ],
    [ROLES.SUPPORT]: [
      'dashboard', 'tickets', 'communications', 'orders',
    ],
  }
  
  return routes[role] || []
}

