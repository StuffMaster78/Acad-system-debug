<template>
  <div class="flex items-center gap-2.5 flex-1 min-w-0">
    <!-- Logo Icon -->
    <div :class="[
      'flex items-center justify-center shrink-0 rounded-lg shadow-lg shadow-primary-500/20 transition-all duration-300',
      size === 'sm' ? 'w-8 h-8' : size === 'md' ? 'w-10 h-10' : 'w-12 h-12',
      variant === 'gradient' 
        ? 'bg-gradient-to-br from-primary-600 to-primary-700 dark:from-primary-500 dark:to-primary-600'
        : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
    ]">
      <!-- SVG Logo -->
      <svg 
        v-if="variant === 'gradient'"
        :class="size === 'sm' ? 'w-5 h-5' : size === 'md' ? 'w-6 h-6' : 'w-7 h-7'"
        viewBox="0 0 40 40" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="penGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:1" />
          </linearGradient>
          <linearGradient id="inkGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.9" />
            <stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:0.7" />
          </linearGradient>
        </defs>
        
        <!-- Ink trail forming "W" shape -->
        <path d="M8 28 Q12 20, 16 24 T24 20 T32 24" stroke="url(#inkGradient)" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>
        <path d="M8 28 Q10 24, 12 26" stroke="url(#inkGradient)" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.6"/>
        
        <!-- Pen/Quill body -->
        <path d="M28 8 L32 12 L30 16 L26 12 Z" fill="url(#penGradient)" stroke="url(#penGradient)" stroke-width="1"/>
        <path d="M28 8 L24 10 L26 12 L30 12 Z" fill="url(#penGradient)" opacity="0.9"/>
        
        <!-- Pen tip -->
        <circle cx="24" cy="10" r="1.5" fill="#ffffff"/>
        
        <!-- Ink drops -->
        <circle cx="10" cy="26" r="1.5" fill="url(#inkGradient)" opacity="0.7"/>
        <circle cx="14" cy="22" r="1" fill="url(#inkGradient)" opacity="0.6"/>
      </svg>
      
      <!-- Text fallback for very small sizes -->
      <span 
        v-else-if="showTextFallback"
        :class="[
          'font-bold text-primary-600 dark:text-primary-400',
          size === 'sm' ? 'text-xs' : size === 'md' ? 'text-sm' : 'text-base'
        ]"
      >
        WF
      </span>
    </div>
    
    <!-- Logo Text -->
    <h1 
      v-if="showText && !collapsed"
      :class="[
        'font-semibold tracking-tight text-gray-900 dark:text-gray-100 transition-all duration-300 leading-tight truncate',
        size === 'sm' ? 'text-sm' : size === 'md' ? 'text-base' : 'text-lg'
      ]"
    >
      {{ appName }}
    </h1>
  </div>
</template>

<script setup>
const props = defineProps({
  size: {
    type: String,
    default: 'md', // 'sm', 'md', 'lg'
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  variant: {
    type: String,
    default: 'gradient', // 'gradient' or 'outline'
    validator: (value) => ['gradient', 'outline'].includes(value)
  },
  showText: {
    type: Boolean,
    default: true
  },
  collapsed: {
    type: Boolean,
    default: false
  },
  showTextFallback: {
    type: Boolean,
    default: false
  }
})

const appName = import.meta.env.VITE_APP_NAME || 'WriteFlow'
</script>

