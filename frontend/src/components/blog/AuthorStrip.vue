<template>
  <div v-if="authors && authors.length > 0" class="author-strip border-t border-b border-gray-200 py-6 my-8">
    <div class="flex flex-wrap items-start gap-6">
      <div
        v-for="author in authors"
        :key="author.id"
        class="flex items-start gap-4 flex-1 min-w-[280px]"
      >
        <!-- Author Avatar -->
        <div class="shrink-0">
          <img
            v-if="author.profile_picture"
            :src="author.profile_picture"
            :alt="author.name"
            class="w-16 h-16 rounded-full object-cover border-2 border-gray-200"
          />
          <div
            v-else
            class="w-16 h-16 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white text-xl font-semibold"
          >
            {{ author.name?.charAt(0)?.toUpperCase() || 'A' }}
          </div>
        </div>

        <!-- Author Info -->
        <div class="flex-1 min-w-0">
          <h3 class="text-lg font-semibold text-gray-900 mb-1">
            {{ author.name }}
          </h3>
          <p v-if="author.designation" class="text-sm text-gray-600 mb-2">
            {{ author.designation }}
          </p>
          <p v-if="author.bio" class="text-sm text-gray-700 mb-3 line-clamp-2">
            {{ author.bio }}
          </p>

          <!-- Social Links -->
          <div v-if="hasSocialLinks(author)" class="flex items-center gap-3">
            <a
              v-if="author.twitter_url"
              :href="author.twitter_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-400 hover:text-blue-400 transition-colors"
              aria-label="Twitter"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"/>
              </svg>
            </a>
            <a
              v-if="author.linkedin_url"
              :href="author.linkedin_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-400 hover:text-blue-600 transition-colors"
              aria-label="LinkedIn"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
            </a>
            <a
              v-if="author.website_url"
              :href="author.website_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Website"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  authors: {
    type: Array,
    default: () => []
  }
})

const hasSocialLinks = (author) => {
  return !!(author.twitter_url || author.linkedin_url || author.website_url)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

