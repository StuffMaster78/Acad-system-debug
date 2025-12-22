<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
    <h1 class="text-3xl font-bold text-gray-900">Referrals</h1>
        <p class="mt-2 text-gray-600">Share your referral link and earn rewards</p>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-4 rounded-xl" :class="messageSuccess ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-yellow-50 text-yellow-800 border border-yellow-200'">
      <div class="flex items-center gap-2">
        <svg v-if="messageSuccess" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <span>{{ message }}</span>
      </div>
    </div>
    <div v-if="error" class="p-4 rounded-xl bg-red-50 text-red-800 border border-red-200">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <span>{{ error }}</span>
      </div>
    </div>

    <!-- Not a client message -->
    <div v-if="notClientMessage" class="p-6 rounded-2xl bg-yellow-50 border border-yellow-200">
      <div class="flex items-start gap-4">
        <div class="shrink-0 w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
          <svg class="w-6 h-6 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div>
          <h3 class="font-semibold text-yellow-900 mb-1">Access Restricted</h3>
          <p class="text-sm text-yellow-800">{{ notClientMessage }}</p>
        </div>
      </div>
    </div>

    <!-- Only show referral content for clients -->
    <template v-if="isClient">
      <!-- Stats Cards - Flup Style -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 hover:shadow-lg transition-all duration-300">
        <div class="flex items-center justify-between">
          <div>
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Total Referred</p>
              <p class="text-3xl font-bold text-gray-900 tracking-tight">{{ codeStats?.total_referrals || stats.total_referred || 0 }}</p>
              <p class="mt-1 text-xs text-gray-500">People who signed up</p>
            </div>
            <div class="p-3 bg-blue-100 rounded-xl">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 hover:shadow-lg transition-all duration-300">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Successful</p>
              <p class="text-3xl font-bold text-green-600 tracking-tight">{{ codeStats?.successful_referrals || 0 }}</p>
              <p class="mt-1 text-xs text-gray-500">Bonuses awarded</p>
            </div>
            <div class="p-3 bg-green-100 rounded-xl">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 hover:shadow-lg transition-all duration-300">
        <div class="flex items-center justify-between">
          <div>
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Conversion Rate</p>
              <p class="text-3xl font-bold text-purple-600 tracking-tight">{{ codeStats?.conversion_rate || 0 }}%</p>
              <p class="mt-1 text-xs text-gray-500">Success rate</p>
            </div>
            <div class="p-3 bg-purple-100 rounded-xl">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 hover:shadow-lg transition-all duration-300">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Orders Placed</p>
              <p class="text-3xl font-bold text-gray-900 tracking-tight">{{ codeStats?.orders_placed || stats.completed_orders || 0 }}</p>
              <p class="mt-1 text-xs text-gray-500">By your referrals</p>
            </div>
            <div class="p-3 bg-orange-100 rounded-xl">
              <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Referral Section -->
      <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-bold text-gray-900 tracking-tight">Your Referral Code & Link</h2>
            <p class="mt-1 text-sm text-gray-600">Share your unique code or link to earn rewards</p>
          </div>
          <button
            v-if="!stats.referral_code && !generating && !loading"
            @click="generateCode"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
          >
            Generate Code
          </button>
    </div>

        <div v-if="stats.referral_code" class="space-y-6">
          <!-- Referral Code -->
        <div>
            <label class="block text-sm font-semibold text-gray-700 mb-3">Referral Code</label>
          <div class="flex items-center gap-3">
              <div class="flex-1 bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl px-6 py-4">
                <div class="text-2xl font-bold text-primary-600 font-mono text-center">{{ stats.referral_code }}</div>
              </div>
            <button
              @click="copyToClipboard(stats.referral_code)"
                class="px-5 py-4 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-all duration-200 flex items-center gap-2 font-medium shadow-sm hover:shadow-md"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy Code
            </button>
          </div>
        </div>

          <!-- Referral Link -->
        <div v-if="stats.referral_link">
            <label class="block text-sm font-semibold text-gray-700 mb-3">Referral Link</label>
          <div class="flex items-center gap-3">
            <input
              :value="stats.referral_link"
              readonly
                class="flex-1 border-2 border-gray-200 rounded-xl px-4 py-3 bg-gray-50 font-mono text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
            />
            <button
              @click="copyToClipboard(stats.referral_link)"
                class="px-5 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-all duration-200 flex items-center gap-2 font-medium shadow-sm hover:shadow-md"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy Link
            </button>
          </div>
        </div>

          <!-- Quick Share Buttons -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-3">Share Via</label>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button
                @click="shareEmail"
                class="px-4 py-3 border-2 border-gray-200 rounded-xl hover:border-primary-300 hover:bg-primary-50 transition-all duration-200 flex items-center justify-center gap-2 font-medium"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Email
              </button>
              <button
                @click="shareWhatsApp"
                class="px-4 py-3 border-2 border-gray-200 rounded-xl hover:border-green-300 hover:bg-green-50 transition-all duration-200 flex items-center justify-center gap-2 font-medium"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                </svg>
                WhatsApp
              </button>
              <button
                @click="shareFacebook"
                class="px-4 py-3 border-2 border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 flex items-center justify-center gap-2 font-medium"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Facebook
              </button>
              <button
                @click="shareTwitter"
                class="px-4 py-3 border-2 border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 flex items-center justify-center gap-2 font-medium"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
                Twitter
              </button>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <div class="max-w-md mx-auto">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
      </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">No Referral Code Yet</h3>
            <p class="text-gray-600 mb-6">Generate your unique referral code to start earning rewards</p>
        <button
              v-if="!generating && !loading"
          @click="generateCode"
          :disabled="generating || loading"
              class="px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors font-medium shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
              {{ generating ? 'Generating...' : 'Generate Referral Code' }}
        </button>
          </div>
        </div>
      </div>

      <!-- Refer Someone by Email -->
      <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
        <div class="flex items-center gap-3 mb-6">
          <div class="p-2 bg-primary-100 rounded-lg">
            <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
    </div>
        <div>
            <h2 class="text-xl font-bold text-gray-900 tracking-tight">Refer Someone by Email</h2>
            <p class="text-sm text-gray-600">Send an invitation to someone who doesn't have an account yet</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
            <input
              v-model="referralEmail"
              type="email"
              placeholder="friend@example.com"
            class="flex-1 border-2 border-gray-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
              :disabled="referring"
              @keyup.enter="submitReferral"
            />
            <button
              @click="submitReferral"
              :disabled="referring || !referralEmail"
            class="px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-all duration-200 font-medium shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg v-if="referring" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ referring ? 'Sending...' : 'Send Invitation' }}</span>
            </button>
        </div>
      </div>

      <!-- Referrals List - Card Layout -->
      <div class="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-bold text-gray-900 tracking-tight">Your Referrals</h2>
            <p class="text-sm text-gray-600 mt-1">{{ referrals.length }} {{ referrals.length === 1 ? 'referral' : 'referrals' }}</p>
    </div>
          <button 
            @click="loadReferrals" 
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-2 border-primary-200 border-t-primary-600"></div>
      </div>

      <div v-else-if="!referrals.length" class="text-center py-12">
          <div class="max-w-md mx-auto">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">No Referrals Yet</h3>
            <p class="text-gray-600">Share your referral link to get started!</p>
          </div>
      </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="ref in referrals"
            :key="ref.id"
            class="border-2 border-gray-200 rounded-xl p-5 hover:border-primary-300 hover:shadow-md transition-all duration-200"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center shrink-0">
                    <span class="text-primary-600 font-semibold text-sm">
                      {{ (ref.referee?.email || ref.referee?.username || 'N/A')[0].toUpperCase() }}
                    </span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-semibold text-gray-900 truncate">{{ ref.referee?.email || ref.referee?.username || 'N/A' }}</p>
                    <p class="text-xs text-gray-500 font-mono">{{ ref.referral_code || '—' }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Date</span>
                <span class="font-medium text-gray-900">{{ formatDate(ref.created_at) }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span :class="getStatusBadgeClass(ref)" class="px-3 py-1 rounded-full text-xs font-semibold">
                  {{ getStatusText(ref) }}
                </span>
                <div v-if="ref.bonus_awarded" class="flex items-center gap-1 text-green-600">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-xs font-medium">Bonus Awarded</span>
                </div>
                <span v-else class="text-xs text-gray-400">Pending</span>
      </div>
    </div>
          </div>
        </div>
      </div>

      <!-- How It Works -->
      <div class="bg-linear-to-br from-primary-50 to-blue-50 rounded-2xl p-6 border border-primary-200">
        <h2 class="text-xl font-bold text-gray-900 mb-6 tracking-tight">How Referrals Work</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="flex items-start gap-4">
            <div class="shrink-0 w-12 h-12 bg-primary-600 text-white rounded-xl flex items-center justify-center font-bold text-lg shadow-md">
              1
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">Share Your Link</h3>
              <p class="text-sm text-gray-600 leading-relaxed">Copy and share your unique referral link with friends and family through email, social media, or any platform.</p>
            </div>
          </div>
          <div class="flex items-start gap-4">
            <div class="shrink-0 w-12 h-12 bg-primary-600 text-white rounded-xl flex items-center justify-center font-bold text-lg shadow-md">
              2
            </div>
          <div>
              <h3 class="font-semibold text-gray-900 mb-2">They Sign Up</h3>
              <p class="text-sm text-gray-600 leading-relaxed">When someone signs up using your link or code, they automatically become your referral.</p>
            </div>
          </div>
          <div class="flex items-start gap-4">
            <div class="shrink-0 w-12 h-12 bg-primary-600 text-white rounded-xl flex items-center justify-center font-bold text-lg shadow-md">
              3
        </div>
          <div>
              <h3 class="font-semibold text-gray-900 mb-2">Earn Rewards</h3>
              <p class="text-sm text-gray-600 leading-relaxed">You earn bonuses automatically when your referrals complete and approve their first order!</p>
            </div>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import referralsAPI from '@/api/referrals'

const authStore = useAuthStore()

// Check if user is a client - only clients can use referrals
const isClient = computed(() => {
  const role = authStore.user?.role || authStore.userRole
  return role === 'client'
})

// Show message if not a client
const notClientMessage = computed(() => {
  if (!isClient.value) {
    const role = authStore.user?.role || authStore.userRole || 'unknown'
    return `Referrals and loyalty points are only available for clients. Your role (${role}) does not have access to this feature.`
  }
  return null
})

const loading = ref(true)
const statsLoading = ref(false)
const generating = ref(false)
const referring = ref(false)
const referralEmail = ref('')
const referrals = ref([])
const codeStats = ref(null)
const stats = ref({
  total_referred: 0,
  completed_orders: 0,
  referral_code: null,
  referral_link: null,
})
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const getWebsiteId = () => {
  const user = authStore.user
  if (!user) {
    if (import.meta.env.DEV) {
    console.warn('No user found in authStore')
    }
    return null
  }
  
  if (user.website_id) return user.website_id
  if (user.website?.id) return user.website.id
  if (typeof user.website === 'number') return user.website
  if (typeof user.website === 'string') {
    const parsed = parseInt(user.website)
    if (!isNaN(parsed)) return parsed
  }
  
  const storedWebsite = localStorage.getItem('current_website')
  if (storedWebsite) {
    const parsed = parseInt(storedWebsite)
    if (!isNaN(parsed)) return parsed
  }
  
  return null
}

const loadCodeStats = async () => {
  try {
    const res = await referralsAPI.getMyCode()
    if (res.data && res.data.usage_stats) {
      codeStats.value = res.data.usage_stats
    }
  } catch (e) {
    if (import.meta.env.DEV) {
      console.debug('Could not load code stats:', e)
    }
  }
}

const loadStats = async () => {
  statsLoading.value = true
  try {
    const websiteId = getWebsiteId()
    if (!websiteId) {
      error.value = 'Website ID is required. Please contact support or refresh the page.'
      statsLoading.value = false
      return
    }
    const res = await referralsAPI.getStats(websiteId)
    stats.value = res.data || stats.value
    error.value = ''
    
    if (stats.value.referral_code) {
      await loadCodeStats()
    }
  } catch (e) {
    if (import.meta.env.DEV) {
    console.error('Failed to load stats:', e)
    }
    const errorMsg = e?.response?.data?.error || e?.response?.data?.message || e.message
    const status = e?.response?.status
    
    if (status === 404 && errorMsg?.includes('Website not found')) {
      error.value = `Website ID ${getWebsiteId()} not found. Please contact support.`
    } else if (errorMsg && errorMsg.includes('Website is required')) {
      error.value = 'Website ID is required. Please contact support.'
    } else {
      error.value = errorMsg || 'Failed to load referral statistics'
    }
  } finally {
    statsLoading.value = false
  }
}

const loadReferrals = async () => {
  loading.value = true
  try {
    const res = await referralsAPI.list({})
    referrals.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    if (import.meta.env.DEV) {
    console.error('Failed to load referrals:', e)
    }
    error.value = 'Failed to load referrals'
  } finally {
    loading.value = false
  }
}

const submitReferral = async () => {
  if (!referralEmail.value || !referralEmail.value.trim()) {
    error.value = 'Please enter an email address'
    return
  }

  referring.value = true
  error.value = ''
  message.value = ''
  
  try {
    const websiteId = getWebsiteId()
    if (!websiteId) {
      error.value = 'Website ID is required. Please contact support or refresh the page.'
      referring.value = false
      return
    }

    const res = await referralsAPI.referByEmail(referralEmail.value.trim(), websiteId)
    
    message.value = res.data?.message || `Successfully referred ${referralEmail.value}!`
    messageSuccess.value = true
    referralEmail.value = ''
    
    await Promise.all([loadReferrals(), loadStats()])
  } catch (e) {
    if (import.meta.env.DEV) {
    console.error('Refer by email error:', e)
    }
    const errorMsg = e?.response?.data?.error || e?.response?.data?.message || e.message
    error.value = errorMsg || 'Failed to create referral'
    messageSuccess.value = false
  } finally {
    referring.value = false
  }
}

const generateCode = async () => {
  generating.value = true
  error.value = ''
  message.value = ''
  try {
    const websiteId = getWebsiteId()
    if (!websiteId) {
      error.value = 'Website ID is required. Please contact support or refresh the page.'
      generating.value = false
      return
    }
    
    const res = await referralsAPI.generateCode(websiteId)
    
    if (res.data?.already_exists) {
      message.value = res.data?.message || `Referral code already exists: ${res.data?.code}`
      messageSuccess.value = true
    } else {
      message.value = res.data?.message || 'Referral code generated successfully!'
      messageSuccess.value = true
    }
    
    await loadStats()
    
    if (!stats.value.referral_code && !res.data?.already_exists) {
      throw new Error('Code generation succeeded but code not found in database')
    }
  } catch (e) {
    if (import.meta.env.DEV) {
    console.error('Generate code error:', e)
    }
    const errorMsg = e?.response?.data?.error || e?.response?.data?.message || e.message
    const status = e?.response?.status
    
    if (status === 404 && errorMsg?.includes('Website not found')) {
      error.value = `Website ID ${getWebsiteId()} not found. Please contact support.`
    } else {
      error.value = errorMsg || 'Failed to generate referral code'
    }
    messageSuccess.value = false
  } finally {
    generating.value = false
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    message.value = 'Copied to clipboard!'
    messageSuccess.value = true
    setTimeout(() => { message.value = '' }, 2000)
  } catch (e) {
    error.value = 'Failed to copy to clipboard'
  }
}

const shareEmail = () => {
  const subject = encodeURIComponent('Join me on Writing System!')
  const body = encodeURIComponent(`Check out Writing System! Use my referral code: ${stats.value.referral_code}\n\nOr sign up here: ${stats.value.referral_link || `${window.location.origin}/signup?ref=${stats.value.referral_code}`}`)
  window.location.href = `mailto:?subject=${subject}&body=${body}`
}

const shareWhatsApp = () => {
  const text = encodeURIComponent(`Check out Writing System! Use my referral code: ${stats.value.referral_code}\n\nSign up here: ${stats.value.referral_link || `${window.location.origin}/signup?ref=${stats.value.referral_code}`}`)
  window.open(`https://wa.me/?text=${text}`, '_blank')
}

const shareFacebook = () => {
  const url = encodeURIComponent(stats.value.referral_link || `${window.location.origin}/signup?ref=${stats.value.referral_code}`)
  window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=600,height=400')
}

const shareTwitter = () => {
  const text = encodeURIComponent(`Check out Writing System! Use my referral code: ${stats.value.referral_code}`)
  const url = encodeURIComponent(stats.value.referral_link || `${window.location.origin}/signup?ref=${stats.value.referral_code}`)
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank', 'width=600,height=400')
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const getStatusText = (ref) => {
  if (ref.bonus_awarded) return 'Bonus Awarded'
  if (ref.first_order_bonus_credited) return 'Order Completed'
  if (ref.registration_bonus_credited) return 'Registered'
  return 'Pending'
}

const getStatusBadgeClass = (ref) => {
  if (ref.bonus_awarded) return 'bg-green-100 text-green-700'
  if (ref.first_order_bonus_credited) return 'bg-blue-100 text-blue-700'
  if (ref.registration_bonus_credited) return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-700'
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([loadStats(), loadReferrals()])
  } catch (e) {
    if (import.meta.env.DEV) {
    console.error('Failed to load referrals page data:', e)
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@reference "tailwindcss";
</style>
