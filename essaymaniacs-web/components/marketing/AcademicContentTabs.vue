<script setup lang="ts">
const tabs = [
  { id: 'leading',     label: 'Why EssayManiacs?' },
  { id: 'why',         label: 'Why EssayManiacs?' },
  { id: 'dissertation', label: 'Dissertation Help' },
  { id: 'class',       label: 'Admission Essays' },
  { id: 'all',         label: 'All Essay Types' },
]

const active = ref('leading')

const whyItems = [
  { n: '01', title: 'Subject-specialist writers only', body: "Every writer holds at minimum a Master's degree in their field, verified against the issuing institution. PhD-qualified writers handle dissertations and doctoral work." },
  { n: '02', title: 'Direct writer communication', body: 'Message your assigned writer directly through your dashboard. Share files, clarify requirements, and follow progress in real time — no middlemen.' },
  { n: '03', title: 'Consistent writer across revisions', body: 'The same expert who wrote your paper handles all revisions — so your argument, voice, and tone stay consistent throughout.' },
  { n: '04', title: 'Free Turnitin report with every order', body: 'Every paper is checked against major plagiarism databases before delivery. Your originality report is included at no extra charge.' },
  { n: '05', title: 'Zero AI content — verified', body: 'All papers are 100% human-written. A free AI-detection report is available on any order, just ask when placing.' },
  { n: '06', title: 'Strict deadline guarantee', body: "We deliver before your deadline or you don't pay. Our writers only accept orders they can complete on time — no overcommitting." },
  { n: '07', title: 'Grade or money-back guarantee', body: "If the delivered paper doesn't meet your stated requirements after revisions, you're entitled to a full refund — no loopholes, no delays." },
  { n: '08', title: 'Fully legal model paper service', body: 'Our papers are model documents provided for reference and study — the same as a tutoring service or writing centre. Every order includes an academic-use acknowledgement.' },
  { n: '09', title: 'Complete confidentiality', body: 'Your name, institution, and order details are never shared with any third party. We never sell data or display client names.' },
  { n: '10', title: 'Escrow-protected payment', body: 'Your payment is held in escrow and only released to your writer after you approve the completed work. If the paper is not delivered, your money is returned automatically.' },
]

const dissertationItems = [
  { title: 'Research proposal writing', desc: 'Strong proposals with clear research questions, rationale, and preliminary literature review.' },
  { title: 'Literature review chapter', desc: 'Systematic or narrative reviews with gap identification, critical synthesis, and full reference list.' },
  { title: 'Methodology chapter', desc: 'Research design, data collection, and analysis approach justified against your programme\'s framework.' },
  { title: 'Data analysis chapter', desc: 'Quantitative or qualitative analysis using SPSS, R, Python, or NVivo — with written interpretation.' },
  { title: 'Results & discussion chapters', desc: 'Clear presentation of findings linked back to your research questions and existing literature.' },
  { title: 'Conclusion & recommendations', desc: 'Summative conclusions, limitations acknowledgement, and directions for future research.' },
]

const classItems = [
  { title: 'Discussion boards & peer responses', desc: 'Weekly posts written in your voice, graded to rubric — on time, every week.' },
  { title: 'Quizzes and online assessments', desc: 'Subject experts handle assessments with your credentials on any LMS platform.' },
  { title: 'Weekly assignments and coursework', desc: 'Regular assignments delivered on time for the full duration of the module or semester.' },
  { title: 'Progress updates throughout', desc: "You're kept informed at every stage — never in the dark about your standing." },
  { title: 'All subjects covered', desc: 'Business, nursing, psychology, STEM, law, social sciences, and more.' },
  { title: 'Instalment-friendly pricing', desc: 'Pay week-by-week or by module — not the whole semester upfront.' },
]

const paperTypes = [
  'Essays', 'Argumentative Essays', 'Analytical Essays', 'Reflective Essays',
  'Research Papers', 'Dissertations', 'Term Papers', 'Literature Reviews',
  'Case Studies', 'Lab Reports', 'Data Analysis', 'Coursework & Assignments',
  'Annotated Bibliographies', 'Book Reports', 'Admission Essays', 'Scholarship Essays',
  'Personal Statements', 'Creative Writing', 'Proofreading & Editing', 'Business Reports',
  'Presentations', 'Compare & Contrast Essays', 'Narrative Essays', 'Discussion Posts',
]
</script>

<template>
  <section class="bg-white py-16">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

      <!-- Tab strip — scrollable on mobile -->
      <div class="overflow-x-auto" style="scrollbar-width: none;">
        <div class="flex min-w-max gap-1 rounded-2xl bg-slate-100 p-1.5">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="shrink-0 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all"
            :class="active === tab.id
              ? 'bg-white text-brand-700 shadow-sm'
              : 'text-slate-500 hover:text-slate-800'"
            @click="active = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab content -->
      <div class="mt-10">

        <!-- Leading Service -->
        <div v-if="active === 'leading'" class="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-3xl font-bold text-slate-900">The Essay Writing Service for Subject Maniacs</h2>
            <p class="mt-5 leading-relaxed text-slate-600">
              EssayManiacs connects students with qualified, subject-specialist writers — not generic freelancers. Every writer holds at minimum a Master's degree in their field, with many holding PhDs and active research or teaching experience.
            </p>
            <p class="mt-4 leading-relaxed text-slate-600">
              Our writers understand the academic standards behind every assignment. When your dissertation needs a PRISMA-compliant systematic review, when your methodology chapter must justify a specific ontological position, when your research paper requires current peer-reviewed sources — your writer has done this professionally, not just as a student.
            </p>
            <p class="mt-4 leading-relaxed text-slate-600">
              We're rated <strong class="text-slate-900">4.8 out of 5 stars</strong> across 20,000+ completed essays and papers. Our fastest turnaround is 2 hours — for assignments that need to be submitted today.
            </p>
            <NuxtLink to="/order" class="btn-primary mt-8 inline-flex px-8 py-3.5">Place an order — from $10/page</NuxtLink>
          </div>
          <div class="grid grid-cols-2 content-start gap-4">
            <div
              v-for="item in [
                { icon: 'graduation-cap', title: 'Master\'s & PhD writers', desc: 'Subject-specialist credentials verified' },
                { icon: 'shield-check',   title: 'Free Turnitin report',    desc: 'Plagiarism-checked before every delivery' },
                { icon: 'zap',            title: '2-hour turnaround',       desc: 'Fastest delivery for urgent papers' },
                { icon: 'trophy',         title: 'Grade or money back',     desc: 'Full refund if requirements aren\'t met' },
                { icon: 'bot',            title: 'Zero AI content',         desc: '100% human-written by a real expert' },
                { icon: 'refresh-cw',     title: 'Unlimited revisions',     desc: 'Within the revision window, always free' },
              ]"
              :key="item.title"
              class="rounded-2xl border border-slate-100 bg-slate-50 p-4"
            >
              <div class="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-brand-100">
                <Icon :name="item.icon" class="h-4 w-4 text-brand-600" />
              </div>
              <p class="text-sm font-semibold text-slate-900">{{ item.title }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ item.desc }}</p>
            </div>
          </div>
        </div>

        <!-- Why EssayManiacs -->
        <div v-else-if="active === 'why'">
          <h2 class="font-serif text-3xl font-bold text-slate-900">Why EssayManiacs?</h2>
          <p class="mt-3 max-w-2xl text-slate-500">Ten things that make EssayManiacs different from every other writing service you've seen.</p>
          <div class="mt-8 grid gap-5 sm:grid-cols-2">
            <div v-for="item in whyItems" :key="item.n" class="flex gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-5">
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
                {{ item.n }}
              </div>
              <div>
                <h3 class="font-semibold text-slate-900">{{ item.title }}</h3>
                <p class="mt-1.5 text-sm leading-relaxed text-slate-500">{{ item.body }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Dissertation Help -->
        <div v-else-if="active === 'dissertation'" class="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-3xl font-bold text-slate-900">Dissertation Help from Proposal to Final Chapter</h2>
            <p class="mt-5 leading-relaxed text-slate-600">
              The dissertation is the most demanding piece of academic writing you will undertake — and one small weakness in any chapter can hold back the entire project. Our PhD-qualified writers have written, supervised, and edited dissertations across every discipline.
            </p>
            <p class="mt-4 leading-relaxed text-slate-600">
              We support the full dissertation journey: research proposal, systematic literature search, methodology design, data collection and analysis, results write-up, discussion, and final editing. We also handle viva preparation if needed.
            </p>
            <p class="mt-4 leading-relaxed text-slate-600">
              Chapter-by-chapter delivery lets you review and incorporate supervisor feedback before the next chapter is written — so the final document is coherent throughout.
            </p>
            <NuxtLink to="/services/dissertations" class="btn-primary mt-8 inline-flex px-8 py-3.5">Get dissertation help →</NuxtLink>
          </div>
          <div class="space-y-4">
            <div
              v-for="item in dissertationItems"
              :key="item.title"
              class="flex items-start gap-4 rounded-xl border border-slate-100 bg-slate-50 p-4"
            >
              <Icon name="graduation-cap" class="mt-0.5 h-5 w-5 shrink-0 text-brand-600" />
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ item.title }}</p>
                <p class="mt-0.5 text-xs text-slate-500">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Class Support -->
        <div v-else-if="active === 'class'" class="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-3xl font-bold text-slate-900">Full Course &amp; Coursework Support Bundles</h2>
            <p class="mt-5 leading-relaxed text-slate-600">
              Balancing a full course load with work, family, and life is genuinely hard. We help students who are falling behind or need sustained support across a module, semester, or full course.
            </p>
            <p class="mt-4 leading-relaxed text-slate-600">
              Our full-class support assigns one dedicated expert to your entire course. They handle every discussion post, assignment, quiz, and exam — freeing you to focus on what matters without falling behind academically.
            </p>
            <p class="mt-4 leading-relaxed text-slate-600">
              We work across all major learning management systems: Canvas, Blackboard, Moodle, McGraw-Hill Connect, and more. Business, nursing, psychology, STEM, law, and social sciences all covered.
            </p>
            <NuxtLink to="/class-support" class="btn-primary mt-8 inline-flex px-8 py-3.5">Get class support →</NuxtLink>
          </div>
          <div class="space-y-4">
            <div
              v-for="item in classItems"
              :key="item.title"
              class="flex items-start gap-4 rounded-xl border border-slate-100 bg-slate-50 p-4"
            >
              <div class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600">
                <Icon name="check" class="h-3 w-3 text-white" />
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ item.title }}</p>
                <p class="mt-0.5 text-xs text-slate-500">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- All Paper Types -->
        <div v-else-if="active === 'all'">
          <h2 class="font-serif text-3xl font-bold text-slate-900">All Essay &amp; Assignment Types</h2>
          <p class="mt-3 max-w-2xl text-slate-500">If it's on your assignment list, we write it. Every essay comes with a free plagiarism report and is written by a credentialed subject specialist.</p>
          <div class="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            <NuxtLink
              v-for="pt in paperTypes"
              :key="pt"
              to="/order"
              class="flex items-center gap-2.5 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700 transition-colors hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700"
            >
              <Icon name="check-circle" class="h-4 w-4 shrink-0 text-brand-500" />
              {{ pt }}
            </NuxtLink>
          </div>
          <div class="mt-8 rounded-2xl bg-brand-900 p-6 text-center">
            <p class="text-base font-semibold text-white">Don't see your assignment type?</p>
            <p class="mt-1 text-sm text-brand-300">Contact us — if it's academic writing, we almost certainly cover it.</p>
            <NuxtLink to="/contact" class="mt-4 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-2.5 text-sm font-bold text-brand-700 transition-colors hover:bg-brand-50">
              Ask us about your assignment
            </NuxtLink>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>
