<script setup lang="ts">
const app  = useAppUrl()
const year = new Date().getFullYear()

// Nav already covers: Essays, Research Papers, Dissertations, Nursing, Online Class, Editing
// Footer carries the long-tail and advanced services
const services = [
  { label: 'Essay Writing',        href: '/services/essay-writing'       },
  { label: 'Research Papers',      href: '/services/research-papers'     },
  { label: 'Term Papers',          href: '/services/term-papers'         },
  { label: 'Case Studies',         href: '/services/case-studies'        },
  { label: 'Literature Reviews',   href: '/services/literature-review'   },
  { label: 'Dissertations',        href: '/services/dissertations'       },
  { label: 'Thesis Writing',       href: '/services/thesis-writing'      },
  { label: 'Capstone Projects',    href: '/services/capstone-projects'   },
  { label: 'Data Analysis',        href: '/services/data-analysis'       },
  { label: 'Nursing Essays',       href: '/services/nursing-essays'      },
  { label: 'Admission Essays',     href: '/services/admission-essays'    },
  { label: 'Coursework Help',      href: '/services/coursework'          },
  { label: 'Online Class Help',    href: '/services/online-class-help'   },
  { label: 'Homework Help',        href: '/services/homework-help'       },
  { label: 'Editing & Proofread',  href: '/services/editing-proofreading'},
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

    <!-- Main grid -->
    <div class="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div class="grid gap-10 lg:grid-cols-4">

        <!-- Brand col -->
        <div class="space-y-5 lg:col-span-1">
          <NuxtLink to="/" class="flex items-center gap-2 text-lg font-bold text-white">
            <span class="flex size-8 items-center justify-center rounded-lg bg-gc-600 text-sm font-extrabold text-white">G</span>
            GradeCrest
          </NuxtLink>
          <p class="max-w-xs text-sm leading-relaxed text-slate-400">
            Human-written academic papers across every subject and level. Grade or money back — no conditions.
          </p>
          <div class="flex items-center gap-1.5 text-xs text-slate-500">
            <span class="flex size-2 rounded-full bg-gc-400" />
            Zero AI content · 50,000+ papers delivered
          </div>
          <div class="flex flex-wrap items-center gap-2 pt-1">
            <span v-for="pm in ['Visa', 'MC', 'AmEx', 'PayPal']" :key="pm"
              class="rounded border border-white/10 bg-white/5 px-2 py-0.5 text-xs font-medium text-slate-400">
              {{ pm }}
            </span>
          </div>
          <!-- Order CTA -->
          <NuxtLink to="/order"
            class="inline-flex items-center gap-2 rounded-lg bg-gc-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-gc-700">
            Place an order →
          </NuxtLink>
        </div>

        <!-- Services — two columns -->
        <div class="lg:col-span-2">
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Services</p>
          <div class="grid grid-cols-2 gap-x-8 gap-y-2">
            <NuxtLink
              v-for="item in services" :key="item.href"
              :to="item.href"
              class="text-sm transition-colors hover:text-white"
            >{{ item.label }}</NuxtLink>
          </div>
          <NuxtLink to="/services" class="mt-4 block text-xs font-semibold text-gold-400 hover:text-gold-300 transition-colors">
            View all services →
          </NuxtLink>
        </div>

        <!-- Company + Account + Legal -->
        <div class="space-y-8">
          <div>
            <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Company</p>
            <ul class="space-y-2">
              <li v-for="item in company" :key="item.href">
                <NuxtLink :to="item.href" class="text-sm transition-colors hover:text-white">{{ item.label }}</NuxtLink>
              </li>
            </ul>
          </div>
          <div>
            <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Account</p>
            <ul class="space-y-2">
              <li><a :href="app.login"    class="text-sm transition-colors hover:text-white">Sign in</a></li>
              <li><a :href="app.register" class="text-sm transition-colors hover:text-white">Create account</a></li>
              <li><NuxtLink to="/order"   class="text-sm transition-colors hover:text-white">Place an order</NuxtLink></li>
            </ul>
          </div>
          <div>
            <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-gold-400">Legal</p>
            <ul class="space-y-2">
              <li v-for="item in legal" :key="item.href">
                <NuxtLink :to="item.href" class="text-sm transition-colors hover:text-white">{{ item.label }}</NuxtLink>
              </li>
            </ul>
          </div>
        </div>

      </div>
    </div>

    <!-- Bottom bar -->
    <div class="border-t border-white/10">
      <div class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-4 py-5 text-xs text-slate-500 sm:flex-row sm:px-6 lg:px-8">
        <p>© {{ year }} GradeCrest. All rights reserved.</p>
        <p class="text-center">
          GradeCrest provides model academic papers for reference and learning purposes only.
        </p>
      </div>
    </div>

  </footer>
</template>
