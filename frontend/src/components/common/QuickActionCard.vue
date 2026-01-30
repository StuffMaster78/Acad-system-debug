<template>
  <router-link
    :to="to"
    class="group relative bg-white dark:bg-slate-800 rounded-2xl shadow-sm p-6 text-center transition-all duration-300 hover:shadow-xl hover:scale-[1.03] border border-gray-200 dark:border-slate-700 hover:border-primary-400 dark:hover:border-primary-500 overflow-hidden"
  >
    <!-- Gradient overlay on hover -->
    <div class="absolute inset-0 bg-gradient-to-br from-primary-500/0 to-primary-600/0 group-hover:from-primary-500/5 group-hover:to-primary-600/5 transition-all duration-300 rounded-2xl"></div>
    
    <!-- Content -->
    <div class="relative z-10">
      <!-- Icon with gradient background -->
      <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br mb-4 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3 shadow-lg"
        :class="gradientClass">
        <component 
          :is="iconComponent" 
          class="w-7 h-7 text-white"
          :stroke-width="2"
        />
      </div>
      
      <!-- Title -->
      <div class="font-bold text-gray-900 dark:text-slate-100 mb-1.5 text-base">
        {{ title }}
      </div>
      
      <!-- Description -->
      <div class="text-sm text-gray-500 dark:text-slate-400">
        {{ description }}
      </div>
      
      <!-- Badge (optional) -->
      <div v-if="badge" class="absolute top-3 right-3">
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400">
          {{ badge }}
        </span>
      </div>
      
      <!-- Active indicator -->
      <div class="absolute top-3 left-3 w-2.5 h-2.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        :class="pulseClass">
        <span class="absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping"
          :class="pulseClass"></span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import * as HeroIcons from '@heroicons/vue/24/outline'

const props = defineProps({
  to: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'blue',
    validator: (value) => ['blue', 'green', 'purple', 'amber', 'red', 'indigo', 'emerald', 'pink', 'cyan', 'orange'].includes(value)
  },
  badge: {
    type: [String, Number],
    default: null
  }
})

// Icon mapping
const iconMap = {
  'orders': HeroIcons.ClipboardDocumentListIcon,
  'users': HeroIcons.UsersIcon,
  'payments': HeroIcons.BanknotesIcon,
  'refunds': HeroIcons.ArrowUturnLeftIcon,
  'websites': HeroIcons.GlobeAltIcon,
  'analytics': HeroIcons.ChartBarIcon,
  'settings': HeroIcons.Cog6ToothIcon,
  'support': HeroIcons.LifebuoyIcon,
  'tickets': HeroIcons.TicketIcon,
  'reports': HeroIcons.DocumentChartBarIcon,
  'content': HeroIcons.DocumentTextIcon,
  'media': HeroIcons.PhotoIcon,
  'blog': HeroIcons.NewspaperIcon,
}

const iconComponent = computed(() => {
  return iconMap[props.icon] || HeroIcons.QuestionMarkCircleIcon
})

const gradientClass = computed(() => {
  const gradients = {
    blue: 'from-blue-400 to-blue-600 shadow-blue-500/30',
    green: 'from-green-400 to-green-600 shadow-green-500/30',
    emerald: 'from-emerald-400 to-emerald-600 shadow-emerald-500/30',
    purple: 'from-purple-400 to-purple-600 shadow-purple-500/30',
    amber: 'from-amber-400 to-amber-600 shadow-amber-500/30',
    red: 'from-red-400 to-red-600 shadow-red-500/30',
    indigo: 'from-indigo-400 to-indigo-600 shadow-indigo-500/30',
    pink: 'from-pink-400 to-pink-600 shadow-pink-500/30',
    cyan: 'from-cyan-400 to-cyan-600 shadow-cyan-500/30',
    orange: 'from-orange-400 to-orange-600 shadow-orange-500/30',
  }
  return gradients[props.color]
})

const pulseClass = computed(() => {
  const pulses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    emerald: 'bg-emerald-500',
    purple: 'bg-purple-500',
    amber: 'bg-amber-500',
    red: 'bg-red-500',
    indigo: 'bg-indigo-500',
    pink: 'bg-pink-500',
    cyan: 'bg-cyan-500',
    orange: 'bg-orange-500',
  }
  return pulses[props.color]
})
</script>
