<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">File Management</h1>
        <p class="mt-2 text-gray-600">Manage order files, extra service files, external links, and file configurations</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Order Files</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total_order_files || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Extra Service Files</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.total_extra_files || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending Deletions</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.pending_deletions || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">External Links</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.total_external_links || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Order Files Tab -->
    <div v-if="activeTab === 'order-files'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Order ID</label>
            <input
              v-model.number="filters.order_id"
              @input="debouncedSearch"
              type="number"
              placeholder="Filter by order ID"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Website</label>
            <select v-model="filters.website" @change="loadOrderFiles" class="w-full border rounded px-3 py-2">
              <option value="">All Websites</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Download Status</label>
            <select v-model="filters.is_downloadable" @change="loadOrderFiles" class="w-full border rounded px-3 py-2">
              <option value="">All</option>
              <option :value="true">Downloadable</option>
              <option :value="false">Locked</option>
            </select>
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Order Files Table -->
      <div class="card overflow-hidden">
        <div v-if="orderFilesLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Uploaded By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="file in orderFiles" :key="file.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ file.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <router-link :to="`/orders/${file.order}`" class="text-blue-600 hover:underline">
                  Order #{{ file.order }}
                </router-link>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ file.file?.split('/').pop() || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ file.uploaded_by || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ file.category?.name || 'Uncategorized' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  file.is_downloadable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                ]">
                  {{ file.is_downloadable ? 'Downloadable' : 'Locked' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(file.created_at) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button @click="downloadFile(file.id)" class="text-blue-600 hover:text-blue-900">Download</button>
                <button @click="toggleFileDownload(file.id)" class="text-yellow-600 hover:text-yellow-900">
                  {{ file.is_downloadable ? 'Lock' : 'Unlock' }}
                </button>
                <button @click="deleteFile(file.id)" class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!orderFilesLoading && orderFiles.length === 0" class="text-center py-12 text-gray-500">
          No order files found
        </div>
      </div>
    </div>

    <!-- Extra Service Files Tab -->
    <div v-if="activeTab === 'extra-files'" class="space-y-4">
      <!-- Similar structure to order files -->
      <div class="card overflow-hidden">
        <div v-if="extraFilesLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="file in extraFiles" :key="file.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ file.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <router-link :to="`/orders/${file.order}`" class="text-blue-600 hover:underline">
                  Order #{{ file.order }}
                </router-link>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ file.file?.split('/').pop() || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ file.service_type || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  file.is_downloadable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                ]">
                  {{ file.is_downloadable ? 'Downloadable' : 'Locked' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(file.created_at) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button @click="downloadExtraFile(file.id)" class="text-blue-600 hover:text-blue-900">Download</button>
                <button @click="toggleExtraFileDownload(file.id)" class="text-yellow-600 hover:text-yellow-900">
                  {{ file.is_downloadable ? 'Lock' : 'Unlock' }}
                </button>
                <button @click="deleteExtraFile(file.id)" class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!extraFilesLoading && extraFiles.length === 0" class="text-center py-12 text-gray-500">
          No extra service files found
        </div>
      </div>
    </div>

    <!-- External Links Tab -->
    <div v-if="activeTab === 'external-links'" class="space-y-4">
      <div class="card overflow-hidden">
        <div v-if="externalLinksLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Link</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="link in externalLinks" :key="link.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ link.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <router-link :to="`/orders/${link.order}`" class="text-blue-600 hover:underline">
                  Order #{{ link.order }}
                </router-link>
              </td>
              <td class="px-6 py-4 text-sm">
                <a :href="link.url" target="_blank" class="text-blue-600 hover:underline truncate block max-w-xs">
                  {{ link.url }}
                </a>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ link.description || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  link.status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                ]">
                  {{ link.status || 'Pending' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(link.created_at) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button v-if="link.status !== 'approved'" @click="approveExternalLink(link.id)" class="text-green-600 hover:text-green-900">Approve</button>
                <button @click="deleteExternalLink(link.id)" class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!externalLinksLoading && externalLinks.length === 0" class="text-center py-12 text-gray-500">
          No external links found
        </div>
      </div>
    </div>

    <!-- Deletion Requests Tab -->
    <div v-if="activeTab === 'deletion-requests'" class="space-y-4">
      <div class="card overflow-hidden">
        <div v-if="deletionRequestsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Requested By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="request in deletionRequests" :key="request.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ request.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                File ID: {{ request.file }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ request.requested_by || 'N/A' }}</td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ request.reason || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  request.status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                ]">
                  {{ request.status || 'Pending' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(request.created_at) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button v-if="request.status !== 'approved'" @click="approveDeletionRequest(request.id)" class="text-green-600 hover:text-green-900">Approve</button>
                <button @click="deleteDeletionRequest(request.id)" class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!deletionRequestsLoading && deletionRequests.length === 0" class="text-center py-12 text-gray-500">
          No deletion requests found
        </div>
      </div>
    </div>

    <!-- Configuration Tab -->
    <div v-if="activeTab === 'config'" class="space-y-4">
      <div class="card p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">File Upload Configuration</h3>
          <button @click="showConfigModal = true" class="btn btn-primary">Add Configuration</button>
        </div>
        <div v-if="configsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Max Size (MB)</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Allowed Extensions</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="config in configs" :key="config.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ config.website?.name || 'Default' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ config.max_upload_size || 'N/A' }}</td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ config.allowed_extensions?.join(', ') || 'All' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button @click="editConfig(config)" class="text-blue-600 hover:text-blue-900">Edit</button>
                <button @click="deleteConfig(config.id)" class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!configsLoading && configs.length === 0" class="text-center py-12 text-gray-500">
          No configurations found. Click "Add Configuration" to create one.
        </div>
      </div>
    </div>

    <!-- File Categories Tab -->
    <div v-if="activeTab === 'categories'" class="space-y-4">
      <div class="card p-4">
        <div class="flex justify-between items-start gap-4 mb-4">
          <div>
            <h3 class="text-lg font-semibold">File Categories</h3>
            <p class="text-sm text-gray-500">
              Configure the file types clients and writers can choose from (e.g. Order instructions, Writing guide, Sample paper, AI draft, Outline, My draft, Plagiarism report, Final paper, etc.).
            </p>
          </div>
          <button
            type="button"
            class="btn btn-primary"
            @click="openCreateCategory"
          >
            Add Category
          </button>
        </div>

        <div v-if="categoriesLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>

        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Website
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Final Draft
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Extra Service
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Allowed Extensions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="cat in categories" :key="cat.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ cat.name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ cat.website_name || 'Default / All' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    cat.is_final_draft ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-700'
                  ]"
                >
                  {{ cat.is_final_draft ? 'Yes' : 'No' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    cat.is_extra_service ? 'bg-indigo-100 text-indigo-800' : 'bg-gray-100 text-gray-700'
                  ]"
                >
                  {{ cat.is_extra_service ? 'Yes' : 'No' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ (cat.allowed_extensions || []).join(', ') || 'Any' }}
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="!categoriesLoading && categories.length === 0" class="text-center py-12 text-gray-500">
          No categories defined yet. Click "Add Category" to create one.
        </div>
      </div>

      <!-- Category Modal -->
      <div
        v-if="showCategoryModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-xl font-semibold">
                {{ editingCategory ? 'Edit File Category' : 'Add File Category' }}
              </h3>
              <button @click="closeCategoryModal" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form @submit.prevent="saveCategory" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Website *
                </label>
                <select
                  v-model="categoryForm.website"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Select Website</option>
                  <option
                    v-for="site in websites"
                    :key="site.id"
                    :value="site.id"
                  >
                    {{ site.name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Category Name *
                </label>
                <input
                  v-model="categoryForm.name"
                  type="text"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., Order Instructions, Sample Paper, Final Paper"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Allowed Extensions
                </label>
                <input
                  v-model="categoryForm.allowed_extensions_text"
                  type="text"
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., pdf,docx,txt (comma-separated, leave empty for any)"
                />
                <p class="text-xs text-gray-500 mt-1">
                  These extensions are in addition to the global file config and are mainly for admin clarity.
                </p>
              </div>

              <div class="flex items-center gap-6">
                <label class="inline-flex items-center">
                  <input
                    v-model="categoryForm.is_final_draft"
                    type="checkbox"
                    class="mr-2"
                  />
                  <span class="text-sm font-medium text-gray-700">
                    Final Paper / Final Draft
                  </span>
                </label>
                <label class="inline-flex items-center">
                  <input
                    v-model="categoryForm.is_extra_service"
                    type="checkbox"
                    class="mr-2"
                  />
                  <span class="text-sm font-medium text-gray-700">
                    Extra Service (e.g., Plagiarism Report)
                  </span>
                </label>
              </div>

              <div class="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  @click="closeCategoryModal"
                  class="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="savingCategory"
                >
                  {{ savingCategory ? 'Saving...' : (editingCategory ? 'Update' : 'Create') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuration Modal -->
    <div v-if="showConfigModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold">{{ editingConfig ? 'Edit Configuration' : 'Add Configuration' }}</h3>
            <button @click="closeConfigModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveConfig" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Website *</label>
              <select v-model="configForm.website" required class="w-full border rounded px-3 py-2">
                <option value="">Select Website</option>
                <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Max Upload Size (MB) *</label>
              <input
                v-model.number="configForm.max_upload_size"
                type="number"
                min="1"
                required
                class="w-full border rounded px-3 py-2"
                placeholder="e.g., 100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Allowed Extensions</label>
              <input
                v-model="configForm.allowed_extensions_text"
                type="text"
                class="w-full border rounded px-3 py-2"
                placeholder="e.g., pdf,docx,xlsx (comma-separated, leave empty for all)"
              />
              <p class="text-xs text-gray-500 mt-1">Enter file extensions separated by commas (e.g., pdf,docx,xlsx). Leave empty to allow all extensions.</p>
            </div>

            <div class="flex items-center">
              <input
                v-model="configForm.enable_external_links"
                type="checkbox"
                id="enable_external_links"
                class="mr-2"
              />
              <label for="enable_external_links" class="text-sm font-medium text-gray-700">Enable External Links</label>
            </div>

            <div class="flex items-center">
              <input
                v-model="configForm.final_draft_required"
                type="checkbox"
                id="final_draft_required"
                class="mr-2"
              />
              <label for="final_draft_required" class="text-sm font-medium text-gray-700">Final Draft Required</label>
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeConfigModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="savingConfig">
                {{ savingConfig ? 'Saving...' : (editingConfig ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Loading State -->
  <div v-else-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
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
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { orderFilesAPI, websitesAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const tabs = [
  { id: 'order-files', label: 'Order Files' },
  { id: 'extra-files', label: 'Extra Service Files' },
  { id: 'external-links', label: 'External Links' },
  { id: 'deletion-requests', label: 'Deletion Requests' },
  { id: 'config', label: 'Configuration' },
  { id: 'categories', label: 'File Categories' },
]

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const componentError = ref(null)
const initialLoading = ref(true)
const activeTab = ref('order-files')
const stats = ref({})
const websites = ref([])
const orderFiles = ref([])
const extraFiles = ref([])
const externalLinks = ref([])
const deletionRequests = ref([])
const configs = ref([])
const categories = ref([])
const categoriesLoading = ref(false)
const showCategoryModal = ref(false)
const editingCategory = ref(null)
const savingCategory = ref(false)
const categoryForm = ref({
  website: '',
  name: '',
  allowed_extensions_text: '',
  is_final_draft: false,
  is_extra_service: false,
})

const orderFilesLoading = ref(false)
const extraFilesLoading = ref(false)
const externalLinksLoading = ref(false)
const deletionRequestsLoading = ref(false)
const configsLoading = ref(false)

const filters = ref({
  order_id: null,
  website: '',
  is_downloadable: '',
})

const showConfigModal = ref(false)
const editingConfig = ref(null)
const savingConfig = ref(false)
const configForm = ref({
  website: '',
  max_upload_size: 100,
  allowed_extensions_text: '',
  enable_external_links: true,
  final_draft_required: true,
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const loadStats = async () => {
  try {
    // Load stats from various endpoints
    const [orderFilesRes, extraFilesRes, externalLinksRes, deletionRequestsRes] = await Promise.all([
      orderFilesAPI.list({ page_size: 1 }),
      orderFilesAPI.listExtraServiceFiles({ page_size: 1 }),
      orderFilesAPI.listExternalLinks({ page_size: 1 }),
      orderFilesAPI.listDeletionRequests({ status: 'pending', page_size: 1 }),
    ])
    
    stats.value = {
      total_order_files: orderFilesRes.data.count || orderFilesRes.data.results?.length || 0,
      total_extra_files: extraFilesRes.data.count || extraFilesRes.data.results?.length || 0,
      total_external_links: externalLinksRes.data.count || externalLinksRes.data.results?.length || 0,
      pending_deletions: deletionRequestsRes.data.count || deletionRequestsRes.data.results?.length || 0,
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites()
    websites.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const loadOrderFiles = async () => {
  orderFilesLoading.value = true
  try {
    const params = {}
    if (filters.value.order_id) params.order = filters.value.order_id
    if (filters.value.website) params.website_id = filters.value.website
    if (filters.value.is_downloadable !== '') params.is_downloadable = filters.value.is_downloadable
    
    const response = await orderFilesAPI.list(params)
    orderFiles.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load order files:', error)
  } finally {
    orderFilesLoading.value = false
  }
}

const loadCategories = async () => {
  categoriesLoading.value = true
  try {
    const response = await orderFilesAPI.listCategories({})
    categories.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load file categories:', error)
  } finally {
    categoriesLoading.value = false
  }
}

const resetCategoryForm = () => {
  categoryForm.value = {
    website: '',
    name: '',
    allowed_extensions_text: '',
    is_final_draft: false,
    is_extra_service: false,
  }
}

const openCreateCategory = () => {
  editingCategory.value = null
  resetCategoryForm()
  showCategoryModal.value = true
}

const openEditCategory = (cat) => {
  editingCategory.value = cat
  categoryForm.value = {
    website: cat.website || '',
    name: cat.name || '',
    allowed_extensions_text: (cat.allowed_extensions || []).join(','),
    is_final_draft: !!cat.is_final_draft,
    is_extra_service: !!cat.is_extra_service,
  }
  showCategoryModal.value = true
}

const closeCategoryModal = () => {
  showCategoryModal.value = false
  editingCategory.value = null
  resetCategoryForm()
}

const saveCategory = async () => {
  if (!categoryForm.value.website || !categoryForm.value.name) return

  savingCategory.value = true
  try {
    const payload = {
      website: categoryForm.value.website,
      name: categoryForm.value.name,
      is_final_draft: categoryForm.value.is_final_draft,
      is_extra_service: categoryForm.value.is_extra_service,
    }
    const rawExt = categoryForm.value.allowed_extensions_text || ''
    const parsed = rawExt
      .split(',')
      .map((e) => e.trim())
      .filter((e) => e.length > 0)
    if (parsed.length) {
      payload.allowed_extensions = parsed
    }

    if (editingCategory.value && editingCategory.value.id) {
      await orderFilesAPI.updateCategory(editingCategory.value.id, payload)
    } else {
      await orderFilesAPI.createCategory(payload)
    }

    await loadCategories()
    closeCategoryModal()
  } catch (error) {
    console.error('Failed to save category:', error)
  } finally {
    savingCategory.value = false
  }
}

const deleteCategory = async (id) => {
  if (!id) return
  if (!confirm('Are you sure you want to delete this category?')) return
  try {
    await orderFilesAPI.deleteCategory(id)
    await loadCategories()
  } catch (error) {
    console.error('Failed to delete category:', error)
  }
}

const loadExtraFiles = async () => {
  extraFilesLoading.value = true
  try {
    const response = await orderFilesAPI.listExtraServiceFiles()
    extraFiles.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load extra files:', error)
  } finally {
    extraFilesLoading.value = false
  }
}

const loadExternalLinks = async () => {
  externalLinksLoading.value = true
  try {
    const response = await orderFilesAPI.listExternalLinks()
    externalLinks.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load external links:', error)
  } finally {
    externalLinksLoading.value = false
  }
}

const loadDeletionRequests = async () => {
  deletionRequestsLoading.value = true
  try {
    const response = await orderFilesAPI.listDeletionRequests()
    deletionRequests.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load deletion requests:', error)
  } finally {
    deletionRequestsLoading.value = false
  }
}

const loadConfigs = async () => {
  configsLoading.value = true
  try {
    const response = await orderFilesAPI.listConfigs()
    configs.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load configs:', error)
  } finally {
    configsLoading.value = false
  }
}

let searchTimeout = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (activeTab.value === 'order-files') {
      loadOrderFiles()
    }
  }, 500)
}

const resetFilters = () => {
  filters.value = {
    order_id: null,
    website: '',
    is_downloadable: '',
  }
  loadOrderFiles()
}

const downloadFile = async (id) => {
  try {
    const response = await orderFilesAPI.getSignedUrl(id)
    if (response.data.signed_url) {
      window.open(response.data.signed_url, '_blank')
    }
  } catch (error) {
    console.error('Failed to download file:', error)
    showError('Failed to download file')
  }
}

const toggleFileDownload = async (id) => {
  try {
    await orderFilesAPI.toggleDownload(id)
    await loadOrderFiles()
    showSuccess('File download status updated')
  } catch (error) {
    console.error('Failed to toggle file download:', error)
    showError('Failed to update file download status')
  }
}

const deleteFile = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this file?',
    'Delete File',
    {
      details: 'This action cannot be undone. The file will be permanently removed.'
    }
  )
  if (!confirmed) return
  try {
    await orderFilesAPI.delete(id)
    await loadOrderFiles()
    showSuccess('File deleted successfully')
  } catch (error) {
    console.error('Failed to delete file:', error)
    showError('Failed to delete file')
  }
}

const downloadExtraFile = async (id) => {
  try {
    const file = await orderFilesAPI.getExtraServiceFile(id)
    // Similar download logic
    alert('Download functionality for extra files')
  } catch (error) {
    console.error('Failed to download extra file:', error)
  }
}

const toggleExtraFileDownload = async (id) => {
  try {
    await orderFilesAPI.toggleExtraServiceDownload(id)
    await loadExtraFiles()
  } catch (error) {
    console.error('Failed to toggle extra file download:', error)
  }
}

const deleteExtraFile = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this file?',
    'Delete Extra Service File',
    {
      details: 'This action cannot be undone. The file will be permanently removed.'
    }
  )
  if (!confirmed) return
  try {
    await orderFilesAPI.deleteExtraServiceFile(id)
    await loadExtraFiles()
    showSuccess('Extra service file deleted successfully')
  } catch (error) {
    console.error('Failed to delete extra file:', error)
    showError('Failed to delete extra service file')
  }
}

const approveExternalLink = async (id) => {
  try {
    await orderFilesAPI.approveExternalLink(id)
    await loadExternalLinks()
  } catch (error) {
    console.error('Failed to approve external link:', error)
  }
}

const deleteExternalLink = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this external link?',
    'Delete External Link',
    {
      details: 'This action cannot be undone.'
    }
  )
  if (!confirmed) return
  try {
    await orderFilesAPI.deleteExternalLink(id)
    await loadExternalLinks()
    showSuccess('External link deleted successfully')
  } catch (error) {
    console.error('Failed to delete external link:', error)
    showError('Failed to delete external link')
  }
}

const approveDeletionRequest = async (id) => {
  try {
    await orderFilesAPI.approveDeletionRequest(id)
    await loadDeletionRequests()
  } catch (error) {
    console.error('Failed to approve deletion request:', error)
  }
}

const deleteDeletionRequest = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this request?',
    'Delete Deletion Request',
    {
      details: 'This action cannot be undone.'
    }
  )
  if (!confirmed) return
  try {
    await orderFilesAPI.deleteDeletionRequest(id)
    await loadDeletionRequests()
    showSuccess('Deletion request deleted successfully')
  } catch (error) {
    console.error('Failed to delete deletion request:', error)
    showError('Failed to delete deletion request')
  }
}

const editConfig = (config) => {
  editingConfig.value = config
  configForm.value = {
    website: config.website?.id || config.website || '',
    max_upload_size: config.max_upload_size || 100,
    allowed_extensions_text: Array.isArray(config.allowed_extensions) 
      ? config.allowed_extensions.join(',') 
      : (config.allowed_extensions || ''),
    enable_external_links: config.enable_external_links !== undefined ? config.enable_external_links : true,
    final_draft_required: config.final_draft_required !== undefined ? config.final_draft_required : true,
  }
  showConfigModal.value = true
}

const closeConfigModal = () => {
  showConfigModal.value = false
  editingConfig.value = null
  configForm.value = {
    website: '',
    max_upload_size: 100,
    allowed_extensions_text: '',
    enable_external_links: true,
    final_draft_required: true,
  }
}

const saveConfig = async () => {
  savingConfig.value = true
  try {
    // Parse allowed extensions
    const allowed_extensions = configForm.value.allowed_extensions_text
      ? configForm.value.allowed_extensions_text.split(',').map(ext => ext.trim()).filter(ext => ext)
      : []

    const data = {
      website: configForm.value.website,
      max_upload_size: configForm.value.max_upload_size,
      allowed_extensions: allowed_extensions,
      enable_external_links: configForm.value.enable_external_links,
      final_draft_required: configForm.value.final_draft_required,
    }

    if (editingConfig.value) {
      await orderFilesAPI.updateConfig(editingConfig.value.id, data)
    } else {
      await orderFilesAPI.createConfig(data)
    }

    await loadConfigs()
    closeConfigModal()
  } catch (error) {
    console.error('Failed to save config:', error)
    showError(error.response?.data?.detail || 'Failed to save configuration')
  } finally {
    savingConfig.value = false
  }
}

const deleteConfig = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this configuration?',
    'Delete Configuration',
    {
      details: 'This action cannot be undone. File upload settings will revert to defaults.'
    }
  )
  if (!confirmed) return
  try {
    await orderFilesAPI.deleteConfig(id)
    await loadConfigs()
    showSuccess('Configuration deleted successfully')
  } catch (error) {
    console.error('Failed to delete config:', error)
    showError('Failed to delete configuration')
  }
}

// Watch active tab to load appropriate data
watch(activeTab, (newTab) => {
  if (newTab === 'order-files') loadOrderFiles()
  else if (newTab === 'extra-files') loadExtraFiles()
  else if (newTab === 'external-links') loadExternalLinks()
  else if (newTab === 'deletion-requests') loadDeletionRequests()
  else if (newTab === 'config') loadConfigs()
})

onMounted(async () => {
  try {
    await Promise.all([
      loadStats(),
      loadWebsites(),
      loadOrderFiles(),
      loadExtraFiles(),
      loadExternalLinks(),
      loadDeletionRequests(),
      loadConfigs(),
      loadCategories(),
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing FileManagement:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

