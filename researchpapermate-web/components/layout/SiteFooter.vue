<script setup lang="ts">
const portal = usePortalStore()
const year = new Date().getFullYear()

const links = {
  Services: [
    { label: 'Research Papers', href: '/services#research-papers' },
    { label: 'Essays',          href: '/services#essays' },
    { label: 'Dissertations',   href: '/services#dissertations' },
    { label: 'Coursework',      href: '/services#coursework' },
  ],
  Company: [
    { label: 'About',           href: '/about' },
    { label: 'Blog',            href: '/blog' },
    { label: 'Contact',         href: '/contact' },
    { label: 'Apply as Writer', href: '/apply' },
  ],
  Legal: [
    { label: 'Privacy Policy', href: '/privacy' },
    { label: 'Terms of Use',   href: '/terms' },
    { label: 'Refund Policy',  href: '/refunds' },
  ],
}
</script>

<template>
  <footer class="border-t border-slate-100 bg-slate-50">
    <div class="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div class="grid grid-cols-2 gap-10 md:grid-cols-4">
        <!-- Brand column -->
        <div class="col-span-2 md:col-span-1">
          <span class="font-serif text-xl font-bold text-brand-700">{{ portal.brandName }}</span>
          <p class="mt-3 text-sm text-slate-500 leading-relaxed">{{ portal.tagline }}</p>
        </div>

        <!-- Link columns -->
        <div v-for="(items, group) in links" :key="group">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ group }}</h4>
          <ul class="mt-4 space-y-3">
            <li v-for="link in items" :key="link.href">
              <NuxtLink :href="link.href" class="text-sm text-slate-600 hover:text-brand-600">
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-12 border-t border-slate-200 pt-8 text-center text-xs text-slate-400">
        &copy; {{ year }} {{ portal.brandName }}. All rights reserved.
        <span class="mx-2">·</span>
        {{ portal.disclosure.text }}
      </div>
    </div>
  </footer>
</template>
