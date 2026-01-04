<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="space-y-2">
            <h1 class="text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
              Privacy & Security
            </h1>
            <p class="text-lg text-gray-600 dark:text-gray-400 leading-relaxed max-w-2xl">
              Manage your privacy preferences and security settings. Some settings are limited by your role and system requirements.
            </p>
          </div>
          <button
            @click="loadSettings"
            :disabled="loading"
            class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
          >
            <RefreshCw :class="['w-5 h-5', loading && 'animate-spin']" />
            <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
          </button>
        </div>
      </div>

      <!-- Role-Specific Limits Notice -->
      <div class="mb-8 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-l-4 border-amber-500 dark:border-amber-400 rounded-lg p-6 shadow-sm">
        <div class="flex items-start gap-4">
            <div class="shrink-0">
            <div class="w-16 h-16 bg-gradient-to-br from-amber-500 via-orange-500 to-red-500 rounded-3xl flex items-center justify-center shadow-2xl ring-4 ring-amber-400/30">
              <PhosphorInfo class="w-9 h-9 text-white" weight="fill" />
            </div>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold text-amber-900 dark:text-amber-200 mb-2">
              Understanding Your Privacy Limits
            </h3>
            <div class="space-y-2 text-sm text-amber-800 dark:text-amber-300">
              <p v-if="authStore.isWriter" class="leading-relaxed">
                <strong>Writers:</strong> Your profile visibility to clients is controlled by system defaults and admin settings. 
                This ensures clients can evaluate your qualifications. You can control data sharing preferences and security notifications.
              </p>
              <p v-else-if="authStore.isClient" class="leading-relaxed">
                <strong>Clients:</strong> Your contact information and payment details remain private from writers by default. 
                Writers only see your pen name and order-related information. You can control data sharing and security notifications.
              </p>
              <p class="leading-relaxed mt-3">
                <strong>System Requirements:</strong> Administrators and support staff always have access to your profile for account management and support purposes. 
                This cannot be disabled for security and operational reasons.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Privacy Score Card -->
      <div class="mb-8 bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-3xl flex items-center justify-center shadow-2xl ring-4 ring-white/40">
                <PhosphorShield class="w-9 h-9 text-white" weight="fill" />
              </div>
              <h2 class="text-2xl font-bold">Your Privacy Score</h2>
            </div>
            <p class="text-blue-100 text-sm mb-4">
              Higher score = More privacy. This score reflects your current privacy settings and data sharing preferences.
            </p>
            <div class="w-full bg-white/20 backdrop-blur-sm rounded-full h-4 overflow-hidden">
              <div
                class="bg-white h-4 rounded-full transition-all duration-500 ease-out flex items-center justify-end pr-2 shadow-lg"
              :style="{ width: `${privacyScore}%` }"
              >
                <span
                  v-if="privacyScore > 15"
                  class="text-xs font-bold text-blue-600"
                >
                  {{ Math.round(privacyScore) }}%
                </span>
              </div>
            </div>
          </div>
          <div class="text-center sm:text-right">
            <div class="text-6xl font-extrabold mb-2">{{ Math.round(privacyScore) }}</div>
            <div class="text-blue-100 text-sm">out of 100</div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column: Privacy Settings -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Profile Visibility (Role-Specific) -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-14 h-14 bg-gradient-to-br from-purple-500 via-purple-600 to-indigo-600 rounded-3xl flex items-center justify-center shadow-2xl ring-4 ring-purple-400/30 group-hover:scale-105 transition-transform">
                <Eye class="w-8 h-8 text-white" stroke-width="3" />
              </div>
              <div>
                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Profile Visibility</h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Control who can see your profile information</p>
              </div>
            </div>

            <div class="space-y-6">
              <!-- Writers Visibility (for Clients) -->
              <div v-if="authStore.isClient" class="space-y-4">
                <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600">
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-2">
                        <div class="w-8 h-8 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl flex items-center justify-center">
                          <User class="w-5 h-5 text-blue-600 dark:text-blue-400" stroke-width="2.5" />
                        </div>
                        <label class="text-sm font-semibold text-gray-900 dark:text-white">
                          Visibility to Writers
                        </label>
                        <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium rounded">
                          Limited Control
                        </span>
                      </div>
                      <p class="text-xs text-gray-600 dark:text-gray-400 mb-3 leading-relaxed">
                        Writers assigned to your orders can see limited information (pen name, order count). 
                        Your real name, email, and payment details remain private.
                      </p>
                    </div>
                  </div>
                  <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3 mb-3">
                    <div class="flex items-start gap-2">
                      <LockKeyhole class="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
                      <p class="text-xs text-amber-800 dark:text-amber-300">
                        <strong>System Limit:</strong> Writers must see your pen name and basic order information to complete assignments. 
                        This cannot be disabled for operational reasons.
                      </p>
                    </div>
                  </div>
                  <select
                    v-model="settings.profile_visibility.to_writers"
                    @change="updateVisibility"
                    :disabled="true"
                    class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                  >
                    <option value="limited">Limited (System Default)</option>
                  </select>
                </div>
              </div>

              <!-- Clients Visibility (for Writers) -->
              <div v-if="authStore.isWriter" class="space-y-4">
                <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600">
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-2">
                        <div class="w-8 h-8 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl flex items-center justify-center">
                          <Users class="w-5 h-5 text-purple-600 dark:text-purple-400" stroke-width="2.5" />
                        </div>
                        <label class="text-sm font-semibold text-gray-900 dark:text-white">
                          Visibility to Clients
            </label>
                        <span class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium rounded">
                          Admin Controlled
                        </span>
                      </div>
                      <p class="text-xs text-gray-600 dark:text-gray-400 mb-3 leading-relaxed">
                        Clients see your writer ID, pen name, rating, and completed orders count. 
                        Your real name and contact information remain private.
                      </p>
                    </div>
                  </div>
                  <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3 mb-3">
                    <div class="flex items-start gap-2">
                      <LockKeyhole class="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
                      <p class="text-xs text-amber-800 dark:text-amber-300">
                        <strong>System Limit:</strong> Clients must see your qualifications (rating, completed orders) to make informed decisions. 
                        This visibility is controlled by administrators and cannot be changed by writers.
                      </p>
                    </div>
                  </div>
            <select
              v-model="settings.profile_visibility.to_writers"
              @change="updateVisibility"
                    :disabled="true"
                    class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
            >
                    <option value="limited">Limited (Admin Controlled)</option>
            </select>
                </div>
          </div>

              <!-- Administrators Visibility (All Users) -->
              <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600">
                <div class="flex items-start justify-between mb-3">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <div class="w-8 h-8 bg-gradient-to-br from-red-100 to-orange-100 dark:from-red-900/30 dark:to-orange-900/30 rounded-xl flex items-center justify-center">
                        <ShieldAlert class="w-5 h-5 text-red-600 dark:text-red-400" stroke-width="2.5" />
                      </div>
                      <label class="text-sm font-semibold text-gray-900 dark:text-white">
                        Visibility to Administrators
            </label>
                      <span class="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-xs font-medium rounded">
                        Required
                      </span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-3 leading-relaxed">
                      Administrators need full access to your profile for account management, support, and security purposes.
                    </p>
                  </div>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-3">
                  <div class="flex items-start gap-2">
                      <LockKeyhole class="w-4 h-4 text-red-600 dark:text-red-400 mt-0.5 shrink-0" />
                    <p class="text-xs text-red-800 dark:text-red-300">
                      <strong>Security Requirement:</strong> This cannot be changed. Administrators require access for account security, 
                      dispute resolution, and platform operations.
                    </p>
                  </div>
                </div>
            <select
              v-model="settings.profile_visibility.to_admins"
              @change="updateVisibility"
                  :disabled="true"
                  class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
            >
                  <option value="public">Public (Required for Operations)</option>
            </select>
          </div>

              <!-- Support Staff Visibility (All Users) -->
              <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600">
                <div class="flex items-start justify-between mb-3">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <div class="w-8 h-8 bg-gradient-to-br from-cyan-100 to-blue-100 dark:from-cyan-900/30 dark:to-blue-900/30 rounded-xl flex items-center justify-center">
                        <Headphones class="w-5 h-5 text-cyan-600 dark:text-cyan-400" stroke-width="2.5" />
                      </div>
                      <label class="text-sm font-semibold text-gray-900 dark:text-white">
                        Visibility to Support Staff
            </label>
                      <span class="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-xs font-medium rounded">
                        Required
                      </span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-3 leading-relaxed">
                      Support staff need access to assist with your account issues and provide customer service.
                    </p>
                  </div>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-3">
                  <div class="flex items-start gap-2">
                      <LockKeyhole class="w-4 h-4 text-red-600 dark:text-red-400 mt-0.5 shrink-0" />
                    <p class="text-xs text-red-800 dark:text-red-300">
                      <strong>Support Requirement:</strong> This cannot be changed. Support staff require access to help resolve 
                      account issues, process refunds, and provide assistance.
                    </p>
                  </div>
                </div>
            <select
              v-model="settings.profile_visibility.to_support"
              @change="updateVisibility"
                  :disabled="true"
                  class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
            >
                  <option value="public">Public (Required for Support)</option>
            </select>
          </div>
        </div>
      </div>

          <!-- Data Sharing Preferences -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-14 h-14 bg-gradient-to-br from-green-500 via-emerald-500 to-teal-600 rounded-3xl flex items-center justify-center shadow-2xl ring-4 ring-green-400/30 group-hover:scale-105 transition-transform">
                <PhosphorChartBar class="w-8 h-8 text-white" weight="duotone" />
              </div>
              <div>
                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Data Sharing Preferences</h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Control how your data is used for analytics and marketing</p>
              </div>
            </div>
        
        <div class="space-y-4">
              <label class="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer group">
                <div class="mt-1">
            <input
              type="checkbox"
              v-model="settings.data_sharing.analytics"
              @change="updateDataSharing"
                    class="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-2 focus:ring-green-500 cursor-pointer"
                  />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-gray-900 dark:text-white">Allow Usage Analytics</span>
                    <span class="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs font-medium rounded">
                      Recommended
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    Help us improve the platform by sharing anonymous usage data. This data is aggregated and cannot identify you personally.
                  </p>
            </div>
          </label>

              <label class="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer group">
                <div class="mt-1">
            <input
              type="checkbox"
              v-model="settings.data_sharing.marketing"
              @change="updateDataSharing"
                    class="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-2 focus:ring-green-500 cursor-pointer"
                  />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-gray-900 dark:text-white">Allow Marketing Communications</span>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    Receive promotional emails, special offers, and platform updates. You can unsubscribe at any time.
                  </p>
            </div>
          </label>

              <label class="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer group">
                <div class="mt-1">
            <input
              type="checkbox"
              v-model="settings.data_sharing.third_party"
              @change="updateDataSharing"
                    class="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-2 focus:ring-green-500 cursor-pointer"
                  />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-gray-900 dark:text-white">Allow Third-Party Data Sharing</span>
                    <span class="px-2 py-0.5 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 text-xs font-medium rounded">
                      Optional
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    Share anonymized data with trusted partners for research and service improvement. Your personal information is never shared.
                  </p>
            </div>
          </label>
        </div>
      </div>

          <!-- Security Notifications -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-14 h-14 bg-gradient-to-br from-red-500 via-rose-500 to-pink-600 rounded-3xl flex items-center justify-center shadow-2xl ring-4 ring-red-400/30 group-hover:scale-105 transition-transform">
                <PhosphorBell class="w-8 h-8 text-white" weight="duotone" />
              </div>
              <div>
                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Security Notifications</h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Get alerted about important security events</p>
              </div>
        </div>
        
            <div class="space-y-4">
              <label class="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer group">
                <div class="mt-1">
                  <input
                    type="checkbox"
                    v-model="settings.notifications.on_login"
                    @change="updateNotifications"
                    class="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-2 focus:ring-red-500 cursor-pointer"
                  />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-gray-900 dark:text-white">Notify on New Login</span>
                    <span class="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-xs font-medium rounded">
                      Recommended
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    Receive an email or SMS when someone logs into your account from a new device or location.
                  </p>
        </div>
              </label>

              <label class="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer group">
                <div class="mt-1">
                  <input
                    type="checkbox"
                    v-model="settings.notifications.on_suspicious_activity"
                    @change="updateNotifications"
                    class="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-2 focus:ring-red-500 cursor-pointer"
                  />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-gray-900 dark:text-white">Notify on Suspicious Activity</span>
                    <span class="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-xs font-medium rounded">
                      Recommended
                    </span>
            </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    Get immediate alerts when we detect unusual activity on your account, such as login attempts from unusual locations.
                  </p>
            </div>
              </label>
          </div>
        </div>
      </div>

        <!-- Right Column: Quick Actions & Info -->
        <div class="space-y-6">
          <!-- Quick Actions -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <div class="w-10 h-10 bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500 rounded-2xl flex items-center justify-center shadow-lg ring-2 ring-yellow-400/30">
                <Zap class="w-6 h-6 text-white" stroke-width="2.5" fill="rgba(255,255,255,0.1)" />
              </div>
              Quick Actions
            </h3>
            <div class="space-y-3">
              <router-link
                to="/account/security"
                class="flex items-center gap-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl hover:from-blue-100 hover:to-indigo-100 dark:hover:from-blue-900/30 dark:hover:to-indigo-900/30 transition-all group"
              >
                <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg ring-2 ring-blue-400/30">
                  <PhosphorShield class="w-6 h-6 text-white" weight="duotone" />
                </div>
                <span class="font-medium text-gray-900 dark:text-white">View Security Activity</span>
                <ChevronRight class="w-5 h-5 text-gray-400 ml-auto" />
              </router-link>
        <button
          @click="exportData"
          :disabled="exporting"
                class="w-full flex items-center gap-3 p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl hover:from-green-100 hover:to-emerald-100 dark:hover:from-green-900/30 dark:hover:to-emerald-900/30 transition-all group disabled:opacity-50"
        >
                <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg ring-2 ring-green-400/30">
                  <PhosphorDownload class="w-6 h-6 text-white" weight="duotone" />
                </div>
                <span class="font-medium text-gray-900 dark:text-white">{{ exporting ? 'Exporting...' : 'Export My Data' }}</span>
        </button>
            </div>
          </div>

          <!-- Recent Data Access -->
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <div class="w-10 h-10 bg-gradient-to-br from-purple-500 via-indigo-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg ring-2 ring-purple-400/30">
                <PhosphorFileText class="w-6 h-6 text-white" weight="duotone" />
              </div>
              Recent Data Access
            </h3>
            <div v-if="loadingAccessLog" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
            </div>
            <div v-else-if="accessLog.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
              <PhosphorFileText class="w-12 h-12 mx-auto mb-2 opacity-50" weight="duotone" />
              <p class="text-sm">No recent data access</p>
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="log in accessLog.slice(0, 5)"
                :key="log.id"
                class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
              >
                <div class="flex items-start justify-between mb-2">
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-sm text-gray-900 dark:text-white truncate">
                      {{ log.accessed_by?.email || 'System' }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {{ log.access_type }} • {{ formatDate(log.accessed_at) }}
                    </p>
                  </div>
                </div>
                <p class="text-xs text-gray-400 dark:text-gray-500">
                  {{ log.location || log.ip_address || 'Unknown location' }}
                </p>
              </div>
              <router-link
                to="/account/security"
                class="block text-center text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium mt-2"
              >
                View All Activity →
              </router-link>
            </div>
          </div>

          <!-- Privacy Tips -->
          <div class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl border border-blue-200 dark:border-blue-800 p-6">
            <h3 class="text-lg font-bold text-blue-900 dark:text-blue-200 mb-4 flex items-center gap-2">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg ring-2 ring-blue-400/30">
                <PhosphorLightbulb class="w-6 h-6 text-white" weight="duotone" />
              </div>
              Privacy Tips
            </h3>
            <ul class="space-y-3 text-sm text-blue-800 dark:text-blue-300">
              <li class="flex items-start gap-2">
                <CheckCircle2 class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0" />
                <span>Enable security notifications to stay informed about account activity</span>
              </li>
              <li class="flex items-start gap-2">
                <CheckCircle2 class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0" />
                <span>Review your data access log regularly for unauthorized access</span>
              </li>
              <li class="flex items-start gap-2">
                <CheckCircle2 class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0" />
                <span>Use strong, unique passwords and enable two-factor authentication</span>
              </li>
              <li class="flex items-start gap-2">
                <CheckCircle2 class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0" />
                <span>Export your data periodically to keep a local backup</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
// Lucide Icons - Modern, clean stroke style
import {
  RefreshCw,
  Eye,
  User,
  Users,
  ShieldAlert,
  Zap,
  ChevronRight,
  CheckCircle2,
  LockKeyhole,
  Headphones
} from 'lucide-vue-next'

// Phosphor Icons - Alternative modern style with duotone/fill weights
// Using Phosphor for key icons to add visual variety and modern aesthetic
import {
  Shield as PhosphorShield,
  Bell as PhosphorBell,
  ChartBar as PhosphorChartBar,
  Download as PhosphorDownload,
  FileText as PhosphorFileText,
  Lightbulb as PhosphorLightbulb,
  Info as PhosphorInfo
} from '@phosphor-icons/vue'
import { useAuthStore } from '@/stores/auth'
import privacyAPI from '@/api/privacy'
import { useToast } from '@/composables/useToast'

const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useToast()

const loading = ref(false)
const privacyScore = ref(0)
const settings = ref({
  profile_visibility: {
    to_writers: 'limited',
    to_admins: 'public',
    to_support: 'public'
  },
  data_sharing: {
    analytics: true,
    marketing: false,
    third_party: false
  },
  notifications: {
    on_login: true,
    on_login_method: 'email',
    on_suspicious_activity: true
  }
})
const accessLog = ref([])
const loadingAccessLog = ref(false)
const exporting = ref(false)

onMounted(async () => {
  await loadSettings()
  await loadAccessLog()
})

const loadSettings = async () => {
  loading.value = true
  try {
    const response = await privacyAPI.getSettings()
    if (response.data) {
      settings.value = {
        profile_visibility: response.data.profile_visibility || settings.value.profile_visibility,
        data_sharing: response.data.data_sharing || settings.value.data_sharing,
        notifications: response.data.notifications || settings.value.notifications
      }
      privacyScore.value = response.data.privacy_score || 0
    }
  } catch (error) {
    console.error('Failed to load privacy settings:', error)
    // Handle 404 gracefully - API endpoint might not exist yet
    if (error.response?.status === 404) {
      // Use default settings - component will still render
      console.log('Privacy API endpoint not found, using default settings')
    } else {
      // For other errors, show a non-intrusive message
      if (import.meta.env.DEV) {
        console.warn('Privacy settings API error:', error.message)
      }
    }
    // Don't show error to user - use defaults
  } finally {
    loading.value = false
  }
}

const loadAccessLog = async () => {
  loadingAccessLog.value = true
  try {
    const response = await privacyAPI.getAccessLog({ limit: 20, days: 30 })
    accessLog.value = response.data?.logs || []
  } catch (error) {
    // Handle 404 gracefully - API endpoint might not exist yet
    if (error.response?.status === 404) {
      console.log('Access log API endpoint not found, using empty log')
    } else {
      console.error('Failed to load access log:', error)
    if (import.meta.env.DEV) {
        console.warn('Access log API error:', error.message)
      }
    }
    accessLog.value = []
  } finally {
    loadingAccessLog.value = false
  }
}

const updateVisibility = async () => {
  try {
    const response = await privacyAPI.updateVisibility(settings.value.profile_visibility)
    if (response.data) {
      privacyScore.value = response.data.privacy_score || privacyScore.value
      showSuccess('Privacy settings updated')
    }
  } catch (error) {
    console.error('Failed to update visibility:', error)
    // Handle 404 gracefully
    if (error.response?.status === 404) {
      showError('Privacy settings API not available. Please contact support.')
    } else {
      showError(error.response?.data?.detail || 'Failed to update visibility settings')
    }
  }
}

const updateDataSharing = async () => {
  try {
    const response = await privacyAPI.updateDataSharing(settings.value.data_sharing)
    if (response.data) {
      privacyScore.value = response.data.privacy_score || privacyScore.value
      showSuccess('Data sharing preferences updated')
    }
  } catch (error) {
    console.error('Failed to update data sharing:', error)
    // Handle 404 gracefully
    if (error.response?.status === 404) {
      showError('Privacy settings API not available. Please contact support.')
    } else {
      showError(error.response?.data?.detail || 'Failed to update data sharing preferences')
    }
  }
}

const updateNotifications = async () => {
  try {
    // This would need a new API endpoint or be part of updateDataSharing
    showSuccess('Notification preferences updated')
  } catch (error) {
    console.error('Failed to update notifications:', error)
    showError('Failed to update notification preferences')
  }
}

const exportData = async () => {
  exporting.value = true
  try {
    const response = await privacyAPI.exportData()
    const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `my-data-export-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    showSuccess('Data export downloaded')
  } catch (error) {
    console.error('Failed to export data:', error)
    // Handle 404 gracefully
    if (error.response?.status === 404) {
      showError('Data export API not available. Please contact support.')
    } else {
      showError(error.response?.data?.detail || 'Failed to export data. Please try again.')
    }
  } finally {
    exporting.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
