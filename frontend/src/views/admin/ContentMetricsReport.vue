<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Content Metrics & Reporting</h1>
        <p class="mt-2 text-gray-600">Track content performance, publishing targets, and freshness</p>
      </div>
      <router-link
        to="/admin/content-metrics"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        View Detailed Metrics
      </router-link>
    </div>

    <!-- Content Reminders Widget -->
    <div class="card">
      <ContentRemindersWidget />
    </div>

    <!-- Additional Content Metrics can be added here -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card">
        <h2 class="text-xl font-semibold mb-4">Quick Links</h2>
        <div class="space-y-3">
          <router-link
            to="/admin/content-metrics"
            class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="font-medium text-gray-900">Content Metrics Dashboard</div>
            <div class="text-sm text-gray-600 mt-1">View detailed content analytics and SEO health</div>
          </router-link>
          <router-link
            to="/admin/content-calendar"
            class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="font-medium text-gray-900">Content Calendar</div>
            <div class="text-sm text-gray-600 mt-1">Manage content scheduling and publishing</div>
          </router-link>
          <router-link
            to="/admin/blog"
            class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="font-medium text-gray-900">Blog Management</div>
            <div class="text-sm text-gray-600 mt-1">Create and manage blog posts</div>
          </router-link>
        </div>
      </div>

      <div class="card">
        <h2 class="text-xl font-semibold mb-4">Content Health Overview</h2>
        <div class="space-y-4">
          <div class="p-4 bg-blue-50 rounded-lg">
            <div class="text-sm text-gray-600 mb-1">Total Published Posts</div>
            <div class="text-2xl font-bold text-blue-700">{{ contentStats.totalPublished || '—' }}</div>
          </div>
          <div class="p-4 bg-green-50 rounded-lg">
            <div class="text-sm text-gray-600 mb-1">Content Freshness Score</div>
            <div class="text-2xl font-bold text-green-700">{{ contentStats.freshnessScore || '—' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ContentRemindersWidget from '@/components/content/ContentRemindersWidget.vue'
import blogPagesAPI from '@/api/blog-pages'

const contentStats = ref({
  totalPublished: null,
  freshnessScore: null
})

const loadContentStats = async () => {
  // Load basic content statistics
  // This can be expanded with more detailed metrics
}

onMounted(() => {
  loadContentStats()
})
</script>

<style scoped>
.card {
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}
</style>

