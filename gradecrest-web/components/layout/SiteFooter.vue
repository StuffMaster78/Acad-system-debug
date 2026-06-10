<script setup lang="ts">
const app = useAppUrl()
const year = new Date().getFullYear()

const services = [
  { label: 'Essay Writing',      href: '/services/essay-writing'       },
  { label: 'Research Papers',    href: '/services/research-papers'     },
  { label: 'Dissertations',      href: '/services/dissertations'       },
  { label: 'Nursing Essays',     href: '/services/nursing-essays'      },
  { label: 'Admission Essays',   href: '/services/admission-essays'    },
  { label: 'Editing & Proofread',href: '/services/editing-proofreading'},
  { label: 'Coursework Help',    href: '/services/coursework'          },
  { label: 'Online Class Help',  href: '/services/online-class-help'   },
  { label: 'Data Analysis',      href: '/services/data-analysis'       },
]

const company = [
  { label: 'About Us',      href: '/about'         },
  { label: 'How It Works',  href: '/how-it-works'  },
  { label: 'Our Writers',   href: '/writers'       },
  { label: 'Reviews',       href: '/reviews'       },
  { label: 'Pricing',       href: '/pricing'       },
  { label: 'Blog',          href: '/blog'          },
  { label: 'Become a Writer',href: '/apply'        },
  { label: 'FAQ',           href: '/faq'           },
  { label: 'Contact Us',    href: '/contact'       },
]

const legal = [
  { label: 'Terms of Service',href: '/legal/terms'   },
  { label: 'Privacy Policy', href: '/legal/privacy'  },
  { label: 'Refund Policy',  href: '/legal/refunds'  },
]
</script>

<template>
  <footer class="border-t border-slate-200 bg-slate-950 text-slate-400">

    <!-- Main grid -->
    <div class="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
      <div class="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">

        <!-- Brand -->
        <div class="space-y-4">
          <NuxtLink to="/" class="flex items-center gap-2 font-bold text-white text-lg">
            <span class="flex size-8 items-center justify-center rounded-lg bg-gc-600 text-white text-sm font-extrabold">G</span>
            GradeCrest
          </NuxtLink>
          <p class="text-sm leading-relaxed text-slate-400 max-w-xs">
            Human-written academic papers across every subject and level. Grade or money back guarantee.
          </p>
          <div class="flex items-center gap-1.5 text-xs text-slate-500">
            <span class="flex size-2 rounded-full bg-emerald-500" />
            <span>Zero AI content</span>
          </div>
          <!-- Payment logos placeholder -->
          <div class="flex flex-wrap items-center gap-2 pt-1">
            <span v-for="pm in ['Visa', 'MC', 'AmEx', 'PayPal']" :key="pm"
              class="rounded border border-slate-700 bg-slate-800 px-2 py-0.5 text-xs font-medium text-slate-400">
              {{ pm }}
            </span>
          </div>
        </div>

        <!-- Services -->
        <div>
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-300">Services</p>
          <ul class="space-y-2">
            <li v-for="item in services" :key="item.href">
              <NuxtLink :to="item.href" class="text-sm hover:text-white transition-colors">{{ item.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Company -->
        <div>
          <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-300">Company</p>
          <ul class="space-y-2">
            <li v-for="item in company" :key="item.href">
              <NuxtLink :to="item.href" class="text-sm hover:text-white transition-colors">{{ item.label }}</NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Account + Legal -->
        <div class="space-y-8">
          <div>
            <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-300">Account</p>
            <ul class="space-y-2">
              <li><a :href="app.login"    class="text-sm hover:text-white transition-colors">Sign in</a></li>
              <li><a :href="app.register" class="text-sm hover:text-white transition-colors">Create account</a></li>
              <li><a :href="app.order"    class="text-sm hover:text-white transition-colors">Place an order</a></li>
            </ul>
          </div>
          <div>
            <p class="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-300">Legal</p>
            <ul class="space-y-2">
              <li v-for="item in legal" :key="item.href">
                <NuxtLink :to="item.href" class="text-sm hover:text-white transition-colors">{{ item.label }}</NuxtLink>
              </li>
            </ul>
          </div>
        </div>

      </div>
    </div>

    <!-- Bottom bar -->
    <div class="border-t border-slate-800">
      <div class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-4 py-5 text-xs text-slate-500 sm:flex-row sm:px-6 lg:px-8">
        <p>© {{ year }} GradeCrest. All rights reserved.</p>
        <p class="text-center">
          GradeCrest provides model academic papers for reference and learning purposes only.
        </p>
      </div>
    </div>

  </footer>
</template>
