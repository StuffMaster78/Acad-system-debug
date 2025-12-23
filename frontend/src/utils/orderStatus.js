/**
 * Enhanced Order Status System
 * Centralized status definitions with icons, colors, descriptions, and metadata
 */

export const ORDER_STATUS_CONFIG = {
  // Initial States
  created: {
    label: 'Created',
    icon: '🟢',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    description: 'Order has been created and is being processed',
    category: 'initial',
    priority: 'low'
  },
  pending: {
    label: 'Pending',
    icon: '⏳',
    color: 'yellow',
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-300',
    description: 'Order is pending payment or assignment',
    category: 'initial',
    priority: 'medium'
  },
  unpaid: {
    label: 'Unpaid',
    icon: '💳',
    color: 'orange',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-800',
    borderColor: 'border-orange-300',
    description: 'Order is waiting for payment',
    category: 'payment',
    priority: 'high'
  },
  paid: {
    label: 'Paid',
    icon: '✅',
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
    description: 'Payment has been received',
    category: 'payment',
    priority: 'low'
  },
  
  // Assignment & Availability
  pending_writer_assignment: {
    label: 'Pending Assignment',
    icon: '⏳',
    color: 'indigo',
    bgColor: 'bg-indigo-100',
    textColor: 'text-indigo-800',
    borderColor: 'border-indigo-300',
    description: 'Waiting for writer assignment',
    category: 'assignment',
    priority: 'medium'
  },
  available: {
    label: 'Available',
    icon: '📋',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
    description: 'Order is available for writers to take',
    category: 'assignment',
    priority: 'medium'
  },
  pending_preferred: {
    label: 'Pending Preferred',
    icon: '⭐',
    color: 'purple',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-800',
    borderColor: 'border-purple-300',
    description: 'Waiting for preferred writer assignment',
    category: 'assignment',
    priority: 'medium'
  },
  assigned: {
    label: 'Assigned',
    icon: '👤',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
    description: 'Order has been assigned to a writer',
    category: 'assignment',
    priority: 'low'
  },
  reassigned: {
    label: 'Reassigned',
    icon: '🔄',
    color: 'cyan',
    bgColor: 'bg-cyan-100',
    textColor: 'text-cyan-800',
    borderColor: 'border-cyan-300',
    description: 'Order has been reassigned to another writer',
    category: 'assignment',
    priority: 'high'
  },
  
  // Active Work States
  in_progress: {
    label: 'In Progress',
    icon: '⚙️',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
    description: 'Writer is actively working on the order',
    category: 'active',
    priority: 'medium'
  },
  draft: {
    label: 'Draft',
    icon: '📝',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    description: 'Order is in draft stage',
    category: 'active',
    priority: 'low'
  },
  on_hold: {
    label: 'On Hold',
    icon: '⏸️',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    description: 'Order work is temporarily paused',
    category: 'active',
    priority: 'medium'
  },
  under_editing: {
    label: 'Under Editing',
    icon: '✏️',
    color: 'purple',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-800',
    borderColor: 'border-purple-300',
    description: 'Order is being edited by an editor',
    category: 'active',
    priority: 'medium'
  },
  
  // Submission and Review States
  submitted: {
    label: 'Submitted',
    icon: '📤',
    color: 'purple',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-800',
    borderColor: 'border-purple-300',
    description: 'Order has been submitted for review',
    category: 'review',
    priority: 'medium'
  },
  in_review: {
    label: 'In Review',
    icon: '🔍',
    color: 'indigo',
    bgColor: 'bg-indigo-100',
    textColor: 'text-indigo-800',
    borderColor: 'border-indigo-300',
    description: 'Order is being reviewed',
    category: 'review',
    priority: 'medium'
  },
  under_review: {
    label: 'Under Review',
    icon: '🔍',
    color: 'indigo',
    bgColor: 'bg-indigo-100',
    textColor: 'text-indigo-800',
    borderColor: 'border-indigo-300',
    description: 'Order is under review',
    category: 'review',
    priority: 'medium'
  },
  reviewed: {
    label: 'Reviewed',
    icon: '👁️',
    color: 'teal',
    bgColor: 'bg-teal-100',
    textColor: 'text-teal-800',
    borderColor: 'border-teal-300',
    description: 'Order has been reviewed',
    category: 'review',
    priority: 'low'
  },
  rated: {
    label: 'Rated',
    icon: '⭐',
    color: 'amber',
    bgColor: 'bg-amber-100',
    textColor: 'text-amber-800',
    borderColor: 'border-amber-300',
    description: 'Order has been rated',
    category: 'review',
    priority: 'low'
  },
  
  // Revision States
  revision_requested: {
    label: 'Revision Requested',
    icon: '🔄',
    color: 'orange',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-800',
    borderColor: 'border-orange-300',
    description: 'Client has requested revisions',
    category: 'revision',
    priority: 'high'
  },
  revision_in_progress: {
    label: 'Revision In Progress',
    icon: '🔧',
    color: 'orange',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-800',
    borderColor: 'border-orange-300',
    description: 'Writer is working on requested revisions',
    category: 'revision',
    priority: 'high'
  },
  on_revision: {
    label: 'On Revision',
    icon: '📝',
    color: 'yellow',
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-300',
    description: 'Order is being revised',
    category: 'revision',
    priority: 'high'
  },
  revised: {
    label: 'Revised',
    icon: '✅',
    color: 'lime',
    bgColor: 'bg-lime-100',
    textColor: 'text-lime-800',
    borderColor: 'border-lime-300',
    description: 'Revisions have been completed',
    category: 'revision',
    priority: 'medium'
  },
  
  // Completion States
  approved: {
    label: 'Approved',
    icon: '✅',
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
    description: 'Order has been approved',
    category: 'completed',
    priority: 'low'
  },
  completed: {
    label: 'Completed',
    icon: '🎉',
    color: 'emerald',
    bgColor: 'bg-emerald-100',
    textColor: 'text-emerald-800',
    borderColor: 'border-emerald-300',
    description: 'Order has been completed',
    category: 'completed',
    priority: 'low'
  },
  closed: {
    label: 'Closed',
    icon: '🔒',
    color: 'slate',
    bgColor: 'bg-slate-100',
    textColor: 'text-slate-800',
    borderColor: 'border-slate-300',
    description: 'Order has been closed',
    category: 'completed',
    priority: 'low'
  },
  archived: {
    label: 'Archived',
    icon: '📦',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    description: 'Order has been archived',
    category: 'completed',
    priority: 'low'
  },
  
  // Issues & Problems
  disputed: {
    label: 'Disputed',
    icon: '⚠️',
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
    description: 'Order has a dispute that needs resolution',
    category: 'issue',
    priority: 'critical'
  },
  late: {
    label: 'Late',
    icon: '⏰',
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
    description: 'Order is past its deadline',
    category: 'issue',
    priority: 'high'
  },
  critical: {
    label: 'Critical',
    icon: '🚨',
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
    description: 'Order requires immediate attention',
    category: 'issue',
    priority: 'critical'
  },
  
  // Cancellation & Refund States
  cancelled: {
    label: 'Cancelled',
    icon: '❌',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    description: 'Order has been cancelled',
    category: 'cancelled',
    priority: 'low'
  },
  refunded: {
    label: 'Refunded',
    icon: '💰',
    color: 'pink',
    bgColor: 'bg-pink-100',
    textColor: 'text-pink-800',
    borderColor: 'border-pink-300',
    description: 'Order payment has been refunded',
    category: 'cancelled',
    priority: 'low'
  },
  rejected: {
    label: 'Rejected',
    icon: '🚫',
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
    description: 'Order has been rejected',
    category: 'cancelled',
    priority: 'medium'
  },
  
  // System States
  expired: {
    label: 'Expired',
    icon: '⏱️',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    description: 'Order has expired',
    category: 'system',
    priority: 'low'
  },
  re_opened: {
    label: 'Reopened',
    icon: '🔓',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
    description: 'Order has been reopened',
    category: 'system',
    priority: 'medium'
  }
}

/**
 * Get status configuration
 */
export function getStatusConfig(status) {
  const normalizedStatus = (status || '').toLowerCase().replace(/\s+/g, '_')
  return ORDER_STATUS_CONFIG[normalizedStatus] || {
    label: status || 'Unknown',
    icon: '❓',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    description: 'Unknown status',
    category: 'unknown',
    priority: 'low'
  }
}

/**
 * Get status label
 */
export function getStatusLabel(status) {
  return getStatusConfig(status).label
}

/**
 * Get status icon
 */
export function getStatusIcon(status) {
  return getStatusConfig(status).icon
}

/**
 * Get status badge classes
 */
export function getStatusBadgeClasses(status, variant = 'default') {
  const config = getStatusConfig(status)
  
  if (variant === 'outline') {
    return `${config.borderColor} border-2 ${config.textColor} bg-transparent`
  }
  
  if (variant === 'solid') {
    // Convert bg-{color}-100 to bg-{color}-600 for solid variant
    const solidColor = config.color === 'gray' ? 'gray' : 
                      config.color === 'slate' ? 'slate' :
                      config.color === 'emerald' ? 'emerald' :
                      config.color === 'lime' ? 'lime' :
                      config.color === 'amber' ? 'amber' :
                      config.color === 'teal' ? 'teal' :
                      config.color === 'cyan' ? 'cyan' :
                      config.color === 'indigo' ? 'indigo' :
                      config.color === 'pink' ? 'pink' : config.color
    return `bg-${solidColor}-600 text-white border-${solidColor}-600`
  }
  
  return `${config.bgColor} ${config.textColor} ${config.borderColor}`
}

/**
 * Get status category
 */
export function getStatusCategory(status) {
  return getStatusConfig(status).category
}

/**
 * Get status priority
 */
export function getStatusPriority(status) {
  return getStatusConfig(status).priority
}

/**
 * Get status description
 */
export function getStatusDescription(status) {
  return getStatusConfig(status).description
}

/**
 * Check if status is in a specific category
 */
export function isStatusInCategory(status, category) {
  return getStatusCategory(status) === category
}

/**
 * Get all statuses in a category
 */
export function getStatusesByCategory(category) {
  return Object.entries(ORDER_STATUS_CONFIG)
    .filter(([_, config]) => config.category === category)
    .map(([key, config]) => ({ value: key, ...config }))
}

/**
 * Status categories
 */
export const STATUS_CATEGORIES = {
  initial: 'Initial States',
  payment: 'Payment States',
  assignment: 'Assignment & Availability',
  active: 'Active Work',
  review: 'Review & Rating',
  revision: 'Revision States',
  completed: 'Completion States',
  issue: 'Issues & Problems',
  cancelled: 'Cancellation & Refund',
  system: 'System States'
}

