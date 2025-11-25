<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="badgeClass"
  >
    <span v-if="icon" class="mr-1">{{ icon }}</span>
    {{ label || status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default' // default, success, warning, error, info
  }
})

const statusColors = {
  // Order statuses
  'pending': 'bg-yellow-100 text-yellow-800',
  'draft': 'bg-gray-100 text-gray-800',
  'assigned': 'bg-blue-100 text-blue-800',
  'in_progress': 'bg-indigo-100 text-indigo-800',
  'submitted': 'bg-purple-100 text-purple-800',
  'completed': 'bg-green-100 text-green-800',
  'cancelled': 'bg-red-100 text-red-800',
  'on_hold': 'bg-orange-100 text-orange-800',
  'archived': 'bg-gray-100 text-gray-800',
  
  // Payment statuses
  'paid': 'bg-green-100 text-green-800',
  'unpaid': 'bg-yellow-100 text-yellow-800',
  'pending_payment': 'bg-yellow-100 text-yellow-800',
  'failed': 'bg-red-100 text-red-800',
  'refunded': 'bg-gray-100 text-gray-800',
  
  // Ticket statuses
  'open': 'bg-blue-100 text-blue-800',
  'closed': 'bg-gray-100 text-gray-800',
  'resolved': 'bg-green-100 text-green-800',
  'escalated': 'bg-red-100 text-red-800',
  
  // User statuses
  'active': 'bg-green-100 text-green-800',
  'inactive': 'bg-gray-100 text-gray-800',
  'suspended': 'bg-red-100 text-red-800',
  'frozen': 'bg-blue-100 text-blue-800',
  
  // General
  'success': 'bg-green-100 text-green-800',
  'error': 'bg-red-100 text-red-800',
  'warning': 'bg-yellow-100 text-yellow-800',
  'info': 'bg-blue-100 text-blue-800',
}

const variantColors = {
  default: 'bg-gray-100 text-gray-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
}

const badgeClass = computed(() => {
  if (props.variant !== 'default') {
    return variantColors[props.variant] || variantColors.default
  }
  
  const normalizedStatus = props.status.toLowerCase().replace(/\s+/g, '_')
  return statusColors[normalizedStatus] || variantColors.default
})
</script>

