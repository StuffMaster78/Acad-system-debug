<template>
  <div
    v-if="website"
    class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-6 mb-6"
  >
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
          <div class="shrink-0">
            <div
              v-if="website.logo"
              class="w-12 h-12 rounded-lg bg-white dark:bg-gray-800 p-1 border border-gray-200 dark:border-gray-700"
            >
              <img
                :src="website.logo"
                :alt="website.name"
                class="w-full h-full object-contain rounded"
              />
            </div>
            <div
              v-else
              class="w-12 h-12 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-primary-600 dark:text-primary-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                />
              </svg>
            </div>
          </div>
          <div class="flex-1">
            <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">
              {{ website.name }}
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
              {{ formatDomain(website.domain) }}
            </p>
          </div>
          <div
            v-if="website.is_active !== undefined"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium',
              website.is_active
                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
            ]"
          >
            {{ website.is_active ? 'Active' : 'Inactive' }}
          </div>
        </div>

        <!-- Stats -->
        <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div class="bg-white dark:bg-gray-800/50 rounded-lg p-3 border border-primary-100 dark:border-primary-900/50">
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Posts</div>
            <div class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {{ stats.totalPosts || 0 }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ stats.publishedPosts || 0 }} published
            </div>
          </div>
          <div class="bg-white dark:bg-gray-800/50 rounded-lg p-3 border border-primary-100 dark:border-primary-900/50">
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Categories</div>
            <div class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {{ stats.totalCategories || 0 }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ stats.activeCategories || 0 }} active
            </div>
          </div>
          <div class="bg-white dark:bg-gray-800/50 rounded-lg p-3 border border-primary-100 dark:border-primary-900/50">
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Authors</div>
            <div class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {{ stats.totalAuthors || 0 }}
            </div>
          </div>
          <div class="bg-white dark:bg-gray-800/50 rounded-lg p-3 border border-primary-100 dark:border-primary-900/50">
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">Drafts</div>
            <div class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {{ stats.draftPosts || 0 }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  website: {
    type: Object,
    default: null
  },
  stats: {
    type: Object,
    default: null
  }
})

const formatDomain = (domain) => {
  if (!domain) return ''
  try {
    const url = new URL(domain)
    return url.hostname.replace('www.', '')
  } catch {
    return domain.replace(/^https?:\/\//, '').replace('www.', '')
  }
}
</script>

