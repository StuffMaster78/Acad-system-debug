<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">📢 Announcements Management</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">Create and manage system announcements</p>
      </div>
      <div class="flex items-center gap-4">
        <router-link
          to="/admin/emails"
          class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm"
        >
          📧 Mass Emails
        </router-link>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          + Create Announcement
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-wrap gap-3 items-center">
        <select v-model="filters.category" @change="loadAnnouncements" class="border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700">
          <option value="">All Categories</option>
          <option value="news">News</option>
          <option value="update">System Update</option>
          <option value="maintenance">Maintenance</option>
          <option value="promotion">Promotion</option>
          <option value="general">General</option>
        </select>
        <select v-model="filters.status" @change="loadAnnouncements" class="border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="pinned">Pinned</option>
        </select>
        <input
          v-model="filters.search"
          @input="loadAnnouncements"
          type="text"
          placeholder="Search..."
          class="border rounded px-3 py-2 flex-1 min-w-[200px] dark:bg-gray-800 dark:border-gray-700"
        />
        <button
          v-if="selectedAnnouncements.length > 0"
          @click="showBulkActions = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Bulk Actions ({{ selectedAnnouncements.length }})
        </button>
      </div>
    </div>

    <!-- Announcements Table -->
    <div class="card p-6">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="!announcements.length" class="text-center py-12">
        <p class="text-gray-500">No announcements found.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th class="text-left py-3 px-4">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  @change="toggleSelectAll"
                  class="rounded"
                />
              </th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Title</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Category</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Status</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Views</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Engagement</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Created</th>
              <th class="text-right py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="announcement in announcements"
              :key="announcement.id"
              class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <td class="py-3 px-4">
                <input
                  type="checkbox"
                  :value="announcement.id"
                  v-model="selectedAnnouncements"
                  class="rounded"
                />
              </td>
              <td class="py-3 px-4">
                <div class="flex items-center gap-2">
                  <span v-if="announcement.is_pinned" class="text-yellow-500">📌</span>
                  <span class="font-medium">{{ announcement.title }}</span>
                </div>
              </td>
              <td class="py-3 px-4">
                <span :class="getCategoryBadgeClass(announcement.category)" class="px-2 py-1 rounded text-xs">
                  {{ getCategoryLabel(announcement.category) }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span :class="announcement.is_active ? 'text-green-600' : 'text-gray-500'" class="text-sm">
                  {{ announcement.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                {{ announcement.view_count || 0 }}
              </td>
              <td class="py-3 px-4">
                <button
                  @click="viewAnalytics(announcement)"
                  class="text-primary-600 dark:text-primary-400 hover:text-primary-700 text-sm"
                >
                  View Analytics
                </button>
              </td>
              <td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                {{ formatDate(announcement.created_at) }}
              </td>
              <td class="py-3 px-4">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="editAnnouncement(announcement)"
                    class="text-blue-600 hover:text-blue-700 text-sm"
                  >
                    Edit
                  </button>
                  <button
                    @click="togglePin(announcement)"
                    class="text-yellow-600 hover:text-yellow-700 text-sm"
                  >
                    {{ announcement.is_pinned ? 'Unpin' : 'Pin' }}
                  </button>
                  <button
                    @click="deleteAnnouncement(announcement)"
                    class="text-red-600 hover:text-red-700 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingAnnouncement" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">{{ editingAnnouncement ? 'Edit' : 'Create' }} Announcement</h2>
          <button
            @click="closeModal"
            class="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>
        <AnnouncementForm
          :announcement="editingAnnouncement"
          @submit="handleFormSubmit"
          @cancel="closeModal"
        />
      </div>
    </div>

    <!-- Analytics Modal -->
    <div v-if="selectedAnnouncementForAnalytics" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Analytics: {{ selectedAnnouncementForAnalytics.title }}</h2>
          <button
            @click="selectedAnnouncementForAnalytics = null"
            class="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>
        <AnnouncementAnalytics
          v-if="analyticsData"
          :analytics="analyticsData"
          :announcement="selectedAnnouncementForAnalytics"
          @export="exportAnalytics"
        />
        <div v-else class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    </div>

    <!-- Bulk Actions Modal -->
    <div v-if="showBulkActions" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
        <h2 class="text-xl font-bold mb-4">Bulk Actions</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ selectedAnnouncements.length }} announcement(s) selected
        </p>
        <div class="space-y-2">
          <button
            @click="bulkPin"
            class="w-full px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
          >
            Pin Selected
          </button>
          <button
            @click="bulkUnpin"
            class="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Unpin Selected
          </button>
          <button
            @click="bulkDelete"
            class="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Delete Selected
          </button>
        </div>
        <button
          @click="showBulkActions = false; selectedAnnouncements = []"
          class="w-full mt-4 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import announcementsAPI from '@/api/announcements'
import AnnouncementForm from './components/AnnouncementForm.vue'
import AnnouncementAnalytics from './components/AnnouncementAnalytics.vue'

const announcements = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const editingAnnouncement = ref(null)
const selectedAnnouncements = ref([])
const showBulkActions = ref(false)
const selectedAnnouncementForAnalytics = ref(null)
const analyticsData = ref(null)

const filters = ref({
  category: '',
  status: '',
  search: ''
})

const allSelected = computed(() => {
  return announcements.value.length > 0 && 
         selectedAnnouncements.value.length === announcements.value.length
})

const loadAnnouncements = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.status === 'active') params.broadcast__is_active = true
    if (filters.value.status === 'inactive') params.broadcast__is_active = false
    if (filters.value.status === 'pinned') params.broadcast__pinned = true
    if (filters.value.search) params.search = filters.value.search

    const response = await announcementsAPI.listAnnouncements(params)
    announcements.value = response.data.results || response.data
  } catch (e) {
    console.error('Error loading announcements:', e)
  } finally {
    loading.value = false
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedAnnouncements.value = []
  } else {
    selectedAnnouncements.value = announcements.value.map(a => a.id)
  }
}

const editAnnouncement = (announcement) => {
  editingAnnouncement.value = announcement
  showCreateModal.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  editingAnnouncement.value = null
}

const handleFormSubmit = async (data) => {
  try {
    if (editingAnnouncement.value) {
      await announcementsAPI.updateAnnouncement(editingAnnouncement.value.id, data)
    } else {
      await announcementsAPI.createAnnouncement(data)
    }
    await loadAnnouncements()
    closeModal()
  } catch (e) {
    console.error('Error saving announcement:', e)
    alert('Failed to save announcement: ' + (e.response?.data?.detail || e.message))
  }
}

const togglePin = async (announcement) => {
  try {
    if (announcement.is_pinned) {
      await announcementsAPI.unpinAnnouncement(announcement.id)
    } else {
      await announcementsAPI.pinAnnouncement(announcement.id)
    }
    await loadAnnouncements()
  } catch (e) {
    console.error('Error toggling pin:', e)
  }
}

const deleteAnnouncement = async (announcement) => {
  if (!confirm(`Are you sure you want to delete "${announcement.title}"?`)) return

  try {
    await announcementsAPI.deleteAnnouncement(announcement.id)
    await loadAnnouncements()
  } catch (e) {
    console.error('Error deleting announcement:', e)
  }
}

const viewAnalytics = async (announcement) => {
  try {
    const response = await announcementsAPI.getAnalytics(announcement.id)
    analyticsData.value = response.data
    selectedAnnouncementForAnalytics.value = announcement
  } catch (e) {
    console.error('Error loading analytics:', e)
  }
}

const exportAnalytics = async () => {
  try {
    const response = await announcementsAPI.exportAnalytics(selectedAnnouncementForAnalytics.value.id)
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `announcement-analytics-${selectedAnnouncementForAnalytics.value.id}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Error exporting analytics:', e)
    // Fallback to client-side CSV generation
    const csv = convertToCSV(analyticsData.value)
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `announcement-analytics-${selectedAnnouncementForAnalytics.value.id}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }
}

const convertToCSV = (data) => {
  const headers = ['User Email', 'User Name', 'Viewed At', 'Time Spent (seconds)', 'Acknowledged', 'Acknowledged At']
  const rows = data.readers.map(reader => [
    reader.user_email || '',
    reader.user_name || '',
    reader.viewed_at || '',
    reader.time_spent || '',
    reader.acknowledged ? 'Yes' : 'No',
    reader.acknowledged_at || ''
  ])
  
  return [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')
}

const bulkPin = async () => {
  try {
    await Promise.all(selectedAnnouncements.value.map(id => 
      announcementsAPI.pinAnnouncement(id)
    ))
    await loadAnnouncements()
    selectedAnnouncements.value = []
    showBulkActions.value = false
  } catch (e) {
    console.error('Error in bulk pin:', e)
  }
}

const bulkUnpin = async () => {
  try {
    await Promise.all(selectedAnnouncements.value.map(id => 
      announcementsAPI.unpinAnnouncement(id)
    ))
    await loadAnnouncements()
    selectedAnnouncements.value = []
    showBulkActions.value = false
  } catch (e) {
    console.error('Error in bulk unpin:', e)
  }
}

const bulkDelete = async () => {
  if (!confirm(`Are you sure you want to delete ${selectedAnnouncements.value.length} announcement(s)?`)) return

  try {
    await Promise.all(selectedAnnouncements.value.map(id => 
      announcementsAPI.deleteAnnouncement(id)
    ))
    await loadAnnouncements()
    selectedAnnouncements.value = []
    showBulkActions.value = false
  } catch (e) {
    console.error('Error in bulk delete:', e)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getCategoryLabel = (category) => {
  const labels = {
    news: 'News',
    update: 'Update',
    maintenance: 'Maintenance',
    promotion: 'Promotion',
    general: 'General'
  }
  return labels[category] || category
}

const getCategoryBadgeClass = (category) => {
  const classes = {
    news: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    update: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    maintenance: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
    promotion: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
    general: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  }
  return classes[category] || classes.general
}

onMounted(() => {
  loadAnnouncements()
})
</script>
