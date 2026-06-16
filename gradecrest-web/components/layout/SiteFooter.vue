<script setup lang="ts">
const app  = useAppUrl()
const year = new Date().getFullYear()

const writingServices = [
  { label: 'Essay Writing',       href: '/services/essay-writing'       },
  { label: 'Research Papers',     href: '/services/research-papers'     },
  { label: 'Term Papers',         href: '/services/term-papers'         },
  { label: 'Case Studies',        href: '/services/case-studies'        },
  { label: 'Literature Reviews',  href: '/services/literature-review'   },
  { label: 'Coursework Help',     href: '/services/coursework'          },
  { label: 'Online Class Help',   href: '/services/online-class-help'   },
  { label: 'Homework Help',       href: '/services/homework-help'       },
]

const advancedServices = [
  { label: 'Dissertations',       href: '/services/dissertations'       },
  { label: 'Thesis Writing',      href: '/services/thesis-writing'      },
  { label: 'Capstone Projects',   href: '/services/capstone-projects'   },
  { label: 'Data Analysis',       href: '/services/data-analysis'       },
  { label: 'Nursing Essays',      href: '/services/nursing-essays'      },
  { label: 'Admission Essays',    href: '/services/admission-essays'    },
  { label: 'Editing & Proofread', href: '/services/editing-proofreading'},
]

const company = [
  { label: 'About Us',        href: '/about'        },
  { label: 'How It Works',    href: '/how-it-works' },
  { label: 'Our Writers',     href: '/writers'      },
  { label: 'Reviews',         href: '/reviews'      },
  { label: 'Pricing',         href: '/pricing'      },
  { label: 'Blog',            href: '/blog'         },
  { label: 'Become a Writer', href: '/apply'        },
  { label: 'FAQ',             href: '/faq'          },
  { label: 'Contact Us',      href: '/contact'      },
]

const legal = [
  { label: 'Terms of Service', href: '/legal/terms'   },
  { label: 'Privacy Policy',   href: '/legal/privacy' },
  { label: 'Refund Policy',    href: '/legal/refunds' },
]
</script>

<template>
  <footer class="border-t border-slate-800 bg-forest-950 text-slate-400">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

      <!-- ── Row 1: Brand · Writing · Advanced · Company ─────────────────── -->
      <div class="grid gap-10 py-14 lg:grid-cols-4">

        <!-- Brand -->
        <div class="space-y-5">
          <NuxtLink to="/" class="flex items-center gap-2 text-lg font-bold text-white">
            <span class="flex size-8 items-center justify-center rounded-lg bg-gc-600 text-sm font-extrabold text-white">G</span>
            GradeCrest
          </NuxtLink>
          <p class="max-w-xs text-sm leading-relaxed text-slate-400">
            Human-written academic papers across every subject and level. Grade or money back — no conditions.
          </p>
          <div class="flex items-center gap-1.5 text-xs text-slate-500">
            <span class="size-2 rounded-full bg-gc-400" />
            Zero AI · 50,000+ papers delivered
          </div>
          <NuxtLink to="/order"
            class="inline-flex items-center gap-2 rounded-lg bg-gc-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-gc-700">
            Place an order →
          </NuxtLink>
        </div>

        <!-- Writing services -->
        <div>
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Writing</p>
          <ul class="space-y-2">
            <li v-for="item in writingServices" :key="item.href">
              <NuxtLink :to="item.href" class="text-sm transition-colors hover:text-white">{{ item.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Advanced & specialist services -->
        <div>
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Advanced & Specialist</p>
          <ul class="space-y-2">
            <li v-for="item in advancedServices" :key="item.href">
              <NuxtLink :to="item.href" class="text-sm transition-colors hover:text-white">{{ item.label }}</NuxtLink>
            </li>
          </ul>
          <NuxtLink to="/services" class="mt-4 block text-xs font-semibold text-gold-400 transition-colors hover:text-gold-300">
            All services →
          </NuxtLink>
        </div>

        <!-- Company -->
        <div>
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Company</p>
          <ul class="space-y-2">
            <li v-for="item in company" :key="item.href">
              <NuxtLink :to="item.href" class="text-sm transition-colors hover:text-white">{{ item.label }}</NuxtLink>
            </li>
          </ul>
        </div>

      </div>

      <!-- ── Row 2: Account · Legal · Trust ──────────────────────────────── -->
      <div class="grid gap-8 border-t border-white/10 py-10 sm:grid-cols-3">

        <!-- Account -->
        <div>
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Account</p>
          <ul class="space-y-2">
            <li><a :href="app.login"    class="text-sm transition-colors hover:text-white">Sign in</a></li>
            <li><a :href="app.register" class="text-sm transition-colors hover:text-white">Create account</a></li>
            <li><NuxtLink to="/order"   class="text-sm transition-colors hover:text-white">Place an order</NuxtLink></li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Legal</p>
          <ul class="space-y-2">
            <li v-for="item in legal" :key="item.href">
              <NuxtLink :to="item.href" class="text-sm transition-colors hover:text-white">{{ item.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Trust & payments -->
        <div>
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">We guarantee</p>
          <ul class="space-y-2 text-sm">
            <li class="flex items-center gap-2"><span class="text-gold-400">★</span> Grade or money back</li>
            <li class="flex items-center gap-2"><span class="text-gc-400">✓</span> Zero AI content</li>
            <li class="flex items-center gap-2"><span class="text-gc-400">✓</span> Free plagiarism report</li>
            <li class="flex items-center gap-2"><span class="text-gc-400">✓</span> 100% confidential</li>
          </ul>
          <div class="mt-5 flex flex-wrap gap-2">
            <span v-for="pm in ['Visa', 'MC', 'AmEx', 'PayPal']" :key="pm"
              class="rounded border border-white/10 bg-white/5 px-2 py-0.5 text-xs font-medium text-slate-400">
              {{ pm }}
            </span>
          </div>
        </div>

      </div>

    </div>

    <!-- Bottom bar -->
    <div class="border-t border-white/10">
      <div class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-4 py-5 text-xs text-slate-500 sm:flex-row sm:px-6 lg:px-8">
        <p>© {{ year }} GradeCrest. All rights reserved.</p>
        <p class="text-center">GradeCrest provides model academic papers for reference and learning purposes only.</p>
      </div>
    </div>

  </footer>
</template>
