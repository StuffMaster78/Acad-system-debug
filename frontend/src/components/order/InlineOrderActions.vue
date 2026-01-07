<template>
  <div class="space-y-4">
    <!-- Action Cards - Expandable Sections -->
    <div
      v-for="actionGroup in actionGroups"
      :key="actionGroup.id"
      class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
    >
      <!-- Action Header (Clickable to expand) -->
      <button
        @click="toggleAction(actionGroup.id)"
        class="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center text-xl" :class="actionGroup.iconBg">
            {{ actionGroup.icon }}
          </div>
          <div class="text-left">
            <h3 class="font-semibold text-gray-900 dark:text-white">{{ actionGroup.title }}</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ actionGroup.description }}</p>
          </div>
        </div>
        <svg
          class="w-5 h-5 text-gray-400 transition-transform"
          :class="{ 'rotate-180': expandedActions[actionGroup.id] }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Expanded Content -->
      <Transition name="expand">
        <div v-if="expandedActions[actionGroup.id]" class="border-t border-gray-200 dark:border-gray-700">
          <div class="p-6">
            <!-- Assign/Reassign Writer Section -->
            <div v-if="actionGroup.id === 'assign-writer'">
              <AssignWriterInline
                :order="order"
                :is-reassign="order?.assigned_writer !== null"
                @success="handleActionSuccess"
                @error="handleActionError"
              />
            </div>

            <!-- Edit Order Section -->
            <div v-else-if="actionGroup.id === 'edit-order'">
              <EditOrderInline
                :order="order"
                @success="handleActionSuccess"
                @error="handleActionError"
              />
            </div>

            <!-- Status Actions Section -->
            <div v-else-if="actionGroup.id === 'status-actions'">
              <StatusActionsInline
                :order="order"
                :available-actions="availableActions"
                @success="handleActionSuccess"
                @error="handleActionError"
              />
            </div>

            <!-- Financial Actions Section -->
            <div v-else-if="actionGroup.id === 'financial-actions'">
              <FinancialActionsInline
                :order="order"
                @success="handleActionSuccess"
                @error="handleActionError"
              />
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AssignWriterInline from './actions/AssignWriterInline.vue'
import EditOrderInline from './actions/EditOrderInline.vue'
import StatusActionsInline from './actions/StatusActionsInline.vue'
import FinancialActionsInline from './actions/FinancialActionsInline.vue'

const props = defineProps({
  order: {
    type: Object,
    required: true
  },
  availableActions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['success', 'error'])

const expandedActions = ref({})

const actionGroups = computed(() => {
  const groups = []

  // Check if assign/reassign actions are available
  const hasAssignAction = props.availableActions?.some(
    action => action.action === 'assign_order' && action.available && action.can_transition
  )
  const hasReassignAction = props.availableActions?.some(
    action => action.action === 'reassign_order' && action.available && action.can_transition
  )

  // Assign/Reassign Writer - only show if action is available
  if (props.order && (hasAssignAction || hasReassignAction)) {
    const canReassign = props.order.assigned_writer && hasReassignAction
    const canAssign = !props.order.assigned_writer && hasAssignAction
    
    if (canReassign || canAssign) {
      groups.push({
        id: 'assign-writer',
        title: canReassign ? 'Reassign Writer' : 'Assign Writer',
        description: canReassign 
          ? 'Change the writer assigned to this order'
          : 'Assign a writer to work on this order',
        icon: '👤',
        iconBg: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
      })
    }
  }

  // Edit Order - only show if edit_order or update_order action is available
  const hasEditAction = props.availableActions?.some(
    action => (action.action === 'edit_order' || action.action === 'update_order') 
      && action.available && action.can_transition
  )
  
  if (hasEditAction) {
    groups.push({
      id: 'edit-order',
      title: 'Edit Order Details',
      description: 'Modify order information, deadlines, and instructions',
      icon: '✏️',
      iconBg: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
    })
  }

  // Status Actions - filter to only show available and valid actions
  const validStatusActions = props.availableActions?.filter(
    action => action.available && action.can_transition 
      && !['assign_order', 'reassign_order', 'edit_order', 'update_order'].includes(action.action)
  ) || []
  
  if (validStatusActions.length > 0) {
    groups.push({
      id: 'status-actions',
      title: 'Status & Workflow Actions',
      description: 'Change order status and manage workflow',
      icon: '⚡',
      iconBg: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
    })
  }

  // Financial Actions
  if (props.order) {
    groups.push({
      id: 'financial-actions',
      title: 'Financial Actions',
      description: 'Manage payment status and financial operations',
      icon: '💰',
      iconBg: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
    })
  }

  return groups
})

const toggleAction = (actionId) => {
  expandedActions.value[actionId] = !expandedActions.value[actionId]
}

const handleActionSuccess = (data) => {
  emit('success', data)
  // Optionally close the expanded section
  Object.keys(expandedActions.value).forEach(key => {
    expandedActions.value[key] = false
  })
}

const handleActionError = (error) => {
  emit('error', error)
}
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 2000px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>

