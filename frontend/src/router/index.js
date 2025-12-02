import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { hasRole } from '@/utils/permissions'

const router = createRouter({
  history: createWebHistory(),
  routes: [
  {
    path: '/login',
    name: 'Login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { requiresAuth: false, title: 'Login' },
    },
    {
      path: '/password-reset',
      name: 'PasswordResetRequest',
      component: () => import('@/views/auth/PasswordResetRequest.vue'),
      meta: { requiresAuth: false, title: 'Password Reset' },
    },
    {
      path: '/password-reset/confirm',
      name: 'PasswordResetConfirm',
      component: () => import('@/views/auth/PasswordResetConfirm.vue'),
      meta: { requiresAuth: false, title: 'Set New Password' },
  },
  {
    path: '/forgot-password',
      name: 'ForgotPassword',
      component: () => import('@/views/auth/PasswordResetRequest.vue'),
      meta: { requiresAuth: false, title: 'Forgot Password' },
    },
    {
      path: '/signup',
      name: 'Signup',
      component: () => import('@/views/auth/Signup.vue'),
      meta: { requiresAuth: false, title: 'Sign Up' },
    },
    {
      path: '/impersonate',
      name: 'Impersonate',
      component: () => import('@/views/auth/Impersonate.vue'),
      meta: { requiresAuth: false, title: 'Impersonate User' },
    },
    {
      path: '/terms',
      name: 'Terms',
      component: () => import('@/views/public/Terms.vue'),
      meta: { requiresAuth: false, title: 'Terms & Conditions' },
    },
    {
      path: '/auth/magic-link',
      name: 'MagicLinkLogin',
      component: () => import('@/views/auth/MagicLinkLogin.vue'),
      meta: { requiresAuth: false, title: 'Passwordless Login' },
    },
  {
    path: '/',
      component: () => import('@/layouts/DashboardLayout.vue'),
      redirect: '/dashboard',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/Dashboard.vue'),
          meta: { requiresAuth: true, title: 'Dashboard' },
        },
        // Client routes
        {
          path: 'orders',
          name: 'Orders',
          component: () => import('@/views/orders/OrderList.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Orders',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'orders/drafts',
          name: 'OrderDrafts',
          component: () => import('@/views/orders/OrderDrafts.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Order Drafts',
            roles: ['client', 'admin', 'superadmin'],
          },
        },
        {
          path: 'orders/new',
          name: 'OrderCreate',
          component: () => import('@/views/orders/OrderCreate.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'New Order',
            roles: ['client'],
          },
        },
        {
          path: 'orders/special/new',
          name: 'SpecialOrderNew',
          component: () => import('@/views/orders/SpecialOrderNew.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Create Special Order',
            roles: ['admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'admin/orders/create',
          name: 'AdminOrderCreate',
          component: () => import('@/views/admin/AdminOrderCreate.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Create Order (Admin)',
            roles: ['admin', 'superadmin', 'support'],
          },
        },
        {
          path: 'orders/wizard',
          name: 'OrderWizard',
          component: () => import('@/views/orders/OrderWizard.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Order Wizard',
            roles: ['client'],
          },
        },
        {
          path: 'orders/templates',
          name: 'OrderTemplates',
          component: () => import('@/views/orders/OrderTemplates.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Order Templates',
            roles: ['client'],
          },
        },
        {
          path: 'orders/special-new',
          name: 'SpecialOrderNew',
          component: () => import('@/views/orders/SpecialOrderNew.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Create Special Order',
            roles: ['admin', 'superadmin', 'support', 'editor', 'writer'],
          },
        },
        {
          path: 'tickets',
          name: 'Tickets',
          component: () => import('@/views/tickets/TicketList.vue'),
          meta: {
            requiresAuth: true,
            title: 'Tickets',
            roles: ['client', 'admin', 'support'],
          },
        },
        {
          path: 'tickets/:id',
          name: 'TicketDetail',
          component: () => import('@/views/tickets/TicketDetail.vue'),
          meta: {
            requiresAuth: true,
            title: 'Ticket Detail',
            roles: ['client', 'admin', 'support'],
          },
        },
        {
          path: 'tickets/new',
          name: 'TicketCreate',
          component: () => import('@/views/tickets/TicketCreate.vue'),
          meta: {
            requiresAuth: true,
            title: 'New Ticket',
            roles: ['client', 'admin', 'support'],
          },
        },
        {
          path: 'orders/:id',
          name: 'OrderDetail',
          component: () => import('@/views/orders/OrderDetail.vue'),
          meta: { requiresAuth: true, title: 'Order Details' },
        },
        {
          path: 'orders/:id/messages',
          name: 'OrderMessages',
          component: () => import('@/views/orders/OrderMessages.vue'),
          meta: { requiresAuth: true, title: 'Order Messages' },
        },
        // Admin/Superadmin routes
        {
          path: 'users',
          name: 'Users',
          component: () => import('@/views/users/UserList.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Users',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'writers',
          name: 'Writers',
          component: () => import('@/views/writers/WriterList.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Writers',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'clients',
          name: 'Clients',
          component: () => import('@/views/clients/ClientList.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Clients',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/settings/Settings.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Settings',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'settings/login-alerts',
          name: 'LoginAlerts',
          component: () => import('@/views/settings/LoginAlerts.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Login Alert Preferences',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'payments',
          name: 'Payments',
          component: () => import('@/views/payments/PaymentHistory.vue'),
          meta: {
            requiresAuth: true,
            title: 'Payment History',
            roles: ['client', 'admin', 'superadmin'],
          },
        },
        {
          path: 'admin/payments/logs',
          name: 'PaymentLogs',
          component: () => import('@/views/admin/payments/PaymentLogs.vue'),
          meta: {
            requiresAuth: true,
            title: 'Payment Logs',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/payments/writer-payments',
          name: 'AdminWriterPayments',
          component: () => import('@/views/admin/payments/WriterPayments.vue'),
          meta: {
            requiresAuth: true,
            title: 'Writer Payments',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/advance-payments',
          name: 'AdvancePaymentsManagement',
          component: () => import('@/views/admin/AdvancePaymentsManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Advance Payments Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/invoices',
          name: 'InvoiceManagement',
          component: () => import('@/views/admin/InvoiceManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Invoice Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/holidays',
          name: 'HolidayManagement',
          component: () => import('@/views/admin/HolidayManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Holiday & Special Days Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'referrals',
          name: 'Referrals',
          component: () => import('@/views/referrals/Referrals.vue'),
          meta: {
            requiresAuth: true,
            title: 'Referrals',
            roles: ['client'], // Only clients can access referral features
          },
        },
        {
          path: 'loyalty',
          name: 'Loyalty',
          component: () => import('@/views/loyalty/Loyalty.vue'),
          meta: {
            requiresAuth: true,
            title: 'Loyalty Program',
            roles: ['client'], // Only clients can access loyalty program features
          },
        },
        {
          path: 'discounts',
          name: 'ClientDiscounts',
          component: () => import('@/views/discounts/ClientDiscounts.vue'),
          meta: {
            requiresAuth: true,
            title: 'Available Discounts',
            roles: ['client', 'admin', 'superadmin'],
          },
        },
        {
          path: 'my-discounts',
          name: 'MyDiscounts',
          component: () => import('@/views/discounts/MyDiscounts.vue'),
          meta: {
            requiresAuth: true,
            title: 'My Discounts',
            roles: ['client', 'admin', 'superadmin'],
          },
        },
        {
          path: 'notifications',
          name: 'Notifications',
          component: () => import('@/views/notifications/Notifications.vue'),
          meta: {
            requiresAuth: true,
            title: 'Notifications',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'messages',
          name: 'Messages',
          component: () => import('@/views/messages/Messages.vue'),
          meta: {
            requiresAuth: true,
            title: 'Messages',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'activity',
          name: 'ActivityLogsGeneral',
          component: () => import('@/views/activity/ActivityLogs.vue'),
          meta: {
            requiresAuth: true,
            title: 'User Activity',
            roles: ['admin', 'superadmin', 'support', 'writer', 'client', 'editor'],
          },
        },
        {
          path: 'wallet',
          name: 'Wallet',
          component: () => import('@/views/wallet/Wallet.vue'),
          meta: {
            requiresAuth: true,
            title: 'My Wallet',
            roles: ['client'],
          },
        },
        {
          path: 'writer/badges',
          name: 'WriterBadgeManagement',
          component: () => import('@/views/writers/BadgeManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Badge Management',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/profile-settings',
          name: 'WriterProfileSettings',
          component: () => import('@/views/writers/WriterProfileSettings.vue'),
          meta: {
            requiresAuth: true,
            title: 'Writer Profile Settings',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/pen-name',
          name: 'PenNameManagement',
          component: () => import('@/views/writers/PenNameManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Pen Name Management',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/performance',
          name: 'WriterPerformance',
          component: () => import('@/views/writers/Performance.vue'),
          meta: {
            requiresAuth: true,
            title: 'Performance Analytics',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/level-details',
          name: 'WriterLevelDetails',
          component: () => import('@/views/writers/WriterLevelDetails.vue'),
          meta: {
            requiresAuth: true,
            title: 'Level Details',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/tickets',
          name: 'WriterTickets',
          component: () => import('@/views/writers/Tickets.vue'),
          meta: {
            requiresAuth: true,
            title: 'My Tickets',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/tips',
          name: 'WriterTips',
          component: () => import('@/views/writers/Tips.vue'),
          meta: {
            requiresAuth: true,
            title: 'My Tips',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/fines',
          name: 'WriterFines',
          component: () => import('@/views/writers/WriterFines.vue'),
          meta: {
            requiresAuth: true,
            title: 'Fines & Appeals',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/payment-request',
          name: 'WriterPaymentRequest',
          component: () => import('@/views/writers/PaymentRequest.vue'),
          meta: {
            requiresAuth: true,
            title: 'Payment Requests',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/advance-payments',
          name: 'AdvancePayments',
          component: () => import('@/views/writers/AdvancePayments.vue'),
          meta: {
            requiresAuth: true,
            title: 'Advance Payments',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/pen-name-change',
          name: 'PenNameChangeRequest',
          component: () => import('@/views/writers/PenNameManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Pen Name Management',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/resources',
          name: 'WriterResources',
          component: () => import('@/views/writers/WriterResources.vue'),
          meta: {
            requiresAuth: true,
            title: 'Writer Resources',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/reviews',
          name: 'WriterReviews',
          component: () => import('@/views/writers/Reviews.vue'),
          meta: {
            requiresAuth: true,
            title: 'My Reviews',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/queue',
          name: 'WriterOrderQueue',
          component: () => import('@/views/writers/OrderQueue.vue'),
          meta: {
            requiresAuth: true,
            title: 'Order Queue',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/payments',
          name: 'WriterPayments',
          component: () => import('@/views/writers/WriterPayments.vue'),
          meta: {
            requiresAuth: true,
            title: 'Payments & Earnings',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/orders',
          name: 'WriterMyOrders',
          component: () => import('@/views/writers/MyOrders.vue'),
          meta: {
            requiresAuth: true,
            title: 'My Orders',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/calendar',
          name: 'WriterCalendar',
          component: () => import('@/views/writers/WriterCalendar.vue'),
          meta: {
            requiresAuth: true,
            title: 'Deadline Calendar',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/workload',
          name: 'WriterWorkload',
          component: () => import('@/views/writers/WriterWorkload.vue'),
          meta: {
            requiresAuth: true,
            title: 'Workload & Capacity',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/order-requests',
          name: 'WriterOrderRequests',
          component: () => import('@/views/writers/WriterOrderRequests.vue'),
          meta: {
            requiresAuth: true,
            title: 'Order Request Status',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/order-holds',
          name: 'WriterOrderHoldRequests',
          component: () => import('@/views/writers/OrderHoldRequests.vue'),
          meta: {
            requiresAuth: true,
            title: 'Order Hold Requests',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/communications',
          name: 'WriterCommunications',
          component: () => import('@/views/writers/WriterCommunications.vue'),
          meta: {
            requiresAuth: true,
            title: 'Client Communications',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/deadline-extensions',
          name: 'DeadlineExtensionRequests',
          component: () => import('@/views/writers/DeadlineExtensionRequests.vue'),
          meta: {
            requiresAuth: true,
            title: 'Deadline Extension Requests',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/dashboard-summary',
          name: 'DashboardSummary',
          component: () => import('@/views/writers/DashboardSummary.vue'),
          meta: {
            requiresAuth: true,
            title: 'Dashboard Summary',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/badge-analytics',
          name: 'BadgeAnalytics',
          component: () => import('@/views/writers/BadgeAnalytics.vue'),
          meta: {
            requiresAuth: true,
            title: 'Badge Analytics',
            roles: ['writer'],
          },
        },
        {
          path: 'writer/discipline-status',
          name: 'DisciplineStatus',
          component: () => import('@/views/writers/DisciplineStatus.vue'),
          meta: {
            requiresAuth: true,
            title: 'Discipline Status',
            roles: ['writer'],
          },
        },
        {
          path: 'editor/tasks',
          name: 'EditorTasks',
          component: () => import('@/views/editors/Tasks.vue'),
          meta: {
            requiresAuth: true,
            title: 'My Tasks',
            roles: ['editor'],
          },
        },
        {
          path: 'support/queue',
          name: 'SupportTicketQueue',
          component: () => import('@/views/support/TicketQueue.vue'),
          meta: {
            requiresAuth: true,
            title: 'Ticket Queue',
            roles: ['support', 'admin', 'superadmin'],
          },
        },
        {
          path: 'support/tickets',
          name: 'SupportTickets',
          component: () => import('@/views/support/Tickets.vue'),
          meta: {
            requiresAuth: true,
            title: 'Recent Tickets',
            roles: ['support', 'admin', 'superadmin'],
          },
        },
        {
          path: 'editor/available-tasks',
          name: 'EditorAvailableTasks',
          component: () => import('@/views/editors/AvailableTasks.vue'),
          meta: {
            requiresAuth: true,
            title: 'Available Tasks',
            roles: ['editor'],
          },
        },
        {
          path: 'editor/performance',
          name: 'EditorPerformance',
          component: () => import('@/views/editors/Performance.vue'),
          meta: {
            requiresAuth: true,
            title: 'Performance Analytics',
            roles: ['editor'],
          },
        },
        {
          path: 'admin/users',
          name: 'UserManagement',
          component: () => import('@/views/admin/UserManagement.vue'),
    meta: {
      requiresAuth: true,
            title: 'User Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/writer-discipline',
          name: 'WriterDisciplineManagement',
          component: () => import('@/views/admin/WriterDisciplineManagement.vue'),
    meta: {
      requiresAuth: true,
            title: 'Writer Discipline Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/appeals',
          name: 'AppealsManagement',
          component: () => import('@/views/admin/AppealsManagement.vue'),
    meta: {
      requiresAuth: true,
            title: 'Appeals Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/discipline-config',
          name: 'DisciplineConfig',
          component: () => import('@/views/admin/DisciplineConfig.vue'),
          meta: {
            requiresAuth: true,
            title: 'Discipline Configuration',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/duplicate-detection',
          name: 'DuplicateAccountDetection',
          component: () => import('@/views/admin/DuplicateAccountDetection.vue'),
    meta: {
      requiresAuth: true,
            title: 'Duplicate Account Detection',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/referral-tracking',
          name: 'ReferralTracking',
          component: () => import('@/views/admin/ReferralTracking.vue'),
    meta: {
      requiresAuth: true,
            title: 'Referral Tracking',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/loyalty-tracking',
          name: 'LoyaltyTracking',
          component: () => import('@/views/admin/LoyaltyTracking.vue'),
    meta: {
      requiresAuth: true,
            title: 'Loyalty Points Tracking',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/deletion-requests',
          name: 'DeletionRequests',
          component: () => import('@/views/admin/DeletionRequests.vue'),
    meta: {
      requiresAuth: true,
            title: 'Deletion Requests',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/configs',
          name: 'ConfigManagement',
          component: () => import('@/views/admin/ConfigManagement.vue'),
    meta: {
      requiresAuth: true,
            title: 'Configuration Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/notification-profiles',
    name: 'NotificationProfiles',
    component: () => import('@/views/admin/NotificationProfiles.vue'),
    meta: {
      requiresAuth: true,
            title: 'Notification Profiles',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/notification-groups',
          name: 'NotificationGroups',
          component: () => import('@/views/admin/NotificationGroups.vue'),
          meta: {
            requiresAuth: true,
            title: 'Notification Groups & Profiles',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/emails',
          name: 'EmailManagement',
          component: () => import('@/views/admin/EmailManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Email Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/blog',
          name: 'BlogManagement',
          component: () => import('@/views/admin/BlogManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Blog Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/seo-pages',
          name: 'SEOPagesManagement',
          component: () => import('@/views/admin/SEOPagesManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'SEO Pages Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/wallets',
          name: 'WalletManagement',
          component: () => import('@/views/admin/WalletManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Wallet Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/special-orders',
          name: 'SpecialOrderManagement',
          component: () => import('@/views/admin/SpecialOrderManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Special Orders Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/reviews',
          name: 'ReviewsManagement',
          component: () => import('@/views/admin/ReviewsManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Reviews Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/reviews/moderation',
          name: 'ReviewModeration',
          component: () => import('@/views/admin/ReviewModeration.vue'),
          meta: {
            requiresAuth: true,
            title: 'Review Moderation',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/orders',
          name: 'OrderManagement',
          component: () => import('@/views/admin/OrderManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Order Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/class-management',
          name: 'ClassManagement',
          component: () => import('@/views/admin/ClassManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Class Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/express-classes',
          name: 'ExpressClassesManagement',
          component: () => import('@/views/admin/ExpressClassesManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Express Classes Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/disputes',
          name: 'DisputeManagement',
          component: () => import('@/views/admin/DisputeManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Dispute Management',
            roles: ['admin', 'superadmin', 'support'],
          },
        },
        {
          path: 'admin/refunds',
          name: 'RefundManagement',
          component: () => import('@/views/admin/RefundManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Refund Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/disputes',
          name: 'DisputeManagement',
          component: () => import('@/views/admin/DisputeManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Dispute Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/tips',
          name: 'TipManagement',
          component: () => import('@/views/admin/TipManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Tip Management & Earnings',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/files',
          name: 'FileManagement',
          component: () => import('@/views/admin/FileManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'File Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/fines',
          name: 'FinesManagement',
          component: () => import('@/views/admin/FinesManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Fines Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/system-health',
          name: 'SystemHealth',
          component: () => import('@/views/admin/SystemHealth.vue'),
          meta: {
            requiresAuth: true,
            title: 'System Health',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/activity-logs',
          name: 'ActivityLogs',
          component: () => import('@/views/admin/ActivityLogs.vue'),
          meta: {
            requiresAuth: true,
            title: 'Activity Logs',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/support-tickets',
          name: 'SupportTicketsManagement',
          component: () => import('@/views/admin/SupportTicketsManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Support Tickets',
            roles: ['admin', 'superadmin', 'support'],
          },
        },
        {
          path: 'admin/discount-analytics',
          name: 'DiscountAnalytics',
          component: () => import('@/views/admin/DiscountAnalytics.vue'),
          meta: {
            requiresAuth: true,
            title: 'Discount Analytics',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/discounts',
          name: 'DiscountManagement',
          component: () => import('@/views/admin/DiscountManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Discount Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/campaigns',
          name: 'PromotionalCampaignManagement',
          component: () => import('@/views/admin/PromotionalCampaignManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Promotional Campaign Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/campaigns/:id/discounts',
          name: 'CampaignDiscounts',
          component: () => import('@/views/admin/CampaignDiscounts.vue'),
          meta: {
            requiresAuth: true,
            title: 'Campaign Discounts',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/campaigns/:id/analytics',
          name: 'CampaignPerformanceDashboard',
          component: () => import('@/views/admin/CampaignPerformanceDashboard.vue'),
          meta: {
            requiresAuth: true,
            title: 'Campaign Performance',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/payments/batched',
          name: 'BatchedWriterPayments',
          component: () => import('@/views/admin/BatchedWriterPayments.vue'),
          meta: {
            requiresAuth: true,
            title: 'Batched Writer Payments',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/payments/all',
          name: 'AllWriterPayments',
          component: () => import('@/views/admin/AllWriterPayments.vue'),
          meta: {
            requiresAuth: true,
            title: 'All Writer Payments',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/financial-overview',
          name: 'FinancialOverview',
          component: () => import('@/views/admin/FinancialOverview.vue'),
          meta: {
            requiresAuth: true,
            title: 'Financial Overview',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/writer-performance',
          name: 'WriterPerformanceAnalytics',
          component: () => import('@/views/admin/WriterPerformanceAnalytics.vue'),
          meta: {
            requiresAuth: true,
            title: 'Writer Performance',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/writer-hierarchy',
          name: 'WriterHierarchy',
          component: () => import('@/views/admin/WriterHierarchy.vue'),
          meta: {
            requiresAuth: true,
            title: 'Writer Hierarchy',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/loyalty-management',
          name: 'LoyaltyManagement',
          component: () => import('@/views/admin/LoyaltyManagement.vue'),
          meta: {
            requiresAuth: true,
            title: 'Loyalty Management',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/advanced-analytics',
          name: 'AdvancedAnalytics',
          component: () => import('@/views/admin/AdvancedAnalytics.vue'),
          meta: {
            requiresAuth: true,
            title: 'Advanced Analytics',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/superadmin',
          name: 'SuperadminDashboard',
          component: () => import('@/views/admin/SuperadminDashboard.vue'),
          meta: {
            requiresAuth: true,
            title: 'Superadmin Dashboard',
            roles: ['superadmin'],
          },
        },
        {
          path: 'admin/review-aggregation',
          name: 'ReviewAggregation',
          component: () => import('@/views/admin/ReviewAggregation.vue'),
          meta: {
            requiresAuth: true,
            title: 'Review Aggregation & Display',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/pricing-analytics',
          name: 'PricingAnalytics',
          component: () => import('@/views/admin/PricingAnalytics.vue'),
          meta: {
            requiresAuth: true,
            title: 'Pricing Analytics',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'admin/enhanced-analytics',
          name: 'EnhancedAnalytics',
          component: () => import('@/views/admin/EnhancedAnalytics.vue'),
          meta: {
            requiresAuth: true,
            title: 'Enhanced Analytics',
            roles: ['admin', 'superadmin'],
          },
        },
        {
          path: 'websites',
          name: 'WebsiteManagement',
          component: () => import('@/views/admin/WebsiteManagement.vue'),
    meta: {
      requiresAuth: true,
            title: 'Website Management',
            roles: ['admin', 'superadmin'],
          },
        },
        // Profile & Account
        {
          path: 'profile',
          name: 'Profile',
          redirect: { name: 'AccountSettings' },
        },
        {
          path: 'account/password-change',
          name: 'PasswordChange',
          component: () => import('@/views/auth/PasswordChange.vue'),
          meta: { 
            requiresAuth: true, 
            title: 'Change Password',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'account/settings',
          name: 'AccountSettings',
          component: () => import('@/views/account/Settings.vue'),
    meta: {
      requiresAuth: true,
            title: 'Account Settings',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'account/privacy',
          name: 'PrivacySettings',
          component: () => import('@/views/account/PrivacySettings.vue'),
          meta: {
            requiresAuth: true,
            title: 'Privacy & Security',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
        {
          path: 'account/security',
          name: 'SecurityActivity',
          component: () => import('@/views/account/SecurityActivity.vue'),
          meta: {
            requiresAuth: true,
            title: 'Security Activity',
            roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
          },
        },
      ],
    },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
      component: () => import('@/views/errors/NotFound.vue'),
      meta: { title: '404 - Not Found' },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Set page title
  const appName = import.meta.env.VITE_APP_NAME || 'Writing System'
  document.title = to.meta.title 
    ? `${to.meta.title} - ${appName}`
    : appName

  // Check authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

  // Redirect authenticated users away from login/signup
  if ((to.name === 'Login' || to.name === 'Signup') && authStore.isAuthenticated) {
      next({ name: 'Dashboard' })
      return
    }

  // Check role-based access
  if (to.meta.requiresAuth && to.meta.roles) {
    const userRole = authStore.userRole
    if (!hasRole(userRole, to.meta.roles)) {
      next({ name: 'Dashboard' }) // Redirect to dashboard if no access
      return
    }
  }

  // Refresh user data if needed
  if (to.meta.requiresAuth && !authStore.user && authStore.isAuthenticated) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('Failed to fetch user:', error)
      next({ name: 'Login' })
      return
    }
  }

  next()
})

export default router

