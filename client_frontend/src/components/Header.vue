<template>
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <nav class="container-custom">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center space-x-2">
          <img 
            v-if="websiteStore.logo" 
            :src="websiteStore.logo" 
            :alt="websiteStore.siteName"
            class="h-8 w-auto"
          />
          <span v-else class="text-2xl font-bold" :style="{ color: websiteStore.themeColor }">
            {{ websiteStore.siteName }}
          </span>
        </router-link>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-8">
          <router-link to="/" class="text-gray-700 hover:text-primary-600 transition">Home</router-link>
          <router-link to="/services" class="text-gray-700 hover:text-primary-600 transition">Services</router-link>
          <router-link to="/pricing" class="text-gray-700 hover:text-primary-600 transition">Pricing</router-link>
          <router-link to="/blog" class="text-gray-700 hover:text-primary-600 transition">Blog</router-link>
        </div>

        <!-- Auth Buttons -->
        <div class="flex items-center space-x-4">
          <template v-if="authStore.isAuthenticated">
            <router-link to="/dashboard" class="text-gray-700 hover:text-primary-600">
              Dashboard
            </router-link>
            <button @click="handleLogout" class="btn btn-outline">
              Logout
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="text-gray-700 hover:text-primary-600">
              Login
            </router-link>
            <router-link to="/order" class="btn btn-primary">
              Order Now
            </router-link>
          </template>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useWebsiteStore } from '@/stores/website'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const websiteStore = useWebsiteStore()
const router = useRouter()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>

