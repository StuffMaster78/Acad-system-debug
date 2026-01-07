<template>
  <div class="account-settings">
    <!-- Header Section -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Account Settings</h1>
      <p class="text-gray-600 dark:text-gray-400">Manage your account preferences and security settings</p>
    </div>

    <!-- Profile Tab -->
    <div v-if="activeTab === 'profile'" class="tab-content space-y-6">
      <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-8 hover:shadow-xl transition-all duration-300">
        <div class="flex items-center gap-3 mb-8">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 flex items-center justify-center">
            <svg class="w-7 h-7 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
        </div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Profile Information</h2>
        </div>
        <div v-if="loadingProfile" class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="relative w-12 h-12 mx-auto mb-4">
              <div class="absolute inset-0 border-4 border-primary-200 dark:border-primary-800 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-transparent border-t-primary-600 dark:border-t-primary-400 rounded-full animate-spin"></div>
            </div>
            <p class="text-gray-600 dark:text-gray-400 font-medium">Loading profile...</p>
          </div>
        </div>
        <!-- Avatar upload is handled on the Profile overview page.
             This form now focuses only on core profile fields. -->
        <form v-else @submit.prevent="updateProfile" class="space-y-6">

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="form-group relative">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
                Email
                <span class="ml-2 text-xs font-normal normal-case text-gray-500 dark:text-gray-400">(read-only)</span>
              </label>
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
            <input
              v-model="profileForm.email"
              type="email"
              disabled
                  class="w-full pl-12 pr-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-xl border border-gray-300 dark:border-gray-600 cursor-not-allowed transition-all duration-200"
                />
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Email cannot be changed for security reasons
              </p>
          </div>

            <div class="form-group relative">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
                Username
                <span class="text-red-500 ml-1">*</span>
              </label>
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
            <input
              v-model="profileForm.username"
              type="text"
              :disabled="loading"
              required
                  class="w-full pl-12 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Enter your username"
            />
              </div>
          </div>

            <div class="form-group relative">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">First Name</label>
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              <input
                v-model="profileForm.first_name"
                type="text"
                :disabled="loading"
                  class="w-full pl-12 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Enter your first name"
              />
              </div>
            </div>

            <div class="form-group relative">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Last Name</label>
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              <input
                v-model="profileForm.last_name"
                type="text"
                :disabled="loading"
                  class="w-full pl-12 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Enter your last name"
              />
            </div>
          </div>

            <div class="form-group relative md:col-span-2">
              <label class="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
              Phone Number
              <Tooltip text="We use your phone number to coordinate order completion and send SMS notifications about important updates regarding your orders." />
            </label>
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </div>
            <input
              v-model="profileForm.phone_number"
              type="tel"
              :disabled="loading"
              placeholder="+1234567890"
                  class="w-full pl-12 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
            />
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">Bio</label>
            <RichTextEditor
              v-model="profileForm.bio"
              :disabled="loading"
              placeholder="Tell us about yourself..."
              :max-length="500"
              :show-char-count="true"
              toolbar="basic"
              height="150px"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="form-group relative">
              <label class="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
                Country
                <Tooltip text="Your country helps us provide localized services and comply with regional regulations." />
              </label>
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 z-10 text-gray-400 dark:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              <input
                v-model="profileForm.country"
                type="text"
                :disabled="loading"
                  @input="handleCountryInput"
                  @focus="showCountrySuggestions = true"
                  @blur="handleCountryBlur"
                  @keydown.down.prevent="navigateCountrySuggestions(1)"
                  @keydown.up.prevent="navigateCountrySuggestions(-1)"
                  @keydown.enter.prevent="selectCountryByIndex"
                  @keydown.escape="showCountrySuggestions = false"
                  placeholder="Start typing country name..."
                  class="w-full pl-12 pr-10 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                />
                <div v-if="countrySuggestions.length > 0 && showCountrySuggestions" 
                     class="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                  <button
                    v-for="(country, index) in countrySuggestions"
                    :key="index"
                    type="button"
                    @click="selectCountry(country.name)"
                    class="w-full text-left px-4 py-2 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors first:rounded-t-xl last:rounded-b-xl"
                    :class="{ 'bg-primary-50 dark:bg-primary-900/20': index === selectedCountryIndex }"
                  >
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-gray-900 dark:text-white">{{ country.name }}</span>
                      <span class="text-xs text-gray-500 dark:text-gray-400">({{ country.code }})</span>
                    </div>
                  </button>
                </div>
                <div v-if="profileForm.country && !countrySuggestions.length && showCountrySuggestions" 
                     class="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-lg p-4 text-sm text-gray-500 dark:text-gray-400">
                  No matching countries found. You can still enter your country name manually.
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Type to search countries or enter manually (e.g., "United States" or "US")
                </p>
              </div>
            </div>

            <div class="form-group relative">
              <label class="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
                State/Province
                <Tooltip text="Your state or province helps us provide more accurate regional support and services." />
              </label>
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
              <input
                v-model="profileForm.state"
                type="text"
                :disabled="loading"
                  placeholder="Enter your state or province"
                  class="w-full pl-12 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
              />
            </div>
          </div>

            <div class="form-group relative md:col-span-2">
              <label class="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
              Timezone
              <Tooltip text="We use your timezone to show deadlines, schedules, and notifications in your local time." />
            </label>
              <div class="relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
            <input
              v-model="profileForm.timezone"
              type="text"
              :disabled="loading"
              placeholder="e.g. America/New_York"
                  class="w-full pl-12 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                />
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Detected: 
                <button
                  v-if="detectedTimezone"
                  @click="useDetectedTimezone"
                  type="button"
                  class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-semibold underline decoration-2 underline-offset-2 hover:decoration-primary-500 dark:hover:decoration-primary-400 transition-colors cursor-pointer"
                  title="Click to use detected timezone"
                >
                  {{ detectedTimezone }}
                </button>
                <strong v-else class="text-gray-400 dark:text-gray-500">Unknown</strong>
              </p>
            </div>
          </div>

          <!-- Error Message with Animation -->
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 transform -translate-y-2 scale-95"
            enter-to-class="opacity-100 transform translate-y-0 scale-100"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 transform translate-y-0 scale-100"
            leave-to-class="opacity-0 transform -translate-y-2 scale-95"
          >
            <div v-if="error" class="p-4 bg-gradient-to-r from-red-50 to-red-100 dark:from-red-900/30 dark:to-red-800/30 border-l-4 border-red-500 rounded-xl text-red-700 dark:text-red-300 shadow-lg backdrop-blur-sm">
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center mt-0.5">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold mb-1">Error</p>
                  <p class="text-sm">{{ error }}</p>
                </div>
                <button
                  @click="error = null"
                  class="flex-shrink-0 text-red-500 hover:text-red-700 dark:hover:text-red-300 transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </Transition>

          <!-- Success Message with Animation -->
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 transform -translate-y-2 scale-95"
            enter-to-class="opacity-100 transform translate-y-0 scale-100"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 transform translate-y-0 scale-100"
            leave-to-class="opacity-0 transform -translate-y-2 scale-95"
          >
            <div v-if="success" class="p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30 border-l-4 border-green-500 rounded-xl text-green-700 dark:text-green-300 shadow-lg backdrop-blur-sm">
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mt-0.5 animate-pulse">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold mb-1">Success!</p>
                  <p class="text-sm">{{ success }}</p>
                </div>
                <button
                  @click="success = null"
                  class="flex-shrink-0 text-green-500 hover:text-green-700 dark:hover:text-green-300 transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </Transition>

          <div class="flex gap-4 pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            type="submit"
            :disabled="loading"
              class="relative px-8 py-3.5 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 active:scale-95 disabled:transform-none overflow-hidden group"
            >
              <span class="absolute inset-0 bg-white/20 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300"></span>
              <span v-if="loading" class="relative flex items-center gap-2">
                <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Saving Changes...
              </span>
              <span v-else class="relative flex items-center gap-2">
                <svg class="w-5 h-5 transform group-hover:scale-110 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Save Changes
              </span>
          </button>
            <button
              type="button"
              @click="loadProfile"
              :disabled="loading"
              class="px-6 py-3.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Security Tab -->
    <div v-if="activeTab === 'security'" class="tab-content space-y-6">
      <!-- Password Change -->
      <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-8 hover:shadow-xl transition-all duration-300">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center">
            <svg class="w-7 h-7 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </div>
          <div class="flex-1">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Change Password</h2>
            <p class="text-gray-600 dark:text-gray-400 mt-1">Update your password to keep your account secure.</p>
          </div>
        </div>
        <router-link to="/account/password-change" class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
          Change Password
        </router-link>
      </div>

      <!-- 2FA -->
      <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-8 hover:shadow-xl transition-all duration-300">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center">
            <svg class="w-7 h-7 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div class="flex-1">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Two-Factor Authentication</h2>
          </div>
        </div>
        <div v-if="!twoFAEnabled" class="space-y-4">
          <p class="text-gray-600 dark:text-gray-400">
            Add an extra layer of security to your account by enabling two-factor authentication.
          </p>
          <button @click="show2FASetup = true" class="px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Enable 2FA
          </button>
        </div>
        <div v-else class="space-y-4">
          <div class="inline-flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-xl font-semibold">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            2FA Enabled
          </div>
          <p class="text-gray-600 dark:text-gray-400">Two-factor authentication is enabled for your account.</p>
          <button @click="disable2FA" class="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200">
            Disable 2FA
          </button>
        </div>
      </div>

      <!-- Active Sessions -->
      <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-8 hover:shadow-xl transition-all duration-300">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
            <svg class="w-7 h-7 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
        </div>
          <div class="flex-1">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Active Sessions</h2>
            <p class="text-gray-600 dark:text-gray-400 mt-1">Manage your active login sessions.</p>
          </div>
        </div>
        <div v-if="loadingSessions" class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="relative w-12 h-12 mx-auto mb-4">
              <div class="absolute inset-0 border-4 border-primary-200 dark:border-primary-800 rounded-full"></div>
              <div class="absolute inset-0 border-4 border-transparent border-t-primary-600 dark:border-t-primary-400 rounded-full animate-spin"></div>
            </div>
            <p class="text-gray-600 dark:text-gray-400 font-medium">Loading sessions...</p>
          </div>
        </div>
        <div v-else-if="sessions.length === 0" class="text-center py-12">
          <p class="text-gray-500 dark:text-gray-400">No active sessions</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="session in sessions"
            :key="session.id"
            class="p-6 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all duration-200"
            :class="{ 'ring-2 ring-primary-500/30': session.is_current }"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <strong class="text-gray-900 dark:text-white font-semibold">{{ session.device_name || 'Unknown Device' }}</strong>
                  <span v-if="session.is_current" class="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-full text-xs font-bold">Current</span>
              </div>
                <div class="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <p class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    IP: {{ session.ip_address }}
                  </p>
                  <p class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Last active: {{ formatDate(session.last_activity) }}
                  </p>
              </div>
            </div>
            <button
              v-if="!session.is_current"
              @click="revokeSession(session.id)"
                class="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-xl font-semibold hover:bg-red-200 dark:hover:bg-red-900/50 transition-all duration-200"
            >
              Revoke
            </button>
          </div>
        </div>
        </div>
        <button v-if="sessions.length > 1" @click="revokeAllSessions" class="mt-6 w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200">
          Logout All Devices
        </button>
      </div>

      <!-- Account Deletion (Only for clients, writers, support, editors) -->
      <div v-if="canRequestDeletion" class="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 backdrop-blur-xl rounded-2xl shadow-lg border-2 border-red-200 dark:border-red-800 p-8 hover:shadow-xl transition-all duration-300">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500/20 to-pink-500/20 flex items-center justify-center">
            <svg class="w-7 h-7 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>
          <div class="flex-1">
            <h2 class="text-2xl font-bold text-red-900 dark:text-red-200">Delete Account</h2>
            <p class="text-red-700 dark:text-red-300 mt-1">
          Once you delete your account, there is no going back. Please be certain.
        </p>
          </div>
        </div>
        <div v-if="deletionRequested" class="space-y-4">
          <div class="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-xl font-semibold">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Deletion Requested
          </div>
          <p class="text-red-700 dark:text-red-300">
            Your account deletion request is pending. Your account will be deleted in 3 months.
          </p>
        </div>
        <div v-else>
          <button @click="showDeletionModal = true" class="px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
            Request Account Deletion
          </button>
        </div>
      </div>
    </div>

    <!-- Sessions Tab -->
    <div v-if="activeTab === 'sessions'" class="tab-content">
      <SessionManagement />
    </div>

    <!-- Update Requests Tab -->
    <div v-if="activeTab === 'update-requests'" class="tab-content">
      <ProfileUpdateRequests />
    </div>
  </div>

    <!-- Account Deletion Modal -->
    <div v-if="showDeletionModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click="showDeletionModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-3xl max-w-lg w-full shadow-2xl p-8 transform transition-all duration-300" @click.stop>
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500/20 to-pink-500/20 flex items-center justify-center">
            <svg class="w-7 h-7 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Request Account Deletion</h2>
        </div>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Are you sure you want to delete your account? This action cannot be undone.
          Your account will be frozen immediately and permanently deleted after 3 months.
        </p>
        <div class="form-group mb-6">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Reason for deletion (optional)</label>
          <textarea
            v-model="deletionReason"
            rows="4"
            placeholder="Please let us know why you're leaving..."
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200"
          ></textarea>
        </div>
        <div v-if="deletionError" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 mb-6">
          {{ deletionError }}
        </div>
        <div class="flex gap-4">
          <button @click="confirmDeletion" :disabled="deleting" class="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none">
            <span v-if="deleting" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
            <span v-else>Yes, Delete My Account</span>
          </button>
          <button @click="showDeletionModal = false" :disabled="deleting" class="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200 disabled:opacity-50">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- 2FA Setup Modal -->
    <div v-if="show2FASetup" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click="show2FASetup = false">
      <div class="bg-white dark:bg-gray-800 rounded-3xl max-w-lg w-full shadow-2xl p-8 transform transition-all duration-300" @click.stop>
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center">
            <svg class="w-7 h-7 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Setup Two-Factor Authentication</h2>
          </div>
        <div v-if="!twoFASecret" class="space-y-6">
          <p class="text-gray-600 dark:text-gray-400">Scan this QR code with your authenticator app:</p>
          <div class="flex justify-center p-6 bg-gray-50 dark:bg-gray-700/50 rounded-2xl">
            <img :src="twoFAQrCode" alt="2FA QR Code" class="max-w-full h-auto rounded-xl" />
          </div>
          <div>
            <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Backup Codes (save these):</p>
            <div class="grid grid-cols-2 gap-3">
              <code v-for="code in twoFABackupCodes" :key="code" class="px-4 py-3 bg-gray-100 dark:bg-gray-700 rounded-xl text-center font-mono text-sm font-semibold text-gray-900 dark:text-white">{{ code }}</code>
            </div>
          </div>
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Enter the 6-digit code from your app to verify:</p>
          <input
            v-model="twoFACode"
            type="text"
            maxlength="6"
            pattern="[0-9]{6}"
            placeholder="000000"
              class="w-full px-4 py-4 text-center text-2xl font-mono tracking-widest border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200"
          />
          </div>
          <div class="flex gap-4 pt-4">
            <button @click="verify2FASetup" class="flex-1 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
              Verify & Enable
            </button>
            <button @click="show2FASetup = false" class="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import { Transition } from 'vue'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import usersAPI from '@/api/users'
import SessionManagement from '@/components/settings/SessionManagement.vue'
import ProfileUpdateRequests from '@/components/profile/ProfileUpdateRequests.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import Tooltip from '@/components/common/Tooltip.vue'
import Avatar from '@/components/common/Avatar.vue'
import { useToast } from '@/composables/useToast'

export default {
  name: 'AccountSettings',
  components: {
    Transition,
    SessionManagement,
    ProfileUpdateRequests,
    RichTextEditor,
    Tooltip,
    Avatar
  },
  setup() {
    const authStore = useAuthStore()
    const { success: showSuccess, error: showError } = useToast()
    return { authStore, showSuccess, showError }
  },
  data() {
    return {
      activeTab: 'profile',
      isDragging: false,
      uploadingAvatar: false,
      tabs: [
        { id: 'profile', label: 'Profile' },
        { id: 'security', label: 'Security' },
        { id: 'update-requests', label: 'Update Requests' }
      ],
      loading: false,
      loadingProfile: false,
      loadingSessions: false,
      error: null,
      success: null,
      profileData: {},
      profileForm: {
        email: '',
        username: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        bio: '',
        country: '',
        state: '',
        avatar: '',
        timezone: ''
      },
      detectedTimezone: null,
      twoFAEnabled: false,
      show2FASetup: false,
      twoFASecret: null,
      twoFAQrCode: null,
      twoFABackupCodes: [],
      twoFACode: '',
      sessions: [],
      showDeletionModal: false,
      deletionReason: '',
      deletionRequested: false,
      deleting: false,
      deletionError: null,
      avatarPreview: null,
      avatarFile: null,
      removeAvatarOnSave: false,
      countrySuggestions: [],
      showCountrySuggestions: false,
      selectedCountryIndex: -1,
      allCountries: []
    }
  },
  computed: {
    fullName() {
      if (this.profileForm.first_name && this.profileForm.last_name) {
        return `${this.profileForm.first_name} ${this.profileForm.last_name}`
      }
      return this.profileForm.first_name || this.profileForm.last_name || this.profileForm.username || ''
    },
    canRequestDeletion() {
      // Only clients, writers, support, and editors can request deletion
      const userRole = this.authStore.userRole
      return ['client', 'writer', 'support', 'editor'].includes(userRole)
    }
  },
  mounted() {
    this.loadProfile()
    this.loadSessions()
    this.check2FAStatus()
    this.checkDeletionStatus()
    this.loadCountries()
  },
  methods: {
    loadCountries() {
      // Load a comprehensive list of countries
      // Using a common list of countries with their ISO codes
      this.allCountries = [
        { name: 'United States', code: 'US' },
        { name: 'United Kingdom', code: 'GB' },
        { name: 'Canada', code: 'CA' },
        { name: 'Australia', code: 'AU' },
        { name: 'Germany', code: 'DE' },
        { name: 'France', code: 'FR' },
        { name: 'Italy', code: 'IT' },
        { name: 'Spain', code: 'ES' },
        { name: 'Netherlands', code: 'NL' },
        { name: 'Belgium', code: 'BE' },
        { name: 'Switzerland', code: 'CH' },
        { name: 'Austria', code: 'AT' },
        { name: 'Sweden', code: 'SE' },
        { name: 'Norway', code: 'NO' },
        { name: 'Denmark', code: 'DK' },
        { name: 'Finland', code: 'FI' },
        { name: 'Poland', code: 'PL' },
        { name: 'Ireland', code: 'IE' },
        { name: 'Portugal', code: 'PT' },
        { name: 'Greece', code: 'GR' },
        { name: 'Czech Republic', code: 'CZ' },
        { name: 'Hungary', code: 'HU' },
        { name: 'Romania', code: 'RO' },
        { name: 'Bulgaria', code: 'BG' },
        { name: 'Croatia', code: 'HR' },
        { name: 'New Zealand', code: 'NZ' },
        { name: 'South Africa', code: 'ZA' },
        { name: 'India', code: 'IN' },
        { name: 'China', code: 'CN' },
        { name: 'Japan', code: 'JP' },
        { name: 'South Korea', code: 'KR' },
        { name: 'Singapore', code: 'SG' },
        { name: 'Malaysia', code: 'MY' },
        { name: 'Thailand', code: 'TH' },
        { name: 'Philippines', code: 'PH' },
        { name: 'Indonesia', code: 'ID' },
        { name: 'Vietnam', code: 'VN' },
        { name: 'Brazil', code: 'BR' },
        { name: 'Mexico', code: 'MX' },
        { name: 'Argentina', code: 'AR' },
        { name: 'Chile', code: 'CL' },
        { name: 'Colombia', code: 'CO' },
        { name: 'Peru', code: 'PE' },
        { name: 'Egypt', code: 'EG' },
        { name: 'Nigeria', code: 'NG' },
        { name: 'Kenya', code: 'KE' },
        { name: 'Ghana', code: 'GH' },
        { name: 'Israel', code: 'IL' },
        { name: 'Turkey', code: 'TR' },
        { name: 'Saudi Arabia', code: 'SA' },
        { name: 'United Arab Emirates', code: 'AE' },
        { name: 'Qatar', code: 'QA' },
        { name: 'Kuwait', code: 'KW' },
        { name: 'Russia', code: 'RU' },
        { name: 'Ukraine', code: 'UA' },
        { name: 'Belarus', code: 'BY' },
        { name: 'Kazakhstan', code: 'KZ' }
      ]
    },
    handleCountryInput(event) {
      const query = event.target.value.toLowerCase().trim()
      this.showCountrySuggestions = true
      this.selectedCountryIndex = -1
      
      if (!query) {
        this.countrySuggestions = []
        return
      }
      
      // Filter countries by name or code
      this.countrySuggestions = this.allCountries.filter(country => 
        country.name.toLowerCase().includes(query) || 
        country.code.toLowerCase() === query
      ).slice(0, 10) // Limit to 10 suggestions
    },
    selectCountry(countryName) {
      this.profileForm.country = countryName
      this.countrySuggestions = []
      this.showCountrySuggestions = false
      this.selectedCountryIndex = -1
    },
    handleCountryBlur() {
      // Delay hiding suggestions to allow click events
      setTimeout(() => {
        this.showCountrySuggestions = false
        this.selectedCountryIndex = -1
      }, 200)
    },
    navigateCountrySuggestions(direction) {
      if (this.countrySuggestions.length === 0) return
      
      this.selectedCountryIndex += direction
      
      if (this.selectedCountryIndex < 0) {
        this.selectedCountryIndex = this.countrySuggestions.length - 1
      } else if (this.selectedCountryIndex >= this.countrySuggestions.length) {
        this.selectedCountryIndex = 0
      }
    },
    selectCountryByIndex() {
      if (this.selectedCountryIndex >= 0 && this.selectedCountryIndex < this.countrySuggestions.length) {
        this.selectCountry(this.countrySuggestions[this.selectedCountryIndex].name)
      } else if (this.countrySuggestions.length > 0) {
        // Select first suggestion if none is selected
        this.selectCountry(this.countrySuggestions[0].name)
      }
    },
    getCountryNameFromCode(code) {
      if (!code || code.length !== 2) return null
      const country = this.allCountries.find(c => c.code.toUpperCase() === code.toUpperCase())
      return country ? country.name : null
    },
    handleTabClick(tab) {
      if (tab.route) {
        // Navigate to separate page for Privacy and Security Activity
        this.$router.push(tab.route)
      } else {
        // Regular tab switch
        this.activeTab = tab.id
      }
    },
    useDetectedTimezone() {
      if (this.detectedTimezone) {
        this.profileForm.timezone = this.detectedTimezone
        // Show a brief success message
        this.showSuccess('Timezone set to detected value')
      }
    },
    
    async loadProfile() {
      this.loadingProfile = true
      this.error = null
      try {
        const response = await authApi.getCurrentUser()
        const data = response.data
        
        // Store full profile data for display
        this.profileData = data
        
        // Handle nested structure (for Client/Writer/Editor/Support profiles)
        // or flat structure (for Admin/Superadmin profiles)
        const userData = data.user || data
        
        // Populate form with available data
        const countryCode = userData.country || data.country || ''
        const countryName = this.getCountryNameFromCode(countryCode) || countryCode
        
        this.profileForm = {
          email: userData.email || data.email || '',
          username: userData.username || data.username || '',
          first_name: userData.first_name || data.first_name || '',
          last_name: userData.last_name || data.last_name || '',
          phone_number: userData.phone_number || data.phone_number || '',
          bio: userData.bio || data.bio || '',
          country: countryName,
          state: userData.state || data.state || '',
          avatar: userData.avatar || data.avatar || '',
          timezone: userData.timezone || data.timezone || ''
        }

        // Try to infer detected timezone from existing sources
        this.detectedTimezone =
          data.timezone ||
          userData.timezone ||
          localStorage.getItem('timezone') ||
          null
        
        // If still no timezone detected, try to get it from the browser
        if (!this.detectedTimezone) {
          try {
            const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
            if (browserTimezone) {
              this.detectedTimezone = browserTimezone
            }
          } catch (e) {
            console.warn('Could not detect browser timezone:', e)
          }
        }
        
        // Update profileData with avatar_url if available
        // Check multiple possible locations for avatar URL
        let avatarUrl = userData.avatar_url || 
                       data.avatar_url || 
                       userData.profile_picture || 
                       data.profile_picture ||
                       (userData.user && (userData.user.avatar_url || userData.user.profile_picture)) ||
                       (data.user && (data.user.avatar_url || data.user.profile_picture)) ||
                       (userData.user_main_profile && (userData.user_main_profile.avatar_url || userData.user_main_profile.profile_picture))
        
        // Also check nested user_main_profile structure
        if (!avatarUrl && userData.user_main_profile) {
          avatarUrl = userData.user_main_profile.avatar_url || userData.user_main_profile.profile_picture
        }
        
        if (avatarUrl) {
          this.profileData.avatar_url = this.constructAvatarUrl(avatarUrl)
        } else {
          // Clear avatar_url if not found (user removed it)
          this.profileData.avatar_url = null
        }
      } catch (err) {
        console.error('Failed to load profile:', err)
        this.error = err.response?.data?.error || 
                    err.response?.data?.detail || 
                    'Failed to load profile. Please try again.'
      } finally {
        this.loadingProfile = false
      }
    },
    
    isValidAvatarUrl(url) {
      if (!url) return false
      
      // Check if it's a data URL (base64 image)
      if (url.startsWith('data:image/')) {
        return true
      }
      
      // Check if it has image file extension
      const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
      const lowerUrl = url.toLowerCase()
      const hasImageExtension = imageExtensions.some(ext => lowerUrl.includes(ext))
      
      // Also check for common image path patterns
      const imagePathPatterns = ['/media/profile_pictures/', '/media/avatars/', '/static/images/', 'profile_picture', 'avatar']
      const hasImagePath = imagePathPatterns.some(pattern => lowerUrl.includes(pattern))
      
      return hasImageExtension || hasImagePath
    },

    constructAvatarUrl(avatarUrl) {
      if (!avatarUrl) return null
      
      // Validate it's actually an image URL before constructing
      if (!this.isValidAvatarUrl(avatarUrl)) {
        console.warn('Invalid avatar URL (not an image):', avatarUrl)
        return null
      }
      
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
    },

    handleAvatarUpload(event) {
      const file = event.target?.files?.[0] || event.dataTransfer?.files?.[0]
      if (!file) return
      this.processAvatarFile(file)
    },

    handleDrop(event) {
      event.preventDefault()
      this.isDragging = false
      const file = event.dataTransfer?.files?.[0]
      if (file) {
        this.processAvatarFile(file)
      }
    },

    processAvatarFile(file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        this.showError('Please select an image file')
        this.error = 'Please select an image file'
        return
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.showError('Image size must be less than 5MB')
        this.error = 'Image size must be less than 5MB'
        return
      }
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        this.avatarPreview = e.target.result
        this.error = null
      }
      reader.onerror = () => {
        this.showError('Failed to read image file')
        this.error = 'Failed to read image file'
      }
      reader.readAsDataURL(file)
      
      this.avatarFile = file
    },
    
    removeAvatar() {
      this.avatarPreview = null
      this.avatarFile = null
      // Set a flag to remove the avatar on save
      this.removeAvatarOnSave = true
    },
    
    async saveAvatarOnly() {
      // Save just the avatar without updating other profile fields
      if (!this.avatarFile) {
        this.showError('Please select an image first')
        this.error = 'Please select an image first'
        return
      }
      
      this.loading = true
      this.uploadingAvatar = true
      this.error = null
      this.success = null
      
      try {
        const formData = new FormData()
        formData.append('profile_picture', this.avatarFile)
        
        console.log('Uploading avatar file:', {
          name: this.avatarFile.name,
          size: this.avatarFile.size,
          type: this.avatarFile.type
        })
        
        // Use users API endpoint which supports file uploads
        const response = await usersAPI.updateProfile(formData)
        
        console.log('Avatar upload response:', response.data)
        
        // Extract avatar_url from response - check multiple possible locations
        let avatarUrl = null
        if (response && response.data) {
          // Check direct avatar_url
          avatarUrl = response.data.avatar_url || 
                     // Check nested user.avatar_url
                     (response.data.user && response.data.user.avatar_url) ||
                     // Check nested user.user_main_profile
                     (response.data.user && response.data.user.user_main_profile && response.data.user.user_main_profile.avatar_url) ||
                     // Check user.profile_picture
                     (response.data.user && response.data.user.profile_picture) ||
                     // Check user.user_main_profile.profile_picture
                     (response.data.user && response.data.user.user_main_profile && response.data.user.user_main_profile.profile_picture)
        }
        
        console.log('Extracted avatar URL:', avatarUrl)
        
        // If we got an avatar URL from response, update immediately
        if (avatarUrl) {
          const constructedUrl = this.constructAvatarUrl(avatarUrl)
          console.log('Constructed avatar URL:', constructedUrl)
          this.profileData.avatar_url = constructedUrl
          // Also update nested structure if it exists
          if (this.profileData.user) {
            this.profileData.user.avatar_url = constructedUrl
          }
        }
        
        // Always reload profile to get the updated avatar URL (this ensures cache is cleared)
        // Use a small delay to ensure backend has processed the file
        await new Promise(resolve => setTimeout(resolve, 200))
        await this.loadProfile()
        
        // Clear the file and preview after successful upload
        this.avatarFile = null
        this.avatarPreview = null
        
        // Show success toast
        this.showSuccess('Profile picture saved successfully!')
        this.success = 'Profile picture saved successfully!'
      } catch (error) {
        console.error('Avatar upload error:', error)
        console.error('Error response:', error.response)
        const errorMessage = error.response?.data?.error || 
                    error.response?.data?.detail || 
                    error.response?.data?.message ||
                    error.message ||
                    'Failed to save profile picture. Please try again.'
        this.showError(errorMessage)
        this.error = errorMessage
      } finally {
        this.loading = false
        this.uploadingAvatar = false
      }
    },

    async updateProfile() {
      this.loading = true
      this.error = null
      this.success = null

      try {
        // If avatar file is selected, upload it first
        if (this.avatarFile) {
          const formData = new FormData()
          formData.append('profile_picture', this.avatarFile)
          
          // Upload avatar separately - use users API which supports file uploads
          try {
            const avatarResponse = await usersAPI.updateProfile(formData)
            
            // Update avatar URL from response if available
            if (avatarResponse.data && avatarResponse.data.avatar_url) {
              this.profileData.avatar_url = this.constructAvatarUrl(avatarResponse.data.avatar_url)
            }
            
            // Reload profile immediately after upload to get the updated avatar URL
            await this.loadProfile()
            
            // Show success toast
            this.showSuccess('Profile picture uploaded successfully!')
          } catch (avatarError) {
            console.error('Avatar upload error:', avatarError)
            const errorMessage = avatarError.response?.data?.error || 
                        avatarError.response?.data?.detail || 
                        'Failed to upload profile picture. Please try again.'
            this.showError(errorMessage)
            this.error = errorMessage
            this.loading = false
            return
          }
          
          // Clear the file after successful upload
          this.avatarFile = null
          this.avatarPreview = null
        }
        
        // Handle avatar removal
        if (this.removeAvatarOnSave) {
          const formData = new FormData()
          formData.append('remove_picture', 'true')
          try {
            await usersAPI.updateProfile(formData)
            // Reload profile after removal to clear avatar
            await this.loadProfile()
            this.showSuccess('Profile picture removed successfully!')
          } catch (removeError) {
            console.error('Avatar removal error:', removeError)
            const errorMessage = removeError.response?.data?.error || 
                                removeError.response?.data?.detail || 
                                'Failed to remove profile picture. Please try again.'
            this.showError(errorMessage)
          }
          this.removeAvatarOnSave = false
        }
        
        // Prepare update data - only include fields that have values or are being cleared
        const updateData = {}
        
        if (this.profileForm.username) updateData.username = this.profileForm.username
        if (this.profileForm.first_name !== undefined) updateData.first_name = this.profileForm.first_name
        if (this.profileForm.last_name !== undefined) updateData.last_name = this.profileForm.last_name
        if (this.profileForm.phone_number !== undefined) updateData.phone_number = this.profileForm.phone_number || null
        if (this.profileForm.bio !== undefined) updateData.bio = this.profileForm.bio || null
        if (this.profileForm.country !== undefined) updateData.country = this.profileForm.country || null
        if (this.profileForm.state !== undefined) updateData.state = this.profileForm.state || null
        if (this.profileForm.timezone !== undefined) updateData.timezone = this.profileForm.timezone || null
        if (this.profileForm.avatar) updateData.avatar = this.profileForm.avatar
        
        // Only update other fields if avatar was not just uploaded
        if (!this.avatarFile && !this.removeAvatarOnSave && Object.keys(updateData).length > 0) {
          // Use users API profile update endpoint (supports PATCH and mirrors overview behavior)
          const response = await usersAPI.updateProfile(updateData)
        
          // Check if response includes updated user data
          if (response.data) {
            this.profileData = response.data.user || response.data
          }
          
          this.success = response.data?.message || 'Profile updated successfully!'
        } else if (this.avatarFile || this.removeAvatarOnSave) {
          // If only avatar was updated, show success message
          this.success = this.success || 'Profile updated successfully!'
        }
        
        // Reload profile to get latest data from database
        // This ensures avatar_url is properly loaded after any updates
        await this.loadProfile()
        
        // Force a small delay to ensure backend has processed the image
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Reload one more time to ensure we get the latest avatar URL
        await this.loadProfile()
        
        // Clear success message after 5 seconds
        setTimeout(() => {
          this.success = null
        }, 5000)
      } catch (err) {
        console.error('Profile update error:', err)
        // Extract error message from various possible locations
        const errorMessage = err.response?.data?.error || 
                            err.response?.data?.detail || 
                            err.response?.data?.message ||
                            err.message ||
                            (typeof err === 'string' ? err : 'Failed to update profile. Please try again.')
        this.error = errorMessage || 'Failed to update profile. Please try again.'
      } finally {
        this.loading = false
      }
    },

    async loadSessions() {
      this.loadingSessions = true
      try {
        const response = await authApi.getActiveSessions()
        // Handle different response structures
        let sessionsData = response.data
        if (sessionsData && !Array.isArray(sessionsData)) {
          sessionsData = sessionsData.results || sessionsData.sessions || sessionsData.data || []
        }
        this.sessions = Array.isArray(sessionsData) ? sessionsData : []
      } catch (err) {
        console.error('Failed to load sessions:', err)
        this.sessions = []
      } finally {
        this.loadingSessions = false
      }
    },

    async revokeSession(sessionId) {
      try {
        // Implement session revocation endpoint call
        await this.loadSessions()
      } catch (err) {
        console.error('Failed to revoke session:', err)
      }
    },

    async revokeAllSessions() {
      if (!confirm('Are you sure you want to logout from all devices?')) {
        return
      }

      try {
        await authApi.logout(true)
        // Redirect to login
        this.$router.push('/login')
      } catch (err) {
        console.error('Failed to logout all devices:', err)
      }
    },

    async check2FAStatus() {
      // Check if 2FA is enabled (implement based on your API)
      // this.twoFAEnabled = ...
    },

    async setup2FA() {
      try {
        const response = await authApi.setup2FA()
        this.twoFASecret = response.data.secret
        this.twoFAQrCode = response.data.qr_code
        this.twoFABackupCodes = response.data.backup_codes || []
      } catch (err) {
        this.error = 'Failed to setup 2FA'
        console.error('2FA setup error:', err)
      }
    },

    async verify2FASetup() {
      try {
        await authApi.verify2FA(this.twoFACode)
        this.twoFAEnabled = true
        this.show2FASetup = false
        this.success = '2FA enabled successfully!'
      } catch (err) {
        this.error = 'Invalid code. Please try again.'
      }
    },

    async disable2FA() {
      if (!confirm('Are you sure you want to disable 2FA?')) {
        return
      }

      try {
        // Implement disable 2FA endpoint call
        this.twoFAEnabled = false
        this.success = '2FA disabled successfully!'
      } catch (err) {
        this.error = 'Failed to disable 2FA'
      }
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    async checkDeletionStatus() {
      // Check if user has a pending deletion request
      if (this.profileData && this.profileData.is_frozen) {
        this.deletionRequested = true
      }
    },

    async confirmDeletion() {
      if (!confirm('Are you absolutely sure? This action cannot be undone.')) {
        return
      }

      this.deleting = true
      this.deletionError = null

      try {
        const response = await usersAPI.requestAccountDeletion(this.deletionReason || 'No reason provided')
        this.success = response.data?.message || 'Account deletion requested successfully.'
        this.deletionRequested = true
        this.showDeletionModal = false
        this.deletionReason = ''
        
        // Reload profile to get updated status
        await this.loadProfile()
      } catch (err) {
        console.error('Deletion request error:', err)
        this.deletionError = err.response?.data?.error || 
                            err.response?.data?.detail || 
                            'Failed to request account deletion. Please try again.'
      } finally {
        this.deleting = false
      }
    }
  },
  watch: {
    show2FASetup(newVal) {
      if (newVal && !this.twoFASecret) {
        this.setup2FA()
      }
    }
  }
}
</script>

<style scoped>
.account-settings {
  animation: fadeIn 0.3s ease-in;
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

/* Smooth scrollbar */
.account-settings::-webkit-scrollbar {
  width: 8px;
}

.account-settings::-webkit-scrollbar-track {
  background: transparent;
}

.account-settings::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.account-settings::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* Dark mode scrollbar */
.dark .account-settings::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
}

.dark .account-settings::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Form group spacing */
.form-group {
  margin-bottom: 0;
}

/* Ensure proper spacing in grid */
.tab-content.space-y-6 > * + * {
  margin-top: 1.5rem;
}

/* Smooth transitions for all interactive elements */
button, a, input, textarea, select {
  transition: all 0.2s ease-in-out;
}

/* Enhanced input focus states */
input:focus,
textarea:focus,
select:focus {
  outline: none;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

/* Input hover states */
input:hover:not(:disabled):not(:focus),
textarea:hover:not(:disabled):not(:focus) {
  border-color: rgba(99, 102, 241, 0.5);
}

/* Loading spinner animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Pulse animation for status indicators */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Pattern animation for background */
@keyframes patternMove {
  from {
    background-position: 0 0;
  }
  to {
    background-position: 60px 60px;
  }
}

/* Enhanced card hover effects */
.bg-white\/80:hover,
.dark .bg-gray-800\/80:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Icon animations */
svg {
  transition: transform 0.2s ease-in-out;
}

button:hover svg,
a:hover svg {
  transform: scale(1.1);
}

/* Smooth tab transitions */
.tab-content {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .account-settings {
    padding: 1rem;
  }
  
  input, textarea, select {
    font-size: 16px; /* Prevents zoom on iOS */
  }
  
  button {
    min-height: 44px; /* Better touch target */
  }
}

/* Accessibility improvements */
button:focus-visible,
a:focus-visible,
input:focus-visible {
  outline: 2px solid rgb(99, 102, 241);
  outline-offset: 2px;
}

/* Disabled state improvements */
input:disabled,
textarea:disabled,
select:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>

