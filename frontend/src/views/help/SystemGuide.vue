<template>
  <div class="system-guide-page min-h-dvh bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto page-shell">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="page-title text-gray-900 dark:text-white mb-2">System Guide</h1>
        <p class="text-lg text-gray-600 dark:text-gray-400">
          Comprehensive documentation for all user roles
        </p>
      </div>

      <!-- Role Tabs -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="flex overflow-x-auto" aria-label="Tabs">
            <button
              v-for="role in availableRoles"
              :key="role.id"
              @click="activeRole = role.id"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
                activeRole === role.id
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              ]"
            >
              <span class="flex items-center gap-2">
                <span class="text-xl">{{ role.icon }}</span>
                {{ role.label }}
              </span>
            </button>
          </nav>
        </div>
      </div>

      <!-- Content -->
      <div class="space-y-6">
        <!-- Order States Section -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            📋 Order States Explained
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="state in orderStates"
              :key="state.status"
              class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-center gap-3 mb-2">
                <span class="text-2xl">{{ state.icon }}</span>
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ state.label }}</h3>
                  <code class="text-xs text-gray-500 dark:text-gray-400">{{ state.status }}</code>
                </div>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">{{ state.description }}</p>
              <div v-if="state.actions && state.actions.length > 0" class="mt-3">
                <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Available Actions:</p>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="action in state.actions"
                    :key="action"
                    class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded"
                  >
                    {{ action }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Communications Guidance -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            💬 Communication Guidelines
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-300">
            Use platform messages as the primary channel for all coordination and updates.
            Email should be secondary only, since inboxes can be easy to miss and harder to track.
          </p>
        </div>

        <!-- Role-Specific Guide -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <component :is="activeGuideComponent" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import WriterGuide from '@/views/help/guides/WriterGuide.vue'
import ClientGuide from '@/views/help/guides/ClientGuide.vue'
import EditorGuide from '@/views/help/guides/EditorGuide.vue'
import SupportGuide from '@/views/help/guides/SupportGuide.vue'
import AdminGuide from '@/views/help/guides/AdminGuide.vue'

const authStore = useAuthStore()
const activeRole = ref(authStore.user?.role || 'writer')

// Order states with descriptions
const orderStates = [
  {
    status: 'draft',
    label: 'Draft',
    icon: '📝',
    description: 'Order is being created but not yet submitted.',
    actions: []
  },
  {
    status: 'pending',
    label: 'Pending',
    icon: '⏳',
    description: 'Order is submitted and awaiting payment or admin review.',
    actions: []
  },
  {
    status: 'unpaid',
    label: 'Unpaid',
    icon: '💳',
    description: 'Order requires payment before it can be processed.',
    actions: []
  },
  {
    status: 'available',
    label: 'Available',
    icon: '✅',
    description: 'Paid order available for writers to request or take. Writers can see and request these orders.',
    actions: ['Request Order', 'Take Order']
  },
  {
    status: 'assigned',
    label: 'Assigned',
    icon: '👤',
    description: 'Order has been assigned to a writer. Writer can accept or reject.',
    actions: ['Accept', 'Reject']
  },
  {
    status: 'pending_writer_assignment',
    label: 'Pending Writer Assignment',
    icon: '⏱️',
    description: 'Order is waiting for writer to accept the assignment.',
    actions: ['Accept', 'Reject']
  },
  {
    status: 'in_progress',
    label: 'In Progress',
    icon: '🔄',
    description: 'Writer is actively working on the order.',
    actions: ['Submit', 'Request Extension', 'Request Hold']
  },
  {
    status: 'under_editing',
    label: 'Under Editing',
    icon: '✏️',
    description: 'Order is being edited by an editor.',
    actions: []
  },
  {
    status: 'submitted',
    label: 'Submitted',
    icon: '📤',
    description: 'Writer has submitted the completed work for review.',
    actions: ['Approve', 'Request Revision']
  },
  {
    status: 'revision_requested',
    label: 'Revision Requested',
    icon: '🔁',
    description: 'Client or admin has requested changes to the submitted work.',
    actions: ['Start Revision', 'View Feedback']
  },
  {
    status: 'on_revision',
    label: 'On Revision',
    icon: '🔧',
    description: 'Writer is working on requested revisions.',
    actions: ['Submit Revision']
  },
  {
    status: 'completed',
    label: 'Completed',
    icon: '✅',
    description: 'Order work is completed and submitted by the writer.',
    actions: ['Approve', 'Rate']
  },
  {
    status: 'approved',
    label: 'Approved',
    icon: '👍',
    description: 'Client has approved the completed work.',
    actions: ['Rate', 'Review']
  },
  {
    status: 'rated',
    label: 'Rated',
    icon: '⭐',
    description: 'Client has rated the completed work.',
    actions: []
  },
  {
    status: 'reviewed',
    label: 'Reviewed',
    icon: '💬',
    description: 'Client has provided a review for the completed work.',
    actions: []
  },
  {
    status: 'closed',
    label: 'Closed',
    icon: '🔒',
    description: 'Order is closed. Deadline passed but not yet rated. Candidate for archiving.',
    actions: []
  },
  {
    status: 'on_hold',
    label: 'On Hold',
    icon: '⏸️',
    description: 'Order is temporarily paused. Can be requested by writer or set by admin.',
    actions: ['Resume']
  },
  {
    status: 'disputed',
    label: 'Disputed',
    icon: '⚠️',
    description: 'Order has a dispute that needs resolution.',
    actions: ['Resolve Dispute']
  },
  {
    status: 'cancelled',
    label: 'Cancelled',
    icon: '❌',
    description: 'Order has been cancelled by client or admin.',
    actions: []
  },
  {
    status: 'archived',
    label: 'Archived',
    icon: '📦',
    description: 'Order is archived. View-only access, no actions allowed.',
    actions: []
  }
]

// Available roles based on user
const availableRoles = computed(() => {
  const userRole = authStore.user?.role
  const allRoles = [
    { id: 'writer', label: 'Writer Guide', icon: '✍️' },
    { id: 'client', label: 'Client Guide', icon: '👤' },
    { id: 'editor', label: 'Editor Guide', icon: '✏️' },
    { id: 'support', label: 'Support Guide', icon: '🛟' },
    { id: 'admin', label: 'Admin Guide', icon: '👨‍💼' }
  ]
  
  // Show all roles if admin/superadmin, otherwise show user's role
  if (userRole === 'admin' || userRole === 'superadmin') {
    return allRoles
  }
  return allRoles.filter(r => r.id === userRole)
})

// Active guide component
const activeGuideComponent = computed(() => {
  const components = {
    writer: WriterGuide,
    client: ClientGuide,
    editor: EditorGuide,
    support: SupportGuide,
    admin: AdminGuide
  }
  return components[activeRole.value] || WriterGuide
})
</script>

<style scoped>
.system-guide-page {
  min-height: calc(100vh - 4rem);
}
</style>

