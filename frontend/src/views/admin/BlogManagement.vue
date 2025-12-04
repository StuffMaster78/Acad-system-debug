<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Blog Pages Management</h1>
        <p class="mt-2 text-gray-600">Manage blog posts, categories, tags, and SEO settings</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Blog Post
      </button>
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

    <!-- Blog Posts Tab -->
    <div v-if="activeTab === 'posts' || activeTab === 'my-drafts' || activeTab === 'needs-review' || activeTab === 'scheduled' || activeTab === 'stale'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Category</label>
            <select v-model="filters.category" @change="loadBlogs" class="w-full border rounded px-3 py-2">
              <option value="">All Categories</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select v-model="filters.status" @change="loadBlogs" class="w-full border rounded px-3 py-2">
              <option value="">All Status</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Search by title..."
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Blog Posts Table -->
      <div class="card overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Author</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Engagement</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Published</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="blog in blogs" :key="blog.id" class="hover:bg-gray-50">
                <td class="px-6 py-4">
                  <div class="font-medium text-gray-900">{{ blog.title }}</div>
                  <div class="text-sm text-gray-500">{{ blog.slug }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div v-if="blog.website" class="text-sm">
                    <div class="font-medium text-gray-900">{{ blog.website.name }}</div>
                    <div class="text-xs text-gray-500">{{ blog.website.domain }}</div>
                  </div>
                  <span v-else class="text-gray-400">—</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                    {{ blog.category?.name || 'Uncategorized' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusBadgeClass(blog.is_published, blog.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ blog.is_published ? 'Published' : (blog.status || 'Draft') }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ blog.authors?.map(a => a.username || a.name).join(', ') || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="flex flex-col gap-1">
                    <div class="flex items-center gap-2 text-gray-600">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span>{{ blog.view_count || 0 }}</span>
                    </div>
                    <div class="flex items-center gap-2 text-green-600">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"/>
                      </svg>
                      <span>{{ blog.like_count || 0 }}</span>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(blog.publish_date || blog.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="flex items-center gap-2">
                    <button @click="viewBlog(blog)" class="text-blue-600 hover:underline">View</button>
                    <button @click="editBlog(blog)" class="text-blue-600 hover:underline">Edit</button>
                    <button @click="toggleActionsMenu(blog.id)" class="text-gray-600 hover:text-gray-900">⋯</button>
                    <div v-if="actionsMenuOpen === blog.id" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border">
                      <div class="py-1">
                        <button @click="publishBlogAction(blog)" v-if="!blog.is_published" class="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-100">Publish</button>
                        <button @click="unpublishBlogAction(blog)" v-else class="block w-full text-left px-4 py-2 text-sm text-yellow-600 hover:bg-gray-100">Unpublish</button>
                        <button @click="viewSEO(blog)" class="block w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-gray-100">SEO Settings</button>
                        <button @click="viewRevisions(blog)" class="block w-full text-left px-4 py-2 text-sm text-indigo-600 hover:bg-gray-100">Revisions</button>
                        <button @click="deleteBlogAction(blog)" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100">Delete</button>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!blogs.length" class="text-center py-12 text-gray-500">
            No blog posts found.
          </div>
        </div>
      </div>
    </div>

    <!-- Categories Tab -->
    <div v-if="activeTab === 'categories'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Categories</h2>
        <button @click="showCategoryModal = true" class="btn btn-primary">Create Category</button>
      </div>
      
      <div class="card">
        <div v-if="categoriesLoading" class="text-center py-12">Loading...</div>
        <div v-else-if="categories.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Slug</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Posts</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="cat in categories" :key="cat.id">
                <td class="px-6 py-4 font-medium">{{ cat.name }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ cat.slug }}</td>
                <td class="px-6 py-4">{{ cat.post_count || 0 }}</td>
                <td class="px-6 py-4">
                  <button @click="editCategory(cat)" class="text-blue-600 hover:underline mr-2">Edit</button>
                  <button @click="deleteCategory(cat.id)" class="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500">No categories found.</div>
      </div>
    </div>

    <!-- Tags Tab -->
    <div v-if="activeTab === 'tags'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Tags</h2>
        <button @click="showTagModal = true" class="btn btn-primary">Create Tag</button>
      </div>
      
      <div class="card">
        <div v-if="tagsLoading" class="text-center py-12">Loading...</div>
        <div v-else-if="tags.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Slug</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Posts</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="tag in tags" :key="tag.id">
                <td class="px-6 py-4 font-medium">{{ tag.name }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ tag.slug }}</td>
                <td class="px-6 py-4">{{ tag.post_count || 0 }}</td>
                <td class="px-6 py-4">
                  <button @click="editTag(tag)" class="text-blue-600 hover:underline mr-2">Edit</button>
                  <button @click="deleteTag(tag.id)" class="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500">No tags found.</div>
      </div>
    </div>

    <!-- Create/Edit Blog Modal -->
    <div v-if="showCreateModal || editingBlog" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingBlog ? 'Edit Blog Post' : 'Create Blog Post' }}</h2>
            <button @click="closeModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="saveBlog" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Website *</label>
                <select 
                  v-model="blogForm.website_id" 
                  @change="onWebsiteChange"
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
                <label class="block text-sm font-medium mb-1">Title *</label>
                <input v-model="blogForm.title" type="text" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Slug</label>
                <input v-model="blogForm.slug" type="text" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Category</label>
                <select v-model="blogForm.category_id" class="w-full border rounded px-3 py-2">
                  <option value="">Select Category</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Status</label>
                <select v-model="blogForm.status" class="w-full border rounded px-3 py-2">
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>
            
            <!-- Authors Selection -->
            <div>
              <label class="block text-sm font-medium mb-1">Authors / Personas</label>
              <div class="flex flex-wrap gap-2 mb-2">
                <span
                  v-for="author in selectedAuthors"
                  :key="author.id"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800"
                >
                  <img 
                    v-if="author.profile_picture" 
                    :src="author.profile_picture" 
                    :alt="author.name"
                    class="w-5 h-5 rounded-full mr-2"
                  />
                  {{ author.name }}
                  <span v-if="author.designation" class="ml-1 text-xs text-purple-600">({{ author.designation }})</span>
                  <button
                    type="button"
                    @click="removeAuthor(author.id)"
                    class="ml-2 text-purple-600 hover:text-purple-800"
                  >
                    ×
                  </button>
                </span>
              </div>
              <select
                v-model="authorSelect"
                @change="addAuthor"
                :disabled="!blogForm.website_id || authorsLoading"
                class="w-full border rounded px-3 py-2"
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
              <p v-if="!blogForm.website_id" class="text-xs text-gray-500 mt-1">Please select a website first to see available authors</p>
            </div>
            
            <!-- Featured Image -->
            <div>
              <label class="block text-sm font-medium mb-1">Featured Image</label>
              <MediaPicker
                v-model="blogForm.featured_image_asset"
                :website-id="blogForm.website_id"
                :accept-types="'image/*'"
                trigger-label="Select Featured Image"
                modal-title="Select Featured Image"
                @selected="handleFeaturedImageSelected"
              />
              <div v-if="blogForm.featured_image || blogForm.featured_image_asset" class="mt-2">
                <img
                  :src="blogForm.featured_image || blogForm.featured_image_asset?.url"
                  alt="Featured image preview"
                  class="w-32 h-32 object-cover rounded border"
                />
                <button
                  type="button"
                  @click="removeFeaturedImage"
                  class="mt-2 text-sm text-red-600 hover:text-red-800"
                >
                  Remove Image
                </button>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">Tags</label>
              <div class="flex flex-wrap gap-2 mb-2">
                <span
                  v-for="tag in selectedTags"
                  :key="tag.id"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                >
                  {{ tag.name }}
                  <button
                    type="button"
                    @click="removeTag(tag.id)"
                    class="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              </div>
              <select
                v-model="tagSelect"
                @change="addTag"
                class="w-full border rounded px-3 py-2"
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
                class="mt-2 text-sm text-blue-600 hover:underline"
              >
                + Create New Tag
              </button>
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

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div class="lg:col-span-2">
                <label class="block text-sm font-medium mb-1">Content *</label>
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
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Meta Title</label>
                <input v-model="blogForm.meta_title" type="text" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Meta Description</label>
                <textarea v-model="blogForm.meta_description" rows="2" class="w-full border rounded px-3 py-2"></textarea>
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
              <div v-if="blogForm.faqs_data && blogForm.faqs_data.length" class="space-y-3">
                <div
                  v-for="(faq, index) in blogForm.faqs_data"
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
                      <textarea
                        v-model="faq.answer"
                        rows="3"
                        required
                        placeholder="Enter answer..."
                        class="w-full border rounded px-2 py-1 text-sm"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-gray-500 italic">No FAQs added. Click "+ Add FAQ" to add one.</p>
            </div>
            
            <!-- Resources Section -->
            <div class="border-t pt-4">
              <div class="flex items-center justify-between mb-3">
                <label class="block text-sm font-medium">Resources (Optional)</label>
                <button
                  type="button"
                  @click="addResource"
                  class="text-sm text-blue-600 hover:underline"
                >
                  + Add Resource
                </button>
              </div>
              <div v-if="blogForm.resources_data && blogForm.resources_data.length" class="space-y-3">
                <div
                  v-for="(resource, index) in blogForm.resources_data"
                  :key="index"
                  class="border rounded p-3 bg-gray-50"
                >
                  <div class="flex justify-between items-start mb-2">
                    <span class="text-sm font-medium text-gray-700">Resource {{ index + 1 }}</span>
                    <button
                      type="button"
                      @click="removeResource(index)"
                      class="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div class="space-y-2">
                    <div>
                      <label class="block text-xs font-medium mb-1">Title *</label>
                      <input
                        v-model="resource.title"
                        type="text"
                        required
                        placeholder="Resource title..."
                        class="w-full border rounded px-2 py-1 text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium mb-1">URL *</label>
                      <input
                        v-model="resource.url"
                        type="url"
                        required
                        placeholder="https://example.com"
                        class="w-full border rounded px-2 py-1 text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium mb-1">Description</label>
                      <textarea
                        v-model="resource.description"
                        rows="2"
                        placeholder="Resource description..."
                        class="w-full border rounded px-2 py-1 text-sm"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-gray-500 italic">No resources added. Click "+ Add Resource" to add one.</p>
            </div>
            
            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="saving" class="btn btn-primary">
                {{ saving ? 'Saving...' : (editingBlog ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Category Modal -->
    <div v-if="showCategoryModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingCategory ? 'Edit Category' : 'Create Category' }}</h2>
            <button @click="closeCategoryModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="saveCategory" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Name *</label>
              <input v-model="categoryForm.name" type="text" required class="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Description</label>
              <textarea v-model="categoryForm.description" rows="3" class="w-full border rounded px-3 py-2"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Website *</label>
                <input v-model="categoryForm.website" type="number" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Display Order</label>
                <input v-model.number="categoryForm.display_order" type="number" class="w-full border rounded px-3 py-2" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Meta Title</label>
                <input v-model="categoryForm.meta_title" type="text" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Meta Description</label>
                <textarea v-model="categoryForm.meta_description" rows="2" class="w-full border rounded px-3 py-2"></textarea>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <label class="flex items-center">
                <input v-model="categoryForm.is_featured" type="checkbox" class="mr-2" />
                <span class="text-sm">Featured</span>
              </label>
              <label class="flex items-center">
                <input v-model="categoryForm.is_active" type="checkbox" class="mr-2" />
                <span class="text-sm">Active</span>
              </label>
            </div>
            
            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closeCategoryModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Tag Modal -->
    <div v-if="showTagModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-lg w-full">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingTag ? 'Edit Tag' : 'Create Tag' }}</h2>
            <button @click="closeTagModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="saveTag" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Name *</label>
              <input v-model="tagForm.name" type="text" required class="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Website *</label>
              <input v-model="tagForm.website" type="number" required class="w-full border rounded px-3 py-2" />
            </div>
            
            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closeTagModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary">Save</button>
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
import { formatWebsiteName } from '@/utils/formatDisplay'

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
const availableAuthors = ref([])
const authorsLoading = ref(false)
const selectedAuthors = ref([])
const authorSelect = ref('')

const filters = ref({
  category: '',
  status: '',
  search: '',
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
    const res = await blogPagesAPI.listCategories({})
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
    
    // If there's only one website available, auto-select it (but still allow selection)
    if (availableWebsites.value.length === 1 && !blogForm.value.website_id) {
      blogForm.value.website_id = availableWebsites.value[0].id
      await loadAvailableAuthors(availableWebsites.value[0].id)
    }
  } catch (e) {
    console.error('Failed to load available websites:', e)
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
    
    if (editingBlog.value) {
      await blogPagesAPI.updateBlog(editingBlog.value.id, formData)
      message.value = 'Blog post updated successfully'
    } else {
      await blogPagesAPI.createBlog(formData)
      message.value = 'Blog post created successfully'
    }
    messageSuccess.value = true
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
  // TODO: Navigate to blog detail view
  console.log('View blog:', blog)
}

const publishBlogAction = async (blog) => {
  try {
    await blogPagesAPI.publishBlog(blog.id)
    message.value = 'Blog post published'
    messageSuccess.value = true
    await loadBlogs()
  } catch (e) {
    message.value = 'Failed to publish: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const unpublishBlogAction = async (blog) => {
  try {
    await blogPagesAPI.unpublishBlog(blog.id)
    message.value = 'Blog post unpublished'
    messageSuccess.value = true
    await loadBlogs()
  } catch (e) {
    message.value = 'Failed to unpublish: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const viewSEO = (blog) => {
  // TODO: Open SEO settings modal
  console.log('View SEO for:', blog)
}

const viewRevisions = (blog) => {
  // TODO: Open revisions modal
  console.log('View revisions for:', blog)
}

const showRevisionDiffModal = ref(false)
const revisionDiffData = ref(null)
const revisionDiffLoading = ref(false)

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
  if (!confirm(`Delete "${blog.title}"?`)) return
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
  if (!confirm('Delete this category?')) return
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
  if (!confirm('Delete this tag?')) return
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
  console.log('Health check results:', healthData)
  // Could show notifications or update UI based on health score
  if (healthData.overall_score < 60) {
    // Show warning if score is low
    console.warn('Content health score is low:', healthData.overall_score)
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
  availableAuthors.value = []
}

const resetFilters = () => {
  filters.value = { category: '', status: '', search: '' }
  loadBlogs()
}

const getStatusBadgeClass = (isPublished, status) => {
  if (isPublished) return 'bg-green-100 text-green-800'
  if (status === 'draft') return 'bg-yellow-100 text-yellow-800'
  if (status === 'archived') return 'bg-gray-100 text-gray-800'
  return 'bg-blue-100 text-blue-800'
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

