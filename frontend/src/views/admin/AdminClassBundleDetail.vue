<template>
  <div class="space-y-6 p-6">
    <!-- Header with Back Button -->
    <div class="flex items-center gap-4 mb-2">
      <router-link
        to="/admin/class-management"
        class="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="text-sm font-medium">Back to Class Management</span>
      </router-link>
    </div>
    
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading class bundle details...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

    <div v-else-if="bundle" class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
              📚
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Class Bundle #{{ bundle.id }}</h1>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ bundle.bundle_name || bundle.name || 'Class bundle order' }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-wrap mt-2">
            <span 
              class="px-3 py-1.5 text-xs font-semibold rounded-full cursor-help relative group transition-all hover:scale-105" 
              :class="getStatusClass(bundle.status)"
            >
              <span class="flex items-center gap-1.5">
                <span>{{ getStatusIcon(bundle.status) }}</span>
                <span>{{ getStatusLabel(bundle.status) }}</span>
              </span>
              <!-- Tooltip -->
              <span class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-800 text-white text-xs rounded-lg shadow-xl whitespace-normal max-w-xs opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                <div class="font-semibold mb-1">{{ getStatusLabel(bundle.status) }}</div>
                <div class="text-gray-300">{{ getStatusTooltip(bundle.status) }}</div>
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                  <div class="w-2 h-2 bg-gray-900 dark:bg-gray-800 transform rotate-45"></div>
                </div>
              </span>
            </span>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            @click="editingBundle = !editingBundle"
            :class="[
              'px-4 py-2.5 rounded-lg font-medium transition-all flex items-center gap-2 shadow-sm',
              editingBundle
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md'
            ]"
            :title="editingBundle ? 'Cancel editing' : 'Edit bundle details'"
          >
            <svg v-if="!editingBundle" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>{{ editingBundle ? 'Cancel' : 'Edit' }}</span>
          </button>
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div v-if="!editingBundle" class="border-b border-gray-200 dark:border-gray-700">
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
      <div v-if="editingBundle" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-blue-300 dark:border-blue-700 shadow-lg p-6">
        <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">Edit Class Bundle</h3>
        <form @submit.prevent="saveBundle" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
              <select
                v-model="editForm.status"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="not_started">Not Started</option>
                <option value="in_progress">In Progress</option>
                <option value="exhausted">Exhausted</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Total Price ($)</label>
              <input
                v-model.number="editForm.total_price"
                type="number"
                step="0.01"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deposit Required ($)</label>
              <input
                v-model.number="editForm.deposit_required"
                type="number"
                step="0.01"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Number of Classes</label>
              <input
                v-model.number="editForm.number_of_classes"
                type="number"
                min="1"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
            <textarea
              v-model="editForm.description"
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
      <div v-if="!editingBundle && activeTab === 'overview'" class="space-y-6">
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
                <span class="font-medium text-gray-600 dark:text-gray-400">Bundle ID:</span>
                <span class="font-mono text-gray-900 dark:text-white">#{{ bundle.id }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Status:</span>
                <span 
                  class="px-3 py-1.5 text-xs font-semibold rounded-full cursor-help relative group transition-all hover:scale-105" 
                  :class="getStatusClass(bundle.status)"
                >
                  <span class="flex items-center gap-1.5">
                    <span>{{ getStatusIcon(bundle.status) }}</span>
                    <span>{{ getStatusLabel(bundle.status) }}</span>
                  </span>
                  <!-- Tooltip -->
                  <span class="absolute bottom-full right-0 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-800 text-white text-xs rounded-lg shadow-xl whitespace-normal max-w-xs opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                    <div class="font-semibold mb-1">{{ getStatusLabel(bundle.status) }}</div>
                    <div class="text-gray-300">{{ getStatusTooltip(bundle.status) }}</div>
                    <div class="absolute top-full right-4 -mt-1">
                      <div class="w-2 h-2 bg-gray-900 dark:bg-gray-800 transform rotate-45"></div>
                    </div>
                  </span>
                </span>
              </div>
              <div v-if="bundle.bundle_name || bundle.name" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Bundle Name:</span>
                <span class="text-gray-900 dark:text-white">{{ bundle.bundle_name || bundle.name }}</span>
              </div>
              <div v-if="bundle.number_of_classes" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Number of Classes:</span>
                <span class="text-gray-900 dark:text-white">{{ bundle.number_of_classes }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Created:</span>
                <span class="text-gray-900 dark:text-white">{{ formatDate(bundle.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Client Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Client Information</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Client:</span>
                <span class="text-gray-900 dark:text-white">{{ bundle.client?.username || bundle.client?.email || 'N/A' }}</span>
              </div>
              <div v-if="bundle.client?.email" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Email:</span>
                <span class="text-gray-900 dark:text-white">{{ bundle.client.email }}</span>
              </div>
            </div>
          </div>

          <!-- Writer Information -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Writer Information</h3>
              <button
                @click="openAssignWriterModal"
                :class="[
                  'text-sm px-3 py-1 rounded transition-colors',
                  bundle.assigned_writer
                    ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                ]"
              >
                {{ bundle.assigned_writer ? 'Reassign Writer' : 'Assign Writer' }}
              </button>
            </div>
            <div v-if="bundle.assigned_writer" class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Writer:</span>
                <span class="text-gray-900 dark:text-white">
                  {{ bundle.assigned_writer?.username || bundle.assigned_writer?.email || 'N/A' }}
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
                <span class="font-medium text-gray-600 dark:text-gray-400">Total Price:</span>
                <span class="text-lg font-bold text-gray-900 dark:text-white">${{ formatCurrency(bundle.total_price || bundle.price || 0) }}</span>
              </div>
              <div v-if="bundle.deposit_required || bundle.deposit_amount" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Deposit Required:</span>
                <span class="text-gray-900 dark:text-white">${{ formatCurrency(bundle.deposit_required || bundle.deposit_amount || 0) }}</span>
              </div>
              <div v-if="bundle.deposit_paid" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Deposit Paid:</span>
                <span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Yes</span>
              </div>
              <div v-if="bundle.balance_remaining" class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Balance Remaining:</span>
                <span class="text-gray-900 dark:text-white">${{ formatCurrency(bundle.balance_remaining) }}</span>
              </div>
            </div>
          </div>

          <!-- Bundle Details -->
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Bundle Description</h3>
            <p v-if="bundle.description" class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ bundle.description }}</p>
            <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic">No description provided</p>
          </div>
        </div>
      </div>

      <!-- Messages Tab -->
      <div v-if="!editingBundle && activeTab === 'messages'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm min-h-[500px]">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span>💬</span>
                <span>Class Bundle Messages</span>
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Communicate with client and writer about this class bundle</p>
            </div>
            <button
              @click="createNewMessageThread"
              :disabled="creatingThread"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 font-medium shadow-sm"
              title="Start a new conversation"
            >
              <span v-if="creatingThread" class="animate-spin">⏳</span>
              <span v-else>➕</span>
              <span>{{ creatingThread ? 'Creating...' : 'New Message' }}</span>
            </button>
          </div>
        </div>
        <SimplifiedOrderMessages 
          :order-id="bundle.id" 
          :show-thread-list="true" 
          @thread-created="handleThreadCreated"
          ref="messagesComponent"
        />
      </div>

      <!-- Files Tab -->
      <div v-if="!editingBundle && activeTab === 'files'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span>📁</span>
                <span>Bundle Files</span>
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Upload and manage files for this class bundle</p>
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
                      <button
                        @click="downloadFile(file)"
                        class="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs font-medium flex items-center gap-1"
                        title="Download"
                      >
                        <span>⬇️</span>
                        <span>Download</span>
                      </button>
                      <button
                        @click="deleteFile(file.id)"
                        class="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-xs font-medium flex items-center gap-1"
                        title="Delete"
                      >
                        <span>🗑️</span>
                        <span>Delete</span>
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
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Upload files for Class Bundle #{{ bundle.id }}</p>
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
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.zip,.rar,.xls,.xlsx,.ppt,.pptx"
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
                  class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600"
                >
                  <option :value="null">Select Category (Optional)</option>
                  <optgroup v-if="universalCategories.length > 0" label="Universal Categories">
                    <option v-for="category in universalCategories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </optgroup>
                  <optgroup v-if="websiteSpecificCategories.length > 0" :label="`Categories for ${bundle.website?.name || 'This Website'}`">
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
                <span class="text-green-600 dark:text-green-400 text-xl">✅</span>
                <span class="text-green-700 dark:text-green-300">{{ uploadSuccess }}</span>
              </div>
              <div v-if="uploadError" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2">
                <span class="text-red-600 dark:text-red-400 text-xl">❌</span>
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
      <div v-if="!editingBundle && activeTab === 'history'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
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
            <div class="text-2xl">{{ getHistoryIcon(item.action || item.action_type || 'updated') }}</div>
            <div class="flex-1">
              <div class="font-medium text-gray-900 dark:text-white">{{ item.description || item.message || item.action || 'Activity' }}</div>
              <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {{ formatDateTime(item.created_at || item.timestamp || item.date) }}
                <span v-if="item.user || item.actor"> • by {{ item.user_username || item.actor?.username || item.user || item.actor || 'System' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Related Tab -->
      <div v-if="!editingBundle && activeTab === 'related'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
              <span class="text-indigo-600 dark:text-indigo-400 text-lg">🔗</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Related Items & Links</h3>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-if="bundle.client || bundle.client_id" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <span class="text-green-600 dark:text-green-400 text-xl">👤</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Client Profile</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ bundle.client?.username || bundle.client_username || bundle.client?.email || bundle.client_email || 'Client' }}</div>
                </div>
                <router-link
                  v-if="bundle.client?.id || bundle.client_id"
                  :to="`/admin/users/${bundle.client?.id || bundle.client_id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View client profile"
                >
                  →
                </router-link>
              </div>
            </div>
            <div v-if="bundle.assigned_writer || bundle.assigned_writer_id" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                  <span class="text-indigo-600 dark:text-indigo-400 text-xl">✍️</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Writer Profile</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ bundle.assigned_writer?.username || bundle.assigned_writer_username || bundle.assigned_writer?.email || 'Writer' }}</div>
                </div>
                <router-link
                  v-if="bundle.assigned_writer?.id || bundle.assigned_writer_id"
                  :to="`/admin/users/${bundle.assigned_writer?.id || bundle.assigned_writer_id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View writer profile"
                >
                  →
                </router-link>
                <span v-else class="text-gray-400">—</span>
              </div>
            </div>
            <div v-if="bundle.website || bundle.website_id" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <span class="text-blue-600 dark:text-blue-400 text-xl">🌐</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Website</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">{{ bundle.website?.name || bundle.website?.domain || 'Website' }}</div>
                </div>
                <router-link
                  v-if="bundle.website?.id || bundle.website_id"
                  :to="`/admin/websites/${bundle.website?.id || bundle.website_id}`"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View website"
                >
                  →
                </router-link>
              </div>
            </div>
            <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                  <span class="text-purple-600 dark:text-purple-400 text-xl">⚙️</span>
                </div>
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">Class Management</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">Manage class bundles and installments</div>
                </div>
                <router-link
                  to="/admin/class-management"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                  title="View class management"
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
            v-if="!bundle.deposit_paid"
            @click="showPayDepositModal = true"
            :disabled="processing"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Pay Deposit
          </button>
          <button
            v-if="bundle.deposit_paid && !bundle.installments_configured"
            @click="showConfigureInstallmentsModal = true"
            :disabled="processing"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            Configure Installments
          </button>
        </div>
      </div>
    </div>
  </div>

    <!-- Assign Writer Modal -->
    <div v-if="showAssignWriterModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ bundle?.assigned_writer ? 'Reassign Writer' : 'Assign Writer' }}
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

          <div v-if="assignForm.writer_id" class="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Bonus Amount (Optional)
                <span class="text-gray-400 text-xs font-normal">Leave empty to auto-calculate from bundle pricing</span>
              </label>
              <input
                v-model.number="assignForm.bonus_amount"
                type="number"
                step="0.01"
                min="0"
                placeholder="Auto-calculated if empty"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
              <p v-if="bundle?.total_price" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Bundle total: ${{ formatCurrency(bundle.total_price) }} | 
                Suggested (60%): ${{ formatCurrency(bundle.total_price * 0.6) }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Admin Notes (Optional)</label>
              <textarea
                v-model="assignForm.admin_notes"
                rows="3"
                placeholder="Add any notes about this assignment..."
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              ></textarea>
            </div>
          </div>

          <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="showAssignWriterModal = false"
              class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="assignWriter"
              :disabled="!assignForm.writer_id || processing"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ processing ? 'Assigning...' : (bundle?.assigned_writer ? 'Reassign Writer' : 'Assign Writer') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pay Deposit Modal -->
    <div v-if="showPayDepositModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Pay Deposit</h3>
          <button
            @click="showPayDepositModal = false"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
          >
            ✕
          </button>
        </div>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          Deposit Amount: ${{ formatCurrency(bundle?.deposit_required || bundle?.deposit_amount || 0) }}
        </p>
        <div class="flex gap-3">
          <button
            @click="showPayDepositModal = false"
            class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="payDeposit"
            :disabled="processing"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {{ processing ? 'Processing...' : 'Pay Deposit' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Configure Installments Modal -->
    <div v-if="showConfigureInstallmentsModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Configure Installments</h3>
          <button
            @click="showConfigureInstallmentsModal = false"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
          >
            ✕
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Number of Installments</label>
            <input
              v-model.number="installmentForm.installment_count"
              type="number"
              min="2"
              max="12"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Interval (Weeks)</label>
            <input
              v-model.number="installmentForm.interval_weeks"
              type="number"
              min="1"
              max="4"
              class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div class="flex gap-3 pt-4">
            <button
              @click="showConfigureInstallmentsModal = false"
              class="flex-1 px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="configureInstallments"
              :disabled="!installmentForm.installment_count || processing"
              class="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 transition-colors"
            >
              {{ processing ? 'Configuring...' : 'Configure' }}
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
import classManagementAPI from '@/api/class-management'
import { writerAssignmentAPI, orderFilesAPI, activityLogsAPI, communicationsAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import SimplifiedOrderMessages from '@/components/order/SimplifiedOrderMessages.vue'
import FileUpload from '@/components/common/FileUpload.vue'

const route = useRoute()
const router = useRouter()
const { success: showSuccessToast, error: showErrorToast } = useToast()

const loading = ref(true)
const error = ref(null)
const bundle = ref(null)
const processing = ref(false)
const saving = ref(false)
const editingBundle = ref(false)
const showAssignWriterModal = ref(false)
const showPayDepositModal = ref(false)
const showConfigureInstallmentsModal = ref(false)
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
const messagesComponent = ref(null)
const uploadForm = ref({ category: null })

const universalCategories = computed(() => {
  return fileCategories.value.filter(cat => cat.website === null || cat.is_universal)
})

const websiteSpecificCategories = computed(() => {
  if (!bundle.value?.website?.id) return []
  return fileCategories.value.filter(cat => cat.website === bundle.value.website.id)
})

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
  total_price: 0,
  deposit_required: 0,
  number_of_classes: 0,
  description: ''
})

const assignForm = ref({
  writer_id: null,
  bonus_amount: null,
  admin_notes: ''
})

const installmentForm = ref({
  installment_count: 2,
  interval_weeks: 2
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

const loadBundle = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await classManagementAPI.getBundle(route.params.id)
    bundle.value = res.data
    initializeEditForm()
    // Load related data
    await Promise.all([
      loadFiles(),
      loadHistory(),
      loadCategories()
    ])
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load class bundle'
    console.error('Error loading class bundle:', err)
  } finally {
    loading.value = false
  }
}

const loadFiles = async () => {
  if (!bundle.value) return
  loadingFiles.value = true
  try {
    const params = { 
      order: bundle.value.id,
      order_id: bundle.value.id,
      class_bundle: bundle.value.id,
      class_bundle_id: bundle.value.id
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
  if (!bundle.value) return
  loadingHistory.value = true
  try {
    const params = { 
      object_type: 'class_bundle', 
      object_id: bundle.value.id,
      ordering: '-created_at'
    }
    const res = await activityLogsAPI.list(params)
    history.value = res.data.results || res.data || []
    
    // If no history from API, create a basic entry from bundle data
    if (history.value.length === 0 && bundle.value) {
      const classHistory = []
      if (bundle.value.created_at) {
        classHistory.push({
          id: 'created',
          action: 'created',
          description: `Class bundle #${bundle.value.id} was created`,
          created_at: bundle.value.created_at,
          timestamp: bundle.value.created_at,
          user: bundle.value.client?.username || bundle.value.client_username || 'System',
          user_username: bundle.value.client?.username || bundle.value.client_username || 'System'
        })
      }
      if (bundle.value.updated_at && bundle.value.updated_at !== bundle.value.created_at) {
        classHistory.push({
          id: 'updated',
          action: 'updated',
          description: `Class bundle was last updated`,
          created_at: bundle.value.updated_at,
          timestamp: bundle.value.updated_at,
          user: 'System',
          user_username: 'System'
        })
      }
      history.value = classHistory
    }
  } catch (err) {
    console.error('Error loading history:', err)
    // Fallback: create basic history from bundle data
    if (bundle.value) {
      history.value = [{
        id: 'created',
        action: 'created',
        description: `Class bundle #${bundle.value.id} was created`,
        created_at: bundle.value.created_at || new Date().toISOString(),
        timestamp: bundle.value.created_at || new Date().toISOString(),
        user: bundle.value.client?.username || bundle.value.client_username || 'System',
        user_username: bundle.value.client?.username || bundle.value.client_username || 'System'
      }]
    } else {
      history.value = []
    }
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

const handleFileSelect = (fileList) => {
  uploadedFiles.value = fileList.map(file => ({ file, name: file.name, size: file.size }))
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

const downloadFile = async (file) => {
  try {
    if (file.download_url || file.url) {
      window.open(file.download_url || file.url, '_blank')
      return
    }
    const blob = await orderFilesAPI.download(file.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.file_name || 'download'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (err) {
    showErrorToast('Failed to download file: ' + (err.response?.data?.detail || err.message))
  }
}

const uploadSelectedFiles = async () => {
  if (uploadedFiles.value.length === 0 || !bundle.value) return
  
  uploadingFiles.value = true
  uploadError.value = ''
  uploadSuccess.value = ''
  
  try {
    const uploadPromises = uploadedFiles.value.map(async (fileObj) => {
      const formData = new FormData()
      formData.append('file', fileObj.file || fileObj)
      formData.append('order', bundle.value.id)
      formData.append('class_bundle', bundle.value.id)
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

const createNewMessageThread = async () => {
  if (!bundle.value) return
  
  creatingThread.value = true
  try {
    const response = await communicationsAPI.startThreadForOrder(bundle.value.id)
    showSuccessToast('Conversation started! You can now send messages.')
    
    // If messagesComponent ref exists, trigger it to reload threads
    if (messagesComponent.value && typeof messagesComponent.value.loadThreads === 'function') {
      await messagesComponent.value.loadThreads()
    } else {
      // Fallback: reload bundle to refresh threads
      await loadBundle()
    }
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.response?.data?.error || 'Failed to start conversation'
    showErrorToast(errorMsg)
    console.error('Error creating message thread:', err)
  } finally {
    creatingThread.value = false
  }
}

const handleThreadCreated = async (threadData) => {
  // Reload threads in the messages component
  if (messagesComponent.value && typeof messagesComponent.value.loadThreads === 'function') {
    await messagesComponent.value.loadThreads()
  }
  // Also reload bundle to ensure everything is in sync
  await loadBundle()
}

const initializeEditForm = () => {
  if (bundle.value) {
    editForm.value = {
      status: bundle.value.status || 'in_progress',
      total_price: parseFloat(bundle.value.total_price || bundle.value.price || 0),
      deposit_required: parseFloat(bundle.value.deposit_required || bundle.value.deposit_amount || 0),
      number_of_classes: bundle.value.number_of_classes || 0,
      description: bundle.value.description || ''
    }
  }
}

const saveBundle = async () => {
  saving.value = true
  try {
    await classManagementAPI.updateBundle(bundle.value.id, editForm.value)
    showSuccessToast('Class bundle updated successfully!')
    editingBundle.value = false
    await loadBundle()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to update bundle')
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  editingBundle.value = false
  initializeEditForm()
}

const payDeposit = async () => {
  processing.value = true
  try {
    await classManagementAPI.payDeposit(bundle.value.id, {})
    showSuccessToast('Deposit payment processed successfully!')
    showPayDepositModal.value = false
    await loadBundle()
  } catch (err) {
    showErrorToast(err.response?.data?.detail || 'Failed to process deposit payment')
  } finally {
    processing.value = false
  }
}

const configureInstallments = async () => {
  if (!installmentForm.value.installment_count) {
    showErrorToast('Please specify the number of installments')
    return
  }
  
  processing.value = true
  try {
    await classManagementAPI.configureInstallments(bundle.value.id, installmentForm.value)
    showSuccessToast('Installments configured successfully!')
    showConfigureInstallmentsModal.value = false
    installmentForm.value = { installment_count: 2, interval_weeks: 2 }
    await loadBundle()
  } catch (err) {
    showErrorToast(err.response?.data?.error || err.response?.data?.detail || 'Failed to configure installments')
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
  if (!assignForm.value.writer_id) {
    showErrorToast('Please select a writer')
    return
  }
  
  processing.value = true
  try {
    const assignmentData = {
      writer_id: assignForm.value.writer_id
    }
    
    // Include bonus_amount if provided
    if (assignForm.value.bonus_amount) {
      assignmentData.bonus_amount = assignForm.value.bonus_amount
    }
    
    // Include admin_notes if provided
    if (assignForm.value.admin_notes) {
      assignmentData.admin_notes = assignForm.value.admin_notes
    }
    
    await classManagementAPI.assignWriter(bundle.value.id, assignmentData)
    showSuccessToast('Writer assigned successfully!')
    showAssignWriterModal.value = false
    assignForm.value = { writer_id: null, bonus_amount: null, admin_notes: '' }
    await loadBundle()
  } catch (err) {
    showErrorToast(err.response?.data?.error || err.response?.data?.detail || 'Failed to assign writer')
  } finally {
    processing.value = false
  }
}

const openAssignWriterModal = () => {
  showAssignWriterModal.value = true
  loadWriters()
  // Pre-fill bonus amount suggestion if bundle has pricing
  if (bundle.value?.total_price && !assignForm.value.bonus_amount) {
    assignForm.value.bonus_amount = parseFloat((bundle.value.total_price * 0.6).toFixed(2))
  }
}

const getStatusClass = (status) => {
  const classes = {
    'not_started': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'exhausted': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const getStatusLabel = (status) => {
  const labels = {
    'not_started': 'Not Started',
    'in_progress': 'In Progress',
    'exhausted': 'Exhausted',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
  }
  return labels[status] || status
}

const getStatusTooltip = (status) => {
  const tooltips = {
    'not_started': 'Bundle has been created but classes have not started yet.',
    'in_progress': 'Bundle is active and classes are currently in progress.',
    'exhausted': 'All classes in the bundle have been used up.',
    'completed': 'Bundle has been fully completed and all classes delivered.',
    'cancelled': 'Bundle has been cancelled.',
  }
  return tooltips[status] || `Status: ${getStatusLabel(status)}`
}

const getStatusIcon = (status) => {
  const icons = {
    'not_started': '⏸️',
    'in_progress': '🔄',
    'exhausted': '⚠️',
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
  loadBundle()
})
</script>

