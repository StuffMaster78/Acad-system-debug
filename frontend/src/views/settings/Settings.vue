<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Settings</h1>
      <div v-if="message" class="p-3 rounded text-sm" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
        {{ message }}
      </div>
    </div>

    <div v-if="error" class="p-4 rounded-lg bg-red-50 border border-red-200">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <span class="text-red-700">{{ error }}</span>
      </div>
    </div>

    <!-- Tabs Navigation -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'notifications'"
          :class="[
            activeTab === 'notifications'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Notifications
        </button>
        <button
          @click="activeTab = 'security'"
          :class="[
            activeTab === 'security'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Security
        </button>
        <button
          v-if="authStore.isAdmin || authStore.isSuperadmin"
          @click="activeTab = 'admin'"
          :class="[
            activeTab === 'admin'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Admin
        </button>
      </nav>
    </div>

    <!-- Notifications Tab -->
    <div v-if="activeTab === 'notifications'" class="space-y-6">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-semibold">Notification Preferences</h2>
            <p class="text-sm text-gray-500 mt-1">Control how and when you receive notifications</p>
          </div>
          <div class="flex gap-2">
            <button @click="enableAllNotifications" class="text-sm text-primary-600 hover:underline">Enable All</button>
            <span class="text-gray-300">|</span>
            <button @click="disableAllNotifications" class="text-sm text-gray-600 hover:underline">Disable All</button>
          </div>
        </div>

        <div v-if="prefsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>

        <form v-else @submit.prevent="savePreferences" class="space-y-8">
          <!-- Master Toggle -->
          <div class="p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
            <label class="flex items-center justify-between cursor-pointer">
              <div>
                <span class="font-semibold text-lg">Enable All Notifications</span>
                <p class="text-sm text-gray-600 mt-1">Master switch for all notification types</p>
              </div>
              <div class="relative">
                <input v-model="prefs.enabled" type="checkbox" class="sr-only" />
                <div :class="[
                  'w-14 h-7 rounded-full transition-colors duration-200 ease-in-out',
                  prefs.enabled ? 'bg-primary-600' : 'bg-gray-300'
                ]">
                  <div :class="[
                    'absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-md transform transition-transform duration-200 ease-in-out',
                    prefs.enabled ? 'translate-x-7' : 'translate-x-0'
                  ]"></div>
                </div>
              </div>
            </label>
          </div>

          <!-- Temporary Mute -->
          <div class="p-4 border rounded-lg">
            <h3 class="text-md font-semibold mb-3 flex items-center">
              <svg class="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m9.9-9.9a9 9 0 010 12.728" />
              </svg>
              Temporary Mute
            </h3>
            <div class="space-y-3">
              <label class="flex items-center justify-between">
                <span class="text-sm">Mute all notifications</span>
                <input v-model="prefs.mute_all" type="checkbox" class="rounded" />
              </label>
              <div v-if="prefs.mute_all" class="mt-2">
                <label class="block text-sm font-medium mb-1">Mute until (optional)</label>
                <input v-model="prefs.mute_until" type="datetime-local" class="w-full border rounded px-3 py-2" />
              </div>
            </div>
          </div>

          <!-- Notification Channels -->
          <div>
            <h3 class="text-md font-semibold mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              Notification Channels
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <div>
                    <span class="font-medium block">Email</span>
                    <span class="text-xs text-gray-500">Receive via email</span>
                  </div>
                </div>
                <input v-model="prefs.receive_email" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <div>
                    <span class="font-medium block">In-App</span>
                    <span class="text-xs text-gray-500">Show in dashboard</span>
                  </div>
                </div>
                <input v-model="prefs.receive_in_app" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <div>
                    <span class="font-medium block">SMS</span>
                    <span class="text-xs text-gray-500">Text messages</span>
                  </div>
                </div>
                <input v-model="prefs.receive_sms" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  <div>
                    <span class="font-medium block">Push</span>
                    <span class="text-xs text-gray-500">Browser notifications</span>
                  </div>
                </div>
                <input v-model="prefs.receive_push" type="checkbox" class="w-5 h-5 rounded" />
              </label>
            </div>
          </div>

          <!-- Notification Frequency -->
          <div>
            <h3 class="text-md font-semibold mb-4">Notification Frequency</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50" :class="{ 'border-primary-500 bg-primary-50': prefs.frequency === 'immediate' }">
                <input v-model="prefs.frequency" type="radio" value="immediate" class="mr-3" />
                <div>
                  <span class="font-medium block">Immediate</span>
                  <span class="text-xs text-gray-500">Get notified right away</span>
                </div>
              </label>
              <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50" :class="{ 'border-primary-500 bg-primary-50': prefs.frequency === 'daily' }">
                <input v-model="prefs.frequency" type="radio" value="daily" class="mr-3" />
                <div>
                  <span class="font-medium block">Daily Digest</span>
                  <span class="text-xs text-gray-500">Once per day summary</span>
                </div>
              </label>
              <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50" :class="{ 'border-primary-500 bg-primary-50': prefs.frequency === 'weekly' }">
                <input v-model="prefs.frequency" type="radio" value="weekly" class="mr-3" />
                <div>
                  <span class="font-medium block">Weekly Digest</span>
                  <span class="text-xs text-gray-500">Once per week summary</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Event Preferences -->
          <div>
            <h3 class="text-md font-semibold mb-4">Event Notifications</h3>
            <div class="space-y-3">
              <label class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <span class="font-medium">Order Updates</span>
                  <p class="text-xs text-gray-500">When your orders are updated</p>
                </div>
                <input v-model="prefs.notify_order_updates" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <span class="font-medium">Payment Notifications</span>
                  <p class="text-xs text-gray-500">Payment status changes</p>
                </div>
                <input v-model="prefs.notify_payments" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <span class="font-medium">Ticket Updates</span>
                  <p class="text-xs text-gray-500">Support ticket responses</p>
                </div>
                <input v-model="prefs.notify_tickets" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <span class="font-medium">Writer Messages</span>
                  <p class="text-xs text-gray-500">Messages from writers</p>
                </div>
                <input v-model="prefs.notify_messages" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <span class="font-medium">MFA Login Alerts</span>
                  <p class="text-xs text-gray-500">When MFA is used</p>
                </div>
                <input v-model="prefs.notify_mfa_login" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <span class="font-medium">Password Changes</span>
                  <p class="text-xs text-gray-500">When password is changed</p>
                </div>
                <input v-model="prefs.notify_password_change" type="checkbox" class="w-5 h-5 rounded" />
              </label>
              <label class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div>
                  <span class="font-medium">Wallet Transactions</span>
                  <p class="text-xs text-gray-500">Wallet activity</p>
                </div>
                <input v-model="prefs.notify_wallet_transactions" type="checkbox" class="w-5 h-5 rounded" />
              </label>
            </div>
          </div>

          <!-- Quiet Hours -->
          <div class="p-4 border rounded-lg">
            <h3 class="text-md font-semibold mb-4">Quiet Hours (Do Not Disturb)</h3>
            <label class="flex items-center justify-between mb-4">
              <span class="text-sm">Enable quiet hours</span>
              <input v-model="prefs.do_not_disturb_enabled" type="checkbox" class="rounded" />
            </label>
            <div v-if="prefs.do_not_disturb_enabled" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Start Time</label>
                <input v-model="prefs.quiet_hours_start" type="time" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">End Time</label>
                <input v-model="prefs.quiet_hours_end" type="time" class="w-full border rounded px-3 py-2" />
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-2">Notifications will be muted during these hours</p>
          </div>

          <!-- Marketing -->
          <div class="p-4 border rounded-lg">
            <label class="flex items-center justify-between cursor-pointer">
              <div>
                <span class="font-medium">Marketing Emails</span>
                <p class="text-xs text-gray-500 mt-1">Receive promotional emails and updates</p>
              </div>
              <input v-model="prefs.marketing_opt_in" type="checkbox" class="w-5 h-5 rounded" />
            </label>
          </div>

          <!-- Save Button -->
          <div class="flex gap-3 pt-4 border-t">
            <button :disabled="saving" class="px-6 py-2 bg-primary-600 text-white rounded-lg disabled:opacity-50 hover:bg-primary-700 transition-colors flex items-center">
              <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ saving ? 'Saving...' : 'Save Preferences' }}
            </button>
            <button type="button" @click="loadPreferences" class="px-6 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">Reset</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Security Tab -->
    <div v-if="activeTab === 'security'" class="space-y-6">
      <div class="card p-6">
        <h2 class="text-xl font-semibold mb-4">Security Settings</h2>
        <div class="space-y-4">
          <router-link to="/profile" class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <div>
              <span class="font-medium">Profile Settings</span>
              <p class="text-xs text-gray-500 mt-1">Manage your profile information</p>
            </div>
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
          <router-link to="/password-reset" class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
            <div>
              <span class="font-medium">Change Password</span>
              <p class="text-xs text-gray-500 mt-1">Update your account password</p>
            </div>
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </div>

      <div class="card p-6 bg-blue-50 border border-blue-200">
        <h3 class="font-semibold mb-2 flex items-center">
          <svg class="w-5 h-5 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
          Rate Limiting Information
        </h3>
        <p class="text-sm text-gray-700">
          Magic link requests are limited to <strong>3 per minute</strong> to prevent spam. If you see "Too many magic link requests", please wait a minute before trying again.
        </p>
      </div>

      <div v-if="authStore.isClient" class="card p-6">
        <h2 class="text-xl font-semibold mb-4">Account Status</h2>
        <div class="space-y-3">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span class="text-sm font-medium">Status:</span>
            <span :class="statusBadgeClass" class="px-3 py-1 rounded-full text-sm">{{ accountStatus }}</span>
          </div>
          <div v-if="deletionRequestStatus" class="flex items-center justify-between p-3 bg-yellow-50 rounded border border-yellow-200">
            <span class="text-sm font-medium">Deletion Request:</span>
            <span class="text-sm text-yellow-700">{{ deletionRequestStatus }}</span>
          </div>
          <router-link to="/profile" class="inline-block mt-2 text-sm text-primary-600 hover:underline">
            Manage Profile & Deletion Requests →
          </router-link>
        </div>
      </div>
    </div>

    <!-- Admin Tab -->
    <div v-if="activeTab === 'admin' && (authStore.isAdmin || authStore.isSuperadmin)" class="card p-6">
      <h2 class="text-xl font-semibold mb-4">Admin Settings</h2>
      <div class="space-y-3">
        <router-link to="/users" class="block p-4 border rounded-lg hover:bg-gray-50 transition-colors">
          <span class="font-medium">Manage Users</span>
          <p class="text-xs text-gray-500 mt-1">View and manage all users</p>
        </router-link>
        <router-link to="/websites" class="block p-4 border rounded-lg hover:bg-gray-50 transition-colors">
          <span class="font-medium">Manage Websites</span>
          <p class="text-xs text-gray-500 mt-1">Multi-tenant website management</p>
        </router-link>
        <router-link to="/settings/system" class="block p-4 border rounded-lg hover:bg-gray-50 transition-colors">
          <span class="font-medium">System Settings</span>
          <p class="text-xs text-gray-500 mt-1">Configure system-wide settings</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import usersAPI from '@/api/users'
import notificationsAPI from '@/api/notifications'

const authStore = useAuthStore()
const activeTab = ref('notifications')

const profile = ref(null)
const prefs = ref({
  enabled: true,
  mute_all: false,
  mute_until: null,
  receive_email: true,
  receive_in_app: true,
  receive_sms: false,
  receive_push: false,
  frequency: 'immediate',
  notify_order_updates: true,
  notify_payments: true,
  notify_tickets: true,
  notify_messages: true,
  notify_mfa_login: true,
  notify_password_change: true,
  notify_wallet_transactions: true,
  marketing_opt_in: false,
  do_not_disturb_enabled: false,
  quiet_hours_start: '22:00',
  quiet_hours_end: '07:00',
})
const prefsLoading = ref(true)
const saving = ref(false)
const loading = ref(true)
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const accountStatus = computed(() => {
  if (profile.value?.is_deleted) return 'Pending Deletion'
  if (!authStore.user?.is_active) return 'Inactive'
  return 'Active'
})

const statusBadgeClass = computed(() => {
  if (profile.value?.is_deleted) return 'bg-red-100 text-red-700'
  if (!authStore.user?.is_active) return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
})

const deletionRequestStatus = computed(() => {
  if (profile.value?.is_deleted) return 'Pending admin approval'
  return null
})

const enableAllNotifications = () => {
  prefs.value.enabled = true
  prefs.value.receive_email = true
  prefs.value.receive_in_app = true
  prefs.value.receive_sms = true
  prefs.value.receive_push = true
  prefs.value.mute_all = false
}

const disableAllNotifications = () => {
  prefs.value.enabled = false
  prefs.value.receive_email = false
  prefs.value.receive_in_app = false
  prefs.value.receive_sms = false
  prefs.value.receive_push = false
}

const loadPreferences = async () => {
  prefsLoading.value = true
  try {
    const res = await notificationsAPI.getPreferences()
    const data = res.data || {}
    prefs.value = {
      enabled: data.enabled ?? true,
      mute_all: data.mute_all ?? false,
      mute_until: data.mute_until || null,
      receive_email: data.receive_email ?? true,
      receive_in_app: data.receive_in_app ?? true,
      receive_sms: data.receive_sms ?? false,
      receive_push: data.receive_push ?? false,
      frequency: data.frequency || 'immediate',
      notify_order_updates: data.notify_order_updates ?? true,
      notify_payments: data.notify_payments ?? true,
      notify_tickets: data.notify_tickets ?? true,
      notify_messages: data.notify_messages ?? true,
      notify_mfa_login: data.notify_mfa_login ?? true,
      notify_password_change: data.notify_password_change ?? true,
      notify_wallet_transactions: data.notify_wallet_transactions ?? true,
      marketing_opt_in: data.marketing_opt_in ?? false,
      do_not_disturb_enabled: data.do_not_disturb_enabled ?? false,
      quiet_hours_start: data.do_not_disturb_start || data.quiet_hours?.start || '22:00',
      quiet_hours_end: data.do_not_disturb_end || data.quiet_hours?.end || '07:00',
    }
  } catch (e) {
    console.error('Failed to load preferences:', e)
    error.value = 'Failed to load notification preferences'
  } finally {
    prefsLoading.value = false
  }
}

const savePreferences = async () => {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    const payload = {
      enabled: prefs.value.enabled,
      mute_all: prefs.value.mute_all,
      mute_until: prefs.value.mute_until || null,
      receive_email: prefs.value.receive_email,
      receive_in_app: prefs.value.receive_in_app,
      receive_sms: prefs.value.receive_sms,
      receive_push: prefs.value.receive_push,
      frequency: prefs.value.frequency,
      notify_order_updates: prefs.value.notify_order_updates,
      notify_payments: prefs.value.notify_payments,
      notify_tickets: prefs.value.notify_tickets,
      notify_messages: prefs.value.notify_messages,
      notify_mfa_login: prefs.value.notify_mfa_login,
      notify_password_change: prefs.value.notify_password_change,
      notify_wallet_transactions: prefs.value.notify_wallet_transactions,
      marketing_opt_in: prefs.value.marketing_opt_in,
      do_not_disturb_enabled: prefs.value.do_not_disturb_enabled,
      do_not_disturb_start: prefs.value.quiet_hours_start,
      do_not_disturb_end: prefs.value.quiet_hours_end,
    }
    await notificationsAPI.updatePreferences(payload)
    message.value = 'Notification preferences saved successfully.'
    messageSuccess.value = true
    setTimeout(() => { message.value = '' }, 3000)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to save preferences'
  } finally {
    saving.value = false
  }
}

const loadProfile = async () => {
  loading.value = true
  try {
    const res = await usersAPI.getProfile()
    profile.value = res.data
  } catch (e) {
    error.value = 'Failed to load profile'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadProfile()
  await loadPreferences()
})
</script>
