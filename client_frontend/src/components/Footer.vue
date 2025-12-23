<template>
  <footer class="bg-gray-900 text-gray-300">
    <div class="container-custom section-padding">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- About -->
        <div>
          <h3 class="text-white font-semibold mb-4">{{ websiteStore.siteName }}</h3>
          <p class="text-sm">
            Professional writing services for all your academic and business needs.
          </p>
        </div>

        <!-- Quick Links -->
        <div>
          <h4 class="text-white font-semibold mb-4">Quick Links</h4>
          <ul class="space-y-2 text-sm">
            <li><router-link to="/" class="hover:text-white transition">Home</router-link></li>
            <li><router-link to="/services" class="hover:text-white transition">Services</router-link></li>
            <li><router-link to="/pricing" class="hover:text-white transition">Pricing</router-link></li>
            <li><router-link to="/blog" class="hover:text-white transition">Blog</router-link></li>
          </ul>
        </div>

        <!-- Support -->
        <div>
          <h4 class="text-white font-semibold mb-4">Support</h4>
          <ul class="space-y-2 text-sm">
            <li><a href="#" class="hover:text-white transition">Contact Us</a></li>
            <li><a href="#" class="hover:text-white transition">FAQ</a></li>
            <li><a href="#" class="hover:text-white transition">Terms of Service</a></li>
            <li><a href="#" class="hover:text-white transition">Privacy Policy</a></li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h4 class="text-white font-semibold mb-4">Contact</h4>
          <ul class="space-y-2 text-sm">
            <li v-if="websiteStore.website?.contact_email">
              Email: {{ websiteStore.website.contact_email }}
            </li>
            <li v-if="websiteStore.website?.contact_phone">
              Phone: {{ websiteStore.website.contact_phone }}
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-8 pt-8 border-t border-gray-800 text-center text-sm">
        <p>&copy; {{ new Date().getFullYear() }} {{ websiteStore.siteName }}. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { useWebsiteStore } from '@/stores/website'

const websiteStore = useWebsiteStore()
</script>

