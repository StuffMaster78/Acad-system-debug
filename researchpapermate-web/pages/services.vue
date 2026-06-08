<script setup lang="ts">
const app = useAppUrl()

const paperTypes = [
  {
    id: 'research-papers',
    icon: '📄',
    title: 'Research Papers',
    desc: 'Original, fully referenced papers built on credible academic sources. Any citation style — APA, MLA, Chicago, Harvard, Vancouver.',
    bullets: ['Primary and secondary source integration', 'Plagiarism-free with Turnitin report', 'Any citation style'],
  },
  {
    id: 'essays',
    icon: '✍️',
    title: 'Essays',
    desc: 'Argumentative, analytical, descriptive, narrative, and reflective essays written to your exact brief.',
    bullets: ['High school through PhD level', 'Strict deadline adherence', 'Free revisions in review window'],
  },
  {
    id: 'dissertations',
    icon: '🎓',
    title: 'Dissertations & Theses',
    desc: 'End-to-end dissertation support — from proposal to final defended version.',
    bullets: ['Chapter-by-chapter delivery', 'Methodology and data analysis', 'Supervisor feedback integration'],
  },
  {
    id: 'case-studies',
    icon: '📋',
    title: 'Case Studies',
    desc: 'In-depth business, medical, and social science case study analysis with structured arguments and evidence.',
    bullets: ['Business, law, nursing, social work', 'Problem–solution–evaluation structure', 'Real-world source integration'],
  },
  {
    id: 'coursework',
    icon: '📚',
    title: 'Coursework & Assignments',
    desc: 'Regular weekly assignments, problem sets, and module work handled consistently.',
    bullets: ['Recurring order discounts', 'Consistent assigned writer', 'Subject-matter specialists'],
  },
  {
    id: 'data-analysis',
    icon: '📊',
    title: 'Data Analysis',
    desc: 'Quantitative and qualitative analysis with full write-up, charts, and interpretation.',
    bullets: ['SPSS, R, Python, Excel', 'Charts and tables included', 'Methodology chapter support'],
  },
  {
    id: 'literature-review',
    icon: '🔍',
    title: 'Literature Reviews',
    desc: 'Systematic, narrative, or scoping reviews with proper gap identification and synthesis.',
    bullets: ['PRISMA flow diagrams available', 'Database search strategy documented', 'Gap identification and critique'],
  },
  {
    id: 'lab-reports',
    icon: '🔬',
    title: 'Lab Reports',
    desc: 'Properly structured scientific lab reports with all standard sections.',
    bullets: ['Introduction, method, results, discussion', 'Correct scientific notation', 'Graph and table formatting'],
  },
  {
    id: 'presentations',
    icon: '📽️',
    title: 'Presentations & Speeches',
    desc: 'PowerPoint presentations and speaker notes, or full speech scripts for academic and professional settings.',
    bullets: ['Slide design guidance', 'Speaker notes included', 'Timed to your delivery slot'],
  },
]

const subjectAreas = [
  {
    area: 'STEM',
    subjects: ['Biology', 'Chemistry', 'Physics', 'Mathematics', 'Statistics', 'Engineering', 'Computer Science', 'Environmental Science'],
  },
  {
    area: 'Business & Finance',
    subjects: ['Accounting', 'Finance', 'Marketing', 'HR Management', 'Supply Chain', 'Economics', 'Entrepreneurship', 'Business Law'],
  },
  {
    area: 'Healthcare & Social Sciences',
    subjects: ['Nursing', 'Public Health', 'Psychology', 'Sociology', 'Social Work', 'Counseling', 'Pharmacology'],
  },
  {
    area: 'Humanities & Law',
    subjects: ['History', 'Literature', 'Philosophy', 'Law', 'Political Science', 'Cultural Studies', 'Media Studies', 'Education'],
  },
]

const usps = [
  { icon: '💬', title: 'Direct writer communication', desc: 'Message your writer throughout the order — share files, ask questions, give feedback.' },
  { icon: '🧬', title: 'Style-matching',              desc: 'Upload a sample of your own writing. Your expert will match your voice.' },
  { icon: '⚡', title: '2-hour minimum turnaround',   desc: 'Need it urgently? We can deliver in as little as 2 hours for shorter assignments.' },
  { icon: '🛡️', title: 'Anti-plagiarism guarantee',   desc: 'Every paper is checked against major databases. Turnitin report available on request.' },
  { icon: '🎯', title: 'Grade or money back',         desc: "We stand behind our work. If the grade isn't met, we refund or rewrite." },
  { icon: '🔐', title: 'Complete privacy',             desc: 'Your identity and order details are never shared with any third party.' },
]

useSeoMeta({
  title: 'Academic Writing Services — 100+ Subjects',
  description: 'Expert help with research papers, essays, dissertations, case studies, lab reports, data analysis, and more — across 100+ academic subjects.',
})

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Academic Writing Services',
      itemListElement: paperTypes.map((s, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        name: s.title,
        description: s.desc,
      })),
    }),
  }],
})
</script>

<template>
  <div>
    <section class="bg-gradient-to-br from-brand-900 to-brand-700 py-20 text-center">
      <div class="section py-0">
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">Academic Writing Services</h1>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-brand-100">
          Expert writers across every discipline — STEM, business, law, healthcare, humanities.
          If it needs to be written, we cover it.
        </p>
        <a :href="app.register" class="btn-primary mt-8 bg-white text-brand-700 hover:bg-brand-50 px-8 py-3.5 text-base">
          Get started from $15/page
        </a>
      </div>
    </section>

    <section class="section">
      <h2 class="section-heading text-center">Paper types we handle</h2>
      <div class="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="s in paperTypes" :id="s.id" :key="s.id" class="card">
          <div class="mb-4 text-4xl">{{ s.icon }}</div>
          <h2 class="text-lg font-semibold text-slate-900">{{ s.title }}</h2>
          <p class="mt-2 text-sm text-slate-600 leading-relaxed">{{ s.desc }}</p>
          <ul class="mt-4 space-y-1.5">
            <li v-for="b in s.bullets" :key="b" class="flex items-start gap-2 text-sm text-slate-500">
              <span class="mt-0.5 font-bold text-brand-500">✓</span>{{ b }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <section class="bg-slate-50">
      <div class="section">
        <h2 class="section-heading text-center">100+ subjects covered</h2>
        <p class="section-sub text-center">Writers hired for subject-matter expertise, not just writing ability.</p>
        <div class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="group in subjectAreas" :key="group.area">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">{{ group.area }}</h3>
            <ul class="space-y-2">
              <li v-for="sub in group.subjects" :key="sub"
                class="rounded-lg border border-brand-100 bg-white px-3 py-2 text-sm text-slate-700">
                {{ sub }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-white">
      <div class="section">
        <h2 class="section-heading text-center">Why ResearchPaperMate?</h2>
        <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="usp in usps" :key="usp.title" class="flex gap-4">
            <span class="mt-1 text-2xl">{{ usp.icon }}</span>
            <div>
              <h3 class="font-semibold text-slate-900">{{ usp.title }}</h3>
              <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ usp.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="bg-brand-700 py-16 text-center">
      <h2 class="font-serif text-3xl font-bold text-white">Not sure what you need?</h2>
      <p class="mt-4 text-brand-200">Place an order, describe your task, and we'll match the right expert.</p>
      <a :href="app.register" class="btn-primary mt-8 bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base">
        Start your order
      </a>
    </section>
  </div>
</template>
