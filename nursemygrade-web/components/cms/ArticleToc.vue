<script setup lang="ts">
interface TocItem { id: string; text: string; level: string }

const props = withDefaults(defineProps<{
  items: TocItem[]
  variant?: 'progress' | 'cards' | 'pills'
}>(), { variant: 'progress' })

const open   = ref(true)
const active = ref('')
let obs: IntersectionObserver | null = null

onMounted(() => {
  open.value = window.innerWidth >= 768
  obs = new IntersectionObserver(
    entries => { for (const e of entries) if (e.isIntersecting) active.value = e.target.id },
    { rootMargin: '-20% 0px -70% 0px' },
  )
  nextTick(() => {
    props.items.forEach(({ id }) => {
      const el = document.getElementById(id)
      if (el) obs?.observe(el)
    })
  })
})
onUnmounted(() => obs?.disconnect())

const h2Items   = computed(() => props.items.filter(i => i.level !== 'h3'))
const activeIdx = computed(() => props.items.findIndex(i => i.id === active.value))
const progressPct = computed(() => {
  if (activeIdx.value < 0) return 0
  return Math.round(((activeIdx.value + 1) / props.items.length) * 100)
})

function rowState(idx: number): 'active' | 'past' | 'upcoming' {
  if (activeIdx.value < 0 || idx > activeIdx.value) return 'upcoming'
  if (idx === activeIdx.value) return 'active'
  return 'past'
}

// Pre-compute h2 sequential numbers (h3s reuse their parent's number)
const h2Numbers = computed(() => {
  let n = 0
  return props.items.map(item => (item.level !== 'h3' ? ++n : n))
})
</script>

<template>
  <!-- ── Variant: progress ──────────────────────────────────────────────── -->
  <nav v-if="variant === 'progress'"
    class="mt-8 overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-sm not-prose"
    aria-label="Table of contents">

    <!-- Top read-progress stripe -->
    <div class="h-1 bg-slate-100" role="progressbar" :aria-valuenow="progressPct" aria-valuemin="0" aria-valuemax="100">
      <div class="h-full bg-gradient-to-r from-brand-400 to-brand-600 transition-[width] duration-500 ease-out"
           :style="{ width: progressPct + '%' }" />
    </div>

    <!-- Header -->
    <button
      class="flex w-full items-center justify-between px-5 py-3.5 text-left transition-colors hover:bg-slate-50/80"
      :aria-expanded="open"
      @click="open = !open"
    >
      <span class="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-slate-500">
        <svg class="h-3.5 w-3.5 shrink-0 text-brand-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h10"/>
        </svg>
        In this article
        <span class="rounded-full bg-slate-100 px-1.5 py-0.5 text-[10px] font-bold text-slate-500 ml-0.5">
          {{ h2Items.length }}
        </span>
      </span>
      <span class="text-[11px] font-medium text-slate-400 transition-colors hover:text-slate-600">
        {{ open ? 'hide' : 'show' }}
      </span>
    </button>

    <!-- Rows -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <ol v-if="open" class="border-t border-slate-100">
        <li v-for="(item, idx) in items" :key="item.id">
          <a
            :href="`#${item.id}`"
            class="group flex items-stretch text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand-500"
            :class="rowState(idx) === 'active' ? 'bg-brand-50/70' : 'hover:bg-slate-50'"
            @click="open = false"
          >
            <!-- Left progress strip -->
            <span class="w-1 shrink-0 transition-colors duration-300"
              :class="{
                'bg-brand-500': rowState(idx) === 'active',
                'bg-brand-200': rowState(idx) === 'past',
                'bg-transparent': rowState(idx) === 'upcoming',
              }" />

            <!-- Row content -->
            <span class="flex flex-1 items-center gap-3 py-2.5 pr-4"
              :class="item.level === 'h3' ? 'pl-10' : 'pl-4'">

              <!-- Number (h2) or sub-bullet (h3) -->
              <span v-if="item.level !== 'h3'"
                class="w-5 shrink-0 text-[11px] font-black tabular-nums leading-none transition-colors"
                :class="{
                  'text-brand-500': rowState(idx) === 'active',
                  'text-slate-200': rowState(idx) === 'past',
                  'text-slate-300': rowState(idx) === 'upcoming',
                }"
              >{{ String(h2Numbers[idx]).padStart(2, '0') }}</span>
              <span v-else class="flex w-5 shrink-0 justify-center">
                <span class="h-1 w-1 rounded-full"
                  :class="rowState(idx) === 'active' ? 'bg-brand-400' : 'bg-slate-200'" />
              </span>

              <!-- Title -->
              <span class="leading-snug transition-colors"
                :class="{
                  'font-semibold text-brand-700': rowState(idx) === 'active',
                  'text-slate-400': rowState(idx) === 'past',
                  'text-slate-600 group-hover:text-slate-800': rowState(idx) === 'upcoming',
                }"
              >{{ item.text }}</span>

              <!-- Active arrow -->
              <svg v-if="rowState(idx) === 'active'"
                class="ml-auto size-3.5 shrink-0 text-brand-400"
                fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
              </svg>
            </span>
          </a>
        </li>
      </ol>
    </Transition>
  </nav>

  <!-- ── Variant: cards ─────────────────────────────────────────────────── -->
  <nav v-else-if="variant === 'cards'"
    class="mt-8 overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-sm not-prose"
    aria-label="Table of contents">

    <button
      class="flex w-full items-center justify-between border-b border-slate-100 bg-slate-50 px-5 py-3.5 text-left transition-colors hover:bg-slate-100/60"
      :aria-expanded="open"
      @click="open = !open"
    >
      <span class="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-slate-500">
        <svg class="h-3.5 w-3.5 shrink-0 text-brand-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h10"/>
        </svg>
        In this article
      </span>
      <svg class="h-4 w-4 text-slate-400 transition-transform duration-200" :class="open ? 'rotate-180' : ''"
        fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="open" class="grid grid-cols-2 gap-px bg-slate-100">
        <a
          v-for="(item, idx) in h2Items" :key="item.id"
          :href="`#${item.id}`"
          class="group flex flex-col gap-1.5 bg-white px-5 py-4 transition-colors hover:bg-brand-50/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand-500"
          :class="active === item.id ? 'bg-brand-50/60' : ''"
          @click="open = false"
        >
          <span class="text-[22px] font-black tabular-nums leading-none select-none transition-colors"
            :class="active === item.id ? 'text-brand-200' : 'text-slate-100 group-hover:text-brand-100'">
            {{ String(idx + 1).padStart(2, '0') }}
          </span>
          <span class="text-xs font-semibold leading-snug transition-colors"
            :class="active === item.id ? 'text-brand-700' : 'text-slate-600 group-hover:text-brand-600'">
            {{ item.text }}
          </span>
          <span class="h-0.5 w-5 rounded-full transition-colors"
            :class="active === item.id ? 'bg-brand-500' : 'bg-transparent group-hover:bg-brand-200'" />
        </a>
      </div>
    </Transition>
  </nav>

  <!-- ── Variant: pills ─────────────────────────────────────────────────── -->
  <div v-else-if="variant === 'pills'"
    class="mt-8 not-prose"
    role="navigation"
    aria-label="Table of contents">
    <div class="flex flex-wrap items-center gap-1.5">
      <span class="mr-1 text-[11px] font-bold uppercase tracking-widest text-slate-400">Jump to:</span>
      <a
        v-for="item in h2Items" :key="item.id"
        :href="`#${item.id}`"
        class="rounded-full border px-3 py-1 text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
        :class="active === item.id
          ? 'border-brand-500 bg-brand-500 text-white shadow-sm'
          : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700'"
      >{{ item.text }}</a>
    </div>
  </div>
</template>
