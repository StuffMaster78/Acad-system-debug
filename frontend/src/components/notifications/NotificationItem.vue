<template>
  <div
    :class="[
      'group relative p-4 rounded-lg border transition-all duration-200 cursor-pointer',
      'hover:shadow-md hover:border-primary-300',
      notification.is_read 
        ? 'bg-white border-gray-200' 
        : 'bg-gradient-to-r from-blue-50 to-white border-blue-200 shadow-sm',
      notification.is_critical && !notification.is_read
        ? 'ring-2 ring-red-200 bg-red-50'
        : ''
    ]"
    @click="handleClick"
  >
    <!-- Unread Indicator -->
    <div 
      v-if="!notification.is_read" 
      class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-blue-400 rounded-l-lg"
    ></div>
    
    <div class="flex items-start gap-3">
      <!-- Icon -->
      <div 
        :class="[
          'shrink-0 w-10 h-10 rounded-lg flex items-center justify-center',
          getIconBgClass(notification.category, notification.event)
        ]"
      >
        <component 
          :is="getIcon(notification.category, notification.event)" 
          :class="[
            'w-5 h-5',
            getIconColorClass(notification.category, notification.event)
          ]"
        />
      </div>
      
      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-2 mb-1">
          <div class="flex-1 min-w-0">
            <h4 
              :class="[
                'text-sm font-semibold line-clamp-1',
                notification.is_read ? 'text-gray-700' : 'text-gray-900'
              ]"
            >
              {{ notification.title || notification.rendered_title || 'Notification' }}
            </h4>
            <p 
              :class="[
                'text-xs mt-1 line-clamp-2',
                notification.is_read ? 'text-gray-500' : 'text-gray-600'
              ]"
            >
              {{ notification.message || notification.rendered_message || notification.description }}
            </p>
          </div>
          
          <!-- Priority Badge -->
          <div v-if="notification.priority_label || notification.is_critical" class="shrink-0">
            <span 
              :class="[
                'px-2 py-0.5 rounded-full text-xs font-medium',
                notification.is_critical 
                  ? 'bg-red-100 text-red-700' 
                  : getPriorityBadgeClass(notification.priority_label)
              ]"
            >
              {{ notification.is_critical ? 'Urgent' : (notification.priority_label || 'Normal') }}
            </span>
          </div>
        </div>
        
        <!-- Meta Info -->
        <div class="flex items-center gap-3 mt-2 text-xs text-gray-400">
          <span class="flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ formatTime(notification.created_at || notification.sent_at) }}
          </span>
          
          <span 
            v-if="notification.category"
            :class="[
              'px-2 py-0.5 rounded text-xs font-medium',
              getCategoryBadgeClass(notification.category)
            ]"
          >
            {{ formatCategory(notification.category) }}
          </span>
          
          <span 
            v-if="notification.actor && showActor"
            class="flex items-center gap-1 text-gray-500"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            {{ getActorName(notification.actor) }}
          </span>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          v-if="!notification.is_read"
          @click.stop="markAsRead"
          class="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
          title="Mark as read"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </button>
        <a
          v-if="notification.link || notification.rendered_link"
          :href="notification.link || notification.rendered_link"
          @click.stop
          class="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
          title="View details"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import notificationsAPI from '@/api/notifications'

const props = defineProps({
  notification: {
    type: Object,
    required: true
  },
  showActor: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['read', 'click'])

const getIcon = (category, event) => {
  // Order-related
  if (event?.includes('order') || category === 'order') {
    return 'OrderIcon'
  }
  // Payment-related
  if (event?.includes('payment') || category === 'payment') {
    return 'PaymentIcon'
  }
  // Message-related
  if (event?.includes('message') || event?.includes('communication')) {
    return 'MessageIcon'
  }
  // File-related
  if (event?.includes('file') || event?.includes('upload')) {
    return 'FileIcon'
  }
  // System
  if (category === 'system') {
    return 'SystemIcon'
  }
  // Default
  return 'BellIcon'
}

const getIconBgClass = (category, event) => {
  if (category === 'order' || event?.includes('order')) {
    return 'bg-blue-100'
  }
  if (category === 'payment' || event?.includes('payment')) {
    return 'bg-green-100'
  }
  if (event?.includes('message') || event?.includes('communication')) {
    return 'bg-purple-100'
  }
  if (event?.includes('file') || event?.includes('upload')) {
    return 'bg-orange-100'
  }
  if (category === 'system') {
    return 'bg-gray-100'
  }
  return 'bg-primary-100'
}

const getIconColorClass = (category, event) => {
  if (category === 'order' || event?.includes('order')) {
    return 'text-blue-600'
  }
  if (category === 'payment' || event?.includes('payment')) {
    return 'text-green-600'
  }
  if (event?.includes('message') || event?.includes('communication')) {
    return 'text-purple-600'
  }
  if (event?.includes('file') || event?.includes('upload')) {
    return 'text-orange-600'
  }
  if (category === 'system') {
    return 'text-gray-600'
  }
  return 'text-primary-600'
}

const getCategoryBadgeClass = (category) => {
  const classes = {
    order: 'bg-blue-100 text-blue-700',
    payment: 'bg-green-100 text-green-700',
    ticket: 'bg-yellow-100 text-yellow-700',
    system: 'bg-gray-100 text-gray-700',
    message: 'bg-purple-100 text-purple-700',
    file: 'bg-orange-100 text-orange-700'
  }
  return classes[category] || 'bg-gray-100 text-gray-700'
}

const getPriorityBadgeClass = (priority) => {
  const classes = {
    high: 'bg-orange-100 text-orange-700',
    medium: 'bg-yellow-100 text-yellow-700',
    low: 'bg-gray-100 text-gray-500',
    critical: 'bg-red-100 text-red-700'
  }
  return classes[priority?.toLowerCase()] || 'bg-gray-100 text-gray-500'
}

const formatCategory = (category) => {
  return category?.charAt(0).toUpperCase() + category?.slice(1) || 'General'
}

const formatTime = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const getActorName = (actor) => {
  if (!actor) return ''
  if (typeof actor === 'string') return actor
  return actor.username || actor.email || 'System'
}

const markAsRead = async () => {
  try {
    await notificationsAPI.markNotificationAsRead(props.notification.id)
    emit('read', props.notification.id)
  } catch (error) {
    console.error('Failed to mark notification as read:', error)
  }
}

const handleClick = () => {
  emit('click', props.notification)
  if (!props.notification.is_read) {
    markAsRead()
  }
}

// Icon components (inline SVG)
const OrderIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  `
}

const PaymentIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
  `
}

const MessageIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  `
}

const FileIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  `
}

const SystemIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  `
}

const BellIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
  `
}
</script>

