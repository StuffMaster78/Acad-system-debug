<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- Header -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Media Library</h1>
            <p class="mt-2 text-gray-600 dark:text-gray-400">Manage images, videos, documents, and other media assets</p>
          </div>
          <div class="flex items-center gap-3">
            <!-- View Mode Toggle -->
            <div class="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
              <button
                @click="viewMode = 'grid'"
                :class="[
                  'p-2 rounded transition-colors',
                  viewMode === 'grid'
                    ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                ]"
                title="Grid View"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                @click="viewMode = 'list'"
                :class="[
                  'p-2 rounded transition-colors',
                  viewMode === 'list'
                    ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                ]"
                title="List View"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
            <!-- Upload Button -->
            <button
              @click="showUploadModal = true"
              class="inline-flex items-center gap-2 px-4 py-2 bg-linear-to-r from-blue-600 to-blue-700 text-white rounded-lg font-medium hover:from-blue-700 hover:to-blue-800 transition-all shadow-sm hover:shadow-md"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Upload Media
            </button>
          </div>
        </div>

        <!-- Stats Bar -->
        <div class="mt-6 grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Total Assets</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ totalCount }}</p>
              </div>
            </div>
          </div>
          <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-green-100 dark:bg-green-900/40 rounded-lg">
                <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Images</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.images }}</p>
              </div>
            </div>
          </div>
          <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-purple-100 dark:bg-purple-900/40 rounded-lg">
                <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Videos</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.videos }}</p>
              </div>
            </div>
          </div>
          <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-orange-100 dark:bg-orange-900/40 rounded-lg">
                <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Documents</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.documents }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters & Search -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search</label>
            <div class="relative">
              <input
                v-model="filters.search"
                @input="debouncedSearch"
                type="text"
                placeholder="Search by title, tags, alt text..."
                class="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
              />
              <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Type</label>
            <select
              v-model="filters.type"
              @change="loadMedia"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
            >
              <option value="">All Types</option>
              <option v-for="type in mediaTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Website</label>
            <select
              v-model="filters.website_id"
              @change="loadMedia"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
            >
              <option value="">All Websites</option>
              <option v-for="website in websites" :key="website.id" :value="website.id">
                {{ website.name }}
              </option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="resetFilters"
              class="w-full px-4 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Reset
            </button>
          </div>
        </div>

        <!-- Bulk Actions -->
        <div v-if="selectedAssets.length > 0" class="mt-4 flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div class="flex items-center gap-3">
            <span class="text-sm font-medium text-blue-900 dark:text-blue-200">
              {{ selectedAssets.length }} {{ selectedAssets.length === 1 ? 'item' : 'items' }} selected
            </span>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="bulkDelete"
              class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
            >
              Delete Selected
            </button>
            <button
              @click="selectedAssets = []"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Clear Selection
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600 dark:text-gray-400">Loading media assets...</p>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="mediaAssets.length === 0" class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
        <div class="max-w-md mx-auto">
          <div class="w-24 h-24 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">No media assets found</h3>
          <p class="text-gray-600 dark:text-gray-400 mb-6">Upload your first asset to get started</p>
          <button
            @click="showUploadModal = true"
            class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Upload Media
          </button>
        </div>
      </div>

      <!-- Grid View -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        <div
          v-for="asset in mediaAssets"
          :key="asset.id"
          :class="[
            'bg-white dark:bg-gray-800 rounded-lg border-2 overflow-hidden transition-all cursor-pointer group',
            selectedAssets.find(a => a.id === asset.id)
              ? 'border-blue-600 ring-2 ring-blue-200 dark:ring-blue-800 shadow-lg'
              : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md'
          ]"
          @click="toggleSelection(asset)"
        >
          <!-- Thumbnail/Preview -->
          <div class="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center relative overflow-hidden">
            <img
              v-if="asset.type === 'image' && asset.url"
              :src="asset.url"
              :alt="asset.alt_text || asset.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <div v-else-if="asset.type === 'video'" class="text-center p-4">
              <div class="w-16 h-16 bg-purple-100 dark:bg-purple-900/40 rounded-full flex items-center justify-center mx-auto mb-2">
                <svg class="w-8 h-8 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
              <p class="text-xs text-gray-600 dark:text-gray-400">Video</p>
            </div>
            <div v-else class="text-center p-4">
              <div class="w-16 h-16 bg-orange-100 dark:bg-orange-900/40 rounded-full flex items-center justify-center mx-auto mb-2">
                <svg class="w-8 h-8 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p class="text-xs text-gray-600 dark:text-gray-400">Document</p>
            </div>

            <!-- Selection Checkbox -->
            <div class="absolute top-2 left-2">
              <div
                :class="[
                  'w-6 h-6 rounded border-2 flex items-center justify-center transition-all',
                  selectedAssets.find(a => a.id === asset.id)
                    ? 'bg-blue-600 border-blue-600'
                    : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 opacity-0 group-hover:opacity-100'
                ]"
              >
                <svg
                  v-if="selectedAssets.find(a => a.id === asset.id)"
                  class="w-4 h-4 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>

            <!-- Quick Actions Overlay -->
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
              <button
                @click.stop="viewAsset(asset)"
                class="p-2.5 bg-white rounded-lg text-gray-700 hover:bg-gray-100 shadow-lg transition-transform hover:scale-110"
                title="View"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
              <button
                @click.stop="editAsset(asset)"
                class="p-2.5 bg-white rounded-lg text-gray-700 hover:bg-gray-100 shadow-lg transition-transform hover:scale-110"
                title="Edit"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                @click.stop="deleteAsset(asset)"
                class="p-2.5 bg-red-500 rounded-lg text-white hover:bg-red-600 shadow-lg transition-transform hover:scale-110"
                title="Delete"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Asset Info -->
          <div class="p-3 border-t border-gray-200 dark:border-gray-700">
            <p class="text-sm font-medium text-gray-900 dark:text-white truncate" :title="asset.title">
              {{ asset.title || 'Untitled' }}
            </p>
            <div class="flex items-center justify-between mt-1">
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatFileSize(asset.size_bytes) }}
              </p>
              <span
                v-if="asset.type"
                :class="[
                  'px-2 py-0.5 text-xs font-medium rounded-full',
                  asset.type === 'image' ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' :
                  asset.type === 'video' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300' :
                  'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300'
                ]"
              >
                {{ asset.type }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left">
                <input
                  type="checkbox"
                  :checked="selectedAssets.length === mediaAssets.length && mediaAssets.length > 0"
                  @change="toggleSelectAll"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Preview</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Size</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Uploaded</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="asset in mediaAssets"
              :key="asset.id"
              :class="[
                'hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer',
                selectedAssets.find(a => a.id === asset.id) ? 'bg-blue-50 dark:bg-blue-900/20' : ''
              ]"
              @click="toggleSelection(asset)"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <input
                  type="checkbox"
                  :checked="!!selectedAssets.find(a => a.id === asset.id)"
                  @change.stop="toggleSelection(asset)"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="w-16 h-16 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700">
                  <img
                    v-if="asset.type === 'image' && asset.url"
                    :src="asset.url"
                    :alt="asset.alt_text || asset.title"
                    class="w-full h-full object-cover"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">{{ asset.title || 'Untitled' }}</p>
                  <p v-if="asset.alt_text" class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ asset.alt_text }}</p>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    asset.type === 'image' ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' :
                    asset.type === 'video' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300' :
                    'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300'
                  ]"
                >
                  {{ asset.type || 'Unknown' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatFileSize(asset.size_bytes) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(asset.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click.stop="viewAsset(asset)"
                    class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                    title="View"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    @click.stop="editAsset(asset)"
                    class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300"
                    title="Edit"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click.stop="deleteAsset(asset)"
                    class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                    title="Delete"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 px-6 py-4">
        <div class="text-sm text-gray-700 dark:text-gray-300">
          Showing page <span class="font-medium">{{ currentPage }}</span> of <span class="font-medium">{{ totalPages }}</span>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
        </div>
      </div>

      <!-- Upload Modal -->
      <UploadModal
        v-model:show="showUploadModal"
        :websites="websites"
        @uploaded="handleUploaded"
      />

      <!-- Edit Modal -->
      <EditModal
        v-if="editingAsset"
        :asset="editingAsset"
        @close="editingAsset = null"
        @updated="handleUpdated"
      />

      <!-- View/Preview Modal -->
      <PreviewModal
        v-if="viewingAsset"
        :asset="viewingAsset"
        @close="viewingAsset = null"
        @edit="editAssetFromPreview"
        @delete="deleteAssetFromPreview"
      />

      <!-- Confirmation Dialog -->
      <ConfirmationDialog
        v-model:show="showDeleteConfirm"
        title="Delete Media Asset"
        :message="deleteConfirmMessage"
        variant="danger"
        @confirm="confirmDelete"
        @cancel="showDeleteConfirm = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import mediaAPI from '@/api/media'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'
import UploadModal from '@/components/media/UploadModal.vue'
import EditModal from '@/components/media/EditModal.vue'
import PreviewModal from '@/components/media/PreviewModal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { success: showSuccess, error: showError } = useToast()

const mediaAssets = ref([])
const websites = ref([])
const mediaTypes = ref([])
const loading = ref(false)
const showUploadModal = ref(false)
const editingAsset = ref(null)
const viewingAsset = ref(null)
const viewMode = ref('grid')
const selectedAssets = ref([])
const showDeleteConfirm = ref(false)
const deleteConfirmMessage = ref('')
const assetToDelete = ref(null)

const filters = ref({
  search: '',
  type: '',
  website_id: ''
})

const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const pageSize = 20

const stats = computed(() => {
  const imageCount = mediaAssets.value.filter(a => a.type === 'image').length
  const videoCount = mediaAssets.value.filter(a => a.type === 'video').length
  const docCount = mediaAssets.value.filter(a => a.type && a.type !== 'image' && a.type !== 'video').length
  return {
    images: imageCount,
    videos: videoCount,
    documents: docCount
  }
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadMedia()
  }, 500)
}

const loadMedia = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.type) params.type = filters.value.type
    if (filters.value.website_id) params.website_id = filters.value.website_id

    const response = await mediaAPI.list(params)
    mediaAssets.value = response.data?.results || response.data || []
    totalPages.value = Math.ceil((response.data?.count || mediaAssets.value.length) / pageSize)
    totalCount.value = response.data?.count || mediaAssets.value.length
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to load media assets'))
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites({ is_active: true })
    websites.value = response.data?.results || response.data || []
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to load websites'))
  }
}

const loadMediaTypes = async () => {
  try {
    const response = await mediaAPI.getAllTypes()
    mediaTypes.value = Array.isArray(response.data) ? response.data : []
  } catch (e) {
    mediaTypes.value = []
  }
}

const toggleSelection = (asset) => {
  const index = selectedAssets.value.findIndex(a => a.id === asset.id)
  if (index >= 0) {
    selectedAssets.value.splice(index, 1)
  } else {
    selectedAssets.value.push(asset)
  }
}

const toggleSelectAll = () => {
  if (selectedAssets.value.length === mediaAssets.value.length) {
    selectedAssets.value = []
  } else {
    selectedAssets.value = [...mediaAssets.value]
  }
}

const bulkDelete = async () => {
  deleteConfirmMessage.value = `Are you sure you want to delete ${selectedAssets.value.length} media asset(s)? This action cannot be undone.`
  assetToDelete.value = { bulk: true, assets: [...selectedAssets.value] }
  showDeleteConfirm.value = true
}

const viewAsset = (asset) => {
  viewingAsset.value = asset
}

const editAsset = (asset) => {
  editingAsset.value = asset
}

const editAssetFromPreview = (asset) => {
  viewingAsset.value = null
  editingAsset.value = asset
}

const deleteAsset = async (asset) => {
  assetToDelete.value = asset
  deleteConfirmMessage.value = `Are you sure you want to delete "${asset.title || 'this asset'}"? This action cannot be undone.`
  showDeleteConfirm.value = true
}

const confirmDelete = async () => {
  if (!assetToDelete.value) return

  try {
    if (assetToDelete.value.bulk) {
      // Bulk delete
      const deletePromises = assetToDelete.value.assets.map(asset => mediaAPI.delete(asset.id))
      await Promise.all(deletePromises)
      selectedAssets.value = []
      showSuccess(`Successfully deleted ${assetToDelete.value.assets.length} asset(s)`)
    } else {
      // Single delete
      await mediaAPI.delete(assetToDelete.value.id)
      showSuccess('Media asset deleted successfully')
      if (viewingAsset.value?.id === assetToDelete.value.id) {
        viewingAsset.value = null
      }
    }
    assetToDelete.value = null
    showDeleteConfirm.value = false
    loadMedia()
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to delete media asset'))
  }
}

const deleteAssetFromPreview = (asset) => {
  viewingAsset.value = null
  deleteAsset(asset)
}

const handleUploaded = () => {
  showUploadModal.value = false
  loadMedia()
  showSuccess('Media uploaded successfully')
}

const handleUpdated = () => {
  editingAsset.value = null
  loadMedia()
  showSuccess('Media updated successfully')
}

const resetFilters = () => {
  filters.value = {
    search: '',
    type: '',
    website_id: ''
  }
  currentPage.value = 1
  loadMedia()
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadMedia()
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'Unknown'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadMedia()
  loadWebsites()
  loadMediaTypes()
})
</script>

<style scoped>
.aspect-square {
  aspect-ratio: 1 / 1;
}
</style>
