<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Express Classes Management</h1>
        <p class="mt-2 text-gray-600">Manage single express class requests, inquiries, scope reviews, and assignments</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Inquiry</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.inquiry || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Scope Review</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.scope_review || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Priced</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.priced || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
        <p class="text-sm font-medium text-indigo-700 mb-1">Assigned</p>
        <p class="text-3xl font-bold text-indigo-900">{{ stats.assigned || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.in_progress || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200">
        <p class="text-sm font-medium text-gray-700 mb-1">Completed</p>
        <p class="text-3xl font-bold text-gray-900">{{ stats.completed || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadExpressClasses" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
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
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Class ID, client, course..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website" @change="loadExpressClasses" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Has Writer</label>
          <select v-model="filters.has_writer" @change="loadExpressClasses" class="w-full border rounded px-3 py-2">
            <option value="">All</option>
            <option value="true">Assigned</option>
            <option value="false">Unassigned</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Express Classes Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dates</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="expressClass in expressClasses" :key="expressClass.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ expressClass.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ expressClass.client_username || expressClass.client_email || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                <div class="flex flex-col">
                  <span class="font-medium">{{ expressClass.course || 'N/A' }}</span>
                  <span class="text-xs text-gray-500">{{ expressClass.discipline || 'N/A' }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span v-if="expressClass.assigned_writer_username">
                  {{ expressClass.assigned_writer_username }}
                </span>
                <span v-else class="text-gray-400 italic">Unassigned</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(expressClass.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ expressClass.status_display || expressClass.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span v-if="expressClass.price">
                  ${{ parseFloat(expressClass.price || 0).toFixed(2) }}
                  <span v-if="expressClass.installments_needed > 0" class="text-xs text-gray-500">
                    ({{ expressClass.installments_needed }} installments)
                  </span>
                </span>
                <span v-else class="text-gray-400 italic">Not priced</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex flex-col text-xs">
                  <span>Start: {{ formatDate(expressClass.start_date) }}</span>
                  <span>End: {{ formatDate(expressClass.end_date) }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button @click="viewExpressClass(expressClass)" class="text-blue-600 hover:underline">View</button>
                  <button 
                    @click="openMessagesForClass(expressClass)" 
                    class="text-blue-600 hover:underline flex items-center gap-1"
                    title="View Messages"
                  >
                    💬
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!loading && expressClasses.length === 0" class="text-center py-12 text-gray-500">
        <p>No express classes found</p>
      </div>

      <!-- Pagination -->
      <div v-if="expressClassesPagination.totalPages > 1" class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          Showing {{ ((expressClassesPagination.page - 1) * expressClassesPagination.pageSize) + 1 }} to 
          {{ Math.min(expressClassesPagination.page * expressClassesPagination.pageSize, expressClassesPagination.total) }} 
          of {{ expressClassesPagination.total }} results
        </div>
        <div class="flex gap-2">
          <button
            @click="goToExpressClassesPage(expressClassesPagination.page - 1)"
            :disabled="expressClassesPagination.page === 1"
            class="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          <span class="px-3 py-1 text-sm text-gray-700">
            Page {{ expressClassesPagination.page }} of {{ expressClassesPagination.totalPages }}
          </span>
          <button
            @click="goToExpressClassesPage(expressClassesPagination.page + 1)"
            :disabled="expressClassesPagination.page >= expressClassesPagination.totalPages"
            class="px-3 py-1 border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Express Class Detail Modal -->
    <div v-if="viewingExpressClass" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-4">
              <h2 class="text-2xl font-bold">Express Class #{{ viewingExpressClass.id }}</h2>
              <button 
                @click="showThreadsModal = true" 
                class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-md hover:shadow-lg"
                title="View and manage messages for this class"
              >
                <span class="text-lg">💬</span>
                <span>Messages</span>
                <span v-if="viewingExpressClass.threads_count !== undefined && viewingExpressClass.threads_count > 0" 
                      class="ml-1 px-2 py-0.5 bg-blue-800 rounded-full text-xs font-bold">
                  {{ viewingExpressClass.threads_count }}
                </span>
              </button>
            </div>
            <button @click="viewingExpressClass = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div class="grid grid-cols-2 gap-6 mb-6">
            <!-- Left Column -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Class Information</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Client:</span> {{ viewingExpressClass.client_username || viewingExpressClass.client_email || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Website:</span> {{ viewingExpressClass.website_name || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Status:</span> 
                  <span :class="getStatusClass(viewingExpressClass.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ viewingExpressClass.status_display || viewingExpressClass.status }}
                  </span>
                </div>
                <div><span class="font-medium text-gray-600">Institution:</span> {{ viewingExpressClass.institution || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Course:</span> {{ viewingExpressClass.course || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Discipline:</span> {{ viewingExpressClass.discipline || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Academic Level:</span> {{ viewingExpressClass.academic_level || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Start Date:</span> {{ formatDate(viewingExpressClass.start_date) }}</div>
                <div><span class="font-medium text-gray-600">End Date:</span> {{ formatDate(viewingExpressClass.end_date) }}</div>
              </div>

              <h3 class="text-lg font-semibold border-b pb-2 mt-4">Workload</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Discussion Posts:</span> {{ viewingExpressClass.number_of_discussion_posts || 0 }}</div>
                <div><span class="font-medium text-gray-600">Discussion Replies:</span> {{ viewingExpressClass.number_of_discussion_posts_replies || 0 }}</div>
                <div><span class="font-medium text-gray-600">Assignments:</span> {{ viewingExpressClass.number_of_assignments || 0 }}</div>
                <div><span class="font-medium text-gray-600">Exams:</span> {{ viewingExpressClass.number_of_exams || 0 }}</div>
                <div><span class="font-medium text-gray-600">Quizzes:</span> {{ viewingExpressClass.number_of_quizzes || 0 }}</div>
                <div><span class="font-medium text-gray-600">Projects:</span> {{ viewingExpressClass.number_of_projects || 0 }}</div>
                <div><span class="font-medium text-gray-600">Presentations:</span> {{ viewingExpressClass.number_of_presentations || 0 }}</div>
                <div><span class="font-medium text-gray-600">Papers:</span> {{ viewingExpressClass.number_of_papers || 0 }}</div>
                <div><span class="font-medium text-gray-600">Total Workload:</span> {{ viewingExpressClass.total_workload_in_pages || 'N/A' }}</div>
              </div>
            </div>

            <!-- Right Column -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Pricing & Assignment</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Price:</span> 
                  <span v-if="viewingExpressClass.price" class="font-bold text-green-600">
                    ${{ parseFloat(viewingExpressClass.price || 0).toFixed(2) }}
                  </span>
                  <span v-else class="text-gray-400 italic">Not set</span>
                </div>
                <div><span class="font-medium text-gray-600">Price Approved:</span> 
                  <span :class="viewingExpressClass.price_approved ? 'text-green-600' : 'text-yellow-600'">
                    {{ viewingExpressClass.price_approved ? 'Yes' : 'No' }}
                  </span>
                </div>
                <div><span class="font-medium text-gray-600">Installments:</span> 
                  {{ viewingExpressClass.installments_needed > 0 ? viewingExpressClass.installments_needed + ' installments' : 'Full payment' }}
                </div>
                <div><span class="font-medium text-gray-600">Assigned Writer:</span> 
                  <span v-if="viewingExpressClass.assigned_writer_username">
                    {{ viewingExpressClass.assigned_writer_username }}
                  </span>
                  <button v-else @click="openAssignWriterModal(viewingExpressClass)" class="text-blue-600 hover:underline text-xs">
                    Assign Writer
                  </button>
                </div>
                <div v-if="viewingExpressClass.reviewed_by_username">
                  <span class="font-medium text-gray-600">Reviewed By:</span> {{ viewingExpressClass.reviewed_by_username }}
                </div>
                <div v-if="viewingExpressClass.reviewed_at">
                  <span class="font-medium text-gray-600">Reviewed At:</span> {{ formatDateTime(viewingExpressClass.reviewed_at) }}
                </div>
              </div>

              <h3 class="text-lg font-semibold border-b pb-2 mt-4">School Login</h3>
              <div class="space-y-2 text-sm">
                <div v-if="viewingExpressClass.school_login_link">
                  <span class="font-medium text-gray-600">Login Link:</span>
                  <a :href="viewingExpressClass.school_login_link" target="_blank" class="text-blue-600 hover:underline ml-1">
                    {{ viewingExpressClass.school_login_link }}
                  </a>
                </div>
                <div v-if="viewingExpressClass.school_login_username">
                  <span class="font-medium text-gray-600">Username:</span> {{ viewingExpressClass.school_login_username }}
                </div>
                <div v-if="viewingExpressClass.school_login_password">
                  <span class="font-medium text-gray-600">Password:</span> 
                  <span class="font-mono bg-gray-100 px-2 py-1 rounded">{{ viewingExpressClass.school_login_password }}</span>
                </div>
                <div v-if="!viewingExpressClass.school_login_link && !viewingExpressClass.school_login_username">
                  <span class="text-gray-400 italic">No login credentials provided</span>
                </div>
              </div>

              <h3 class="text-lg font-semibold border-b pb-2 mt-4">Notes</h3>
              <div class="space-y-2 text-sm">
                <div v-if="viewingExpressClass.instructions">
                  <span class="font-medium text-gray-600">Instructions:</span>
                  <p class="mt-1 text-gray-700 whitespace-pre-wrap">{{ viewingExpressClass.instructions }}</p>
                </div>
                <div v-if="viewingExpressClass.scope_review_notes">
                  <span class="font-medium text-gray-600">Scope Review Notes:</span>
                  <p class="mt-1 text-gray-700 whitespace-pre-wrap">{{ viewingExpressClass.scope_review_notes }}</p>
                </div>
                <div v-if="viewingExpressClass.admin_notes">
                  <span class="font-medium text-gray-600">Admin Notes:</span>
                  <p class="mt-1 text-gray-700 whitespace-pre-wrap">{{ viewingExpressClass.admin_notes }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-4 border-t">
            <button 
              v-if="viewingExpressClass.status === 'inquiry' || viewingExpressClass.status === 'scope_review'" 
              @click="openScopeReviewModal(viewingExpressClass)" 
              class="btn btn-primary bg-orange-600 hover:bg-orange-700"
            >
              Review Scope & Set Price
            </button>
            <button 
              v-if="viewingExpressClass.status === 'priced' && !viewingExpressClass.assigned_writer" 
              @click="openAssignWriterModal(viewingExpressClass)" 
              class="btn btn-primary bg-indigo-600 hover:bg-indigo-700"
            >
              Assign Writer
            </button>
            <button 
              v-if="viewingExpressClass.status === 'assigned'" 
              @click="startProgress(viewingExpressClass)" 
              class="btn btn-primary bg-green-600 hover:bg-green-700"
            >
              Start Progress
            </button>
            <button 
              v-if="viewingExpressClass.status === 'in_progress'" 
              @click="completeExpressClass(viewingExpressClass)" 
              class="btn btn-primary bg-purple-600 hover:bg-purple-700"
            >
              Mark Complete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Scope Review Modal -->
    <div v-if="showScopeReviewModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Review Scope & Set Price</h3>
          <button @click="closeScopeReviewModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Scope Review Notes *</label>
            <textarea 
              v-model="scopeReviewForm.scope_review_notes" 
              rows="5" 
              class="w-full border rounded px-3 py-2"
              :class="{ 'border-red-500': scopeReviewFormErrors.scope_review_notes }"
              placeholder="Enter your scope review notes..."
            ></textarea>
            <p v-if="scopeReviewFormErrors.scope_review_notes" class="text-xs text-red-600 mt-1">{{ scopeReviewFormErrors.scope_review_notes }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Price *</label>
            <input 
              v-model.number="scopeReviewForm.price" 
              type="number" 
              step="0.01" 
              class="w-full border rounded px-3 py-2"
              :class="{ 'border-red-500': scopeReviewFormErrors.price }"
              placeholder="0.00"
            />
            <p v-if="scopeReviewFormErrors.price" class="text-xs text-red-600 mt-1">{{ scopeReviewFormErrors.price }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Installments Needed</label>
            <input 
              v-model.number="scopeReviewForm.installments_needed" 
              type="number" 
              min="0" 
              class="w-full border rounded px-3 py-2"
              :class="{ 'border-red-500': scopeReviewFormErrors.installments_needed }"
              placeholder="0 for full payment"
            />
            <p v-if="scopeReviewFormErrors.installments_needed" class="text-xs text-red-600 mt-1">{{ scopeReviewFormErrors.installments_needed }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Admin Notes (optional)</label>
            <textarea 
              v-model="scopeReviewForm.admin_notes" 
              rows="3" 
              class="w-full border rounded px-3 py-2"
              placeholder="Optional admin notes..."
            ></textarea>
          </div>
          <div class="flex gap-2 pt-4">
            <button @click="saveScopeReview" class="btn btn-primary flex-1">Save Review</button>
            <button @click="closeScopeReviewModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign Writer Modal -->
    <div v-if="showAssignWriterModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-3xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Assign Writer to Express Class #{{ currentExpressClassForAction?.id }}</h3>
          <button @click="closeAssignWriterModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        
        <div v-if="currentExpressClassForAction" class="mb-4 p-4 bg-gray-50 rounded">
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div>
              <strong class="text-gray-700">Client:</strong>
              <span class="text-gray-600 ml-2">{{ currentExpressClassForAction.client_username || currentExpressClassForAction.client_email || 'N/A' }}</span>
            </div>
            <div>
              <strong class="text-gray-700">Course:</strong>
              <span class="text-gray-600 ml-2">{{ currentExpressClassForAction.course || 'N/A' }}</span>
            </div>
            <div>
              <strong class="text-gray-700">Status:</strong>
              <span :class="getStatusClass(currentExpressClassForAction.status)" class="ml-2 px-2 py-1 rounded-full text-xs font-medium">
                {{ currentExpressClassForAction.status_display || currentExpressClassForAction.status }}
              </span>
            </div>
            <div>
              <strong class="text-gray-700">Price:</strong>
              <span class="text-gray-600 ml-2">${{ parseFloat(currentExpressClassForAction.price || 0).toFixed(2) }}</span>
            </div>
            <div v-if="currentExpressClassForAction.assigned_writer" class="col-span-2">
              <strong class="text-gray-700">Currently Assigned Writer:</strong>
              <span class="text-gray-600 ml-2">
                {{ currentExpressClassForAction.assigned_writer_username || 'N/A' }}
              </span>
              <span class="text-xs text-yellow-600 ml-2">(Will be replaced)</span>
            </div>
          </div>
        </div>

        <!-- Admin Notes Section -->
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1">Admin Notes (Optional)</label>
          <textarea
            v-model="assignWriterForm.admin_notes"
            rows="3"
            placeholder="Add any notes about this assignment..."
            class="w-full border rounded px-3 py-2 text-sm"
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">These notes will be saved with the assignment</p>
        </div>
        
        <div v-if="writersLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600">Loading available writers...</span>
        </div>
        
        <div v-else-if="availableWriters.length === 0" class="text-center py-12 text-gray-500">
          <p>No available writers found</p>
        </div>
        
        <div v-else class="space-y-3">
          <div class="mb-4">
            <input
              v-model="writerSearchQuery"
              type="text"
              placeholder="Search writers by name, email, or username..."
              class="w-full border rounded px-3 py-2"
            />
          </div>
          
          <div class="max-h-96 overflow-y-auto space-y-2">
            <div
              v-for="writer in filteredWriters"
              :key="writer.id"
              class="p-4 border rounded hover:bg-gray-50 cursor-pointer transition-colors"
              :class="{ 'bg-blue-50 border-blue-300': selectedWriterId === writer.id }"
              @click="selectedWriterId = writer.id"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3">
                    <input
                      type="radio"
                      :id="`writer-${writer.id}`"
                      :value="writer.id"
                      v-model="selectedWriterId"
                      class="cursor-pointer"
                    />
                    <label :for="`writer-${writer.id}`" class="cursor-pointer flex-1">
                      <div class="font-medium text-gray-900">
                        {{ writer.username || writer.email || `Writer #${writer.id}` }}
                      </div>
                      <div class="text-sm text-gray-600 mt-1">
                        <span v-if="writer.email">{{ writer.email }}</span>
                        <span v-if="writer.writer_profile">
                          <span v-if="writer.writer_profile.rating" class="ml-2">
                            ⭐ {{ parseFloat(writer.writer_profile.rating).toFixed(1) }}
                          </span>
                          <span v-if="writer.workload" class="ml-2">
                            Workload: {{ writer.workload.active_orders_count || 0 }}/{{ writer.workload.max_orders || 'N/A' }}
                            <span v-if="writer.workload.capacity !== undefined" class="ml-1">
                              (Capacity: {{ writer.workload.capacity }})
                            </span>
                          </span>
                        </span>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex gap-2 pt-4 border-t mt-4">
          <button
            @click="selectedWriterId && saveAssignWriter()"
            :disabled="!selectedWriterId || assigningWriter"
            class="btn btn-primary flex-1"
          >
            {{ assigningWriter ? 'Assigning...' : (currentExpressClassForAction?.assigned_writer ? 'Reassign Writer' : 'Assign Writer') }}
          </button>
          <button 
            @click="closeAssignWriterModal" 
            :disabled="assigningWriter"
            class="btn btn-secondary flex-1"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Message Threads Modal -->
    <ClassMessageThreads
      v-if="viewingExpressClass"
      :show="showThreadsModal"
      :class-id="viewingExpressClass.id"
      class-type="express"
      @close="showThreadsModal = false"
    />

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
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { expressClassesAPI, usersAPI, writerAssignmentAPI } from '@/api'
import apiClient from '@/api/client'
import ClassMessageThreads from '@/components/classes/ClassMessageThreads.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { useToast } from '@/composables/useToast'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const router = useRouter()

const confirm = useConfirmDialog()
const { handleError, handleSuccess, handleValidationError, handleWarning } = useErrorHandler()
const { warning: showWarning } = useToast()

const componentError = ref(null)
const initialLoading = ref(true)
const loading = ref(false)
const expressClasses = ref([])
const websites = ref([])
const writers = ref([])
const availableWriters = ref([])
const writersLoading = ref(false)
const assigningWriter = ref(false)
const selectedWriterId = ref(null)
const writerSearchQuery = ref('')
const viewingExpressClass = ref(null)
const showScopeReviewModal = ref(false)
const showAssignWriterModal = ref(false)
const showThreadsModal = ref(false)
const currentExpressClassForAction = ref(null)

const filters = ref({
  status: '',
  search: '',
  website: '',
  has_writer: '',
})

// Pagination
const expressClassesPagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

const stats = ref({
  total: 0,
  inquiry: 0,
  scope_review: 0,
  priced: 0,
  assigned: 0,
  in_progress: 0,
  completed: 0,
})

const scopeReviewForm = ref({
  scope_review_notes: '',
  price: 0,
  installments_needed: 0,
  admin_notes: '',
})

const scopeReviewFormErrors = ref({})

const assignWriterForm = ref({
  writer_id: '',
  admin_notes: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadExpressClasses()
  }, 500)
}

const loadExpressClasses = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: expressClassesPagination.value.pageSize
    }
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website
    if (filters.value.has_writer !== '') {
      if (filters.value.has_writer === 'true') {
        params.assigned_writer__isnull = false
      } else {
        params.assigned_writer__isnull = true
      }
    }

    const res = await expressClassesAPI.list(params)
    expressClasses.value = res.data.results || res.data || []
    
    // Update pagination
    if (res.data.count !== undefined) {
      expressClassesPagination.value = {
        page: res.data.page || page,
        pageSize: res.data.page_size || expressClassesPagination.value.pageSize,
        total: res.data.count || 0,
        totalPages: Math.ceil((res.data.count || 0) / (res.data.page_size || expressClassesPagination.value.pageSize))
      }
    }
    
    // Calculate stats from all classes (if no pagination) or current page
    if (!res.data.count) {
      stats.value.total = expressClasses.value.length
      stats.value.inquiry = expressClasses.value.filter(c => c.status === 'inquiry').length
      stats.value.scope_review = expressClasses.value.filter(c => c.status === 'scope_review').length
      stats.value.priced = expressClasses.value.filter(c => c.status === 'priced').length
      stats.value.assigned = expressClasses.value.filter(c => c.status === 'assigned').length
      stats.value.in_progress = expressClasses.value.filter(c => c.status === 'in_progress').length
      stats.value.completed = expressClasses.value.filter(c => c.status === 'completed').length
    }
  } catch (error) {
    console.error('Error loading express classes:', error)
    handleError(error, { action: 'loading express classes' })
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading websites:', error)
  }
}

const loadWriters = async () => {
  try {
    const res = await usersAPI.list({ role: 'writer' })
    writers.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading writers:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    search: '',
    website: '',
    has_writer: '',
  }
  loadExpressClasses()
}

const viewExpressClass = async (expressClass) => {
  // Navigate to the express class detail page instead of opening a modal
  router.push({ name: 'AdminExpressClassDetail', params: { id: expressClass.id } })
}

const openMessagesForClass = async (expressClass) => {
  // Set viewing class so the modal has the correct class ID
  if (!viewingExpressClass.value || viewingExpressClass.value.id !== expressClass.id) {
    try {
      const res = await expressClassesAPI.get(expressClass.id)
      viewingExpressClass.value = res.data
    } catch (error) {
      console.error('Error loading express class for messages:', error)
      // Still open modal with the class ID we have
      viewingExpressClass.value = { id: expressClass.id }
    }
  }
  showThreadsModal.value = true
}

const openScopeReviewModal = (expressClass) => {
  currentExpressClassForAction.value = expressClass
  scopeReviewForm.value = {
    scope_review_notes: expressClass.scope_review_notes || '',
    price: expressClass.price || 0,
    installments_needed: expressClass.installments_needed || 0,
    admin_notes: expressClass.admin_notes || '',
  }
  showScopeReviewModal.value = true
}

const closeScopeReviewModal = () => {
  showScopeReviewModal.value = false
  currentExpressClassForAction.value = null
  scopeReviewForm.value = {
    scope_review_notes: '',
    price: 0,
    installments_needed: 0,
    admin_notes: '',
  }
  scopeReviewFormErrors.value = {}
}

const validateScopeReviewForm = () => {
  scopeReviewFormErrors.value = {}
  let isValid = true

  if (!scopeReviewForm.value.scope_review_notes?.trim()) {
    scopeReviewFormErrors.value.scope_review_notes = 'Scope review notes are required'
    isValid = false
  }
  if (!scopeReviewForm.value.price || scopeReviewForm.value.price <= 0) {
    scopeReviewFormErrors.value.price = 'Price must be greater than 0'
    isValid = false
  }
  if (scopeReviewForm.value.installments_needed < 0) {
    scopeReviewFormErrors.value.installments_needed = 'Installments cannot be negative'
    isValid = false
  }

  return isValid
}

const saveScopeReview = async () => {
  if (!currentExpressClassForAction.value) return
  
  if (!validateScopeReviewForm()) {
    handleWarning('Please correct the errors in the form')
    return
  }
  
  try {
    await expressClassesAPI.reviewScope(currentExpressClassForAction.value.id, scopeReviewForm.value)
    handleSuccess('Scope reviewed and price set successfully')
    closeScopeReviewModal()
    if (viewingExpressClass.value && viewingExpressClass.value.id === currentExpressClassForAction.value.id) {
      await viewExpressClass(currentExpressClassForAction.value)
    }
    loadExpressClasses()
  } catch (error) {
    if (error?.response?.status === 422) {
      handleValidationError(error)
      if (error.response?.data?.errors) {
        scopeReviewFormErrors.value = { ...scopeReviewFormErrors.value, ...error.response.data.errors }
      }
    } else {
      handleError(error, { action: 'reviewing scope' })
    }
  }
}

const filteredWriters = computed(() => {
  if (!writerSearchQuery.value) return availableWriters.value
  
  const query = writerSearchQuery.value.toLowerCase()
  return availableWriters.value.filter(writer => {
    const username = (writer.username || '').toLowerCase()
    const email = (writer.email || '').toLowerCase()
    const fullName = (writer.full_name || writer.get_full_name || '').toLowerCase()
    return username.includes(query) || email.includes(query) || fullName.includes(query)
  })
})

const openAssignWriterModal = async (expressClass) => {
  if (!expressClass || !expressClass.id) {
    handleError('Invalid express class data', { action: 'opening assign writer modal' })
    return
  }
  currentExpressClassForAction.value = expressClass
  showAssignWriterModal.value = true
  await loadAvailableWriters()
}

const closeAssignWriterModal = () => {
  showAssignWriterModal.value = false
  availableWriters.value = []
  selectedWriterId.value = null
  writerSearchQuery.value = ''
  assignWriterForm.value = {
    writer_id: '',
    admin_notes: '',
  }
  // Don't clear currentExpressClassForAction immediately - might be needed for retry
}

const loadAvailableWriters = async () => {
  writersLoading.value = true
  try {
    // Use the same endpoint as order assignment for consistency
    const response = await writerAssignmentAPI.getAvailableWriters()
    availableWriters.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load available writers:', error)
    handleError(error, { action: 'loading available writers' })
  } finally {
    writersLoading.value = false
  }
}

const saveAssignWriter = async () => {
  if (!currentExpressClassForAction.value) return
  
  const writerId = selectedWriterId.value || assignWriterForm.value.writer_id
  if (!writerId) {
    handleWarning('Please select a writer to assign')
    return
  }
  
  const isReassignment = currentExpressClassForAction.value.assigned_writer && 
                         currentExpressClassForAction.value.assigned_writer.id !== writerId
  
  // Confirm reassignment if writer is already assigned
  if (isReassignment) {
    const currentWriter = currentExpressClassForAction.value.assigned_writer?.username || 
                         currentExpressClassForAction.value.assigned_writer?.email || 
                         'another writer'
    const confirmed = await confirm.showDialog(
      `This express class is already assigned to ${currentWriter}. Do you want to reassign it to the selected writer?`,
      'Reassign Writer',
      {
        variant: 'warning',
        icon: '⚠️',
        confirmText: 'Reassign',
        cancelText: 'Cancel'
      }
    )
    if (!confirmed) return
  }
  
  const expressClassId = currentExpressClassForAction.value.id
  assigningWriter.value = true
  try {
    await expressClassesAPI.assignWriter(expressClassId, {
      writer_id: writerId,
      admin_notes: assignWriterForm.value.admin_notes || undefined
    })
    handleSuccess(isReassignment ? 'Writer reassigned successfully' : 'Writer assigned successfully')
    closeAssignWriterModal()
    currentExpressClassForAction.value = null
    if (viewingExpressClass.value && viewingExpressClass.value.id === expressClassId) {
      await viewExpressClass({ id: expressClassId })
    }
    loadExpressClasses()
  } catch (error) {
    if (error?.response?.status === 422) {
      handleValidationError(error)
    } else {
      handleError(error, { action: 'assigning writer' })
    }
    // Don't clear currentExpressClassForAction on error so user can retry
  } finally {
    assigningWriter.value = false
  }
}

const startProgress = async (expressClass) => {
  try {
    await expressClassesAPI.startProgress(expressClass.id)
    handleSuccess('Progress started successfully')
    if (viewingExpressClass.value && viewingExpressClass.value.id === expressClass.id) {
      await viewExpressClass(expressClass)
    }
    loadExpressClasses()
  } catch (error) {
    handleError(error, { action: 'starting progress' })
  }
}

const completeExpressClass = async (expressClass) => {
  const confirmed = await confirm.showDialog(
    'Are you sure you want to mark this express class as completed?',
    'Mark as Complete',
    {
      variant: 'default',
      icon: '✅',
      confirmText: 'Mark Complete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await expressClassesAPI.complete(expressClass.id)
    handleSuccess('Express class marked as completed')
    if (viewingExpressClass.value && viewingExpressClass.value.id === expressClass.id) {
      await viewExpressClass(expressClass)
    }
    loadExpressClasses()
  } catch (error) {
    handleError(error, { action: 'completing express class' })
  }
}

const getStatusClass = (status) => {
  const classes = {
    'inquiry': 'bg-yellow-100 text-yellow-800',
    'scope_review': 'bg-orange-100 text-orange-800',
    'priced': 'bg-purple-100 text-purple-800',
    'assigned': 'bg-indigo-100 text-indigo-800',
    'in_progress': 'bg-green-100 text-green-800',
    'completed': 'bg-gray-100 text-gray-800',
    'cancelled': 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

// Pagination helpers
const goToExpressClassesPage = (page) => {
  expressClassesPagination.value.page = page
  loadExpressClasses(page)
}

onMounted(async () => {
  try {
    await Promise.all([
      loadExpressClasses(),
      loadWebsites(),
      loadWriters()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing ExpressClassesManagement:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

