<script setup lang="ts">
const app = useAppUrl()

const milestones = [
  { year: '2019', label: 'Founded with 20 writers' },
  { year: '2021', label: 'Passed 1,000 completed orders' },
  { year: '2024', label: '200+ active writers, 100+ subjects' },
]

useSeoMeta({
  title: 'About Us',
  description: 'ResearchPaperMate connects students with expert academic writers for research papers, essays, and dissertations.',
})
</script>

<template>
  <div>
    <section class="bg-gradient-to-br from-brand-900 to-brand-700 py-20 text-center">
      <div class="section py-0">
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">About ResearchPaperMate</h1>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-brand-100">
          Connecting students with subject-matter experts since 2019.
        </p>
      </div>
    </section>

    <section class="section max-w-4xl">
      <div class="prose prose-slate prose-lg max-w-none">
        <h2>Our mission</h2>
        <p>
          ResearchPaperMate was founded on a simple belief: every student deserves access to expert academic support,
          regardless of their first language, learning style, or time constraints. We connect you directly with writers
          who hold advanced degrees in your subject area — not generalists, but specialists.
        </p>

        <h2>How we vet our writers</h2>
        <p>
          Every writer on our platform goes through a multi-stage screening: academic credential verification,
          subject-knowledge testing, a sample writing assessment, and an initial supervised trial period.
          Only writers who pass all stages at a high standard are approved to take orders.
        </p>

        <h2>Our commitment to originality</h2>
        <p>
          Every paper is written from scratch to your specific brief. We check all completed work through
          industry-standard plagiarism detection tools before delivery. If you ever have concerns about originality,
          we'll provide the report.
        </p>

        <h2>Privacy first</h2>
        <p>
          We never sell or share your personal information. Your name, email, and order details remain strictly
          confidential. Our payment processing is handled by a regulated third-party processor to ensure your
          financial data never touches our servers.
        </p>
      </div>

      <div class="mt-16 grid gap-6 sm:grid-cols-3">
        <div v-for="m in milestones" :key="m.year" class="card text-center">
          <div class="text-2xl font-bold text-brand-700">{{ m.year }}</div>
          <p class="mt-2 text-sm text-slate-600">{{ m.label }}</p>
        </div>
      </div>
    </section>

    <section class="bg-brand-700 py-16 text-center">
      <h2 class="font-serif text-3xl font-bold text-white">Ready to get started?</h2>
      <NuxtLink to="/register" class="btn-primary mt-8 bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base">
        Place your first order
      </NuxtLink>
    </section>
  </div>
</template>
