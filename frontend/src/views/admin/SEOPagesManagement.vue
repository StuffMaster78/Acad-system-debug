<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">SEO Pages Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage service pages, SEO metadata, FAQs, and resources</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create SEO Page
      </button>
    </div>

    <!-- Website Switcher (for superadmins or when multiple websites available) -->
    <div v-if="canSelectWebsite && availableWebsites.length > 1" class="card p-4 dark:bg-gray-800 dark:border-gray-700">
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

    <!-- Filters -->
    <div class="card p-4 dark:bg-gray-800 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="filters.is_active"
            @change="loadPages"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Service Pages Table -->
    <EnhancedDataTable
      :items="pages"
      :columns="seoPagesColumns"
      :loading="loading"
      :searchable="true"
      search-placeholder="Search pages by title, slug..."
      :search-fields="['title', 'slug', 'short_description']"
      :sortable="true"
      :striped="true"
      empty-message="No SEO pages found"
      empty-description="Create your first SEO page to get started"
      empty-icon="📄"
    >
      <template #cell-title="{ item }">
        <div>
          <div class="font-semibold text-gray-900 dark:text-gray-100">{{ item.title }}</div>
          <div class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{{ item.short_description || item.header || '' }}</div>
        </div>
      </template>
      <template #cell-website="{ item }" v-if="!selectedWebsiteId || canSelectWebsite">
        <div v-if="item.website" class="text-sm">
          <div class="font-medium text-gray-900 dark:text-gray-100">{{ item.website.name }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">{{ item.website.domain }}</div>
        </div>
        <span v-else class="text-gray-400 dark:text-gray-500">—</span>
      </template>
      <template #cell-status="{ item }">
        <span
          :class="item.is_published || item.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'"
          class="px-3 py-1 rounded-full text-xs font-semibold"
        >
          {{ (item.is_published || item.is_active) ? 'Published' : 'Draft' }}
        </span>
      </template>
      <template #cell-views="{ value }">
        <span class="font-medium text-gray-900 dark:text-gray-100">{{ value || 0 }}</span>
      </template>
      <template #cell-actions="{ item }">
        <div class="flex items-center gap-2">
          <button
            @click="previewPage(item)"
            class="px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 dark:bg-green-900/20 rounded-md hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors flex items-center gap-1"
            title="Preview Page"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Preview
          </button>
          <button
            @click="viewPage(item)"
            class="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 dark:bg-blue-900/20 rounded-md hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
            title="View Page"
          >
            View
          </button>
          <button
            @click="editPage(item)"
            class="px-3 py-1.5 text-xs font-medium text-purple-600 bg-purple-50 dark:bg-purple-900/20 rounded-md hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
            title="Edit Page"
          >
            Edit
          </button>
          <div class="relative">
            <button
              @click="toggleActionsMenu(item.id)"
              class="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 rounded-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              title="More Actions"
            >
              ⋯
            </button>
            <div
              v-if="actionsMenuOpen === item.id"
              class="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-xl z-20 border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div class="py-1">
                <button
                  @click="viewSEO(item); actionsMenuOpen = null"
                  class="block w-full text-left px-4 py-2 text-sm text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors flex items-center gap-2"
                >
                  <span>⚙️</span> SEO Settings
                </button>
                <button
                  @click="manageFAQs(item); actionsMenuOpen = null"
                  class="block w-full text-left px-4 py-2 text-sm text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors flex items-center gap-2"
                >
                  <span>❓</span> Manage FAQs
                </button>
                <button
                  @click="manageResources(item); actionsMenuOpen = null"
                  class="block w-full text-left px-4 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors flex items-center gap-2"
                >
                  <span>🔗</span> Manage Resources
                </button>
                <button
                  @click="manageCTAs(item); actionsMenuOpen = null"
                  class="block w-full text-left px-4 py-2 text-sm text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors flex items-center gap-2"
                >
                  <span>📢</span> Manage CTAs
                </button>
                <button
                  @click="viewEditHistory(item); actionsMenuOpen = null"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
                >
                  <span>📜</span> Edit History
                </button>
                <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                <button
                  @click="deletePageAction(item); actionsMenuOpen = null"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2"
                >
                  <span>🗑️</span> Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </EnhancedDataTable>

    <!-- Edit History Modal -->
    <div v-if="showEditHistoryModal && selectedPageForHistory" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeEditHistoryModal">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-indigo-50 to-indigo-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Edit History</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ selectedPageForHistory?.title || 'Page' }}</p>
            </div>
            <button 
              @click="closeEditHistoryModal" 
              class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 text-2xl"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="editHistoryLoading" class="flex items-center justify-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
          
          <div v-else-if="editHistoryError" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
            {{ editHistoryError }}
          </div>
          
          <div v-else-if="editHistory.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <p class="text-lg">No edit history found</p>
            <p class="text-sm mt-2">This page hasn't been edited yet.</p>
          </div>
          
          <div v-else class="space-y-4">
            <div
              v-for="(entry, index) in editHistory"
              :key="entry.id || index"
              class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div class="flex items-start justify-between mb-3">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="font-semibold text-gray-900 dark:text-white">
                      {{ entry.edited_by_username || entry.edited_by?.username || entry.edited_by?.email || 'Unknown User' }}
                    </span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">
                      {{ formatDateTime(entry.edited_at) }}
                    </span>
                  </div>
                  <div v-if="entry.changes_summary" class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    {{ entry.changes_summary }}
                  </div>
                </div>
              </div>
              
              <div v-if="entry.fields_changed && entry.fields_changed.length > 0" class="mt-2">
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="field in entry.fields_changed"
                    :key="field"
                    class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded"
                  >
                    {{ field }}
                  </span>
                </div>
              </div>
              
              <div v-if="entry.previous_content || entry.current_content" class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div v-if="entry.previous_content" class="p-3 bg-gray-50 dark:bg-gray-900/50 rounded border border-gray-200 dark:border-gray-700">
                  <div class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Previous Content</div>
                  <div class="text-sm text-gray-700 dark:text-gray-300 line-clamp-6">
                    {{ entry.previous_content.substring(0, 200) }}{{ entry.previous_content.length > 200 ? '...' : '' }}
                  </div>
                </div>
                <div v-if="entry.current_content" class="p-3 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800">
                  <div class="text-xs font-medium text-green-700 dark:text-green-300 mb-2">Current Content</div>
                  <div class="text-sm text-gray-700 dark:text-gray-300 line-clamp-6">
                    {{ entry.current_content.substring(0, 200) }}{{ entry.current_content.length > 200 ? '...' : '' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <button
            @click="closeEditHistoryModal"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Page Modal -->
    <div v-if="showCreateModal || editingPage" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-indigo-50 to-indigo-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ editingPage ? 'Edit SEO Page' : 'Create SEO Page' }}</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ editingPage ? 'Update page content and SEO settings' : 'Create a new SEO-optimized page' }}</p>
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
          
          <form @submit.prevent="savePage" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Website *</label>
                <select 
                  v-model="pageForm.website_id" 
                  :disabled="!canSelectWebsite || availableWebsites.length === 0"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Select Website</option>
                  <option v-for="website in availableWebsites" :key="website.id" :value="website.id">
                    {{ formatWebsiteName(website) }}
                  </option>
                </select>
                <p v-if="!canSelectWebsite && availableWebsites.length === 0" class="text-xs text-gray-500 mt-1">No websites available</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Title <span class="text-red-500">*</span>
                </label>
                <input 
                  v-model="pageForm.title" 
                  type="text" 
                  required 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="Enter page title"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Slug</label>
              <input 
                v-model="pageForm.slug" 
                type="text" 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder="auto-generated-from-title"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Leave empty to auto-generate from title</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Short Description</label>
              <textarea 
                v-model="pageForm.short_description" 
                rows="3" 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder="Brief description of the page"
              ></textarea>
            </div>
            
            <!-- Content Section -->
            <div class="space-y-4" data-seo-section>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Page Content</h3>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Content <span class="text-red-500">*</span>
                </label>
                <RichTextEditor
                  v-model="pageForm.content"
                  :required="true"
                  placeholder="Write your service page content..."
                  toolbar="full"
                  height="400px"
                  :allow-images="true"
                />
              </div>
            </div>
            
            <!-- SEO Settings Section -->
            <div class="space-y-4" data-seo-section>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">SEO Settings</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Meta Title</label>
                  <input 
                    v-model="pageForm.meta_title" 
                    type="text" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="SEO meta title (50-60 chars)"
                    maxlength="60"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ pageForm.meta_title?.length || 0 }}/60 characters</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Meta Description</label>
                  <textarea 
                    v-model="pageForm.meta_description" 
                    rows="3" 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="SEO meta description (150-160 chars)"
                    maxlength="160"
                  ></textarea>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ pageForm.meta_description?.length || 0 }}/160 characters</p>
                </div>
              </div>
            </div>
            
            <!-- Settings Section -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Settings</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <input
                    v-model="pageForm.is_active"
                    type="checkbox"
                    id="page_active"
                    class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label for="page_active" class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Active
                  </label>
                  <p class="ml-auto text-xs text-gray-500 dark:text-gray-400">Page is visible to users</p>
                </div>
                <div class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <input
                    v-model="pageForm.is_featured"
                    type="checkbox"
                    id="page_featured"
                    class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label for="page_featured" class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Featured
                  </label>
                  <p class="ml-auto text-xs text-gray-500 dark:text-gray-400">Highlight on homepage</p>
                </div>
              </div>
            </div>
            
            <!-- FAQs Section -->
            <div class="border-t pt-4">
              <div class="flex items-center justify-between mb-3">
                <label class="block text-sm font-medium">FAQs (Optional)</label>
                <button
                  type="button"
                  @click="addFAQ"
                  class="text-sm text-blue-600 hover:underline"
                >
                  + Add FAQ
                </button>
              </div>
              <div v-if="pageForm.faqs_data && pageForm.faqs_data.length" class="space-y-3">
                <div
                  v-for="(faq, index) in pageForm.faqs_data"
                  :key="index"
                  class="border rounded p-3 bg-gray-50"
                >
                  <div class="flex justify-between items-start mb-2">
                    <span class="text-sm font-medium text-gray-700">FAQ {{ index + 1 }}</span>
                    <button
                      type="button"
                      @click="removeFAQ(index)"
                      class="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div class="space-y-2">
                    <div>
                      <label class="block text-xs font-medium mb-1">Question *</label>
                      <input
                        v-model="faq.question"
                        type="text"
                        required
                        placeholder="Enter question..."
                        class="w-full border rounded px-2 py-1 text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium mb-1">Answer *</label>
                      <RichTextEditor
                        v-model="faq.answer"
                        :required="true"
                        placeholder="Enter answer..."
                        toolbar="basic"
                        height="150px"
                        :allow-images="true"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-gray-500 italic">No FAQs added. Click "+ Add FAQ" to add one.</p>
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
              <div v-if="pageForm.resources_data && pageForm.resources_data.length" class="space-y-4">
                <div
                  v-for="(resource, index) in pageForm.resources_data"
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
            @click="savePage"
            :disabled="saving"
            class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
            {{ saving ? 'Saving...' : (editingPage ? 'Update Page' : 'Create Page') }}
          </button>
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
import { ref, computed, onMounted, watch } from 'vue'
import seoPagesAPI from '@/api/seo-pages'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
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

const pages = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingPage = ref(null)
const actionsMenuOpen = ref(null)
const showEditHistoryModal = ref(false)
const selectedPageForHistory = ref(null)
const editHistory = ref([])
const editHistoryLoading = ref(false)
const editHistoryError = ref(null)

// Website selection
const availableWebsites = ref([])
const canSelectWebsite = ref(false)
const selectedWebsiteId = ref(null)

const filters = ref({
  search: '',
  is_active: '',
})

// Computed: Selected website object
const selectedWebsite = computed(() => {
  if (!selectedWebsiteId.value) return null
  return availableWebsites.value.find(w => w.id === selectedWebsiteId.value) || null
})

// Computed: Website stats
const websiteStats = computed(() => {
  if (!selectedWebsite.value) return null
  
  const websitePages = pages.value.filter(p => 
    p.website?.id === selectedWebsite.value.id || p.website_id === selectedWebsite.value.id
  )
  
  return {
    totalPosts: websitePages.length,
    publishedPosts: websitePages.filter(p => p.is_published).length,
    draftPosts: websitePages.filter(p => !p.is_published).length,
    totalCategories: 0, // SEO pages don't have categories
    activeCategories: 0,
    totalAuthors: 0, // SEO pages don't have authors
  }
})

const pageForm = ref({
  website_id: null,
  title: '',
  slug: '',
  short_description: '',
  content: '',
  meta_title: '',
  meta_description: '',
  is_active: true,
  is_featured: false,
  faqs_data: [],
  resources_data: [],
})

const message = ref('')
const messageSuccess = ref(false)

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadPages()
  }, 500)
}

const loadPages = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.is_active) params.is_active = filters.value.is_active
    
    // Add website filter if a specific website is selected
    if (selectedWebsiteId.value) {
      params.website_id = selectedWebsiteId.value
    }
    
    const res = await seoPagesAPI.listServicePages(params)
    pages.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    message.value = 'Failed to load pages: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const savePage = async () => {
  saving.value = true
  message.value = ''
  try {
    if (editingPage.value) {
      await seoPagesAPI.updateServicePage(editingPage.value.id, pageForm.value)
      message.value = 'SEO page updated successfully'
    } else {
      await seoPagesAPI.createServicePage(pageForm.value)
      message.value = 'SEO page created successfully'
    }
    messageSuccess.value = true
    closeModal()
    await loadPages()
  } catch (e) {
    message.value = 'Failed to save page: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data))
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const editPage = (page) => {
  editingPage.value = page
  pageForm.value = {
    website_id: page.website?.id || null,
    title: page.title || '',
    slug: page.slug || '',
    short_description: page.short_description || '',
    content: page.content || '',
    meta_title: page.meta_title || '',
    meta_description: page.meta_description || '',
    is_active: page.is_active !== undefined ? page.is_active : true,
    is_featured: page.is_featured || false,
    faqs_data: page.faqs?.map(faq => ({
      question: faq.question || '',
      answer: faq.answer || ''
    })) || [],
    resources_data: page.resources?.map(resource => ({
      title: resource.title || '',
      url: resource.url || '',
      description: resource.description || ''
    })) || [],
  }
  showCreateModal.value = true
}

const viewPage = (page) => {
  // Navigate to public page view
  if (page.slug) {
    window.open(`/page/${page.slug}`, '_blank')
  } else {
    showError('Page slug not available')
  }
}

const showPreviewModal = ref(false)
const previewContentType = ref(null)
const previewContentId = ref(null)
const previewContentSlug = ref(null)
const previewWebsiteId = ref(null)

const previewPage = (page) => {
  previewContentType.value = 'seo'
  previewContentId.value = page.id
  previewContentSlug.value = page.slug
  previewWebsiteId.value = page.website?.id || null
  showPreviewModal.value = true
}

const viewSEO = (page) => {
  // Open edit modal with SEO section focused
  editPage(page)
  // Scroll to SEO section if needed
  setTimeout(() => {
    const seoSection = document.querySelector('[data-seo-section]')
    if (seoSection) {
      seoSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, 100)
}

const manageFAQs = (page) => {
  // Open edit modal with FAQs section
  editPage(page)
}

const manageResources = (page) => {
  // Open edit modal with Resources section
  editPage(page)
}

const addFAQ = () => {
  if (!pageForm.value.faqs_data) {
    pageForm.value.faqs_data = []
  }
  pageForm.value.faqs_data.push({
    question: '',
    answer: ''
  })
}

const removeFAQ = (index) => {
  pageForm.value.faqs_data.splice(index, 1)
}

const addResource = () => {
  if (!pageForm.value.resources_data) {
    pageForm.value.resources_data = []
  }
  pageForm.value.resources_data.push({
    title: '',
    url: '',
    description: ''
  })
}

const removeResource = (index) => {
  pageForm.value.resources_data.splice(index, 1)
}

const manageCTAs = (page) => {
  // Open edit modal with CTAs section
  editPage(page)
  showSuccess('Use the edit form to manage CTAs for this page')
}

const viewEditHistory = async (page) => {
  selectedPageForHistory.value = page
  showEditHistoryModal.value = true
  editHistoryLoading.value = true
  editHistoryError.value = null
  editHistory.value = []
  
  try {
    // Try to get edit history from API
    const response = await seoPagesAPI.getServicePageEditHistory(page.id)
    editHistory.value = response.data?.results || response.data || []
    
    // If no edit history endpoint, try revisions
    if (editHistory.value.length === 0) {
      try {
        const revisionsResponse = await seoPagesAPI.getServicePageRevisions(page.id)
        const revisions = revisionsResponse.data?.results || revisionsResponse.data || []
        // Transform revisions to edit history format
        editHistory.value = revisions.map((rev, index) => ({
          id: rev.id,
          edited_by: rev.created_by,
          edited_by_username: rev.created_by?.username || rev.created_by?.email,
          edited_at: rev.created_at,
          changes_summary: rev.change_summary || `Revision ${rev.revision_number}`,
          fields_changed: [],
          previous_content: index < revisions.length - 1 ? revisions[index + 1]?.content : '',
          current_content: rev.content
        }))
      } catch (revisionError) {
        // If both fail, show empty state
        // No edit history or revisions available
      }
    }
  } catch (error) {
    editHistoryError.value = error.response?.data?.detail || error.message || 'Failed to load edit history'
    console.error('Error loading edit history:', error)
  } finally {
    editHistoryLoading.value = false
  }
}

const closeEditHistoryModal = () => {
  showEditHistoryModal.value = false
  selectedPageForHistory.value = null
  editHistory.value = []
  editHistoryError.value = null
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const deletePageAction = async (page) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${page.title}"?`,
    'Delete SEO Page',
    {
      details: `This action cannot be undone. The SEO page "${page.title}" and all its associated content (FAQs, resources, CTAs) will be permanently deleted.`,
      confirmText: 'Delete Page',
      cancelText: 'Cancel',
      icon: '🗑️'
    }
  )
  
  if (!confirmed) {
    actionsMenuOpen.value = null
    return
  }
  
  try {
    await seoPagesAPI.deleteServicePage(page.id)
    message.value = 'SEO page deleted'
    messageSuccess.value = true
    await loadPages()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const toggleActionsMenu = (pageId) => {
  actionsMenuOpen.value = actionsMenuOpen.value === pageId ? null : pageId
}

const loadAvailableWebsites = async () => {
  try {
    const res = await seoPagesAPI.getAvailableWebsites()
    availableWebsites.value = res.data?.websites || []
    canSelectWebsite.value = res.data?.can_select_website || false
    
    // Auto-select website if only one available or if user can't select
    if (availableWebsites.value.length === 1) {
      selectedWebsiteId.value = availableWebsites.value[0].id
      if (!pageForm.value.website_id) {
        pageForm.value.website_id = availableWebsites.value[0].id
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
  // Reload pages for the selected website
  loadPages()
}

const closeModal = () => {
  showCreateModal.value = false
  editingPage.value = null
  pageForm.value = {
    website_id: null,
    title: '',
    slug: '',
    short_description: '',
    content: '',
    meta_title: '',
    meta_description: '',
    is_active: true,
    is_featured: false,
    faqs_data: [],
    resources_data: [],
  }
}

const resetFilters = () => {
  filters.value = { search: '', is_active: '' }
  loadPages()
}

// Column definitions for SEO Pages table
const seoPagesColumns = computed(() => {
  const columns = [
    {
      key: 'title',
      label: 'Title',
      sortable: true
    }
  ]
  
  if (!selectedWebsiteId.value || canSelectWebsite.value) {
    columns.push({
      key: 'website',
      label: 'Website',
      sortable: false
    })
  }
  
  columns.push(
    {
      key: 'slug',
      label: 'Slug',
      sortable: true,
      format: (value) => value || 'N/A'
    },
    {
      key: 'is_published',
      label: 'Status',
      sortable: true,
      class: 'w-28'
    },
    {
      key: 'click_count',
      label: 'Views',
      sortable: true,
      align: 'right',
      class: 'w-24',
      format: (value) => value || 0
    },
    {
      key: 'updated_at',
      label: 'Updated',
      sortable: true,
      format: (value, item) => formatDate(item.updated_at || item.created_at),
      class: 'w-40'
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      align: 'right',
      class: 'w-48'
    }
  )
  
  return columns
})

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

onMounted(async () => {
  await Promise.all([loadPages(), loadAvailableWebsites()])
  
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
      actionsMenuOpen.value = null
    }
  })
})

// Watch for modal opening to load websites if needed
watch(showCreateModal, async (isOpen) => {
  if (isOpen && !availableWebsites.value.length) {
    await loadAvailableWebsites()
  }
})

// Watch for website changes to reload data
watch(selectedWebsiteId, () => {
  loadPages()
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

