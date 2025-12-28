<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Website Management</h1>
        <p class="mt-2 text-gray-600">Manage all websites, domains, SEO settings, and branding</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="btn btn-primary"
        v-if="authStore.isSuperAdmin"
      >
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Website
      </button>
    </div>

    <!-- Terms & Conditions Modal -->
    <div v-if="showTermsModal && selectedWebsite" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-2xl font-bold">Terms &amp; Conditions - {{ selectedWebsite.name }}</h2>
              <p class="mt-1 text-sm text-gray-500">
                This content is shown on <code>/terms</code> for this website.
              </p>
              <p v-if="termsForm.last_updated || termsForm.version" class="mt-1 text-xs text-gray-400">
                <span v-if="termsForm.last_updated">
                  Last changed: {{ formatDate(termsForm.last_updated) }}
                </span>
                <span v-if="termsForm.version" class="ml-2">
                  Version: v{{ termsForm.version }}
                </span>
              </p>
            </div>
            <button @click="closeTermsModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>

          <form @submit.prevent="saveTerms" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Title</label>
                <input
                  v-model="termsForm.title"
                  type="text"
                  class="w-full border rounded px-3 py-2"
                  placeholder="Terms & Conditions"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Language</label>
                <select v-model="termsForm.language" class="w-full border rounded px-3 py-2">
                  <option value="en">English</option>
                  <option value="fr">French</option>
                  <option value="es">Spanish</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Meta Title</label>
              <input
                v-model="termsForm.meta_title"
                type="text"
                class="w-full border rounded px-3 py-2"
                placeholder="Terms & Conditions"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Meta Description</label>
              <textarea
                v-model="termsForm.meta_description"
                rows="2"
                class="w-full border rounded px-3 py-2"
                placeholder="Short description for SEO"
              ></textarea>
            </div>

            <div>
              <RichTextEditor
                v-model="termsForm.content"
                label="Terms &amp; Conditions Content"
                :required="true"
                toolbar="full"
                height="400px"
                :allow-images="false"
                help-text="Paste or edit the full terms here. This supports basic formatting and links."
              />
            </div>

            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closeTermsModal" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" :disabled="saving" class="btn btn-primary">
                {{ saving ? 'Saving...' : 'Save Terms' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Websites</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total || 0 }}</p>
        <p class="text-xs text-blue-600 mt-1">All websites</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.active || 0 }}</p>
        <p class="text-xs text-green-600 mt-1">Currently active</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Inactive</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.inactive || 0 }}</p>
        <p class="text-xs text-red-600 mt-1">Deactivated</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200">
        <p class="text-sm font-medium text-gray-700 mb-1">Deleted</p>
        <p class="text-3xl font-bold text-gray-900">{{ stats.deleted || 0 }}</p>
        <p class="text-xs text-gray-600 mt-1">Soft deleted</p>
      </div>
    </div>

    <!-- Filters & View Toggle -->
    <div class="card p-4">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 flex-1">
          <div>
            <label class="block text-sm font-medium mb-1.5 text-gray-700">Status Filter</label>
            <select 
              v-model="filters.status" 
              @change="loadWebsites" 
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="deleted">Deleted</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1.5 text-gray-700">Search</label>
            <div class="relative">
              <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="filters.search"
                @input="debouncedSearch"
                type="text"
                placeholder="Search by name, domain..."
                class="w-full border border-gray-300 rounded-lg pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
          </div>
          <div class="flex items-end">
            <button 
              @click="resetFilters" 
              class="btn btn-secondary w-full flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Reset
            </button>
          </div>
        </div>
        <div class="flex items-end gap-2">
          <div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
            <button
              @click="viewMode = 'table'"
              :class="viewMode === 'table' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              class="px-3 py-1.5 rounded-md text-sm font-medium transition-all"
              title="Table View"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Table
            </button>
            <button
              @click="viewMode = 'grid'"
              :class="viewMode === 'grid' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              class="px-3 py-1.5 rounded-md text-sm font-medium transition-all"
              title="Grid View"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              Grid
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Websites List -->
    <div class="card overflow-hidden p-0">
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="flex flex-col items-center gap-3">
          <div class="animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600"></div>
          <p class="text-sm text-gray-500">Loading websites...</p>
        </div>
      </div>
      
      <!-- Table View -->
      <div v-else-if="viewMode === 'table'">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Website</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Domain</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Settings</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">SEO</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-100">
              <tr 
                v-for="website in websites" 
                :key="website.id" 
                class="hover:bg-gray-50 transition-colors website-table-row"
              >
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <div v-if="website.logo" class="shrink-0 h-10 w-10">
                      <img :src="website.logo" :alt="website.name" class="h-10 w-10 rounded-lg object-cover border border-gray-200" />
                    </div>
                    <div v-else class="shrink-0 h-10 w-10 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
                      {{ getWebsiteInitials(website) }}
                    </div>
                    <div class="min-w-0">
                      <div class="font-semibold text-gray-900 text-sm">{{ website.name }}</div>
                      <div class="text-xs text-gray-500 mt-0.5">{{ website.slug }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <a 
                    :href="website.domain" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    class="text-blue-600 hover:text-blue-800 hover:underline text-sm font-medium flex items-center gap-1 group"
                  >
                    <span>{{ formatDomain(website.domain) }}</span>
                    <svg class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex flex-col gap-1.5">
                    <span :class="getStatusBadgeClass(website)" class="px-2.5 py-1 rounded-md text-xs font-semibold inline-flex items-center gap-1.5 w-fit">
                      <span :class="getStatusDotClass(website)" class="w-1.5 h-1.5 rounded-full"></span>
                      {{ getStatusText(website) }}
                    </span>
                    <span v-if="website.is_deleted" class="text-xs text-gray-500">
                      {{ formatDate(website.deleted_at) }}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-3 text-xs">
                    <div class="flex items-center gap-1" :class="website.allow_registration ? 'text-green-600' : 'text-gray-400'">
                      <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                        <path v-if="website.allow_registration" fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                        <path v-else fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                      <span class="font-medium">Registration</span>
                    </div>
                    <div class="flex items-center gap-1" :class="website.allow_guest_checkout ? 'text-green-600' : 'text-gray-400'">
                      <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                        <path v-if="website.allow_guest_checkout" fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                        <path v-else fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                      <span class="font-medium">Guest</span>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex flex-col gap-1 text-xs">
                    <div v-if="website.meta_title" class="text-gray-700 truncate max-w-xs font-medium" :title="website.meta_title">
                      {{ website.meta_title }}
                    </div>
                    <div v-if="website.google_analytics_id" class="flex items-center gap-1 text-blue-600">
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                      </svg>
                      <span>{{ website.google_analytics_id }}</span>
                    </div>
                    <div v-else class="text-gray-400">No analytics</div>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button 
                      @click="viewWebsiteDetail(website)" 
                      class="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                      title="View Details"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button 
                      @click="editWebsite(website)" 
                      class="p-1.5 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors"
                      title="Edit"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <div class="relative">
                      <button 
                        @click="toggleActionsMenu(website.id)" 
                        class="p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                        title="More Actions"
                      >
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                        </svg>
                      </button>
                      <div 
                        v-if="actionsMenuOpen === website.id" 
                        class="absolute right-0 mt-1 w-56 bg-white rounded-lg shadow-lg z-20 border border-gray-200 py-1"
                      >
                        <button @click="viewSEOSettings(website)" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                          <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                          </svg>
                          SEO Settings
                        </button>
                        <button @click="viewIntegrations(website)" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                          </svg>
                          Integrations
                        </button>
                        <button @click="openTermsModal(website)" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                          <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          Edit Terms
                        </button>
                        <button @click="viewActionLogs(website)" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                          <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Action Logs
                        </button>
                        <div class="border-t border-gray-100 my-1"></div>
                        <button @click="toggleActive(website)" v-if="!website.is_deleted" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                          <svg class="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="website.is_active ? 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' : 'M13 10V3L4 14h7v7l9-11h-7z'" />
                          </svg>
                          {{ website.is_active ? 'Deactivate' : 'Activate' }}
                        </button>
                        <button @click="softDeleteWebsite(website)" v-if="!website.is_deleted && authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          Soft Delete
                        </button>
                        <button @click="restoreWebsite(website)" v-if="website.is_deleted && authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-green-50 flex items-center gap-2">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Restore
                        </button>
                        <button @click="deleteWebsitePermanently(website)" v-if="authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-red-800 hover:bg-red-50 flex items-center gap-2">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          Delete Permanently
                        </button>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="!websites.length && !loading" class="text-center py-16">
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-1">No websites found</h3>
          <p class="text-sm text-gray-500 mb-4">{{ filters.search || filters.status ? 'Try adjusting your filters' : 'Get started by creating your first website' }}</p>
          <button v-if="authStore.isSuperAdmin && !filters.search && !filters.status" @click="showCreateModal = true" class="btn btn-primary">
            Create Website
          </button>
        </div>
      </div>

      <!-- Grid View -->
      <div v-else class="p-6">
        <div v-if="!websites.length && !loading" class="text-center py-16">
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-1">No websites found</h3>
          <p class="text-sm text-gray-500 mb-4">{{ filters.search || filters.status ? 'Try adjusting your filters' : 'Get started by creating your first website' }}</p>
          <button v-if="authStore.isSuperAdmin && !filters.search && !filters.status" @click="showCreateModal = true" class="btn btn-primary">
            Create Website
          </button>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="website in websites" 
            :key="website.id"
            class="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-all hover:border-blue-300 group flex flex-col overflow-hidden"
          >
            <!-- Header Section -->
            <div class="flex items-start justify-between mb-4 min-w-0">
              <div class="flex items-center gap-3 min-w-0 flex-1">
                <div v-if="website.logo" class="shrink-0 h-12 w-12">
                  <img :src="website.logo" :alt="website.name" class="h-12 w-12 rounded-lg object-cover border border-gray-200" />
                </div>
                <div v-else class="shrink-0 h-12 w-12 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-base shadow-sm">
                  {{ getWebsiteInitials(website) }}
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-gray-900 text-sm truncate" :title="website.name">{{ website.name }}</h3>
                  <p class="text-xs text-gray-500 mt-0.5 truncate" :title="website.slug">{{ website.slug }}</p>
                </div>
              </div>
              <span :class="getStatusBadgeClass(website)" class="px-2 py-1 rounded-md text-xs font-semibold inline-flex items-center gap-1.5 shrink-0 ml-2">
                <span :class="getStatusDotClass(website)" class="w-1.5 h-1.5 rounded-full"></span>
                <span class="whitespace-nowrap">{{ getStatusText(website) }}</span>
              </span>
            </div>
            
            <!-- Content Section -->
            <div class="space-y-3 mb-4 flex-1 min-h-0">
              <div class="min-w-0">
                <a 
                  :href="website.domain" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="text-blue-600 hover:text-blue-800 hover:underline text-sm font-medium flex items-center gap-1.5 group/link min-w-0"
                >
                  <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  <span class="truncate min-w-0" :title="formatDomain(website.domain)">{{ formatDomain(website.domain) }}</span>
                </a>
              </div>
              
              <div class="flex items-center gap-3 text-xs flex-wrap">
                <div class="flex items-center gap-1 shrink-0" :class="website.allow_registration ? 'text-green-600' : 'text-gray-400'">
                  <svg class="w-3.5 h-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path v-if="website.allow_registration" fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    <path v-else fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                  <span class="whitespace-nowrap">Registration</span>
                </div>
                <div class="flex items-center gap-1 shrink-0" :class="website.allow_guest_checkout ? 'text-green-600' : 'text-gray-400'">
                  <svg class="w-3.5 h-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path v-if="website.allow_guest_checkout" fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    <path v-else fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                  <span class="whitespace-nowrap">Guest</span>
                </div>
              </div>
              
              <div v-if="website.meta_title || website.google_analytics_id" class="pt-2 border-t border-gray-100 min-w-0">
                <div v-if="website.meta_title" class="text-xs text-gray-600 truncate mb-1.5" :title="website.meta_title">
                  {{ website.meta_title }}
                </div>
                <div v-if="website.google_analytics_id" class="flex items-center gap-1 text-xs text-blue-600 min-w-0">
                  <svg class="w-3 h-3 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                  </svg>
                  <span class="truncate min-w-0" :title="website.google_analytics_id">{{ website.google_analytics_id }}</span>
                </div>
              </div>
            </div>
            
            <!-- Actions Section -->
            <div class="flex items-center justify-between pt-4 border-t border-gray-100 shrink-0">
              <div class="flex items-center gap-1">
                <button 
                  @click="viewWebsiteDetail(website)" 
                  class="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors shrink-0"
                  title="View Details"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button 
                  @click="editWebsite(website)" 
                  class="p-1.5 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors shrink-0"
                  title="Edit"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </div>
              <div class="relative">
                <button 
                  @click="toggleActionsMenu(website.id)" 
                  class="p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors shrink-0"
                  title="More Actions"
                >
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                  </svg>
                </button>
                <div 
                  v-if="actionsMenuOpen === website.id" 
                  class="absolute right-0 bottom-full mb-1 w-56 bg-white rounded-lg shadow-lg z-20 border border-gray-200 py-1 max-h-80 overflow-y-auto"
                >
                  <button @click="viewSEOSettings(website)" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 whitespace-nowrap">
                    <svg class="w-4 h-4 text-purple-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    SEO Settings
                  </button>
                  <button @click="openTermsModal(website)" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 whitespace-nowrap">
                    <svg class="w-4 h-4 text-blue-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Edit Terms
                  </button>
                  <button @click="viewActionLogs(website)" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 whitespace-nowrap">
                    <svg class="w-4 h-4 text-indigo-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Action Logs
                  </button>
                  <div class="border-t border-gray-100 my-1"></div>
                  <button @click="toggleActive(website)" v-if="!website.is_deleted" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 whitespace-nowrap">
                    <svg class="w-4 h-4 text-yellow-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="website.is_active ? 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' : 'M13 10V3L4 14h7v7l9-11h-7z'" />
                    </svg>
                    {{ website.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                  <button @click="softDeleteWebsite(website)" v-if="!website.is_deleted && authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 whitespace-nowrap">
                    <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Soft Delete
                  </button>
                  <button @click="restoreWebsite(website)" v-if="website.is_deleted && authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-green-50 flex items-center gap-2 whitespace-nowrap">
                    <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Restore
                  </button>
                  <button @click="deleteWebsitePermanently(website)" v-if="authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-red-800 hover:bg-red-50 flex items-center gap-2 whitespace-nowrap">
                    <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Delete Permanently
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Website Modal -->
    <div v-if="showCreateModal || editingWebsite" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingWebsite ? 'Edit Website' : 'Create Website' }}</h2>
            <button @click="closeModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="saveWebsite" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Name *</label>
                <input v-model="websiteForm.name" type="text" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Domain *</label>
                <input v-model="websiteForm.domain" type="url" required class="w-full border rounded px-3 py-2" placeholder="https://example.com" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Contact Email</label>
                <input v-model="websiteForm.contact_email" type="email" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Admin Notifications Email</label>
                <input
                  v-model="websiteForm.admin_notifications_email"
                  type="email"
                  class="w-full border rounded px-3 py-2"
                  placeholder="alerts@gmail.com (recommended)"
                />
                <p class="mt-1 text-xs text-gray-500">
                  Critical order &amp; payment alerts for this website can be forwarded here for admins/superadmins.
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Contact Phone</label>
                <input v-model="websiteForm.contact_phone" type="tel" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Theme Color</label>
                <input v-model="websiteForm.theme_color" type="color" class="w-full border rounded px-3 py-2 h-10" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Active</label>
                <input v-model="websiteForm.is_active" type="checkbox" class="mt-2" />
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Allow Registration</label>
                <input v-model="websiteForm.allow_registration" type="checkbox" class="mt-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Allow Guest Checkout</label>
                <input v-model="websiteForm.allow_guest_checkout" type="checkbox" class="mt-2" />
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Meta Title</label>
                <input v-model="websiteForm.meta_title" type="text" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Meta Description</label>
                <textarea v-model="websiteForm.meta_description" rows="2" class="w-full border rounded px-3 py-2"></textarea>
              </div>
            </div>
            
            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="saving" class="btn btn-primary">
                {{ saving ? 'Saving...' : (editingWebsite ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- SEO Settings Modal -->
    <div v-if="showSEOModal && selectedWebsite" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-2xl font-bold">SEO & Analytics – {{ selectedWebsite.name }}</h2>
            <p class="mt-1 text-sm text-gray-500">
              Configure how this site appears in search results and connect it to your analytics / webmaster tools.
            </p>
          </div>
          <button @click="closeSEOModal" class="text-gray-500 hover:text-gray-700 text-2xl leading-none">✕</button>
        </div>
        
        <form @submit.prevent="saveSEOSettings" class="space-y-6">
          <!-- Search appearance -->
          <div class="border border-gray-200 rounded-lg p-4 space-y-3">
            <h3 class="text-sm font-semibold text-gray-900">Search appearance</h3>
            <p class="text-xs text-gray-500">
              These values are used for default meta tags on the main site (can be overridden per page).
            </p>
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium mb-1">Meta Title</label>
                <input
                  v-model="seoForm.meta_title"
                  type="text"
                  class="w-full border rounded px-3 py-2 text-sm"
                  placeholder="e.g. Affordable Academic Writing Services | {{ selectedWebsite.name }}"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Meta Description</label>
                <textarea
                  v-model="seoForm.meta_description"
                  rows="3"
                  class="w-full border rounded px-3 py-2 text-sm"
                  placeholder="Short summary that will appear under your site title in Google and Bing results."
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Verification & tracking -->
          <div class="border border-gray-200 rounded-lg p-4 space-y-4">
            <h3 class="text-sm font-semibold text-gray-900">Verification & tracking IDs</h3>
            <p class="text-xs text-gray-500">
              Paste only the ID/token from each service (no full script tags). These are usually found in the admin
              dashboard of each tool.
            </p>
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium mb-1">Google Analytics Measurement ID</label>
                <input
                  v-model="seoForm.google_analytics_id"
                  type="text"
                  class="w-full border rounded px-3 py-2 text-sm"
                  placeholder="G-XXXXXXXXXX"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Google Search Console Verification ID</label>
                <input
                  v-model="seoForm.google_search_console_id"
                  type="text"
                  class="w-full border rounded px-3 py-2 text-sm"
                  placeholder="e.g. your GSC HTML meta content value"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Bing Webmaster Verification ID</label>
                <input
                  v-model="seoForm.bing_webmaster_id"
                  type="text"
                  class="w-full border rounded px-3 py-2 text-sm"
                  placeholder="e.g. your Bing meta content value"
                />
              </div>
            </div>
          </div>

          <!-- Communication Widgets -->
          <div class="border border-gray-200 rounded-lg p-4 space-y-4">
            <h3 class="text-sm font-semibold text-gray-900">Live Chat & Communication Widgets</h3>
            <p class="text-xs text-gray-500">
              Configure live chat widgets like Tawk.to, Intercom, or Zendesk Chat for customer support.
            </p>
            <div class="space-y-3">
              <div class="flex items-center gap-2">
                <input
                  v-model="seoForm.enable_live_chat"
                  type="checkbox"
                  id="enable_live_chat"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label for="enable_live_chat" class="text-sm font-medium text-gray-700">
                  Enable Live Chat Widget
                </label>
              </div>
              
              <div v-if="seoForm.enable_live_chat">
                <label class="block text-sm font-medium mb-1">Widget Type</label>
                <select
                  v-model="seoForm.communication_widget_type"
                  class="w-full border rounded px-3 py-2 text-sm"
                >
                  <option value="">Select widget type</option>
                  <option value="tawkto">Tawk.to</option>
                  <option value="intercom">Intercom</option>
                  <option value="zendesk">Zendesk Chat</option>
                  <option value="custom">Custom Widget</option>
                </select>
              </div>

              <div v-if="seoForm.enable_live_chat && seoForm.communication_widget_type === 'tawkto'" class="space-y-3">
                <div>
                  <label class="block text-sm font-medium mb-1">Tawk.to Widget ID</label>
                  <input
                    v-model="seoForm.tawkto_widget_id"
                    type="text"
                    class="w-full border rounded px-3 py-2 text-sm"
                    placeholder="e.g. 1a2b3c4d5e6f7g8h9i0j"
                  />
                  <p class="text-xs text-gray-500 mt-1">
                    Found in Tawk.to dashboard: Administration → Property Settings → Widget ID
                  </p>
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1">Tawk.to Property ID (Optional)</label>
                  <input
                    v-model="seoForm.tawkto_property_id"
                    type="text"
                    class="w-full border rounded px-3 py-2 text-sm"
                    placeholder="e.g. property-12345"
                  />
                  <p class="text-xs text-gray-500 mt-1">
                    Only needed for multi-property Tawk.to accounts
                  </p>
                </div>
              </div>

              <div v-if="seoForm.enable_live_chat && seoForm.communication_widget_type === 'intercom'" class="p-3 bg-blue-50 rounded">
                <p class="text-xs text-gray-600">
                  Intercom configuration can be added in the custom widget config field below or via their standard embed code.
                </p>
              </div>

              <div v-if="seoForm.enable_live_chat && seoForm.communication_widget_type === 'zendesk'" class="p-3 bg-blue-50 rounded">
                <p class="text-xs text-gray-600">
                  Zendesk Chat configuration can be added in the custom widget config field below or via their standard embed code.
                </p>
              </div>

              <div v-if="seoForm.enable_live_chat && seoForm.communication_widget_type === 'custom'" class="p-3 bg-blue-50 rounded">
                <p class="text-xs text-gray-600">
                  For custom widgets, add your configuration as JSON in the custom widget config field.
                </p>
              </div>
            </div>
          </div>
          
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="closeSEOModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">Save SEO Settings</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Integrations Management Modal -->
    <div v-if="showIntegrationsModal && selectedWebsite" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] flex flex-col">
        <!-- Fixed Header -->
        <div class="p-6 border-b flex-shrink-0">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-2xl font-bold">Integrations - {{ selectedWebsite.name }}</h2>
              <p class="mt-1 text-sm text-gray-500">Manage API keys and third-party service integrations</p>
            </div>
            <button @click="closeIntegrationsModal" class="text-gray-500 hover:text-gray-700 text-2xl leading-none">✕</button>
          </div>

          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <input
                v-model="integrationSearch"
                type="text"
                placeholder="Search integrations..."
                class="border rounded px-3 py-2 text-sm w-64"
              />
              <select
                v-model="integrationTypeFilter"
                class="border rounded px-3 py-2 text-sm"
              >
                <option value="">All Types</option>
                <option value="stripe">Payment Gateways</option>
                <option value="sendgrid">Email Services</option>
                <option value="twilio">SMS Services</option>
                <option value="s3">Storage</option>
                <option value="cloudflare">CDN</option>
                <option value="google_oauth">Social Auth</option>
                <option value="facebook_pixel">Analytics</option>
                <option value="intercom">Communication</option>
              </select>
            </div>
            <button @click="openIntegrationForm()" class="btn btn-primary">
              <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Add Integration
            </button>
          </div>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- Integrations List -->
          <div v-if="integrationsLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          <div v-else-if="filteredIntegrations.length === 0" class="text-center py-12 text-gray-500">
            <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <p class="text-lg font-medium">No integrations configured</p>
            <p class="text-sm mt-1">Click "Add Integration" to get started</p>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="integration in filteredIntegrations"
              :key="integration.id"
              class="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <h3 class="font-semibold text-lg">{{ getIntegrationDisplayName(integration.integration_type) }}</h3>
                    <span
                      :class="integration.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                      class="px-2 py-1 rounded text-xs font-medium"
                    >
                      {{ integration.is_active ? 'Active' : 'Inactive' }}
                    </span>
                    <span v-if="integration.name" class="text-sm text-gray-500">({{ integration.name }})</span>
                  </div>
                  <p v-if="integration.description" class="text-sm text-gray-600 mb-2">{{ integration.description }}</p>
                  <div class="flex flex-wrap gap-4 text-xs text-gray-500">
                    <span v-if="integration.api_key">
                      <span class="font-medium">API Key:</span> {{ integration.api_key }}
                    </span>
                    <span v-if="integration.secret_key">
                      <span class="font-medium">Secret:</span> {{ integration.secret_key }}
                    </span>
                    <span v-if="integration.access_token">
                      <span class="font-medium">Token:</span> {{ integration.access_token }}
                    </span>
                  </div>
                  <div v-if="integration.config && Object.keys(integration.config).length > 0" class="mt-2 text-xs">
                    <span class="font-medium text-gray-600">Config:</span>
                    <pre class="mt-1 text-gray-500 bg-gray-50 p-2 rounded text-xs overflow-x-auto">{{ JSON.stringify(integration.config, null, 2) }}</pre>
                  </div>
                </div>
                <div class="flex items-center gap-2 ml-4">
                  <button
                    @click="openIntegrationForm(integration)"
                    class="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="Edit"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteIntegration(integration.id)"
                    class="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="Delete"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Integration Form Modal -->
    <div v-if="showIntegrationFormModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold">{{ editingIntegration ? 'Edit Integration' : 'Add Integration' }}</h3>
            <button @click="closeIntegrationForm" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <form @submit.prevent="saveIntegration" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Integration Type *</label>
              <select
                v-model="integrationForm.integration_type"
                required
                class="w-full border rounded px-3 py-2"
                :disabled="!!editingIntegration"
              >
                <option value="">Select integration type</option>
                <optgroup label="Payment Gateways">
                  <option value="stripe">Stripe</option>
                  <option value="paypal">PayPal</option>
                  <option value="razorpay">Razorpay</option>
                  <option value="square">Square</option>
                  <option value="mollie">Mollie</option>
                </optgroup>
                <optgroup label="Email Services">
                  <option value="sendgrid">SendGrid</option>
                  <option value="mailgun">Mailgun</option>
                  <option value="ses">AWS SES</option>
                  <option value="postmark">Postmark</option>
                </optgroup>
                <optgroup label="SMS Services">
                  <option value="twilio">Twilio</option>
                  <option value="nexmo">Vonage (Nexmo)</option>
                  <option value="aws_sns">AWS SNS</option>
                </optgroup>
                <optgroup label="Storage">
                  <option value="s3">AWS S3</option>
                  <option value="do_spaces">DigitalOcean Spaces</option>
                  <option value="gcs">Google Cloud Storage</option>
                </optgroup>
                <optgroup label="CDN">
                  <option value="cloudflare">Cloudflare</option>
                  <option value="cloudfront">AWS CloudFront</option>
                </optgroup>
                <optgroup label="Social Auth">
                  <option value="google_oauth">Google OAuth</option>
                  <option value="facebook_oauth">Facebook OAuth</option>
                  <option value="github_oauth">GitHub OAuth</option>
                </optgroup>
                <optgroup label="Analytics">
                  <option value="facebook_pixel">Facebook Pixel</option>
                  <option value="pinterest_tag">Pinterest Tag</option>
                  <option value="hotjar">Hotjar</option>
                </optgroup>
                <optgroup label="Communication">
                  <option value="intercom">Intercom</option>
                  <option value="zendesk">Zendesk</option>
                </optgroup>
                <optgroup label="AI Services">
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                </optgroup>
                <optgroup label="Other">
                  <option value="zapier">Zapier</option>
                  <option value="webhook">Custom Webhook</option>
                  <option value="custom">Custom Integration</option>
                </optgroup>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Name (Optional)</label>
              <input
                v-model="integrationForm.name"
                type="text"
                class="w-full border rounded px-3 py-2"
                placeholder="e.g., Production Stripe, Test SendGrid"
              />
              <p class="text-xs text-gray-500 mt-1">Useful when you have multiple integrations of the same type</p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Description (Optional)</label>
              <textarea
                v-model="integrationForm.description"
                rows="2"
                class="w-full border rounded px-3 py-2"
                placeholder="Notes about this integration"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">API Key</label>
              <input
                v-model="integrationForm.api_key"
                type="text"
                class="w-full border rounded px-3 py-2"
                placeholder="Enter API key (will be encrypted)"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Secret Key</label>
              <input
                v-model="integrationForm.secret_key"
                type="text"
                class="w-full border rounded px-3 py-2"
                placeholder="Enter secret key (will be encrypted)"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Access Token (Optional)</label>
              <input
                v-model="integrationForm.access_token"
                type="text"
                class="w-full border rounded px-3 py-2"
                placeholder="Enter access token (will be encrypted)"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Configuration (JSON)</label>
              <textarea
                v-model="integrationForm.configJson"
                rows="4"
                class="w-full border rounded px-3 py-2 font-mono text-sm"
                placeholder='{"endpoint": "https://api.example.com", "region": "us-east-1"}'
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">Additional configuration as JSON (endpoints, regions, etc.)</p>
            </div>

            <div class="flex items-center gap-2">
              <input
                v-model="integrationForm.is_active"
                type="checkbox"
                id="integration_active"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded"
              />
              <label for="integration_active" class="text-sm font-medium">Active</label>
            </div>

            <div class="flex justify-end gap-2 pt-4 border-t">
              <button type="button" @click="closeIntegrationForm" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="savingIntegration" class="btn btn-primary">
                {{ savingIntegration ? 'Saving...' : (editingIntegration ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Website Detail Modal -->
    <div v-if="viewingWebsite" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-4">
              <div v-if="viewingWebsite.logo" class="h-16 w-16">
                <img :src="viewingWebsite.logo" :alt="viewingWebsite.name" class="h-16 w-16 rounded object-cover" />
              </div>
              <div v-else class="h-16 w-16 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-2xl">
                {{ getWebsiteInitials(viewingWebsite) }}
              </div>
              <div>
                <h2 class="text-2xl font-bold text-gray-900">{{ viewingWebsite.name }}</h2>
                <p class="text-gray-500">{{ viewingWebsite.domain }}</p>
              </div>
            </div>
            <button @click="closeWebsiteDetail" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div class="grid grid-cols-2 gap-6 mb-6">
            <!-- Basic Info -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">Basic Information</h3>
              <div class="space-y-2">
                <div>
                  <span class="text-sm font-medium text-gray-600">Name:</span>
                  <span class="ml-2 text-gray-900">{{ viewingWebsite.name }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Domain:</span>
                  <a :href="viewingWebsite.domain" target="_blank" class="ml-2 text-blue-600 hover:underline">{{ viewingWebsite.domain }}</a>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Slug:</span>
                  <span class="ml-2 text-gray-900">{{ viewingWebsite.slug }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Status:</span>
                  <span :class="getStatusBadgeClass(viewingWebsite)" class="ml-2 px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusText(viewingWebsite) }}
                  </span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Theme Color:</span>
                  <span class="ml-2 inline-block w-6 h-6 rounded border" :style="{ backgroundColor: viewingWebsite.theme_color || '#000' }"></span>
                  <span class="ml-2 text-gray-900">{{ viewingWebsite.theme_color || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <!-- Contact & Settings -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">Contact & Settings</h3>
              <div class="space-y-2">
                <div>
                  <span class="text-sm font-medium text-gray-600">Contact Email:</span>
                  <span class="ml-2 text-gray-900">{{ viewingWebsite.contact_email || 'N/A' }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Contact Phone:</span>
                  <span class="ml-2 text-gray-900">{{ viewingWebsite.contact_phone || 'N/A' }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Allow Registration:</span>
                  <span :class="viewingWebsite.allow_registration ? 'text-green-600' : 'text-red-600'" class="ml-2 font-medium">
                    {{ viewingWebsite.allow_registration ? 'Yes' : 'No' }}
                  </span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Guest Checkout:</span>
                  <span :class="viewingWebsite.allow_guest_checkout ? 'text-green-600' : 'text-red-600'" class="ml-2 font-medium">
                    {{ viewingWebsite.allow_guest_checkout ? 'Yes' : 'No' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- SEO Information -->
          <div class="mb-6">
            <h3 class="text-lg font-semibold text-gray-900 border-b pb-2 mb-4">SEO Information</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-sm font-medium text-gray-600">Meta Title:</span>
                <p class="text-gray-900 mt-1">{{ viewingWebsite.meta_title || 'N/A' }}</p>
              </div>
              <div>
                <span class="text-sm font-medium text-gray-600">Meta Description:</span>
                <p class="text-gray-900 mt-1">{{ viewingWebsite.meta_description || 'N/A' }}</p>
              </div>
              <div>
                <span class="text-sm font-medium text-gray-600">Google Analytics ID:</span>
                <p class="text-gray-900 mt-1">{{ viewingWebsite.google_analytics_id || 'N/A' }}</p>
              </div>
              <div>
                <span class="text-sm font-medium text-gray-600">Google Search Console ID:</span>
                <p class="text-gray-900 mt-1">{{ viewingWebsite.google_search_console_id || 'N/A' }}</p>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="flex gap-2 pt-4 border-t">
            <button @click="editWebsite(viewingWebsite); closeWebsiteDetail()" class="btn btn-primary">Edit Website</button>
            <button @click="viewSEOSettings(viewingWebsite); closeWebsiteDetail()" class="btn btn-secondary">SEO Settings</button>
            <button @click="viewActionLogs(viewingWebsite); closeWebsiteDetail()" class="btn btn-secondary">Action Logs</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import websitesAPI from '@/api/websites'
import RichTextEditor from '@/components/common/RichTextEditor.vue'

const authStore = useAuthStore()

const websites = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const showSEOModal = ref(false)
const showTermsModal = ref(false)
const showIntegrationsModal = ref(false)
const showIntegrationFormModal = ref(false)
const editingWebsite = ref(null)
const viewingWebsite = ref(null)
const selectedWebsite = ref(null)
const actionsMenuOpen = ref(null)
const viewMode = ref('table') // 'table' or 'grid'
const integrations = ref([])
const integrationsLoading = ref(false)
const integrationSearch = ref('')
const integrationTypeFilter = ref('')
const editingIntegration = ref(null)
const savingIntegration = ref(false)

const filters = ref({
  status: '',
  search: '',
})

const stats = ref({
  total: 0,
  active: 0,
  inactive: 0,
  deleted: 0,
})

const websiteForm = ref({
  name: '',
  domain: '',
  contact_email: '',
  admin_notifications_email: '',
  contact_phone: '',
  theme_color: '#000000',
  is_active: true,
  allow_registration: true,
  allow_guest_checkout: false,
  meta_title: '',
  meta_description: '',
})

const seoForm = ref({
  meta_title: '',
  meta_description: '',
  google_analytics_id: '',
  google_search_console_id: '',
  bing_webmaster_id: '',
  enable_live_chat: false,
  communication_widget_type: '',
  tawkto_widget_id: '',
  tawkto_property_id: '',
  communication_widget_config: {},
})

const termsForm = ref({
  title: 'Terms & Conditions',
  content: '',
  language: 'en',
  meta_title: '',
  meta_description: '',
  last_updated: null,
  version: null,
})

const integrationForm = ref({
  website: null,
  integration_type: '',
  name: '',
  description: '',
  api_key: '',
  secret_key: '',
  access_token: '',
  configJson: '{}',
  is_active: true,
})

const message = ref('')
const messageSuccess = ref(false)
const router = useRouter()

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadWebsites()
  }, 500)
}

const loadWebsites = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status === 'active') params.is_active = 'true'
    if (filters.value.status === 'inactive') params.is_active = 'false'
    if (filters.value.status === 'deleted') params.is_deleted = 'true'
    if (filters.value.search) params.search = filters.value.search
    
    const res = await websitesAPI.listWebsites(params)
    websites.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
    calculateStats()
  } catch (e) {
    message.value = 'Failed to load websites: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  stats.value = {
    total: websites.value.length,
    active: websites.value.filter(w => w.is_active && !w.is_deleted).length,
    inactive: websites.value.filter(w => !w.is_active && !w.is_deleted).length,
    deleted: websites.value.filter(w => w.is_deleted).length,
  }
}

const saveWebsite = async () => {
  saving.value = true
  message.value = ''
  try {
    if (editingWebsite.value) {
      await websitesAPI.updateWebsite(editingWebsite.value.id, websiteForm.value)
      message.value = 'Website updated successfully'
    } else {
      await websitesAPI.createWebsite(websiteForm.value)
      message.value = 'Website created successfully'
    }
    messageSuccess.value = true
    closeModal()
    await loadWebsites()
  } catch (e) {
    message.value = 'Failed to save website: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const editWebsite = (website) => {
  editingWebsite.value = website
  websiteForm.value = {
    name: website.name || '',
    domain: website.domain || '',
    contact_email: website.contact_email || '',
    admin_notifications_email: website.admin_notifications_email || '',
    contact_phone: website.contact_phone || '',
    theme_color: website.theme_color || '#000000',
    is_active: website.is_active !== undefined ? website.is_active : true,
    allow_registration: website.allow_registration !== undefined ? website.allow_registration : true,
    allow_guest_checkout: website.allow_guest_checkout || false,
    meta_title: website.meta_title || '',
    meta_description: website.meta_description || '',
  }
  showCreateModal.value = true
}

const viewWebsiteDetail = async (website) => {
  try {
    const res = await websitesAPI.getWebsite(website.id)
    viewingWebsite.value = res.data
  } catch (e) {
    message.value = 'Failed to load website details: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeWebsiteDetail = () => {
  viewingWebsite.value = null
}

const viewSEOSettings = (website) => {
  selectedWebsite.value = website
  seoForm.value = {
    meta_title: website.meta_title || '',
    meta_description: website.meta_description || '',
    google_analytics_id: website.google_analytics_id || '',
    google_search_console_id: website.google_search_console_id || '',
    bing_webmaster_id: website.bing_webmaster_id || '',
    enable_live_chat: website.enable_live_chat || false,
    communication_widget_type: website.communication_widget_type || '',
    tawkto_widget_id: website.tawkto_widget_id || '',
    tawkto_property_id: website.tawkto_property_id || '',
    communication_widget_config: website.communication_widget_config || {},
  }
  showSEOModal.value = true
}

const saveSEOSettings = async () => {
  saving.value = true
  message.value = ''
  try {
    await websitesAPI.updateSEOSettings(selectedWebsite.value.id, seoForm.value)
    message.value = 'SEO settings updated successfully'
    messageSuccess.value = true
    closeSEOModal()
    await loadWebsites()
  } catch (e) {
    message.value = 'Failed to save SEO settings: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const closeSEOModal = () => {
  showSEOModal.value = false
  selectedWebsite.value = null
}

// Integration Management Functions
const viewIntegrations = async (website) => {
  selectedWebsite.value = website
  showIntegrationsModal.value = true
  await loadIntegrations(website.id)
}

const closeIntegrationsModal = () => {
  showIntegrationsModal.value = false
  selectedWebsite.value = null
  integrations.value = []
  integrationSearch.value = ''
  integrationTypeFilter.value = ''
}

const loadIntegrations = async (websiteId) => {
  integrationsLoading.value = true
  try {
    const response = await websitesAPI.listIntegrations({ website: websiteId })
    integrations.value = response.data.results || response.data || []
  } catch (error) {
    message.value = 'Failed to load integrations: ' + (error.response?.data?.detail || error.message)
    messageSuccess.value = false
  } finally {
    integrationsLoading.value = false
  }
}

const filteredIntegrations = computed(() => {
  let filtered = integrations.value

  if (integrationSearch.value) {
    const search = integrationSearch.value.toLowerCase()
    filtered = filtered.filter(i => 
      i.integration_type?.toLowerCase().includes(search) ||
      i.name?.toLowerCase().includes(search) ||
      i.description?.toLowerCase().includes(search)
    )
  }

  if (integrationTypeFilter.value) {
    const categoryMap = {
      'stripe': ['stripe', 'paypal', 'razorpay', 'square', 'mollie'],
      'sendgrid': ['sendgrid', 'mailgun', 'ses', 'postmark'],
      'twilio': ['twilio', 'nexmo', 'aws_sns'],
      's3': ['s3', 'do_spaces', 'gcs'],
      'cloudflare': ['cloudflare', 'cloudfront'],
      'google_oauth': ['google_oauth', 'facebook_oauth', 'github_oauth'],
      'facebook_pixel': ['facebook_pixel', 'pinterest_tag', 'hotjar'],
      'intercom': ['intercom', 'zendesk']
    }
    const types = categoryMap[integrationTypeFilter.value] || [integrationTypeFilter.value]
    filtered = filtered.filter(i => types.includes(i.integration_type))
  }

  return filtered
})

const getIntegrationDisplayName = (type) => {
  const names = {
    stripe: 'Stripe',
    paypal: 'PayPal',
    sendgrid: 'SendGrid',
    twilio: 'Twilio',
    s3: 'AWS S3',
    do_spaces: 'DigitalOcean Spaces',
    cloudflare: 'Cloudflare',
    google_oauth: 'Google OAuth',
    facebook_pixel: 'Facebook Pixel',
    intercom: 'Intercom',
    openai: 'OpenAI',
  }
  return names[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const openIntegrationForm = (integration = null) => {
  editingIntegration.value = integration
  if (integration) {
    integrationForm.value = {
      website: integration.website,
      integration_type: integration.integration_type,
      name: integration.name || '',
      description: integration.description || '',
      api_key: '', // Don't show existing keys for security
      secret_key: '',
      access_token: '',
      configJson: JSON.stringify(integration.config || {}, null, 2),
      is_active: integration.is_active,
    }
  } else {
    integrationForm.value = {
      website: selectedWebsite.value.id,
      integration_type: '',
      name: '',
      description: '',
      api_key: '',
      secret_key: '',
      access_token: '',
      configJson: '{}',
      is_active: true,
    }
  }
  showIntegrationFormModal.value = true
}

const closeIntegrationForm = () => {
  showIntegrationFormModal.value = false
  editingIntegration.value = null
  integrationForm.value = {
    website: null,
    integration_type: '',
    name: '',
    description: '',
    api_key: '',
    secret_key: '',
    access_token: '',
    configJson: '{}',
    is_active: true,
  }
}

const saveIntegration = async () => {
  savingIntegration.value = true
  message.value = ''
  try {
    let config = {}
    try {
      config = JSON.parse(integrationForm.value.configJson || '{}')
    } catch (e) {
      message.value = 'Invalid JSON in configuration field'
      messageSuccess.value = false
      savingIntegration.value = false
      return
    }

    const data = {
      website: integrationForm.value.website,
      integration_type: integrationForm.value.integration_type,
      name: integrationForm.value.name || undefined,
      description: integrationForm.value.description || undefined,
      api_key: integrationForm.value.api_key || undefined,
      secret_key: integrationForm.value.secret_key || undefined,
      access_token: integrationForm.value.access_token || undefined,
      config: config,
      is_active: integrationForm.value.is_active,
    }

    if (editingIntegration.value) {
      await websitesAPI.updateIntegration(editingIntegration.value.id, data)
      message.value = 'Integration updated successfully'
    } else {
      await websitesAPI.createIntegration(data)
      message.value = 'Integration created successfully'
    }
    messageSuccess.value = true
    closeIntegrationForm()
    await loadIntegrations(selectedWebsite.value.id)
  } catch (error) {
    message.value = 'Failed to save integration: ' + (error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message)
    messageSuccess.value = false
  } finally {
    savingIntegration.value = false
  }
}

const deleteIntegration = async (id) => {
  if (!confirm('Are you sure you want to delete this integration? This action cannot be undone.')) {
    return
  }
  try {
    await websitesAPI.deleteIntegration(id)
    message.value = 'Integration deleted successfully'
    messageSuccess.value = true
    await loadIntegrations(selectedWebsite.value.id)
  } catch (error) {
    message.value = 'Failed to delete integration: ' + (error.response?.data?.detail || error.message)
    messageSuccess.value = false
  }
}

const toggleActive = async (website) => {
  try {
    await websitesAPI.patchWebsite(website.id, { is_active: !website.is_active })
    message.value = `Website ${website.is_active ? 'deactivated' : 'activated'} successfully`
    messageSuccess.value = true
    await loadWebsites()
  } catch (e) {
    message.value = 'Failed to update website: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const softDeleteWebsite = async (website) => {
  if (!confirm(`Soft delete "${website.name}"? This will mark it as deleted but not remove it permanently.`)) return
  try {
    await websitesAPI.softDeleteWebsite(website.id)
    message.value = 'Website soft deleted successfully'
    messageSuccess.value = true
    await loadWebsites()
  } catch (e) {
    message.value = 'Failed to delete website: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const restoreWebsite = async (website) => {
  try {
    await websitesAPI.restoreWebsite(website.id)
    message.value = 'Website restored successfully'
    messageSuccess.value = true
    await loadWebsites()
  } catch (e) {
    message.value = 'Failed to restore website: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const deleteWebsitePermanently = async (website) => {
  if (!confirm(`Permanently delete "${website.name}"? This action cannot be undone!`)) return
  try {
    await websitesAPI.deleteWebsite(website.id)
    message.value = 'Website deleted permanently'
    messageSuccess.value = true
    await loadWebsites()
  } catch (e) {
    message.value = 'Failed to delete website: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const viewActionLogs = (website) => {
  // Navigate to activity logs page with website filter
  // Use router to navigate to activity page with website filter
  router.push({
    name: 'ActivityLogs',
    query: { website_id: website.id }
  })
}

const toggleActionsMenu = (websiteId) => {
  actionsMenuOpen.value = actionsMenuOpen.value === websiteId ? null : websiteId
}

const openTermsModal = async (website) => {
  selectedWebsite.value = website
  showTermsModal.value = true
  message.value = ''

  // Load existing terms page for this website (if any)
  try {
    const params = { website: website.domain?.replace(/^https?:\/\//, '').replace(/^www\./, '') }
    const res = await websitesAPI.getStaticPage('terms', params)
    const page = res.data
    termsForm.value = {
      title: page.title || 'Terms & Conditions',
      content: page.content || '',
      language: page.language || 'en',
      meta_title: page.meta_title || page.title || 'Terms & Conditions',
      meta_description: page.meta_description || '',
      last_updated: page.last_updated || null,
      version: page.version || null,
    }
  } catch (e) {
    // If 404, initialize empty terms for this website
    console.warn('No existing terms page found, starting fresh:', e?.response?.status)
    termsForm.value = {
      title: 'Terms & Conditions',
      content: '',
      language: 'en',
      meta_title: '',
      meta_description: '',
      last_updated: null,
      version: null,
    }
  }
}

const closeTermsModal = () => {
  showTermsModal.value = false
  selectedWebsite.value = null
}

const saveTerms = async () => {
  if (!selectedWebsite.value) return

  saving.value = true
  message.value = ''

  try {
    const payload = {
      title: termsForm.value.title,
      content: termsForm.value.content,
      language: termsForm.value.language || 'en',
      meta_title: termsForm.value.meta_title || termsForm.value.title,
      meta_description: termsForm.value.meta_description || '',
    }

    const res = await websitesAPI.updateTerms(selectedWebsite.value.id, payload)
    const page = res.data?.page || {}

    termsForm.value.last_updated = page.last_updated || null
    termsForm.value.version = page.version || null

    message.value = 'Terms & Conditions updated successfully'
    messageSuccess.value = true
    showTermsModal.value = false
  } catch (e) {
    console.error('Failed to save terms:', e)
    message.value =
      'Failed to save terms: ' +
      (e.response?.data?.detail || e.response?.data?.error || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingWebsite.value = null
  websiteForm.value = {
    name: '',
    domain: '',
    contact_email: '',
    contact_phone: '',
    theme_color: '#000000',
    is_active: true,
    allow_registration: true,
    allow_guest_checkout: false,
    meta_title: '',
    meta_description: '',
  }
}

const resetFilters = () => {
  filters.value = { status: '', search: '' }
  loadWebsites()
}

const getStatusBadgeClass = (website) => {
  if (website.is_deleted) return 'bg-gray-100 text-gray-800'
  if (website.is_active) return 'bg-green-100 text-green-800'
  return 'bg-red-100 text-red-800'
}

const getStatusDotClass = (website) => {
  if (website.is_deleted) return 'bg-gray-500'
  if (website.is_active) return 'bg-green-500'
  return 'bg-red-500'
}

const getStatusText = (website) => {
  if (website.is_deleted) return 'Deleted'
  if (website.is_active) return 'Active'
  return 'Inactive'
}

const formatDomain = (domain) => {
  if (!domain) return '—'
  try {
    const url = new URL(domain)
    return url.hostname.replace(/^www\./, '')
  } catch {
    return domain.replace(/^https?:\/\//, '').replace(/^www\./, '')
  }
}

const getWebsiteInitials = (website) => {
  const name = website.name || 'W'
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(async () => {
  await loadWebsites()
  
  // Close actions menu when clicking outside
  document.addEventListener('click', (e) => {
    const clickedElement = e.target
    const isClickInsideMenu = clickedElement.closest('.relative') || clickedElement.closest('[class*="absolute"]')
    if (!isClickInsideMenu) {
      actionsMenuOpen.value = null
    }
  })
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
.website-table-row td {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}
</style>

