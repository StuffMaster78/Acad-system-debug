<script setup lang="ts">
const tabs = [
  { id: 'leading',  label: 'Leading Service' },
  { id: 'why',      label: 'Why NurseMyGrade?' },
  { id: 'class',    label: 'Class Help Bundles' },
  { id: 'admissions', label: 'Nursing School' },
  { id: 'capstone', label: 'Capstone Help' },
  { id: 'all',      label: 'All Paper Types' },
]

const active = ref('leading')

const admissionTips = [
  { n: '1', title: 'A specific moment that defines your calling', body: "Not a generic 'I want to help people' — a real, vivid scene from your life that explains why nursing, why now, why you." },
  { n: '2', title: "Alignment with the programme's mission", body: 'Each school has specific values: community focus, research emphasis, leadership track. Your statement should mirror them.' },
  { n: '3', title: 'Clinical evidence, not just intent', body: 'Admissions committees want to see that you understand what nursing work actually involves — not just what you imagine it to be.' },
  { n: '4', title: 'A clear picture of your future self', body: 'Where are you going? FNP? Public health? Oncology? Specificity signals commitment — vagueness signals uncertainty.' },
]

const paperTypes = [
  'Nursing Essays', 'Care Plans (NANDA/NIC/NOC)', 'SOAP Notes',
  'Capstone Projects', 'Research Papers', 'Case Studies',
  'Concept Maps', 'Nursing Dissertations', 'Coursework & Assignments',
  'Shadow Health DCEs', 'iHuman Virtual Patients', 'Reflective Journals',
  'Annotated Bibliographies', 'Literature Reviews', 'Discussion Posts',
  'Nursing Presentations', 'Admission Essays', 'Scholarship Essays',
  'ATI Assignments', 'NCLEX-Style Prep', 'Pharmacology Papers',
  'Pathophysiology Reports', 'Community Health Assessments', 'Evidence-Based Practice Papers',
]

const whyItems = [
  {
    n: '01',
    title: 'All writers hold active nursing credentials',
    body: 'Every writer on our platform holds at minimum a BSN degree with verified clinical experience. We screen for MSN and DNP credentials for advanced work — you\'ll always see your writer\'s qualifications before your order begins.',
  },
  {
    n: '02',
    title: 'Expert nursing blog and resource library',
    body: 'Clients get access to our growing library of nursing study guides, APA 7th formatting templates, NANDA diagnosis lists, and clinical writing resources — free with every order.',
  },
  {
    n: '03',
    title: 'Direct writer communication',
    body: 'Message your assigned writer directly through your dashboard. Share additional files, clarify requirements, and follow progress in real time — no middlemen, no delays.',
  },
  {
    n: '04',
    title: 'Consistent writer across revisions',
    body: 'The same nurse who wrote your paper handles all revisions. That means your clinical voice, terminology, and tone stay consistent throughout — not patched together by different people.',
  },
  {
    n: '05',
    title: 'Strict deadline guarantee',
    body: 'We deliver before the deadline or you don\'t pay. Our nursing writers take on only what they can deliver on time — overcommitting is how other services fail. We don\'t.',
  },
  {
    n: '06',
    title: 'Fully legal model paper service',
    body: 'Our papers are model documents provided for reference and study — the same as using a writing centre, tutor, or sample essay service. Every order includes an academic use acknowledgement.',
  },
  {
    n: '07',
    title: 'Country-specific clinical references',
    body: 'Whether you follow US, UK, Australian, or Canadian nursing guidelines, your writer uses the appropriate clinical frameworks, drug names, measurement units, and citation conventions.',
  },
  {
    n: '08',
    title: 'Grade or money-back guarantee',
    body: 'If the delivered paper doesn\'t meet your stated requirements after revisions, you\'re entitled to a full refund. We stand behind every order — no loopholes, no stalling.',
  },
  {
    n: '09',
    title: 'Complete confidentiality',
    body: 'Your name, institution, and order details are never shared with any third party. We don\'t sell data, display client names, or publish samples without explicit permission.',
  },
  {
    n: '10',
    title: 'Escrow-protected payment',
    body: 'Your payment is held in escrow and only released to your writer after you approve the completed work. If the paper isn\'t delivered, your money is returned automatically.',
  },
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

      <!-- ── Tab content ────────────────────────────────────────────── -->
      <div class="mt-10">

        <!-- Leading Service -->
        <div v-if="active === 'leading'" class="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-3xl font-bold text-slate-900">Leading Nursing Paper Writing Service</h2>
            <p class="mt-5 text-slate-600 leading-relaxed">
              NurseMyGrade connects nursing students with qualified nurses — not generic academic writers. Every writer on our platform holds a BSN degree at minimum, with many holding MSN and DNP credentials and years of active clinical practice.
            </p>
            <p class="mt-4 text-slate-600 leading-relaxed">
              Our nursing writers understand the clinical context behind every assignment. When your care plan references NANDA-I diagnoses, when your SOAP note needs ICD-10 awareness, when your capstone project requires a PICOT question — your writer has done this in practice, not just in theory.
            </p>
            <p class="mt-4 text-slate-600 leading-relaxed">
              We're rated <strong class="text-slate-900">4.98 out of 5 stars</strong> across 9,800+ completed nursing papers. Our fastest turnaround is 3 hours — for those clinical write-ups that need to be submitted tonight.
            </p>
            <NuxtLink to="/order" class="btn-primary mt-8 inline-flex px-8 py-3.5">Place an order — from $24/page</NuxtLink>
          </div>
          <div class="grid grid-cols-2 gap-4 content-start">
            <div v-for="item in [
              { icon: 'stethoscope',  title: 'BSN/MSN/DNP writers',     desc: 'Clinically credentialed nursing professionals' },
              { icon: 'shield-check', title: 'Free Turnitin report',     desc: 'Plagiarism-checked before every delivery' },
              { icon: 'zap',          title: '3-hour turnaround',        desc: 'Fastest delivery for urgent nursing papers' },
              { icon: 'trophy',       title: 'Grade or money back',      desc: 'Full refund if requirements aren\'t met' },
              { icon: 'bot',          title: 'Zero AI content',          desc: '100% human-written by a qualified nurse' },
              { icon: 'refresh-cw',   title: 'Unlimited revisions',      desc: 'Within the revision window, always free' },
            ]" :key="item.title" class="rounded-2xl border border-slate-100 bg-slate-50 p-4">
              <div class="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-brand-100">
                <Icon :name="item.icon" class="h-4 w-4 text-brand-600" />
              </div>
              <p class="text-sm font-semibold text-slate-900">{{ item.title }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ item.desc }}</p>
            </div>
          </div>
        </div>

        <!-- Why NurseMyGrade -->
        <div v-else-if="active === 'why'">
          <h2 class="font-serif text-3xl font-bold text-slate-900">Why NurseMyGrade?</h2>
          <p class="mt-3 text-slate-500 max-w-2xl">Ten reasons nursing students choose us over generic academic writing services.</p>
          <div class="mt-8 grid gap-5 sm:grid-cols-2">
            <div v-for="item in whyItems" :key="item.n" class="flex gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-5">
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
                {{ item.n }}
              </div>
              <div>
                <h3 class="font-semibold text-slate-900">{{ item.title }}</h3>
                <p class="mt-1.5 text-sm text-slate-500 leading-relaxed">{{ item.body }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Class Help Bundles -->
        <div v-else-if="active === 'class'" class="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-3xl font-bold text-slate-900">Entire Class &amp; Coursework Help Bundles</h2>
            <p class="mt-5 text-slate-600 leading-relaxed">
              Nursing programmes are demanding. Between clinical rotations, simulation labs, skills checkoffs, and a full courseload, many nursing students find themselves overwhelmed by online coursework. We help.
            </p>
            <p class="mt-4 text-slate-600 leading-relaxed">
              Our full-class support assigns one dedicated nursing expert to your entire course for the semester. They handle every discussion post, every weekly assignment, every quiz and exam — freeing you to focus on your clinical hours without falling behind on the academic side.
            </p>
            <p class="mt-4 text-slate-600 leading-relaxed">
              We've helped students through Pathophysiology, Pharmacology, Medical-Surgical Nursing, Psychiatric Nursing, Community Health, and advanced NP courses. We work on all major learning platforms: Canvas, Blackboard, Moodle, McGraw-Hill Connect, and more.
            </p>
            <NuxtLink to="/class-support" class="btn-primary mt-8 inline-flex px-8 py-3.5">Get class support →</NuxtLink>
          </div>
          <div class="space-y-4">
            <div v-for="item in [
              { title: 'Discussion boards & peer responses', desc: 'Weekly posts written in your voice, graded to rubric.' },
              { title: 'Quizzes and proctored exams', desc: 'Subject experts handle assessments with your credentials.' },
              { title: 'Weekly assignments and case studies', desc: 'On-time, every week, for the full duration of the course.' },
              { title: 'Progress updates throughout', desc: 'You\'re kept informed — never in the dark about your standing.' },
              { title: 'All nursing subjects covered', desc: 'Pharm, Patho, Med-Surg, Psych, Community Health, FNP and more.' },
              { title: 'Instalment-friendly pricing', desc: 'Pay week-by-week or by module — not the whole semester upfront.' },
            ]" :key="item.title" class="flex items-start gap-4 rounded-xl border border-slate-100 bg-slate-50 p-4">
              <div class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600">
                <Icon name="check" class="h-3 w-3 text-white" />
              </div>
              <div>
                <p class="font-semibold text-slate-900 text-sm">{{ item.title }}</p>
                <p class="mt-0.5 text-xs text-slate-500">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Nursing School Admissions -->
        <div v-else-if="active === 'admissions'" class="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-3xl font-bold text-slate-900">Let's Get You Into Nursing School</h2>
            <p class="mt-5 text-slate-600 leading-relaxed">
              Your nursing school personal statement is the single piece of writing that determines whether you get interviewed — and whether you get accepted. Our writers are nurses who have been through the admissions process themselves.
            </p>
            <p class="mt-4 text-slate-600 leading-relaxed">
              We write personal statements for BSN, MSN, DNP, and NP programmes. We also help with scholarship essays, "why nursing" statements, clinical experience narratives, and letters of intent. Every document is tailored to the specific programme, its values, and what its admissions committee looks for.
            </p>
            <div class="mt-6 rounded-2xl bg-brand-50 border border-brand-100 p-5">
              <p class="text-sm font-semibold text-brand-800">What we write for admissions:</p>
              <ul class="mt-3 space-y-2 text-sm text-brand-700">
                <li class="flex items-center gap-2"><Icon name="check" class="h-3.5 w-3.5 text-brand-500 shrink-0" /> Personal statement / statement of purpose</li>
                <li class="flex items-center gap-2"><Icon name="check" class="h-3.5 w-3.5 text-brand-500 shrink-0" /> "Why I want to be a nurse" essays</li>
                <li class="flex items-center gap-2"><Icon name="check" class="h-3.5 w-3.5 text-brand-500 shrink-0" /> Scholarship and grant application essays</li>
                <li class="flex items-center gap-2"><Icon name="check" class="h-3.5 w-3.5 text-brand-500 shrink-0" /> Clinical experience narratives</li>
                <li class="flex items-center gap-2"><Icon name="check" class="h-3.5 w-3.5 text-brand-500 shrink-0" /> Letter of intent for advanced programmes</li>
              </ul>
            </div>
            <NuxtLink to="/contact" class="btn-primary mt-8 inline-flex px-8 py-3.5">Discuss your admission essay →</NuxtLink>
          </div>
          <div class="rounded-2xl border border-slate-100 bg-slate-50 p-7">
            <h3 class="font-serif text-xl font-bold text-slate-900 mb-5">What makes a strong nursing personal statement?</h3>
            <div class="space-y-5">
              <div v-for="tip in admissionTips" :key="tip.n" class="flex gap-3">
                <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white">{{ tip.n }}</div>
                <div>
                  <p class="font-semibold text-slate-900 text-sm">{{ tip.title }}</p>
                  <p class="mt-1 text-xs text-slate-500 leading-relaxed">{{ tip.body }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Capstone Help -->
        <div v-else-if="active === 'capstone'" class="grid gap-10 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-3xl font-bold text-slate-900">Your Nursing Capstone is Sorted Here</h2>
            <p class="mt-5 text-slate-600 leading-relaxed">
              The nursing capstone is the culminating academic project of your BSN, MSN, or DNP programme — and one of the most demanding pieces of writing you'll ever be asked to complete. Our DNP and PhD-level nursing writers have written, supervised, and defended capstones across every nursing speciality.
            </p>
            <p class="mt-4 text-slate-600 leading-relaxed">
              We support the full capstone journey: PICOT question development, systematic literature search, evidence appraisal using the Iowa Model, ACE Star, or your programme's preferred framework, implementation planning, and the final manuscript. We also write the accompanying PowerPoint presentation if required.
            </p>
            <NuxtLink to="/services/capstone-projects" class="btn-primary mt-8 inline-flex px-8 py-3.5">Get capstone help →</NuxtLink>
          </div>
          <div class="space-y-4">
            <div v-for="item in [
              { title: 'PICOT question development', desc: 'We help you build a focused, researchable clinical question from your area of interest.' },
              { title: 'Systematic literature search & appraisal', desc: 'Full database search (CINAHL, PubMed, Cochrane) with evidence tables and appraisal tools.' },
              { title: 'EBP framework application', desc: 'Iowa Model, ACE Star, Johns Hopkins — we work within your programme\'s required framework.' },
              { title: 'Implementation & evaluation chapter', desc: 'From planning through PDSA cycles to outcome measurement and sustainability.' },
              { title: 'PowerPoint presentation slides', desc: 'Capstone defence slides built to your programme\'s slide count and formatting requirements.' },
              { title: 'Chapter-by-chapter delivery', desc: 'Review each chapter before the next is written — full supervisor feedback integration.' },
            ]" :key="item.title" class="flex items-start gap-4 rounded-xl border border-slate-100 bg-slate-50 p-4">
              <Icon name="graduation-cap" class="mt-0.5 h-5 w-5 shrink-0 text-brand-600" />
              <div>
                <p class="font-semibold text-slate-900 text-sm">{{ item.title }}</p>
                <p class="mt-0.5 text-xs text-slate-500">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- All Paper Types -->
        <div v-else-if="active === 'all'">
          <h2 class="font-serif text-3xl font-bold text-slate-900">All Nursing Papers &amp; Homework Types</h2>
          <p class="mt-3 text-slate-500 max-w-2xl">If it's on your assignment list, we write it. Every paper type comes with a free Turnitin report and is written by a credentialed nurse.</p>
          <div class="mt-8 grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
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
            <p class="mt-1 text-sm text-brand-300">Contact us — if it's nursing-related, we almost certainly cover it.</p>
            <NuxtLink to="/contact" class="mt-4 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-2.5 text-sm font-bold text-brand-700 hover:bg-brand-50 transition-colors">
              Ask us about your assignment
            </NuxtLink>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>
