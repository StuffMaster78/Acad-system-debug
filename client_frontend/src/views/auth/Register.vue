<template>
  <Layout>
    <div class="section-padding bg-gray-50 min-h-screen flex items-center">
      <div class="container-custom max-w-md">
        <div class="bg-white rounded-lg shadow-lg p-8">
          <h1 class="text-3xl font-bold mb-2">Create Account</h1>
          <p class="text-gray-600 mb-8">Sign up to get started with our writing services.</p>

          <div v-if="authStore.error" class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-4">
            {{ authStore.error }}
          </div>

          <form @submit.prevent="handleRegister" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input 
                v-model="form.full_name" 
                type="text" 
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Email *
              </label>
              <input 
                v-model="form.email" 
                type="email" 
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
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
                minlength="8"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="••••••••"
              />
              <p class="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password *
              </label>
              <input 
                v-model="form.password_confirm" 
                type="password" 
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="••••••••"
              />
            </div>

            <div class="flex items-start">
              <input 
                v-model="form.accept_terms" 
                type="checkbox" 
                required
                class="mt-1 mr-2"
              />
              <label class="text-sm text-gray-600">
                I agree to the 
                <a href="#" class="text-primary-600 hover:underline">Terms of Service</a> 
                and 
                <a href="#" class="text-primary-600 hover:underline">Privacy Policy</a>
              </label>
            </div>

            <button 
              type="submit" 
              :disabled="authStore.loading || form.password !== form.password_confirm"
              class="btn btn-primary w-full"
            >
              {{ authStore.loading ? 'Creating account...' : 'Create Account' }}
            </button>
          </form>

          <div class="mt-6 text-center">
            <p class="text-gray-600">
              Already have an account? 
              <router-link to="/login" class="text-primary-600 hover:underline font-semibold">
                Login here
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
import { useRouter } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useAuthStore } from '@/stores/auth'
import { useWebsiteStore } from '@/stores/website'

const router = useRouter()
const authStore = useAuthStore()
const websiteStore = useWebsiteStore()

const form = ref({
  full_name: '',
  email: '',
  password: '',
  password_confirm: '',
  accept_terms: false,
  role: 'client', // Default role
})

const handleRegister = async () => {
  if (form.value.password !== form.value.password_confirm) {
    alert('Passwords do not match')
    return
  }

  const result = await authStore.register(form.value)
  if (result.success) {
    router.push('/dashboard')
  }
}

onMounted(() => {
  websiteStore.detectWebsite()
})
</script>

