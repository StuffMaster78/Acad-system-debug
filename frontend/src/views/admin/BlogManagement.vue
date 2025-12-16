<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Pages Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage blog posts, categories, tags, and SEO settings</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Blog Post
      </button>
    </div>

    <!-- Website Switcher (for superadmins or when multiple websites available) -->
    <div v-if="canSelectWebsite && availableWebsites.length > 1" class="card p-4">
      <WebsiteSwitcher
        v-model="selectedWebsiteId"
        :websites="availableWebsites"
        :can-select-website="canSelectWebsite"
        :show-all-option="true"
        all-option-label="All Websites"
        label="Filter by Website"
        @change="handleWebsiteChange"
      />
    </div>

    <!-- Website Context Banner -->
    <WebsiteContextBanner
      v-if="selectedWebsite"
      :website="selectedWebsite"
      :stats="websiteStats"
    />

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200',
            activeTab === tab.id
              ? 'border-blue-500 dark:border-blue-400 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Blog Posts Tab -->
    <div v-if="activeTab === 'posts' || activeTab === 'my-drafts' || activeTab === 'needs-review' || activeTab === 'scheduled' || activeTab === 'stale'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4 dark:bg-gray-800 dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Category</label>
            <select
              v-model="filters.category"
              @change="loadBlogs"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option
                v-for="cat in filteredCategories"
                :key="cat.id"
                :value="cat.id"
              >
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
            <select
              v-model="filters.status"
              @change="loadBlogs"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Search by title..."
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Blog Posts Table -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200 dark:bg-gray-800 dark:border-gray-700">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="!blogs.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-2 text-sm font-medium">No blog posts found</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700" style="min-width: 1400px;">
            <thead class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-800 border-b-2 border-blue-200 dark:border-gray-600">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                    </svg>
                    ID
                  </div>
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Title
                  </div>
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    URL / Slug
                  </div>
                </th>
                <th
                  v-if="!selectedWebsiteId || canSelectWebsite"
                  class="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap"
                >
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    Website
                  </div>
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    Category
                  </div>
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    Tags
                  </div>
                </th>
                <th class="px-6 py-4 text-center text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center justify-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Status
                  </div>
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Author(s)
                  </div>
                </th>
                <th class="px-6 py-4 text-right text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center justify-end gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    Clicks
                  </div>
                </th>
                <th class="px-6 py-4 text-right text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center justify-end gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Conversions
                  </div>
                </th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Published
                  </div>
                </th>
                <th class="px-6 py-4 text-center text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">
                  <div class="flex items-center justify-center gap-2">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                    </svg>
                    Actions
                  </div>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="blog in blogs" :key="blog.id" class="hover:bg-blue-50/50 dark:hover:bg-gray-700/50 transition-all duration-150">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white text-xs font-bold">
                      #
                    </div>
                    <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">#{{ blog.id }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-base font-semibold text-gray-900 dark:text-gray-100" :title="blog.title">
                    {{ blog.title }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-mono text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 px-2 py-1 rounded border border-gray-200 dark:border-gray-600">
                      /{{ blog.slug }}
                    </span>
                    <button
                      @click="copyToClipboard(`/${blog.slug}`)"
                      class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                      title="Copy URL"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </td>
                <td
                  v-if="!selectedWebsiteId || canSelectWebsite"
                  class="px-6 py-4 whitespace-nowrap"
                >
                  <div v-if="blog.website" class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center text-white text-xs font-bold">
                      {{ blog.website.name.charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ blog.website.name }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">{{ blog.website.domain }}</div>
                    </div>
                  </div>
                  <span v-else class="text-gray-400 dark:text-gray-500">—</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold shadow-sm"
                        :class="blog.category ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'">
                    {{ blog.category?.name || 'Uncategorized' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1 max-w-xs">
                    <span
                      v-for="tag in (blog.tags || []).slice(0, 3)"
                      :key="tag.id || tag"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300"
                    >
                      {{ tag.name || tag }}
                    </span>
                    <span
                      v-if="blog.tags && blog.tags.length > 3"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400"
                    >
                      +{{ blog.tags.length - 3 }}
                    </span>
                    <span v-if="!blog.tags || blog.tags.length === 0" class="text-xs text-gray-400 dark:text-gray-500">—</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <span :class="getStatusBadgeClass(blog.is_published, blog.status)" 
                        class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold shadow-sm">
                    <span class="w-2 h-2 rounded-full mr-2" :class="getStatusDotClass(blog.is_published, blog.status)"></span>
                    {{ blog.is_published ? 'Published' : (blog.status || 'Draft') }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex flex-wrap gap-1 max-w-xs">
                    <span
                      v-for="(author, idx) in (blog.authors || []).slice(0, 2)"
                      :key="author.id || idx"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300"
                    >
                      {{ author.username || author.name || 'N/A' }}
                    </span>
                    <span
                      v-if="blog.authors && blog.authors.length > 2"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400"
                    >
                      +{{ blog.authors.length - 2 }}
                    </span>
                    <span v-if="!blog.authors || blog.authors.length === 0" class="text-xs text-gray-400 dark:text-gray-500">—</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="flex items-center justify-end gap-2">
                    <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ formatNumber(blog.click_count || blog.view_count || 0) }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="flex items-center justify-end gap-2">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <span class="text-sm font-semibold text-green-600 dark:text-green-400">{{ formatNumber(blog.conversion_count || 0) }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900 dark:text-gray-100">{{ formatDate(blog.publish_date || blog.created_at) }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">{{ formatTime(blog.publish_date || blog.created_at) }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center gap-2">
                    <button
                      @click="previewBlog(blog)"
                      class="px-3 py-1.5 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors text-xs font-semibold shadow-sm flex items-center gap-1"
                      title="Preview"
                    >
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      Preview
                    </button>
                    <button
                      @click="viewBlog(blog)"
                      class="px-3 py-1.5 bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors text-xs font-semibold shadow-sm"
                      title="View"
                    >
                      View
                    </button>
                    <button
                      @click="editBlog(blog)"
                      class="px-3 py-1.5 bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 rounded-lg hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors text-xs font-semibold shadow-sm"
                      title="Edit"
                    >
                      Edit
                    </button>
                    <div class="relative">
                      <button
                        @click="toggleActionsMenu(blog.id)"
                        class="px-3 py-1.5 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-xs font-semibold shadow-sm"
                        title="More actions"
                      >
                        ⋯
                      </button>
                      <div
                        v-if="actionsMenuOpen === blog.id"
                        class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg z-10 border border-gray-200 dark:border-gray-700"
                      >
                        <div class="py-1">
                          <button
                            @click="publishBlogAction(blog)"
                            v-if="!blog.is_published"
                            class="block w-full text-left px-4 py-2 text-sm text-green-600 dark:text-green-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            Publish
                          </button>
                          <button
                            @click="unpublishBlogAction(blog)"
                            v-else
                            class="block w-full text-left px-4 py-2 text-sm text-yellow-600 dark:text-yellow-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            Unpublish
                          </button>
                          <button
                            @click="viewSEO(blog)"
                            class="block w-full text-left px-4 py-2 text-sm text-purple-600 dark:text-purple-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            SEO Settings
                          </button>
                          <button
                            @click="viewRevisions(blog)"
                            class="block w-full text-left px-4 py-2 text-sm text-indigo-600 dark:text-indigo-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            Revisions
                          </button>
                          <button
                            @click="deleteBlogAction(blog)"
                            class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Categories Tab -->
    <div v-if="activeTab === 'categories'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Categories</h2>
        <button @click="showCategoryModal = true" class="btn btn-primary">Create Category</button>
      </div>
      
      <div class="card dark:bg-gray-800 dark:border-gray-700">
        <div v-if="categoriesLoading" class="text-center py-12 text-gray-500 dark:text-gray-400">Loading...</div>
        <div v-else-if="filteredCategories.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Slug</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Posts</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="cat in filteredCategories" :key="cat.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-gray-100">{{ cat.name }}</td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ cat.slug }}</td>
                <td class="px-6 py-4 text-gray-900 dark:text-gray-100">{{ cat.post_count || 0 }}</td>
                <td class="px-6 py-4">
                  <button @click="editCategory(cat)" class="text-blue-600 dark:text-blue-400 hover:underline mr-2">Edit</button>
                  <button @click="deleteCategory(cat.id)" class="text-red-600 dark:text-red-400 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500 dark:text-gray-400">No categories found.</div>
      </div>
    </div>

    <!-- Tags Tab -->
    <div v-if="activeTab === 'tags'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Tags</h2>
        <button @click="showTagModal = true" class="btn btn-primary">Create Tag</button>
      </div>
      
      <div class="card dark:bg-gray-800 dark:border-gray-700">
        <div v-if="tagsLoading" class="text-center py-12 text-gray-500 dark:text-gray-400">Loading...</div>
        <div v-else-if="filteredTags.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Slug</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Posts</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="tag in filteredTags" :key="tag.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-gray-100">{{ tag.name }}</td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ tag.slug }}</td>
                <td class="px-6 py-4 text-gray-900 dark:text-gray-100">{{ tag.post_count || 0 }}</td>
                <td class="px-6 py-4">
                  <button @click="editTag(tag)" class="text-blue-600 dark:text-blue-400 hover:underline mr-2">Edit</button>
                  <button @click="deleteTag(tag.id)" class="text-red-600 dark:text-red-400 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500 dark:text-gray-400">No tags found.</div>
      </div>
    </div>

    <!-- Create/Edit Blog Modal -->
    <div v-if="showCreateModal || editingBlog" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ editingBlog ? 'Edit Blog Post' : 'Create Blog Post' }}</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ editingBlog ? 'Update your blog post content and settings' : 'Create a new blog post with rich content' }}</p>
            </div>
            <button 
              @click="closeModal" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="saveBlog" class="space-y-6">
            <!-- Basic Information Section -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Basic Information</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Website <span class="text-red-500">*</span>
                  </label>
                  <select 
                    v-model="blogForm.website_id" 
                    @change="onWebsiteChange"
                    :disabled="!canSelectWebsite || availableWebsites.length === 0"
                    required
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <option value="">Select Website</option>
                    <option v-for="website in availableWebsites" :key="website.id" :value="website.id">
                      {{ formatWebsiteName(website) }}
                    </option>
                  </select>
                  <p v-if="!canSelectWebsite && availableWebsites.length === 0" class="text-xs text-gray-500 dark:text-gray-400 mt-1">No websites available</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Title <span class="text-red-500">*</span>
                  </label>
                  <input 
                    v-model="blogForm.title" 
                    type="text" 
                    required 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="Enter blog post title"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Slug</label>
                  <input 
                    v-model="blogForm.slug" 
                    type="text" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="auto-generated-from-title"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Leave empty to auto-generate from title</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category</label>
                  <select 
                    v-model="blogForm.category_id" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  >
                    <option value="">Select Category</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
                  <select 
                    v-model="blogForm.status" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  >
                    <option value="draft">Draft</option>
                    <option value="published">Published</option>
                    <option value="archived">Archived</option>
                  </select>
                </div>
              </div>
            </div>
            
            <!-- Content Organization Section -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Content Organization</h3>
              
              <!-- Authors Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Authors / Personas</label>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span
                    v-for="author in selectedAuthors"
                    :key="author.id"
                    class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300"
                  >
                    <img 
                      v-if="author.profile_picture" 
                      :src="author.profile_picture" 
                      :alt="author.name"
                      class="w-5 h-5 rounded-full mr-2 object-cover"
                    />
                    {{ author.name }}
                    <span v-if="author.designation" class="ml-1 text-xs text-purple-600 dark:text-purple-400">({{ author.designation }})</span>
                    <button
                      type="button"
                      @click="removeAuthor(author.id)"
                      class="ml-2 text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-200 transition-colors"
                      title="Remove author"
                    >
                      ×
                    </button>
                  </span>
                </div>
                <select
                  v-model="authorSelect"
                  @change="addAuthor"
                  :disabled="!blogForm.website_id || authorsLoading"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <option value="">{{ blogForm.website_id ? (authorsLoading ? 'Loading authors...' : 'Select an author...') : 'Select a website first' }}</option>
                  <option
                    v-for="author in availableAuthorsList"
                    :key="author.id"
                    :value="author.id"
                  >
                    {{ author.name }} {{ author.designation ? `(${author.designation})` : '' }}
                  </option>
                </select>
                <p v-if="!blogForm.website_id" class="text-xs text-gray-500 dark:text-gray-400 mt-1">Please select a website first to see available authors</p>
              </div>
              
              <!-- Tags Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tags</label>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span
                    v-for="tag in selectedTags"
                    :key="tag.id"
                    class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
                  >
                    {{ tag.name }}
                    <button
                      type="button"
                      @click="removeTag(tag.id)"
                      class="ml-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors"
                      title="Remove tag"
                    >
                      ×
                    </button>
                  </span>
                </div>
                <div class="flex gap-2">
                  <select
                    v-model="tagSelect"
                    @change="addTag"
                    class="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  >
                    <option value="">Add a tag...</option>
                    <option
                      v-for="tag in availableTags"
                      :key="tag.id"
                      :value="tag.id"
                    >
                      {{ tag.name }}
                    </option>
                  </select>
                  <button
                    type="button"
                    @click="showTagModal = true"
                    class="px-4 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    + New Tag
                  </button>
                </div>
              </div>
              
              <!-- Featured Image -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Featured Image</label>
                <MediaPicker
                  v-model="blogForm.featured_image_asset"
                  :website-id="blogForm.website_id"
                  :accept-types="'image/*'"
                  trigger-label="Select Featured Image"
                  modal-title="Select Featured Image"
                  trigger-class="px-4 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors"
                  @selected="handleFeaturedImageSelected"
                />
                <div v-if="blogForm.featured_image || blogForm.featured_image_asset" class="mt-3">
                  <div class="relative inline-block">
                    <img
                      :src="blogForm.featured_image || blogForm.featured_image_asset?.url"
                      alt="Featured image preview"
                      class="w-40 h-40 object-cover rounded-lg border-2 border-gray-200 dark:border-gray-700"
                    />
                    <button
                      type="button"
                      @click="removeFeaturedImage"
                      class="absolute top-2 right-2 px-2 py-1 text-xs font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Editor Toolbar -->
            <EditorToolbar
              v-if="blogForm.website_id"
              :website-id="blogForm.website_id"
              content-type="blog_post"
              :editor-instance="editorInstance"
              :current-content="blogForm.content"
              :meta-title="blogForm.meta_title"
              :meta-description="blogForm.meta_description"
              :slug="blogForm.slug"
              @content-inserted="handleContentInserted"
              @template-applied="handleTemplateApplied"
              @template-used="handleTemplateUsed"
              @snippet-used="handleSnippetUsed"
              @block-used="handleBlockUsed"
              @health-check="handleHealthCheck"
              @health-check-run="handleHealthCheckRun"
            />

            <!-- Editor Session Tracker (hidden, tracks usage) -->
            <EditorSessionTracker
              v-if="blogForm.website_id && editingBlog?.id"
              :website-id="blogForm.website_id"
              content-type="blog_post"
              :content-id="editingBlog.id"
              ref="sessionTrackerRef"
            />

            <!-- Content Section -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Blog Content</h3>
              
              <!-- Editor Toolbar -->
              <EditorToolbar
                v-if="blogForm.website_id"
                :website-id="blogForm.website_id"
                content-type="blog_post"
                :editor-instance="editorInstance"
                :current-content="blogForm.content"
                :meta-title="blogForm.meta_title"
                :meta-description="blogForm.meta_description"
                :slug="blogForm.slug"
                @content-inserted="handleContentInserted"
                @template-applied="handleTemplateApplied"
                @template-used="handleTemplateUsed"
                @snippet-used="handleSnippetUsed"
                @block-used="handleBlockUsed"
                @health-check="handleHealthCheck"
                @health-check-run="handleHealthCheckRun"
              />

              <!-- Editor Session Tracker (hidden, tracks usage) -->
              <EditorSessionTracker
                v-if="blogForm.website_id && editingBlog?.id"
                :website-id="blogForm.website_id"
                content-type="blog_post"
                :content-id="editingBlog.id"
                ref="sessionTrackerRef"
              />

              <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div class="lg:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Content <span class="text-red-500">*</span>
                  </label>
                  <RichTextEditor
                    ref="editorRef"
                    v-model="blogForm.content"
                    :required="true"
                    placeholder="Write your blog post content..."
                    toolbar="full"
                    height="400px"
                    :allow-images="true"
                  />
                </div>
                <div class="lg:col-span-1">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Internal Linking</label>
                  <InternalLinkingWidget
                    :content="blogForm.content"
                    :website-id="blogForm.website_id"
                    :current-post-id="editingBlog?.id"
                    content-type="blog"
                    :editor-instance="editorInstance"
                    @link-inserted="handleLinkInserted"
                  />
                </div>
              </div>
            </div>
            
            <!-- SEO Settings Section -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">SEO Settings</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Meta Title</label>
                  <input 
                    v-model="blogForm.meta_title" 
                    type="text" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="SEO meta title (50-60 chars)"
                    maxlength="60"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ blogForm.meta_title?.length || 0 }}/60 characters</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Meta Description</label>
                  <textarea 
                    v-model="blogForm.meta_description" 
                    rows="3" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="SEO meta description (150-160 chars)"
                    maxlength="160"
                  ></textarea>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ blogForm.meta_description?.length || 0 }}/160 characters</p>
                </div>
              </div>
            </div>
            
            <!-- FAQs Section -->
            <div class="space-y-4 border-t border-gray-200 dark:border-gray-700 pt-6">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">FAQs (Optional)</h3>
                <button
                  type="button"
                  @click="addFAQ"
                  class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Add FAQ
                </button>
              </div>
              <div v-if="blogForm.faqs_data && blogForm.faqs_data.length" class="space-y-4">
                <div
                  v-for="(faq, index) in blogForm.faqs_data"
                  :key="index"
                  class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50"
                >
                  <div class="flex justify-between items-start mb-3">
                    <span class="text-sm font-semibold text-gray-900 dark:text-white">FAQ {{ index + 1 }}</span>
                    <button
                      type="button"
                      @click="removeFAQ(index)"
                      class="px-3 py-1 text-xs font-medium text-red-600 bg-red-50 dark:bg-red-900/20 rounded-md hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                    >
                      Remove
                    </button>
                  </div>
                  <div class="space-y-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Question <span class="text-red-500">*</span>
                      </label>
                      <input
                        v-model="faq.question"
                        type="text"
                        required
                        placeholder="Enter question..."
                        class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Answer <span class="text-red-500">*</span>
                      </label>
                      <textarea
                        v-model="faq.answer"
                        rows="3"
                        required
                        placeholder="Enter answer..."
                        class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-sm"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <p class="text-sm">No FAQs added yet. Click "Add FAQ" to get started.</p>
              </div>
            </div>
            
            <!-- Resources Section -->
            <div class="space-y-4 border-t border-gray-200 dark:border-gray-700 pt-6">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Resources (Optional)</h3>
                <button
                  type="button"
                  @click="addResource"
                  class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Add Resource
                </button>
              </div>
              <div v-if="blogForm.resources_data && blogForm.resources_data.length" class="space-y-4">
                <div
                  v-for="(resource, index) in blogForm.resources_data"
                  :key="index"
                  class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50"
                >
                  <div class="flex justify-between items-start mb-3">
                    <span class="text-sm font-semibold text-gray-900 dark:text-white">Resource {{ index + 1 }}</span>
                    <button
                      type="button"
                      @click="removeResource(index)"
                      class="px-3 py-1 text-xs font-medium text-red-600 bg-red-50 dark:bg-red-900/20 rounded-md hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                    >
                      Remove
                    </button>
                  </div>
                  <div class="space-y-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Title <span class="text-red-500">*</span>
                      </label>
                      <input
                        v-model="resource.title"
                        type="text"
                        required
                        placeholder="Resource title..."
                        class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        URL <span class="text-red-500">*</span>
                      </label>
                      <input
                        v-model="resource.url"
                        type="url"
                        required
                        placeholder="https://example.com"
                        class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
                      <textarea
                        v-model="resource.description"
                        rows="2"
                        placeholder="Resource description..."
                        class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-sm"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <p class="text-sm">No resources added yet. Click "Add Resource" to get started.</p>
              </div>
            </div>
            
            <!-- Content Blocks Section -->
            <div class="space-y-4 border-t border-gray-200 dark:border-gray-700 pt-6">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Content Blocks</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Add rich content blocks (tables, info boxes, timelines, etc.) to make your blog post unique and information-rich</p>
                </div>
                <button
                  type="button"
                  @click="openAddContentBlockModal"
                  class="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Insert Content Block
                </button>
              </div>
              
              <div v-if="contentBlocksLoading" class="text-center py-8">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
              </div>
              <div v-else-if="allContentBlocks.length > 0" class="space-y-3">
                <div
                  v-for="block in allContentBlocks"
                  :key="block.id || block.tempId"
                  class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50"
                >
                  <div class="flex justify-between items-start mb-3">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-1">
                        <span class="text-sm font-semibold text-gray-900 dark:text-white">
                          {{ getBlockTemplateName(block) }}
                        </span>
                        <span v-if="block.tempId" class="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 rounded-full">
                          Pending
                        </span>
                        <span v-else class="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded-full">
                          {{ formatBlockType(block.block_type || block.template?.block_type) }}
                        </span>
                      </div>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Position: {{ block.position || 0 }} | 
                        <span :class="block.is_active !== false ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                          {{ block.is_active !== false ? 'Active' : 'Inactive' }}
                        </span>
                      </p>
                    </div>
                    <div class="flex gap-2">
                      <button
                        type="button"
                        @click="editContentBlock(block)"
                        class="px-3 py-1 text-xs font-medium text-primary-600 bg-primary-50 dark:bg-primary-900/20 rounded-md hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        @click="removeContentBlock(block)"
                        class="px-3 py-1 text-xs font-medium text-red-600 bg-red-50 dark:bg-red-900/20 rounded-md hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <p class="text-sm mb-2">No content blocks added yet.</p>
                <p class="text-xs">Click "Insert Content Block" to add tables, info boxes, timelines, and more to make your blog post unique and information-rich.</p>
                <button
                  type="button"
                  @click="openAddContentBlockModal"
                  class="mt-4 px-4 py-2 text-sm font-medium text-purple-600 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
                >
                  Get Started
                </button>
              </div>
            </div>
          </form>
        </div>
        
        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-end gap-3">
          <button 
            type="button" 
            @click="closeModal" 
            class="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            @click="saveBlog"
            :disabled="saving"
            class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
            {{ saving ? 'Saving...' : (editingBlog ? 'Update Blog Post' : 'Create Blog Post') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Category Modal -->
    <div v-if="showCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeCategoryModal">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-green-50 to-emerald-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ editingCategory ? 'Edit Category' : 'Create Category' }}</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ editingCategory ? 'Update category information' : 'Create a new blog category' }}</p>
            </div>
            <button 
              @click="closeCategoryModal" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="saveCategory" class="space-y-6">
            <!-- Basic Information -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Basic Information</h3>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Name <span class="text-red-500">*</span>
                </label>
                <input 
                  v-model="categoryForm.name" 
                  type="text" 
                  required 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="Enter category name"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
                <textarea 
                  v-model="categoryForm.description" 
                  rows="3" 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="Category description (optional)"
                ></textarea>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Website <span class="text-red-500">*</span>
                  </label>
                  <select
                    v-model="categoryForm.website"
                    required
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  >
                    <option value="">Select Website</option>
                    <option v-for="website in availableWebsites" :key="website.id" :value="website.id">
                      {{ formatWebsiteName(website) }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Display Order</label>
                  <input 
                    v-model.number="categoryForm.display_order" 
                    type="number" 
                    min="0"
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="0"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Lower numbers appear first</p>
                </div>
              </div>
            </div>
            
            <!-- SEO Settings -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">SEO Settings</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Meta Title</label>
                  <input 
                    v-model="categoryForm.meta_title" 
                    type="text" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="SEO meta title"
                    maxlength="60"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ categoryForm.meta_title?.length || 0 }}/60 characters</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Meta Description</label>
                  <textarea 
                    v-model="categoryForm.meta_description" 
                    rows="2" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="SEO meta description"
                    maxlength="160"
                  ></textarea>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ categoryForm.meta_description?.length || 0 }}/160 characters</p>
                </div>
              </div>
            </div>
            
            <!-- Settings -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Settings</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <input
                    v-model="categoryForm.is_featured"
                    type="checkbox"
                    id="category_featured"
                    class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label for="category_featured" class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Featured
                  </label>
                  <p class="ml-auto text-xs text-gray-500 dark:text-gray-400">Show on homepage</p>
                </div>
                <div class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <input
                    v-model="categoryForm.is_active"
                    type="checkbox"
                    id="category_active"
                    class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label for="category_active" class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Active
                  </label>
                  <p class="ml-auto text-xs text-gray-500 dark:text-gray-400">Category is visible</p>
                </div>
              </div>
            </div>
            
            <!-- Form Footer -->
            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button 
                type="button" 
                @click="closeCategoryModal" 
                class="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button 
                type="submit"
                class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
              >
                {{ editingCategory ? 'Update Category' : 'Create Category' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Tag Modal -->
    <div v-if="showTagModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeTagModal">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-pink-50 to-rose-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ editingTag ? 'Edit Tag' : 'Create Tag' }}</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ editingTag ? 'Update tag information' : 'Create a new blog tag' }}</p>
            </div>
            <button 
              @click="closeTagModal" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="saveTag" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Name <span class="text-red-500">*</span>
              </label>
              <input 
                v-model="tagForm.name" 
                type="text" 
                required 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder="Enter tag name"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Tag name will be used to create a URL-friendly slug</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Website <span class="text-red-500">*</span>
              </label>
              <select
                v-model="tagForm.website"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              >
                <option value="">Select Website</option>
                <option v-for="website in availableWebsites" :key="website.id" :value="website.id">
                  {{ formatWebsiteName(website) }}
                </option>
              </select>
            </div>
            
            <!-- Form Footer -->
            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button 
                type="button" 
                @click="closeTagModal" 
                class="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button 
                type="submit"
                class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
              >
                {{ editingTag ? 'Update Tag' : 'Create Tag' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Revision Diff Modal -->
    <div v-if="showRevisionDiffModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">Compare Revisions</h2>
            <button @click="showRevisionDiffModal = false" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <div v-if="revisionDiffLoading && !revisionDiffData" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          
          <div v-else-if="revisionDiffData" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Select Revision to Compare</label>
              <select 
                v-model="revisionDiffData.selectedRevisionId" 
                @change="loadRevisionDiff(revisionDiffData.selectedRevisionId)"
                class="w-full border rounded px-3 py-2"
              >
                <option value="">Select a revision...</option>
                <option 
                  v-for="rev in revisionDiffData.revisions" 
                  :key="rev.id" 
                  :value="rev.id"
                >
                  Revision #{{ rev.revision_number }} - {{ formatDate(rev.created_at) }}
                </option>
              </select>
            </div>
            
            <div v-if="revisionDiffData.diff" class="border rounded p-4">
              <h3 class="font-semibold mb-2">Differences</h3>
              <div class="space-y-2">
                <div v-for="(diff, index) in revisionDiffData.diff.diffs" :key="index" class="border-b pb-2">
                  <div class="font-medium text-sm text-gray-700 mb-1">{{ diff.field }}</div>
                  <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div class="text-xs text-gray-500 mb-1">Current</div>
                      <div class="bg-red-50 p-2 rounded">{{ diff.current || '(empty)' }}</div>
                    </div>
                    <div>
                      <div class="text-xs text-gray-500 mb-1">Revision</div>
                      <div class="bg-green-50 p-2 rounded">{{ diff.revision || '(empty)' }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else-if="revisionDiffData.selectedRevisionId" class="text-center py-8 text-gray-500">
              Select a revision to see differences
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>

    <!-- Content Preview Modal -->
    <ContentPreview
      v-model:show="showPreviewModal"
      :content-type="previewContentType"
      :content-id="previewContentId"
      :content-slug="previewContentSlug"
      :website-id="previewWebsiteId"
      @close="showPreviewModal = false"
    />

    <!-- Content Block Modal -->
    <div v-if="showContentBlockModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="showContentBlockModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">
              {{ editingContentBlock ? 'Edit Content Block' : 'Insert Content Block' }}
            </h2>
            <button 
              @click="showContentBlockModal = false" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Template *</label>
              <select
                v-model.number="contentBlockForm.template"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select Template</option>
                <option v-for="template in contentBlockTemplates" :key="template.id" :value="template.id">
                  {{ template.name }} ({{ formatBlockType(template.block_type) }})
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Position *</label>
              <input
                v-model.number="contentBlockForm.position"
                type="number"
                min="0"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="0 (paragraph/heading index)"
              />
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Position in content where block should appear (0 = top, 1 = after first paragraph, etc.)</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Custom Data (JSON)</label>
              <textarea
                v-model="contentBlockCustomDataJson"
                rows="4"
                class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono text-sm"
                placeholder='{"key": "value"}'
              ></textarea>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Blog-specific data overriding template data</p>
            </div>
            <div>
              <label class="flex items-center gap-2">
                <input
                  v-model="contentBlockForm.is_active"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
              </label>
            </div>
          </div>
        </div>
        
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-end gap-3">
          <button 
            @click="showContentBlockModal = false" 
            class="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="saveContentBlock"
            class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
          >
            {{ editingContentBlock ? 'Update' : 'Insert' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import InternalLinkingWidget from '@/components/blog/InternalLinkingWidget.vue'
import MediaPicker from '@/components/media/MediaPicker.vue'
import EditorToolbar from '@/components/editor/EditorToolbar.vue'
import EditorSessionTracker from '@/components/editor/EditorSessionTracker.vue'
import WebsiteSwitcher from '@/components/common/WebsiteSwitcher.vue'
import WebsiteContextBanner from '@/components/common/WebsiteContextBanner.vue'
import EnhancedDataTable from '@/components/common/EnhancedDataTable.vue'
import ContentPreview from '@/components/content/ContentPreview.vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { getErrorMessage } from '@/utils/errorHandler'
import { formatWebsiteName } from '@/utils/formatDisplay'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const activeTab = ref('posts')
const tabs = [
  { id: 'posts', label: 'Blog Posts' },
  { id: 'my-drafts', label: 'My Drafts' },
  { id: 'needs-review', label: 'Needs Review' },
  { id: 'scheduled', label: 'Scheduled' },
  { id: 'stale', label: 'Stale Published' },
  { id: 'categories', label: 'Categories' },
  { id: 'tags', label: 'Tags' },
]

const blogs = ref([])
const categories = ref([])
const tags = ref([])
const loading = ref(false)
const categoriesLoading = ref(false)
const tagsLoading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const showCategoryModal = ref(false)
const showTagModal = ref(false)
const editingBlog = ref(null)
const actionsMenuOpen = ref(null)

// Website and Author selection
const availableWebsites = ref([])
const canSelectWebsite = ref(false)
const selectedWebsiteId = ref(null)
const availableAuthors = ref([])
const authorsLoading = ref(false)
const selectedAuthors = ref([])
const authorSelect = ref('')

const filters = ref({
  category: '',
  status: '',
  search: '',
})

// Computed: Selected website object
const selectedWebsite = computed(() => {
  if (!selectedWebsiteId.value) return null
  return availableWebsites.value.find(w => w.id === selectedWebsiteId.value) || null
})

// Computed: Website stats
const websiteStats = computed(() => {
  if (!selectedWebsite.value) return null
  
  const websiteBlogs = blogs.value.filter(b => 
    b.website?.id === selectedWebsite.value.id || b.website_id === selectedWebsite.value.id
  )
  
  return {
    totalPosts: websiteBlogs.length,
    publishedPosts: websiteBlogs.filter(b => b.is_published).length,
    draftPosts: websiteBlogs.filter(b => !b.is_published && b.status === 'draft').length,
    totalCategories: filteredCategories.value.length,
    activeCategories: filteredCategories.value.filter(c => c.is_active !== false).length,
    totalAuthors: availableAuthors.value.length,
  }
})

// Computed: Filtered categories by selected website
const filteredCategories = computed(() => {
  if (!selectedWebsiteId.value) return categories.value
  return categories.value.filter(cat => 
    cat.website?.id === selectedWebsiteId.value || cat.website_id === selectedWebsiteId.value
  )
})

// Computed: Filtered tags by selected website
const filteredTags = computed(() => {
  if (!selectedWebsiteId.value) return tags.value
  return tags.value.filter(tag => 
    tag.website?.id === selectedWebsiteId.value || tag.website_id === selectedWebsiteId.value
  )
})

const blogForm = ref({
  website_id: null,
  title: '',
  slug: '',
  content: '',
  category_id: null,
  tag_ids: [],
  author_ids: [],
  status: 'draft',
  meta_title: '',
  meta_description: '',
  faqs_data: [],
  resources_data: [],
  featured_image: null,
  featured_image_asset: null,
})

const selectedTags = ref([])
const tagSelect = ref('')
const editingCategory = ref(null)
const editingTag = ref(null)
const categoryForm = ref({
  name: '',
  description: '',
  website: '',
  display_order: 0,
  is_featured: false,
  is_active: true,
  meta_title: '',
  meta_description: '',
})
const tagForm = ref({
  name: '',
  website: '',
})

const message = ref('')
const messageSuccess = ref(false)
const editorRef = ref(null)
const editorInstance = ref(null)
const sessionTrackerRef = ref(null)

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadBlogs()
  }, 500)
}

const loadBlogs = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.status) params.is_published = filters.value.status === 'published'
    if (filters.value.search) params.search = filters.value.search
    
    // Add website filter if a specific website is selected
    if (selectedWebsiteId.value) {
      params.website_id = selectedWebsiteId.value
    }
    
    let res
    // Use editorial workflow filters based on active tab
    if (activeTab.value === 'my-drafts') {
      res = await blogPagesAPI.getMyDrafts(params)
    } else if (activeTab.value === 'needs-review') {
      res = await blogPagesAPI.getNeedsReview(params)
    } else if (activeTab.value === 'scheduled') {
      res = await blogPagesAPI.getScheduled(params)
    } else if (activeTab.value === 'stale') {
      res = await blogPagesAPI.getStalePublished(params)
    } else {
      res = await blogPagesAPI.listBlogs(params)
    }
    
    blogs.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    message.value = 'Failed to load blogs: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  categoriesLoading.value = true
  try {
    const params = {}
    // Filter categories by selected website
    if (selectedWebsiteId.value) {
      params.website_id = selectedWebsiteId.value
    }
    const res = await blogPagesAPI.listCategories(params)
    categories.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load categories:', e)
  } finally {
    categoriesLoading.value = false
  }
}

const loadTags = async () => {
  tagsLoading.value = true
  try {
    const res = await blogPagesAPI.listTags({})
    tags.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load tags:', e)
  } finally {
    tagsLoading.value = false
  }
}

const loadAvailableWebsites = async () => {
  try {
    const res = await blogPagesAPI.getAvailableWebsites()
    availableWebsites.value = res.data?.websites || []
    canSelectWebsite.value = res.data?.can_select_website || false
    
    // Auto-select website if only one available or if user can't select
    if (availableWebsites.value.length === 1) {
      selectedWebsiteId.value = availableWebsites.value[0].id
      if (!blogForm.value.website_id) {
        blogForm.value.website_id = availableWebsites.value[0].id
        await loadAvailableAuthors(availableWebsites.value[0].id)
      }
    } else if (!canSelectWebsite.value && availableWebsites.value.length > 0) {
      // Regular admin: auto-select their assigned website
      selectedWebsiteId.value = availableWebsites.value[0].id
    }
  } catch (e) {
    console.error('Failed to load available websites:', e)
  }
}

const handleWebsiteChange = (websiteId) => {
  selectedWebsiteId.value = websiteId
  // Reload blogs and categories for the selected website
  loadBlogs()
  loadCategories()
  // Load authors for the selected website
  if (websiteId) {
    loadAvailableAuthors(websiteId)
  }
}

const loadAvailableAuthors = async (websiteId) => {
  if (!websiteId) {
    availableAuthors.value = []
    return
  }
  
  authorsLoading.value = true
  try {
    const res = await blogPagesAPI.getAvailableAuthors(websiteId)
    availableAuthors.value = res.data?.authors || []
  } catch (e) {
    console.error('Failed to load available authors:', e)
    message.value = 'Failed to load authors: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    authorsLoading.value = false
  }
}

const onWebsiteChange = async () => {
  // Clear selected authors when website changes
  selectedAuthors.value = []
  blogForm.value.author_ids = []
  
  // Load authors for the selected website
  if (blogForm.value.website_id) {
    await loadAvailableAuthors(blogForm.value.website_id)
  } else {
    availableAuthors.value = []
  }
}

const addAuthor = () => {
  if (!authorSelect.value) return
  const author = availableAuthors.value.find(a => a.id === parseInt(authorSelect.value))
  if (author && !selectedAuthors.value.find(a => a.id === author.id)) {
    selectedAuthors.value.push(author)
    blogForm.value.author_ids = selectedAuthors.value.map(a => a.id)
  }
  authorSelect.value = ''
}

const removeAuthor = (authorId) => {
  selectedAuthors.value = selectedAuthors.value.filter(a => a.id !== authorId)
  blogForm.value.author_ids = selectedAuthors.value.map(a => a.id)
}

const handleFeaturedImageSelected = (asset) => {
  blogForm.value.featured_image_asset = asset
  blogForm.value.featured_image = asset?.url || null
}

const removeFeaturedImage = () => {
  blogForm.value.featured_image_asset = null
  blogForm.value.featured_image = null
}

const saveBlog = async () => {
  saving.value = true
  message.value = ''
  try {
    const formData = { ...blogForm.value }
    // Include featured_image URL if asset is selected
    if (formData.featured_image_asset?.url) {
      formData.featured_image = formData.featured_image_asset.url
    }
    
    let createdBlogId = null
    if (editingBlog.value) {
      await blogPagesAPI.updateBlog(editingBlog.value.id, formData)
      message.value = 'Blog post updated successfully'
      createdBlogId = editingBlog.value.id
    } else {
      const response = await blogPagesAPI.createBlog(formData)
      createdBlogId = response.data?.id || response.data?.id
      message.value = 'Blog post created successfully'
      
      // Save pending content blocks if any
      if (pendingContentBlocks.value.length > 0 && createdBlogId) {
        try {
          for (const pendingBlock of pendingContentBlocks.value) {
            const blockData = {
              ...pendingBlock,
              blog: createdBlogId,
            }
            // Remove tempId before sending
            delete blockData.tempId
            await blogPagesAPI.createBlogContentBlock(blockData)
          }
          message.value = `Blog post created successfully with ${pendingContentBlocks.value.length} content block(s)`
          pendingContentBlocks.value = []
        } catch (blockError) {
          console.error('Error saving pending content blocks:', blockError)
          // Don't fail the whole operation, just log the error
          message.value = 'Blog post created, but some content blocks failed to save'
        }
      }
    }
    
    messageSuccess.value = true
    
    // If we created a new blog, reload it to get the ID and load content blocks
    if (createdBlogId && !editingBlog.value) {
      await loadBlogs()
      // Find the newly created blog and load its content blocks
      const newBlog = blogs.value.find(b => b.id === createdBlogId)
      if (newBlog) {
        await loadBlogContentBlocks(createdBlogId)
      }
    }
    
    closeModal()
    await loadBlogs()
  } catch (e) {
    message.value = 'Failed to save blog: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data))
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const editBlog = async (blog) => {
  editingBlog.value = blog
  blogForm.value = {
    website_id: blog.website?.id || null,
    title: blog.title || '',
    slug: blog.slug || '',
    content: blog.content || '',
    category_id: blog.category?.id || null,
    tag_ids: blog.tags?.map(t => t.id) || [],
    author_ids: blog.authors?.map(a => a.id) || [],
    status: blog.status || 'draft',
    meta_title: blog.meta_title || '',
    meta_description: blog.meta_description || '',
    faqs_data: blog.faqs?.map(faq => ({
      question: faq.question || '',
      answer: faq.answer || ''
    })) || [],
    resources_data: blog.resources?.map(resource => ({
      title: resource.title || '',
      url: resource.url || '',
      description: resource.description || ''
    })) || [],
    featured_image: blog.featured_image || null,
    featured_image_asset: blog.featured_image ? { url: blog.featured_image } : null,
  }
  selectedTags.value = blog.tags || []
  selectedAuthors.value = blog.authors || []
  
  // Load authors for the blog's website
  if (blogForm.value.website_id) {
    await loadAvailableAuthors(blogForm.value.website_id)
  }
  
  // Load content blocks for this blog
  if (blog.id) {
    await loadBlogContentBlocks(blog.id)
    await loadContentBlockTemplates()
  }
  
  showCreateModal.value = true
}

const addTag = () => {
  if (!tagSelect.value) return
  const tag = tags.value.find(t => t.id === parseInt(tagSelect.value))
  if (tag && !selectedTags.value.find(t => t.id === tag.id)) {
    selectedTags.value.push(tag)
    blogForm.value.tag_ids = selectedTags.value.map(t => t.id)
  }
  tagSelect.value = ''
}

const removeTag = (tagId) => {
  selectedTags.value = selectedTags.value.filter(t => t.id !== tagId)
  blogForm.value.tag_ids = selectedTags.value.map(t => t.id)
}

const availableTags = computed(() => {
  return tags.value.filter(tag => !selectedTags.value.find(st => st.id === tag.id))
})

const availableAuthorsList = computed(() => {
  return availableAuthors.value.filter(author => !selectedAuthors.value.find(sa => sa.id === author.id))
})

const viewBlog = (blog) => {
  // Navigate to public blog view
  if (blog.slug) {
    window.open(`/blog/${blog.slug}`, '_blank')
  } else {
    showError('Blog slug not available')
  }
}

const showPreviewModal = ref(false)
const previewContentType = ref(null)
const previewContentId = ref(null)
const previewContentSlug = ref(null)
const previewWebsiteId = ref(null)

const previewBlog = (blog) => {
  previewContentType.value = 'blog'
  previewContentId.value = blog.id
  previewContentSlug.value = blog.slug
  previewWebsiteId.value = blog.website?.id || null
  showPreviewModal.value = true
}

const publishBlogAction = async (blog) => {
  try {
    await blogPagesAPI.publishBlog(blog.id)
    showSuccess('Blog post published successfully')
    await loadBlogs()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to publish blog post. Please try again.')
    showError(errorMsg)
  }
  actionsMenuOpen.value = null
}

const unpublishBlogAction = async (blog) => {
  try {
    await blogPagesAPI.unpublishBlog(blog.id)
    showSuccess('Blog post unpublished successfully')
    await loadBlogs()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to unpublish blog post. Please try again.')
    showError(errorMsg)
  }
  actionsMenuOpen.value = null
}

const viewSEO = (blog) => {
  // Open edit modal with SEO section focused
  editBlog(blog)
  showSuccess('Use the edit form to manage SEO settings for this blog post')
}

const viewRevisions = (blog) => {
  // Open revisions modal if available
  viewRevisionDiff(blog)
}

const showRevisionDiffModal = ref(false)
const revisionDiffData = ref(null)
const revisionDiffLoading = ref(false)

// Content Blocks Management
const blogContentBlocks = ref([])
const pendingContentBlocks = ref([]) // For blocks added before blog is saved
const contentBlocksLoading = ref(false)
const showContentBlockModal = ref(false)
const editingContentBlock = ref(null)
const contentBlockTemplates = ref([])
const contentBlockForm = ref({
  template: null,
  position: 0,
  custom_data: {},
  is_active: true,
})
const contentBlockCustomDataJson = ref('{}')

// Computed: Combine pending and saved blocks
const allContentBlocks = computed(() => {
  return [...pendingContentBlocks.value, ...blogContentBlocks.value]
})

// Helper to get template name
const getBlockTemplateName = (block) => {
  if (block.template_name) return block.template_name
  if (block.template?.name) return block.template.name
  if (block.template) {
    const template = contentBlockTemplates.value.find(t => t.id === block.template)
    return template?.name || 'Content Block'
  }
  return 'Content Block'
}

const viewRevisionDiff = async (blog) => {
  showRevisionDiffModal.value = true
  revisionDiffLoading.value = true
  revisionDiffData.value = null
  
  try {
    // First, get list of revisions to show in selector
    const revisionsRes = await blogPagesAPI.listRevisions({ blog: blog.id })
    revisionDiffData.value = {
      blog,
      revisions: revisionsRes.data?.results || revisionsRes.data || [],
      selectedRevisionId: null,
      diff: null
    }
  } catch (e) {
    message.value = 'Failed to load revisions: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    revisionDiffLoading.value = false
  }
  actionsMenuOpen.value = null
}

const loadRevisionDiff = async (revisionId) => {
  if (!revisionDiffData.value?.blog) return
  
  revisionDiffLoading.value = true
  try {
    const res = await blogPagesAPI.getRevisionDiff(revisionDiffData.value.blog.id, { revision_id: revisionId })
    revisionDiffData.value.diff = res.data
  } catch (e) {
    message.value = 'Failed to load diff: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    revisionDiffLoading.value = false
  }
}

const deleteBlogAction = async (blog) => {
  const confirmed = await confirm.showDestructive(
    `Delete "${blog.title}"?`,
    'Delete Blog Post',
    {
      details: 'This action cannot be undone. The blog post will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteBlog(blog.id)
    message.value = 'Blog post deleted'
    messageSuccess.value = true
    await loadBlogs()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const editCategory = (cat) => {
  editingCategory.value = cat
  categoryForm.value = {
    name: cat.name || '',
    description: cat.description || '',
    website: cat.website || '',
    display_order: cat.display_order || 0,
    is_featured: cat.is_featured || false,
    is_active: cat.is_active !== undefined ? cat.is_active : true,
    meta_title: cat.meta_title || '',
    meta_description: cat.meta_description || '',
  }
  showCategoryModal.value = true
}

const saveCategory = async () => {
  try {
    if (editingCategory.value) {
      await blogPagesAPI.updateCategory(editingCategory.value.id, categoryForm.value)
      message.value = 'Category updated successfully'
    } else {
      await blogPagesAPI.createCategory(categoryForm.value)
      message.value = 'Category created successfully'
    }
    messageSuccess.value = true
    closeCategoryModal()
    await loadCategories()
  } catch (e) {
    message.value = 'Failed to save category: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data))
    messageSuccess.value = false
  }
}

const closeCategoryModal = () => {
  showCategoryModal.value = false
  editingCategory.value = null
  categoryForm.value = {
    name: '',
    description: '',
    website: '',
    display_order: 0,
    is_featured: false,
    is_active: true,
    meta_title: '',
    meta_description: '',
  }
}

const deleteCategory = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Delete this category?',
    'Delete Category',
    {
      details: 'This action cannot be undone. The category will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteCategory(id)
    await loadCategories()
  } catch (e) {
    message.value = 'Failed to delete category: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const editTag = (tag) => {
  editingTag.value = tag
  tagForm.value = {
    name: tag.name || '',
    website: tag.website || '',
  }
  showTagModal.value = true
}

const saveTag = async () => {
  try {
    let newTag = null
    if (editingTag.value) {
      await blogPagesAPI.updateTag(editingTag.value.id, tagForm.value)
      message.value = 'Tag updated successfully'
    } else {
      const res = await blogPagesAPI.createTag(tagForm.value)
      message.value = 'Tag created successfully'
      newTag = res.data
    }
    messageSuccess.value = true
    closeTagModal()
    await loadTags()
    
    // If tag was created from blog modal, add it to selected tags
    if (newTag && showCreateModal.value) {
      selectedTags.value.push(newTag)
      blogForm.value.tag_ids = selectedTags.value.map(t => t.id)
    }
  } catch (e) {
    message.value = 'Failed to save tag: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data))
    messageSuccess.value = false
  }
}

const closeTagModal = () => {
  showTagModal.value = false
  editingTag.value = null
  tagForm.value = {
    name: '',
    website: '',
  }
}

const deleteTag = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Delete this tag?',
    'Delete Tag',
    {
      details: 'This action cannot be undone. The tag will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteTag(id)
    await loadTags()
  } catch (e) {
    message.value = 'Failed to delete tag: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const toggleActionsMenu = (blogId) => {
  actionsMenuOpen.value = actionsMenuOpen.value === blogId ? null : blogId
}

const addFAQ = () => {
  if (!blogForm.value.faqs_data) {
    blogForm.value.faqs_data = []
  }
  blogForm.value.faqs_data.push({
    question: '',
    answer: ''
  })
}

const removeFAQ = (index) => {
  blogForm.value.faqs_data.splice(index, 1)
}

const addResource = () => {
  if (!blogForm.value.resources_data) {
    blogForm.value.resources_data = []
  }
  blogForm.value.resources_data.push({
    title: '',
    url: '',
    description: ''
  })
}

const removeResource = (index) => {
  blogForm.value.resources_data.splice(index, 1)
}

// Content Blocks Functions
const formatBlockType = (type) => {
  if (!type) return 'N/A'
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const loadBlogContentBlocks = async (blogId) => {
  contentBlocksLoading.value = true
  try {
    const response = await blogPagesAPI.listBlogContentBlocks({ blog: blogId })
    blogContentBlocks.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Error loading content blocks:', error)
  } finally {
    contentBlocksLoading.value = false
  }
}

const loadContentBlockTemplates = async () => {
  try {
    const response = await blogPagesAPI.listContentBlockTemplates({ is_active: true })
    contentBlockTemplates.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Error loading content block templates:', error)
  }
}

const openAddContentBlockModal = () => {
  if (!editingBlog.value?.id) {
    showError('Please save the blog post first before adding content blocks')
    return
  }
  editingContentBlock.value = null
  contentBlockForm.value = {
    template: null,
    position: 0,
    custom_data: {},
    is_active: true,
  }
  contentBlockCustomDataJson.value = '{}'
  showContentBlockModal.value = true
}

const editContentBlock = async (block) => {
  // Load templates if not already loaded
  if (contentBlockTemplates.value.length === 0) {
    await loadContentBlockTemplates()
  }
  editingContentBlock.value = block
  contentBlockForm.value = {
    template: block.template || block.template_id || null,
    position: block.position || 0,
    custom_data: block.custom_data || {},
    is_active: block.is_active !== undefined ? block.is_active : true,
  }
  contentBlockCustomDataJson.value = JSON.stringify(block.custom_data || {}, null, 2)
  showContentBlockModal.value = true
}

const saveContentBlock = async () => {
  // If blog is not saved yet, add to pending blocks
  if (!editingBlog.value?.id) {
    try {
      // Parse custom data JSON
      try {
        contentBlockForm.value.custom_data = JSON.parse(contentBlockCustomDataJson.value || '{}')
      } catch (e) {
        showError('Invalid JSON in custom data')
        return
      }
      
      if (editingContentBlock.value?.tempId) {
        // Update pending block
        const index = pendingContentBlocks.value.findIndex(b => b.tempId === editingContentBlock.value.tempId)
        if (index !== -1) {
          pendingContentBlocks.value[index] = {
            ...contentBlockForm.value,
            tempId: editingContentBlock.value.tempId,
          }
        }
        showSuccess('Content block updated (will be saved when blog is created)')
      } else {
        // Add new pending block
        const tempId = Date.now()
        pendingContentBlocks.value.push({
          ...contentBlockForm.value,
          tempId,
        })
        showSuccess('Content block added (will be saved when blog is created)')
      }
      
      showContentBlockModal.value = false
    } catch (error) {
      showError('Failed to add content block')
    }
    return
  }
  
  // Blog exists, save to API
  try {
    // Parse custom data JSON
    try {
      contentBlockForm.value.custom_data = JSON.parse(contentBlockCustomDataJson.value || '{}')
    } catch (e) {
      showError('Invalid JSON in custom data')
      return
    }
    
    const blockData = {
      ...contentBlockForm.value,
      blog: editingBlog.value.id,
    }
    
    if (editingContentBlock.value?.id) {
      await blogPagesAPI.updateBlogContentBlock(editingContentBlock.value.id, blockData)
      showSuccess('Content block updated successfully')
    } else {
      await blogPagesAPI.createBlogContentBlock(blockData)
      showSuccess('Content block added successfully')
    }
    
    showContentBlockModal.value = false
    await loadBlogContentBlocks(editingBlog.value.id)
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save content block'
    showError(errorMessage)
  }
}

const removeContentBlock = async (block) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to remove this content block?',
    'Remove Content Block',
    {
      details: 'This will remove the content block from the blog post. This action cannot be undone.',
      confirmText: 'Remove',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  // If it's a pending block (has tempId), just remove from array
  if (block.tempId) {
    pendingContentBlocks.value = pendingContentBlocks.value.filter(b => b.tempId !== block.tempId)
    showSuccess('Content block removed')
    return
  }
  
  // Otherwise, delete from API
  if (!editingBlog.value?.id) {
    showError('Blog post ID is required')
    return
  }
  
  try {
    await blogPagesAPI.deleteBlogContentBlock(block.id)
    showSuccess('Content block removed successfully')
    await loadBlogContentBlocks(editingBlog.value.id)
  } catch (error) {
    showError('Failed to remove content block')
  }
}

// Editor toolbar handlers
const handleContentInserted = (data) => {
  // Content was inserted via toolbar (snippet or block)
  if (editorRef.value) {
    editorInstance.value = editorRef.value.getQuillInstance?.() || null
  }
}

const handleTemplateApplied = (templateData) => {
  // Template was applied - update form with template data
  if (templateData) {
    blogForm.value.title = templateData.title || blogForm.value.title
    blogForm.value.content = templateData.content || blogForm.value.content
    blogForm.value.meta_title = templateData.meta_title || blogForm.value.meta_title
    blogForm.value.meta_description = templateData.meta_description || blogForm.value.meta_description
  }
}

const handleHealthCheck = (healthData) => {
  // Health check results received
  if (healthData.overall_score < 60) {
    // Show warning if score is low
    showError(`Content health score is low: ${healthData.overall_score}%. Please review your content.`)
  } else if (healthData.overall_score >= 80) {
    showSuccess(`Great! Content health score: ${healthData.overall_score}%`)
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingBlog.value = null
  blogForm.value = {
    website_id: null,
    title: '',
    slug: '',
    content: '',
    category_id: null,
    tag_ids: [],
    author_ids: [],
    status: 'draft',
    meta_title: '',
    meta_description: '',
    faqs_data: [],
    resources_data: [],
  }
  selectedTags.value = []
  tagSelect.value = ''
  selectedAuthors.value = []
  authorSelect.value = ''
  blogContentBlocks.value = []
  pendingContentBlocks.value = []
  availableAuthors.value = []
}

const resetFilters = () => {
  filters.value = { category: '', status: '', search: '' }
  loadBlogs()
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusDotClass = (isPublished, status) => {
  if (isPublished) {
    return 'bg-green-500'
  }
  if (status === 'scheduled') {
    return 'bg-yellow-500'
  }
  if (status === 'archived') {
    return 'bg-gray-500'
  }
  return 'bg-gray-400'
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    showSuccess('Copied to clipboard!')
  } catch (err) {
    showError('Failed to copy to clipboard')
  }
}

const getStatusBadgeClass = (isPublished, status) => {
  if (isPublished) return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
  if (status === 'draft') return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300'
  if (status === 'archived') return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
  return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300'
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

watch(activeTab, () => {
  if (activeTab.value === 'categories' && !categories.value.length) {
    loadCategories()
  } else if (activeTab.value === 'tags' && !tags.value.length) {
    loadTags()
  } else if (['posts', 'my-drafts', 'needs-review', 'scheduled', 'stale'].includes(activeTab.value)) {
    loadBlogs()
  }
})

onMounted(async () => {
  await Promise.all([loadBlogs(), loadCategories(), loadTags(), loadAvailableWebsites()])
  
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
      actionsMenuOpen.value = null
    }
  })
})

// Watch for modal opening to load websites if needed and get editor instance
watch(showCreateModal, async (isOpen) => {
  if (isOpen && contentBlockTemplates.value.length === 0) {
    await loadContentBlockTemplates()
  }
  if (isOpen) {
    await nextTick()
    // Get Quill editor instance from RichTextEditor component
    if (editorRef.value) {
      editorInstance.value = editorRef.value.getQuillInstance?.() || null
    }
  }
  if (isOpen && !availableWebsites.value.length) {
    await loadAvailableWebsites()
  }
})
</script>

<style scoped>
@reference "tailwindcss";
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300;
}
.card {
  @apply bg-white rounded-lg shadow-sm p-6;
}
</style>

