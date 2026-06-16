<script setup lang="ts">
const portal = usePortalStore()
const appUrl = useAppUrl()
const year = new Date().getFullYear()

const assignmentTypes = [
  { label: 'Essay Writing',     href: '/earnings' },
  { label: 'Research Papers',   href: '/earnings' },
  { label: 'Dissertations',     href: '/earnings' },
  { label: 'Nursing Essays',    href: '/earnings' },
  { label: 'Data Analysis',     href: '/earnings' },
  { label: 'Case Studies',      href: '/earnings' },
  { label: 'Capstone Projects', href: '/earnings' },
]

const company = [
  { label: 'How it works', href: '/how-it-works' },
  { label: 'Earnings',     href: '/earnings'      },
  { label: 'Blog',         href: '/blog'          },
  { label: 'FAQ',          href: '/faq'           },
  { label: 'About',        href: '/about'         },
  { label: 'Contact',      href: '/contact'       },
]

const writerLinks = [
  { label: 'Apply to write',    href: '/apply'         },
  { label: 'Writer login',      href: appUrl.login     },
  { label: 'Writer resources',  href: '/blog'          },
  { label: 'Vetting process',   href: '/how-it-works'  },
  { label: 'Payout schedule',   href: '/earnings'      },
]

const account = [
  { label: 'Writer login',    href: appUrl.login    },
  { label: 'Create account',  href: appUrl.register },
  { label: 'Apply now',       href: '/apply'        },
]

const legal = [
  { label: 'Privacy Policy', href: '/legal/privacy' },
  { label: 'Terms of Service', href: '/legal/terms' },
  { label: 'Refund Policy',  href: '/legal/refunds' },
]

const platform = [
  { label: 'Grade guarantee',   href: '/how-it-works' },
  { label: 'Zero AI policy',    href: '/how-it-works' },
  { label: 'Writer standards',  href: '/how-it-works' },
  { label: 'Support',           href: '/contact'      },
]

const SOCIAL_ICONS: Record<string, string> = {
  twitter:   `<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622 5.911-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>`,
  instagram: `<path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162S8.597 18.163 12 18.163s6.162-2.759 6.162-6.162S15.403 5.838 12 5.838zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>`,
  linkedin:  `<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>`,
}

const social = computed(() => portal.socialLinks)
</script>

<template>
  <footer class="border-t border-slate-800 bg-slate-900 text-slate-400">

    <!-- Trust strip -->
    <div class="border-b border-slate-800">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-6 px-4 py-5 sm:px-6 lg:px-8">
        <span class="text-sm"><strong class="text-white">2,000+</strong> active writers</span>
        <span class="hidden text-slate-700 sm:block">·</span>
        <span class="text-sm"><strong class="text-white">$18–$45</strong> per page earned</span>
        <span class="hidden text-slate-700 sm:block">·</span>
        <span class="text-sm">Bi-weekly payouts, every time</span>
        <span class="hidden text-slate-700 sm:block">·</span>
        <span class="text-sm">4.8/5 writer satisfaction</span>
      </div>
    </div>

    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

      <!-- Row 1: Brand · Assignment types · Company · Writers -->
      <div class="grid gap-8 py-14 sm:grid-cols-2 lg:grid-cols-4">

        <!-- Brand -->
        <div class="space-y-4">
          <NuxtLink href="/" class="flex items-center gap-2.5">
            <svg width="26" height="26" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="1" width="28" height="28" rx="7" fill="#1e293b"/>
              <path d="M7 8l3.5 12L14 12l3.5 8L21 8" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="text-base font-bold leading-none tracking-tight">
              <span class="text-white">Writers</span><span class="text-brand-400">Creek</span>
            </span>
          </NuxtLink>
          <p class="text-xs leading-relaxed text-slate-500">A selective academic writing network. Competitive rates, expert assignments, reliable payouts.</p>
          <div v-if="social.length" class="flex flex-wrap gap-1.5">
            <a v-for="s in social" :key="s.name" :href="s.href" :aria-label="s.name" target="_blank" rel="noreferrer"
              class="flex h-7 w-7 items-center justify-center rounded-md bg-slate-800 text-slate-400 transition-colors hover:bg-brand-700 hover:text-white">
              <svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24"><g v-html="SOCIAL_ICONS[s.icon] ?? ''" /></svg>
            </a>
          </div>
          <NuxtLink href="/apply" class="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand-700">
            Apply now →
          </NuxtLink>
        </div>

        <!-- Assignment Types -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">What you'll write</p>
          <ul class="space-y-2">
            <li v-for="s in assignmentTypes" :key="s.label">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Company -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Company</p>
          <ul class="space-y-2">
            <li v-for="s in company" :key="s.href">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Writers -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Writers</p>
          <ul class="space-y-2">
            <li v-for="s in writerLinks" :key="s.label">
              <a :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</a>
            </li>
          </ul>
        </div>

      </div>

      <!-- Row 2: Account · Legal · Platform -->
      <div class="grid gap-8 border-t border-slate-800 py-10 sm:grid-cols-3">

        <!-- Account -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Account</p>
          <ul class="space-y-2">
            <li v-for="s in account" :key="s.label">
              <a :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</a>
            </li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Legal</p>
          <ul class="space-y-2">
            <li v-for="s in legal" :key="s.href">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Platform -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Platform</p>
          <ul class="space-y-2">
            <li v-for="s in platform" :key="s.label">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
          <div class="mt-5 space-y-1.5 text-xs text-slate-500">
            <p class="flex items-center gap-2"><span class="text-brand-400">✓</span> Credential-verified writers only</p>
            <p class="flex items-center gap-2"><span class="text-brand-400">✓</span> Zero AI content</p>
            <p class="flex items-center gap-2"><span class="text-brand-400">✓</span> Bi-weekly reliable payouts</p>
          </div>
        </div>

      </div>

    </div>

    <!-- Bottom bar -->
    <div class="border-t border-slate-800">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-5 sm:px-6 lg:px-8">
        <p class="text-xs text-slate-600">&copy; {{ year }} {{ portal.brandName }}. All rights reserved.</p>
        <p class="max-w-xl text-center text-xs leading-relaxed text-slate-700">{{ portal.disclosure?.text }}</p>
      </div>
    </div>

  </footer>
</template>
