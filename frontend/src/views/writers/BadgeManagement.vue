<template>
  <div class="min-h-dvh bg-gray-50 page-shell space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="page-title text-gray-900">Badge Management</h1>
        <p class="mt-2 text-gray-600">View and manage your earned badges</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Badges</p>
            <p class="mt-2 text-3xl font-bold text-gray-900">{{ badgeStats.total_badges || 0 }}</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-lg">
            <span class="text-2xl">🏆</span>
          </div>
        </div>
      </div>
      <div 
        v-for="(count, type) in badgeStats.counts_by_type" 
        :key="type"
        class="card bg-white rounded-lg shadow-sm p-6"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 capitalize">{{ type }} Badges</p>
            <p class="mt-2 text-3xl font-bold text-gray-900">{{ count }}</p>
          </div>
          <div class="p-3 bg-primary-100 rounded-lg">
            <span class="text-2xl">⭐</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'earned'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === 'earned'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Earned Badges ({{ earnedBadges.length }})
        </button>
        <button
          @click="activeTab = 'available'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === 'available'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Available Badges ({{ availableBadges.length }})
        </button>
      </nav>
    </div>

    <!-- Earned Badges Tab -->
    <div v-if="activeTab === 'earned'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <select v-model="filters.type" @change="filterBadges" class="border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="performance">Performance</option>
            <option value="loyalty">Loyalty</option>
            <option value="behavioral">Behavioral</option>
            <option value="special">Special</option>
          </select>
          <input 
            v-model="filters.search" 
            @input="debouncedSearch"
            type="text" 
            placeholder="Search badges..." 
            class="border rounded px-3 py-2"
          />
          <select v-model="filters.sort" @change="filterBadges" class="border rounded px-3 py-2">
            <option value="recent">Most Recent</option>
            <option value="oldest">Oldest First</option>
            <option value="name">Name A-Z</option>
            <option value="type">By Type</option>
          </select>
        </div>
      </div>

      <!-- Badges Grid -->
      <div v-if="filteredEarnedBadges.length" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <div 
          v-for="badge in filteredEarnedBadges" 
          :key="badge.id"
          class="card bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg shadow-sm p-6 border-2 border-yellow-300 hover:shadow-lg transition-all cursor-pointer"
          @click="showBadgeDetail(badge)"
        >
          <div class="text-center">
            <div class="text-5xl mb-3">{{ badge.icon || '🏆' }}</div>
            <div class="font-bold text-gray-900 mb-1">{{ badge.name }}</div>
            <div class="text-xs text-gray-600 mb-2 capitalize">{{ badge.type }}</div>
            <div class="text-xs text-gray-500">
              Earned: {{ badge.issued_at ? new Date(badge.issued_at).toLocaleDateString() : 'N/A' }}
            </div>
            <div v-if="badge.is_auto_awarded" class="mt-2">
              <span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Auto Awarded</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-12">
        <div class="text-6xl mb-4">🏆</div>
        <p class="text-gray-500 text-lg">No badges found</p>
        <p class="text-gray-400 text-sm mt-2">Try adjusting your filters</p>
      </div>
    </div>

    <!-- Available Badges Tab -->
    <div v-if="activeTab === 'available'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <select v-model="filters.type" @change="filterAvailableBadges" class="border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="performance">Performance</option>
            <option value="loyalty">Loyalty</option>
            <option value="behavioral">Behavioral</option>
            <option value="special">Special</option>
          </select>
          <input 
            v-model="filters.search" 
            @input="debouncedSearch"
            type="text" 
            placeholder="Search badges..." 
            class="border rounded px-3 py-2"
          />
        </div>
      </div>

      <!-- Available Badges Grid -->
      <div v-if="filteredAvailableBadges.length" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <div 
          v-for="badge in filteredAvailableBadges" 
          :key="badge.id"
          class="card bg-gray-50 rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-all cursor-pointer opacity-75"
          @click="showBadgeDetail(badge)"
        >
          <div class="text-center">
            <div class="text-5xl mb-3 opacity-50">{{ badge.icon || '🏆' }}</div>
            <div class="font-bold text-gray-700 mb-1">{{ badge.name }}</div>
            <div class="text-xs text-gray-500 mb-2 capitalize">{{ badge.type }}</div>
            <div class="text-xs text-gray-400 mt-2">
              <span v-if="badge.auto_award" class="bg-blue-100 text-blue-700 px-2 py-1 rounded">Auto Award</span>
              <span v-else class="bg-gray-200 text-gray-600 px-2 py-1 rounded">Manual</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-12">
        <p class="text-gray-500">No available badges found</p>
      </div>
    </div>

    <!-- Badge Detail Modal -->
    <div 
      v-if="showDetailModal && selectedBadge"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeBadgeDetail"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-2xl font-bold text-gray-900">Badge Details</h3>
            <button @click="closeBadgeDetail" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="text-center mb-6">
            <div class="text-8xl mb-4">{{ selectedBadge.icon || '🏆' }}</div>
            <h4 class="text-2xl font-bold text-gray-900 mb-2">{{ selectedBadge.name }}</h4>
            <span class="inline-block bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm capitalize">
              {{ selectedBadge.type }}
            </span>
          </div>
          
          <div class="space-y-4">
            <div>
              <h5 class="font-semibold text-gray-700 mb-2">Description</h5>
              <p class="text-gray-600">{{ selectedBadge.description || 'No description available' }}</p>
            </div>
            
            <div v-if="selectedBadge.issued_at">
              <h5 class="font-semibold text-gray-700 mb-2">Earned</h5>
              <p class="text-gray-600">{{ new Date(selectedBadge.issued_at).toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              }) }}</p>
            </div>
            
            <div v-if="selectedBadge.is_auto_awarded !== undefined">
              <h5 class="font-semibold text-gray-700 mb-2">Award Type</h5>
              <p class="text-gray-600">
                <span :class="selectedBadge.is_auto_awarded ? 'text-green-600' : 'text-blue-600'">
                  {{ selectedBadge.is_auto_awarded ? 'Auto Awarded' : 'Manually Awarded' }}
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import writerDashboardAPI from '@/api/writer-dashboard'

const authStore = useAuthStore()

// State
const earnedBadges = ref([])
const availableBadges = ref([])
const loading = ref(false)
const activeTab = ref('earned')
const showDetailModal = ref(false)
const selectedBadge = ref(null)

const filters = ref({
  type: '',
  search: '',
  sort: 'recent',
})

// Computed
const badgeStats = computed(() => {
  const counts_by_type = {}
  earnedBadges.value.forEach(badge => {
    counts_by_type[badge.type] = (counts_by_type[badge.type] || 0) + 1
  })
  
  return {
    total_badges: earnedBadges.value.length,
    counts_by_type,
  }
})

const filteredEarnedBadges = computed(() => {
  let filtered = [...earnedBadges.value]
  
  // Filter by type
  if (filters.value.type) {
    filtered = filtered.filter(b => b.type === filters.value.type)
  }
  
  // Filter by search
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(b => 
      b.name.toLowerCase().includes(search) ||
      b.description?.toLowerCase().includes(search)
    )
  }
  
  // Sort
  if (filters.value.sort === 'recent') {
    filtered.sort((a, b) => new Date(b.issued_at || 0) - new Date(a.issued_at || 0))
  } else if (filters.value.sort === 'oldest') {
    filtered.sort((a, b) => new Date(a.issued_at || 0) - new Date(b.issued_at || 0))
  } else if (filters.value.sort === 'name') {
    filtered.sort((a, b) => a.name.localeCompare(b.name))
  } else if (filters.value.sort === 'type') {
    filtered.sort((a, b) => a.type.localeCompare(b.type))
  }
  
  return filtered
})

const filteredAvailableBadges = computed(() => {
  let filtered = [...availableBadges.value]
  
  // Filter by type
  if (filters.value.type) {
    filtered = filtered.filter(b => b.type === filters.value.type)
  }
  
  // Filter by search
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(b => 
      b.name.toLowerCase().includes(search) ||
      b.description?.toLowerCase().includes(search)
    )
  }
  
  return filtered
})

// Methods
const loadBadges = async () => {
  if (!authStore.isWriter) return
  
  loading.value = true
  try {
    const response = await writerDashboardAPI.getBadgesAndAchievements()
    earnedBadges.value = response.data?.badges || []
    availableBadges.value = response.data?.available_badges || []
  } catch (error) {
    console.error('Failed to load badges:', error)
  } finally {
    loading.value = false
  }
}

const filterBadges = () => {
  // Filters are reactive, no action needed
}

const filterAvailableBadges = () => {
  // Filters are reactive, no action needed
}

let searchTimeout = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // Search is reactive, filters will update automatically
  }, 300)
}

const showBadgeDetail = (badge) => {
  selectedBadge.value = badge
  showDetailModal.value = true
}

const closeBadgeDetail = () => {
  showDetailModal.value = false
  selectedBadge.value = null
}

// Lifecycle
onMounted(() => {
  loadBadges()
})
</script>

<style scoped>
.card {
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
}
</style>

