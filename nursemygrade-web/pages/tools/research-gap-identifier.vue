<script setup lang="ts">
useSeoMeta({
  title: 'Research Gap Identifier — Find Your Research Gap & Build Hypotheses | NurseMyGrade',
  description: 'Identify your research gap, generate a gap statement for Chapter 1, and build properly formatted H₀/H₁ hypotheses. Free tool for dissertation and thesis students.',
})

// ─── Types ────────────────────────────────────────────────────────────────────

type Paradigm = 'quantitative' | 'qualitative' | 'mixed'

interface ResearchContext {
  topic: string
  field: string
  population: string
  timePeriod: string
  finding1: string
  finding2: string
  finding3: string
  gapTypes: string[]
  paradigm: Paradigm
  design: string
}

interface HypothesisPair {
  h0: string
  h1dir: string
  h1nondir: string
}

// ─── Gap type config ──────────────────────────────────────────────────────────

const GAP_TYPE_OPTIONS = [
  {
    value: 'population',
    label: 'Population gap',
    sublabel: 'The topic has been studied in one population but not yours',
  },
  {
    value: 'geographic',
    label: 'Geographic gap',
    sublabel: 'Research is concentrated in specific regions (e.g. Western countries) but not your context',
  },
  {
    value: 'methodological',
    label: 'Methodological gap',
    sublabel: 'Existing studies use only one method; yours uses a different/mixed approach',
  },
  {
    value: 'temporal',
    label: 'Temporal gap',
    sublabel: 'Existing research is outdated; recent developments haven\'t been studied',
  },
  {
    value: 'conceptual',
    label: 'Conceptual gap',
    sublabel: 'Two or more variables have been studied separately but not together',
  },
  {
    value: 'contextual',
    label: 'Contextual gap',
    sublabel: 'The topic hasn\'t been studied in your specific setting or context',
  },
  {
    value: 'contradictory',
    label: 'Contradictory findings',
    sublabel: 'Existing studies conflict; yours aims to resolve the contradiction',
  },
]

const GAP_DESCRIPTIONS: Record<string, string> = {
  population:    'the specific population of {population} remains underrepresented in the literature',
  geographic:    'research from {population} context remains scarce, with most studies based in Western or high-income country settings',
  methodological: 'existing research has predominantly relied on a single methodological approach, limiting the depth and generalisability of findings',
  temporal:      'much of the existing evidence dates from {timePeriod} and may not reflect recent developments in this rapidly evolving area',
  conceptual:    'the relationship between the key variables has rarely been examined in an integrated framework',
  contextual:    'the specific context of {field} in relation to {population} has not been adequately addressed',
  contradictory: 'existing findings are contradictory and inconclusive, highlighting the need for further empirical investigation',
}

// ─── Design options per paradigm ─────────────────────────────────────────────

const DESIGNS: Record<Paradigm, string[]> = {
  quantitative: ['Experimental', 'Survey/Cross-sectional', 'Longitudinal', 'Quasi-experimental', 'Correlational', 'Other'],
  qualitative:  ['Phenomenological', 'Grounded Theory', 'Case Study', 'Ethnographic', 'Narrative Inquiry', 'Other'],
  mixed:        ['Sequential Explanatory', 'Sequential Exploratory', 'Convergent Parallel', 'Case Study', 'Other'],
}

// ─── Form state ───────────────────────────────────────────────────────────────

const topic      = ref('')
const field      = ref('')
const population = ref('')
const timePeriod = ref('')
const finding1   = ref('')
const finding2   = ref('')
const finding3   = ref('')
const gapTypes   = ref<string[]>([])
const paradigm   = ref<Paradigm>('quantitative')
const design     = ref('Survey/Cross-sectional')

watch(paradigm, (p) => {
  design.value = DESIGNS[p][0]
})

// ─── Validation ───────────────────────────────────────────────────────────────

const canGenerate = computed(() =>
  topic.value.trim().length > 0 &&
  (finding1.value.trim().length > 0 || finding2.value.trim().length > 0) &&
  gapTypes.value.length > 0
)

// ─── Output state ─────────────────────────────────────────────────────────────

const generated = ref(false)
const gapStatement    = ref('')
const researchQuestions = ref<string[]>([])
const hypotheses      = ref<HypothesisPair[]>([])
const copiedKey       = ref('')

// ─── Builder functions ────────────────────────────────────────────────────────

function sub(template: string, ctx: ResearchContext): string {
  return template
    .replace(/\{population\}/g, ctx.population || 'the target population')
    .replace(/\{field\}/g, ctx.field || 'the relevant field')
    .replace(/\{timePeriod\}/g, ctx.timePeriod || 'prior decades')
    .replace(/\{topic\}/g, ctx.topic || 'the topic')
}

function buildGapStatement(ctx: ResearchContext): string {
  const topic_   = ctx.topic || 'the topic'
  const pop_     = ctx.population || 'the target population'
  const field_   = ctx.field || 'the relevant field'

  const f1 = ctx.finding1.trim()
  const f2 = ctx.finding2.trim()

  const findingsClauses: string[] = []
  if (f1) findingsClauses.push(f1.replace(/\.$/, ''))
  if (f2) findingsClauses.push(f2.replace(/\.$/, ''))
  const findingStr = findingsClauses.length === 2
    ? `${findingsClauses[0]}, and ${findingsClauses[1]}`
    : findingsClauses[0] || 'important relationships in this domain'

  const gapClauses = ctx.gapTypes.map(g => sub(GAP_DESCRIPTIONS[g] || '', ctx)).filter(Boolean)
  const gapStr = gapClauses.length === 1
    ? gapClauses[0]
    : gapClauses.length === 2
      ? `${gapClauses[0]}, and ${gapClauses[1]}`
      : gapClauses.slice(0, -1).join(', ') + ', and ' + gapClauses[gapClauses.length - 1]

  let stmt = `Despite a growing body of literature on ${topic_}, significant gaps remain in our understanding of this phenomenon within ${pop_ ? pop_ + ' contexts' : 'the broader field'}. While existing studies have established that ${findingStr}, ${gapStr}.`

  if (ctx.gapTypes.includes('temporal') && ctx.timePeriod) {
    stmt += ` Furthermore, most studies in this area were conducted between ${ctx.timePeriod}, and the field has since evolved considerably.`
  }
  if (ctx.gapTypes.includes('geographic') && ctx.population) {
    stmt += ` The majority of research has focused on Western or high-income settings, leaving ${pop_} largely underexplored.`
  }
  if (ctx.gapTypes.includes('methodological')) {
    stmt += ` Methodologically, existing research has predominantly relied on a single approach, which constrains the generalisability and depth of available evidence.`
  }

  const paradigmPhrase = ctx.paradigm === 'quantitative' ? 'quantitative'
    : ctx.paradigm === 'qualitative' ? 'qualitative'
    : 'mixed-methods'

  stmt += ` This study therefore seeks to address this gap by examining ${topic_}${pop_ ? ' among ' + pop_ : ''} using ${paradigmPhrase} methods, contributing new evidence to an underrepresented area of inquiry${field_ ? ' within ' + field_ : ''}.`

  return stmt
}

function buildResearchQuestions(ctx: ResearchContext): string[] {
  const topic_ = ctx.topic || 'the topic'
  const pop_   = ctx.population || 'the study population'
  const field_ = ctx.field || 'the study context'

  if (ctx.paradigm === 'quantitative') {
    return [
      `To what extent does ${topic_} influence academic and psychosocial outcomes among ${pop_} in ${field_}?`,
      `What is the relationship between key variables associated with ${topic_} and observed outcomes among ${pop_}?`,
    ]
  } else if (ctx.paradigm === 'qualitative') {
    return [
      `How do ${pop_} experience and make sense of ${topic_} within ${field_}?`,
      `What meanings do ${pop_} assign to their encounters with ${topic_} in ${field_}?`,
    ]
  } else {
    return [
      `What is the relationship between variables associated with ${topic_} among ${pop_}, and how do ${pop_} make sense of this relationship in ${field_}?`,
      `To what extent does ${topic_} influence outcomes among ${pop_}, and what lived experiences shape this relationship?`,
    ]
  }
}

function buildHypotheses(ctx: ResearchContext): HypothesisPair[] {
  const topic_ = ctx.topic || 'the topic'
  const pop_   = ctx.population || 'the study population'

  if (ctx.paradigm === 'qualitative') {
    return [
      {
        h0: `[Proposition 1] It is proposed that ${pop_} construct contextually specific understandings of ${topic_} that are shaped by their immediate social and cultural environment.`,
        h1dir: `[Proposition 2] It is anticipated that ${pop_} who have greater exposure to ${topic_} will develop more nuanced and adaptive responses compared to those with limited exposure.`,
        h1nondir: `[Proposition 3] The ways in which ${pop_} navigate ${topic_} are expected to reflect broader structural and institutional factors within their context.`,
      },
    ]
  }

  return [
    {
      h0: `H₀: There is no statistically significant relationship between ${topic_} and the primary outcome variable among ${pop_}.`,
      h1dir: `H₁ (Directional): ${pop_ ? pop_.charAt(0).toUpperCase() + pop_.slice(1) : 'Participants'} with higher levels of exposure to ${topic_} will demonstrate significantly greater changes in the outcome variable compared to those with lower levels of exposure.`,
      h1nondir: `H₁ (Non-directional): There is a statistically significant relationship between ${topic_} and the primary outcome variable among ${pop_}.`,
    },
    {
      h0: `H₀: There is no statistically significant difference in key outcome measures related to ${topic_} between subgroups within ${pop_}.`,
      h1dir: `H₁ (Directional): ${pop_ ? pop_.charAt(0).toUpperCase() + pop_.slice(1) : 'Participants'} in the high-exposure group will score significantly higher on outcome measures related to ${topic_} than those in the low-exposure group.`,
      h1nondir: `H₁ (Non-directional): Statistically significant differences exist in outcome measures related to ${topic_} across subgroups within ${pop_}.`,
    },
    {
      h0: `H₀: ${topic_ ? topic_.charAt(0).toUpperCase() + topic_.slice(1) : 'The independent variable'} does not significantly predict the dependent variable among ${pop_} when controlling for confounding variables.`,
      h1dir: `H₁ (Directional): ${topic_ ? topic_.charAt(0).toUpperCase() + topic_.slice(1) : 'The independent variable'} will significantly and positively predict the dependent variable among ${pop_} after controlling for relevant covariates.`,
      h1nondir: `H₁ (Non-directional): ${topic_ ? topic_.charAt(0).toUpperCase() + topic_.slice(1) : 'The independent variable'} will significantly predict the dependent variable among ${pop_} after controlling for relevant covariates.`,
    },
  ]
}

// ─── Generate ─────────────────────────────────────────────────────────────────

function generate() {
  if (!canGenerate.value) return
  const ctx: ResearchContext = {
    topic:      topic.value.trim(),
    field:      field.value.trim(),
    population: population.value.trim(),
    timePeriod: timePeriod.value.trim(),
    finding1:   finding1.value.trim(),
    finding2:   finding2.value.trim(),
    finding3:   finding3.value.trim(),
    gapTypes:   gapTypes.value,
    paradigm:   paradigm.value,
    design:     design.value,
  }
  gapStatement.value      = buildGapStatement(ctx)
  researchQuestions.value = buildResearchQuestions(ctx)
  hypotheses.value        = buildHypotheses(ctx)
  generated.value         = true
  // Scroll to results on mobile
  if (window.innerWidth < 1024) {
    setTimeout(() => {
      document.getElementById('rgi-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 100)
  }
}

// ─── Clipboard ────────────────────────────────────────────────────────────────

async function copyText(text: string, key: string) {
  await navigator.clipboard.writeText(text)
  copiedKey.value = key
  setTimeout(() => { copiedKey.value = '' }, 2000)
}

const gapCharCount = computed(() => gapStatement.value.length)

// ─── Quick tips (always visible) ─────────────────────────────────────────────

const TIPS = [
  'A strong gap statement appears in both your Introduction and Literature Review chapters.',
  'Your research gap directly justifies your study\'s existence — be specific, not vague.',
  'Cite the studies you mentioned in Key Findings to support your gap claim.',
  'Your hypothesis should directly address your research question and name specific variables.',
]
</script>

<template>
  <div class="bg-slate-50 min-h-screen">

    <!-- Breadcrumb -->
    <div class="max-w-6xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Research Gap Identifier</span>
      </nav>
    </div>

    <!-- Page header -->
    <div class="max-w-6xl mx-auto px-4 pb-6">
      <div class="flex flex-wrap items-start gap-3">
        <div class="flex-1 min-w-0">
          <div class="flex flex-wrap items-center gap-2 mb-1">
            <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800">Research Gap Identifier</h1>
            <span class="rounded-full bg-brand-100 text-brand-700 text-xs font-bold px-3 py-1">Doctoral &amp; Master's level</span>
          </div>
          <p class="text-slate-500 text-sm max-w-2xl">For dissertation and thesis writers. Identify your gap, generate a gap statement, and build testable hypotheses — in seconds.</p>
        </div>
      </div>
    </div>

    <div class="max-w-6xl mx-auto px-4 pb-16 flex flex-col lg:flex-row gap-6">

      <!-- ── Left: Form ── -->
      <div class="flex-1 space-y-5 min-w-0">

        <!-- Step 1: Research Context -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-4">
          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Step 1 — Your Research Context</h2>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Research Topic <span class="text-red-400">*</span>
            </label>
            <input
              v-model="topic"
              type="text"
              placeholder="e.g. the impact of social media on adolescent mental health"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Research Field / Discipline</label>
              <input
                v-model="field"
                type="text"
                placeholder="e.g. Clinical Psychology"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Study Population</label>
              <input
                v-model="population"
                type="text"
                placeholder="e.g. university students aged 18–25 in Sub-Saharan Africa"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Time Period of Existing Studies</label>
            <input
              v-model="timePeriod"
              type="text"
              placeholder="e.g. 2010–2023"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>
        </div>

        <!-- Step 2: Key Findings -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-4">
          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Step 2 — What Existing Literature Has Found</h2>
          <p class="text-xs text-slate-400">Briefly summarise up to 3 key findings from existing studies on your topic. At least one is required.</p>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Key Finding 1 <span class="text-red-400">*</span></label>
            <textarea
              v-model="finding1"
              rows="2"
              placeholder="e.g. Studies show a correlation between Instagram use and depression scores in Western teenagers"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none resize-none"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Key Finding 2</label>
            <textarea
              v-model="finding2"
              rows="2"
              placeholder="e.g. Longitudinal studies report persistent effects of excessive screen time on anxiety in adolescents aged 13–17"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none resize-none"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Key Finding 3 <span class="text-slate-400 font-normal text-xs">(optional)</span></label>
            <textarea
              v-model="finding3"
              rows="2"
              placeholder="e.g. Protective factors such as parental monitoring moderate the relationship between social media use and depression"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none resize-none"
            />
          </div>
        </div>

        <!-- Step 3: Gap types -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-3">
          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Step 3 — What Type of Gap Exists? <span class="text-red-400">*</span></h2>
          <p class="text-xs text-slate-400">Select all that apply. Each gap type you select will be incorporated into the generated statement.</p>

          <div class="space-y-3 pt-1">
            <label
              v-for="opt in GAP_TYPE_OPTIONS"
              :key="opt.value"
              class="flex items-start gap-3 rounded-xl border p-3 cursor-pointer transition-all"
              :class="gapTypes.includes(opt.value)
                ? 'border-brand-400 bg-brand-50'
                : 'border-slate-200 hover:border-brand-200 hover:bg-slate-50'"
            >
              <input
                type="checkbox"
                :value="opt.value"
                v-model="gapTypes"
                class="mt-0.5 rounded accent-brand-600 w-4 h-4 shrink-0"
              />
              <div>
                <p class="text-sm font-semibold text-slate-700">{{ opt.label }}</p>
                <p
                  v-if="gapTypes.includes(opt.value)"
                  class="text-xs text-slate-500 mt-0.5"
                >{{ opt.sublabel }}</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Step 4: Approach -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-4">
          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Step 4 — Your Research Approach</h2>

          <!-- Paradigm pills -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2">Research Paradigm</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="p in (['quantitative', 'qualitative', 'mixed'] as Paradigm[])"
                :key="p"
                type="button"
                @click="paradigm = p"
                class="rounded-full border px-4 py-1.5 text-sm font-semibold transition-all capitalize"
                :class="paradigm === p
                  ? 'border-brand-500 bg-brand-600 text-white'
                  : 'border-slate-200 text-slate-600 hover:border-brand-300'"
              >
                {{ p === 'mixed' ? 'Mixed Methods' : p.charAt(0).toUpperCase() + p.slice(1) }}
              </button>
            </div>
          </div>

          <!-- Design dropdown -->
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">Research Design</label>
            <select
              v-model="design"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            >
              <option v-for="d in DESIGNS[paradigm]" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>

          <!-- Generate button -->
          <button
            type="button"
            :disabled="!canGenerate"
            @click="generate"
            class="w-full rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z"/>
            </svg>
            Generate Gap Statement &amp; Hypotheses
          </button>
          <p v-if="!canGenerate" class="text-xs text-slate-400 text-center">Fill in your topic, at least one key finding, and select at least one gap type to continue.</p>
        </div>

      </div>

      <!-- ── Right: Results ── -->
      <div id="rgi-results" class="lg:w-[480px] xl:w-[520px] flex-shrink-0 space-y-5">

        <!-- Quick Tips — always visible -->
        <div class="rounded-2xl bg-amber-50 border border-amber-200 p-5">
          <h3 class="text-xs font-bold text-amber-800 uppercase tracking-widest mb-3">Quick Tips</h3>
          <ul class="space-y-2">
            <li v-for="tip in TIPS" :key="tip" class="flex items-start gap-2 text-xs text-amber-900">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 mt-0.5 shrink-0 text-amber-600" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/>
              </svg>
              {{ tip }}
            </li>
          </ul>
        </div>

        <!-- Empty state -->
        <div v-if="!generated" class="rounded-2xl bg-white shadow-sm border border-slate-100 p-8 text-center">
          <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-50 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 text-brand-500" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 15.803m10.607 0A7.5 7.5 0 0 0 5.196 15.803"/>
            </svg>
          </div>
          <p class="text-sm font-semibold text-slate-700 mb-1">Your output will appear here</p>
          <p class="text-xs text-slate-400">Complete the form on the left and click Generate.</p>
        </div>

        <!-- Output sections -->
        <template v-if="generated">

          <!-- Section 1: Gap Types -->
          <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
            <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Gap Type(s) Identified</h2>
            <div class="flex flex-wrap gap-2">
              <div
                v-for="g in gapTypes"
                :key="g"
                class="rounded-full bg-brand-100 text-brand-700 text-xs font-bold px-3 py-1.5"
              >
                {{ GAP_TYPE_OPTIONS.find(o => o.value === g)?.label }}
              </div>
            </div>
            <div class="mt-3 space-y-2">
              <div
                v-for="g in gapTypes"
                :key="'desc-' + g"
                class="text-xs text-slate-600 bg-slate-50 rounded-lg px-3 py-2"
              >
                <span class="font-semibold text-slate-700">{{ GAP_TYPE_OPTIONS.find(o => o.value === g)?.label }}:</span>
                {{ GAP_TYPE_OPTIONS.find(o => o.value === g)?.sublabel }}
              </div>
            </div>
          </div>

          <!-- Section 2: Gap Statement -->
          <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Research Gap Statement</h2>
              <span class="text-[10px] text-slate-400 font-medium">{{ gapCharCount }} chars</span>
            </div>
            <p class="text-sm text-slate-700 leading-relaxed bg-slate-50 rounded-xl p-4 border border-slate-200">{{ gapStatement }}</p>
            <button
              type="button"
              @click="copyText(gapStatement, 'gap')"
              class="mt-3 flex items-center gap-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700 transition-colors"
            >
              <svg v-if="copiedKey !== 'gap'" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"/>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/>
              </svg>
              {{ copiedKey === 'gap' ? 'Copied!' : 'Copy gap statement' }}
            </button>
            <p class="mt-3 text-[10px] text-slate-400">Suitable for Chapter 1 (Introduction) and Chapter 2 (Literature Review). Adapt variable names to match your study.</p>
          </div>

          <!-- Section 3: Research Questions -->
          <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
            <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Research Questions</h2>
            <div class="space-y-4">
              <div
                v-for="(rq, i) in researchQuestions"
                :key="'rq-' + i"
                class="rounded-xl bg-slate-50 border border-slate-200 p-4"
              >
                <p class="text-xs font-bold text-brand-700 mb-1.5">Option {{ i + 1 }}</p>
                <p class="text-sm text-slate-700 leading-relaxed italic">{{ rq }}</p>
                <button
                  type="button"
                  @click="copyText(rq, 'rq' + i)"
                  class="mt-2 flex items-center gap-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700 transition-colors"
                >
                  <svg v-if="copiedKey !== 'rq' + i" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"/>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"/>
                  </svg>
                  {{ copiedKey === 'rq' + i ? 'Copied!' : 'Copy' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Section 4: Hypotheses / Propositions -->
          <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
            <h2 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">
              {{ paradigm === 'qualitative' ? 'Research Propositions' : 'Hypothesis Pairs' }}
            </h2>
            <p v-if="paradigm === 'qualitative'" class="text-xs text-slate-400 mb-3">
              Qualitative research uses propositions rather than H₀/H₁ hypotheses.
            </p>
            <p v-else class="text-xs text-slate-400 mb-3">
              Each pair includes a null hypothesis (H₀) and two alternative forms.
            </p>

            <div class="space-y-6">
              <div
                v-for="(pair, i) in hypotheses"
                :key="'hyp-' + i"
                class="rounded-xl bg-slate-50 border border-slate-200 p-4 space-y-3"
              >
                <p v-if="paradigm !== 'qualitative'" class="text-xs font-bold text-slate-500 uppercase tracking-wider">Pair {{ i + 1 }}</p>

                <div class="space-y-2">
                  <div class="rounded-lg bg-red-50 border border-red-100 px-3 py-2.5">
                    <p class="text-xs font-bold text-red-700 mb-1">{{ paradigm === 'qualitative' ? 'Proposition 1' : 'H₀ — Null Hypothesis' }}</p>
                    <p class="text-xs text-slate-700 leading-relaxed">{{ pair.h0.replace(/^\[Proposition \d\]\s*/, '') }}</p>
                    <button type="button" @click="copyText(pair.h0.replace(/^\[Proposition \d\]\s*/, ''), 'h0-' + i)"
                      class="mt-1.5 text-[10px] font-semibold text-brand-600 hover:text-brand-700 transition-colors">
                      {{ copiedKey === 'h0-' + i ? 'Copied!' : 'Copy' }}
                    </button>
                  </div>
                  <div class="rounded-lg bg-emerald-50 border border-emerald-100 px-3 py-2.5">
                    <p class="text-xs font-bold text-emerald-700 mb-1">{{ paradigm === 'qualitative' ? 'Proposition 2' : 'H₁ — Directional Alternative' }}</p>
                    <p class="text-xs text-slate-700 leading-relaxed">{{ pair.h1dir.replace(/^\[Proposition \d\]\s*/, '') }}</p>
                    <button type="button" @click="copyText(pair.h1dir.replace(/^\[Proposition \d\]\s*/, ''), 'h1d-' + i)"
                      class="mt-1.5 text-[10px] font-semibold text-brand-600 hover:text-brand-700 transition-colors">
                      {{ copiedKey === 'h1d-' + i ? 'Copied!' : 'Copy' }}
                    </button>
                  </div>
                  <div class="rounded-lg bg-blue-50 border border-blue-100 px-3 py-2.5">
                    <p class="text-xs font-bold text-blue-700 mb-1">{{ paradigm === 'qualitative' ? 'Proposition 3' : 'H₁ — Non-directional Alternative' }}</p>
                    <p class="text-xs text-slate-700 leading-relaxed">{{ pair.h1nondir.replace(/^\[Proposition \d\]\s*/, '') }}</p>
                    <button type="button" @click="copyText(pair.h1nondir.replace(/^\[Proposition \d\]\s*/, ''), 'h1n-' + i)"
                      class="mt-1.5 text-[10px] font-semibold text-brand-600 hover:text-brand-700 transition-colors">
                      {{ copiedKey === 'h1n-' + i ? 'Copied!' : 'Copy' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Soft CTA -->
          <div class="rounded-2xl bg-brand-50 border border-brand-100 p-5 text-center">
            <p class="text-sm text-slate-600 mb-3">Need help writing your dissertation chapter? Our PhD-qualified writers specialise in research gap development and methodology.</p>
            <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
              Get expert help with your dissertation →
            </NuxtLink>
          </div>

        </template>
      </div>
    </div>
  </div>
</template>
