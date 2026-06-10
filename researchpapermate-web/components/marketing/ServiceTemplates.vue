<script setup lang="ts">
/**
 * ServiceTemplates — browse sample templates for a service type.
 *
 * Static fallback data shown immediately; replaced by CMS templates when
 * staff publish Template pages in Wagtail for this service slug.
 * "Use this template" pre-fills the order form via query params.
 */

const props = defineProps<{ serviceSlug: string; serviceName: string }>()

interface Template {
  id: string
  name: string
  level: string
  words: string
  description: string
  tags: string[]
  previewLines: string[]
}

// Static templates per service slug — CMS overrides when available
const TEMPLATES: Record<string, Template[]> = {
  'essays': [
    { id: 'essay-argumentative-social', name: 'Argumentative Essay — Social Issues', level: 'Undergraduate', words: '1,000–1,500', description: 'Three-part structure: claim, evidence, rebuttal. Strong thesis on a current social topic.', tags: ['Argumentative', 'APA', 'Social Sciences'], previewLines: ['Thesis statement in final sentence of intro', 'Body: 3 paragraphs, each with claim + evidence + analysis', 'Counterargument addressed in paragraph 3', 'Conclusion restates thesis + implications'] },
    { id: 'essay-analytical-literature', name: 'Analytical Essay — Literature', level: 'Undergraduate', words: '800–1,200', description: 'Literary analysis essay examining theme, character, or style in a specific text.', tags: ['Analytical', 'MLA', 'Literature'], previewLines: ['Intro with hook + context + thesis', 'Body paragraphs each analyse one literary element', 'Textual evidence with close reading', 'Conclusion synthesises analysis'] },
    { id: 'essay-reflective-placement', name: 'Reflective Essay — Work Placement', level: 'Undergraduate / Postgrad', words: '600–1,000', description: 'Gibbs reflective cycle applied to a professional or clinical placement experience.', tags: ['Reflective', 'Gibbs Cycle', 'Harvard'], previewLines: ['Description: what happened', 'Feelings: emotional response', 'Evaluation: what worked and what didn\'t', 'Analysis: why it happened + what it means', 'Action plan: what to do differently'] },
  ],
  'dissertations': [
    { id: 'diss-proposal-social', name: 'Dissertation Proposal — Social Science', level: "Master's", words: '1,500–2,000', description: 'Full proposal with research question, rationale, literature gap, methodology outline, and timeline.', tags: ['Proposal', 'APA', 'Social Science'], previewLines: ['Background and context', 'Research question and aims', 'Preliminary literature review', 'Proposed methodology', 'Ethical considerations', 'Timeline and chapter plan'] },
    { id: 'diss-litreview-business', name: 'Literature Review Chapter — Business', level: "Master's / PhD", words: '3,000–4,000', description: 'Thematic synthesis of 20–30 sources, with critical gap identification and theoretical framework.', tags: ['Lit Review', 'Business', 'Harvard'], previewLines: ['Search strategy documented', 'Themes identified and synthesised', 'Critical comparison of major authors', 'Gap identification for research rationale'] },
  ],
  'research-papers': [
    { id: 'rp-apa-stem', name: 'Research Paper — STEM (APA)', level: 'Undergraduate', words: '2,000–3,000', description: 'Structured research paper with abstract, introduction, methodology, results discussion, and references.', tags: ['APA', 'STEM', 'Empirical'], previewLines: ['Abstract: 150–250 words', 'Introduction with research question', 'Methodology section', 'Results and discussion', 'Conclusion and future research', 'Full reference list'] },
    { id: 'rp-mla-humanities', name: 'Research Paper — Humanities (MLA)', level: 'Undergraduate', words: '1,500–2,500', description: 'Argumentative research paper with primary and secondary sources in MLA format.', tags: ['MLA', 'Humanities', 'Argumentative'], previewLines: ['Thesis-driven introduction', 'Body paragraphs with integrated quotes', 'Works Cited page in MLA 9th edition'] },
  ],
  'admission-essays': [
    { id: 'ae-common-app', name: 'Common App Personal Statement', level: 'Undergraduate', words: '650', description: 'Narrative personal statement for US college Common App — showing character, not just achievements.', tags: ['Common App', 'Personal', 'Narrative'], previewLines: ['Opens with a specific scene, not a general statement', 'Tells a story that reveals character', 'Connects to future goals in the conclusion', 'Sounds like the applicant, not a template'] },
    { id: 'ae-graduate-sop', name: 'Graduate School Statement of Purpose', level: "Master's / PhD", words: '500–1,000', description: 'SOP for graduate programme application covering academic background, research interests, and programme fit.', tags: ['SOP', 'Graduate', 'Research'], previewLines: ['Academic background + key achievements', 'Research interests and gaps you want to address', 'Why this specific programme and supervisor', 'Career trajectory after graduation'] },
    { id: 'ae-mba-goals', name: 'MBA Goals Essay', level: 'Postgraduate', words: '500–800', description: 'Short-term and long-term goals essay for MBA applications, with programme-specific fit paragraph.', tags: ['MBA', 'Goals', 'Specific'], previewLines: ['Concrete short-term goal post-MBA', 'Longer-term career vision', 'Why this MBA programme specifically', 'What you bring to the cohort'] },
  ],
  'scholarship-essays': [
    { id: 'se-merit', name: 'Merit Scholarship Essay', level: 'Any', words: '250–500', description: 'Concise essay demonstrating academic achievement, leadership, and community impact.', tags: ['Merit', 'Leadership', 'Community'], previewLines: ['Specific achievement + context', 'Leadership example with outcome', 'Community impact with evidence', 'Future plans tied to scholarship purpose'] },
  ],
  'personal-statements': [
    { id: 'ps-law', name: 'Law School Personal Statement', level: 'Postgraduate', words: '500–700', description: 'Personal statement for law school application connecting life experience to legal career.', tags: ['Law', 'Personal', 'Narrative'], previewLines: ['Opening anecdote that reveals your interest in law', 'Academic and professional background', 'Why law — specific moment of decision', 'Why this school specifically'] },
  ],
}

const cmsTemplates = ref<Template[]>([]) // future: fetch from /cms-api/service-templates/
const staticTemplates = computed(() => TEMPLATES[props.serviceSlug] ?? [])
const templates = computed(() => cmsTemplates.value.length ? cmsTemplates.value : staticTemplates.value)

const expanded = ref<string | null>(null)

function useTemplate(t: Template) {
  const query = new URLSearchParams({
    type: 'paper',
    template: t.id,
    level: t.level,
  })
  window.location.href = `/order?${query.toString()}`
}
</script>

<template>
  <section v-if="templates.length" class="border-t border-slate-100 bg-white py-14">
    <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">

      <div class="mb-8 flex items-end justify-between gap-4">
        <div>
          <p class="mb-1 text-xs font-bold uppercase tracking-widest text-brand-600">Templates</p>
          <h2 class="font-serif text-2xl font-bold text-slate-900">Browse {{ serviceName }} templates</h2>
          <p class="mt-1.5 text-sm text-slate-600">Pick a structure that fits your assignment — then we adapt it to your specific brief.</p>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="t in templates"
          :key="t.id"
          class="group relative flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white transition-all hover:border-brand-300 hover:shadow-sm"
        >
          <!-- Header -->
          <div class="border-b border-slate-100 p-5">
            <div class="mb-3 flex flex-wrap gap-1.5">
              <span
                v-for="tag in t.tags"
                :key="tag"
                class="rounded-full bg-brand-50 px-2 py-0.5 text-[10px] font-semibold text-brand-700"
              >{{ tag }}</span>
            </div>
            <h3 class="font-semibold leading-snug text-slate-900">{{ t.name }}</h3>
            <p class="mt-1 text-xs text-slate-500">{{ t.level }} · {{ t.words }} words</p>
          </div>

          <!-- Body -->
          <div class="flex flex-1 flex-col p-5">
            <p class="text-sm leading-relaxed text-slate-600">{{ t.description }}</p>

            <!-- Collapsible preview -->
            <button
              class="mt-3 flex items-center gap-1 text-xs font-semibold text-brand-600 hover:underline"
              @click="expanded = expanded === t.id ? null : t.id"
            >
              <svg
                class="h-3.5 w-3.5 transition-transform"
                :class="expanded === t.id ? 'rotate-90' : ''"
                fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
              ><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
              {{ expanded === t.id ? 'Hide structure' : 'View structure' }}
            </button>

            <Transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0 max-h-0"
              enter-to-class="opacity-100 max-h-60"
              leave-active-class="transition-all duration-150 ease-in"
              leave-from-class="opacity-100 max-h-60"
              leave-to-class="opacity-0 max-h-0"
            >
              <ul v-if="expanded === t.id" class="mt-3 overflow-hidden space-y-1.5 rounded-xl bg-slate-50 p-4">
                <li
                  v-for="line in t.previewLines"
                  :key="line"
                  class="flex items-start gap-2 text-xs text-slate-600"
                >
                  <span class="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500"></span>
                  {{ line }}
                </li>
              </ul>
            </Transition>

            <!-- CTA -->
            <button
              class="mt-5 w-full rounded-xl bg-brand-600 py-2.5 text-sm font-bold text-white transition-colors hover:bg-brand-700"
              @click="useTemplate(t)"
            >
              Use this template →
            </button>
          </div>
        </div>
      </div>

      <p class="mt-6 text-center text-xs text-slate-400">
        Templates are starting points — your writer adapts the structure to your exact brief, rubric, and institution.
      </p>
    </div>
  </section>
</template>
