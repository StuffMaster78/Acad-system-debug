<template>
  <div class="writer-guide">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
      ✍️ Writer Guide
    </h2>

    <!-- Getting Started -->
    <section class="mb-8">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">🚀 Getting Started</h3>
      <div class="space-y-4 text-gray-700 dark:text-gray-300">
        <p>
          Welcome to the writer dashboard! This guide will help you navigate the system and understand how to work with orders effectively.
        </p>
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p class="font-semibold text-blue-900 dark:text-blue-200 mb-2">Important:</p>
          <p class="text-sm text-blue-800 dark:text-blue-300">
            You can only see and work with <strong>paid orders</strong>. Unpaid orders are hidden from your view to ensure you only work on orders that are guaranteed to be compensated.
          </p>
        </div>
      </div>
    </section>

    <!-- Order Categories -->
    <section class="mb-8">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">📊 Order Categories</h3>
      <div class="space-y-4">
        <div
          v-for="category in orderCategories"
          :key="category.id"
          class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
        >
          <div class="flex items-center gap-3 mb-2">
            <span class="text-2xl">{{ category.icon }}</span>
            <h4 class="font-semibold text-gray-900 dark:text-white">{{ category.label }}</h4>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">{{ category.description }}</p>
          <div v-if="category.notes" class="mt-2 text-xs text-gray-500 dark:text-gray-400 italic">
            {{ category.notes }}
          </div>
        </div>
      </div>
    </section>

    <!-- Workflow -->
    <section class="mb-8">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">🔄 Order Workflow</h3>
      <div class="space-y-3">
        <div
          v-for="(step, index) in workflowSteps"
          :key="index"
          class="flex gap-4"
        >
          <div class="flex-shrink-0">
            <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">
              {{ index + 1 }}
            </div>
          </div>
          <div class="flex-1">
            <h4 class="font-semibold text-gray-900 dark:text-white mb-1">{{ step.title }}</h4>
            <p class="text-sm text-gray-600 dark:text-gray-300">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Operations -->
    <section class="mb-8">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">⚙️ Available Operations</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="operation in operations"
          :key="operation.id"
          class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
        >
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xl">{{ operation.icon }}</span>
            <h4 class="font-semibold text-gray-900 dark:text-white">{{ operation.title }}</h4>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">{{ operation.description }}</p>
          <div v-if="operation.when" class="text-xs text-gray-500 dark:text-gray-400">
            <strong>When:</strong> {{ operation.when }}
          </div>
        </div>
      </div>
    </section>

    <!-- Tips -->
    <section class="mb-8">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">💡 Tips & Best Practices</h3>
      <ul class="space-y-2 text-gray-700 dark:text-gray-300">
        <li v-for="(tip, index) in tips" :key="index" class="flex gap-2">
          <span class="text-blue-600 dark:text-blue-400">•</span>
          <span>{{ tip }}</span>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
const orderCategories = [
  {
    id: 'available',
    label: 'Available Orders',
    icon: '✅',
    description: 'Paid orders that you can request or take. These are orders in the common pool that haven\'t been assigned yet.',
    notes: 'Once you request an order and it\'s assigned to another writer, your request will be removed automatically.'
  },
  {
    id: 'assigned',
    label: 'Assigned Orders',
    icon: '👤',
    description: 'Orders that have been assigned to you. You can accept or reject these assignments.',
    notes: 'If you\'re a preferred writer, you\'ll see these orders here. You can still reject if you\'re not available.'
  },
  {
    id: 'order_requests',
    label: 'Order Requests',
    icon: '📝',
    description: 'Orders you have requested. Track the status of your requests here.',
    notes: 'When a request is approved, the order moves to "In Progress". If another writer gets assigned, your request is removed.'
  },
  {
    id: 'in_progress',
    label: 'In Progress',
    icon: '🔄',
    description: 'Orders you are actively working on. These include orders you\'ve accepted and started working on.',
    notes: 'Prioritize orders with approaching deadlines. Use the deadline calendar to manage your workload.'
  },
  {
    id: 'revision_requests',
    label: 'Revision Requests',
    icon: '🔁',
    description: 'Orders requiring revision. These are prioritized in your active orders list.',
    notes: 'Revisions are shown first in the Active tab. Address these promptly to maintain quality ratings.'
  },
  {
    id: 'completed',
    label: 'Completed',
    icon: '✅',
    description: 'Orders you have submitted. Waiting for client approval and rating.',
    notes: 'Completed orders may still require revisions if the client requests changes.'
  },
  {
    id: 'disputed',
    label: 'Disputed Orders',
    icon: '⚠️',
    description: 'Orders with disputes that need resolution. Work with support to resolve these.',
    notes: 'Contact support immediately if you have questions about a disputed order.'
  },
  {
    id: 'on_hold',
    label: 'Orders On Hold',
    icon: '⏸️',
    description: 'Orders that are temporarily paused. You can request a hold or admin may set one.',
    notes: 'Use hold requests when you need temporary relief from an order due to emergencies.'
  },
  {
    id: 'cancelled',
    label: 'Cancelled Orders',
    icon: '❌',
    description: 'Orders that have been cancelled by the client or admin.',
    notes: 'Cancelled orders are for reference only. No further action is required.'
  },
  {
    id: 'closed',
    label: 'Closed Orders',
    icon: '🔒',
    description: 'Orders whose deadlines have passed but haven\'t been rated yet. Candidates for archiving.',
    notes: 'These orders are in a final state and may be archived soon.'
  },
  {
    id: 'archived',
    label: 'Archived Orders',
    icon: '📦',
    description: 'Orders that have been archived. View-only access - you cannot download files, send messages, or copy content.',
    notes: 'Archived orders are locked. You can view them for reference but cannot interact with them.'
  }
]

const workflowSteps = [
  {
    title: 'Browse Available Orders',
    description: 'View paid orders in the "Available" tab. You can see order details, requirements, and deadlines before requesting.'
  },
  {
    title: 'Request or Take Order',
    description: 'Request an order to express interest, or take it directly if takes are enabled. Only paid orders are visible.'
  },
  {
    title: 'Accept Assignment',
    description: 'If assigned as a preferred writer, accept or reject the assignment. Once accepted, the order moves to "In Progress".'
  },
  {
    title: 'Work on Order',
    description: 'Access order details, requirements, and files. Use the deadline calendar to manage your schedule.'
  },
  {
    title: 'Submit Work',
    description: 'Upload your completed work. The order status changes to "Submitted" and awaits client review.'
  },
  {
    title: 'Handle Revisions',
    description: 'If revisions are requested, address them promptly. Revisions are prioritized in your active orders.'
  },
  {
    title: 'Get Rated',
    description: 'Once approved, clients rate your work. Maintain high ratings to access better orders and improve your level.'
  }
]

const operations = [
  {
    id: 'request_order',
    title: 'Request Order',
    icon: '📝',
    description: 'Express interest in an available order. Admins review and approve requests.',
    when: 'Available orders tab'
  },
  {
    id: 'take_order',
    title: 'Take Order',
    icon: '⚡',
    description: 'Immediately take an available order if takes are enabled for your level.',
    when: 'Available orders tab (if enabled)'
  },
  {
    id: 'accept_reject',
    title: 'Accept/Reject Assignment',
    icon: '✅',
    description: 'Accept or reject orders assigned to you as a preferred writer.',
    when: 'Assigned orders tab'
  },
  {
    id: 'submit_work',
    title: 'Submit Work',
    icon: '📤',
    description: 'Upload completed work for client review. Ensure all requirements are met.',
    when: 'In Progress orders'
  },
  {
    id: 'request_extension',
    title: 'Request Deadline Extension',
    icon: '⏰',
    description: 'Request more time if you need it. Submit before the deadline when possible.',
    when: 'In Progress orders'
  },
  {
    id: 'request_hold',
    title: 'Request Hold',
    icon: '⏸️',
    description: 'Temporarily pause an order due to emergencies or personal reasons.',
    when: 'In Progress orders'
  },
  {
    id: 'start_revision',
    title: 'Start Revision',
    icon: '🔧',
    description: 'Begin working on requested revisions. Review feedback carefully.',
    when: 'Revision Requests tab'
  },
  {
    id: 'communicate',
    title: 'Communicate',
    icon: '💬',
    description: 'Message clients, admins, or support through the messaging system.',
    when: 'Any order (if messaging not locked)'
  }
]

const tips = [
  'Always check order requirements and deadlines before requesting.',
  'Prioritize revisions as they affect your quality ratings.',
  'Use the deadline calendar to manage your workload effectively.',
  'Request extensions early rather than missing deadlines.',
  'Communicate proactively with clients about progress or issues.',
  'Maintain high ratings to access better orders and advance your level.',
  'Only paid orders are visible - you\'ll never see unpaid orders.',
  'Archived orders are view-only - download files before orders are archived.',
  'Track your performance metrics to understand your progress.',
  'Use the order queue to find orders that match your expertise.'
]
</script>

