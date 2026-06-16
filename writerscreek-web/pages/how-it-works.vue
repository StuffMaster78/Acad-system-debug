<script setup lang="ts">
useSeoMeta({
  title: 'How It Works | Writers Creek',
  description: 'Learn how Writers Creek works — from application to first payout. Understand our vetting process, assignment matching, and quality standards.',
})

const steps = [
  {
    n: '01',
    title: 'Submit your application',
    desc: 'Fill out the online application with your academic background, subject specialisms, and a portfolio link or writing sample. The form takes about 10 minutes.',
    detail: 'We ask about your qualifications, subject expertise, and writing experience. We do not ask for payment or personal financial information at this stage.',
  },
  {
    n: '02',
    title: 'Complete the vetting quiz',
    desc: 'Approved applicants are invited to complete a short assessment covering grammar, academic writing conventions, and subject-specific knowledge.',
    detail: "The quiz is designed to be selective. Not every applicant passes. We maintain quality by keeping the bar high — it's better for writers who are accepted and better for clients.",
  },
  {
    n: '03',
    title: 'Account activation and assignment access',
    desc: 'Once you pass the vetting stage, your writer account is activated. Assignments in your subject areas appear immediately in your dashboard.',
    detail: "You choose which assignments to pick up. There's no obligation to take any particular order. You can filter by subject, deadline, page count, and academic level.",
  },
  {
    n: '04',
    title: 'Deliver quality work and get paid',
    desc: 'Submit your completed work through the platform. After the client review window closes, your earnings are queued for the next bi-weekly payout.',
    detail: 'Payments are released every two weeks, consistently. You do not need to invoice us or chase payments. If a revision is required within scope, complete it — the payout is not affected.',
  },
]

const standards = [
  {
    title: 'Credential verification',
    desc: "Every writer must hold a postgraduate degree or professional credential in their claimed subject area. We verify qualifications before activation. You cannot write nursing papers without nursing credentials, and you cannot write finance papers without a relevant postgraduate background.",
  },
  {
    title: 'Original work only',
    desc: 'All work must be original and written from scratch for each assignment. AI-generated content, plagiarised text, or repurposed prior work is grounds for immediate account suspension and removal from the platform.',
  },
  {
    title: 'Within-scope revisions',
    desc: 'Revision requests from clients that fall within the original brief are your responsibility. Requests that expand the scope or introduce new requirements are handled separately — you will never be asked to absorb unlimited unpaid rework.',
  },
  {
    title: 'Deadline commitment',
    desc: 'When you accept an assignment, you commit to the deadline. Missing a deadline without prior notice affects your writer rating. Communicate early if circumstances change.',
  },
]

const vetQuizTopics = [
  'Academic grammar and style',
  'Citation and referencing conventions (APA, MLA, Chicago)',
  'Argument structure and essay organisation',
  'Subject-specific terminology in your declared disciplines',
  'Critical thinking and source evaluation',
]
</script>

<template>
  <div class="bg-white">

    <!-- Hero -->
    <div class="bg-slate-900 px-4 py-16 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <h1 class="text-4xl font-bold text-white sm:text-5xl">How Writers Creek works</h1>
        <p class="mt-5 text-lg text-slate-300">
          From application to first payout — a clear, straightforward process built around quality and writer respect.
        </p>
      </div>
    </div>

    <!-- Steps -->
    <div class="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <div class="space-y-12">
        <div
          v-for="step in steps"
          :key="step.n"
          class="grid gap-6 sm:grid-cols-[80px_1fr]"
        >
          <div class="text-5xl font-black text-brand-400/30">{{ step.n }}</div>
          <div>
            <h2 class="text-xl font-bold text-slate-900">{{ step.title }}</h2>
            <p class="mt-2 text-slate-700">{{ step.desc }}</p>
            <div class="mt-3 rounded-xl border border-brand-100 bg-brand-50 px-4 py-3 text-sm text-brand-800">
              {{ step.detail }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quality standards -->
    <div class="bg-slate-50 py-16">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold text-slate-900 sm:text-3xl">Quality standards</h2>
        <p class="mt-3 text-slate-600">These are not guidelines — they are requirements. Writers who do not meet these standards are removed from the platform.</p>
        <div class="mt-8 grid gap-5 sm:grid-cols-2">
          <div
            v-for="std in standards"
            :key="std.title"
            class="rounded-2xl border border-slate-100 bg-white p-6"
          >
            <div class="mb-2 flex items-center gap-2">
              <span class="text-brand-500">✓</span>
              <h3 class="font-bold text-slate-900">{{ std.title }}</h3>
            </div>
            <p class="text-sm leading-relaxed text-slate-600">{{ std.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Vetting quiz -->
    <div class="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <h2 class="text-2xl font-bold text-slate-900 sm:text-3xl">What the vetting quiz covers</h2>
      <p class="mt-3 text-slate-600">The quiz takes approximately 20–30 minutes. It is designed to be passed by strong academic writers — not to be tricky.</p>
      <ul class="mt-8 space-y-3">
        <li
          v-for="topic in vetQuizTopics"
          :key="topic"
          class="flex items-center gap-3 text-slate-700"
        >
          <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-700">✓</span>
          {{ topic }}
        </li>
      </ul>
      <p class="mt-8 text-sm text-slate-500">Writers who do not pass the first time may reapply after 60 days.</p>
    </div>

    <!-- CTA -->
    <div class="bg-slate-900 py-16">
      <div class="mx-auto max-w-2xl px-4 text-center">
        <h2 class="text-2xl font-bold text-white">Ready to apply?</h2>
        <p class="mt-3 text-slate-400">The application form takes about 10 minutes. Decisions within 48 hours.</p>
        <NuxtLink to="/apply" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-7 py-3.5 text-base font-bold text-white transition-colors hover:bg-brand-500">
          Start your application →
        </NuxtLink>
      </div>
    </div>

  </div>
</template>
