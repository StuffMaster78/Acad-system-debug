<script setup lang="ts">
// ── CMS content (editable in Wagtail) ────────────────────────────────────────
const config      = useRuntimeConfig()
const apiBase     = config.public.apiBase || ''
const wagtailBase = `${apiBase}/wagtail`

interface CmsServicePage {
  id: number
  title: string
  meta: { slug: string; seo_title: string; search_description: string }
  hero_image?: { url: string } | null
  thumbnail?: { url: string } | null
  body: Array<{ type: string; value: unknown }>
  schema?: unknown
}

const { data: cmsPage } = await useAsyncData<CmsServicePage | null>(
  'nmg-ihuman-patients-cms',
  async () => {
    if (!wagtailBase) return null
    try {
      const res = await $fetch<{ items: CmsServicePage[] }>(
        `${wagtailBase}/api/v2/pages/`,
        { params: { type: 'cms_service_pages.ServicePage', slug: 'ihuman-patients', fields: '*' } },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

// ── iHuman order form ─────────────────────────────────────────────────────────
const auth = useRpmAuthStore()

const CASE_TYPES = [
  { id: 'full_encounter',     label: 'Full patient encounter',   desc: 'History, physical exam, assessment & plan' },
  { id: 'soap_note',          label: 'SOAP note only',           desc: 'Structured clinical documentation' },
  { id: 'differential_dx',    label: 'Differential diagnosis',   desc: 'DDx list with clinical reasoning' },
  { id: 'chief_complaint',    label: 'Chief complaint analysis', desc: 'HPI and initial assessment' },
  { id: 'full_case_and_soap', label: 'Full case + SOAP',         desc: 'Everything end-to-end' },
]

const BODY_SYSTEMS = [
  'Cardiovascular', 'Respiratory / Pulmonary', 'Neurological',
  'Gastrointestinal', 'Musculoskeletal', 'Renal / Genitourinary',
  'Endocrine / Metabolic', 'Hematology / Oncology',
  'Infectious Disease', 'Psychiatric / Mental Health', 'OB / Women\'s Health',
  'Pediatrics', 'Other / Mixed',
]

const DIFFICULTY = [
  { id: 'beginner',     label: 'Beginner',     desc: 'First or second year nursing student' },
  { id: 'intermediate', label: 'Intermediate', desc: 'Upper-division BSN or ADN' },
  { id: 'advanced',     label: 'Advanced',     desc: 'MSN, NP, or DNP student' },
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

const step       = ref(1)
const submitted  = ref(false)
const submitting = ref(false)
const serverError = ref<string | null>(null)

const form = reactive({
  // Case details
  caseType:     CASE_TYPES[0],
  caseTitle:    '',          // e.g. "Chest pain — 58yr male smoker"
  bodySystem:   '',
  difficulty:   DIFFICULTY[1],
  numberOfCases: 1,
  deadline:     DEADLINES[3],
  platformNotes: '',         // login credentials process, rubric notes
  // Account
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
const canonicalUrl = `${siteUrl}/services/ihuman-patients`

const seoTitle = computed(() => cmsPage.value?.meta?.seo_title || 'iHuman Virtual Patient Case Help | NurseMyGrade')
const seoDesc  = computed(() => cmsPage.value?.meta?.search_description || 'Expert nursing help for iHuman virtual patient cases. Full encounter completion, SOAP notes, differential diagnosis, and clinical reasoning — by real nurses.')

useSeoMeta({
  title: seoTitle,
  description: seoDesc,
  ogTitle: seoTitle,
  ogDescription: seoDesc,
  ogImage: cmsPage.value?.thumbnail?.url ?? `${siteUrl}/og-default.png`,
  ogType: 'website',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
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
          { '@type': 'ListItem', position: 1, name: 'Home',     item: `${siteUrl}/` },
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
          { '@type': 'Question', name: 'What is iHuman?', acceptedAnswer: { '@type': 'Answer', text: 'iHuman is a clinical simulation platform used in nursing and NP programs. Students complete virtual patient encounters covering history-taking, physical examination, differential diagnosis, assessment, and care planning.' } },
          { '@type': 'Question', name: 'Can you complete my entire iHuman case?', acceptedAnswer: { '@type': 'Answer', text: 'Yes. Our clinically trained nurses complete every section of your iHuman virtual patient case — from the chief complaint and HPI through the full assessment, diagnosis, and SOAP note.' } },
          { '@type': 'Question', name: 'How fast can you complete an iHuman case?', acceptedAnswer: { '@type': 'Answer', text: 'As fast as 3 hours for a standard single-encounter case. Most cases are matched with a writer within minutes of placing your order.' } },
          { '@type': 'Question', name: 'Do I need to share my iHuman login?', acceptedAnswer: { '@type': 'Answer', text: 'For full encounter completion (where we log in for you), yes. For documentation tasks like SOAP notes or differential diagnosis write-ups, we only need the case details.' } },
        ],
      }),
    },
  ],
})
</script>

<template>
  <!-- ── Success ─────────────────────────────────────────────────────────── -->
  <div v-if="submitted" class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-16">
    <div class="w-full max-w-lg text-center">
      <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-brand-100">
        <Icon name="check" class="h-10 w-10 text-brand-600" />
      </div>
      <h1 class="font-serif text-3xl font-bold text-slate-900">iHuman case request received!</h1>
      <p class="mt-4 text-slate-600 leading-relaxed">
        We've sent a confirmation link to <strong>{{ form.email }}</strong>.
        A clinically trained nurse will be matched to your case within 30 minutes of you confirming your account.
      </p>
      <div class="mt-6 rounded-2xl border border-brand-100 bg-brand-50 p-5 text-sm text-slate-600 text-left">
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

  <!-- ── Page ────────────────────────────────────────────────────────────── -->
  <div v-else>

    <!-- Hero -->
    <div class="bg-gradient-to-br from-brand-900 via-brand-800 to-brand-700 py-14 text-center">
      <div class="mx-auto max-w-3xl px-4">
        <div class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-white text-3xl">🩺</div>
        <h1 class="font-serif text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
          {{ cmsPage?.title || 'iHuman Virtual Patient Case Help' }}
        </h1>
        <p class="mx-auto mt-4 max-w-2xl text-brand-100 leading-relaxed">
          Full iHuman case completion by a clinically trained nursing expert — chief complaint, physical exam, differential diagnosis, SOAP note, and plan — matched to your rubric.
        </p>
        <div class="mt-6 flex flex-wrap justify-center gap-5 text-sm text-brand-200">
          <span class="flex items-center gap-1.5"><Icon name="clock" class="h-4 w-4" /> As fast as 3 hours</span>
          <span class="flex items-center gap-1.5"><Icon name="shield" class="h-4 w-4" /> 100% confidential</span>
          <span class="flex items-center gap-1.5"><Icon name="star" class="h-4 w-4" /> BSN, MSN, NP-qualified writers</span>
          <span class="flex items-center gap-1.5"><Icon name="refresh-cw" class="h-4 w-4" /> Free revisions included</span>
        </div>
        <a href="#order-form" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3 font-bold text-brand-800 shadow hover:bg-brand-50 transition-colors">
          Get help now
          <Icon name="arrow-down" class="h-4 w-4" />
        </a>
      </div>
    </div>

    <!-- CMS body (editable in Wagtail) -->
    <div v-if="cmsPage?.body?.length" class="bg-white">
      <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6">
        <BlockRenderer :blocks="cmsPage.body" />
      </div>
    </div>

    <!-- Static content shown when no CMS page is published yet -->
    <div v-else class="bg-white">
      <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6 prose prose-slate prose-lg max-w-none">
        <h2>What is iHuman?</h2>
        <p>iHuman is the clinical simulation platform used by hundreds of nursing programs across the US. Each case presents a virtual patient with a realistic chief complaint. Students must complete a thorough history, physical examination, order workup, establish a differential diagnosis, and formulate an evidence-based plan — all scored against a detailed rubric.</p>
        <h2>How our nurses help</h2>
        <p>Our writers are working BSN, MSN, and NP-prepared nurses who have completed iHuman cases during their own clinical training. They know the scoring rubrics, the expected documentation format, and how to approach each body system with clinical accuracy.</p>
        <h2>What we can complete for you</h2>
        <ul>
          <li>Full virtual patient encounter (history + exam + workup + assessment + plan)</li>
          <li>SOAP note written to your program's format</li>
          <li>Differential diagnosis list with clinical reasoning for each entry</li>
          <li>Chief complaint and HPI write-up</li>
          <li>Nursing diagnosis with NANDA format</li>
        </ul>
        <p class="text-sm text-slate-400 italic">This page is editable in the Wagtail admin — add or replace this content at any time.</p>
      </div>
    </div>

    <!-- ── Order form ─────────────────────────────────────────────────── -->
    <div id="order-form" class="bg-slate-50 py-14">
      <div class="mx-auto max-w-2xl px-4 sm:px-6">
        <div class="mb-8 text-center">
          <h2 class="font-serif text-2xl font-bold text-slate-900">Submit your iHuman case</h2>
          <p class="mt-2 text-slate-500">Takes 2 minutes — a nurse is matched within 30 minutes of account confirmation.</p>
        </div>

        <!-- Step pills -->
        <div class="mb-8 flex items-center gap-3">
          <div v-for="(s, i) in [{ n: 1, label: 'Case details' }, { n: 2, label: 'Your account' }]" :key="s.n" class="flex items-center gap-2">
            <div class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold"
              :class="step === s.n ? 'bg-brand-600 text-white' : step > s.n ? 'bg-brand-100 text-brand-700' : 'bg-slate-100 text-slate-400'">
              <Icon v-if="step > s.n" name="check" class="h-3.5 w-3.5" />
              <span v-else>{{ s.n }}</span>
            </div>
            <span class="text-sm" :class="step === s.n ? 'font-semibold text-slate-900' : 'text-slate-400'">{{ s.label }}</span>
            <div v-if="i === 0" class="h-px w-8 bg-slate-200" />
          </div>
        </div>

        <!-- Step 1: Case details -->
        <div v-if="step === 1" class="space-y-6">

          <!-- Case type -->
          <div>
            <label class="form-label">What do you need? <span class="text-rose-500">*</span></label>
            <div class="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              <button v-for="ct in CASE_TYPES" :key="ct.id" type="button"
                class="rounded-xl border p-3 text-left transition-all"
                :class="form.caseType.id === ct.id ? 'border-brand-500 bg-brand-50 ring-1 ring-brand-400' : 'border-slate-200 bg-white hover:border-brand-300'"
                @click="form.caseType = ct"
              >
                <p class="text-sm font-semibold text-slate-800">{{ ct.label }}</p>
                <p class="mt-0.5 text-xs text-slate-400">{{ ct.desc }}</p>
              </button>
            </div>
          </div>

          <!-- Body system -->
          <div>
            <label class="form-label">Body system / speciality <span class="text-rose-500">*</span></label>
            <select v-model="form.bodySystem" class="form-input mt-1.5">
              <option value="" disabled>— Select system —</option>
              <option v-for="s in BODY_SYSTEMS" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <!-- Case title + number of cases -->
          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="form-label">Case title / chief complaint <span class="text-xs text-slate-400">(optional)</span></label>
              <input v-model="form.caseTitle" type="text" class="form-input mt-1.5" placeholder="e.g. Chest pain — 58yr male, smoker" />
            </div>
            <div>
              <label class="form-label">Number of cases</label>
              <div class="mt-1.5 flex h-10 items-stretch overflow-hidden rounded-xl border border-slate-200 bg-white">
                <button type="button" class="flex w-10 items-center justify-center text-lg text-slate-500 hover:bg-slate-50 disabled:opacity-30 transition-colors"
                  :disabled="form.numberOfCases <= 1" @click="form.numberOfCases = Math.max(1, form.numberOfCases - 1)">−</button>
                <input v-model.number="form.numberOfCases" type="number" min="1" max="10" class="min-w-0 flex-1 border-x border-slate-200 text-center text-sm font-bold focus:outline-none" />
                <button type="button" class="flex w-10 items-center justify-center text-lg text-slate-500 hover:bg-slate-50 transition-colors"
                  @click="form.numberOfCases++">+</button>
              </div>
            </div>
          </div>

          <!-- Difficulty -->
          <div>
            <label class="form-label">Your academic level</label>
            <div class="mt-2 grid grid-cols-3 gap-3">
              <button v-for="d in DIFFICULTY" :key="d.id" type="button"
                class="rounded-xl border p-3 text-left transition-all"
                :class="form.difficulty.id === d.id ? 'border-brand-500 bg-brand-50 ring-1 ring-brand-400' : 'border-slate-200 bg-white hover:border-brand-300'"
                @click="form.difficulty = d"
              >
                <p class="text-sm font-semibold text-slate-800">{{ d.label }}</p>
                <p class="mt-0.5 text-xs text-slate-400">{{ d.desc }}</p>
              </button>
            </div>
          </div>

          <!-- Deadline -->
          <div>
            <label class="form-label">Deadline <span class="text-rose-500">*</span></label>
            <div class="mt-2 flex flex-wrap gap-2">
              <button v-for="dl in DEADLINES" :key="dl.id" type="button"
                class="rounded-lg border px-3.5 py-1.5 text-sm font-medium transition-colors"
                :class="form.deadline.id === dl.id ? 'border-brand-500 bg-brand-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300'"
                @click="form.deadline = dl"
              >{{ dl.label }}</button>
            </div>
          </div>

          <!-- Platform notes -->
          <div>
            <label class="form-label">Platform / rubric notes <span class="text-xs text-slate-400">(optional)</span></label>
            <textarea v-model="form.platformNotes" class="form-input mt-1.5 min-h-[90px] resize-y"
              placeholder="Rubric requirements, specific iHuman module, how you'll share login access, any grading criteria we should match…" />
          </div>

          <div class="flex justify-end">
            <button type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-3 font-semibold text-white shadow hover:bg-brand-700 disabled:opacity-50 transition-colors"
              :disabled="!step1Valid" @click="step = 2"
            >
              Continue <Icon name="chevron-right" class="h-4 w-4" />
            </button>
          </div>
        </div>

        <!-- Step 2: Account -->
        <div v-else class="space-y-6">
          <p class="text-slate-600">Create a free account to submit your iHuman case request. A nurse will be matched within 30 minutes of email confirmation.</p>

          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div><label class="form-label">First name</label><input v-model="form.firstName" type="text" class="form-input mt-1" placeholder="Jane" /></div>
              <div><label class="form-label">Last name</label><input v-model="form.lastName" type="text" class="form-input mt-1" placeholder="Smith" /></div>
            </div>
            <div><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-input mt-1" placeholder="you@example.com" /></div>
            <div><label class="form-label">Password</label><input v-model="form.password" type="password" class="form-input mt-1" placeholder="At least 8 characters" minlength="8" /></div>
            <div v-if="serverError" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ serverError }}</div>
            <label class="flex cursor-pointer items-start gap-3">
              <input v-model="form.agreeToTerms" type="checkbox" class="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-600" />
              <span class="text-xs text-slate-500 leading-relaxed">I agree to the <NuxtLink to="/terms" target="_blank" class="text-brand-700 underline">Terms</NuxtLink> and <NuxtLink to="/privacy" target="_blank" class="text-brand-700 underline">Privacy Policy</NuxtLink>.</span>
            </label>
          </div>

          <div class="flex justify-between">
            <button type="button" class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-6 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors" @click="step = 1">
              <Icon name="arrow-left" class="h-4 w-4" /> Back
            </button>
            <button type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-3 font-semibold text-white shadow hover:bg-brand-700 disabled:opacity-50 transition-colors"
              :disabled="!step2Valid || submitting" @click="submit"
            >
              <Icon v-if="submitting" name="loader-2" class="h-4 w-4 animate-spin" />
              {{ submitting ? 'Submitting…' : 'Submit case & create account' }}
            </button>
          </div>
          <p class="text-center text-sm text-slate-400">Already have an account? <NuxtLink to="/login" class="text-brand-700 hover:underline font-medium">Sign in</NuxtLink></p>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
.form-label { @apply block text-sm font-semibold text-slate-700; }
.form-input  { @apply w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100; }
</style>
