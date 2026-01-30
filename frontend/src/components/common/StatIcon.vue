<template>
  <div
    :class="[
      'inline-flex items-center justify-center rounded-xl transition-all duration-300',
      sizeClasses,
      colorClasses,
      animated ? 'group-hover:scale-110 group-hover:rotate-3' : ''
    ]"
  >
    <component 
      :is="iconComponent" 
      :class="iconSizeClasses"
      :stroke-width="strokeWidth"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import * as HeroIconsOutline from '@heroicons/vue/24/outline'
import * as HeroIconsSolid from '@heroicons/vue/24/solid'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  variant: {
    type: String,
    default: 'outline', // 'outline' | 'solid'
    validator: (value) => ['outline', 'solid'].includes(value)
  },
  size: {
    type: String,
    default: 'md', // 'sm' | 'md' | 'lg' | 'xl'
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  color: {
    type: String,
    default: 'blue', // Color theme
    validator: (value) => ['blue', 'green', 'purple', 'amber', 'red', 'indigo', 'emerald', 'pink', 'cyan', 'orange', 'gray'].includes(value)
  },
  gradient: {
    type: Boolean,
    default: true
  },
  animated: {
    type: Boolean,
    default: true
  },
  strokeWidth: {
    type: [String, Number],
    default: 2
  }
})

// Icon mapping
const iconMap = {
  // Orders & Documents
  'document': 'DocumentTextIcon',
  'orders': 'ClipboardDocumentListIcon',
  'clipboard': 'ClipboardIcon',
  'paper': 'DocumentTextIcon',
  'file': 'DocumentIcon',
  
  // Financial
  'dollar': 'CurrencyDollarIcon',
  'money': 'BanknotesIcon',
  'wallet': 'WalletIcon',
  'credit-card': 'CreditCardIcon',
  'cash': 'BanknotesIcon',
  'revenue': 'ChartBarIcon',
  
  // Users & People
  'user': 'UserIcon',
  'users': 'UsersIcon',
  'user-group': 'UserGroupIcon',
  'team': 'UserGroupIcon',
  
  // Status & Actions
  'check': 'CheckCircleIcon',
  'check-badge': 'CheckBadgeIcon',
  'x-circle': 'XCircleIcon',
  'clock': 'ClockIcon',
  'pending': 'ClockIcon',
  'hourglass': 'ClockIcon',
  
  // Analytics & Charts
  'chart': 'ChartBarIcon',
  'chart-bar': 'ChartBarIcon',
  'chart-pie': 'ChartPieIcon',
  'trending-up': 'ArrowTrendingUpIcon',
  'trending-down': 'ArrowTrendingDownIcon',
  'presentation': 'PresentationChartLineIcon',
  
  // Special
  'star': 'StarIcon',
  'trophy': 'TrophyIcon',
  'gift': 'GiftIcon',
  'sparkles': 'SparklesIcon',
  'lightning': 'BoltIcon',
  'fire': 'FireIcon',
  
  // Communication
  'chat': 'ChatBubbleLeftRightIcon',
  'mail': 'EnvelopeIcon',
  'bell': 'BellIcon',
  'inbox': 'InboxIcon',
  
  // Content
  'book': 'BookOpenIcon',
  'newspaper': 'NewspaperIcon',
  'photo': 'PhotoIcon',
  'video': 'VideoCameraIcon',
  
  // System
  'cog': 'Cog6ToothIcon',
  'adjustments': 'AdjustmentsHorizontalIcon',
  'shield': 'ShieldCheckIcon',
  'globe': 'GlobeAltIcon',
  'server': 'ServerIcon',
  
  // Misc
  'tag': 'TagIcon',
  'ticket': 'TicketIcon',
  'briefcase': 'BriefcaseIcon',
  'academic-cap': 'AcademicCapIcon',
  'beaker': 'BeakerIcon',
  'cube': 'CubeIcon',
  'puzzle': 'PuzzlePieceIcon',
  'calendar': 'CalendarIcon',
  'arrow-path': 'ArrowPathIcon',
  'ban': 'NoSymbolIcon',
  'exclamation': 'ExclamationTriangleIcon',
  'information': 'InformationCircleIcon',
  'archive': 'ArchiveBoxIcon',
  'trash': 'TrashIcon',
  'pencil': 'PencilIcon',
  'folder': 'FolderIcon',
}

const iconComponent = computed(() => {
  const iconName = iconMap[props.name] || 'QuestionMarkCircleIcon'
  const icons = props.variant === 'solid' ? HeroIconsSolid : HeroIconsOutline
  return icons[iconName] || HeroIconsOutline.QuestionMarkCircleIcon
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'w-8 h-8 p-1.5',
    md: 'w-10 h-10 p-2',
    lg: 'w-12 h-12 p-2.5',
    xl: 'w-14 h-14 p-3'
  }
  return sizes[props.size]
})

const iconSizeClasses = computed(() => {
  const sizes = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-7 h-7',
    xl: 'w-8 h-8'
  }
  return sizes[props.size]
})

const colorClasses = computed(() => {
  if (props.gradient) {
    const gradients = {
      blue: 'bg-gradient-to-br from-blue-400 to-blue-600 text-white shadow-blue-500/20',
      green: 'bg-gradient-to-br from-green-400 to-green-600 text-white shadow-green-500/20',
      emerald: 'bg-gradient-to-br from-emerald-400 to-emerald-600 text-white shadow-emerald-500/20',
      purple: 'bg-gradient-to-br from-purple-400 to-purple-600 text-white shadow-purple-500/20',
      amber: 'bg-gradient-to-br from-amber-400 to-amber-600 text-white shadow-amber-500/20',
      red: 'bg-gradient-to-br from-red-400 to-red-600 text-white shadow-red-500/20',
      indigo: 'bg-gradient-to-br from-indigo-400 to-indigo-600 text-white shadow-indigo-500/20',
      pink: 'bg-gradient-to-br from-pink-400 to-pink-600 text-white shadow-pink-500/20',
      cyan: 'bg-gradient-to-br from-cyan-400 to-cyan-600 text-white shadow-cyan-500/20',
      orange: 'bg-gradient-to-br from-orange-400 to-orange-600 text-white shadow-orange-500/20',
      gray: 'bg-gradient-to-br from-gray-400 to-gray-600 text-white shadow-gray-500/20',
    }
    return `${gradients[props.color]} shadow-lg`
  } else {
    const flat = {
      blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
      green: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
      emerald: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400',
      purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
      amber: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400',
      red: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
      indigo: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
      pink: 'bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400',
      cyan: 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400',
      orange: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
      gray: 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400',
    }
    return flat[props.color]
  }
})
</script>

<style scoped>
/* Add smooth transitions */
div {
  transform-origin: center;
}
</style>
