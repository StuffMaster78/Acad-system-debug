<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Writer Resources & Samples Management</h1>
        <p class="mt-2 text-gray-600">Upload and manage resources, guides, and samples for writers</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="showCategoryModal = true"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          + Add Category
        </button>
        <button
          @click="openAddResourceModal"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          + Add Resource
        </button>
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
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Resources Tab -->
    <div v-if="activeTab === 'resources'" class="space-y-4">
      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              v-model="filters.category"
              @change="loadResources"
              class="w-full border border-gray-300 rounded-lg px-4 py-2"
            >
              <option value="">All Categories</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              v-model="filters.resource_type"
              @change="loadResources"
              class="w-full border border-gray-300 rounded-lg px-4 py-2"
            >
              <option value="">All Types</option>
              <option value="document">Document</option>
              <option value="link">Link</option>
              <option value="video">Video</option>
              <option value="article">Article</option>
              <option value="tool">Tool</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              v-model="filters.is_active"
              @change="loadResources"
              class="w-full border border-gray-300 rounded-lg px-4 py-2"
            >
              <option value="">All</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Search resources..."
              class="w-full border border-gray-300 rounded-lg px-4 py-2"
            />
          </div>
        </div>
      </div>

      <!-- Resources Table -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div v-if="loading" class="p-8 text-center">
          <p class="text-gray-500">Loading resources...</p>
        </div>
        <div v-else-if="resources.length === 0" class="p-8 text-center">
          <p class="text-gray-500">No resources found. Click "Add Resource" to create one.</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Views</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Downloads</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="resource in resources" :key="resource.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <span v-if="resource.is_featured" class="mr-2 text-yellow-500">⭐</span>
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ resource.title }}</div>
                      <div v-if="resource.description" class="text-sm text-gray-500 truncate max-w-xs">
                        {{ resource.description }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ resource.category?.name || 'Uncategorized' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="getTypeBadgeClass(resource.resource_type)">
                    {{ getTypeLabel(resource.resource_type) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ resource.view_count || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ resource.download_count || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="resource.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ resource.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="editResource(resource)"
                    class="text-primary-600 hover:text-primary-900 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteResource(resource.id)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Categories Tab -->
    <div v-if="activeTab === 'categories'" class="space-y-4">
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div v-if="loadingCategories" class="p-8 text-center">
          <p class="text-gray-500">Loading categories...</p>
        </div>
        <div v-else-if="categories.length === 0" class="p-8 text-center">
          <p class="text-gray-500">No categories found. Click "Add Category" to create one.</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resources</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="category in categories" :key="category.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ category.name }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">
                  {{ category.description || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ category.resource_count || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ category.display_order || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="category.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ category.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="editCategory(category)"
                    class="text-primary-600 hover:text-primary-900 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteCategory(category.id)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Portfolio Samples Tab -->
    <div v-if="activeTab === 'samples'" class="space-y-4">
      <div class="flex justify-end">
        <button
          @click="openAddSampleModal"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          + Add Sample
        </button>
      </div>

      <!-- Samples Table -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div v-if="loadingSamples" class="p-8 text-center">
          <p class="text-gray-500">Loading samples...</p>
        </div>
        <div v-else-if="samples.length === 0" class="p-8 text-center">
          <p class="text-gray-500">No portfolio samples found.</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Writer</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="sample in samples" :key="sample.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <span v-if="sample.is_featured" class="mr-2 text-yellow-500">⭐</span>
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ sample.title }}</div>
                      <div v-if="sample.description" class="text-sm text-gray-500 truncate max-w-xs">
                        {{ sample.description }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ sample.writer?.email || sample.writer_email || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ sample.subject?.name || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ sample.type_of_work?.name || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 text-xs font-medium rounded-full"
                    :class="sample.is_featured ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'">
                    {{ sample.is_featured ? 'Featured' : 'Regular' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="editSample(sample)"
                    class="text-primary-600 hover:text-primary-900 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteSample(sample.id)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Resource Modal -->
    <div v-if="showResourceModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingResource ? 'Edit Resource' : 'Add New Resource' }}
            </h2>
            <button @click="closeResourceModal" class="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>

          <form @submit.prevent="saveResource" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  v-model="resourceForm.title"
                  type="text"
                  required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  v-model="resourceForm.category"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2"
                >
                  <option value="">Select Category</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="resourceForm.description"
                rows="3"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Resource Type *</label>
              <select
                v-model="resourceForm.resource_type"
                @change="handleResourceTypeChange"
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              >
                <option value="document">Document (PDF, DOC, etc.)</option>
                <option value="link">External Link</option>
                <option value="video">Video</option>
                <option value="article">Article/Guide</option>
                <option value="tool">Tool/Software</option>
              </select>
            </div>

            <!-- Document Upload -->
            <div v-if="resourceForm.resource_type === 'document'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Upload File *</label>
              <input
                type="file"
                @change="handleFileChange"
                accept=".pdf,.doc,.docx,.txt"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              />
              <p v-if="resourceForm.file_url" class="mt-2 text-sm text-gray-500">
                Current: {{ resourceForm.file_url }}
              </p>
            </div>

            <!-- External Link -->
            <div v-if="resourceForm.resource_type === 'link'">
              <label class="block text-sm font-medium text-gray-700 mb-1">External URL *</label>
              <input
                v-model="resourceForm.external_url"
                type="url"
                required
                placeholder="https://example.com"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              />
            </div>

            <!-- Video URL -->
            <div v-if="resourceForm.resource_type === 'video'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Video URL *</label>
              <input
                v-model="resourceForm.video_url"
                type="url"
                required
                placeholder="https://youtube.com/watch?v=..."
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              />
            </div>

            <!-- Article Content -->
            <div v-if="resourceForm.resource_type === 'article'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Content *</label>
              <textarea
                v-model="resourceForm.content"
                rows="10"
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="Enter article content (HTML supported)"
              ></textarea>
            </div>

            <!-- Tool URL -->
            <div v-if="resourceForm.resource_type === 'tool'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Tool URL *</label>
              <input
                v-model="resourceForm.external_url"
                type="url"
                required
                placeholder="https://tool.example.com"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
                <input
                  v-model.number="resourceForm.display_order"
                  type="number"
                  min="0"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>
              <div class="flex items-center space-x-4 pt-6">
                <label class="flex items-center">
                  <input
                    v-model="resourceForm.is_featured"
                    type="checkbox"
                    class="mr-2"
                  />
                  <span class="text-sm text-gray-700">Featured</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="resourceForm.is_active"
                    type="checkbox"
                    class="mr-2"
                  />
                  <span class="text-sm text-gray-700">Active</span>
                </label>
              </div>
            </div>

            <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
              <p class="text-sm text-red-600">{{ error }}</p>
            </div>

            <div class="flex justify-end gap-3 pt-4">
              <button
                type="button"
                @click="closeResourceModal"
                class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : 'Save Resource' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Add/Edit Category Modal -->
    <div v-if="showCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingCategory ? 'Edit Category' : 'Add New Category' }}
            </h2>
            <button @click="closeCategoryModal" class="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>

          <form @submit.prevent="saveCategory" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input
                v-model="categoryForm.name"
                type="text"
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="categoryForm.description"
                rows="3"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
              <input
                v-model.number="categoryForm.display_order"
                type="number"
                min="0"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              />
            </div>
            <div>
              <label class="flex items-center">
                <input
                  v-model="categoryForm.is_active"
                  type="checkbox"
                  class="mr-2"
                />
                <span class="text-sm text-gray-700">Active</span>
              </label>
            </div>

            <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
              <p class="text-sm text-red-600">{{ error }}</p>
            </div>

            <div class="flex justify-end gap-3 pt-4">
              <button
                type="button"
                @click="closeCategoryModal"
                class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : 'Save Category' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Add/Edit Sample Modal -->
    <div v-if="showSampleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingSample ? 'Edit Portfolio Sample' : 'Add New Portfolio Sample' }}
            </h2>
            <button @click="closeSampleModal" class="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>

          <form @submit.prevent="saveSample" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  v-model="sampleForm.title"
                  type="text"
                  required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Writer *</label>
                <select
                  v-model="sampleForm.writer"
                  required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2"
                >
                  <option value="">Select Writer</option>
                  <option v-for="writer in writers" :key="writer.id" :value="writer.id">
                    {{ writer.email || writer.username }}
                  </option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="sampleForm.description"
                rows="3"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <select
                  v-model="sampleForm.subject"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2"
                >
                  <option value="">Select Subject</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Type of Work</label>
                <select
                  v-model="sampleForm.type_of_work"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2"
                >
                  <option value="">Select Type</option>
                  <option v-for="type in typesOfWork" :key="type.id" :value="type.id">
                    {{ type.name }}
                  </option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Upload Sample File</label>
              <input
                type="file"
                @change="handleSampleFileChange"
                accept=".pdf,.doc,.docx,.txt"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
              />
              <p v-if="editingSample?.file" class="mt-2 text-sm text-gray-500">
                Current: {{ editingSample.file }}
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Content Preview</label>
              <textarea
                v-model="sampleForm.content_preview"
                rows="6"
                class="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="Enter a preview of the sample content..."
              ></textarea>
            </div>

            <div class="flex items-center space-x-4">
              <label class="flex items-center">
                <input
                  v-model="sampleForm.is_featured"
                  type="checkbox"
                  class="mr-2"
                />
                <span class="text-sm text-gray-700">Featured</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="sampleForm.is_anonymized"
                  type="checkbox"
                  class="mr-2"
                />
                <span class="text-sm text-gray-700">Anonymized</span>
              </label>
            </div>

            <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
              <p class="text-sm text-red-600">{{ error }}</p>
            </div>

            <div class="flex justify-end gap-3 pt-4">
              <button
                type="button"
                @click="closeSampleModal"
                class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : 'Save Sample' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import writersAPI from '@/api/writers'
import writerManagementAPI from '@/api/writer-management'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Get current website ID from auth store or localStorage
const getCurrentWebsiteId = () => {
  const user = authStore.user
  if (user) {
    if (user.website_id) {
      return user.website_id
    }
    if (user.website?.id) {
      return user.website.id
    }
    if (typeof user.website === 'number') {
      return user.website
    }
  }
  
  // Fallback to localStorage
  const storedWebsite = localStorage.getItem('current_website')
  if (storedWebsite) {
    const parsed = parseInt(storedWebsite)
    if (!isNaN(parsed)) {
      return parsed
    }
  }
  
  const storedWebsiteId = localStorage.getItem('website_id')
  if (storedWebsiteId) {
    const parsed = parseInt(storedWebsiteId)
    if (!isNaN(parsed)) {
      return parsed
    }
  }
  
  return null
}

const activeTab = ref('resources')
const tabs = [
  { id: 'resources', label: 'Resources' },
  { id: 'categories', label: 'Categories' },
  { id: 'samples', label: 'Portfolio Samples' }
]

const loading = ref(false)
const loadingCategories = ref(false)
const loadingSamples = ref(false)
const saving = ref(false)
const error = ref('')
const resources = ref([])
const categories = ref([])
const samples = ref([])
const writers = ref([])
const subjects = ref([])
const typesOfWork = ref([])

const filters = ref({
  category: '',
  resource_type: '',
  is_active: '',
  search: ''
})

const showResourceModal = ref(false)
const showCategoryModal = ref(false)
const showSampleModal = ref(false)
const editingResource = ref(null)
const editingCategory = ref(null)
const editingSample = ref(null)
const selectedFile = ref(null)
const selectedSampleFile = ref(null)

const resourceForm = ref({
  title: '',
  description: '',
  category: '',
  resource_type: 'document',
  file: null,
  external_url: '',
  video_url: '',
  content: '',
  display_order: 0,
  is_featured: false,
  is_active: true
})

const categoryForm = ref({
  name: '',
  description: '',
  display_order: 0,
  is_active: true
})

const sampleForm = ref({
  title: '',
  description: '',
  writer: '',
  subject: '',
  type_of_work: '',
  content_preview: '',
  is_featured: false,
  is_anonymized: true
})

const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const websiteId = getCurrentWebsiteId()
    const params = {}
    if (websiteId) params.website = websiteId
    const response = await writersAPI.getResourceCategories(params)
    categories.value = response.data.results || response.data || []
  } catch (err) {
    error.value = 'Failed to load categories'
    console.error(err)
  } finally {
    loadingCategories.value = false
  }
}

const loadResources = async () => {
  loading.value = true
  try {
    const websiteId = getCurrentWebsiteId()
    const params = {}
    if (websiteId) params.website = websiteId
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.resource_type) params.resource_type = filters.value.resource_type
    if (filters.value.is_active !== '') params.is_active = filters.value.is_active === 'true'
    if (filters.value.search) params.search = filters.value.search

    const response = await writersAPI.getResources(params)
    resources.value = response.data.results || response.data || []
  } catch (err) {
    error.value = 'Failed to load resources'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openAddResourceModal = () => {
  editingResource.value = null
  resourceForm.value = {
    title: '',
    description: '',
    category: '',
    resource_type: 'document',
    file: null,
    external_url: '',
    video_url: '',
    content: '',
    display_order: 0,
    is_featured: false,
    is_active: true
  }
  selectedFile.value = null
  showResourceModal.value = true
}

const editResource = (resource) => {
  editingResource.value = resource
  resourceForm.value = {
    title: resource.title || '',
    description: resource.description || '',
    category: resource.category?.id || '',
    resource_type: resource.resource_type || 'document',
    file: null,
    file_url: resource.file || null,
    external_url: resource.external_url || '',
    video_url: resource.video_url || '',
    content: resource.content || '',
    display_order: resource.display_order || 0,
    is_featured: resource.is_featured || false,
    is_active: resource.is_active !== false
  }
  selectedFile.value = null
  showResourceModal.value = true
}

const closeResourceModal = () => {
  showResourceModal.value = false
  editingResource.value = null
  error.value = ''
}

const handleResourceTypeChange = () => {
  // Clear type-specific fields when changing type
  resourceForm.value.external_url = ''
  resourceForm.value.video_url = ''
  resourceForm.value.content = ''
  resourceForm.value.file = null
  selectedFile.value = null
}

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

const saveResource = async () => {
  saving.value = true
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('title', resourceForm.value.title)
    formData.append('description', resourceForm.value.description || '')
    formData.append('resource_type', resourceForm.value.resource_type)
    formData.append('display_order', resourceForm.value.display_order)
    formData.append('is_featured', resourceForm.value.is_featured)
    formData.append('is_active', resourceForm.value.is_active)
    
    if (resourceForm.value.category) {
      formData.append('category', resourceForm.value.category)
    }
    
    const websiteId = getCurrentWebsiteId()
    if (websiteId) {
      formData.append('website', websiteId)
    }

    // Add type-specific fields
    if (resourceForm.value.resource_type === 'document' && selectedFile.value) {
      formData.append('file', selectedFile.value)
    } else if (resourceForm.value.resource_type === 'link' || resourceForm.value.resource_type === 'tool') {
      formData.append('external_url', resourceForm.value.external_url)
    } else if (resourceForm.value.resource_type === 'video') {
      formData.append('video_url', resourceForm.value.video_url)
    } else if (resourceForm.value.resource_type === 'article') {
      formData.append('content', resourceForm.value.content)
    }

    if (editingResource.value) {
      await writersAPI.updateResource(editingResource.value.id, formData)
    } else {
      await writersAPI.createResource(formData)
    }

    await loadResources()
    closeResourceModal()
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to save resource'
    console.error(err)
  } finally {
    saving.value = false
  }
}

const deleteResource = async (id) => {
  if (!confirm('Are you sure you want to delete this resource?')) return

  try {
    await writersAPI.deleteResource(id)
    await loadResources()
  } catch (err) {
    error.value = 'Failed to delete resource'
    console.error(err)
  }
}

const editCategory = (category) => {
  editingCategory.value = category
  categoryForm.value = {
    name: category.name || '',
    description: category.description || '',
    display_order: category.display_order || 0,
    is_active: category.is_active !== false
  }
  showCategoryModal.value = true
}

const closeCategoryModal = () => {
  showCategoryModal.value = false
  editingCategory.value = null
  error.value = ''
}

const saveCategory = async () => {
  saving.value = true
  error.value = ''

  try {
    const data = {
      name: categoryForm.value.name,
      description: categoryForm.value.description || '',
      display_order: categoryForm.value.display_order,
      is_active: categoryForm.value.is_active
    }

    const websiteId = getCurrentWebsiteId()
    if (websiteId) {
      data.website = websiteId
    }

    if (editingCategory.value) {
      await writersAPI.updateResourceCategory(editingCategory.value.id, data)
    } else {
      await writersAPI.createResourceCategory(data)
    }

    await loadCategories()
    closeCategoryModal()
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to save category'
    console.error(err)
  } finally {
    saving.value = false
  }
}

const deleteCategory = async (id) => {
  if (!confirm('Are you sure you want to delete this category? Resources in this category will be uncategorized.')) return

  try {
    await writersAPI.deleteResourceCategory(id)
    await loadCategories()
    await loadResources()
  } catch (err) {
    error.value = 'Failed to delete category'
    console.error(err)
  }
}

const getTypeLabel = (type) => {
  const labels = {
    document: 'Document',
    link: 'Link',
    video: 'Video',
    article: 'Article',
    tool: 'Tool'
  }
  return labels[type] || type
}

const getTypeBadgeClass = (type) => {
  const classes = {
    document: 'bg-blue-100 text-blue-800',
    link: 'bg-purple-100 text-purple-800',
    video: 'bg-red-100 text-red-800',
    article: 'bg-green-100 text-green-800',
    tool: 'bg-yellow-100 text-yellow-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadResources()
  }, 500)
}

const loadSamples = async () => {
  loadingSamples.value = true
  try {
    const websiteId = getCurrentWebsiteId()
    const params = {}
    if (websiteId) params.website = websiteId
    const response = await writerManagementAPI.listPortfolioSamples(params)
    samples.value = response.data.results || response.data || []
  } catch (err) {
    error.value = 'Failed to load samples'
    console.error(err)
  } finally {
    loadingSamples.value = false
  }
}

const loadWriters = async () => {
  try {
    const websiteId = getCurrentWebsiteId()
    const params = { role: 'writer' }
    if (websiteId) params.website = websiteId
    const response = await writerManagementAPI.listWriters(params)
    writers.value = response.data.results || response.data || []
  } catch (err) {
    console.error('Failed to load writers:', err)
  }
}

const loadDropdownOptions = async () => {
  try {
    const response = await apiClient.get('/order-configs/api/order-configs/')
    const configs = response.data || {}
    subjects.value = configs.subjects || []
    typesOfWork.value = configs.types_of_work || []
  } catch (err) {
    console.error('Failed to load dropdown options:', err)
  }
}

const openAddSampleModal = async () => {
  editingSample.value = null
  sampleForm.value = {
    title: '',
    description: '',
    writer: '',
    subject: '',
    type_of_work: '',
    content_preview: '',
    is_featured: false,
    is_anonymized: true
  }
  selectedSampleFile.value = null
  
  if (writers.value.length === 0) await loadWriters()
  if (subjects.value.length === 0 || typesOfWork.value.length === 0) await loadDropdownOptions()
  
  showSampleModal.value = true
}

const editSample = async (sample) => {
  editingSample.value = sample
  sampleForm.value = {
    title: sample.title || '',
    description: sample.description || '',
    writer: sample.writer?.id || sample.writer || '',
    subject: sample.subject?.id || sample.subject || '',
    type_of_work: sample.type_of_work?.id || sample.type_of_work || '',
    content_preview: sample.content_preview || '',
    is_featured: sample.is_featured || false,
    is_anonymized: sample.is_anonymized !== false
  }
  selectedSampleFile.value = null
  
  if (writers.value.length === 0) await loadWriters()
  if (subjects.value.length === 0 || typesOfWork.value.length === 0) await loadDropdownOptions()
  
  showSampleModal.value = true
}

const closeSampleModal = () => {
  showSampleModal.value = false
  editingSample.value = null
  error.value = ''
}

const handleSampleFileChange = (event) => {
  selectedSampleFile.value = event.target.files[0]
}

const saveSample = async () => {
  saving.value = true
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('title', sampleForm.value.title)
    formData.append('description', sampleForm.value.description || '')
    formData.append('writer', sampleForm.value.writer)
    formData.append('content_preview', sampleForm.value.content_preview || '')
    formData.append('is_featured', sampleForm.value.is_featured)
    formData.append('is_anonymized', sampleForm.value.is_anonymized)
    
    if (sampleForm.value.subject) formData.append('subject', sampleForm.value.subject)
    if (sampleForm.value.type_of_work) formData.append('type_of_work', sampleForm.value.type_of_work)
    if (selectedSampleFile.value) formData.append('file', selectedSampleFile.value)
    
    const websiteId = getCurrentWebsiteId()
    if (websiteId) {
      formData.append('website', websiteId)
    }

    if (editingSample.value) {
      await writerManagementAPI.updatePortfolioSample(editingSample.value.id, formData)
    } else {
      await writerManagementAPI.createPortfolioSample(formData)
    }

    await loadSamples()
    closeSampleModal()
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to save sample'
    console.error(err)
  } finally {
    saving.value = false
  }
}

const deleteSample = async (id) => {
  if (!confirm('Are you sure you want to delete this sample?')) return

  try {
    await writerManagementAPI.deletePortfolioSample(id)
    await loadSamples()
  } catch (err) {
    error.value = 'Failed to delete sample'
    console.error(err)
  }
}

onMounted(() => {
  loadCategories()
  loadResources()
  loadSamples()
})
</script>


