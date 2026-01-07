<template>
  <div class="relative inline-block max-w-full">
    <div
      @mouseenter="showTooltip = true"
      @mouseleave="showTooltip = false"
      class="cursor-help"
    >
      <slot>
        <span class="inline-flex items-center gap-1">
          {{ statusLabel }}
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
      </slot>
    </div>
    
    <Transition name="tooltip">
      <div
        v-if="showTooltip"
        class="absolute z-50 max-w-xs sm:max-w-sm md:max-w-md p-3 bg-gray-900 text-white text-sm rounded-lg shadow-xl pointer-events-none break-words"
        :class="tooltipPosition"
      >
        <div class="flex items-start gap-2 mb-2">
          <span class="text-lg">{{ statusInfo.icon }}</span>
          <div>
            <h4 class="font-semibold">{{ statusInfo.label }}</h4>
            <code class="text-xs text-gray-400">{{ status }}</code>
          </div>
        </div>
        <p class="text-gray-300 mb-2 leading-snug">
          {{ statusInfo.description }}
        </p>
        <div v-if="statusInfo.actions && statusInfo.actions.length > 0" class="mt-2 pt-2 border-t border-gray-700">
          <p class="text-xs font-semibold text-gray-400 mb-1">Available Actions:</p>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="action in statusInfo.actions"
              :key="action"
              class="px-2 py-0.5 bg-blue-600 text-white text-xs rounded"
            >
              {{ action }}
            </span>
          </div>
        </div>
        <div class="absolute w-2 h-2 bg-gray-900 transform rotate-45" :class="arrowPosition"></div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  position: {
    type: String,
    default: 'bottom', // 'top', 'bottom', 'left', 'right'
    validator: (value) => ['top', 'bottom', 'left', 'right'].includes(value)
  }
})

const showTooltip = ref(false)

const statusInfoMap = {
  draft: {
    label: 'Draft',
    icon: '📝',
    description: 'Order is being created but not yet submitted.',
    actions: []
  },
  pending: {
    label: 'Pending',
    icon: '⏳',
    description: 'Order is submitted and awaiting payment or admin review.',
    actions: []
  },
  unpaid: {
    label: 'Unpaid',
    icon: '💳',
    description: 'Order requires payment before it can be processed.',
    actions: []
  },
  available: {
    label: 'Available',
    icon: '✅',
    description: 'Paid order available for writers to request or take.',
    actions: ['Request Order', 'Take Order']
  },
  assigned: {
    label: 'Assigned',
    icon: '👤',
    description: 'Order has been assigned to a writer. Writer can accept or reject.',
    actions: ['Accept', 'Reject']
  },
  pending_writer_assignment: {
    label: 'Pending Writer Assignment',
    icon: '⏱️',
    description: 'Order is waiting for writer to accept the assignment.',
    actions: ['Accept', 'Reject']
  },
  in_progress: {
    label: 'In Progress',
    icon: '🔄',
    description: 'Writer is actively working on the order.',
    actions: ['Submit', 'Request Extension', 'Request Hold']
  },
  under_editing: {
    label: 'Under Editing',
    icon: '✏️',
    description: 'Order is being edited by an editor.',
    actions: []
  },
  submitted: {
    label: 'Submitted',
    icon: '📤',
    description: 'Writer has submitted the completed work for review.',
    actions: ['Approve', 'Request Revision']
  },
  revision_requested: {
    label: 'Revision Requested',
    icon: '🔁',
    description: 'Client or admin has requested changes to the submitted work.',
    actions: ['Start Revision', 'View Feedback']
  },
  on_revision: {
    label: 'On Revision',
    icon: '🔧',
    description: 'Writer is working on requested revisions.',
    actions: ['Submit Revision']
  },
  completed: {
    label: 'Completed',
    icon: '✅',
    description: 'Order work is completed and submitted by the writer.',
    actions: ['Approve', 'Rate']
  },
  approved: {
    label: 'Approved',
    icon: '👍',
    description: 'Client has approved the completed work.',
    actions: ['Rate', 'Review']
  },
  rated: {
    label: 'Rated',
    icon: '⭐',
    description: 'Client has rated the completed work.',
    actions: []
  },
  reviewed: {
    label: 'Reviewed',
    icon: '💬',
    description: 'Client has provided a review for the completed work.',
    actions: []
  },
  closed: {
    label: 'Closed',
    icon: '🔒',
    description: 'Order is closed. Deadline passed but not yet rated. Candidate for archiving.',
    actions: []
  },
  on_hold: {
    label: 'On Hold',
    icon: '⏸️',
    description: 'Order is temporarily paused. Can be requested by writer or set by admin.',
    actions: ['Resume']
  },
  disputed: {
    label: 'Disputed',
    icon: '⚠️',
    description: 'Order has a dispute that needs resolution.',
    actions: ['Resolve Dispute']
  },
  cancelled: {
    label: 'Cancelled',
    icon: '❌',
    description: 'Order has been cancelled by client or admin.',
    actions: []
  },
  archived: {
    label: 'Archived',
    icon: '📦',
    description: 'Order is archived. View-only access, no actions allowed.',
    actions: []
  }
}

const statusInfo = computed(() => {
  return statusInfoMap[props.status] || {
    label: props.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    icon: '📋',
    description: 'Order status information.',
    actions: []
  }
})

const statusLabel = computed(() => {
  return statusInfo.value.label
})

const tooltipPosition = computed(() => {
  const positions = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  }
  return positions[props.position] || positions.bottom
})

const arrowPosition = computed(() => {
  const positions = {
    top: 'bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2',
    bottom: 'top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2',
    left: 'right-0 top-1/2 transform -translate-y-1/2 translate-x-1/2',
    right: 'left-0 top-1/2 transform -translate-y-1/2 -translate-x-1/2'
  }
  return positions[props.position] || positions.bottom
})
</script>

<style scoped>
.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>

