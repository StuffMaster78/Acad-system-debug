<script setup lang="ts">
definePageMeta({ ssr: false })

import {
  Search, Layout, GitBranch,
  Sparkles, School, ChevronRight, ChevronDown, Edit, PenLine,
  Trophy, ShieldCheck, RefreshCw, Lock, Bot, MessageSquare, Clock,
  Plus, Minus, Check, ArrowLeft, ArrowRight, Loader2,
} from '@lucide/vue'

import {
  ORDER_TYPES, WRITER_TIERS, DESIGN_TYPES, DIAGRAM_TYPES, DIAGRAM_SOFTWARE,
} from '~/composables/useOrderForm'
import type { PublicPricingConfig } from '~/composables/usePricingConfig'
import { fetchPricingConfig } from '~/composables/usePricingConfig'

const cfg = ref<PublicPricingConfig | null>(null)

const {
  form, totalPrice, pricePerUnit, unitLabel, unitCount,
  wordCount, deadlineDate, step1Valid, step2Valid, step3Valid, savePendingOrder,
  levels, paperTypes, deadlines, subjects, workTypes, formattingStyles, englishTypes, addons, isPricing, addonTotal,
} = useOrderForm(cfg)

const auth        = useRpmAuthStore()
const router      = useRouter()
const route       = useRoute()

const step          = ref(0)
const submitting    = ref(false)
const submitted     = ref(false)
const serverError   = ref<string | null>(null)
const showDiscount  = ref(false)
const subjectSearch = ref('')

onMounted(async () => {
  cfg.value = await fetchPricingConfig()
  const q = route.query

  const qtype = String(q.type ?? '')
  if (qtype) {
    const found = ORDER_TYPES.find(t => t.id === qtype)
    if (found && !found.external) {
      form.orderType = found
      if (found.presetWorkType) {
        const wt = workTypes.value.find(w => w.id === found.presetWorkType || w.label.toLowerCase().startsWith(found.presetWorkType!.toLowerCase()))
        if (wt) { form.workType = wt; form.workTypePreset = true }
      }
      step.value = 1
    }
  }

  if (q.level) {
    const lvl = levels.value.find(l => l.id === String(q.level))
    if (lvl) form.level = lvl
  }
  if (q.deadline) {
    const dl = deadlines.value.find(d => d.hours === Number(q.deadline))
    if (dl) form.deadline = dl
  }
  if (q.pages) {
    const pg = Number(q.pages)
    if (pg >= 1 && pg <= 100) form.pages = pg
  }
  if (q.paper) {
    const pt = paperTypes.value.find(p => p.id === String(q.paper))
    if (pt) form.paperType = pt
  }
  if (q.subject) {
    const subj = subjects.value.find(s => s.label === String(q.subject))
    if (subj) form.subject = subj
  }
  if (q.spacing === 'single') form.spacing = 'single'
  if (q.addons) {
    const codes = String(q.addons).split(',').filter(Boolean)
    const ids = addons.value.filter(a => codes.includes(a.addon_code)).map(a => a.id)
    if (ids.length) form.selectedAddonIds.push(...ids)
  }
})

const subjectGroups = computed(() => {
  const q = subjectSearch.value.toLowerCase()
  const filtered = subjects.value.filter(s => !q || s.label.toLowerCase().includes(q) || s.category.toLowerCase().includes(q))
  const groups: Record<string, typeof filtered> = {}
  for (const s of filtered) { if (!groups[s.category]) groups[s.category] = []; groups[s.category].push(s) }
  return groups
})

const steps = [
  { n: 1, label: 'Details' },
  { n: 2, label: 'Requirements' },
  { n: 3, label: 'Account' },
]


function selectType(ot: typeof ORDER_TYPES[0]) {
  if (ot.external) { router.push(ot.external); return }
  form.orderType = ot
  const presetWorkType = ot.presetWorkType
  if (presetWorkType) {
    const match = workTypes.value.find(w => w.id === presetWorkType || w.label.toLowerCase().startsWith(presetWorkType.toLowerCase()))
    if (match) { form.workType = match; form.workTypePreset = true }
  } else {
    form.workTypePreset = false
  }
  step.value = 1
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goNext() { if (step.value < 3) { step.value++; window.scrollTo({ top: 0, behavior: 'smooth' }) } }
function goBack() {
  if (step.value > 1) { step.value--; window.scrollTo({ top: 0, behavior: 'smooth' }) }
  else { step.value = 0 }
}

async function submitOrder() {
  submitting.value = true; serverError.value = null
  try {
    savePendingOrder()
    await auth.register({ email: form.email, password: form.password, first_name: form.firstName, last_name: form.lastName })
    submitted.value = true
  } catch { serverError.value = auth.error || 'Something went wrong. Please try again.' }
  finally { submitting.value = false }
}

useSeoMeta({
  title: 'Place an Order — EssayManiacs',
  description: 'Place your academic writing order in 3 steps. Papers, design, diagrams from $15. Human-written, plagiarism-free.',
  robots: 'noindex',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/order' }] })
</script>

<template>
  <!-- ─── Success ────────────────────────────────────────────────────── -->
  <div v-if="submitted" class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-16">
    <div class="w-full max-w-lg text-center">
      <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100">
        <Check class="h-10 w-10 text-emerald-600" />
      </div>
      <h1 class="font-serif text-3xl font-bold text-slate-900">Check your inbox</h1>
      <p class="mt-4 text-slate-600 leading-relaxed">
        We've sent a confirmation link to <strong>{{ form.email }}</strong>.
        Your order details are saved and ready to confirm after login.
      </p>
      <div class="mt-8 rounded-2xl border border-brand-100 bg-brand-50 p-6 text-left">
        <h2 class="mb-4 font-semibold text-brand-800">Your order summary</h2>
        <dl class="space-y-2 text-sm">
          <div class="flex justify-between"><dt class="text-slate-500">Order type</dt><dd class="font-medium">{{ form.orderType.label }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">Deadline</dt><dd class="font-medium">{{ form.deadline.label }} — {{ deadlineDate }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">{{ unitLabel }}</dt><dd class="font-medium">{{ unitCount }}</dd></div>
          <div class="flex justify-between border-t border-brand-200 pt-2">
            <dt class="font-semibold text-brand-800">Estimated total</dt>
            <dd class="text-lg font-bold text-brand-700">${{ totalPrice }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </div>

  <!-- ─── Order form ──────────────────────────────────────────────────── -->
  <div v-else class="min-h-[calc(100vh-4rem)] bg-slate-50">

    <!-- Progress bar (only when past type selection) -->
    <div v-if="step > 0" class="sticky top-16 z-40 border-b border-slate-200 bg-white shadow-sm">
      <div class="mx-auto max-w-5xl px-4 py-3 sm:px-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <!-- Back to type selection -->
            <button type="button" class="flex items-center gap-1.5 text-sm text-slate-400 hover:text-brand-600 transition-colors" @click="goBack">
              <ArrowLeft class="h-4 w-4" />
              <span class="hidden sm:inline">{{ step === 1 ? 'Order types' : 'Back' }}</span>
            </button>
            <div class="h-4 w-px bg-slate-200"></div>
            <!-- Order type badge -->
            <span class="rounded-full border px-2.5 py-1 text-xs font-semibold" :class="form.orderType.color">
              {{ form.orderType.label }}
            </span>
            <div class="hidden items-center gap-1 sm:flex">
              <template v-for="(s, i) in steps" :key="s.n">
                <div class="flex items-center gap-1.5">
                  <div class="flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold transition-colors"
                    :class="step === s.n ? 'bg-brand-700 text-white' : step > s.n ? 'bg-brand-100 text-brand-700' : 'bg-slate-100 text-slate-400'">
                    <Check v-if="step > s.n" class="h-3 w-3" />
                    <span v-else>{{ s.n }}</span>
                  </div>
                  <span class="text-xs" :class="step === s.n ? 'font-semibold text-slate-900' : 'text-slate-400'">{{ s.label }}</span>
                </div>
                <div v-if="i < steps.length - 1" class="h-px w-6 bg-slate-200" />
              </template>
            </div>
          </div>
          <!-- Mobile price pill -->
          <div class="flex items-center gap-1.5 rounded-full bg-brand-700 px-3 py-1.5 sm:hidden">
            <span class="text-xs text-brand-200">Est.</span>
            <span class="text-sm font-bold text-white">${{ totalPrice }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-5xl px-4 py-8 sm:px-6">

      <!-- ══ STEP 0: Service Type Selection ══ -->
      <div v-if="step === 0">
        <div class="mb-8 text-center">
          <h1 class="font-serif text-3xl font-bold text-slate-900 sm:text-4xl">What kind of help do you need?</h1>
          <p class="mt-3 text-slate-500">Choose the type of service — we'll tailor the form and price to match.</p>
        </div>

        <div class="mb-3 flex items-center gap-3">
          <span class="text-xs font-bold uppercase tracking-widest text-slate-400">Academic writing</span>
          <div class="flex-1 border-t border-slate-200" />
        </div>
        <div class="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <button
            v-for="ot in ORDER_TYPES.filter(t => t.group === 'academic')"
            :key="ot.id"
            type="button"
            class="group flex flex-col rounded-2xl border-2 bg-white p-5 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md border-slate-200 hover:border-brand-300"
            @click="selectType(ot)"
          >
            <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl" :class="ot.iconBg">
              <Edit      v-if="ot.id === 'editing'"      class="h-5 w-5" :class="ot.color.split(' ')[0]" />
              <Search    v-else-if="ot.id === 'proofreading'" class="h-5 w-5" :class="ot.color.split(' ')[0]" />
              <RefreshCw v-else-if="ot.id === 'rewriting'"   class="h-5 w-5" :class="ot.color.split(' ')[0]" />
              <PenLine   v-else class="h-5 w-5" :class="ot.color.split(' ')[0]" />
            </div>
            <h2 class="font-bold text-slate-900">{{ ot.label }}</h2>
            <p class="mt-0.5 text-xs font-medium" :class="ot.color.split(' ')[0]">{{ ot.tagline }}</p>
            <p class="mt-2 flex-1 text-xs leading-relaxed text-slate-500 line-clamp-2">{{ ot.desc }}</p>
            <div class="mt-3 flex items-center justify-between">
              <span class="text-xs font-semibold text-brand-600">from ${{ ot.priceFrom }}/{{ ot.priceUnit }}</span>
              <ChevronRight class="h-4 w-4 text-slate-300 transition-all group-hover:text-brand-600 group-hover:translate-x-0.5" />
            </div>
          </button>
        </div>

        <div class="mb-3 flex items-center gap-3">
          <span class="text-xs font-bold uppercase tracking-widest text-slate-400">Visual & other services</span>
          <div class="flex-1 border-t border-slate-200" />
        </div>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <button
            v-for="ot in ORDER_TYPES.filter(t => t.group !== 'academic')"
            :key="ot.id"
            type="button"
            class="group flex flex-col rounded-2xl border-2 bg-white p-5 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
            :class="ot.external ? 'border-dashed border-slate-200 hover:border-slate-300' : 'border-slate-200 hover:border-brand-300'"
            @click="selectType(ot)"
          >
            <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl" :class="ot.iconBg">
              <Layout    v-if="ot.id === 'design'"   class="h-5 w-5" :class="ot.color.split(' ')[0]" />
              <GitBranch v-else-if="ot.id === 'diagram'" class="h-5 w-5" :class="ot.color.split(' ')[0]" />
              <School    v-else-if="ot.id === 'class'"   class="h-5 w-5" :class="ot.color.split(' ')[0]" />
              <Sparkles  v-else class="h-5 w-5" :class="ot.color.split(' ')[0]" />
            </div>
            <h2 class="font-bold text-slate-900">{{ ot.label }}</h2>
            <p class="mt-0.5 text-xs font-medium" :class="ot.color.split(' ')[0]">{{ ot.tagline }}</p>
            <p class="mt-2 flex-1 text-xs leading-relaxed text-slate-500 line-clamp-2">{{ ot.desc }}</p>
            <div class="mt-3 flex items-center justify-between">
              <span class="text-xs font-semibold" :class="ot.external ? 'text-slate-400' : 'text-brand-600'">
                {{ ot.external ? 'Get a quote' : `from $${ot.priceFrom}/${ot.priceUnit}` }}
              </span>
              <ChevronRight class="h-4 w-4 text-slate-300 transition-all group-hover:text-brand-600 group-hover:translate-x-0.5" />
            </div>
          </button>
        </div>

        <div class="mt-10 flex flex-wrap justify-center gap-6 text-sm text-slate-500">
          <span class="flex items-center gap-1.5"><ShieldCheck class="h-4 w-4 text-green-500" /> Grade or money back</span>
          <span class="flex items-center gap-1.5"><Bot class="h-4 w-4 text-blue-500" /> Zero AI content</span>
          <span class="flex items-center gap-1.5"><RefreshCw class="h-4 w-4 text-amber-500" /> Free revisions</span>
          <span class="flex items-center gap-1.5"><Lock class="h-4 w-4 text-slate-400" /> Secure & private</span>
        </div>
      </div>

      <!-- ══ STEPS 1-3: Form ══ -->
      <div v-else class="grid gap-8 lg:grid-cols-[1fr_300px]">

        <!-- Form panel -->
        <div>

          <!-- ── STEP 1 ── -->
          <div v-show="step === 1" class="space-y-6">
            <h1 class="font-serif text-2xl font-bold text-slate-900">
              {{ form.orderType.baseType === 'design' ? 'Design details' : form.orderType.baseType === 'diagram' ? 'Diagram details' : form.orderType.label + ' details' }}
            </h1>

            <!-- PAPER / COMBO fields -->
            <template v-if="form.orderType.baseType === 'paper' || form.orderType.baseType === 'combo'">
              <!-- Paper type -->
              <div>
                <label class="form-label">Paper type</label>
                <select
                  class="form-input mt-2"
                  :value="form.paperType.id"
                  @change="form.paperType = paperTypes.find(p => p.id === ($event.target as HTMLSelectElement).value) ?? paperTypes[0]"
                >
                  <option v-for="pt in paperTypes" :key="pt.id" :value="pt.id">{{ pt.label }}</option>
                </select>
              </div>

              <!-- Level -->
              <div>
                <label class="form-label">Academic level</label>
                <div class="mt-2 flex flex-wrap gap-2">
                  <button v-for="l in levels" :key="l.id" type="button"
                    class="rounded-lg border px-3 py-2 text-sm transition-all"
                    :class="form.level.id === l.id ? 'border-brand-600 bg-brand-600 text-white font-semibold' : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300'"
                    @click="form.level = l"
                  >{{ l.label }}</button>
                </div>
                <p class="mt-1.5 text-xs text-slate-400">{{ form.level.note }}</p>
              </div>

              <!-- Pages + spacing -->
              <div class="grid gap-4 sm:grid-cols-2">
                <div>
                  <label class="form-label">Number of pages</label>
                  <div class="mt-2 flex items-center gap-4">
                    <button type="button" class="stepper-btn" :disabled="form.pages <= 1" @click="form.pages = Math.max(1, form.pages - 1)">
                      <Minus class="h-4 w-4" />
                    </button>
                    <span class="w-8 text-center text-lg font-bold text-slate-900">{{ form.pages }}</span>
                    <button type="button" class="stepper-btn" @click="form.pages++">
                      <Plus class="h-4 w-4" />
                    </button>
                    <span class="text-sm text-slate-500">≈ {{ wordCount.toLocaleString() }} words</span>
                  </div>
                </div>
                <div>
                  <label class="form-label">Spacing</label>
                  <div class="mt-2 flex gap-2">
                    <button v-for="sp in [{ id: 'double', label: 'Double' }, { id: 'single', label: 'Single' }]" :key="sp.id"
                      type="button"
                      class="flex-1 rounded-lg border py-2 text-sm font-medium transition-colors"
                      :class="form.spacing === sp.id ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300'"
                      @click="form.spacing = sp.id as any"
                    >{{ sp.label }}</button>
                  </div>
                </div>
              </div>

              <!-- Subject -->
              <div>
                <label class="form-label">Subject area</label>
                <div class="relative mt-2">
                  <input v-model="subjectSearch" type="text" class="form-input" style="padding-left:2.25rem" placeholder="Search a subject…" />
                  <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
                <div class="mt-2 max-h-52 overflow-y-auto rounded-xl border border-slate-200 bg-white">
                  <template v-for="(subjects, category) in subjectGroups" :key="category">
                    <p class="sticky top-0 border-b border-slate-100 bg-slate-50 px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-slate-400">{{ category }}</p>
                    <button v-for="s in subjects" :key="s.id" type="button"
                      class="flex w-full items-center justify-between px-3 py-2 text-sm transition-colors hover:bg-brand-50"
                      :class="form.subject.id === s.id ? 'bg-brand-50 font-semibold text-brand-700' : 'text-slate-700'"
                      @click="form.subject = s; subjectSearch = ''"
                    >
                      {{ s.label }}
                      <Check v-if="form.subject.id === s.id" class="h-4 w-4 text-brand-600" />
                    </button>
                  </template>
                </div>
                <p class="mt-1.5 text-xs text-slate-400">Selected: <strong class="text-slate-600">{{ form.subject.label }}</strong></p>
              </div>
              <!-- COMBO: plus component picker (appears below paper fields) -->
              <template v-if="form.orderType.baseType === 'combo'">
                <div class="rounded-2xl border-2 border-dashed border-amber-300 bg-amber-50 p-5">
                  <div class="mb-4 flex items-center gap-2">
                    <div class="flex h-6 w-6 items-center justify-center rounded-full bg-amber-500 text-xs font-bold text-white">+</div>
                    <h2 class="font-semibold text-slate-900">Plus component</h2>
                    <span class="text-xs text-slate-500">— choose what accompanies your paper</span>
                  </div>

                  <!-- Design vs Diagram toggle -->
                  <div class="mb-4 flex gap-2">
                    <button type="button"
                      class="flex-1 rounded-xl border py-2.5 text-sm font-semibold transition-all"
                      :class="form.comboComponent === 'design' ? 'border-purple-600 bg-purple-600 text-white shadow-sm' : 'border-slate-200 bg-white text-slate-600 hover:border-purple-300'"
                      @click="form.comboComponent = 'design'"
                    >
                      Design
                      <span class="ml-1 text-xs font-normal opacity-75">PPT · infographic · poster</span>
                    </button>
                    <button type="button"
                      class="flex-1 rounded-xl border py-2.5 text-sm font-semibold transition-all"
                      :class="form.comboComponent === 'diagram' ? 'border-teal-600 bg-teal-600 text-white shadow-sm' : 'border-slate-200 bg-white text-slate-600 hover:border-teal-300'"
                      @click="form.comboComponent = 'diagram'"
                    >
                      Diagram
                      <span class="ml-1 text-xs font-normal opacity-75">flowchart · ER · mind map</span>
                    </button>
                  </div>

                  <!-- Design sub-fields -->
                  <div v-if="form.comboComponent === 'design'" class="space-y-4">
                    <div>
                      <label class="form-label">Design type</label>
                      <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3">
                        <button v-for="dt in DESIGN_TYPES" :key="dt.id" type="button"
                          class="rounded-xl border p-3 text-left transition-all"
                          :class="form.designType.id === dt.id ? 'border-purple-600 bg-purple-600 text-white shadow-sm' : 'border-slate-200 bg-white hover:border-purple-300'"
                          @click="form.designType = dt"
                        >
                          <p class="text-sm font-semibold" :class="form.designType.id === dt.id ? 'text-white' : 'text-slate-900'">{{ dt.label }}</p>
                          <p class="mt-0.5 text-xs" :class="form.designType.id === dt.id ? 'text-purple-200' : 'text-slate-400'">{{ dt.desc }}</p>
                        </button>
                      </div>
                    </div>
                    <div>
                      <label class="form-label">Number of {{ form.designType.unit }}</label>
                      <div class="mt-2 flex items-center gap-4">
                        <button type="button" class="stepper-btn" :disabled="form.designUnits <= 1" @click="form.designUnits = Math.max(1, form.designUnits - 1)"><Minus class="h-4 w-4" /></button>
                        <span class="w-8 text-center text-lg font-bold text-slate-900">{{ form.designUnits }}</span>
                        <button type="button" class="stepper-btn" @click="form.designUnits++"><Plus class="h-4 w-4" /></button>
                      </div>
                    </div>
                    <div>
                      <label class="form-label">Style notes <span class="text-xs font-normal text-slate-400">(optional — colours, theme, brand kit)</span></label>
                      <input v-model="form.designStyle" type="text" class="form-input mt-2" placeholder="e.g. Corporate blue, minimal, matches university branding" />
                    </div>
                  </div>

                  <!-- Diagram sub-fields -->
                  <div v-else class="space-y-4">
                    <div>
                      <label class="form-label">Diagram type</label>
                      <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
                        <button v-for="dt in DIAGRAM_TYPES" :key="dt.id" type="button"
                          class="rounded-xl border p-3 text-left transition-all"
                          :class="form.diagramType.id === dt.id ? 'border-teal-600 bg-teal-600 text-white shadow-sm' : 'border-slate-200 bg-white hover:border-teal-300'"
                          @click="form.diagramType = dt"
                        >
                          <p class="text-sm font-semibold" :class="form.diagramType.id === dt.id ? 'text-white' : 'text-slate-900'">{{ dt.label }}</p>
                          <p class="mt-0.5 text-xs" :class="form.diagramType.id === dt.id ? 'text-teal-200' : 'text-slate-400'">{{ dt.desc }}</p>
                        </button>
                      </div>
                    </div>
                    <div class="grid gap-4 sm:grid-cols-2">
                      <div>
                        <label class="form-label">Number of diagrams</label>
                        <div class="mt-2 flex items-center gap-4">
                          <button type="button" class="stepper-btn" :disabled="form.diagramCount <= 1" @click="form.diagramCount = Math.max(1, form.diagramCount - 1)"><Minus class="h-4 w-4" /></button>
                          <span class="w-8 text-center text-lg font-bold text-slate-900">{{ form.diagramCount }}</span>
                          <button type="button" class="stepper-btn" @click="form.diagramCount++"><Plus class="h-4 w-4" /></button>
                        </div>
                      </div>
                      <div>
                        <label class="form-label">Output software</label>
                        <select v-model="form.diagramSoftware" class="form-input mt-2">
                          <option v-for="s in DIAGRAM_SOFTWARE" :key="s.id" :value="s">{{ s.label }}</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </template>


            <!-- DESIGN fields (standalone — not combo) -->
            <template v-else-if="form.orderType.baseType === 'design'">
              <div>
                <label class="form-label">Design type</label>
                <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3">
                  <button v-for="dt in DESIGN_TYPES" :key="dt.id" type="button"
                    class="rounded-xl border p-3 text-left transition-all hover:-translate-y-0.5"
                    :class="form.designType.id === dt.id ? 'border-purple-600 bg-purple-600 text-white shadow-sm' : 'border-slate-200 bg-white hover:border-purple-300'"
                    @click="form.designType = dt"
                  >
                    <p class="text-sm font-semibold" :class="form.designType.id === dt.id ? 'text-white' : 'text-slate-900'">{{ dt.label }}</p>
                    <p class="mt-0.5 text-xs" :class="form.designType.id === dt.id ? 'text-purple-200' : 'text-slate-400'">{{ dt.desc }}</p>
                  </button>
                </div>
              </div>
              <div>
                <label class="form-label">Number of {{ form.designType.unit }}</label>
                <div class="mt-2 flex items-center gap-4">
                  <button type="button" class="stepper-btn" :disabled="form.designUnits <= 1" @click="form.designUnits = Math.max(1, form.designUnits - 1)"><Minus class="h-4 w-4" /></button>
                  <span class="w-8 text-center text-lg font-bold text-slate-900">{{ form.designUnits }}</span>
                  <button type="button" class="stepper-btn" @click="form.designUnits++"><Plus class="h-4 w-4" /></button>
                </div>
              </div>
              <div>
                <label class="form-label">Style notes <span class="font-normal text-slate-400 text-xs ml-1">(optional — colours, theme, brand kit)</span></label>
                <input v-model="form.designStyle" type="text" class="form-input mt-2" placeholder="e.g. Corporate blue, minimal, matches university branding" />
              </div>
            </template>

            <!-- DIAGRAM fields -->
            <template v-else-if="form.orderType.baseType === 'diagram'">
              <div>
                <label class="form-label">Diagram type</label>
                <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
                  <button v-for="dt in DIAGRAM_TYPES" :key="dt.id" type="button"
                    class="rounded-xl border p-3 text-left transition-all hover:-translate-y-0.5"
                    :class="form.diagramType.id === dt.id ? 'border-teal-600 bg-teal-600 text-white shadow-sm' : 'border-slate-200 bg-white hover:border-teal-300'"
                    @click="form.diagramType = dt"
                  >
                    <p class="text-sm font-semibold">{{ dt.label }}</p>
                    <p class="mt-0.5 text-xs" :class="form.diagramType.id === dt.id ? 'text-teal-200' : 'text-slate-400'">{{ dt.desc }}</p>
                  </button>
                </div>
              </div>
              <div class="grid gap-4 sm:grid-cols-3">
                <div>
                  <label class="form-label">Number of diagrams</label>
                  <div class="mt-2 flex items-center gap-4">
                    <button type="button" class="stepper-btn" :disabled="form.diagramCount <= 1" @click="form.diagramCount = Math.max(1, form.diagramCount - 1)"><Minus class="h-4 w-4" /></button>
                    <span class="w-6 text-center font-bold text-slate-900">{{ form.diagramCount }}</span>
                    <button type="button" class="stepper-btn" @click="form.diagramCount++"><Plus class="h-4 w-4" /></button>
                  </div>
                </div>
                <div>
                  <label class="form-label">Complexity</label>
                  <div class="mt-2 flex flex-col gap-1.5">
                    <button v-for="c in [{ id: 'simple', label: 'Simple' }, { id: 'standard', label: 'Standard' }, { id: 'complex', label: 'Complex' }]" :key="c.id"
                      type="button"
                      class="rounded-lg border px-3 py-1.5 text-sm transition-colors"
                      :class="form.diagramComplexity === c.id ? 'border-teal-600 bg-teal-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-teal-300'"
                      @click="form.diagramComplexity = c.id as any"
                    >{{ c.label }}</button>
                  </div>
                </div>
                <div>
                  <label class="form-label">Output software</label>
                  <select v-model="form.diagramSoftware" class="form-input mt-2">
                    <option v-for="s in DIAGRAM_SOFTWARE" :key="s.id" :value="s">{{ s.label }}</option>
                  </select>
                </div>
              </div>
            </template>

            <!-- Shared: deadline + writer tier -->
            <div>
              <label class="form-label">Deadline</label>
              <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-5">
                <button v-for="d in deadlines" :key="d.id" type="button"
                  class="relative rounded-xl border px-2 py-2.5 text-center transition-all hover:-translate-y-0.5"
                  :class="form.deadline.id === d.id ? 'border-brand-600 bg-brand-600 text-white shadow-sm' : 'border-slate-200 bg-white text-slate-700 hover:border-brand-300'"
                  @click="form.deadline = d"
                >
                  <span v-if="d.badge" class="absolute -top-2 left-1/2 -translate-x-1/2 rounded-full bg-amber-400 px-1.5 py-0.5 text-xs font-bold text-white">{{ d.badge }}</span>
                  <p class="text-sm font-semibold">{{ d.label }}</p>
                  <p class="text-xs" :class="form.deadline.id === d.id ? 'text-brand-200' : 'text-slate-400'">{{ d.sublabel }}</p>
                </button>
              </div>
              <p class="mt-2 flex items-center gap-1.5 text-xs text-slate-500">
                <Clock class="h-3.5 w-3.5" />
                Delivery by <strong>{{ deadlineDate }}</strong>
              </p>
            </div>

            <div>
              <label class="form-label">Writer tier</label>
              <div class="mt-2 grid grid-cols-3 gap-3">
                <button v-for="tier in WRITER_TIERS" :key="tier.id" type="button"
                  class="rounded-xl border p-3 text-left transition-all"
                  :class="form.writerTier.id === tier.id ? 'border-brand-600 bg-brand-50 ring-1 ring-brand-600' : 'border-slate-200 bg-white hover:border-brand-200'"
                  @click="form.writerTier = tier"
                >
                  <p class="text-sm font-semibold text-slate-900">{{ tier.label }}</p>
                  <p class="mt-0.5 text-xs text-slate-500">{{ tier.desc }}</p>
                  <p class="mt-1 text-xs font-medium text-brand-600">{{ tier.surcharge === 0 ? 'Base price' : `+${(tier.surcharge * 100).toFixed(0)}%` }}</p>
                </button>
              </div>
            </div>

            <div class="flex justify-end pt-2">
              <button type="button" class="btn-primary flex items-center gap-2 px-8 py-3 disabled:opacity-50" :disabled="!step1Valid" @click="goNext">
                Continue <ArrowRight class="h-4 w-4" />
              </button>
            </div>
          </div>

          <!-- ── STEP 2 ── -->
          <div v-show="step === 2" class="space-y-6">
            <h1 class="font-serif text-2xl font-bold text-slate-900">Tell us what you need</h1>

            <div>
              <label for="topic" class="form-label">Topic / title <span class="text-rose-500">*</span></label>
              <input id="topic" v-model="form.topic" type="text" class="form-input mt-2" placeholder="e.g. Impact of social media on adolescent mental health" required />
            </div>

            <div>
              <label for="instructions" class="form-label">
                Instructions <span class="text-rose-500">*</span>
                <span class="ml-1 text-xs font-normal text-slate-400">rubric, assignment brief, any specific requirements</span>
              </label>
              <textarea id="instructions" v-model="form.instructions" class="form-input mt-2 min-h-[160px] resize-y" placeholder="Paste your full assignment brief here. The more detail, the better your result." required />
              <p class="mt-1 text-xs text-slate-400">{{ form.instructions.length }} characters</p>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div v-if="!form.workTypePreset">
                <label class="form-label">Type of work</label>
                <div class="mt-2 grid grid-cols-2 gap-2">
                  <button v-for="wt in workTypes" :key="wt.id" type="button"
                    class="rounded-xl border px-3 py-2.5 text-left transition-colors"
                    :class="form.workType.id === wt.id ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 bg-white hover:border-brand-300'"
                    @click="form.workType = wt"
                  >
                    <p class="text-sm font-semibold">{{ wt.label }}</p>
                    <p class="text-xs" :class="form.workType.id === wt.id ? 'text-brand-200' : 'text-slate-400'">{{ wt.desc }}</p>
                  </button>
                </div>
              </div>
              <div v-else class="flex items-start gap-2 rounded-xl border border-brand-200 bg-brand-50 px-3 py-2.5">
                <Check class="mt-0.5 h-4 w-4 shrink-0 text-brand-700" />
                <div>
                  <p class="text-xs font-semibold text-brand-900">{{ form.workType.label }}</p>
                  <p class="text-xs text-brand-700">Selected at previous step</p>
                </div>
              </div>
              <div>
                <label class="form-label">Citation style</label>
                <select v-model="form.formatStyle" class="form-input mt-2">
                  <option v-for="f in formattingStyles" :key="f.id" :value="f">{{ f.label }}</option>
                </select>
                <label class="form-label mt-4">English variant</label>
                <div class="mt-2 flex gap-2">
                  <button v-for="et in englishTypes" :key="et.id" type="button"
                    class="flex-1 rounded-lg border py-2 text-xs font-medium transition-colors"
                    :class="form.englishType.id === et.id ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300'"
                    @click="form.englishType = et"
                  >{{ et.label }}</button>
                </div>
              </div>
            </div>

            <div>
              <label class="form-label">References needed</label>
              <div class="mt-2 flex items-center gap-4">
                <button type="button" class="stepper-btn" :disabled="form.references <= 0" @click="form.references = Math.max(0, form.references - 1)"><Minus class="h-4 w-4" /></button>
                <span class="w-10 text-center font-bold text-slate-900">{{ form.references || 'Any' }}</span>
                <button type="button" class="stepper-btn" @click="form.references++"><Plus class="h-4 w-4" /></button>
              </div>
            </div>

            <div>
              <button type="button" class="flex items-center gap-1.5 text-sm text-brand-600 hover:underline" @click="showDiscount = !showDiscount">
                <ChevronDown class="h-4 w-4 transition-transform" :class="showDiscount ? 'rotate-180' : ''" />
                {{ showDiscount ? 'Hide' : 'Have a discount code?' }}
              </button>
              <div v-if="showDiscount" class="mt-2 flex gap-2">
                <input v-model="form.discountCode" type="text" class="form-input flex-1 uppercase" placeholder="e.g. FIRST15" />
                <button type="button" class="btn-outline px-4 py-2 text-sm">Apply</button>
              </div>
            </div>

            <!-- Additional services -->
            <div v-if="addons.length" class="rounded-xl border border-brand-100 bg-brand-50 p-5">
              <h2 class="mb-1 text-sm font-semibold text-slate-900">Additional services</h2>
              <p class="mb-4 text-xs text-slate-500">Optional add-ons included in your order total.</p>
              <div class="space-y-3">
                <label
                  v-for="addon in addons"
                  :key="addon.id"
                  class="flex cursor-pointer items-start gap-3 rounded-lg border bg-white p-3 transition-colors"
                  :class="form.selectedAddonIds.includes(addon.id) ? 'border-brand-400 bg-brand-50' : 'border-slate-200 hover:border-slate-300'"
                >
                  <input
                    type="checkbox"
                    class="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-600"
                    :checked="form.selectedAddonIds.includes(addon.id)"
                    @change="form.selectedAddonIds.includes(addon.id)
                      ? form.selectedAddonIds.splice(form.selectedAddonIds.indexOf(addon.id), 1)
                      : form.selectedAddonIds.push(addon.id)"
                  />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-slate-900">{{ addon.name }}</p>
                    <p v-if="addon.description" class="mt-0.5 text-xs text-slate-500">{{ addon.description }}</p>
                  </div>
                  <span class="shrink-0 text-sm font-semibold text-brand-700">+${{ addon.flat_amount }}</span>
                </label>
              </div>
              <p v-if="addonTotal > 0" class="mt-3 text-right text-xs font-semibold text-brand-700">
                Add-ons: +${{ addonTotal }}
              </p>
            </div>

            <div class="flex justify-between pt-2">
              <button type="button" class="btn-outline flex items-center gap-2 px-6 py-2.5" @click="goBack"><ArrowLeft class="h-4 w-4" /> Back</button>
              <button type="button" class="btn-primary flex items-center gap-2 px-8 py-3 disabled:opacity-50" :disabled="!step2Valid" @click="goNext">
                Continue <ArrowRight class="h-4 w-4" />
              </button>
            </div>
          </div>

          <!-- ── STEP 3 ── -->
          <div v-show="step === 3" class="space-y-6">
            <h1 class="font-serif text-2xl font-bold text-slate-900">Create your free account</h1>

            <!-- Summary -->
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h2 class="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Order summary</h2>
              <div class="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                <span class="text-slate-500">Type</span>       <span class="font-medium">{{ form.orderType.label }}</span>
                <span class="text-slate-500">Deadline</span>   <span class="font-medium">{{ form.deadline.label }}</span>
                <span class="text-slate-500">{{ unitLabel }}</span> <span class="font-medium">{{ unitCount }} × ${{ pricePerUnit }}/{{ unitLabel }}</span>
                <span class="text-slate-500">Topic</span>      <span class="font-medium truncate">{{ form.topic }}</span>
              </div>
              <div class="mt-3 flex items-center justify-between border-t border-slate-200 pt-3">
                <span class="font-semibold text-slate-700">Estimated total</span>
                <span class="text-xl font-bold text-brand-700">${{ totalPrice }}</span>
              </div>
            </div>

            <!-- Register -->
            <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 class="mb-4 font-semibold text-slate-800">Your account details</h2>
              <div class="space-y-4">
                <div class="grid grid-cols-2 gap-3">
                  <div><label class="form-label" for="fn">First name</label><input id="fn" v-model="form.firstName" type="text" class="form-input mt-1" placeholder="Jane" autocomplete="given-name" /></div>
                  <div><label class="form-label" for="ln">Last name</label><input id="ln" v-model="form.lastName" type="text" class="form-input mt-1" placeholder="Smith" autocomplete="family-name" /></div>
                </div>
                <div><label class="form-label" for="em">Email address</label><input id="em" v-model="form.email" type="email" class="form-input mt-1" placeholder="you@example.com" autocomplete="email" /></div>
                <div><label class="form-label" for="pw">Password</label><input id="pw" v-model="form.password" type="password" class="form-input mt-1" placeholder="At least 8 characters" minlength="8" autocomplete="new-password" /></div>
                <div v-if="serverError" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ serverError }}</div>
                <label class="flex cursor-pointer items-start gap-3">
                  <input v-model="form.agreeToTerms" type="checkbox" class="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-600" />
                  <span class="text-xs text-slate-500 leading-relaxed">
                    I agree to the <NuxtLink to="/terms" target="_blank" class="text-brand-600 underline">Terms</NuxtLink> and <NuxtLink to="/privacy" target="_blank" class="text-brand-600 underline">Privacy Policy</NuxtLink>. I understand this is a model paper service for reference use.
                  </span>
                </label>
              </div>
            </div>

            <div class="flex justify-between pt-2">
              <button type="button" class="btn-outline flex items-center gap-2 px-6 py-2.5" @click="goBack"><ArrowLeft class="h-4 w-4" /> Back</button>
              <button type="button" class="btn-primary flex items-center gap-2 px-8 py-3.5 text-base disabled:opacity-50" :disabled="!step3Valid || submitting" @click="submitOrder">
                <Loader2 v-if="submitting" class="h-4 w-4 animate-spin" />
                {{ submitting ? 'Creating account…' : 'Place order & create account' }}
              </button>
            </div>
            <p class="text-center text-sm text-slate-400">Already have an account? <NuxtLink to="/login" class="font-medium text-brand-600 hover:underline">Sign in</NuxtLink></p>
          </div>
        </div>

        <!-- ─── Sticky sidebar ─────────────────────────────────────────── -->
        <div class="hidden lg:block">
          <div class="sticky top-28 space-y-4">
            <!-- Live price -->
            <div class="rounded-2xl border border-brand-100 bg-white p-5 shadow-sm">
              <h3 class="mb-4 font-serif text-base font-bold text-slate-900">Price estimate</h3>
              <dl class="space-y-2 text-sm">
                <div class="flex justify-between"><dt class="text-slate-500">Type</dt><dd class="font-medium text-slate-700">{{ form.orderType.label }}</dd></div>
                <div class="flex justify-between"><dt class="text-slate-500">Deadline</dt><dd class="font-medium text-slate-700">{{ form.deadline.label }}</dd></div>
                <div class="flex justify-between"><dt class="text-slate-500">{{ unitLabel }}</dt><dd class="font-medium text-slate-700">{{ unitCount }}</dd></div>
                <div class="flex justify-between"><dt class="text-slate-500">Per {{ unitLabel === 'slides' ? 'slide' : unitLabel.replace('s','') }}</dt><dd class="font-medium text-slate-700">${{ pricePerUnit }}</dd></div>
              </dl>
              <div class="mt-4 rounded-xl bg-brand-50 px-4 py-3">
                <p class="text-xs font-medium text-brand-600">Estimated total</p>
                <p class="text-3xl font-bold text-brand-700">${{ totalPrice }}</p>
              </div>
              <p class="mt-2 text-center text-xs text-slate-400">Delivery by {{ deadlineDate }}</p>
            </div>
            <!-- Guarantees -->
            <div class="rounded-2xl border border-slate-100 bg-white p-5">
              <h3 class="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Included</h3>
              <ul class="space-y-2.5 text-sm">
                <li class="flex items-center gap-2.5 text-slate-600"><Trophy class="h-4 w-4 shrink-0 text-amber-500" /> Grade or money back</li>
                <li class="flex items-center gap-2.5 text-slate-600"><Bot class="h-4 w-4 shrink-0 text-blue-500" /> Zero AI — 100% human</li>
                <li class="flex items-center gap-2.5 text-slate-600"><ShieldCheck class="h-4 w-4 shrink-0 text-green-500" /> Free plagiarism report</li>
                <li class="flex items-center gap-2.5 text-slate-600"><RefreshCw class="h-4 w-4 shrink-0 text-purple-500" /> Unlimited revisions</li>
                <li class="flex items-center gap-2.5 text-slate-600"><Lock class="h-4 w-4 shrink-0 text-slate-400" /> Secure payment & escrow</li>
                <li class="flex items-center gap-2.5 text-slate-600"><MessageSquare class="h-4 w-4 shrink-0 text-brand-500" /> Direct writer messaging</li>
              </ul>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.form-label  { @apply block text-sm font-semibold text-slate-700; }
.form-input  { @apply w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 transition-colors focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200; }
.stepper-btn { @apply flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors disabled:opacity-30; }
</style>
