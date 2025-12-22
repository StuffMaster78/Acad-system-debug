<template>
  <div class="referral-link-sharing">
    <div class="bg-linear-to-r from-primary-600 to-primary-700 rounded-lg p-6 text-white mb-6">
      <h3 class="text-xl font-bold mb-2">Share Your Referral Link</h3>
      <p class="text-primary-100">Earn rewards when your friends sign up and make their first order!</p>
    </div>

    <!-- Referral Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="card p-4">
        <div class="text-sm text-gray-600 mb-1">Total Referrals</div>
        <div class="text-2xl font-bold text-gray-900">{{ stats.total_referrals || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-600 mb-1">Active Referrals</div>
        <div class="text-2xl font-bold text-green-600">{{ stats.active_referrals || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-600 mb-1">Total Earnings</div>
        <div class="text-2xl font-bold text-primary-600">${{ formatCurrency(stats.total_earnings || 0) }}</div>
      </div>
    </div>

    <!-- Referral Link -->
    <div class="card p-6 mb-6">
      <h4 class="text-lg font-semibold mb-4">Your Referral Link</h4>
      <div class="flex gap-2">
        <input
          :value="referralLink"
          readonly
          class="flex-1 border rounded-lg px-4 py-2 bg-gray-50 text-gray-700 font-mono text-sm"
          ref="linkInput"
        />
        <button
          @click="copyLink"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          {{ copied ? '✓ Copied!' : 'Copy Link' }}
        </button>
      </div>
      <p class="text-xs text-gray-500 mt-2">
        Share this link with friends. You'll earn rewards when they sign up and make their first order!
      </p>
    </div>

    <!-- Share Buttons -->
    <div class="card p-6 mb-6">
      <h4 class="text-lg font-semibold mb-4">Share Via</h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button
          @click="shareEmail"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
        >
          📧 Email
        </button>
        <button
          @click="shareWhatsApp"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
        >
          💬 WhatsApp
        </button>
        <button
          @click="shareFacebook"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
        >
          📘 Facebook
        </button>
        <button
          @click="shareTwitter"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
        >
          🐦 Twitter
        </button>
      </div>
    </div>

    <!-- Referral Code (Alternative) -->
    <div class="card p-6">
      <h4 class="text-lg font-semibold mb-4">Or Share Your Referral Code</h4>
      <div class="flex items-center gap-4">
        <div class="flex-1">
          <div class="text-3xl font-bold text-primary-600 font-mono text-center py-4 bg-gray-50 rounded-lg border-2 border-dashed border-primary-300">
            {{ referralCode }}
          </div>
        </div>
        <button
          @click="copyCode"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          {{ codeCopied ? '✓ Copied!' : 'Copy Code' }}
        </button>
      </div>
      <p class="text-xs text-gray-500 mt-2 text-center">
        Friends can enter this code during signup or checkout
      </p>
    </div>

    <!-- Referral Terms -->
    <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h5 class="font-semibold text-blue-900 mb-2">How It Works</h5>
      <ul class="text-sm text-blue-800 space-y-1 list-disc list-inside">
        <li>Share your unique referral link or code with friends</li>
        <li>When they sign up using your link, they become your referral</li>
        <li>You earn rewards when they complete their first order</li>
        <li>Rewards are credited to your account automatically</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import referralsAPI from '@/api/referrals'

const props = defineProps({
  referralCode: {
    type: String,
    default: ''
  },
  referralLink: {
    type: String,
    default: ''
  }
})

const stats = ref({
  total_referrals: 0,
  active_referrals: 0,
  total_earnings: 0
})

const copied = ref(false)
const codeCopied = ref(false)
const linkInput = ref(null)

const referralLink = computed(() => {
  if (props.referralLink) return props.referralLink
  const baseUrl = window.location.origin
  return `${baseUrl}/signup?ref=${props.referralCode}`
})

const copyLink = async () => {
  if (linkInput.value) {
    linkInput.value.select()
    linkInput.value.setSelectionRange(0, 99999) // For mobile devices
    try {
      await navigator.clipboard.writeText(referralLink.value)
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
    } catch (err) {
      // Fallback for older browsers
      document.execCommand('copy')
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
    }
  }
}

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.referralCode)
    codeCopied.value = true
    setTimeout(() => {
      codeCopied.value = false
    }, 2000)
  } catch (err) {
    document.execCommand('copy')
    codeCopied.value = true
    setTimeout(() => {
      codeCopied.value = false
    }, 2000)
  }
}

const shareEmail = () => {
  const subject = encodeURIComponent('Join me on Writing System!')
  const body = encodeURIComponent(`Check out Writing System! Use my referral code: ${props.referralCode}\n\nOr sign up here: ${referralLink.value}`)
  window.location.href = `mailto:?subject=${subject}&body=${body}`
}

const shareWhatsApp = () => {
  const text = encodeURIComponent(`Check out Writing System! Use my referral code: ${props.referralCode}\n\nSign up here: ${referralLink.value}`)
  window.open(`https://wa.me/?text=${text}`, '_blank')
}

const shareFacebook = () => {
  const url = encodeURIComponent(referralLink.value)
  window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=600,height=400')
}

const shareTwitter = () => {
  const text = encodeURIComponent(`Check out Writing System! Use my referral code: ${props.referralCode}`)
  const url = encodeURIComponent(referralLink.value)
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank', 'width=600,height=400')
}

const loadStats = async () => {
  try {
    const response = await referralsAPI.getStats()
    stats.value = response.data || stats.value
  } catch (error) {
    console.error('Failed to load referral stats:', error)
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.referral-link-sharing {
  width: 100%;
}
</style>

