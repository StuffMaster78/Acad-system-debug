/**
 * Modern Navigation Configuration
 * 
 * Design Principles:
 * 1. Flat hierarchy (max 2 levels)
 * 2. Icon-first design
 * 3. Search-driven (not group-driven)
 * 4. User workflow focused
 * 5. Progressive disclosure (core → more)
 */

/**
 * Core Navigation Items (Always Visible)
 * These are the 80% use case - most accessed features
 */
export const coreNavigation = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'home',
    to: '/dashboard',
    color: 'indigo',
    roles: ['all'],
    description: 'Overview and key metrics',
  },
  {
    id: 'orders',
    label: 'Orders',
    icon: 'clipboard-list',
    to: '/admin/orders',
    color: 'blue',
    roles: ['admin', 'superadmin', 'support'],
    badge: 'orderCount',
    description: 'Manage all orders',
    quickLinks: [
      { label: 'All Orders', to: '/admin/orders', badge: 'total' },
      { label: 'Pending', to: '/admin/orders?status=pending', badge: 'pending', color: 'yellow' },
      { label: 'In Progress', to: '/admin/orders?status=in_progress', badge: 'in_progress', color: 'blue' },
      { label: 'Submitted', to: '/admin/orders?status=submitted', badge: 'submitted', color: 'indigo' },
      { label: 'Completed', to: '/admin/orders?status=completed', badge: 'completed', color: 'green' },
      { label: 'Revisions', to: '/admin/orders?status=revision_requested', badge: 'revision_requested', color: 'amber' },
      { label: 'Disputed', to: '/admin/orders?status=disputed', badge: 'disputed', color: 'red' },
    ],
  },
  {
    id: 'financial',
    label: 'Financial',
    icon: 'currency-dollar',
    to: '/admin/payments/client-payments',
    color: 'green',
    roles: ['admin', 'superadmin'],
    description: 'Payments and financial operations',
    quickLinks: [
      { label: 'Client Payments', to: '/admin/payments/client-payments', icon: 'credit-card' },
      { label: 'Writer Payments', to: '/admin/payments/writer-payments', icon: 'cash' },
      { label: 'Invoices', to: '/admin/invoices', icon: 'document-text' },
      { label: 'Refunds', to: '/admin/refunds', icon: 'arrow-left' },
      { label: 'Wallets', to: '/admin/wallets', icon: 'wallet' },
    ],
  },
  {
    id: 'users',
    label: 'Users',
    icon: 'users',
    to: '/admin/users',
    color: 'purple',
    roles: ['admin', 'superadmin'],
    description: 'User management and roles',
  },
  {
    id: 'support',
    label: 'Support',
    icon: 'support',
    to: '/admin/support-tickets',
    color: 'orange',
    roles: ['admin', 'superadmin', 'support'],
    badge: 'supportTicketCount',
    description: 'Customer support and tickets',
    quickLinks: [
      { label: 'Tickets', to: '/admin/support-tickets', badge: 'open' },
      { label: 'Escalations', to: '/admin/escalations', badge: 'escalated' },
      { label: 'FAQs', to: '/admin/faqs', icon: 'question-mark-circle' },
    ],
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: 'chart-bar',
    to: '/admin/analytics-reports',
    color: 'emerald',
    roles: ['admin', 'superadmin'],
    description: 'Reports and insights',
    quickLinks: [
      { label: 'Overview', to: '/admin/analytics-reports', icon: 'chart-pie' },
      { label: 'Financial', to: '/admin/financial-overview', icon: 'currency-dollar' },
      { label: 'Performance', to: '/admin/writer-performance', icon: 'trending-up' },
      { label: 'Geographic', to: '/admin/geographic-analytics', icon: 'globe' },
    ],
  },
  {
    id: 'websites',
    label: 'Websites',
    icon: 'globe-alt',
    to: '/websites',
    color: 'cyan',
    roles: ['admin', 'superadmin'],
    description: 'Multi-tenant website management',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: 'cog',
    to: '/admin/configs',
    color: 'gray',
    roles: ['admin', 'superadmin'],
    description: 'System configuration',
  },
]

/**
 * Client Navigation (Simplified)
 */
export const clientNavigation = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'home',
    to: '/dashboard',
    color: 'indigo',
  },
  {
    id: 'orders',
    label: 'My Orders',
    icon: 'clipboard-list',
    to: '/client/orders',
    color: 'blue',
    badge: 'orderCount',
    quickLinks: [
      { label: 'All', to: '/client/orders', badge: 'total' },
      { label: 'Unpaid', to: '/client/orders?is_paid=false', badge: 'unpaid', color: 'orange' },
      { label: 'Pending', to: '/client/orders?status=pending', badge: 'pending', color: 'yellow' },
      { label: 'In Progress', to: '/client/orders?status=in_progress', badge: 'in_progress', color: 'blue' },
      { label: 'Completed', to: '/client/orders?status=completed', badge: 'completed', color: 'green' },
      { label: 'Revisions', to: '/client/orders?status=revision_requested', badge: 'revision_requested', color: 'amber' },
    ],
  },
  {
    id: 'wallet',
    label: 'Wallet',
    icon: 'wallet',
    to: '/wallet',
    color: 'green',
  },
  {
    id: 'payments',
    label: 'Payments',
    icon: 'credit-card',
    to: '/payments',
    color: 'emerald',
  },
  {
    id: 'loyalty',
    label: 'Loyalty',
    icon: 'star',
    to: '/loyalty',
    color: 'yellow',
  },
  {
    id: 'messages',
    label: 'Messages',
    icon: 'chat',
    to: '/messages',
    color: 'blue',
    badge: 'unreadMessages',
  },
  {
    id: 'profile',
    label: 'Profile',
    icon: 'user',
    to: '/profile',
    color: 'gray',
  },
]

/**
 * Writer Navigation (Simplified)
 */
export const writerNavigation = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'home',
    to: '/dashboard',
    color: 'indigo',
  },
  {
    id: 'orders',
    label: 'My Orders',
    icon: 'clipboard-list',
    to: '/writer/orders',
    color: 'blue',
    badge: 'orderCount',
    quickLinks: [
      { label: 'Queue', to: '/writer/queue', badge: 'available' },
      { label: 'Active', to: '/writer/orders', badge: 'active' },
      { label: 'Revisions', to: '/writer/orders?status=revision_requested', badge: 'revisions' },
    ],
  },
  {
    id: 'earnings',
    label: 'Earnings',
    icon: 'cash',
    to: '/writer/payments',
    color: 'green',
    quickLinks: [
      { label: 'Payments', to: '/writer/payments' },
      { label: 'Request Payment', to: '/writer/payment-request' },
      { label: 'Advance Payments', to: '/writer/advance-payments' },
    ],
  },
  {
    id: 'performance',
    label: 'Performance',
    icon: 'chart-bar',
    to: '/writer/performance',
    color: 'purple',
  },
  {
    id: 'messages',
    label: 'Messages',
    icon: 'chat',
    to: '/messages',
    color: 'blue',
    badge: 'unreadMessages',
  },
  {
    id: 'profile',
    label: 'Profile',
    icon: 'user',
    to: '/writer/profile-settings',
    color: 'gray',
  },
]

/**
 * "More" Items (Less Frequently Used)
 * Organized by category for the "More" section
 */
export const moreNavigation = {
  admin: [
    // Orders & Operations
    {
      category: 'Orders',
      items: [
        { label: 'Special Orders', to: '/admin/special-orders', icon: 'star', color: 'yellow' },
        { label: 'Class Orders', to: '/admin/class-orders', icon: 'academic-cap', color: 'blue' },
        { label: 'Order Templates', to: '/admin/order-templates', icon: 'template', color: 'indigo' },
      ],
    },
    // Financial
    {
      category: 'Financial',
      items: [
        { label: 'Disputes', to: '/admin/disputes', icon: 'scale', color: 'red' },
        { label: 'Tips', to: '/admin/tips', icon: 'cash', color: 'green' },
        { label: 'Fines', to: '/admin/fines', icon: 'ban', color: 'red' },
        { label: 'Advance Payments', to: '/admin/advance-payments', icon: 'currency-dollar', color: 'green' },
      ],
    },
    // Content
    {
      category: 'Content',
      items: [
        { label: 'Blog', to: '/admin/blog', icon: 'document-text', color: 'indigo' },
        { label: 'SEO Pages', to: '/admin/seo-pages', icon: 'search', color: 'purple' },
        { label: 'Media Library', to: '/admin/media-library', icon: 'photograph', color: 'pink' },
        { label: 'Email Campaigns', to: '/admin/emails', icon: 'mail', color: 'blue' },
      ],
    },
    // Users & Access
    {
      category: 'Users & Access',
      items: [
        { label: 'Writer Discipline', to: '/admin/writer-discipline', icon: 'shield-exclamation', color: 'red' },
        { label: 'Appeals', to: '/admin/appeals', icon: 'document-duplicate', color: 'yellow' },
        { label: 'Duplicate Detection', to: '/admin/duplicate-detection', icon: 'duplicate', color: 'orange' },
      ],
    },
    // System
    {
      category: 'System',
      items: [
        { label: 'System Health', to: '/admin/system-health', icon: 'heart', color: 'red' },
        { label: 'Activity Logs', to: '/admin/activity-logs', icon: 'clipboard-list', color: 'gray' },
        { label: 'Performance', to: '/admin/performance-monitoring', icon: 'lightning-bolt', color: 'yellow' },
        { label: 'Notifications', to: '/admin/notification-profiles', icon: 'bell', color: 'blue' },
      ],
    },
    // Analytics (Advanced)
    {
      category: 'Advanced Analytics',
      items: [
        { label: 'Pricing Analytics', to: '/admin/pricing-analytics', icon: 'tag', color: 'green' },
        { label: 'Discount Analytics', to: '/admin/discount-analytics', icon: 'ticket', color: 'purple' },
        { label: 'Campaign Analytics', to: '/admin/campaigns', icon: 'megaphone', color: 'orange' },
        { label: 'Writer Badges', to: '/admin/writer-badge-analytics', icon: 'badge-check', color: 'blue' },
        { label: 'Loyalty Tracking', to: '/admin/loyalty-tracking', icon: 'star', color: 'yellow' },
        { label: 'Referral Tracking', to: '/admin/referral-tracking', icon: 'gift', color: 'pink' },
        { label: 'Newsletter Analytics', to: '/admin/newsletter-analytics', icon: 'mail-open', color: 'indigo' },
        { label: 'Blog Analytics', to: '/admin/blog-analytics', icon: 'chart-line', color: 'purple' },
      ],
    },
    // Superadmin Only
    {
      category: 'Superadmin',
      roles: ['superadmin'],
      items: [
        { label: 'Superadmin Dashboard', to: '/admin/superadmin', icon: 'shield-check', color: 'purple' },
        { label: 'Superadmin Logs', to: '/admin/superadmin-logs', icon: 'clipboard-check', color: 'gray' },
        { label: 'Data Exports', to: '/admin/data-exports', icon: 'download', color: 'blue' },
      ],
    },
  ],
}

/**
 * Get navigation for current user role
 */
export function getNavigationForRole(role) {
  if (role === 'client') return clientNavigation
  if (role === 'writer') return writerNavigation
  if (role === 'admin' || role === 'superadmin') {
    const core = coreNavigation.filter(item => 
      !item.roles || item.roles.includes('all') || item.roles.includes(role)
    )
    const more = moreNavigation.admin.filter(group =>
      !group.roles || group.roles.includes(role)
    )
    return { core, more }
  }
  return { core: [], more: [] }
}

/**
 * Search through all navigation items
 */
export function searchNavigation(query, role) {
  const navigation = getNavigationForRole(role)
  const allItems = []
  
  // Add core items
  if (navigation.core) {
    navigation.core.forEach(item => {
      allItems.push(item)
      if (item.quickLinks) {
        item.quickLinks.forEach(link => {
          allItems.push({
            ...link,
            parent: item.label,
            color: item.color,
          })
        })
      }
    })
  }
  
  // Add more items
  if (navigation.more) {
    navigation.more.forEach(group => {
      group.items.forEach(item => {
        allItems.push({
          ...item,
          category: group.category,
        })
      })
    })
  }
  
  // Fuzzy search
  const lowerQuery = query.toLowerCase()
  return allItems.filter(item => {
    const searchText = `${item.label} ${item.description || ''} ${item.category || ''} ${item.parent || ''}`.toLowerCase()
    return searchText.includes(lowerQuery)
  }).slice(0, 10)
}

/**
 * Icon mapping (Heroicons)
 */
export const iconMap = {
  'home': 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  'clipboard-list': 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
  'currency-dollar': 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  'users': 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
  'support': 'M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z',
  'chart-bar': 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  'globe-alt': 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9',
  'cog': 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
  'wallet': 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
  'credit-card': 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
  'star': 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z',
  'chat': 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
  'user': 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  'cash': 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
  'ticket': 'M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z',
  'academic-cap': 'M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z',
  'document-text': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  'arrow-left': 'M10 19l-7-7m0 0l7-7m-7 7h18',
  'scale': 'M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3',
  'ban': 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636',
  'search': 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
  'photograph': 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
  'mail': 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  'heart': 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
  'bell': 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
  'lightning-bolt': 'M13 10V3L4 14h7v7l9-11h-7z',
  'trending-up': 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
  'chart-pie': 'M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z',
  'tag': 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z',
  'megaphone': 'M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z',
  'badge-check': 'M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z',
  'gift': 'M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7',
  'shield-check': 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  'download': 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4',
  'mail-open': 'M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76',
  'chart-line': 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z',
  'template': 'M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z',
  'shield-exclamation': 'M20.618 5.984A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016zM12 9v2m0 4h.01',
  'document-duplicate': 'M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2',
  'duplicate': 'M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z',
  'clock': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  'check-circle': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  'exclamation-triangle': 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  'pencil': 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z',
  'paper-airplane': 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8',
  'clipboard': 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
  'clipboard-check': 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
  'question-mark-circle': 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
}

/**
 * Category color mapping
 */
export const categoryColors = {
  'Orders': 'blue',
  'Financial': 'green',
  'Content': 'indigo',
  'Users & Access': 'purple',
  'System': 'gray',
  'Advanced Analytics': 'emerald',
  'Superadmin': 'violet',
}

/**
 * Get color classes for a category
 */
export function getCategoryColorClasses(color) {
  const colors = {
    blue: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      bgHover: 'hover:bg-blue-100 dark:hover:bg-blue-900/30',
      text: 'text-blue-700 dark:text-blue-300',
      icon: 'text-blue-600 dark:text-blue-400',
      border: 'border-blue-500',
      badge: 'bg-blue-100 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200',
    },
    green: {
      bg: 'bg-green-50 dark:bg-green-900/20',
      bgHover: 'hover:bg-green-100 dark:hover:bg-green-900/30',
      text: 'text-green-700 dark:text-green-300',
      icon: 'text-green-600 dark:text-green-400',
      border: 'border-green-500',
      badge: 'bg-green-100 dark:bg-green-900/60 text-green-800 dark:text-green-200',
    },
    purple: {
      bg: 'bg-purple-50 dark:bg-purple-900/20',
      bgHover: 'hover:bg-purple-100 dark:hover:bg-purple-900/30',
      text: 'text-purple-700 dark:text-purple-300',
      icon: 'text-purple-600 dark:text-purple-400',
      border: 'border-purple-500',
      badge: 'bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200',
    },
    orange: {
      bg: 'bg-orange-50 dark:bg-orange-900/20',
      bgHover: 'hover:bg-orange-100 dark:hover:bg-orange-900/30',
      text: 'text-orange-700 dark:text-orange-300',
      icon: 'text-orange-600 dark:text-orange-400',
      border: 'border-orange-500',
      badge: 'bg-orange-100 dark:bg-orange-900/60 text-orange-800 dark:text-orange-200',
    },
    indigo: {
      bg: 'bg-indigo-50 dark:bg-indigo-900/20',
      bgHover: 'hover:bg-indigo-100 dark:hover:bg-indigo-900/30',
      text: 'text-indigo-700 dark:text-indigo-300',
      icon: 'text-indigo-600 dark:text-indigo-400',
      border: 'border-indigo-500',
      badge: 'bg-indigo-100 dark:bg-indigo-900/60 text-indigo-800 dark:text-indigo-200',
    },
    emerald: {
      bg: 'bg-emerald-50 dark:bg-emerald-900/20',
      bgHover: 'hover:bg-emerald-100 dark:hover:bg-emerald-900/30',
      text: 'text-emerald-700 dark:text-emerald-300',
      icon: 'text-emerald-600 dark:text-emerald-400',
      border: 'border-emerald-500',
      badge: 'bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200',
    },
    gray: {
      bg: 'bg-gray-50 dark:bg-gray-900/20',
      bgHover: 'hover:bg-gray-100 dark:hover:bg-gray-900/30',
      text: 'text-gray-700 dark:text-gray-300',
      icon: 'text-gray-600 dark:text-gray-400',
      border: 'border-gray-500',
      badge: 'bg-gray-100 dark:bg-gray-900/60 text-gray-800 dark:text-gray-200',
    },
    cyan: {
      bg: 'bg-cyan-50 dark:bg-cyan-900/20',
      bgHover: 'hover:bg-cyan-100 dark:hover:bg-cyan-900/30',
      text: 'text-cyan-700 dark:text-cyan-300',
      icon: 'text-cyan-600 dark:text-cyan-400',
      border: 'border-cyan-500',
      badge: 'bg-cyan-100 dark:bg-cyan-900/60 text-cyan-800 dark:text-cyan-200',
    },
    yellow: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      bgHover: 'hover:bg-yellow-100 dark:hover:bg-yellow-900/30',
      text: 'text-yellow-700 dark:text-yellow-300',
      icon: 'text-yellow-600 dark:text-yellow-400',
      border: 'border-yellow-500',
      badge: 'bg-yellow-100 dark:bg-yellow-900/60 text-yellow-800 dark:text-yellow-200',
    },
    red: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      bgHover: 'hover:bg-red-100 dark:hover:bg-red-900/30',
      text: 'text-red-700 dark:text-red-300',
      icon: 'text-red-600 dark:text-red-400',
      border: 'border-red-500',
      badge: 'bg-red-100 dark:bg-red-900/60 text-red-800 dark:text-red-200',
    },
    amber: {
      bg: 'bg-amber-50 dark:bg-amber-900/20',
      bgHover: 'hover:bg-amber-100 dark:hover:bg-amber-900/30',
      text: 'text-amber-700 dark:text-amber-300',
      icon: 'text-amber-600 dark:text-amber-400',
      border: 'border-amber-500',
      badge: 'bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200',
    },
  }
  
  return colors[color] || colors.gray
}
