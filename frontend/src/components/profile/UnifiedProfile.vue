<template>
  <div class="unified-profile">
    <!-- Modern SaaS Profile Design -->
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center min-h-[600px]">
        <div class="text-center">
          <div class="relative w-16 h-16 mx-auto mb-4">
            <div class="absolute inset-0 border-4 border-primary-200 dark:border-primary-800 rounded-full"></div>
            <div class="absolute inset-0 border-4 border-transparent border-t-primary-600 dark:border-t-primary-400 rounded-full animate-spin"></div>
          </div>
          <p class="text-gray-600 dark:text-gray-400 font-medium">Loading profile...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-gradient-to-r from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border border-red-200 dark:border-red-800 rounded-2xl p-8 mb-6 backdrop-blur-sm shadow-lg">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0 w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-xl font-bold text-red-800 dark:text-red-200 mb-2">Error Loading Profile</h3>
            <p class="text-red-600 dark:text-red-300 mb-4">{{ error }}</p>
            <button
              @click="loadProfile"
              class="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>

      <!-- Profile Content -->
      <div v-else-if="profile" class="space-y-6">
        <!-- Simplified Header Section - Better UX -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <div class="px-6 py-6">
            <!-- Top Row: Avatar and Basic Info -->
            <div class="flex items-start gap-6 mb-6">
              <!-- Avatar Section -->
              <div class="relative group flex-shrink-0">
                <div class="relative">
                  <div 
                    class="relative w-24 h-24 sm:w-28 sm:h-28 rounded-full overflow-hidden border-2 border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 transition-all duration-300 group-hover:border-primary-400 dark:group-hover:border-primary-500 cursor-pointer shadow-sm group-hover:shadow-md"
                    @click="showAvatarUpload = true"
                  >
                    <Avatar
                      v-if="profile.user"
                      :image-url="profile.user.avatar_url || profile.avatar_url"
                      :first-name="profile.user?.first_name || profile.first_name"
                      :last-name="profile.user?.last_name || profile.last_name"
                      :username="profile.user?.username || profile.username"
                      :email="profile.user?.email || profile.email"
                      size="xl"
                      shape="circle"
                      class="w-full h-full"
                    />
                    <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                      <div class="bg-white rounded-full p-2 shadow-lg">
                        <svg class="w-4 h-4 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </div>
                    </div>
                  </div>
                  <button
                    @click="showAvatarUpload = true"
                    class="absolute -bottom-1 -right-1 w-8 h-8 bg-primary-600 hover:bg-primary-700 text-white rounded-full flex items-center justify-center shadow-lg transition-all duration-200 hover:scale-110 border-2 border-white dark:border-gray-800"
                    title="Change profile picture"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- User Info - Compact -->
              <div class="flex-1 min-w-0 pt-1">
                <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-1.5 tracking-tight">
                  {{ fullName || profile.user?.username || profile.username || 'User' }}
                </h1>
                <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
                  <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span class="truncate">{{ profile.user?.email || profile.email }}</span>
                </div>
                
                <!-- Badges - Compact -->
                <div class="flex flex-wrap items-center gap-2">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    {{ roleLabel }}
                  </span>
                  <span v-if="profile.user?.is_active !== false" class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 gap-1.5">
                    <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                    Active
                  </span>
                  <span v-if="profile.user?.email_verified" class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 gap-1.5">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    Verified
                  </span>
                </div>
              </div>

              <!-- Quick Actions - Prominent -->
              <div class="flex-shrink-0 flex flex-col gap-2">
                <router-link
                  to="/profile/settings"
                  class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors duration-200 gap-2 shadow-sm hover:shadow"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Settings
                </router-link>
              </div>
            </div>

            <!-- Stats Cards - Compact Horizontal Layout -->
            <div v-if="stats.length > 0" class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div
                v-for="(stat, index) in stats"
                :key="stat.label"
                class="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
              >
                <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">{{ stat.label }}</p>
                <p class="text-xl font-bold text-gray-900 dark:text-white">
                  {{ stat.value }}
                </p>
                <div v-if="stat.change" class="mt-1">
                  <span :class="[
                    'text-xs font-medium',
                    stat.change > 0 
                      ? 'text-green-600 dark:text-green-400' 
                      : 'text-red-600 dark:text-red-400'
                  ]">
                    {{ stat.change > 0 ? '↑' : '↓' }} {{ Math.abs(stat.change) }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content - Single Column Layout -->
        <div class="space-y-4">
          <!-- Personal Information Card - Improved Layout -->
            <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <h2 class="text-base font-semibold text-gray-900 dark:text-white">Personal Information</h2>
                <button
                  @click="editingSection = editingSection === 'personal' ? null : 'personal'"
                  class="px-3 py-1.5 text-xs font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors duration-200 flex items-center gap-1.5"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  {{ editingSection === 'personal' ? 'Cancel' : 'Edit' }}
                </button>
              </div>
              <div class="p-5">
              <div v-if="editingSection !== 'personal'" class="space-y-4">
                <!-- Contact Information Group -->
                <div>
                  <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Contact</h3>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div class="space-y-1">
                      <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Email</label>
                      <p class="text-sm text-gray-900 dark:text-white flex items-center gap-2">
                        <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <span class="truncate">{{ profile.user?.email || profile.email || '—' }}</span>
                      </p>
                    </div>
                    <div class="space-y-1">
                      <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Phone</label>
                      <p class="text-sm text-gray-900 dark:text-white flex items-center gap-2">
                        <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                        {{ profile.user?.phone_number || profile.phone_number || '—' }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Location & Time Group -->
                <div>
                  <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Location & Time</h3>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div class="space-y-1">
                      <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Country</label>
                      <p class="text-sm text-gray-900 dark:text-white flex items-center gap-2">
                        <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {{ profile.user?.country || profile.country || '—' }}
                      </p>
                    </div>
                    <div class="space-y-1">
                      <label class="text-xs font-medium text-gray-500 dark:text-gray-400">State/Province</label>
                      <p class="text-sm text-gray-900 dark:text-white">{{ profile.user?.state || profile.state || '—' }}</p>
                    </div>
                    <div class="space-y-1">
                      <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Timezone</label>
                      <p class="text-sm text-gray-900 dark:text-white flex items-center gap-2">
                        <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {{ profile.user?.timezone || profile.timezone || '—' }}
                      </p>
                    </div>
                    <div class="space-y-1">
                      <label class="text-xs font-medium text-gray-500 dark:text-gray-400">Member Since</label>
                      <p class="text-sm text-gray-900 dark:text-white flex items-center gap-2">
                        <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        {{ formatDate(profile.user?.date_joined || profile.date_joined) }}
                      </p>
                    </div>
                  </div>
                </div>
                <!-- Bio Section -->
                <div v-if="profile.user?.bio || profile.bio" class="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">About</h3>
                  <div class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed prose prose-sm max-w-none">
                    <SafeHtml :content="profile.user?.bio || profile.bio" />
                  </div>
                </div>
              </div>

              <!-- Edit Form -->
              <form v-else @submit.prevent="savePersonalInfo" class="space-y-5">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">Phone Number</label>
                    <input
                      v-model="editForm.phone_number"
                      type="tel"
                      class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">Country</label>
                    <input
                      v-model="editForm.country"
                      type="text"
                      class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">State/Province</label>
                    <input
                      v-model="editForm.state"
                      type="text"
                      class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">Timezone</label>
                    <input
                      v-model="editForm.timezone"
                      type="text"
                      class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200"
                    />
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">Bio</label>
                  <RichTextEditor
                    v-model="editForm.bio"
                    :height="150"
                    toolbar="basic"
                    :max-length="500"
                    :show-char-count="true"
                  />
                </div>
                <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="submit"
                    :disabled="saving"
                    class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {{ saving ? 'Saving...' : 'Save Changes' }}
                  </button>
                  <button
                    type="button"
                    @click="editingSection = null"
                    class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors duration-200"
                  >
                    Cancel
                  </button>
                </div>
              </form>
              </div>
            </div>

            <!-- Role-Specific Information -->
            <div v-if="roleSpecificInfo" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                  <svg class="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h2 class="text-base font-semibold text-gray-900 dark:text-white">{{ roleSpecificInfo.title }}</h2>
              </div>
              <div class="p-5">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div v-for="(value, key) in roleSpecificInfo.data" :key="key" class="space-y-1">
                    <label class="text-xs font-medium text-gray-500 dark:text-gray-400">{{ formatLabel(key) }}</label>
                    <p class="text-sm text-gray-900 dark:text-white">{{ formatValue(value) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions Card - Moved Below Personal Info -->
            <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
              <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 class="text-base font-semibold text-gray-900 dark:text-white">Quick Actions</h2>
              </div>
              <div class="p-4">
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <router-link
                    to="/profile/settings"
                    class="flex flex-col items-start gap-2 p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-200 group border border-transparent hover:border-gray-200 dark:hover:border-gray-700"
                  >
                    <div class="w-10 h-10 rounded-lg bg-primary-50 dark:bg-primary-900/20 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <span class="text-sm font-medium text-gray-900 dark:text-white block">Account Settings</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">Manage your account</span>
                    </div>
                  </router-link>
                  <router-link
                    to="/profile/security"
                    class="flex flex-col items-start gap-2 p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-200 group border border-transparent hover:border-gray-200 dark:hover:border-gray-700"
                  >
                    <div class="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <span class="text-sm font-medium text-gray-900 dark:text-white block">Security Activity</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">View login history</span>
                    </div>
                  </router-link>
                  <router-link
                    to="/profile/privacy-security"
                    class="flex flex-col items-start gap-2 p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-200 group border border-transparent hover:border-gray-200 dark:hover:border-gray-700"
                  >
                    <div class="w-10 h-10 rounded-lg bg-purple-50 dark:bg-purple-900/20 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <span class="text-sm font-medium text-gray-900 dark:text-white block">Privacy & Security</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">Privacy settings</span>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    <!-- Modern Avatar Upload Modal -->
    <div 
      v-if="showAvatarUpload" 
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="handleCloseModal"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl max-w-lg w-full shadow-xl transform transition-all duration-300 overflow-hidden">
        <!-- Header -->
        <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Profile Picture</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Update your profile photo</p>
          </div>
          <button
            @click="handleCloseModal"
            class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-200"
          >
            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
    </div>

        <!-- Content -->
        <div class="p-6">
        <input
          ref="avatarInput"
          type="file"
          accept="image/*"
          @change="handleAvatarChange"
          class="hidden"
        />

          <!-- Drag and Drop Zone - Clean Modern Design -->
          <div
            v-if="!avatarPreview"
            class="relative border-2 border-dashed rounded-xl p-10 transition-all duration-200 cursor-pointer"
            :class="[
              isDragging 
                ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-900/10' 
                : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500',
              'bg-gray-50/50 dark:bg-gray-700/30'
            ]"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            @click="openFilePicker"
          >
            <div class="text-center space-y-4">
              <!-- Icon -->
              <div class="mx-auto w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center">
                <svg class="w-8 h-8 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              
              <!-- Text Content -->
              <div class="space-y-2">
                <p class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ isDragging ? 'Drop your image here' : 'Drag and drop an image here' }}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  or <button type="button" class="text-primary-600 dark:text-primary-400 font-medium hover:underline">browse</button> to choose a file
                </p>
                <p class="text-xs text-gray-400 dark:text-gray-500 pt-1">
                  PNG, JPG, GIF up to 5MB
                </p>
              </div>
              
              <!-- Upload Button -->
          <button
                type="button"
                @click.stop="openFilePicker"
                class="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow"
          >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Upload Picture
          </button>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-else class="space-y-5">
            <!-- Image Preview -->
            <div class="flex items-center justify-center">
              <div class="relative">
                <div class="w-40 h-40 rounded-full overflow-hidden border-2 border-gray-200 dark:border-gray-700 shadow-md">
                  <img 
                    :src="avatarPreview" 
                    alt="Preview" 
                    class="w-full h-full object-cover"
                  />
                </div>
                <!-- Remove Preview Button -->
            <button
                  @click="clearPreview"
                  class="absolute -top-1 -right-1 w-8 h-8 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center shadow-md transition-all duration-200 hover:scale-110 border-2 border-white dark:border-gray-800"
                  title="Remove preview"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
            </button>
          </div>
        </div>

            <!-- Upload Progress -->
            <div v-if="uploadingAvatar" class="space-y-3">
              <div class="flex items-center justify-center gap-3">
                <div class="relative w-6 h-6">
                  <div class="absolute inset-0 border-2 border-primary-200 dark:border-primary-800 rounded-full"></div>
                  <div class="absolute inset-0 border-2 border-transparent border-t-primary-600 dark:border-t-primary-400 rounded-full animate-spin"></div>
                </div>
                <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Uploading...</p>
              </div>
              <div class="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div class="h-full bg-primary-600 rounded-full animate-pulse" style="width: 60%"></div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div v-else class="flex gap-3">
        <button
                @click="uploadAvatar"
                :disabled="uploadingAvatar"
                class="flex-1 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-sm"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Save Photo
              </button>
              <button
                @click="openFilePicker"
                class="px-4 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Change
        </button>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, shallowRef } from 'vue'
import { useAuthStore } from '@/stores/auth'
import usersAPI from '@/api/users'
import { authApi } from '@/api/auth'
import Avatar from '@/components/common/Avatar.vue'
import SafeHtml from '@/components/common/SafeHtml.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import { useToast } from '@/composables/useToast'

const { success: showSuccess, error: showError } = useToast()

const authStore = useAuthStore()

const profile = shallowRef(null)
const loading = ref(true)
const error = ref(null)
const saving = ref(false)
const editingSection = ref(null)
const showAvatarUpload = ref(false)
const avatarPreview = ref(null)
const avatarFile = ref(null)
const uploadingAvatar = ref(false)
const isDragging = ref(false)
const avatarInput = ref(null)

const editForm = ref({
  phone_number: '',
  country: '',
  state: '',
  timezone: '',
  bio: ''
})

const fullName = computed(() => {
  if (!profile.value) return ''
  const user = profile.value.user || profile.value
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`
  }
  return user.first_name || user.last_name || user.username || ''
})

const roleLabel = computed(() => {
  if (!profile.value) return ''
  const role = profile.value.user?.role || profile.value.role || authStore.userRole
  return role.charAt(0).toUpperCase() + role.slice(1)
})

const stats = computed(() => {
  if (!profile.value) return []
  const role = profile.value.user?.role || profile.value.role || authStore.userRole
  const statsList = []

  // Simple icon component for stats
  const IconComponent = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>' }
  
  if (role === 'client') {
    statsList.push(
      { label: 'Total Orders', value: profile.value.total_orders || 0, icon: IconComponent },
      { label: 'Loyalty Points', value: profile.value.loyalty_points || 0, icon: IconComponent },
      { label: 'Total Spent', value: `$${(profile.value.total_spent || 0).toFixed(2)}`, icon: IconComponent }
    )
  } else if (role === 'writer') {
    statsList.push(
      { label: 'Completed Orders', value: profile.value.completed_orders || 0, icon: IconComponent },
      { label: 'Active Orders', value: profile.value.active_orders || 0, icon: IconComponent },
      { label: 'Rating', value: (profile.value.rating || 0).toFixed(1), icon: IconComponent },
      { label: 'Total Earnings', value: `$${(profile.value.total_earnings || 0).toFixed(2)}`, icon: IconComponent }
    )
  } else if (role === 'editor') {
    statsList.push(
      { label: 'Edited Orders', value: profile.value.edited_orders || 0, icon: IconComponent }
    )
  } else if (role === 'support') {
    statsList.push(
      { label: 'Handled Tickets', value: profile.value.handled_tickets || 0, icon: IconComponent },
      { label: 'Resolved Orders', value: profile.value.resolved_orders || 0, icon: IconComponent }
    )
  }

  return statsList
})

const roleSpecificInfo = computed(() => {
  if (!profile.value) return null
  const role = profile.value.user?.role || profile.value.role || authStore.userRole

  if (role === 'client') {
    return {
      title: 'Client Information',
      data: {
        registration_id: profile.value.registration_id,
        loyalty_points: profile.value.loyalty_points,
        subscription_status: profile.value.subscription_status
      }
    }
  } else if (role === 'writer') {
    return {
      title: 'Writer Information',
      data: {
        writer_level: profile.value.writer_level?.name || profile.value.writer_level,
        pen_name: profile.value.pen_name,
        verification_status: profile.value.verification_status ? 'Verified' : 'Not Verified',
        rating: (profile.value.rating || 0).toFixed(1)
      }
    }
  }

  return null
})

// Load profile function
const loadProfile = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await usersAPI.getProfile()
    profile.value = response.data
    
    // Populate edit form
    const user = profile.value.user || profile.value
    editForm.value = {
      phone_number: user.phone_number || profile.value.phone_number || '',
      country: user.country || profile.value.country || '',
      state: user.state || profile.value.state || '',
      timezone: user.timezone || profile.value.timezone || '',
      bio: user.bio || profile.value.bio || ''
    }
  } catch (err) {
    console.error('Failed to load profile:', err)
    error.value = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to load profile'
    // Set profile to null to ensure error state shows
    profile.value = null
  } finally {
    loading.value = false
  }
}

const constructAvatarUrl = (avatarUrl) => {
  if (!avatarUrl) return null
  
  // Ensure avatar URL is absolute if it's a relative path
  if (avatarUrl.startsWith('http') || avatarUrl.startsWith('//')) {
    return avatarUrl
  }
  
  // Construct full URL for relative paths (handle /media/ paths)
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_FULL_URL || 'http://localhost:8000'
  // Remove /api/v1 if present, and ensure we have the base URL
  const baseUrl = apiBaseUrl.replace('/api/v1', '').replace(/\/$/, '')
  // Handle both /media/... and media/... paths
  const cleanPath = avatarUrl.startsWith('/') ? avatarUrl : `/${avatarUrl}`
  return `${baseUrl}${cleanPath}`
}

const savePersonalInfo = async () => {
  saving.value = true
  try {
    await usersAPI.updateProfile(editForm.value)
    await loadProfile()
    editingSection.value = null
    showSuccess('Profile updated successfully!')
  } catch (err) {
    console.error('Failed to update profile:', err)
    showError(err.response?.data?.detail || err.message || 'Failed to update profile')
  } finally {
    saving.value = false
  }
}

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  processImageFile(file)
}

const handleDrop = (event) => {
  isDragging.value = false
  event.preventDefault()
  const file = event.dataTransfer.files[0]
  if (file) {
    processImageFile(file)
  }
}

const processImageFile = (file) => {
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    showError('Please select an image file')
    error.value = 'Please select an image file'
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    showError('Image size must be less than 5MB')
    error.value = 'Image size must be less than 5MB'
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  avatarFile.value = file
  error.value = null // Clear any previous errors
}

const clearPreview = () => {
  avatarPreview.value = null
  avatarFile.value = null
  if (avatarInput.value) {
    avatarInput.value.value = ''
  }
}

const openFilePicker = () => {
  if (avatarInput.value) {
    avatarInput.value.click()
  }
}

const handleCloseModal = () => {
  if (!uploadingAvatar.value) {
    showAvatarUpload.value = false
    // Clear preview if user closes without uploading
    if (avatarPreview.value && !uploadingAvatar.value) {
      clearPreview()
    }
  }
}

const uploadAvatar = async () => {
  if (!avatarFile.value) {
    showError('Please select an image first')
    return
  }
  
  uploadingAvatar.value = true
  error.value = null
  try {
    const formData = new FormData()
    formData.append('profile_picture', avatarFile.value)
    
    // Use users API endpoint which supports file uploads
    const response = await usersAPI.updateProfile(formData)
    
    // Update avatar URL from response if available
    if (response.data && response.data.avatar_url && profile.value) {
      const avatarUrl = constructAvatarUrl(response.data.avatar_url)
      profile.value.avatar_url = avatarUrl
      // Also update nested user object if it exists
      if (profile.value.user) {
        profile.value.user.avatar_url = avatarUrl
      }
    }
    
    await loadProfile()
    
    // Close modal and clear preview after successful upload
    showAvatarUpload.value = false
    clearPreview()
    
    // Show success toast
    showSuccess('Profile picture uploaded successfully!')
  } catch (err) {
    console.error('Failed to upload avatar:', err)
    const errorMessage = err.response?.data?.detail || err.response?.data?.error || err.message || 'Failed to upload avatar'
    showError(errorMessage)
    error.value = errorMessage
  } finally {
    uploadingAvatar.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const formatLabel = (key) => {
  return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const formatValue = (value) => {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  return value
}

onMounted(async () => {
  try {
    await loadProfile()
  } catch (err) {
    console.error('Error in onMounted:', err)
    // Ensure loading is set to false even on error
    loading.value = false
  }
})
</script>

<style scoped>
.unified-profile {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes patternMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(60px, 60px);
  }
}

/* Modal Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active > div,
.modal-fade-leave-active > div {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-fade-enter-from > div,
.modal-fade-leave-to > div {
  transform: scale(0.95) translateY(-20px);
  opacity: 0;
}

/* Smooth scrollbar */
.unified-profile::-webkit-scrollbar {
  width: 8px;
}

.unified-profile::-webkit-scrollbar-track {
  background: transparent;
}

.unified-profile::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.unified-profile::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* Dark mode scrollbar */
.dark .unified-profile::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}

.dark .unified-profile::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
