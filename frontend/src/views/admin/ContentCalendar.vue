<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Content Calendar</h1>
        <p class="mt-2 text-gray-600">View blog posts and SEO pages by publish date</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="selectedWebsiteId"
          @change="loadCalendar"
          class="border rounded px-3 py-2"
        >
          <option value="">Select Website</option>
          <option v-for="website in websites" :key="website.id" :value="website.id">
            {{ website.name }}
          </option>
        </select>
        <button
          @click="previousMonth"
          class="px-3 py-2 border rounded hover:bg-gray-50"
        >
          ← Previous
        </button>
        <button
          @click="nextMonth"
          class="px-3 py-2 border rounded hover:bg-gray-50"
        >
          Next →
        </button>
        <button
          @click="goToToday"
          class="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Today
        </button>
        <button
          v-if="selectedWebsiteId"
          @click="exportCalendar"
          class="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Export iCal
        </button>
        <button
          v-if="selectedItems.length > 0"
          @click="showBulkActions = true"
          class="px-3 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          Bulk Actions ({{ selectedItems.length }})
        </button>
      </div>
    </div>

    <!-- Monthly Summary -->
    <div v-if="monthlySummary.length" class="card">
      <h3 class="text-lg font-semibold mb-4">Monthly Publishing Summary</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="month in monthlySummary"
          :key="month.month"
          class="border rounded p-3 text-center"
        >
          <div class="text-sm text-gray-600 mb-1">{{ formatMonth(month.month) }}</div>
          <div class="text-2xl font-bold">{{ month.total }}</div>
          <div class="text-xs text-gray-500 mt-1">
            {{ month.blog_posts }} blogs, {{ month.service_pages }} pages
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar View -->
    <div v-if="selectedWebsiteId && !loading" class="card">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-xl font-semibold">{{ currentMonthYear }}</h2>
        <div class="flex items-center gap-4 text-sm">
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 bg-blue-500 rounded"></div>
            <span>Blog Posts</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 bg-green-500 rounded"></div>
            <span>Service Pages</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-7 gap-2">
        <!-- Day headers -->
        <div
          v-for="day in dayHeaders"
          :key="day"
          class="text-center font-semibold text-gray-700 py-2"
        >
          {{ day }}
        </div>

        <!-- Calendar days -->
        <div
          v-for="(day, index) in calendarDays"
          :key="index"
          class="border rounded p-2 min-h-[100px]"
          :class="{
            'bg-gray-50': !day.isCurrentMonth,
            'bg-white': day.isCurrentMonth,
            'border-blue-400': day.isToday,
            'border-green-400 bg-green-50': dragOverDate === day.date && day.isCurrentMonth
          }"
          @dragover="handleDragOver($event, day)"
          @drop="handleDrop($event, day)"
          @dragleave="dragOverDate = null"
        >
          <div class="flex items-center justify-between mb-1">
            <span
              class="text-sm font-medium"
              :class="{
                'text-gray-400': !day.isCurrentMonth,
                'text-blue-600 font-bold': day.isToday,
                'text-gray-900': day.isCurrentMonth && !day.isToday
              }"
            >
              {{ day.date }}
            </span>
            <span
              v-if="day.contentCount > 0"
              class="text-xs bg-blue-100 text-blue-800 rounded-full px-2 py-0.5"
            >
              {{ day.contentCount }}
            </span>
          </div>

          <div class="space-y-1">
            <!-- Blog Posts -->
            <div
              v-for="post in day.blogPosts"
              :key="`blog-${post.id}`"
              class="text-xs rounded px-1 py-0.5 truncate cursor-move hover:opacity-80 transition-all"
              :class="getContentClass(post)"
              :title="`${post.title}${post.category ? ' - ' + post.category : ''}`"
              @click.stop="viewContent(post)"
              @mousedown="startDrag($event, post, day.date)"
              draggable="true"
              @dragstart="handleDragStart($event, post)"
              @dragend="handleDragEnd"
            >
              <input
                type="checkbox"
                :checked="isSelected(post)"
                @click.stop
                @change="toggleSelection(post)"
                class="mr-1"
              />
              📝 {{ post.title }}
            </div>

            <!-- Service Pages -->
            <div
              v-for="page in day.servicePages"
              :key="`page-${page.id}`"
              class="text-xs bg-green-100 text-green-800 rounded px-1 py-0.5 truncate cursor-move hover:opacity-80 transition-all"
              :title="page.title"
              @click.stop="viewContent(page)"
              @mousedown="startDrag($event, page, day.date)"
              draggable="true"
              @dragstart="handleDragStart($event, page)"
              @dragend="handleDragEnd"
            >
              <input
                type="checkbox"
                :checked="isSelected(page)"
                @click.stop
                @change="toggleSelection(page)"
                class="mr-1"
              />
              📄 {{ page.title }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-if="!selectedWebsiteId && !loading" class="card text-center py-12 text-gray-500">
      Please select a website to view the content calendar.
    </div>

    <!-- Content Detail Modal -->
    <div
      v-if="selectedContent"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click="selectedContent = null"
    >
      <div
        class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ selectedContent.title }}</h2>
            <button
              @click="selectedContent = null"
              class="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <span class="font-semibold">Type:</span>
              <span
                class="ml-2 px-2 py-1 rounded text-sm"
                :class="selectedContent.type === 'blog_post' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'"
              >
                {{ selectedContent.type === 'blog_post' ? 'Blog Post' : 'Service Page' }}
              </span>
            </div>

            <div v-if="selectedContent.category">
              <span class="font-semibold">Category:</span>
              <span class="ml-2">{{ selectedContent.category }}</span>
            </div>

            <div v-if="selectedContent.authors && selectedContent.authors.length">
              <span class="font-semibold">Authors:</span>
              <span class="ml-2">
                {{ selectedContent.authors.map(a => a.name).join(', ') }}
              </span>
            </div>

            <div>
              <span class="font-semibold">Published:</span>
              <span class="ml-2">{{ formatDate(selectedContent.publish_date) }}</span>
            </div>

            <div>
              <span class="font-semibold">URL:</span>
              <a
                :href="selectedContent.url"
                target="_blank"
                class="ml-2 text-blue-600 hover:underline"
              >
                {{ selectedContent.url }}
              </a>
            </div>

            <div class="flex gap-2 pt-4">
              <a
                :href="selectedContent.url"
                target="_blank"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                View Content
              </a>
              <button
                v-if="selectedContent.type === 'blog_post'"
                @click="editBlog(selectedContent.id)"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
              >
                Edit Blog Post
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'

const router = useRouter()
const websites = ref([])
const selectedWebsiteId = ref('')
const currentDate = ref(new Date())
const calendarData = ref([])
const monthlySummary = ref([])
const loading = ref(false)
const selectedContent = ref(null)
const selectedItems = ref([])
const showBulkActions = ref(false)
const bulkRescheduleDate = ref('')
const draggedItem = ref(null)
const dragOverDate = ref(null)
const dropZoneStyle = ref({})

const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const currentMonthYear = computed(() => {
  return currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  // First day of month
  const firstDay = new Date(year, month, 1)
  const firstDayOfWeek = firstDay.getDay()
  
  // Last day of month
  const lastDay = new Date(year, month + 1, 0)
  const daysInMonth = lastDay.getDate()
  
  // Previous month's last days
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  
  const days = []
  
  // Previous month days
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = prevMonthLastDay - i
    days.push({
      date,
      isCurrentMonth: false,
      isToday: false,
      blogPosts: [],
      servicePages: [],
      contentCount: 0
    })
  }
  
  // Current month days
  const today = new Date()
  for (let date = 1; date <= daysInMonth; date++) {
    const dayDate = new Date(year, month, date)
    const dateKey = dayDate.toISOString().split('T')[0]
    const dayData = calendarData.value.find(d => d.date === dateKey) || {
      blog_posts: [],
      service_pages: []
    }
    
    days.push({
      date,
      isCurrentMonth: true,
      isToday: dayDate.toDateString() === today.toDateString(),
      blogPosts: dayData.blog_posts || [],
      servicePages: dayData.service_pages || [],
      contentCount: dayData.total_count || 0
    })
  }
  
  // Next month days to fill the grid
  const remainingDays = 42 - days.length // 6 rows * 7 days
  for (let date = 1; date <= remainingDays; date++) {
    days.push({
      date,
      isCurrentMonth: false,
      isToday: false,
      blogPosts: [],
      servicePages: [],
      contentCount: 0
    })
  }
  
  return days
})

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({})
    websites.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadCalendar = async () => {
  if (!selectedWebsiteId.value) {
    calendarData.value = []
    return
  }
  
  loading.value = true
  try {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    const startDate = new Date(year, month, 1).toISOString().split('T')[0]
    const endDate = new Date(year, month + 1, 0).toISOString().split('T')[0]
    
    const [calendarRes, summaryRes] = await Promise.all([
      blogPagesAPI.getContentCalendar({
        website_id: selectedWebsiteId.value,
        start_date: startDate,
        end_date: endDate
      }),
      blogPagesAPI.getMonthlySummary({
        website_id: selectedWebsiteId.value,
        months: 12
      })
    ])
    
    calendarData.value = calendarRes.data?.calendar || []
    monthlySummary.value = summaryRes.data?.monthly_summary || []
  } catch (e) {
    console.error('Failed to load calendar:', e)
  } finally {
    loading.value = false
  }
}

const loadMonthlySummary = async () => {
  if (!selectedWebsiteId.value) return
  
  try {
    const res = await blogPagesAPI.getMonthlySummary({
      website_id: selectedWebsiteId.value,
      months: 12
    })
    monthlySummary.value = res.data?.monthly_summary || []
  } catch (e) {
    console.error('Failed to load monthly summary:', e)
  }
}

const previousMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() - 1,
    1
  )
  loadCalendar()
}

const nextMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() + 1,
    1
  )
  loadCalendar()
}

const goToToday = () => {
  currentDate.value = new Date()
  loadCalendar()
}

const viewContent = (content) => {
  selectedContent.value = content
}

const editBlog = (id) => {
  router.push(`/admin/blog/${id}`)
  selectedContent.value = null
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatMonth = (monthString) => {
  const [year, month] = monthString.split('-')
  const date = new Date(year, parseInt(month) - 1, 1)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

const getContentClass = (post) => {
  // Color coding by category
  const categoryColors = {
    'Technology': 'bg-blue-100 text-blue-800',
    'Marketing': 'bg-purple-100 text-purple-800',
    'Business': 'bg-green-100 text-green-800',
    'Design': 'bg-pink-100 text-pink-800',
    'SEO': 'bg-yellow-100 text-yellow-800',
  }
  
  if (post.category && categoryColors[post.category]) {
    return categoryColors[post.category]
  }
  
  return 'bg-blue-100 text-blue-800' // Default
}

const toggleSelection = (item) => {
  const index = selectedItems.value.findIndex(
    i => i.id === item.id && i.type === item.type
  )
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(item)
  }
}

const isSelected = (item) => {
  return selectedItems.value.some(
    i => i.id === item.id && i.type === item.type
  )
}

const clearSelection = () => {
  selectedItems.value = []
  showBulkActions.value = false
}

const bulkReschedule = async () => {
  if (!bulkRescheduleDate.value || selectedItems.value.length === 0) return
  
  try {
    const contentItems = selectedItems.value.map(item => ({
      id: item.id,
      type: item.type,
      new_date: bulkRescheduleDate.value
    }))
    
    await blogPagesAPI.bulkRescheduleContent({ content_items: contentItems })
    await loadCalendar()
    clearSelection()
    bulkRescheduleDate.value = ''
  } catch (e) {
    console.error('Failed to reschedule:', e)
    alert('Failed to reschedule content. Please try again.')
  }
}

const exportCalendar = async () => {
  if (!selectedWebsiteId.value) return
  
  try {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    const startDate = new Date(year, month, 1).toISOString().split('T')[0]
    const endDate = new Date(year, month + 1, 0).toISOString().split('T')[0]
    
    const response = await blogPagesAPI.exportCalendarICal({
      website_id: selectedWebsiteId.value,
      start_date: startDate,
      end_date: endDate
    })
    
    // Create download link
    const blob = new Blob([response.data], { type: 'text/calendar' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `content-calendar-${selectedWebsiteId.value}.ics`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Failed to export calendar:', e)
    alert('Failed to export calendar. Please try again.')
  }
}

const startDrag = (event, item, currentDate) => {
  draggedItem.value = { ...item, currentDate }
}

const handleDragStart = (event, item) => {
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', JSON.stringify(item))
}

const handleDragEnd = () => {
  draggedItem.value = null
  dragOverDate.value = null
}

// Add drag and drop handlers to calendar days
const handleDragOver = (event, day) => {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'
  
  if (day.isCurrentMonth) {
    dragOverDate.value = day.date
    // Calculate drop zone position (simplified - would need actual element position)
    const rect = event.currentTarget.getBoundingClientRect()
    dropZoneStyle.value = {
      left: `${rect.left}px`,
      top: `${rect.top}px`,
      width: `${rect.width}px`,
      height: `${rect.height}px`
    }
  }
}

const handleDrop = async (event, day) => {
  event.preventDefault()
  
  if (!draggedItem.value || !day.isCurrentMonth) return
  
  try {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    const newDate = new Date(year, month, day.date).toISOString().split('T')[0]
    
    await blogPagesAPI.bulkRescheduleContent({
      content_items: [{
        id: draggedItem.value.id,
        type: draggedItem.value.type,
        new_date: newDate
      }]
    })
    
    await loadCalendar()
    dragOverDate.value = null
    draggedItem.value = null
  } catch (e) {
    console.error('Failed to reschedule:', e)
    alert('Failed to reschedule content. Please try again.')
  }
}

const formatDropDate = (date) => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const dateObj = new Date(year, month, date)
  return dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

watch(selectedWebsiteId, () => {
  if (selectedWebsiteId.value) {
    loadCalendar()
    loadMonthlySummary()
  }
})

onMounted(async () => {
  await loadWebsites()
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}
</style>

