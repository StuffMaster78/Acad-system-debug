<template>
  <Layout>
    <div class="section-padding bg-gray-50 min-h-screen flex items-center">
      <div class="container-custom max-w-md">
        <div class="bg-white rounded-lg shadow-lg p-8">
          <h1 class="text-3xl font-bold mb-2">Login</h1>
          <p class="text-gray-600 mb-8">Welcome back! Please login to your account.</p>

          <div v-if="authStore.error" class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-4">
            {{ authStore.error }}
          </div>

          <form @submit.prevent="handleLogin" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Email *
              </label>
              <input 
                v-model="form.email" 
                type="email" 
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Password *
              </label>
              <input 
                v-model="form.password" 
                type="password" 
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="••••••••"
              />
            </div>

            <div class="flex items-center justify-between">
              <label class="flex items-center">
                <input 
                  v-model="form.remember_me" 
                  type="checkbox" 
                  class="mr-2"
                />
                <span class="text-sm text-gray-600">Remember me</span>
              </label>
              <a href="#" class="text-sm text-primary-600 hover:underline">
                Forgot password?
              </a>
            </div>

            <button 
              type="submit" 
              :disabled="authStore.loading"
              class="btn btn-primary w-full"
            >
              {{ authStore.loading ? 'Logging in...' : 'Login' }}
            </button>
          </form>

          <div class="mt-6 text-center">
            <p class="text-gray-600">
              Don't have an account? 
              <router-link to="/register" class="text-primary-600 hover:underline font-semibold">
                Register here
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { useWebsiteStore } from '@/stores/website'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const websiteStore = useWebsiteStore()

const form = ref({
  email: '',
  password: '',
  remember_me: false,
})

const handleLogin = async () => {
  const result = await authStore.login(form.value)
  if (result.success) {
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  }
}

onMounted(() => {
  websiteStore.detectWebsite()
})
</script>

