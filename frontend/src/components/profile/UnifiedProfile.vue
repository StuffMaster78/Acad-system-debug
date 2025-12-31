<template>
  <div class="unified-profile min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
    <!-- Background Pattern -->
    <div class="fixed inset-0 opacity-5 dark:opacity-10 pointer-events-none">
      <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, currentColor 1px, transparent 0); background-size: 40px 40px;"></div>
    </div>

    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
      <div v-else-if="profile" class="space-y-8">
        <!-- Hero Header Section -->
        <div class="relative overflow-hidden rounded-3xl shadow-2xl">
          <!-- Gradient Background -->
          <div class="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-purple-600 dark:from-primary-800 dark:via-primary-900 dark:to-purple-900"></div>
          
          <!-- Animated Background Pattern -->
          <div class="absolute inset-0 opacity-20">
            <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 60px 60px; animation: patternMove 20s linear infinite;"></div>
          </div>

          <!-- Content -->
          <div class="relative px-8 py-12 sm:px-12 sm:py-16">
            <div class="flex flex-col lg:flex-row items-start lg:items-center gap-8">
              <!-- Avatar Section -->
              <div class="relative group">
                <div class="relative">
                  <!-- Glow Effect -->
                  <div class="absolute inset-0 bg-white/30 rounded-full blur-2xl group-hover:blur-3xl transition-all duration-300"></div>
                  
                  <!-- Avatar Container -->
                  <div class="relative w-32 h-32 sm:w-40 sm:h-40 rounded-full bg-white/10 backdrop-blur-md border-4 border-white/30 shadow-2xl ring-4 ring-white/20">
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
                  </div>
                  
                  <!-- Edit Button -->
                  <button
                    @click="showAvatarUpload = true"
                    class="absolute -bottom-2 -right-2 w-12 h-12 bg-white hover:bg-gray-50 text-primary-600 rounded-full flex items-center justify-center shadow-xl ring-4 ring-primary-500/20 transition-all duration-200 hover:scale-110 hover:rotate-12"
                    title="Change avatar"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- User Info -->
              <div class="flex-1 text-white">
                <div class="mb-4">
                  <h1 class="text-4xl sm:text-5xl font-extrabold mb-3 tracking-tight drop-shadow-lg">
                    {{ fullName || profile.user?.username || profile.username || 'User' }}
                  </h1>
                  <div class="flex items-center gap-3 text-primary-100">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <p class="text-lg font-medium">{{ profile.user?.email || profile.email }}</p>
                  </div>
                </div>
                
                <!-- Badges -->
                <div class="flex flex-wrap items-center gap-3">
                  <span class="px-4 py-2 bg-white/20 backdrop-blur-md rounded-full text-sm font-semibold border border-white/30 shadow-lg">
                    {{ roleLabel }}
                  </span>
                  <span v-if="profile.user?.is_active !== false" class="px-4 py-2 bg-green-500/30 backdrop-blur-md rounded-full text-sm font-semibold border border-green-400/30 shadow-lg flex items-center gap-2">
                    <span class="w-2 h-2 bg-green-300 rounded-full animate-pulse"></span>
                    Active
                  </span>
                  <span v-if="profile.user?.email_verified" class="px-4 py-2 bg-blue-500/30 backdrop-blur-md rounded-full text-sm font-semibold border border-blue-400/30 shadow-lg flex items-center gap-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    Verified
                  </span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex flex-col sm:flex-row gap-3">
                <router-link
                  to="/account/settings"
                  class="px-6 py-3 bg-white/20 hover:bg-white/30 backdrop-blur-md text-white rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl border border-white/30 flex items-center justify-center gap-2 hover:scale-105"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Settings
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div v-if="stats.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="(stat, index) in stats"
            :key="stat.label"
            class="group relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 overflow-hidden"
            :style="{ animationDelay: `${index * 100}ms` }"
          >
            <!-- Gradient Overlay on Hover -->
            <div class="absolute inset-0 bg-gradient-to-br from-primary-500/0 to-purple-500/0 group-hover:from-primary-500/10 group-hover:to-purple-500/10 transition-all duration-300"></div>
            
            <!-- Content -->
            <div class="relative">
              <div class="flex items-center justify-between mb-4">
                <p class="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">{{ stat.label }}</p>
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/10 to-purple-500/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <component :is="stat.icon" class="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
              </div>
              <p class="text-3xl font-extrabold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-300">
                {{ stat.value }}
              </p>
              <div v-if="stat.change" class="flex items-center gap-2">
                <span :class="[
                  'text-xs font-semibold px-2 py-1 rounded-lg',
                  stat.change > 0 
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
                    : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                ]">
                  {{ stat.change > 0 ? '↑' : '↓' }} {{ Math.abs(stat.change) }}%
                </span>
                <span class="text-xs text-gray-500 dark:text-gray-400">vs last month</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Left Column - Profile Details -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Personal Information Card -->
            <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-8 hover:shadow-xl transition-all duration-300">
              <div class="flex items-center justify-between mb-8">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 flex items-center justify-center">
                    <svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Personal Information</h2>
                </div>
                <button
                  @click="editingSection = editingSection === 'personal' ? null : 'personal'"
                  class="px-4 py-2 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-semibold flex items-center gap-2 rounded-xl hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all duration-200"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  {{ editingSection === 'personal' ? 'Cancel' : 'Edit' }}
                </button>
              </div>

              <div v-if="editingSection !== 'personal'" class="space-y-6">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Email</label>
                    <p class="text-base font-medium text-gray-900 dark:text-white flex items-center gap-2">
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      {{ profile.user?.email || profile.email || '—' }}
                    </p>
                  </div>
                  <div class="space-y-2">
                    <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Phone</label>
                    <p class="text-base font-medium text-gray-900 dark:text-white flex items-center gap-2">
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      {{ profile.user?.phone_number || profile.phone_number || '—' }}
                    </p>
                  </div>
                  <div class="space-y-2">
                    <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Country</label>
                    <p class="text-base font-medium text-gray-900 dark:text-white flex items-center gap-2">
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ profile.user?.country || profile.country || '—' }}
                    </p>
                  </div>
                  <div class="space-y-2">
                    <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">State/Province</label>
                    <p class="text-base font-medium text-gray-900 dark:text-white">{{ profile.user?.state || profile.state || '—' }}</p>
                  </div>
                  <div class="space-y-2">
                    <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Timezone</label>
                    <p class="text-base font-medium text-gray-900 dark:text-white flex items-center gap-2">
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ profile.user?.timezone || profile.timezone || '—' }}
                    </p>
                  </div>
                  <div class="space-y-2">
                    <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Member Since</label>
                    <p class="text-base font-medium text-gray-900 dark:text-white flex items-center gap-2">
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {{ formatDate(profile.user?.date_joined || profile.date_joined) }}
                    </p>
                  </div>
                </div>
                <div v-if="profile.user?.bio || profile.bio" class="pt-6 border-t border-gray-200 dark:border-gray-700">
                  <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3 block">Bio</label>
                  <div class="text-gray-900 dark:text-white prose prose-sm max-w-none">
                    <SafeHtml :content="profile.user?.bio || profile.bio" />
                  </div>
                </div>
              </div>

              <!-- Edit Form -->
              <form v-else @submit.prevent="savePersonalInfo" class="space-y-6">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Phone Number</label>
                    <input
                      v-model="editForm.phone_number"
                      type="tel"
                      class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Country</label>
                    <input
                      v-model="editForm.country"
                      type="text"
                      class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">State/Province</label>
                    <input
                      v-model="editForm.state"
                      type="text"
                      class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Timezone</label>
                    <input
                      v-model="editForm.timezone"
                      type="text"
                      class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200"
                    />
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Bio</label>
                  <RichTextEditor
                    v-model="editForm.bio"
                    :height="150"
                    toolbar="basic"
                    :max-length="500"
                    :show-char-count="true"
                  />
                </div>
                <div class="flex gap-3 pt-4">
                  <button
                    type="submit"
                    :disabled="saving"
                    class="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                  >
                    {{ saving ? 'Saving...' : 'Save Changes' }}
                  </button>
                  <button
                    type="button"
                    @click="editingSection = null"
                    class="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>

            <!-- Role-Specific Information -->
            <div v-if="roleSpecificInfo" class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-8 hover:shadow-xl transition-all duration-300">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                  <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ roleSpecificInfo.title }}</h2>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div v-for="(value, key) in roleSpecificInfo.data" :key="key" class="space-y-2">
                  <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">{{ formatLabel(key) }}</label>
                  <p class="text-base font-semibold text-gray-900 dark:text-white">{{ formatValue(value) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column - Quick Actions & Info -->
          <div class="space-y-6">
            <!-- Quick Actions Card -->
            <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-xl transition-all duration-300">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center">
                  <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Quick Actions</h2>
              </div>
              <div class="space-y-2">
                <router-link
                  to="/account/settings"
                  class="flex items-center gap-4 p-4 rounded-xl hover:bg-gradient-to-r hover:from-primary-50 hover:to-purple-50 dark:hover:from-primary-900/20 dark:hover:to-purple-900/20 transition-all duration-200 group"
                >
                  <div class="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                    <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <span class="text-gray-700 dark:text-gray-300 font-medium group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-200">Account Settings</span>
                </router-link>
                <router-link
                  to="/account/security"
                  class="flex items-center gap-4 p-4 rounded-xl hover:bg-gradient-to-r hover:from-green-50 hover:to-emerald-50 dark:hover:from-green-900/20 dark:hover:to-emerald-900/20 transition-all duration-200 group"
                >
                  <div class="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                    <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <span class="text-gray-700 dark:text-gray-300 font-medium group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors duration-200">Security Activity</span>
                </router-link>
                <router-link
                  to="/account/privacy"
                  class="flex items-center gap-4 p-4 rounded-xl hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 dark:hover:from-purple-900/20 dark:hover:to-pink-900/20 transition-all duration-200 group"
                >
                  <div class="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                    <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <span class="text-gray-700 dark:text-gray-300 font-medium group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors duration-200">Privacy Settings</span>
                </router-link>
              </div>
            </div>

            <!-- Account Status Card -->
            <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-xl transition-all duration-300">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
                  <svg class="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Account Status</h2>
              </div>
              <div class="space-y-4">
                <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Status</span>
                  <span :class="[
                    'px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wide',
                    profile.user?.is_active !== false
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                  ]">
                    {{ profile.user?.is_active !== false ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <div v-if="profile.user?.email_verified" class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Email Verified</span>
                  <div class="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Avatar Upload Modal -->
    <div v-if="showAvatarUpload" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="showAvatarUpload = false">
      <div class="bg-white dark:bg-gray-800 rounded-3xl max-w-md w-full shadow-2xl p-8 transform transition-all duration-300">
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Change Profile Picture</h3>
        <input
          ref="avatarInput"
          type="file"
          accept="image/*"
          @change="handleAvatarChange"
          class="hidden"
        />
        <div class="space-y-6">
          <button
            @click="$refs.avatarInput?.click()"
            class="w-full px-6 py-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all duration-200 text-gray-600 dark:text-gray-400 font-medium"
          >
            Choose Image
          </button>
          <div v-if="avatarPreview" class="text-center space-y-4">
            <div class="relative inline-block">
              <img :src="avatarPreview" alt="Preview" class="w-32 h-32 rounded-full mx-auto mb-4 ring-4 ring-primary-200 dark:ring-primary-800" />
            </div>
            <button
              @click="uploadAvatar"
              :disabled="uploadingAvatar"
              class="px-8 py-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              {{ uploadingAvatar ? 'Uploading...' : 'Upload' }}
            </button>
          </div>
        </div>
        <button
          @click="showAvatarUpload = false"
          class="mt-6 w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200"
        >
          Cancel
        </button>
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
import { useDebounceFn } from '@vueuse/core'
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

// Debounced load profile
const loadProfile = useDebounceFn(async () => {
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
    error.value = err.response?.data?.detail || err.message || 'Failed to load profile'
  } finally {
    loading.value = false
  }
}, 200)

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
    
    showAvatarUpload.value = false
    avatarPreview.value = null
    avatarFile.value = null
    
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

onMounted(() => {
  loadProfile()
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
