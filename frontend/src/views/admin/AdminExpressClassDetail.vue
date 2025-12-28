<template>
  <div class="space-y-6 p-6">
    <!-- Header with Back Button -->
    <div class="flex items-center gap-4 mb-2">
      <router-link
        to="/admin/express-classes"
        class="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="text-sm font-medium">Back to Express Classes</span>
      </router-link>
    </div>
    
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading express class details...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

    <div v-else-if="expressClass" class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
              🚀
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Express Class #{{ expressClass.id }}</h1>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ expressClass.course || expressClass.discipline || 'Express class order' }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-wrap mt-2">
            <span 
              class="px-3 py-1.5 text-xs font-semibold rounded-full cursor-help relative group transition-all hover:scale-105" 
              :class="getStatusClass(expressClass.status)"
            >
              <span class="flex items-center gap-1.5">
                <span>{{ getStatusIcon(expressClass.status) }}</span>
                <span>{{ getStatusLabel(expressClass.status) }}</span>
              </span>
              <!-- Tooltip -->
              <span class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-800 text-white text-xs rounded-lg shadow-xl whitespace-normal max-w-xs opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                <div class="font-semibold mb-1">{{ getStatusLabel(expressClass.status) }}</div>
                <div class="text-gray-300">{{ getStatusTooltip(expressClass.status) }}</div>
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                  <div class="w-2 h-2 bg-gray-900 dark:bg-gray-800 transform rotate-45"></div>
                </div>
              </span>
            </span>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            @click="editingClass = !editingClass"
            :class="[
              'px-4 py-2.5 rounded-lg font-medium transition-all flex items-center gap-2 shadow-sm',
              editingClass
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md'
            ]"
            :title="editingClass ? 'Cancel editing' : 'Edit class details'"
          >
            <svg v-if="!editingClass" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>{{ editingClass ? 'Cancel' : 'Edit' }}</span>
          </button>
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div v-if="!editingClass" class="border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8 overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors flex items-center gap-2',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            <span>{{ tab.icon }}</span>
            <span>{{ tab.label }}</span>
            <span v-if="tab.badge" class="ml-2 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              {{ tab.badge }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Edit Form -->
      <div v-if="editingClass" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-blue-300 dark:border-blue-700 shadow-lg p-6">
        <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">Edit Express Class</h3>
        <form @submit.prevent="saveClass" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
              <select
                v-model="editForm.status"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="inquiry">Inquiry</option>
                <option value="scope_review">Scope Review</option>
                <option value="priced">Priced</option>
                <option value="assigned">Assigned</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Price ($)</label>
              <input
                v-model.number="editForm.price"
                type="number"
                step="0.01"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Course</label>
              <input
                v-model="editForm.course"
                type="text"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Discipline</label>
              <input
                v-model="editForm.discipline"
                type="text"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Date</label>
              <input
                v-model="editForm.start_date"
                type="date"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Date</label>
              <input
                v-model="editForm.end_date"
                type="date"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Instructions</label>
            <textarea
              v-model="editForm.instructions"
              rows="5"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Admin Notes</label>
            <textarea
              v-model="editForm.admin_notes"
              rows="4"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>
          <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              @click="cancelEdit"
              class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Overview Tab -->
      <div v-if="!editingClass && activeTab === 'overview'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Left Column -->
        <div class="space-y-6">
          <!-- Basic Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Basic Information</h3>
            </div>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Class ID:</span>
                <span class="font-mono text-gray-900 dark:text-white">#{{ expressClass.id }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Status:</span>
                <span 
                  class="px-3 py-1.5 text-xs font-semibold rounded-full cursor-help relative group transition-all hover:scale-105" 
                  :class="getStatusClass(expressClass.status)"
                >
                  <span class="flex items-center gap-1.5">
                    <span>{{ getStatusIcon(expressClass.status) }}</span>
                    <span>{{ getStatusLabel(expressClass.status) }}</span>
                  </span>
                  <!-- Tooltip -->
                  <span class="absolute bottom-full right-0 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-800 text-white text-xs rounded-lg shadow-xl whitespace-normal max-w-xs opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                    <div class="font-semibold mb-1">{{ getStatusLabel(expressClass.status) }}</div>
                    <div class="text-gray-300">{{ getStatusTooltip(expressClass.status) }}</div>
                    <div class="absolute top-full right-4 -mt-1">
                      <div class="w-2 h-2 bg-gray-900 dark:bg-gray-800 transform rotate-45"></div>
                    </div>
                  </span>
                </span>
              </div>
              <div v-if="expressClass.course" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Course:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.course }}</span>
              </div>
              <div v-if="expressClass.discipline" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Discipline:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.discipline }}</span>
              </div>
              <div v-if="expressClass.institution" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Institution:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.institution }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Start Date:</span>
                <span class="text-gray-900 dark:text-white">{{ formatDate(expressClass.start_date) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">End Date:</span>
                <span class="text-gray-900 dark:text-white">{{ formatDate(expressClass.end_date) }}</span>
              </div>
            </div>
          </div>

          <!-- Client Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Client Information</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Client:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.client_username || expressClass.client_email || 'N/A' }}</span>
              </div>
              <div v-if="expressClass.client_email" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Email:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.client_email }}</span>
              </div>
            </div>
          </div>

          <!-- Writer Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Writer Information</h3>
              <button
                v-if="expressClass.status === 'priced'"
                @click="openAssignWriterModal"
                :class="[
                  'text-sm px-3 py-1 rounded transition-colors',
                  expressClass.assigned_writer
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                ]"
              >
                {{ expressClass.assigned_writer ? 'Reassign Writer' : 'Assign Writer' }}
              </button>
            </div>
            <div v-if="expressClass.assigned_writer || expressClass.assigned_writer_username" class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Writer:</span>
                <span class="text-gray-900 dark:text-white">
                  {{ expressClass.assigned_writer_username || expressClass.assigned_writer?.username || 'N/A' }}
                </span>
              </div>
            </div>
            <div v-else class="text-sm text-gray-500 dark:text-gray-400 italic">
              No writer assigned
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="space-y-6">
          <!-- Financial Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Financial Information</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Price:</span>
                <span class="text-lg font-bold text-gray-900 dark:text-white">
                  <span v-if="expressClass.price">${{ formatCurrency(expressClass.price) }}</span>
                  <span v-else class="text-gray-400 italic">Not priced</span>
                </span>
              </div>
              <div v-if="expressClass.price_approved" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Price Approved:</span>
                <span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Yes</span>
              </div>
              <div v-if="expressClass.installments_needed" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Installments:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.installments_needed }}</span>
              </div>
            </div>
          </div>

          <!-- Workload Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Workload</h3>
            <div class="space-y-3 text-sm">
              <div v-if="expressClass.number_of_discussion_posts" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Discussion Posts:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.number_of_discussion_posts }}</span>
              </div>
              <div v-if="expressClass.number_of_discussion_posts_replies" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Discussion Replies:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.number_of_discussion_posts_replies }}</span>
              </div>
              <div v-if="expressClass.number_of_assignments" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Assignments:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.number_of_assignments }}</span>
              </div>
              <div v-if="expressClass.total_workload_in_pages" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Total Pages:</span>
                <span class="text-gray-900 dark:text-white">{{ expressClass.total_workload_in_pages }}</span>
              </div>
            </div>
          </div>

          <!-- Instructions -->
          <div v-if="expressClass.instructions" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Instructions</h3>
            <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ expressClass.instructions }}</p>
          </div>

          <!-- Admin Notes -->
          <div v-if="expressClass.admin_notes" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Admin Notes</h3>
            <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ expressClass.admin_notes }}</p>
          </div>
        </div>
        </div>
      </div>

      <!-- Messages Tab -->
      <div v-if="!editingClass && activeTab === 'messages'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
        <SimplifiedOrderMessages :order-id="expressClass.id" :show-thread-list="true" @thread-created="loadClass" />
      </div>

      <!-- Files Tab -->
      <div v-if="!editingClass && activeTab === 'files'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span>📁</span>
                <span>Express Class Files</span>
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Upload and manage files for this express class</p>
            </div>
            <button
              @click="showFileUploadModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <span>➕</span>
              <span>Upload File</span>
            </button>
          </div>

          <div v-if="loadingFiles" class="text-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-4 text-gray-600 dark:text-gray-400">Loading files...</p>
          </div>

          <div v-else-if="files.length === 0" class="text-center py-12">
            <div class="text-4xl mb-4">📄</div>
            <p class="text-gray-600 dark:text-gray-400">No files uploaded yet</p>
            <button
              @click="showFileUploadModal = true"
              class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload First File
            </button>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">File</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Category</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Uploaded By</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="file in files" :key="file.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-2">
                      <span class="text-xl">📄</span>
                      <span class="text-sm font-medium text-gray-900 dark:text-white">{{ file.file_name || 'Unnamed' }}</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {{ getCategoryName(file.category) || '—' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {{ file.uploaded_by_username || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {{ formatDate(file.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex items-center gap-2">
                      <a
                        v-if="file.download_url || file.url"
                        :href="file.download_url || file.url"
                        target="_blank"
                        class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-200"
                        title="Download"
                      >
                        ⬇️
                      </a>
                      <button
                        @click="deleteFile(file.id)"
                        class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-200"
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- File Upload Modal -->
        <div v-if="showFileUploadModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="showFileUploadModal = false">
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between z-10">
              <div>
                <h3 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <span>📤</span>
                  <span>Upload Files</span>
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Upload files for Express Class #{{ expressClass.id }}</p>
              </div>
              <button
                @click="showFileUploadModal = false"
                class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                ✕
              </button>
            </div>
            
            <div class="p-6 space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select Files
                </label>
                <FileUpload
                  v-model="uploadedFiles"
                  :multiple="true"
                  :auto-upload="false"
                  :max-size="100 * 1024 * 1024"
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.zip,.rar"
                  label="Drop files here or click to browse"
                  @upload="handleFileSelect"
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category <span class="text-gray-400">(Optional)</span>
                </label>
                <select
                  v-model="uploadForm.category"
                  class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option :value="null">Select Category (Optional)</option>
                  <optgroup v-if="universalCategories.length > 0" label="Universal Categories">
                    <option v-for="category in universalCategories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </optgroup>
                  <optgroup v-if="websiteSpecificCategories.length > 0" :label="`Categories for ${expressClass.website?.name || 'This Website'}`">
                    <option v-for="category in websiteSpecificCategories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </optgroup>
                </select>
                <p v-if="uploadForm.category && getCategoryById(uploadForm.category)?.is_final_draft" class="text-xs text-orange-600 dark:text-orange-400 mt-1">
                  ⚠️ Final Draft files require payment completion for client download
                </p>
              </div>

              <div v-if="uploadSuccess" class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-2">
                <svg class="w-5 h-5 text-green-700 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span class="text-green-700 dark:text-green-300">{{ uploadSuccess }}</span>
              </div>
              <div v-if="uploadError" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2">
                <svg class="w-5 h-5 text-red-700 dark:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span class="text-red-700 dark:text-red-300">{{ uploadError }}</span>
              </div>
              
              <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  @click="clearUploadForm"
                  class="px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  Clear
                </button>
                <button
                  type="button"
                  @click="uploadSelectedFiles"
                  :disabled="uploadedFiles.length === 0 || uploadingFiles"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  <span v-if="uploadingFiles" class="animate-spin">⏳</span>
                  <span>{{ uploadingFiles ? 'Uploading...' : `Upload ${uploadedFiles.length} File(s)` }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- History Tab -->
      <div v-if="!editingClass && activeTab === 'history'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
        <div class="flex items-center gap-2 mb-6">
          <div class="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
            <span class="text-purple-600 dark:text-purple-400 text-lg">📜</span>
          </div>
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Activity History</h3>
        </div>
        <div v-if="loadingHistory" class="text-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading history...</p>
        </div>
        <div v-else-if="history.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
          <p>No activity history available</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="item in history"
            :key="item.id"
            class="flex items-start gap-4 p-4 border-l-4 border-blue-500 bg-gray-50 dark:bg-gray-900/50 rounded-r-lg"
          >
            <div class="text-2xl">{{ getHistoryIcon(item.action) }}</div>
            <div class="flex-1">
              <div class="font-medium text-gray-900 dark:text-white">{{ item.description || item.action }}</div>
              <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {{ formatDateTime(item.created_at || item.timestamp) }}
                <span v-if="item.user"> • by {{ item.user_username || item.user }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Related Tab -->
      <div v-if="!editingClass && activeTab === 'related'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
              <span class="text-indigo-600 dark:text-indigo-400 text-lg">🔗</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Related Items & Links</h3>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-if="expressClass.client" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <span class="text-green-600 dark:text-green-400 text-xl">👤</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Client Profile</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ expressClass.client_username || expressClass.client_email }}</div>
                </div>
                <router-link
                  :to="`/admin/users/${expressClass.client?.id || expressClass.client_id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View client profile"
                >
                  →
                </router-link>
              </div>
            </div>
            <div v-if="expressClass.assigned_writer" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                  <span class="text-indigo-600 dark:text-indigo-400 text-xl">✍️</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Writer Profile</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ expressClass.assigned_writer_username || expressClass.assigned_writer?.username }}</div>
                </div>
                <router-link
                  :to="`/admin/users/${expressClass.assigned_writer?.id || expressClass.assigned_writer_id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View writer profile"
                >
                  →
                </router-link>
              </div>
            </div>
            <div v-if="expressClass.website" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <span class="text-blue-600 dark:text-blue-400 text-xl">🌐</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Website</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ expressClass.website?.name || expressClass.website?.domain }}</div>
                </div>
                <router-link
                  :to="`/admin/websites/${expressClass.website?.id || expressClass.website_id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View website"
                >
                  →
                </router-link>
              </div>
            </div>
            <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                  <span class="text-orange-600 dark:text-orange-400 text-xl">🚀</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">All Express Classes</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">View all express classes</div>
                </div>
                <router-link
                  to="/admin/express-classes"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View all express classes"
                >
                  →
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Admin Actions -->
      <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Admin Actions</h3>
        <div class="flex gap-3 flex-wrap">
          <button
            v-if="expressClass.status === 'inquiry'"
            @click="showReviewScopeModal = true"
            :disabled="processing"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Review Scope
          </button>
          <button
            v-if="expressClass.status === 'assigned'"
            @click="startProgress"
            :disabled="processing"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            Start Progress
          </button>
          <button
            v-if="expressClass.status === 'in_progress'"
            @click="completeClass"
            :disabled="processing"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            Complete Class
          </button>
        </div>
      </div>
    </div>

    <!-- Assign Writer Modal -->
    <div v-if="showAssignWriterModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ expressClass?.assigned_writer ? 'Reassign Writer' : 'Assign Writer' }}
          </h3>
          <button
            @click="showAssignWriterModal = false"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
          >
            ✕
          </button>
        </div>

        <div v-if="loadingWriters" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading writers...</p>
        </div>

        <div v-else class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search Writers</label>
            <input
              v-model="writerSearch"
              type="text"
              placeholder="Search by name or email..."
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div class="max-h-64 overflow-y-auto border rounded-lg">
            <div
              v-for="writer in filteredWriters"
              :key="writer.id"
              @click="selectWriter(writer.id)"
              :class="[
                'p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-200 dark:border-gray-700',
                assignForm.writer_id === writer.id ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700' : ''
              ]"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ writer.username || writer.email }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ writer.email }}</p>
                  <p v-if="writer.writer_level" class="text-xs text-gray-400 dark:text-gray-500">
                    Level: {{ writer.writer_level.name || writer.writer_level }}
                  </p>
                </div>
                <div v-if="assignForm.writer_id === writer.id" class="text-blue-600 dark:text-blue-400">
                  ✓
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Bonus Amount ($) <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="assignForm.bonus_amount"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Payment amount for the class (paid as bonus)</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Admin Notes (Optional)</label>
            <textarea
              v-model="assignForm.admin_notes"
              rows="3"
              placeholder="Add notes about this assignment..."
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              @click="showAssignWriterModal = false"
              class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="assignWriter"
              :disabled="!assignForm.writer_id || !assignForm.bonus_amount || processing"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ processing ? 'Assigning...' : (expressClass?.assigned_writer ? 'Reassign Writer' : 'Assign Writer') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Scope Modal -->
    <div v-if="showReviewScopeModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Review Scope & Set Price</h3>
          <button
            @click="showReviewScopeModal = false"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
          >
            ✕
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Price ($) <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="scopeReviewForm.price"
              type="number"
              step="0.01"
              min="0"
              required
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Scope Review Notes</label>
            <textarea
              v-model="scopeReviewForm.scope_review_notes"
              rows="5"
              placeholder="Add notes about the scope review..."
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Admin Notes (Optional)</label>
            <textarea
              v-model="scopeReviewForm.admin_notes"
              rows="3"
              placeholder="Add internal admin notes..."
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              @click="showReviewScopeModal = false"
              class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="reviewScope"
              :disabled="!scopeReviewForm.price || processing"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ processing ? 'Reviewing...' : 'Review Scope & Set Price' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import expressClassesAPI from '@/api/express-classes'
import { writerAssignmentAPI, orderFilesAPI, activityLogsAPI, communicationsAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import SimplifiedOrderMessages from '@/components/order/SimplifiedOrderMessages.vue'
import FileUpload from '@/components/common/FileUpload.vue'

const route = useRoute()
const router = useRouter()
const { success: showSuccessToast, error: showErrorToast } = useToast()

const loading = ref(true)
const error = ref(null)
const expressClass = ref(null)
const processing = ref(false)
const saving = ref(false)
const editingClass = ref(false)
const showAssignWriterModal = ref(false)
const showReviewScopeModal = ref(false)
const loadingWriters = ref(false)
const writerSearch = ref('')
const availableWriters = ref([])
const activeTab = ref('overview')
const files = ref([])
const loadingFiles = ref(false)
const history = ref([])
const loadingHistory = ref(false)
const showFileUploadModal = ref(false)
const fileCategories = ref([])
const uploadedFiles = ref([])
const uploadingFiles = ref(false)
const uploadSuccess = ref('')
const uploadError = ref('')
const threads = ref([])
const creatingThread = ref(false)

const tabs = computed(() => {
  const baseTabs = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'messages', label: 'Messages', icon: '💬', badge: null },
    { id: 'files', label: 'Files', icon: '📁', badge: files.value.length || null },
    { id: 'history', label: 'History', icon: '📜' },
    { id: 'related', label: 'Related', icon: '🔗' },
  ]
  return baseTabs
})

const editForm = ref({
  status: '',
  price: 0,
  course: '',
  discipline: '',
  start_date: '',
  end_date: '',
  instructions: '',
  admin_notes: ''
})

const assignForm = ref({
  writer_id: null,
  bonus_amount: null,
  admin_notes: ''
})

const scopeReviewForm = ref({
  price: null,
  scope_review_notes: '',
  admin_notes: ''
})

const filteredWriters = computed(() => {
  if (!writerSearch.value) return availableWriters.value
  
  const search = writerSearch.value.toLowerCase()
  return availableWriters.value.filter(writer => {
    const name = (writer.username || '').toLowerCase()
    const email = (writer.email || '').toLowerCase()
    return name.includes(search) || email.includes(search)
  })
})

const loadClass = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await expressClassesAPI.get(route.params.id)
    expressClass.value = res.data
    initializeEditForm()
    // Load related data
    await Promise.all([
      loadFiles(),
      loadHistory(),
      loadCategories()
    ])
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load express class'
    console.error('Error loading express class:', err)
  } finally {
    loading.value = false
  }
}

const loadFiles = async () => {
  if (!expressClass.value) return
  loadingFiles.value = true
  try {
    const params = { 
      order_id: expressClass.value.id,
      express_class: expressClass.value.id,
      express_class_id: expressClass.value.id
    }
    const res = await orderFilesAPI.list(params)
    files.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Error loading files:', err)
    files.value = []
  } finally {
    loadingFiles.value = false
  }
}

const loadHistory = async () => {
  if (!expressClass.value) return
  loadingHistory.value = true
  try {
    const res = await activityLogsAPI.list({ object_type: 'express_class', object_id: expressClass.value.id })
    history.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Error loading history:', err)
    history.value = []
  } finally {
    loadingHistory.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await orderFilesAPI.listCategories()
    fileCategories.value = res.data.results || res.data || []
  } catch (err) {
    console.error('Error loading categories:', err)
    fileCategories.value = []
  }
}

const getCategoryName = (categoryId) => {
  const category = fileCategories.value.find(c => c.id === categoryId)
  return category?.name || null
}

const getCategoryById = (categoryId) => {
  return fileCategories.value.find(c => c.id === categoryId) || null
}

const universalCategories = computed(() => {
  return fileCategories.value.filter(cat => cat.is_universal || cat.website === null)
})

const websiteSpecificCategories = computed(() => {
  return fileCategories.value.filter(cat => !cat.is_universal && cat.website === expressClass.value?.website?.id)
})

const uploadForm = ref({
  category: null,
})

const handleFileSelect = (fileList) => {
  uploadedFiles.value = fileList.map(file => ({ file, name: file.name, size: file.size }))
}

const uploadSelectedFiles = async () => {
  if (uploadedFiles.value.length === 0 || !expressClass.value) return
  
  uploadingFiles.value = true
  uploadError.value = ''
  uploadSuccess.value = ''
  
  try {
    const uploadPromises = uploadedFiles.value.map(async (fileObj) => {
      const formData = new FormData()
      formData.append('file', fileObj.file || fileObj)
      formData.append('order_id', expressClass.value.id)
      formData.append('express_class', expressClass.value.id) // Link to express class
      if (uploadForm.value.category) {
        formData.append('category', uploadForm.value.category)
      }
      return await orderFilesAPI.upload(formData)
    })
    
    await Promise.all(uploadPromises)
    uploadSuccess.value = `Successfully uploaded ${uploadedFiles.value.length} file(s)!`
    uploadedFiles.value = []
    uploadForm.value.category = null
    await loadFiles()
    
    setTimeout(() => {
      uploadSuccess.value = ''
      if (uploadedFiles.value.length === 0) {
        showFileUploadModal.value = false
      }
    }, 3000)
  } catch (error) {
    uploadError.value = 'Failed to upload files: ' + (error.response?.data?.detail || error.message)
    setTimeout(() => {
      uploadError.value = ''
    }, 5000)
  } finally {
    uploadingFiles.value = false
  }
}

const clearUploadForm = () => {
  uploadedFiles.value = []
  uploadForm.value.category = null
  uploadError.value = ''
  uploadSuccess.value = ''
}

const deleteFile = async (fileId) => {
  if (!confirm('Are you sure you want to delete this file?')) return
  try {
    await orderFilesAPI.delete(fileId)
    showSuccessToast('File deleted successfully')
    await loadFiles()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to delete file')
  }
}

const getHistoryIcon = (action) => {
  const icons = {
    'created': '✨',
    'updated': '✏️',
    'status_changed': '🔄',
    'assigned': '👤',
    'completed': '🏁',
    'cancelled': '❌',
  }
  return icons[action] || '📝'
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const initializeEditForm = () => {
  if (expressClass.value) {
    editForm.value = {
      status: expressClass.value.status || '',
      price: parseFloat(expressClass.value.price || 0),
      course: expressClass.value.course || '',
      discipline: expressClass.value.discipline || '',
      start_date: expressClass.value.start_date ? expressClass.value.start_date.split('T')[0] : '',
      end_date: expressClass.value.end_date ? expressClass.value.end_date.split('T')[0] : '',
      instructions: expressClass.value.instructions || '',
      admin_notes: expressClass.value.admin_notes || ''
    }
  }
}

const saveClass = async () => {
  saving.value = true
  try {
    await expressClassesAPI.update(expressClass.value.id, editForm.value)
    showSuccessToast('Express class updated successfully!')
    editingClass.value = false
    await loadClass()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to update express class')
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  editingClass.value = false
  initializeEditForm()
}

const reviewScope = async () => {
  if (!scopeReviewForm.value.price) {
    showErrorToast('Price is required')
    return
  }
  
  processing.value = true
  try {
    await expressClassesAPI.reviewScope(expressClass.value.id, scopeReviewForm.value)
    showSuccessToast('Scope reviewed and price set successfully!')
    showReviewScopeModal.value = false
    scopeReviewForm.value = { price: null, scope_review_notes: '', admin_notes: '' }
    await loadClass()
  } catch (err) {
    showErrorToast(err.response?.data?.error || err.response?.data?.detail || 'Failed to review scope')
  } finally {
    processing.value = false
  }
}

const startProgress = async () => {
  if (!confirm('Are you sure you want to start progress on this express class?')) return
  
  processing.value = true
  try {
    await expressClassesAPI.startProgress(expressClass.value.id)
    showSuccessToast('Progress started successfully!')
    await loadClass()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to start progress')
  } finally {
    processing.value = false
  }
}

const completeClass = async () => {
  if (!confirm('Are you sure you want to mark this express class as completed?')) return
  
  processing.value = true
  try {
    await expressClassesAPI.complete(expressClass.value.id)
    showSuccessToast('Express class marked as completed!')
    await loadClass()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to complete express class')
  } finally {
    processing.value = false
  }
}

const loadWriters = async () => {
  loadingWriters.value = true
  try {
    const res = await writerAssignmentAPI.getAvailableWriters()
    availableWriters.value = res.data.writers || res.data.results || res.data || []
  } catch (err) {
    console.error('Error loading writers:', err)
    showErrorToast('Failed to load writers')
    availableWriters.value = []
  } finally {
    loadingWriters.value = false
  }
}

const selectWriter = (writerId) => {
  assignForm.value.writer_id = assignForm.value.writer_id === writerId ? null : writerId
}

const assignWriter = async () => {
  if (!assignForm.value.writer_id || !assignForm.value.bonus_amount) {
    showErrorToast('Please select a writer and enter bonus amount')
    return
  }
  
  processing.value = true
  try {
    await expressClassesAPI.assignWriter(expressClass.value.id, assignForm.value)
    showSuccessToast('Writer assigned successfully!')
    showAssignWriterModal.value = false
    assignForm.value = { writer_id: null, bonus_amount: null, admin_notes: '' }
    await loadClass()
  } catch (err) {
    showErrorToast(err.response?.data?.error || err.response?.data?.detail || 'Failed to assign writer')
  } finally {
    processing.value = false
  }
}

const openAssignWriterModal = () => {
  if (expressClass.value.status !== 'priced') {
    showErrorToast('Can only assign writer after price has been set')
    return
  }
  showAssignWriterModal.value = true
  loadWriters()
}

const getStatusClass = (status) => {
  const classes = {
    'inquiry': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'scope_review': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    'priced': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'assigned': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const getStatusLabel = (status) => {
  const labels = {
    'inquiry': 'Inquiry',
    'scope_review': 'Scope Review',
    'priced': 'Priced',
    'assigned': 'Assigned',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
  }
  return labels[status] || status
}

const getStatusTooltip = (status) => {
  const tooltips = {
    'inquiry': 'Client has submitted an inquiry. Awaiting admin review and scope assessment.',
    'scope_review': 'Admin is reviewing the scope and requirements to determine pricing.',
    'priced': 'Price has been set and approved. Ready for writer assignment.',
    'assigned': 'Writer has been assigned to this express class.',
    'in_progress': 'Writer is actively working on the class assignments.',
    'completed': 'Express class has been completed and delivered.',
    'cancelled': 'Express class has been cancelled.',
  }
  return tooltips[status] || `Status: ${getStatusLabel(status)}`
}

const getStatusIcon = (status) => {
  const icons = {
    'inquiry': '📝',
    'scope_review': '🔍',
    'priced': '💰',
    'assigned': '👤',
    'in_progress': '🔄',
    'completed': '✅',
    'cancelled': '❌',
  }
  return icons[status] || '📌'
}

const formatCurrency = (value) => {
  return parseFloat(value || 0).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

onMounted(() => {
  loadClass()
})
</script>

