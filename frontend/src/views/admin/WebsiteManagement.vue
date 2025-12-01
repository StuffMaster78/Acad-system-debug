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

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadWebsites" class="w-full border rounded px-3 py-2">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="deleted">Deleted</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by name, domain..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Websites Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else>
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Domain</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Settings</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SEO</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="website in websites" :key="website.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div v-if="website.logo" class="flex-shrink-0 h-10 w-10 mr-3">
                    <img :src="website.logo" :alt="website.name" class="h-10 w-10 rounded object-cover" />
                  </div>
                  <div v-else class="flex-shrink-0 h-10 w-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-sm mr-3">
                    {{ getWebsiteInitials(website) }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-900">{{ website.name }}</div>
                    <div class="text-sm text-gray-500">{{ website.slug }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <a :href="website.domain" target="_blank" class="text-blue-600 hover:underline text-sm">
                  {{ website.domain }}
                </a>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-col gap-1">
                  <span :class="getStatusBadgeClass(website)" class="px-2 py-1 rounded-full text-xs font-medium inline-block w-fit">
                    {{ getStatusText(website) }}
                  </span>
                  <span v-if="website.is_deleted" class="text-xs text-gray-500">
                    Deleted: {{ formatDate(website.deleted_at) }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span :class="website.allow_registration ? 'text-green-600' : 'text-gray-400'" class="text-xs">
                      {{ website.allow_registration ? '✓' : '✗' }} Registration
                    </span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span :class="website.allow_guest_checkout ? 'text-green-600' : 'text-gray-400'" class="text-xs">
                      {{ website.allow_guest_checkout ? '✓' : '✗' }} Guest Checkout
                    </span>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="space-y-1">
                  <div v-if="website.meta_title" class="text-xs truncate max-w-xs" :title="website.meta_title">
                    Title: {{ website.meta_title }}
                  </div>
                  <div v-if="website.google_analytics_id" class="text-xs text-blue-600">
                    GA: {{ website.google_analytics_id }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center gap-2">
                  <button @click="viewWebsiteDetail(website)" class="text-blue-600 hover:underline" title="View Details">👁️</button>
                  <button @click="editWebsite(website)" class="text-green-600 hover:underline" title="Edit">✏️</button>
                  <div class="relative">
                    <button @click="toggleActionsMenu(website.id)" class="text-gray-600 hover:text-gray-900">⋯</button>
                    <div v-if="actionsMenuOpen === website.id" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border">
                      <div class="py-1">
                        <button @click="viewSEOSettings(website)" class="block w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-gray-100">SEO Settings</button>
                        <button @click="openTermsModal(website)" class="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-100">Edit Terms</button>
                        <button @click="viewActionLogs(website)" class="block w-full text-left px-4 py-2 text-sm text-indigo-600 hover:bg-gray-100">Action Logs</button>
                        <button @click="toggleActive(website)" v-if="!website.is_deleted" class="block w-full text-left px-4 py-2 text-sm text-yellow-600 hover:bg-gray-100">
                          {{ website.is_active ? 'Deactivate' : 'Activate' }}
                        </button>
                        <button @click="softDeleteWebsite(website)" v-if="!website.is_deleted && authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100">Soft Delete</button>
                        <button @click="restoreWebsite(website)" v-if="website.is_deleted && authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-100">Restore</button>
                        <button @click="deleteWebsitePermanently(website)" v-if="authStore.isSuperAdmin" class="block w-full text-left px-4 py-2 text-sm text-red-800 hover:bg-gray-100">Delete Permanently</button>
                      </div>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!websites.length" class="text-center py-12 text-gray-500">
          No websites found.
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
          <h2 class="text-2xl font-bold">SEO Settings - {{ selectedWebsite.name }}</h2>
          <button @click="closeSEOModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <form @submit.prevent="saveSEOSettings" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Meta Title</label>
            <input v-model="seoForm.meta_title" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Meta Description</label>
            <textarea v-model="seoForm.meta_description" rows="3" class="w-full border rounded px-3 py-2"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Google Analytics ID</label>
            <input v-model="seoForm.google_analytics_id" type="text" class="w-full border rounded px-3 py-2" placeholder="G-XXXXXXXXXX" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Google Search Console ID</label>
            <input v-model="seoForm.google_search_console_id" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Bing Webmaster ID</label>
            <input v-model="seoForm.bing_webmaster_id" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeSEOModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">Save SEO Settings</button>
          </div>
        </form>
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
const editingWebsite = ref(null)
const viewingWebsite = ref(null)
const selectedWebsite = ref(null)
const actionsMenuOpen = ref(null)

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

const message = ref('')
const messageSuccess = ref(false)

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
  // TODO: Navigate to action logs page or open modal
  window.location.href = `/activity?website=${website.id}`
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

const getStatusText = (website) => {
  if (website.is_deleted) return 'Deleted'
  if (website.is_active) return 'Active'
  return 'Inactive'
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
  
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
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
</style>

