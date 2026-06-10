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
  'nursing-essays': [
    { id: 'essay-reflective-nursing', name: 'Reflective Essay — Clinical Practice', level: 'BSN', words: '800–1,200', description: 'Gibbs or Driscoll reflective model applied to a clinical nursing experience.', tags: ['Reflective', 'Gibbs', 'APA 7th'], previewLines: ['Description of the clinical event', 'Feelings and initial reaction', 'Evaluation: what went well and what did not', 'Analysis with reference to nursing theory (ADPIE)', 'Action plan for future practice'] },
    { id: 'essay-evidence-based', name: 'Evidence-Based Practice Essay', level: 'BSN / RN-to-BSN', words: '1,000–1,500', description: 'EBP essay applying a PICOT question to current nursing literature.', tags: ['EBP', 'PICOT', 'APA 7th'], previewLines: ['PICOT question stated clearly', 'Literature search strategy (CINAHL, PubMed)', 'Summary and critical appraisal of evidence', 'Nursing practice implications', 'Conclusion + recommendations'] },
  ],
  'care-plans': [
    { id: 'careplan-nanda', name: 'NANDA-I Care Plan (Full)', level: 'BSN / ADN', words: 'Full document', description: 'Comprehensive care plan: assessment, NANDA diagnoses, NIC interventions, NOC outcomes, and evaluation.', tags: ['NANDA-I', 'NIC', 'NOC', 'ADPIE'], previewLines: ['Patient assessment summary (subjective + objective)', '3 NANDA-I nursing diagnoses, prioritised', 'NIC interventions for each diagnosis', 'NOC outcomes with measurable targets', 'Evaluation criteria and timeline'] },
    { id: 'careplan-soap', name: 'SOAP Note — Primary Care Encounter', level: 'BSN / MSN', words: '500–800', description: 'Clinically accurate SOAP note for a primary care patient encounter, NP format.', tags: ['SOAP', 'NP', 'Primary Care'], previewLines: ['Subjective: chief complaint, HPI, ROS, social history', 'Objective: vital signs, physical exam findings, diagnostics', 'Assessment: differential diagnoses ranked by probability', 'Plan: pharmacological + non-pharmacological interventions, follow-up'] },
  ],
  'capstone-projects': [
    { id: 'capstone-picot', name: 'Capstone — PICOT to Proposal', level: 'BSN', words: '2,000–3,000', description: 'BSN capstone proposal from PICOT question through evidence synthesis to implementation plan.', tags: ['PICOT', 'BSN', 'EBP'], previewLines: ['Background and clinical problem', 'PICOT question formulation', 'Literature search and evidence synthesis', 'EBP framework selection (Iowa Model, ACE Star)', 'Implementation and evaluation plan'] },
    { id: 'capstone-dnp', name: 'DNP Scholarly Project Proposal', level: 'DNP', words: '4,000–6,000', description: 'Full DNP scholarly project proposal through PDSA framework with outcome measures.', tags: ['DNP', 'PDSA', 'QI'], previewLines: ['Problem statement and organisational context', 'Review of evidence (CINAHL, Cochrane)', 'Theoretical framework (Lewin, Kotter)', 'Intervention design and PDSA cycle', 'Outcome measures and evaluation plan', 'Sustainability and dissemination'] },
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
