<template>
  <!-- Main Nav Item -->
  <div>
    <SidebarTooltip :text="item.label" :collapsed="collapsed">
      <component
        :is="item.to ? 'router-link' : 'button'"
        :to="item.to"
        @click="handleClick"
        :class="[
          'w-full flex items-center gap-3 rounded-xl transition-all duration-200 group relative overflow-hidden',
          collapsed ? 'justify-center px-2 py-2.5' : (compact ? 'px-3 py-2' : 'px-3 py-2.5'),
          getItemClasses()
        ]"
        :aria-label="collapsed ? item.label : undefined"
        :aria-expanded="hasSubmenu ? submenuExpanded : undefined"
      >
        <!-- Icon -->
        <div :class="[
          'flex items-center justify-center rounded-lg shrink-0 transition-all duration-200',
          collapsed ? 'w-9 h-9' : (compact ? 'w-7 h-7' : 'w-9 h-9'),
          getIconBgClasses()
        ]">
          <svg :class="['transition-all duration-200', collapsed ? 'w-5 h-5' : (compact ? 'w-4 h-4' : 'w-5 h-5'), getIconClasses()]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPath" />
          </svg>
        </div>

        <!-- Label & Badge -->
        <div v-show="!collapsed" class="flex-1 flex items-center justify-between min-w-0">
          <span :class="['truncate transition-all', compact ? 'text-sm' : 'text-sm font-medium']">
            {{ item.label }}
          </span>
          
          <!-- Badge (if has count) -->
          <span
            v-if="badgeCount > 0"
            :class="[
              'ml-2 px-2 py-0.5 text-xs font-bold rounded-full shrink-0 transition-all',
              getBadgeClasses()
            ]"
          >
            {{ badgeCount > 99 ? '99+' : badgeCount }}
          </span>
        </div>

        <!-- Chevron (if has submenu) -->
        <svg
          v-if="hasSubmenu && !collapsed"
          :class="['w-4 h-4 transition-all shrink-0', submenuExpanded ? 'rotate-180' : '', getChevronClasses()]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>

        <!-- Active Indicator -->
        <div
          v-if="active"
          class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-current rounded-r-full"
          :class="getActiveIndicatorClasses()"
        />
      </component>
    </SidebarTooltip>

    <!-- Quick Links / Submenu -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div
        v-if="hasSubmenu && submenuExpanded && !collapsed"
        class="ml-3 mt-1 space-y-0.5 pl-4 border-l-2 transition-colors"
        :class="getSubmenuBorderClasses()"
      >
        <router-link
          v-for="link in item.quickLinks"
          :key="link.to"
          :to="link.to"
          @click="$emit('click')"
          :class="[
            'flex items-center justify-between gap-2 px-3 py-1.5 rounded-lg text-sm transition-all duration-150 group',
            isSubmenuActive(link) ? getSubmenuActiveClasses() : getSubmenuInactiveClasses()
          ]"
        >
          <span class="truncate">{{ link.label }}</span>
          <span
            v-if="link.badge && getBadgeValue(link.badge) > 0"
            :class="[
              'px-1.5 py-0.5 text-xs font-semibold rounded-full shrink-0',
              getSubmenuBadgeClasses(link.color)
            ]"
          >
            {{ getBadgeValue(link.badge) }}
          </span>
        </router-link>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import SidebarTooltip from '@/components/common/SidebarTooltip.vue'
import { iconMap, getCategoryColorClasses } from '@/config/modernNavigation.js'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  collapsed: {
    type: Boolean,
    default: false,
  },
  active: {
    type: Boolean,
    default: false,
  },
  compact: {
    type: Boolean,
    default: false,
  },
  badgeCounts: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['click'])

const route = useRoute()
const submenuExpanded = ref(false)

const hasSubmenu = computed(() => {
  return props.item.quickLinks && props.item.quickLinks.length > 0
})

const iconPath = computed(() => {
  return iconMap[props.item.icon] || iconMap['home']
})

const badgeCount = computed(() => {
  if (!props.item.badge) return 0
  return props.badgeCounts[props.item.badge] || 0
})

const colorClasses = computed(() => {
  return getCategoryColorClasses(props.item.color || 'gray')
})

function handleClick() {
  if (hasSubmenu.value) {
    submenuExpanded.value = !submenuExpanded.value
  }
  emit('click')
}

function isSubmenuActive(link) {
  const path = route.path
  const query = route.query
  
  if (link.to.includes('?')) {
    const [linkPath, linkQuery] = link.to.split('?')
    if (path === linkPath) {
      const params = new URLSearchParams(linkQuery)
      for (const [key, value] of params) {
        if (query[key] === value) return true
      }
    }
  }
  
  return path === link.to
}

function getBadgeValue(badgeKey) {
  return props.badgeCounts[badgeKey] || 0
}

function getItemClasses() {
  if (props.active) {
    return `${colorClasses.value.bg} ${colorClasses.value.text} font-semibold shadow-sm`
  }
  return 'text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-800/50 hover:scale-[1.01]'
}

function getIconBgClasses() {
  if (props.active) {
    return `${colorClasses.value.bg} ring-2 ring-current ring-opacity-20`
  }
  return 'bg-gray-100/80 dark:bg-slate-800/80 group-hover:bg-gray-200 dark:group-hover:bg-slate-700'
}

function getIconClasses() {
  if (props.active) {
    return colorClasses.value.icon
  }
  return `text-gray-500 dark:text-slate-400 group-hover:${colorClasses.value.icon}`
}

function getBadgeClasses() {
  return colorClasses.value.badge
}

function getChevronClasses() {
  if (props.active) {
    return colorClasses.value.icon
  }
  return 'text-gray-400 dark:text-slate-500 group-hover:text-gray-600 dark:group-hover:text-slate-300'
}

function getActiveIndicatorClasses() {
  return colorClasses.value.icon
}

function getSubmenuBorderClasses() {
  return `border-${props.item.color}-200 dark:border-${props.item.color}-800/50`
}

function getSubmenuActiveClasses() {
  return `${colorClasses.value.bg} ${colorClasses.value.text} font-semibold`
}

function getSubmenuInactiveClasses() {
  return `text-gray-600 dark:text-slate-400 hover:${colorClasses.value.bg} hover:${colorClasses.value.text}`
}

function getSubmenuBadgeClasses(color) {
  if (color) {
    const classes = getCategoryColorClasses(color)
    return classes.badge
  }
  return colorClasses.value.badge
}

// Auto-expand if child is active
watch(() => props.active, (newActive) => {
  if (newActive && hasSubmenu.value) {
    // Check if any submenu item is active
    const hasActiveChild = props.item.quickLinks?.some(link => isSubmenuActive(link))
    if (hasActiveChild) {
      submenuExpanded.value = true
    }
  }
}, { immediate: true })

// Auto-expand if child route is active
watch(() => route.path, (newPath) => {
  if (hasSubmenu.value && props.item.quickLinks) {
    const hasActiveChild = props.item.quickLinks.some(link => isSubmenuActive(link))
    if (hasActiveChild) {
      submenuExpanded.value = true
    }
  }
}, { immediate: true })
</script>

<style scoped>
/* Add smooth transitions */
button, a {
  -webkit-tap-highlight-color: transparent;
}
</style>
