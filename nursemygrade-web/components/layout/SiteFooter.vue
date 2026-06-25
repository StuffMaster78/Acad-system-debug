<script setup lang="ts">
const portal = usePortalStore()
const year = new Date().getFullYear()

const writingServices = [
  { label: 'Nursing Essays',        href: '/nursing-essays'         },
  { label: 'Care Plans',            href: '/care-plans'             },
  { label: 'SOAP Notes',            href: '/soap-notes'             },
  { label: 'Research Papers',       href: '/nursing-research-papers'},
  { label: 'Capstone Projects',     href: '/capstone-projects'      },
  { label: 'Dissertations',         href: '/nursing-dissertations'  },
]

const clinicalServices = [
  { label: 'Case Studies',          href: '/nursing-case-studies'   },
  { label: 'Concept Maps',          href: '/concept-maps'           },
  { label: 'Coursework Help',       href: '/nursing-coursework'     },
  { label: 'Shadow Health',         href: '/shadow-health'          },
  { label: 'iHuman Patients',       href: '/ihuman-patients'        },
  { label: 'Online Class Help',     href: '/online-nursing-classes' },
]

const specialtyServices = [
  { label: 'BSN Writing',           href: '/bsn-writing'           },
  { label: 'MSN Writing Help',      href: '/msn-help'              },
  { label: 'APA Nursing Papers',    href: '/apa-nursing-papers'    },
  { label: 'Nursing Reports',       href: '/nursing-report'        },
  { label: 'Nursing Presentations', href: '/nursing-presentation'  },
]

const company = [
  { label: 'How It Works',          href: '/how-it-works'  },
  { label: 'Our Nurse Writers',     href: '/writers'       },
  { label: 'Student Reviews',       href: '/reviews'       },
  { label: 'Pricing',               href: '/pricing'       },
  { label: 'About Us',              href: '/about'         },
  { label: 'Blog',                  href: '/blog'          },
  { label: 'Contact',               href: '/contact'       },
  { label: 'Become a Writer',       href: '/apply'         },
]

const quickLinks = [
  { label: 'Place an Order',        href: '/order'         },
  { label: 'Custom Quote',          href: '/quote'         },
  { label: 'Discounts & Offers',   href: '/discounts'     },
  { label: 'FAQ',                   href: '/faq'           },
  { label: 'Our Authors',           href: '/authors'       },
]

const resources = [
  { label: 'Care Plan Guide',       href: '/nursing-care-plan-guide'                          },
  { label: 'SOAP Note Guide',       href: '/soap-notes-guide-for-nursing-students'            },
  { label: 'APA 7th for Nursing',   href: '/apa-7th-edition-guide-nursing-papers'             },
  { label: 'Shadow Health Tips',    href: '/tips-for-succeeding-in-shadow-health-assessments' },
  { label: 'iHuman Tips',           href: '/ihuman-tips-help-and-tricks'                      },
]

const legal = [
  { label: 'Privacy Policy', href: '/privacy' },
  { label: 'Terms of Use',   href: '/terms'   },
  { label: 'Refund Policy',  href: '/refunds' },
]

const SOCIAL_ICONS: Record<string, string> = {
  twitter:   `<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622 5.911-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>`,
  instagram: `<path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162S8.597 18.163 12 18.163s6.162-2.759 6.162-6.162S15.403 5.838 12 5.838zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>`,
  facebook:  `<path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>`,
  youtube:   `<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>`,
  tiktok:    `<path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>`,
  linkedin:  `<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>`,
}

const social = computed(() => portal.socialLinks)
</script>

<template>
  <footer class="border-t border-slate-800 bg-slate-900 text-slate-400">

    <!-- Trust strip -->
    <div class="border-b border-slate-800">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-6 px-4 py-5 sm:px-6 lg:px-8">
        <div class="flex items-center gap-2" aria-label="Rated 4.98 out of 5 on Trustpilot">
          <div class="flex gap-0.5" aria-hidden="true">
            <svg v-for="i in 5" :key="i" class="h-4 w-4 text-[#00b67a]" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
          <span class="text-sm font-semibold text-white">4.98/5</span>
          <span class="text-sm text-slate-500">on Trustpilot</span>
        </div>
        <span class="hidden text-slate-700 sm:block">·</span>
        <span class="text-sm"><strong class="text-white">9,800+</strong> nursing papers delivered</span>
        <span class="hidden text-slate-700 sm:block">·</span>
        <span class="text-sm">Grade or money back</span>
        <span class="hidden text-slate-700 sm:block">·</span>
        <span class="text-sm">BSN, MSN &amp; DNP writers · zero AI</span>
      </div>
    </div>

    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

      <!-- ── Row 1: Brand · Writing · Clinical · Specialty · Company ─────── -->
      <div class="grid gap-8 py-14 sm:grid-cols-2 lg:grid-cols-5">

        <!-- Brand -->
        <div class="space-y-4 sm:col-span-2 lg:col-span-1">
          <NuxtLink href="/" class="flex items-center gap-2">
            <svg width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <defs>
                <linearGradient id="nmg-vf" x1="16" y1="2" x2="16" y2="30" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#5eead4"/><stop offset="100%" stop-color="#0d9488"/>
                </linearGradient>
                <linearGradient id="nmg-hf" x1="2" y1="16" x2="30" y2="16" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#99f6e4"/><stop offset="100%" stop-color="#2dd4bf"/>
                </linearGradient>
              </defs>
              <rect x="12" y="2" width="8" height="28" rx="4" fill="url(#nmg-vf)"/>
              <rect x="2" y="12" width="28" height="8" rx="4" fill="url(#nmg-hf)" opacity="0.85"/>
            </svg>
            <span class="text-base font-bold leading-none tracking-tight">
              <span class="text-white">Nurse</span><span class="text-brand-400">MyGrade</span>
            </span>
          </NuxtLink>
          <p class="text-xs leading-relaxed text-slate-500">Expert nursing papers by BSN, MSN &amp; DNP nurses. NANDA, ADPIE, APA 7th — clinically accurate.</p>
          <div v-if="social.length" class="flex flex-wrap gap-1.5">
            <a v-for="s in social" :key="s.name" :href="s.href" :aria-label="s.name" target="_blank" rel="noreferrer"
              class="flex h-7 w-7 items-center justify-center rounded-md bg-slate-800 text-slate-400 transition-colors hover:bg-brand-700 hover:text-white">
              <svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24"><g v-html="SOCIAL_ICONS[s.icon] ?? ''" /></svg>
            </a>
          </div>
          <NuxtLink href="/order" class="inline-flex items-center gap-1.5 rounded-lg bg-brand-700 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand-800">
            Place an order →
          </NuxtLink>
        </div>

        <!-- Writing -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Writing</p>
          <ul class="space-y-2">
            <li v-for="s in writingServices" :key="s.href">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Clinical -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Clinical</p>
          <ul class="space-y-2">
            <li v-for="s in clinicalServices" :key="s.href">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Specialty -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Specialty</p>
          <ul class="space-y-2">
            <li v-for="s in specialtyServices" :key="s.href">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
          <NuxtLink href="/services" class="mt-3 block text-xs font-semibold text-brand-400 transition-colors hover:text-brand-300">All services →</NuxtLink>
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

      </div>

    </div>

    <NewsletterSignup />

    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

      <!-- ── Row 2: Quick Links · Resources · Free Tools · Legal ─────────── -->
      <div class="grid gap-8 border-t border-slate-800 py-10 sm:grid-cols-2 lg:grid-cols-4">

        <!-- Quick links / account -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Quick Links</p>
          <ul class="space-y-2">
            <li v-for="s in quickLinks" :key="s.href">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Resources / blog -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Resources</p>
          <ul class="space-y-2">
            <li v-for="s in resources" :key="s.href">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
            <li><NuxtLink href="/blog" class="text-xs font-semibold text-brand-400 hover:text-brand-300">Nursing Blog →</NuxtLink></li>
          </ul>
        </div>

        <!-- Free Tools -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Free Tools</p>
          <ul class="space-y-2">
            <li><NuxtLink href="/tools/citation-generator"   class="text-sm transition-colors hover:text-white">Citation Generator</NuxtLink></li>
            <li><NuxtLink href="/tools/thesis-generator"     class="text-sm transition-colors hover:text-white">Thesis Generator</NuxtLink></li>
            <li><NuxtLink href="/tools/outline-generator"    class="text-sm transition-colors hover:text-white">Outline Generator</NuxtLink></li>
            <li><NuxtLink href="/tools/title-page-generator" class="text-sm transition-colors hover:text-white">Title Page Generator</NuxtLink></li>
            <li><NuxtLink href="/tools/word-counter"         class="text-sm transition-colors hover:text-white">Word Counter</NuxtLink></li>
            <li><NuxtLink href="/tools/words-to-pages"       class="text-sm transition-colors hover:text-white">Words to Pages</NuxtLink></li>
            <li><NuxtLink href="/tools/gpa-calculator"       class="text-sm transition-colors hover:text-white">GPA Calculator</NuxtLink></li>
            <li><NuxtLink href="/tools/plagiarism-checker"      class="text-sm transition-colors hover:text-white">Plagiarism Checker</NuxtLink></li>
            <li><NuxtLink href="/tools/research-gap-identifier" class="text-sm transition-colors hover:text-white">Research Gap Identifier</NuxtLink></li>
          </ul>
          <NuxtLink href="/tools" class="mt-3 block text-xs font-semibold text-brand-400 hover:text-brand-300 transition-colors">All tools →</NuxtLink>
        </div>

        <!-- Legal + guarantees -->
        <div>
          <p class="mb-4 text-[10px] font-bold uppercase tracking-widest text-brand-400">Legal</p>
          <ul class="space-y-2">
            <li v-for="s in legal" :key="s.href">
              <NuxtLink :href="s.href" class="text-sm transition-colors hover:text-white">{{ s.label }}</NuxtLink>
            </li>
          </ul>
          <div class="mt-5 space-y-1.5 text-xs text-slate-500">
            <p class="flex items-center gap-2"><span class="text-brand-400">✓</span> Grade or money back</p>
            <p class="flex items-center gap-2"><span class="text-brand-400">✓</span> Zero AI content</p>
            <p class="flex items-center gap-2"><span class="text-brand-400">✓</span> Free Turnitin report</p>
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
