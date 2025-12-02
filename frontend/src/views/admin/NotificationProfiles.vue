<template>
  <div class="notification-profiles">
    <!-- Header -->
    <div class="header">
      <h1>Notification Profiles</h1>
      <div class="header-actions">
        <button @click="handleCreateClick" class="btn btn-primary">
          <span>➕</span> Create Profile
        </button>
        <button @click="loadProfiles" :disabled="loading" class="btn btn-secondary">
          <span v-if="loading">Loading...</span>
          <span v-else>🔄 Refresh</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="summary" class="summary-cards">
      <div class="summary-card">
        <div class="summary-label">Total Profiles</div>
        <div class="summary-value">{{ summary.total_profiles }}</div>
      </div>
      <div class="summary-card">
        <div class="summary-label">Default Profiles</div>
        <div class="summary-value">{{ summary.default_profiles }}</div>
      </div>
      <div class="summary-card">
        <div class="summary-label">Email Enabled</div>
        <div class="summary-value">{{ summary.channels.email_enabled }}</div>
      </div>
      <div class="summary-card">
        <div class="summary-label">DND Enabled</div>
        <div class="summary-value">{{ summary.dnd_enabled }}</div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="filters">
      <div class="filters-row">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="Search profiles by name or description..."
          class="search-input"
        />

        <div class="filters-inline">
          <div class="filter-group">
            <label class="filter-label">Default</label>
            <select v-model="filters.default" class="filter-select">
              <option value="all">All</option>
              <option value="default">Default only</option>
              <option value="non_default">Non‑default</option>
            </select>
          </div>

          <div class="filter-group">
            <label class="filter-label">DND</label>
            <select v-model="filters.dnd" class="filter-select">
              <option value="all">All</option>
              <option value="enabled">Enabled</option>
              <option value="disabled">Disabled</option>
            </select>
          </div>

          <div class="filter-group">
            <label class="filter-label">Channel</label>
            <select v-model="filters.channel" class="filter-select">
              <option value="all">All</option>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
              <option value="push">Push</option>
              <option value="in_app">In‑App</option>
            </select>
          </div>

          <div class="filter-group" v-if="websiteOptions.length">
            <label class="filter-label">Website</label>
            <select v-model="filters.website" class="filter-select">
              <option value="all">All</option>
              <option
                v-for="site in websiteOptions"
                :key="site"
                :value="site"
              >
                {{ site }}
              </option>
            </select>
          </div>

          <button
            v-if="hasActiveFilters"
            class="btn btn-ghost-sm"
            type="button"
            @click="resetFilters"
          >
            Reset filters
          </button>
        </div>
      </div>
    </div>

    <!-- Loading / Error / Table -->
    <div v-if="loading && !profiles.length" class="loading">Loading profiles...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="profiles-table-wrapper">
      <div v-if="displayedProfiles.length === 0" class="empty-state">
        <p>No notification profiles match your filters.</p>
        <button @click="handleCreateClick" class="btn btn-primary">
          Create Your First Profile
        </button>
      </div>

      <div v-else class="table-container">
        <table class="profiles-table">
          <thead>
            <tr>
              <th @click="setSort('name')">
                <span>Name</span>
                <span class="sort-indicator">{{ sortIcon('name') }}</span>
              </th>
              <th @click="setSort('website_name')">
                <span>Website</span>
                <span class="sort-indicator">{{ sortIcon('website_name') }}</span>
              </th>
              <th @click="setSort('is_default')">
                <span>Default</span>
                <span class="sort-indicator">{{ sortIcon('is_default') }}</span>
              </th>
              <th>Channels</th>
              <th @click="setSort('dnd_enabled')">
                <span>DND</span>
                <span class="sort-indicator">{{ sortIcon('dnd_enabled') }}</span>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="profile in displayedProfiles"
              :key="profile.id"
            >
              <td>
                <div class="cell-name">
                  <div class="cell-title">
                    <button
                      type="button"
                      class="link-button"
                      @click="openDetail(profile)"
                    >
                      {{ profile.name }}
                    </button>
                    <span
                      v-if="profile.is_default"
                      class="badge badge-primary"
                    >
                      Default
                    </span>
                  </div>
                  <div
                    v-if="profile.description"
                    class="cell-description"
                  >
                    {{ profile.description }}
                  </div>
                </div>
              </td>
              <td>
                <span class="cell-website">
                  {{ profile.website_name || 'All / Default' }}
                </span>
              </td>
              <td>
                <span
                  :class="[
                    'pill',
                    profile.is_default ? 'pill-success' : 'pill-muted'
                  ]"
                >
                  {{ profile.is_default ? 'Yes' : 'No' }}
                </span>
              </td>
              <td>
                <div class="cell-channels">
                  <span
                    :class="['channel-pill', profile.email_enabled ? 'on' : 'off']"
                    title="Email"
                  >
                    ✉️
                  </span>
                  <span
                    :class="['channel-pill', profile.sms_enabled ? 'on' : 'off']"
                    title="SMS"
                  >
                    📱
                  </span>
                  <span
                    :class="['channel-pill', profile.push_enabled ? 'on' : 'off']"
                    title="Push"
                  >
                    🔔
                  </span>
                  <span
                    :class="['channel-pill', profile.in_app_enabled ? 'on' : 'off']"
                    title="In‑App"
                  >
                    💬
                  </span>
                </div>
              </td>
              <td>
                <div v-if="profile.dnd_enabled" class="cell-dnd">
                  <span class="pill pill-warning">
                    {{ profile.dnd_start_hour }}:00 – {{ profile.dnd_end_hour }}:00
                  </span>
                </div>
                <span v-else class="pill pill-muted">
                  Off
                </span>
              </td>
              <td>
                <div class="cell-actions">
                  <button
                    type="button"
                    class="btn-link-sm"
                    @click="openDetail(profile)"
                    title="View details"
                  >
                    View
                  </button>
                  <button
                    type="button"
                    class="btn-link-sm"
                    @click="editProfile(profile)"
                    title="Edit profile"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    class="btn-link-sm"
                    @click="duplicateProfile(profile)"
                    title="Duplicate profile"
                  >
                    Duplicate
                  </button>
                  <button
                    type="button"
                    class="btn-link-sm"
                    @click="applyToUsers(profile)"
                    title="Apply to users"
                  >
                    Apply
                  </button>
                  <button
                    type="button"
                    class="btn-link-sm"
                    @click="openStatistics(profile)"
                    title="View statistics"
                  >
                    Stats
                  </button>
                  <button
                    type="button"
                    class="btn-link-sm text-danger"
                    @click="deleteProfile(profile)"
                    title="Delete profile"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ showEditModal ? 'Edit Profile' : 'Create Profile' }}</h2>
          <button @click="closeModal" class="btn-close">✕</button>
        </div>

        <form @submit.prevent="saveProfile" class="modal-body">
          <div class="form-group">
            <label>Profile Name *</label>
            <input
              v-model="formData.name"
              type="text"
              required
              placeholder="e.g., Quiet Hours Profile"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea
              v-model="formData.description"
              placeholder="Describe this profile..."
              class="form-control"
              rows="3"
            ></textarea>
          </div>

          <div class="form-section">
            <h3>Channel Settings</h3>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.email_enabled"
                  type="checkbox"
                />
                <span>Email Enabled</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.default_email"
                  type="checkbox"
                />
                <span>Default Email</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.sms_enabled"
                  type="checkbox"
                />
                <span>SMS Enabled</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.default_sms"
                  type="checkbox"
                />
                <span>Default SMS</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.push_enabled"
                  type="checkbox"
                />
                <span>Push Enabled</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.default_push"
                  type="checkbox"
                />
                <span>Default Push</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.in_app_enabled"
                  type="checkbox"
                />
                <span>In-App Enabled</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.default_in_app"
                  type="checkbox"
                />
                <span>Default In-App</span>
              </label>
            </div>
          </div>

          <div class="form-section">
            <h3>Do-Not-Disturb Settings</h3>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="formData.dnd_enabled"
                  type="checkbox"
                />
                <span>Enable Do-Not-Disturb</span>
              </label>
            </div>

            <div v-if="formData.dnd_enabled" class="form-row">
              <div class="form-group">
                <label>Start Hour (0-23)</label>
                <input
                  v-model.number="formData.dnd_start_hour"
                  type="number"
                  min="0"
                  max="23"
                  class="form-control"
                />
              </div>
              <div class="form-group">
                <label>End Hour (0-23)</label>
                <input
                  v-model.number="formData.dnd_end_hour"
                  type="number"
                  min="0"
                  max="23"
                  class="form-control"
                />
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="formData.is_default"
                type="checkbox"
              />
              <span>Set as Default Profile</span>
            </label>
          </div>

          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              <span v-if="saving">Saving...</span>
              <span v-else>{{ showEditModal ? 'Update' : 'Create' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Apply to Users Modal -->
    <div v-if="showApplyModal" class="modal-overlay" @click="showApplyModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Apply Profile to Users</h2>
          <button @click="showApplyModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>User IDs (comma-separated)</label>
            <input
              v-model="applyUserIds"
              type="text"
              placeholder="e.g., 1, 2, 3"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="overrideExisting" type="checkbox" />
              <span>Override Existing Preferences</span>
            </label>
          </div>
          <div class="modal-footer">
            <button @click="showApplyModal = false" class="btn btn-secondary">Cancel</button>
            <button @click="confirmApply" :disabled="applying" class="btn btn-primary">
              <span v-if="applying">Applying...</span>
              <span v-else>Apply Profile</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div
      v-if="showDetailModal && detailProfile"
      class="modal-overlay"
      @click="closeDetail"
    >
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>Profile Details – {{ detailProfile.name }}</h2>
          <button @click="closeDetail" class="btn-close">✕</button>
        </div>
        <div class="modal-body detail-body">
          <div class="detail-section">
            <h3>Overview</h3>
            <p v-if="detailProfile.description" class="detail-description">
              {{ detailProfile.description }}
            </p>
            <p v-else class="detail-description muted">
              No description provided.
            </p>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">Website</span>
                <span class="detail-value">
                  {{ detailProfile.website_name || 'All / Default' }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Default Profile</span>
                <span class="detail-value">
                  {{ detailProfile.is_default ? 'Yes' : 'No' }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">DND</span>
                <span class="detail-value">
                  <template v-if="detailProfile.dnd_enabled">
                    {{ detailProfile.dnd_start_hour }}:00 – {{ detailProfile.dnd_end_hour }}:00
                  </template>
                  <template v-else>
                    Off
                  </template>
                </span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3>Channels</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">Email</span>
                <span class="detail-value">
                  {{ detailProfile.email_enabled ? 'Enabled' : 'Disabled' }}
                  <span v-if="detailProfile.default_email" class="detail-tag">
                    Default
                  </span>
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">SMS</span>
                <span class="detail-value">
                  {{ detailProfile.sms_enabled ? 'Enabled' : 'Disabled' }}
                  <span v-if="detailProfile.default_sms" class="detail-tag">
                    Default
                  </span>
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Push</span>
                <span class="detail-value">
                  {{ detailProfile.push_enabled ? 'Enabled' : 'Disabled' }}
                  <span v-if="detailProfile.default_push" class="detail-tag">
                    Default
                  </span>
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">In‑App</span>
                <span class="detail-value">
                  {{ detailProfile.in_app_enabled ? 'Enabled' : 'Disabled' }}
                  <span v-if="detailProfile.default_in_app" class="detail-tag">
                    Default
                  </span>
                </span>
              </div>
            </div>
          </div>

          <div class="detail-actions">
            <button
              class="btn btn-secondary"
              type="button"
              @click="openStatistics(detailProfile)"
            >
              View Statistics
            </button>
            <button
              class="btn btn-primary"
              type="button"
              @click="applyToUsers(detailProfile)"
            >
              Apply to Users
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Modal -->
    <div
      v-if="showStatsModal && statsProfile"
      class="modal-overlay"
      @click="closeStatistics"
    >
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Profile Statistics – {{ statsProfile.name }}</h2>
          <button @click="closeStatistics" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="statsLoading" class="loading">
            Loading statistics...
          </div>
          <div v-else-if="statsError" class="error">
            {{ statsError }}
          </div>
          <div v-else-if="statsData" class="stats-grid">
            <div class="stats-section">
              <h3>Channels Enabled</h3>
              <ul class="stats-list">
                <li>Email: {{ statsData.channels_enabled?.email ? 'Yes' : 'No' }}</li>
                <li>SMS: {{ statsData.channels_enabled?.sms ? 'Yes' : 'No' }}</li>
                <li>Push: {{ statsData.channels_enabled?.push ? 'Yes' : 'No' }}</li>
                <li>
                  In‑App: {{ statsData.channels_enabled?.in_app ? 'Yes' : 'No' }}
                </li>
              </ul>
            </div>
            <div class="stats-section">
              <h3>Profile Status</h3>
              <ul class="stats-list">
                <li>
                  DND:
                  <span v-if="statsData.dnd_enabled">
                    Enabled ({{ statsData.dnd_hours }})
                  </span>
                  <span v-else>Disabled</span>
                </li>
                <li>Default: {{ statsData.is_default ? 'Yes' : 'No' }}</li>
              </ul>
            </div>
          </div>
          <div v-else class="muted">
            No statistics available for this profile.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { notificationProfilesApi } from '@/api/admin/notifications'

export default {
  name: 'NotificationProfiles',
  data() {
    return {
      loading: false,
      saving: false,
      applying: false,
      error: null,
      profiles: [],
      summary: null,
      searchQuery: '',
      searchTimeout: null,
      
      // Modal states
      showCreateModal: false,
      showEditModal: false,
      showApplyModal: false,
      
      // Form data
      formData: {
        name: '',
        description: '',
        default_email: true,
        default_sms: false,
        default_push: false,
        default_in_app: true,
        email_enabled: true,
        sms_enabled: false,
        push_enabled: false,
        in_app_enabled: true,
        dnd_enabled: false,
        dnd_start_hour: 22,
        dnd_end_hour: 6,
        is_default: false,
      },
      
      // Apply modal data
      selectedProfile: null,
      applyUserIds: '',
      overrideExisting: false,

      // Table UX state
      filters: {
        default: 'all',
        dnd: 'all',
        channel: 'all',
        website: 'all',
      },
      sortKey: 'name',
      sortDirection: 'asc',

      // Detail & statistics modals
      showDetailModal: false,
      detailProfile: null,
      showStatsModal: false,
      statsProfile: null,
      statsData: null,
      statsLoading: false,
      statsError: null,
    }
  },
  mounted() {
    this.loadProfiles()
    this.loadSummary()
  },
  computed: {
    websiteOptions() {
      const names = new Set()
      this.profiles.forEach(p => {
        if (p.website_name) {
          names.add(p.website_name)
        }
      })
      return Array.from(names).sort()
    },
    hasActiveFilters() {
      return (
        this.filters.default !== 'all' ||
        this.filters.dnd !== 'all' ||
        this.filters.channel !== 'all' ||
        this.filters.website !== 'all'
      )
    },
    displayedProfiles() {
      let items = [...this.profiles]

      // Client-side filters (in addition to server search)
      items = items.filter(profile => {
        // Default filter
        if (this.filters.default === 'default' && !profile.is_default) {
          return false
        }
        if (this.filters.default === 'non_default' && profile.is_default) {
          return false
        }

        // DND filter
        if (this.filters.dnd === 'enabled' && !profile.dnd_enabled) {
          return false
        }
        if (this.filters.dnd === 'disabled' && profile.dnd_enabled) {
          return false
        }

        // Channel filter
        if (this.filters.channel === 'email' && !profile.email_enabled) return false
        if (this.filters.channel === 'sms' && !profile.sms_enabled) return false
        if (this.filters.channel === 'push' && !profile.push_enabled) return false
        if (this.filters.channel === 'in_app' && !profile.in_app_enabled) return false

        // Website filter
        if (
          this.filters.website !== 'all' &&
          (profile.website_name || '') !== this.filters.website
        ) {
          return false
        }

        return true
      })

      // Sorting
      const key = this.sortKey
      const dir = this.sortDirection === 'asc' ? 1 : -1

      items.sort((a, b) => {
        const av = a[key]
        const bv = b[key]

        // Boolean sort
        if (typeof av === 'boolean' && typeof bv === 'boolean') {
          return (av === bv ? 0 : av ? -1 : 1) * dir
        }

        // Fallback to string comparison
        const as = (av ?? '').toString().toLowerCase()
        const bs = (bv ?? '').toString().toLowerCase()
        if (as < bs) return -1 * dir
        if (as > bs) return 1 * dir
        return 0
      })

      return items
    },
  },
  methods: {
    handleCreateClick() {
      console.log('Create button clicked')
      this.resetForm()
      this.showCreateModal = true
      this.showEditModal = false
    },
    
    async loadProfiles() {
      this.loading = true
      this.error = null
      try {
        const params = {}
        if (this.searchQuery) {
          params.search = this.searchQuery
        }
        const response = await notificationProfilesApi.listProfiles(params)
        this.profiles = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load profiles'
        console.error('Load profiles error:', err)
      } finally {
        this.loading = false
      }
    },
    
    async loadSummary() {
      try {
        const response = await notificationProfilesApi.getSummary()
        this.summary = response.data
      } catch (err) {
        console.error('Load summary error:', err)
      }
    },
    
    handleSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.loadProfiles()
      }, 500)
    },

    resetFilters() {
      this.filters = {
        default: 'all',
        dnd: 'all',
        channel: 'all',
        website: 'all',
      }
    },
    
    resetForm() {
      this.formData = {
        name: '',
        description: '',
        default_email: true,
        default_sms: false,
        default_push: false,
        default_in_app: true,
        email_enabled: true,
        sms_enabled: false,
        push_enabled: false,
        in_app_enabled: true,
        dnd_enabled: false,
        dnd_start_hour: 22,
        dnd_end_hour: 6,
        is_default: false,
      }
    },
    
    closeModal() {
      this.showCreateModal = false
      this.showEditModal = false
      this.resetForm()
      this.selectedProfile = null
    },
    
    editProfile(profile) {
      this.selectedProfile = profile
      this.formData = {
        name: profile.name,
        description: profile.description || '',
        default_email: profile.default_email,
        default_sms: profile.default_sms,
        default_push: profile.default_push,
        default_in_app: profile.default_in_app,
        email_enabled: profile.email_enabled,
        sms_enabled: profile.sms_enabled,
        push_enabled: profile.push_enabled,
        in_app_enabled: profile.in_app_enabled,
        dnd_enabled: profile.dnd_enabled,
        dnd_start_hour: profile.dnd_start_hour,
        dnd_end_hour: profile.dnd_end_hour,
        is_default: profile.is_default,
      }
      this.showEditModal = true
    },
    
    async saveProfile() {
      this.saving = true
      this.error = null
      try {
        if (this.showEditModal && this.selectedProfile) {
          await notificationProfilesApi.updateProfile(this.selectedProfile.id, this.formData)
          alert('Profile updated successfully!')
        } else {
          await notificationProfilesApi.createProfile(this.formData)
          alert('Profile created successfully!')
        }
        this.closeModal()
        this.loadProfiles()
        this.loadSummary()
      } catch (err) {
        this.error = err.response?.data?.detail || err.response?.data?.error || 'Failed to save profile'
        alert(this.error)
      } finally {
        this.saving = false
      }
    },
    
    async deleteProfile(profile) {
      if (!confirm(`Are you sure you want to delete "${profile.name}"?`)) {
        return
      }
      
      try {
        await notificationProfilesApi.deleteProfile(profile.id)
        alert('Profile deleted successfully!')
        this.loadProfiles()
        this.loadSummary()
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to delete profile')
      }
    },
    
    async duplicateProfile(profile) {
      const newName = prompt('Enter a name for the duplicated profile:', `Copy of ${profile.name}`)
      if (!newName) return
      
      try {
        await notificationProfilesApi.duplicateProfile(profile.id, { new_name: newName })
        alert('Profile duplicated successfully!')
        this.loadProfiles()
        this.loadSummary()
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to duplicate profile')
      }
    },
    
    // Sorting helpers
    setSort(key) {
      if (this.sortKey === key) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortKey = key
        this.sortDirection = 'asc'
      }
    },

    sortIcon(key) {
      if (this.sortKey !== key) return '↕'
      return this.sortDirection === 'asc' ? '↑' : '↓'
    },

    // Detail modal
    openDetail(profile) {
      this.detailProfile = profile
      this.showDetailModal = true
    },

    closeDetail() {
      this.showDetailModal = false
      this.detailProfile = null
    },

    // Statistics modal
    async openStatistics(profile) {
      this.showStatsModal = true
      this.statsProfile = profile
      this.statsLoading = true
      this.statsError = null
      this.statsData = null

      try {
        const response = await notificationProfilesApi.getStatistics(profile.id)
        this.statsData = response.data
      } catch (err) {
        this.statsError =
          err.response?.data?.detail ||
          err.response?.data?.error ||
          'Failed to load statistics'
      } finally {
        this.statsLoading = false
      }
    },

    closeStatistics() {
      this.showStatsModal = false
      this.statsProfile = null
      this.statsData = null
      this.statsError = null
      this.statsLoading = false
    },
    
    applyToUsers(profile) {
      this.selectedProfile = profile
      this.applyUserIds = ''
      this.overrideExisting = false
      this.showApplyModal = true
    },
    
    async confirmApply() {
      if (!this.applyUserIds.trim()) {
        alert('Please enter user IDs')
        return
      }
      
      const userIds = this.applyUserIds.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
      if (userIds.length === 0) {
        alert('Please enter valid user IDs')
        return
      }
      
      this.applying = true
      try {
        const response = await notificationProfilesApi.applyToUsers(this.selectedProfile.id, {
          user_ids: userIds,
          override_existing: this.overrideExisting
        })
        alert(`Profile applied to ${response.data.successful} user(s) successfully!`)
        this.showApplyModal = false
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to apply profile')
      } finally {
        this.applying = false
      }
    },
  }
}
</script>

<style scoped>
.notification-profiles {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header h1 {
  font-size: clamp(24px, 4vw, 32px);
  font-weight: 700;
  color: var(--gray-900);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.summary-label {
  font-size: 14px;
  color: var(--gray-600);
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--gray-900);
}

.filters {
  margin-bottom: 24px;
}

.search-input {
  width: 100%;
  max-width: 400px;
  padding: 12px;
  border: 1px solid var(--gray-300);
  border-radius: 6px;
  font-size: 14px;
}

.profiles-list {
  display: grid;
  gap: 20px;
}

.profile-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
  transition: box-shadow 0.2s;
}

.profile-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.profile-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-title h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.profile-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: var(--gray-100);
}

.btn-icon.btn-danger:hover {
  background: #fee2e2;
}

.profile-body {
  margin-bottom: 16px;
}

.profile-description {
  color: var(--gray-600);
  margin-bottom: 16px;
}

.profile-channels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.channel-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-label {
  font-weight: 500;
  color: var(--gray-700);
}

.channel-status.enabled {
  color: #10b981;
  font-weight: 500;
}

.channel-status.disabled {
  color: #ef4444;
}

.profile-dnd {
  margin-top: 12px;
  padding: 8px;
  background: var(--gray-50);
  border-radius: 4px;
}

.dnd-label {
  font-weight: 500;
  margin-right: 8px;
}

.dnd-hours {
  color: var(--gray-700);
}

.profile-website {
  margin-top: 8px;
  font-size: 14px;
  color: var(--gray-600);
}

.profile-footer {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--gray-200);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--gray-200);
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--gray-600);
}

.modal-body {
  padding: 20px;
}

.form-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--gray-200);
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: var(--gray-900);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--gray-700);
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--gray-300);
  border-radius: 6px;
  font-size: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid var(--gray-200);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--gray-600);
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 16px;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: var(--gray-600);
}

.error {
  color: #ef4444;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: var(--gray-200);
  color: var(--gray-700);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--gray-300);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-primary {
  background: #dbeafe;
  color: #1e40af;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

