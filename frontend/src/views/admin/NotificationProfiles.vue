<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
    <div class="max-w-7xl mx-auto">
    <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Notification Profiles
            </h1>
            <p class="text-gray-600 dark:text-gray-400">
              Manage notification preferences and channel settings for users
            </p>
          </div>
          <div class="flex gap-3">
            <button
              @click="loadProfiles"
              :disabled="loading"
              class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
            <button
              @click="handleCreateClick"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2 shadow-sm"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Create Profile
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
        <div v-if="summary" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Profiles</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ summary.total_profiles }}</p>
      </div>
              <div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
      </div>
      </div>
          </div>
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Default Profiles</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ summary.default_profiles }}</p>
              </div>
              <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Email Enabled</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ summary.channels.email_enabled }}</p>
              </div>
              <div class="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">DND Enabled</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ summary.dnd_enabled }}</p>
              </div>
              <div class="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              </div>
            </div>
      </div>
    </div>

    <!-- Search and Filters -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
          <div class="flex flex-col lg:flex-row gap-4">
            <div class="flex-1">
              <div class="relative">
                <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
      <input
        v-model="searchQuery"
        @input="handleSearch"
        type="text"
                  placeholder="Search profiles by name or description..."
                  class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </div>
            </div>
            <div class="flex flex-wrap gap-3">
              <select
                v-model="filters.default"
                class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              >
                <option value="all">All Defaults</option>
                <option value="default">Default only</option>
                <option value="non_default">Non-default</option>
              </select>
              <select
                v-model="filters.dnd"
                class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              >
                <option value="all">All DND</option>
                <option value="enabled">DND Enabled</option>
                <option value="disabled">DND Disabled</option>
              </select>
              <select
                v-model="filters.channel"
                class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              >
                <option value="all">All Channels</option>
                <option value="email">Email</option>
                <option value="sms">SMS</option>
                <option value="push">Push</option>
                <option value="in_app">In-App</option>
              </select>
              <select
                v-if="websiteOptions.length"
                v-model="filters.website"
                class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              >
                <option value="all">All Websites</option>
                <option v-for="site in websiteOptions" :key="site" :value="site">{{ site }}</option>
              </select>
              <button
                v-if="hasActiveFilters"
                @click="resetFilters"
                class="px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading / Error / Table -->
      <div v-if="loading && !profiles.length" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading profiles...</p>
          </div>
      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
        <p class="text-red-800 dark:text-red-400">{{ error }}</p>
      </div>
      <div v-else-if="displayedProfiles.length === 0" class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">No profiles found</h3>
        <p class="mt-2 text-gray-600 dark:text-gray-400">No notification profiles match your filters.</p>
        <button @click="handleCreateClick" class="mt-6 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
          Create Your First Profile
            </button>
          </div>
      <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th
                  @click="setSort('name')"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <div class="flex items-center gap-2">
                    <span>Name</span>
                    <span class="text-gray-400">{{ sortIcon('name') }}</span>
        </div>
                </th>
                <th
                  @click="setSort('website_name')"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <div class="flex items-center gap-2">
                    <span>Website</span>
                    <span class="text-gray-400">{{ sortIcon('website_name') }}</span>
            </div>
                </th>
                <th
                  @click="setSort('is_default')"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <div class="flex items-center gap-2">
                    <span>Default</span>
                    <span class="text-gray-400">{{ sortIcon('is_default') }}</span>
            </div>
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Channels</th>
                <th
                  @click="setSort('dnd_enabled')"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <div class="flex items-center gap-2">
                    <span>DND</span>
                    <span class="text-gray-400">{{ sortIcon('dnd_enabled') }}</span>
            </div>
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="profile in displayedProfiles"
                :key="profile.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div>
                      <button
                        @click="openDetail(profile)"
                        class="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                      >
                        {{ profile.name }}
                      </button>
                      <div v-if="profile.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {{ profile.description }}
                      </div>
                      <span
                        v-if="profile.is_default"
                        class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 mt-1"
                      >
                        Default
              </span>
            </div>
          </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-sm text-gray-900 dark:text-gray-100">
                    {{ profile.website_name || 'All / Default' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      profile.is_default
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                    ]"
                  >
                    {{ profile.is_default ? 'Yes' : 'No' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <span
                      :class="[
                        'inline-flex items-center justify-center w-8 h-8 rounded-full text-xs',
                        profile.email_enabled
                          ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-400'
                      ]"
                      title="Email"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </span>
                    <span
                      :class="[
                        'inline-flex items-center justify-center w-8 h-8 rounded-full text-xs',
                        profile.sms_enabled
                          ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-400'
                      ]"
                      title="SMS"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    </span>
                    <span
                      :class="[
                        'inline-flex items-center justify-center w-8 h-8 rounded-full text-xs',
                        profile.push_enabled
                          ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-400'
                      ]"
                      title="Push"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                    </span>
                    <span
                      :class="[
                        'inline-flex items-center justify-center w-8 h-8 rounded-full text-xs',
                        profile.in_app_enabled
                          ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-400'
                      ]"
                      title="In-App"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </span>
          </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div v-if="profile.dnd_enabled">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300">
                      {{ profile.dnd_start_hour }}:00 – {{ profile.dnd_end_hour }}:00
                    </span>
          </div>
                  <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300">
                    Off
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      @click="openDetail(profile)"
                      class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                      title="View details"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button
                      @click="editProfile(profile)"
                      class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                      title="Edit profile"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <div class="relative" v-click-outside="() => activeDropdown = null">
                      <button
                        @click="activeDropdown = activeDropdown === profile.id ? null : profile.id"
                        class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                        title="More options"
                      >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                        </svg>
                      </button>
                      <div
                        v-if="activeDropdown === profile.id"
                        class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 z-10"
                      >
                        <div class="py-1">
                          <button
                            @click="duplicateProfile(profile); activeDropdown = null"
                            class="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            Duplicate
                          </button>
                          <button
                            @click="applyToUsers(profile); activeDropdown = null"
                            class="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
            Apply to Users
          </button>
                          <button
                            @click="openStatistics(profile); activeDropdown = null"
                            class="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                          >
                            View Statistics
                          </button>
                          <hr class="my-1 border-gray-200 dark:border-gray-700">
                          <button
                            @click="deleteProfile(profile); activeDropdown = null"
                            class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                          >
                            Delete
          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showCreateModal || showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click="closeModal"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ showEditModal ? 'Edit Profile' : 'Create Profile' }}
          </h2>
          <button
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveProfile" class="p-6 space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Profile Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.name"
              type="text"
              required
              placeholder="e.g., Quiet Hours Profile"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea
              v-model="formData.description"
              placeholder="Describe this profile..."
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ></textarea>
          </div>

          <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Channel Settings</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-3">
                <label class="flex items-center gap-3 cursor-pointer">
                <input
                  v-model="formData.email_enabled"
                  type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Email Enabled</span>
              </label>
                <label class="flex items-center gap-3 cursor-pointer">
                <input
                  v-model="formData.default_email"
                  type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Default Email</span>
              </label>
            </div>
              <div class="space-y-3">
                <label class="flex items-center gap-3 cursor-pointer">
                <input
                  v-model="formData.sms_enabled"
                  type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                  <span class="text-sm text-gray-700 dark:text-gray-300">SMS Enabled</span>
              </label>
                <label class="flex items-center gap-3 cursor-pointer">
                <input
                  v-model="formData.default_sms"
                  type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Default SMS</span>
              </label>
            </div>
              <div class="space-y-3">
                <label class="flex items-center gap-3 cursor-pointer">
                <input
                  v-model="formData.push_enabled"
                  type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Push Enabled</span>
              </label>
                <label class="flex items-center gap-3 cursor-pointer">
                <input
                  v-model="formData.default_push"
                  type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Default Push</span>
              </label>
            </div>
              <div class="space-y-3">
                <label class="flex items-center gap-3 cursor-pointer">
                <input
                  v-model="formData.in_app_enabled"
                  type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                  <span class="text-sm text-gray-700 dark:text-gray-300">In-App Enabled</span>
              </label>
                <label class="flex items-center gap-3 cursor-pointer">
                <input
                  v-model="formData.default_in_app"
                  type="checkbox"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Default In-App</span>
              </label>
              </div>
            </div>
          </div>

          <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Do-Not-Disturb Settings</h3>
            <label class="flex items-center gap-3 cursor-pointer mb-4">
                <input
                  v-model="formData.dnd_enabled"
                  type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              <span class="text-sm text-gray-700 dark:text-gray-300">Enable Do-Not-Disturb</span>
              </label>
            <div v-if="formData.dnd_enabled" class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Start Hour (0-23)
                </label>
                <input
                  v-model.number="formData.dnd_start_hour"
                  type="number"
                  min="0"
                  max="23"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  End Hour (0-23)
                </label>
                <input
                  v-model.number="formData.dnd_end_hour"
                  type="number"
                  min="0"
                  max="23"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          <div>
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                v-model="formData.is_default"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">Set as Default Profile</span>
            </label>
          </div>

          <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ saving ? 'Saving...' : showEditModal ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Apply to Users Modal -->
    <div
      v-if="showApplyModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click="showApplyModal = false"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full"
        @click.stop
      >
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Apply Profile to Users</h2>
          <button
            @click="showApplyModal = false"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              User IDs (comma-separated)
            </label>
            <input
              v-model="applyUserIds"
              type="text"
              placeholder="e.g., 1, 2, 3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <label class="flex items-center gap-3 cursor-pointer">
            <input
              v-model="overrideExisting"
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">Override Existing Preferences</span>
            </label>
          <div class="flex justify-end gap-3 pt-4">
            <button
              @click="showApplyModal = false"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="confirmApply"
              :disabled="applying"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ applying ? 'Applying...' : 'Apply Profile' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div
      v-if="showDetailModal && detailProfile"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click="closeDetail"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            Profile Details – {{ detailProfile.name }}
          </h2>
          <button
            @click="closeDetail"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            </button>
          </div>
        <div class="p-6 space-y-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Overview</h3>
            <p v-if="detailProfile.description" class="text-gray-600 dark:text-gray-400">
              {{ detailProfile.description }}
            </p>
            <p v-else class="text-gray-400 dark:text-gray-500 italic">
              No description provided.
            </p>
            <div class="grid grid-cols-2 gap-4 mt-4">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Website</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ detailProfile.website_name || 'All / Default' }}
                </p>
        </div>
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Default Profile</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ detailProfile.is_default ? 'Yes' : 'No' }}
                </p>
      </div>
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">DND</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">
                  <template v-if="detailProfile.dnd_enabled">
                    {{ detailProfile.dnd_start_hour }}:00 – {{ detailProfile.dnd_end_hour }}:00
                  </template>
                  <template v-else>Off</template>
                </p>
              </div>
            </div>
          </div>

          <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Channels</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span class="text-sm text-gray-700 dark:text-gray-300">Email</span>
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'text-xs font-medium px-2 py-1 rounded',
                      detailProfile.email_enabled
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                        : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                    ]"
                  >
                    {{ detailProfile.email_enabled ? 'Enabled' : 'Disabled' }}
                  </span>
                  <span
                    v-if="detailProfile.default_email"
                    class="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
                  >
                    Default
                  </span>
                </div>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span class="text-sm text-gray-700 dark:text-gray-300">SMS</span>
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'text-xs font-medium px-2 py-1 rounded',
                      detailProfile.sms_enabled
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                        : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                    ]"
                  >
                    {{ detailProfile.sms_enabled ? 'Enabled' : 'Disabled' }}
                  </span>
                  <span
                    v-if="detailProfile.default_sms"
                    class="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
                  >
                    Default
                  </span>
                </div>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span class="text-sm text-gray-700 dark:text-gray-300">Push</span>
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'text-xs font-medium px-2 py-1 rounded',
                      detailProfile.push_enabled
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                        : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                    ]"
                  >
                    {{ detailProfile.push_enabled ? 'Enabled' : 'Disabled' }}
                  </span>
                  <span
                    v-if="detailProfile.default_push"
                    class="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
                  >
                    Default
                  </span>
                </div>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span class="text-sm text-gray-700 dark:text-gray-300">In‑App</span>
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'text-xs font-medium px-2 py-1 rounded',
                      detailProfile.in_app_enabled
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                        : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                    ]"
                  >
                    {{ detailProfile.in_app_enabled ? 'Enabled' : 'Disabled' }}
                  </span>
                  <span
                    v-if="detailProfile.default_in_app"
                    class="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
                  >
                    Default
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="openStatistics(detailProfile)"
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              View Statistics
            </button>
            <button
              @click="applyToUsers(detailProfile)"
              class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
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
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click="closeStatistics"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full"
        @click.stop
      >
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            Profile Statistics – {{ statsProfile.name }}
          </h2>
          <button
            @click="closeStatistics"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <div v-if="statsLoading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600 dark:text-gray-400">Loading statistics...</p>
          </div>
          <div v-else-if="statsError" class="text-red-600 dark:text-red-400">
            {{ statsError }}
          </div>
          <div v-else-if="statsData" class="space-y-6">
            <div>
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Channels Enabled</h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <p class="text-sm text-gray-600 dark:text-gray-400">Email</p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ statsData.channels_enabled?.email ? 'Yes' : 'No' }}
                  </p>
                </div>
                <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <p class="text-sm text-gray-600 dark:text-gray-400">SMS</p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ statsData.channels_enabled?.sms ? 'Yes' : 'No' }}
                  </p>
                </div>
                <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <p class="text-sm text-gray-600 dark:text-gray-400">Push</p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ statsData.channels_enabled?.push ? 'Yes' : 'No' }}
                  </p>
                </div>
                <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <p class="text-sm text-gray-600 dark:text-gray-400">In‑App</p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ statsData.channels_enabled?.in_app ? 'Yes' : 'No' }}
                  </p>
                </div>
              </div>
            </div>
            <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Profile Status</h3>
              <div class="space-y-3">
                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <span class="text-sm text-gray-700 dark:text-gray-300">DND</span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    <template v-if="statsData.dnd_enabled">
                      Enabled ({{ statsData.dnd_hours }})
                    </template>
                    <template v-else>Disabled</template>
                  </span>
                </div>
                <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <span class="text-sm text-gray-700 dark:text-gray-300">Default</span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ statsData.is_default ? 'Yes' : 'No' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
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
      activeDropdown: null,
      
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
  },
  directives: {
    'click-outside': {
      mounted(el, binding) {
        el.clickOutsideEvent = (event) => {
          if (!(el === event.target || el.contains(event.target))) {
            binding.value()
          }
        }
        document.addEventListener('click', el.clickOutsideEvent)
      },
      unmounted(el) {
        document.removeEventListener('click', el.clickOutsideEvent)
      }
    }
  }
}
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
