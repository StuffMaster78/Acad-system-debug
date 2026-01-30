<template>
  <aside
    :class="[
      'fixed inset-y-0 left-0 z-40 flex flex-col transition-all duration-300 ease-out',
      'glass-strong border-r border-gray-200/50 dark:border-slate-700/50',
      sidebarOpen ? 'translate-x-0' : '-translate-x-full',
      'lg:translate-x-0',
      collapsed ? 'w-20' : 'w-72'
    ]"
    :aria-label="collapsed ? 'Collapsed navigation' : 'Navigation'"
    role="navigation"
  >
    <!-- HEADER -->
    <div class="flex items-center justify-between h-16 px-4 border-b border-gray-200/50 dark:border-slate-700/50 shrink-0">
      <router-link 
        to="/dashboard" 
        class="flex items-center gap-3 transition-opacity hover:opacity-80"
        :class="collapsed ? 'w-full justify-center' : ''"
      >
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 shadow-lg shrink-0">
          <span class="text-xl font-bold text-white">W</span>
        </div>
        <span v-show="!collapsed" class="text-lg font-bold text-gray-900 dark:text-slate-100 tracking-tight">
          WritePro
        </span>
      </router-link>

      <!-- Desktop: Collapse Toggle -->
      <button
        v-if="!collapsed"
        @click="collapsed = !collapsed"
        class="hidden lg:flex p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:hover:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 transition-all shrink-0 group"
        title="Collapse sidebar"
      >
        <svg class="w-5 h-5 transition-transform group-hover:-translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      </button>

      <!-- Mobile: Close Button -->
      <button
        @click="$emit('close')"
        class="lg:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:hover:bg-slate-800 transition-all"
        aria-label="Close sidebar"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- SEARCH -->
    <div v-show="!collapsed" class="px-3 py-3 border-b border-gray-200/50 dark:border-slate-700/50 shrink-0">
      <div class="relative">
        <input
          v-model="searchQuery"
          ref="searchInput"
          type="text"
          placeholder="Search menu... ⌘K"
          class="w-full pl-10 pr-10 py-2.5 text-sm bg-gray-50 dark:bg-slate-900/50 border border-gray-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all placeholder-gray-400 dark:placeholder-slate-500"
          @focus="searchFocused = true"
          @blur="handleSearchBlur"
        />
        <svg class="absolute left-3 top-3 w-4 h-4 text-gray-400 dark:text-slate-500 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <button
          v-if="searchQuery"
          @click="searchQuery = ''"
          class="absolute right-3 top-3 w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-slate-300"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Search Results Dropdown -->
      <div
        v-if="searchQuery && searchResults.length > 0"
        class="absolute left-3 right-3 mt-2 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl shadow-2xl max-h-96 overflow-y-auto z-50 animate-slideDown"
      >
        <div class="p-2">
          <router-link
            v-for="result in searchResults"
            :key="result.to"
            :to="result.to"
            @click="searchQuery = ''; $emit('close')"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-all group"
          >
            <div :class="['w-8 h-8 rounded-lg flex items-center justify-center shrink-0', `bg-${result.color}-100 dark:bg-${result.color}-900/30`]">
              <svg :class="['w-4 h-4', `text-${result.color}-600 dark:text-${result.color}-400`]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getIconPath(result.icon)" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                {{ result.label }}
              </div>
              <div v-if="result.description" class="text-xs text-gray-500 dark:text-slate-400 truncate">
                {{ result.description }}
              </div>
            </div>
            <svg class="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Collapsed Search Button -->
    <div v-show="collapsed" class="px-3 py-3 border-b border-gray-200/50 dark:border-slate-700/50 shrink-0">
      <button
        @click="collapsed = false; $nextTick(() => $refs.searchInput?.focus())"
        class="w-full p-3 rounded-xl text-gray-500 hover:text-gray-700 dark:hover:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 transition-all flex items-center justify-center group"
        title="Search menu"
      >
        <svg class="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </button>
    </div>

    <!-- PRIMARY ACTION -->
    <div class="px-3 py-3 shrink-0">
      <SidebarTooltip :text="ctaLabel" :collapsed="collapsed">
        <router-link
          :to="ctaRoute"
          :class="[
            'flex items-center justify-center gap-2.5 py-3 rounded-xl font-semibold text-sm transition-all shadow-lg group',
            'bg-gradient-to-r from-primary-600 to-primary-700 text-white',
            'hover:from-primary-700 hover:to-primary-800 hover:shadow-xl hover:scale-[1.02]',
            'active:scale-95',
            collapsed ? 'w-full' : 'w-full'
          ]"
        >
          <svg class="w-5 h-5 group-hover:rotate-90 transition-transform shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
          </svg>
          <span v-show="!collapsed" class="truncate">{{ ctaLabel }}</span>
        </router-link>
      </SidebarTooltip>
    </div>

    <!-- NAVIGATION -->
    <nav class="flex-1 px-3 py-2 overflow-y-auto custom-scrollbar" aria-label="Main navigation">
      <!-- Core Navigation Items -->
      <div class="space-y-1">
        <template v-for="item in visibleCoreItems" :key="item.id">
          <NavItem
            :item="item"
            :collapsed="collapsed"
            :active="isActive(item)"
            @click="handleItemClick(item)"
          />
        </template>
      </div>

      <!-- Divider -->
      <div class="my-4 border-t border-gray-200/50 dark:border-slate-700/50"></div>

      <!-- MORE Section (Collapsed by default) -->
      <div v-if="hasMoreItems">
        <SidebarTooltip :text="'More'" :collapsed="collapsed">
          <button
            @click="moreExpanded = !moreExpanded"
            :class="[
              'w-full flex items-center gap-3 py-2.5 rounded-xl transition-all group',
              'text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-100',
              'hover:bg-gray-100 dark:hover:bg-slate-800',
              collapsed ? 'justify-center px-2' : 'px-3'
            ]"
          >
            <div class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-slate-800 flex items-center justify-center shrink-0 group-hover:bg-gray-200 dark:group-hover:bg-slate-700 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
              </svg>
            </div>
            <span v-show="!collapsed" class="flex-1 text-left text-sm font-medium">More</span>
            <svg v-show="!collapsed" :class="['w-4 h-4 transition-transform', moreExpanded ? 'rotate-180' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </SidebarTooltip>

        <!-- More Items (When Expanded) -->
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div v-if="moreExpanded && !collapsed" class="mt-2 space-y-3 pl-2">
            <div v-for="category in moreCategories" :key="category.category" class="space-y-1">
              <div class="px-3 py-1 text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider">
                {{ category.category }}
              </div>
              <NavItem
                v-for="item in category.items"
                :key="item.to"
                :item="item"
                :collapsed="false"
                :active="isActive(item)"
                :compact="true"
                :badge-counts="badgeCounts"
                @click="handleItemClick(item)"
              />
            </div>
          </div>
        </Transition>
      </div>
    </nav>

    <!-- FOOTER -->
    <div class="px-3 py-3 border-t border-gray-200/50 dark:border-slate-700/50 shrink-0 space-y-2">
      <!-- Theme Toggle -->
      <SidebarTooltip :text="'Toggle theme'" :collapsed="collapsed">
        <button
          @click="toggleTheme"
          :class="[
            'w-full flex items-center gap-3 py-2.5 rounded-xl transition-all group',
            'text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-100',
            'hover:bg-gray-100 dark:hover:bg-slate-800',
            collapsed ? 'justify-center px-2' : 'px-3'
          ]"
        >
          <div class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-slate-800 flex items-center justify-center shrink-0 group-hover:bg-gray-200 dark:group-hover:bg-slate-700 transition-colors">
            <svg v-if="isDark" class="w-4 h-4 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg v-else class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          </div>
          <span v-show="!collapsed" class="text-sm font-medium">
            {{ isDark ? 'Light Mode' : 'Dark Mode' }}
          </span>
        </button>
      </SidebarTooltip>

      <!-- Expand Button (when collapsed) -->
      <button
        v-if="collapsed"
        @click="collapsed = false"
        class="w-full p-3 rounded-xl text-gray-500 hover:text-gray-700 dark:hover:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 transition-all flex items-center justify-center group"
        title="Expand sidebar"
      >
        <svg class="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <!-- Mobile Overlay -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="sidebarOpen"
          class="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden"
          @click="$emit('close')"
        />
      </Transition>
    </Teleport>
  </aside>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SidebarTooltip from '@/components/common/SidebarTooltip.vue'
import NavItem from './NavItem.vue'
import { coreNavigation, clientNavigation, writerNavigation, moreNavigation, iconMap } from '@/config/modernNavigation.js'

const props = defineProps({
  sidebarOpen: {
    type: Boolean,
    default: false,
  },
  badgeCounts: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['close', 'update:sidebarOpen'])

const route = useRoute()
const authStore = useAuthStore()

// State
const collapsed = ref(false)
const searchQuery = ref('')
const searchFocused = ref(false)
const moreExpanded = ref(false)
const isDark = ref(false)
const searchInput = ref(null)

// Computed
const userRole = computed(() => {
  if (authStore.isClient) return 'client'
  if (authStore.isWriter) return 'writer'
  if (authStore.isSuperAdmin) return 'superadmin'
  if (authStore.isAdmin) return 'admin'
  if (authStore.isSupport) return 'support'
  return 'client'
})

const ctaLabel = computed(() => {
  if (authStore.isClient) return 'Create Order'
  return 'Place Order'
})

const ctaRoute = computed(() => {
  if (authStore.isClient) return '/orders/wizard'
  return '/admin/orders/create'
})

const visibleCoreItems = computed(() => {
  let items = []
  
  if (userRole.value === 'client') {
    items = clientNavigation
  } else if (userRole.value === 'writer') {
    items = writerNavigation
  } else {
    items = coreNavigation.filter(item => 
      !item.roles || item.roles.includes('all') || item.roles.includes(userRole.value)
    )
  }
  
  return items
})

const hasMoreItems = computed(() => {
  return userRole.value === 'admin' || userRole.value === 'superadmin'
})

const moreCategories = computed(() => {
  if (!hasMoreItems.value) return []
  
  return moreNavigation.admin.filter(group =>
    !group.roles || group.roles.includes(userRole.value)
  )
})

const searchResults = computed(() => {
  if (!searchQuery.value || searchQuery.value.length < 2) return []
  
  const query = searchQuery.value.toLowerCase()
  const allItems = []
  
  // Search core items
  visibleCoreItems.value.forEach(item => {
    if (matchesSearch(item, query)) {
      allItems.push(item)
    }
    // Search quick links
    if (item.quickLinks) {
      item.quickLinks.forEach(link => {
        if (matchesSearch(link, query)) {
          allItems.push({
            ...link,
            parent: item.label,
            color: link.color || item.color,
            icon: link.icon || item.icon,
          })
        }
      })
    }
  })
  
  // Search more items
  if (hasMoreItems.value) {
    moreCategories.value.forEach(category => {
      category.items.forEach(item => {
        if (matchesSearch(item, query)) {
          allItems.push({
            ...item,
            category: category.category,
          })
        }
      })
    })
  }
  
  return allItems.slice(0, 8)
})

// Methods
function matchesSearch(item, query) {
  const searchText = `${item.label} ${item.description || ''} ${item.category || ''} ${item.parent || ''}`.toLowerCase()
  return searchText.includes(query)
}

function isActive(item) {
  if (!item.to) return false
  const path = route.path
  const query = route.query
  
  // Exact match
  if (path === item.to) return true
  
  // Handle query params
  if (item.to.includes('?')) {
    const [itemPath, itemQuery] = item.to.split('?')
    if (path === itemPath) {
      const itemParams = new URLSearchParams(itemQuery)
      for (const [key, value] of itemParams) {
        if (query[key] === value) return true
      }
    }
  }
  
  // Starts with (for parent routes)
  if (item.to !== '/dashboard' && path.startsWith(item.to)) return true
  
  return false
}

function handleItemClick(item) {
  if (window.innerWidth < 1024) {
    emit('close')
  }
}

function handleSearchBlur() {
  // Delay to allow click events on search results
  setTimeout(() => {
    searchFocused.value = false
  }, 200)
}

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

function getIconPath(iconName) {
  return iconMap[iconName] || iconMap['home']
}

// Keyboard shortcut (⌘K)
function handleKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    if (collapsed.value) {
      collapsed.value = false
    }
    searchInput.value?.focus()
  }
  
  // Escape to collapse search
  if (e.key === 'Escape' && searchFocused.value) {
    searchQuery.value = ''
    searchInput.value?.blur()
  }
}

// Lifecycle
onMounted(() => {
  // Initialize theme
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.classList.toggle('dark', isDark.value)
  
  // Add keyboard listener
  window.addEventListener('keydown', handleKeydown)
  
  // Auto-collapse on mobile
  if (window.innerWidth < 1024) {
    collapsed.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

// Watch for responsive changes
watch(() => props.sidebarOpen, (newVal) => {
  if (newVal && window.innerWidth < 1024) {
    collapsed.value = false
  }
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgb(203 213 225) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgb(203 213 225);
  border-radius: 3px;
}

.dark .custom-scrollbar {
  scrollbar-color: rgb(51 65 85) transparent;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgb(51 65 85);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slideDown {
  animation: slideDown 0.2s ease-out;
}
</style>
