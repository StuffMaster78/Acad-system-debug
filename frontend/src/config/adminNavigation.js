/**
 * Admin/Superadmin Navigation Configuration
 * Organized by logical groups following UI/UX best practices
 */

export const adminNavigationGroups = [
  {
    id: 'core-operations',
    label: 'Core Operations',
    icon: '⚙️',
    items: [
      {
        name: 'OrderManagement',
        to: '/admin/orders',
        label: 'Order Management',
        icon: '📋',
        description: 'Manage all orders, assignments, and status',
      },
      {
        name: 'SpecialOrderManagement',
        to: '/admin/special-orders',
        label: 'Special Orders',
        icon: '⭐',
        description: 'Handle special and custom orders',
      },
      {
        name: 'UserManagement',
        to: '/admin/users',
        label: 'User Management',
        icon: '👥',
        description: 'Manage users, roles, and permissions',
      },
      {
        name: 'SupportTicketsManagement',
        to: '/admin/support-tickets',
        label: 'Support Tickets',
        icon: '🎫',
        description: 'Manage customer support tickets',
        roles: ['admin', 'superadmin', 'support'],
      },
    ],
  },
  {
    id: 'financial',
    label: 'Financial Management',
    icon: '💰',
    items: [
      {
        name: 'Payments',
        to: '/admin/payments/writer-payments',
        label: 'Writer Payments',
        icon: '💳',
        description: 'Manage writer payments and payouts',
      },
      {
        name: 'RefundManagement',
        to: '/admin/refunds',
        label: 'Refunds',
        icon: '↩️',
        description: 'Process and manage refunds',
      },
      {
        name: 'DisputeManagement',
        to: '/admin/disputes',
        label: 'Disputes',
        icon: '⚖️',
        description: 'Resolve order disputes',
      },
      {
        name: 'TipManagement',
        to: '/admin/tips',
        label: 'Tips',
        icon: '💸',
        description: 'Manage writer tips',
      },
      {
        name: 'FinesManagement',
        to: '/admin/fines',
        label: 'Fines',
        icon: '🚫',
        description: 'Manage fines and penalties',
      },
      {
        name: 'AdvancePaymentsManagement',
        to: '/admin/advance-payments',
        label: 'Advance Payments',
        icon: '💵',
        description: 'Manage advance payment requests',
      },
      {
        name: 'WalletManagement',
        to: '/admin/wallets',
        label: 'Wallets',
        icon: '💼',
        description: 'Manage user wallets',
      },
      {
        name: 'FinancialOverview',
        to: '/admin/financial-overview',
        label: 'Financial Overview',
        icon: '📊',
        description: 'Financial analytics and reports',
      },
      {
        name: 'InvoiceManagement',
        to: '/admin/invoices',
        label: 'Invoices',
        icon: '📄',
        description: 'Manage invoices',
      },
    ],
  },
  {
    id: 'content',
    label: 'Content & Services',
    icon: '📝',
    items: [
      {
        name: 'ReviewsManagement',
        to: '/admin/reviews',
        label: 'Reviews',
        icon: '💬',
        description: 'Manage reviews and ratings',
      },
      {
        name: 'ReviewModeration',
        to: '/admin/reviews/moderation',
        label: 'Review Moderation',
        icon: '✅',
        description: 'Moderate user reviews',
      },
      {
        name: 'ReviewAggregation',
        to: '/admin/review-aggregation',
        label: 'Review Aggregation',
        icon: '⭐',
        description: 'Aggregate and analyze reviews',
      },
      {
        name: 'ClassManagement',
        to: '/admin/class-management',
        label: 'Class Management',
        icon: '📚',
        description: 'Manage class bundles',
      },
      {
        name: 'ExpressClassesManagement',
        to: '/admin/express-classes',
        label: 'Express Classes',
        icon: '⚡',
        description: 'Manage express class offerings',
      },
      {
        name: 'BlogManagement',
        to: '/admin/blog',
        label: 'Blog Pages',
        icon: '📝',
        description: 'Manage blog content',
      },
      {
        name: 'SEOPagesManagement',
        to: '/admin/seo-pages',
        label: 'SEO Pages',
        icon: '🔍',
        description: 'Manage SEO landing pages',
      },
      {
        name: 'FileManagement',
        to: '/admin/files',
        label: 'File Management',
        icon: '📁',
        description: 'Manage system files',
      },
    ],
  },
  {
    id: 'analytics',
    label: 'Analytics & Reporting',
    icon: '📊',
    items: [
      {
        name: 'AdvancedAnalytics',
        to: '/admin/advanced-analytics',
        label: 'Advanced Analytics',
        icon: '📈',
        description: 'Comprehensive analytics dashboard',
      },
      {
        name: 'EnhancedAnalytics',
        to: '/admin/enhanced-analytics',
        label: 'Enhanced Analytics',
        icon: '📉',
        description: 'Enhanced performance metrics',
      },
      {
        name: 'PricingAnalytics',
        to: '/admin/pricing-analytics',
        label: 'Pricing Analytics',
        icon: '💰',
        description: 'Pricing trends and analysis',
      },
      {
        name: 'DiscountAnalytics',
        to: '/admin/discount-analytics',
        label: 'Discount Analytics',
        icon: '🎟️',
        description: 'Discount usage and effectiveness',
      },
      {
        name: 'WriterPerformanceAnalytics',
        to: '/admin/writer-performance',
        label: 'Writer Performance',
        icon: '👤',
        description: 'Writer performance metrics',
      },
      {
        name: 'ReferralTracking',
        to: '/admin/referral-tracking',
        label: 'Referral Tracking',
        icon: '🎁',
        description: 'Track referral programs',
      },
      {
        name: 'LoyaltyTracking',
        to: '/admin/loyalty-tracking',
        label: 'Loyalty Tracking',
        icon: '⭐',
        description: 'Track loyalty program usage',
      },
      {
        name: 'LoyaltyManagement',
        to: '/admin/loyalty-management',
        label: 'Loyalty Management',
        icon: '🏆',
        description: 'Manage loyalty programs',
      },
      {
        name: 'CampaignPerformanceDashboard',
        to: '/admin/campaigns',
        label: 'Campaign Analytics',
        icon: '📢',
        description: 'Campaign performance metrics',
      },
    ],
  },
  {
    id: 'system',
    label: 'System Management',
    icon: '⚙️',
    items: [
      {
        name: 'ConfigManagement',
        to: '/admin/configs',
        label: 'Configurations',
        icon: '🎛️',
        description: 'System and pricing configurations',
      },
      {
        name: 'SystemHealth',
        to: '/admin/system-health',
        label: 'System Health',
        icon: '🏥',
        description: 'Monitor system performance',
      },
      {
        name: 'ActivityLogs',
        to: '/admin/activity-logs',
        label: 'Activity Logs',
        icon: '📋',
        description: 'View system activity logs',
      },
      {
        name: 'EmailManagement',
        to: '/admin/emails',
        label: 'Email Management',
        icon: '📧',
        description: 'Manage email templates and campaigns',
      },
      {
        name: 'NotificationProfiles',
        to: '/admin/notification-profiles',
        label: 'Notification Profiles',
        icon: '🔔',
        description: 'Configure notification profiles',
      },
      {
        name: 'NotificationGroups',
        to: '/admin/notification-groups',
        label: 'Notification Groups',
        icon: '👥',
        description: 'Manage notification groups',
      },
      {
        name: 'DuplicateAccountDetection',
        to: '/admin/duplicate-detection',
        label: 'Duplicate Detection',
        icon: '🔍',
        description: 'Detect duplicate accounts',
      },
    ],
  },
  {
    id: 'discipline',
    label: 'Discipline & Appeals',
    icon: '⚖️',
    items: [
      {
        name: 'WriterDisciplineManagement',
        to: '/admin/writer-discipline',
        label: 'Writer Discipline',
        icon: '📜',
        description: 'Manage writer discipline actions',
      },
      {
        name: 'AppealsManagement',
        to: '/admin/appeals',
        label: 'Appeals',
        icon: '📝',
        description: 'Handle discipline appeals',
      },
      {
        name: 'DisciplineConfig',
        to: '/admin/discipline-config',
        label: 'Discipline Config',
        icon: '⚙️',
        description: 'Configure discipline rules',
      },
    ],
  },
  {
    id: 'multi-tenant',
    label: 'Multi-Tenant',
    icon: '🌐',
    items: [
      {
        name: 'WebsiteManagement',
        to: '/websites',
        label: 'Websites',
        icon: '🌐',
        description: 'Manage multi-tenant websites',
      },
    ],
  },
  {
    id: 'superadmin-only',
    label: 'Superadmin',
    icon: '👑',
    roles: ['superadmin'],
    items: [
      {
        name: 'SuperadminDashboard',
        to: '/admin/superadmin',
        label: 'Superadmin Dashboard',
        icon: '👑',
        description: 'Superadmin overview and controls',
      },
    ],
  },
]

/**
 * Get navigation groups filtered by user role
 */
export function getAdminNavigationGroups(userRole) {
  return adminNavigationGroups.filter(group => {
    // Filter groups by role
    if (group.roles && !group.roles.includes(userRole)) {
      return false
    }
    // Filter items within groups by role
    if (group.items) {
      group.items = group.items.filter(item => {
        if (item.roles && !item.roles.includes(userRole)) {
          return false
        }
        return true
      })
    }
    // Only return groups that have items
    return !group.items || group.items.length > 0
  })
}

/**
 * Get all navigation items as a flat list (for backward compatibility)
 */
export function getAllAdminNavigationItems(userRole) {
  const groups = getAdminNavigationGroups(userRole)
  return groups.flatMap(group => group.items || [])
}

