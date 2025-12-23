<template>
  <Layout>
    <div class="section-padding bg-gray-50 min-h-screen">
      <div class="container-custom">
        <h1 class="text-3xl font-bold mb-8">Dashboard</h1>
        <p class="text-gray-600 mb-8">
          Welcome back, {{ authStore.user?.full_name || authStore.user?.email }}!
        </p>

        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
          <p class="text-yellow-800">
            <strong>Note:</strong> This is a basic dashboard. For full functionality, 
            please access the main client dashboard at your website's client portal.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-white p-6 rounded-lg shadow-sm">
            <h3 class="text-lg font-semibold mb-2">Active Orders</h3>
            <p class="text-3xl font-bold text-primary-600">0</p>
          </div>
          <div class="bg-white p-6 rounded-lg shadow-sm">
            <h3 class="text-lg font-semibold mb-2">Completed</h3>
            <p class="text-3xl font-bold text-green-600">0</p>
          </div>
          <div class="bg-white p-6 rounded-lg shadow-sm">
            <h3 class="text-lg font-semibold mb-2">Wallet Balance</h3>
            <p class="text-3xl font-bold text-blue-600">$0.00</p>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
          <div class="flex flex-wrap gap-4">
            <router-link to="/order" class="btn btn-primary">
              Place New Order
            </router-link>
            <button class="btn btn-secondary">
              View Orders
            </button>
            <button class="btn btn-outline">
              Payment History
            </button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { useWebsiteStore } from '@/stores/website'

const authStore = useAuthStore()
const websiteStore = useWebsiteStore()

onMounted(() => {
  websiteStore.detectWebsite()
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchUser()
  }
})
</script>

