<script setup lang="ts">
const config = useRuntimeConfig()

// SSR-safe API base (same pattern used throughout the codebase)
const apiBase = import.meta.server
  ? ((config as Record<string, unknown>).apiBaseInternal as string || 'http://localhost:8000')
  : (config.public.apiBase || '')
const siteHost = import.meta.server
  ? { Host: (config.siteHostname as string) || 'nursemygrade.com' }
  : undefined

interface CmsServicePage {
  id: number
  title: string
  meta: { slug: string; seo_title: string; search_description: string }
  hero_image?: { url: string } | null
  thumbnail?: { url: string } | null
  body: Array<{ type: string; value: unknown }>
}

const { data: cmsPage } = await useAsyncData<CmsServicePage | null>(
  'nmg-ihuman-patients-cms',
  async () => {
    try {
      const res = await $fetch<{ items: CmsServicePage[] }>(
        `${apiBase}/api/v2/pages/`,
        {
          params: { type: 'cms_service_pages.ServicePage', slug: 'ihuman-patients', fields: '*' },
          headers: siteHost,
        },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

// ── iHuman order form state ───────────────────────────────────────────────────
const auth = useRpmAuthStore()

const CASE_TYPES = [
  { id: 'full_encounter',     label: 'Full patient encounter',   desc: 'History, physical, assessment & plan' },
  { id: 'soap_note',          label: 'SOAP note only',           desc: 'Structured clinical documentation' },
  { id: 'differential_dx',    label: 'Differential diagnosis',   desc: 'DDx list with clinical reasoning' },
  { id: 'chief_complaint',    label: 'Chief complaint analysis', desc: 'HPI and initial assessment' },
  { id: 'full_case_and_soap', label: 'Full case + SOAP',         desc: 'Everything end-to-end' },
]

const BODY_SYSTEMS = [
  'Cardiovascular', 'Respiratory / Pulmonary', 'Neurological',
  'Gastrointestinal', 'Musculoskeletal', 'Renal / Genitourinary',
  'Endocrine / Metabolic', 'Hematology / Oncology',
  'Infectious Disease', 'Psychiatric / Mental Health', "OB / Women's Health",
  'Pediatrics', 'Other / Mixed',
]

const DIFFICULTY = [
  { id: 'beginner',     label: 'Beginner',     desc: 'First or second year' },
  { id: 'intermediate', label: 'Intermediate', desc: 'Upper-division BSN / ADN' },
  { id: 'advanced',     label: 'Advanced',     desc: 'MSN, NP, or DNP' },
]

const DEADLINES = [
  { id: '3h',  label: '3 hours'  },
  { id: '6h',  label: '6 hours'  },
  { id: '12h', label: '12 hours' },
  { id: '24h', label: '24 hours' },
  { id: '48h', label: '2 days'   },
  { id: '72h', label: '3 days'   },
  { id: '7d',  label: '7 days'   },
]

const FAQS = [
  { q: 'What is iHuman?', a: 'iHuman is a clinical simulation platform used in nursing and NP programs. Students complete virtual patient encounters covering history-taking, physical examination, differential diagnosis, assessment, and care planning.' },
  { q: 'Do you complete the actual iHuman case on the platform?', a: 'Yes, for full encounter orders. For documentation-only orders (SOAP note, DDx write-up) we provide the completed documents — you enter them.' },
  { q: 'How fast can you complete an iHuman case?', a: 'As fast as 3 hours for a standard single encounter. Complex multi-system cases may take 6–12 hours. Select your deadline when ordering.' },
  { q: 'Do I need to share my iHuman login?', a: 'Only for full encounter completion. For documentation tasks we only need the case details — chief complaint, patient demographics, and your rubric.' },
  { q: 'What if my case spans multiple body systems?', a: "Select \"Other / Mixed\" and describe the systems in the platform notes field. We'll match a writer with cross-system experience." },
]

const step        = ref(1)
const submitted   = ref(false)
const submitting  = ref(false)
const serverError = ref<string | null>(null)

const form = reactive({
  caseType:      CASE_TYPES[0],
  caseTitle:     '',
  bodySystem:    '',
  difficulty:    DIFFICULTY[1],
  numberOfCases: 1,
  deadline:      DEADLINES[3],
  platformNotes: '',
  firstName: '', lastName: '', email: '', password: '', agreeToTerms: false,
})

const step1Valid = computed(() =>
  form.caseType.id.length > 0 && form.bodySystem.length > 0 && form.deadline.id.length > 0
)
const step2Valid = computed(() =>
  form.firstName.trim().length > 0 && form.email.includes('@') && form.password.length >= 8 && form.agreeToTerms
)

function savePending() {
  if (!import.meta.client) return
  localStorage.setItem('nmg_pending_ihuman_order', JSON.stringify({
    type: 'ihuman_case',
    caseType: form.caseType.label,
    caseTitle: form.caseTitle,
    bodySystem: form.bodySystem,
    difficulty: form.difficulty.label,
    numberOfCases: form.numberOfCases,
    deadline: form.deadline.label,
    platformNotes: form.platformNotes,
    savedAt: new Date().toISOString(),
  }))
}

async function submit() {
  submitting.value = true; serverError.value = null
  try {
    savePending()
    await auth.register({ email: form.email, password: form.password, first_name: form.firstName, last_name: form.lastName })
    submitted.value = true
  } catch { serverError.value = auth.error || 'Something went wrong. Please try again.' }
  finally { submitting.value = false }
}

// ── SEO ───────────────────────────────────────────────────────────────────────
const siteUrl      = config.public.siteUrl || 'https://nursemygrade.com'
const canonicalUrl = `${siteUrl}/ihuman-patients`

const seoTitle = computed(() => cmsPage.value?.meta?.seo_title || 'iHuman Virtual Patient Case Help | NurseMyGrade')
const seoDesc  = computed(() => cmsPage.value?.meta?.search_description || 'Expert nursing help for iHuman virtual patient cases. Full encounter completion, SOAP notes, differential diagnosis, and clinical reasoning — by real nurses.')

useSeoMeta({
  title: seoTitle, description: seoDesc, ogTitle: seoTitle, ogDescription: seoDesc,
  ogImage: computed(() => cmsPage.value?.thumbnail?.url ?? `${siteUrl}/og-default.png`),
  ogType: 'website', ogImageWidth: 1200, ogImageHeight: 630, twitterCard: 'summary_large_image',
})

useHead({
  link: [{ rel: 'canonical', href: canonicalUrl }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: 'Home', item: `${siteUrl}/` },
          { '@type': 'ListItem', position: 2, name: 'Services', item: `${siteUrl}/services` },
          { '@type': 'ListItem', position: 3, name: 'iHuman Virtual Patient Help', item: canonicalUrl },
        ],
      }),
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: [
          { '@type': 'Question', name: 'What is iHuman?', acceptedAnswer: { '@type': 'Answer', text: 'iHuman is a clinical simulation platform used in nursing and NP programs for virtual patient encounters covering history-taking, physical examination, differential diagnosis, assessment, and care planning.' } },
          { '@type': 'Question', name: 'Can you complete my entire iHuman case?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. Our clinically trained nurses complete every section — chief complaint and HPI through the full assessment, diagnosis, and SOAP note.' } },
          { '@type': 'Question', name: 'How fast can you complete an iHuman case?', acceptedAnswer: { '@type': 'Answer', text: 'As fast as 3 hours for a standard single-encounter case. Most cases are matched within minutes of account confirmation.' } },
          { '@type': 'Question', name: 'Do I need to share my iHuman login?', acceptedAnswer: { '@type': 'Answer', text: 'For full encounter completion (where we log in for you), yes. For documentation tasks like SOAP notes or differential diagnosis, we only need the case details.' } },
        ],
      }),
    },
  ],
})
</script>

<template>
  <!-- ── Success ───────────────────────────────────────────────────────────── -->
  <div v-if="submitted" class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-16">
    <div class="w-full max-w-lg text-center">
      <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-brand-100">
        <Icon name="check" class="h-10 w-10 text-brand-600" />
      </div>
      <h1 class="font-serif text-3xl font-bold text-slate-900">iHuman case request received!</h1>
      <p class="mt-4 text-slate-600 leading-relaxed">
        We've sent a confirmation link to <strong>{{ form.email }}</strong>.
        A clinically trained nurse will be matched to your case within 30 minutes of email confirmation.
      </p>
      <div class="mt-6 rounded-2xl border border-brand-100 bg-brand-50 p-5 text-sm text-left">
        <p class="font-semibold text-brand-800 mb-2">Your case summary</p>
        <dl class="space-y-1.5">
          <div class="flex justify-between"><dt class="text-slate-500">Case type</dt><dd class="font-medium">{{ form.caseType.label }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">Body system</dt><dd class="font-medium">{{ form.bodySystem }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">Level</dt><dd class="font-medium">{{ form.difficulty.label }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">Cases</dt><dd class="font-medium">{{ form.numberOfCases }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">Deadline</dt><dd class="font-medium">{{ form.deadline.label }}</dd></div>
        </dl>
      </div>
    </div>
  </div>

  <!-- ── Main page ─────────────────────────────────────────────────────────── -->
  <div v-else>

    <!-- Hero -->
    <div class="bg-gradient-to-br from-brand-900 via-brand-800 to-brand-700 py-14 text-center">
      <div class="mx-auto max-w-3xl px-4">
        <div class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-3xl">🩺</div>
        <h1 class="font-serif text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
          {{ cmsPage?.title || 'iHuman Virtual Patient Case Help' }}
        </h1>
        <p class="mx-auto mt-4 max-w-2xl text-brand-100 leading-relaxed">
          Full iHuman case completion by a clinically trained nursing expert — chief complaint, physical exam, differential diagnosis, SOAP note, and plan — matched to your rubric.
        </p>
        <div class="mt-6 flex flex-wrap justify-center gap-5 text-sm text-brand-200">
          <span class="flex items-center gap-1.5"><Icon name="clock" class="h-4 w-4" /> As fast as 3 hours</span>
          <span class="flex items-center gap-1.5"><Icon name="shield" class="h-4 w-4" /> 100% confidential</span>
          <span class="flex items-center gap-1.5"><Icon name="star" class="h-4 w-4" /> BSN, MSN, NP-qualified</span>
          <span class="flex items-center gap-1.5"><Icon name="refresh-cw" class="h-4 w-4" /> Free revisions included</span>
        </div>
      </div>
    </div>

    <!-- Two-column: content left | sticky form right -->
    <div class="bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div class="lg:grid lg:grid-cols-3 lg:gap-12 xl:gap-16">

          <!-- Left 2/3 -->
          <article class="lg:col-span-2 space-y-12 min-w-0" aria-label="iHuman service details">

            <!-- CMS body when Wagtail content is published -->
            <template v-if="cmsPage?.body?.length">
              <BlockRenderer :blocks="cmsPage.body" />
            </template>

            <!-- Static fallback -->
            <template v-else>

              <section aria-labelledby="what-heading">
                <h2 id="what-heading" class="font-serif text-xl font-bold text-brand-900 mb-4">What is iHuman?</h2>
                <p class="text-slate-600 leading-relaxed">
                  iHuman is the clinical simulation platform used by hundreds of nursing and NP programs across the US.
                  Each case presents a virtual patient with a realistic chief complaint. Students must complete a thorough
                  history, physical examination, order workup, establish a differential diagnosis, and formulate an
                  evidence-based plan — all scored against a detailed rubric.
                </p>
              </section>

              <section aria-labelledby="complete-heading">
                <h2 id="complete-heading" class="font-serif text-xl font-bold text-brand-900 mb-5">What we complete for you</h2>
                <div class="grid gap-3 sm:grid-cols-2">
                  <div v-for="(item, i) in [
                    'Full virtual patient encounter — history, physical, workup, assessment & plan',
                    'SOAP note written to your program\'s exact format',
                    'Differential diagnosis list with evidence-based clinical reasoning for each entry',
                    'Chief complaint and HPI write-up (opening encounter documentation)',
                    'Nursing diagnosis in NANDA-I format with supporting evidence',
                    'iHuman scoring rubric matched — every required field completed',
                  ]" :key="item" class="flex items-start gap-3 rounded-xl border border-brand-100 bg-brand-50/60 p-4">
                    <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-[11px] font-bold text-white">{{ i + 1 }}</span>
                    <span class="text-sm text-slate-700 leading-relaxed">{{ item }}</span>
                  </div>
                </div>
              </section>

              <section aria-labelledby="systems-heading">
                <h2 id="systems-heading" class="font-serif text-xl font-bold text-brand-900 mb-4">Body systems we cover</h2>
                <p class="mb-4 text-slate-600 leading-relaxed">Our nurses are matched to your case by speciality. We cover all major systems tested in iHuman:</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="s in BODY_SYSTEMS" :key="s"
                    class="rounded-full border border-brand-200 bg-brand-50 px-3.5 py-1.5 text-sm font-medium text-brand-700">
                    {{ s }}
                  </span>
                </div>
              </section>

              <section aria-labelledby="how-heading">
                <h2 id="how-heading" class="font-serif text-xl font-bold text-brand-900 mb-5">How it works</h2>
                <ol class="relative border-l border-brand-200 ml-3 space-y-0">
                  <li v-for="(s, idx) in [
                    { title: 'Submit your case details', desc: 'Select case type, body system, academic level, and deadline. Add any rubric notes or platform access info.' },
                    { title: 'Confirm your account', desc: 'Click the link in your confirmation email. Your case is held in queue — a nurse is matched within 30 minutes.' },
                    { title: 'Nurse completes your case', desc: 'A clinically trained writer completes every section of your iHuman encounter, matching your rubric exactly.' },
                    { title: 'Review and request revisions', desc: 'Receive the completed documentation. Request free revisions if anything needs adjusting — always by your original writer.' },
                  ]" :key="idx" class="mb-8 ml-6 last:mb-0">
                    <span class="absolute -left-3 flex size-6 items-center justify-center rounded-full bg-brand-600 ring-4 ring-white text-[10px] font-bold text-white">{{ idx + 1 }}</span>
                    <p class="font-semibold text-slate-900 text-sm">{{ s.title }}</p>
                    <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ s.desc }}</p>
                  </li>
                </ol>
              </section>

              <section aria-labelledby="guarantees-heading">
                <h2 id="guarantees-heading" class="font-serif text-xl font-bold text-brand-900 mb-5">Our guarantees</h2>
                <div class="grid gap-3 sm:grid-cols-2">
                  <div v-for="g in [
                    { icon: 'trophy',       title: 'Grade or money back',      desc: 'Full refund if the work doesn\'t meet your stated requirements after revisions.' },
                    { icon: 'stethoscope',  title: 'Real clinical nurses',     desc: 'BSN minimum, MSN and NP writers available for advanced cases. All credentials verified.' },
                    { icon: 'shield-check', title: 'Rubric-matched delivery',  desc: 'Every required iHuman section completed. We read your rubric before starting.' },
                    { icon: 'refresh-cw',   title: 'Unlimited free revisions', desc: 'Within the revision window, always by your original nurse writer.' },
                  ]" :key="g.title" class="flex gap-3 rounded-xl border border-slate-100 bg-white p-4 shadow-sm">
                    <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-100">
                      <Icon :name="g.icon" class="h-4 w-4 text-brand-600" />
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-slate-900">{{ g.title }}</p>
                      <p class="mt-0.5 text-xs text-slate-500 leading-relaxed">{{ g.desc }}</p>
                    </div>
                  </div>
                </div>
              </section>

              <section aria-labelledby="faq-heading">
                <h2 id="faq-heading" class="font-serif text-xl font-bold text-brand-900 mb-5">Common questions about iHuman help</h2>
                <div class="divide-y divide-slate-100 rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
                  <details v-for="faq in FAQS" :key="faq.q" class="group px-5 py-4">
                    <summary class="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-semibold text-slate-900">
                      {{ faq.q }}
                      <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 transition-transform group-open:rotate-45 text-xs font-bold">+</span>
                    </summary>
                    <p class="mt-3 text-sm text-slate-500 leading-relaxed">{{ faq.a }}</p>
                  </details>
                </div>
              </section>

            </template>
          </article>

          <!-- Right 1/3 — sticky iHuman order form -->
          <aside class="mt-10 lg:mt-0" aria-label="Submit iHuman case">
            <div class="sticky top-24">
              <div class="overflow-hidden rounded-2xl border border-brand-100 bg-white shadow-md">

                <div class="bg-brand-700 px-5 py-4">
                  <p class="text-[10px] font-bold uppercase tracking-widest text-brand-300 mb-0.5">iHuman case help</p>
                  <p class="text-lg font-bold text-white">Submit your case</p>
                  <p class="mt-0.5 text-xs text-brand-200">Matched to a nurse within 30 min of confirmation</p>
                </div>

                <div class="p-5">

                  <!-- Step pills -->
                  <div class="mb-5 flex items-center gap-2 text-xs">
                    <div v-for="(s, i) in [{ n: 1, label: 'Case' }, { n: 2, label: 'Account' }]" :key="s.n" class="flex items-center gap-1.5">
                      <div class="flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold"
                        :class="step === s.n ? 'bg-brand-600 text-white' : step > s.n ? 'bg-brand-100 text-brand-700' : 'bg-slate-100 text-slate-400'">
                        <Icon v-if="step > s.n" name="check" class="h-3 w-3" /><span v-else>{{ s.n }}</span>
                      </div>
                      <span :class="step === s.n ? 'font-semibold text-slate-700' : 'text-slate-400'">{{ s.label }}</span>
                      <div v-if="i === 0" class="h-px w-4 bg-slate-200" />
                    </div>
                  </div>

                  <!-- Step 1: Case details -->
                  <div v-if="step === 1" class="space-y-4">

                    <div>
                      <label class="form-label">What do you need? <span class="text-rose-500">*</span></label>
                      <div class="mt-1.5 space-y-1.5">
                        <button v-for="ct in CASE_TYPES" :key="ct.id" type="button"
                          class="flex w-full items-center gap-3 rounded-lg border px-3 py-2.5 text-left transition-all"
                          :class="form.caseType.id === ct.id ? 'border-brand-400 bg-brand-50 ring-1 ring-brand-300' : 'border-slate-200 bg-white hover:border-brand-200'"
                          @click="form.caseType = ct"
                        >
                          <span class="flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 transition-colors"
                            :class="form.caseType.id === ct.id ? 'border-brand-600 bg-brand-600' : 'border-slate-300'" />
                          <div class="min-w-0">
                            <p class="text-xs font-semibold text-slate-800">{{ ct.label }}</p>
                            <p class="text-[11px] text-slate-400">{{ ct.desc }}</p>
                          </div>
                        </button>
                      </div>
                    </div>

                    <div>
                      <label class="form-label">Body system <span class="text-rose-500">*</span></label>
                      <select v-model="form.bodySystem" class="form-input mt-1">
                        <option value="" disabled>— Select —</option>
                        <option v-for="s in BODY_SYSTEMS" :key="s" :value="s">{{ s }}</option>
                      </select>
                    </div>

                    <div>
                      <label class="form-label">Case / chief complaint <span class="text-[11px] font-normal text-slate-400">optional</span></label>
                      <input v-model="form.caseTitle" type="text" class="form-input mt-1" placeholder="e.g. Chest pain — 58yr male, smoker" />
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                      <div>
                        <label class="form-label">Cases</label>
                        <div class="mt-1 flex h-10 items-stretch overflow-hidden rounded-xl border border-slate-200 bg-white">
                          <button type="button" class="flex w-9 items-center justify-center text-slate-500 hover:bg-slate-50 disabled:opacity-30 transition-colors text-lg"
                            :disabled="form.numberOfCases <= 1" @click="form.numberOfCases = Math.max(1, form.numberOfCases - 1)">−</button>
                          <input v-model.number="form.numberOfCases" type="number" min="1" max="10" class="min-w-0 flex-1 border-x border-slate-200 text-center text-sm font-bold focus:outline-none" />
                          <button type="button" class="flex w-9 items-center justify-center text-slate-500 hover:bg-slate-50 transition-colors text-lg" @click="form.numberOfCases++">+</button>
                        </div>
                      </div>
                      <div>
                        <label class="form-label">Deadline <span class="text-rose-500">*</span></label>
                        <select v-model="form.deadline" class="form-input mt-1">
                          <option v-for="dl in DEADLINES" :key="dl.id" :value="dl">{{ dl.label }}</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label class="form-label">Academic level</label>
                      <div class="mt-1.5 flex gap-1.5">
                        <button v-for="d in DIFFICULTY" :key="d.id" type="button"
                          class="flex-1 rounded-lg border py-2 text-[11px] font-semibold transition-all"
                          :class="form.difficulty.id === d.id ? 'border-brand-500 bg-brand-600 text-white' : 'border-slate-200 bg-white text-slate-500 hover:border-brand-200'"
                          @click="form.difficulty = d"
                        >{{ d.label }}</button>
                      </div>
                    </div>

                    <div>
                      <label class="form-label">Rubric / platform notes <span class="text-[11px] font-normal text-slate-400">optional</span></label>
                      <textarea v-model="form.platformNotes" class="form-input mt-1 min-h-[70px] resize-y text-xs"
                        placeholder="Scoring rubric, login access process, specific iHuman module…" />
                    </div>

                    <button type="button"
                      class="w-full rounded-xl bg-brand-600 py-3 text-sm font-bold text-white shadow hover:bg-brand-700 disabled:opacity-50 transition-colors"
                      :disabled="!step1Valid" @click="step = 2"
                    >
                      Continue →
                    </button>
                  </div>

                  <!-- Step 2: Account -->
                  <div v-else class="space-y-4">
                    <p class="text-xs text-slate-500">Create a free account — a nurse is matched within 30 min of email confirmation.</p>

                    <div class="grid grid-cols-2 gap-2">
                      <div><label class="form-label">First name</label><input v-model="form.firstName" type="text" class="form-input mt-1" placeholder="Jane" /></div>
                      <div><label class="form-label">Last name</label><input v-model="form.lastName" type="text" class="form-input mt-1" placeholder="Smith" /></div>
                    </div>
                    <div><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-input mt-1" placeholder="you@example.com" /></div>
                    <div><label class="form-label">Password</label><input v-model="form.password" type="password" class="form-input mt-1" placeholder="At least 8 characters" minlength="8" /></div>

                    <div v-if="serverError" class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2.5 text-xs text-rose-800">{{ serverError }}</div>

                    <label class="flex cursor-pointer items-start gap-2.5">
                      <input v-model="form.agreeToTerms" type="checkbox" class="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-600" />
                      <span class="text-[11px] text-slate-500 leading-relaxed">I agree to the <NuxtLink to="/terms" target="_blank" class="text-brand-700 underline">Terms</NuxtLink> and <NuxtLink to="/privacy" target="_blank" class="text-brand-700 underline">Privacy Policy</NuxtLink>.</span>
                    </label>

                    <div class="flex gap-2">
                      <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors" @click="step = 1">← Back</button>
                      <button type="button"
                        class="flex-1 rounded-xl bg-brand-600 py-2.5 text-sm font-bold text-white shadow hover:bg-brand-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
                        :disabled="!step2Valid || submitting" @click="submit"
                      >
                        <Icon v-if="submitting" name="loader-2" class="h-4 w-4 animate-spin" />
                        {{ submitting ? 'Submitting…' : 'Submit case' }}
                      </button>
                    </div>
                    <p class="text-center text-[11px] text-slate-400">Already have an account? <NuxtLink to="/login" class="text-brand-700 hover:underline font-medium">Sign in</NuxtLink></p>
                  </div>

                </div>
              </div>

              <!-- Trust strip -->
              <div class="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-[11px] text-slate-400 px-1">
                <span class="flex items-center gap-1"><Icon name="shield" class="h-3 w-3" /> 100% confidential</span>
                <span class="flex items-center gap-1"><Icon name="refresh-cw" class="h-3 w-3" /> Free revisions</span>
                <span class="flex items-center gap-1"><Icon name="clock" class="h-3 w-3" /> As fast as 3 hours</span>
              </div>
            </div>
          </aside>

        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.form-label { @apply block text-xs font-semibold text-slate-700; }
.form-input  { @apply w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100; }
</style>
