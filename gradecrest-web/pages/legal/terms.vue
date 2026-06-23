<script setup lang="ts">
useSeoMeta({
  title: 'Terms of Service | GradeCrest',
  description: 'GradeCrest Terms of Service — how our academic writing service works, your rights, and your responsibilities as a customer.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useSeoBase('https://gradecrest.com/legal/terms')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Terms of Service', url: 'https://gradecrest.com/legal/terms' },
])

const sections = [
  {
    title: '1. About this service',
    body: `GradeCrest provides custom academic model papers written by human experts. Our papers are intended for reference and study purposes only — as examples of correctly structured, well-argued academic work. By placing an order, you confirm that you understand and accept this intended use.`,
  },
  {
    title: '2. Eligibility',
    body: `You must be at least 18 years old to use GradeCrest. By creating an account or placing an order, you represent that you meet this requirement. We reserve the right to refuse service or cancel orders at our discretion.`,
  },
  {
    title: '3. Orders and payment',
    body: `Orders become binding when payment is confirmed. Your payment is held in escrow and released to your writer only after you approve the completed work. Prices are shown in USD. You are responsible for any applicable local taxes. We accept Visa, Mastercard, American Express, Discover, and PayPal.`,
  },
  {
    title: '4. Delivery',
    body: `Deadlines are calculated from the time your payment is confirmed and all required files have been received. We make every effort to deliver on time. If your order is delivered late, you are entitled to a partial or full refund in proportion to the delay, as described in our Refund Policy.`,
  },
  {
    title: '5. Revisions',
    body: `Free revisions are available within 14 days of delivery for standard papers (30 days for dissertations and theses). Revisions must be within the scope of the original order instructions. Changes to the original brief after writing has begun may be subject to an additional charge.`,
  },
  {
    title: '6. Grade guarantee',
    body: `If the completed work does not meet the grade requirement you stated in your original instructions, we will rewrite it at no additional cost. If the work still does not meet your requirements after revision, we will issue a full refund. Grade requirements must be stated clearly in your original order brief.`,
  },
  {
    title: '7. Originality',
    body: `All papers are written from scratch by human writers. We do not use AI writing tools. Each paper is unique to your order and is never resold, shared, or reused. A plagiarism report is included with every completed order at no extra charge.`,
  },
  {
    title: '8. Intellectual property',
    body: `Upon payment and approval of the completed work, you receive full rights to use the paper as a reference or study aid. GradeCrest retains no claim over the content of completed orders. You must not represent our model papers as your own original academic submissions to your institution.`,
  },
  {
    title: '9. Acceptable use',
    body: `You agree to use our service only for lawful purposes and in accordance with these Terms. You must not use GradeCrest to produce content that is fraudulent, defamatory, harmful, or in violation of any applicable law. We reserve the right to terminate your account if we have reason to believe our service is being misused.`,
  },
  {
    title: '10. Confidentiality',
    body: `We treat all customer information and order details as strictly confidential. We will never share your name, email address, order details, or any personal information with third parties, except as required by applicable law. See our Privacy Policy for full details.`,
  },
  {
    title: '11. Limitation of liability',
    body: `GradeCrest's liability is limited to the amount you paid for the specific order in question. We are not liable for indirect, consequential, or incidental losses arising from the use of our service, including academic consequences resulting from your use of model papers.`,
  },
  {
    title: '12. Changes to these terms',
    body: `We may update these Terms from time to time. Changes will be posted on this page with an updated effective date. Continued use of the service after changes are posted constitutes your acceptance of the revised Terms.`,
  },
  {
    title: '13. Contact',
    body: `Questions about these Terms? Contact our support team at support@gradecrest.com or via live chat on the website.`,
  },
]
</script>

<template>
  <div class="pt-16">

    <section class="bg-forest-950 py-14 relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gc-400 mb-3">Legal</p>
        <h1 class="text-3xl font-bold text-white sm:text-4xl">Terms of Service</h1>
        <p class="mt-3 text-slate-400 text-sm">Effective date: 1 January 2024</p>
      </div>
    </section>

    <section class="bg-white py-14">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="prose prose-sm prose-slate max-w-none space-y-8">
          <div v-for="sec in sections" :key="sec.title">
            <h2 class="text-base font-bold text-ink mb-2">{{ sec.title }}</h2>
            <p class="text-sm text-graphite leading-relaxed">{{ sec.body }}</p>
          </div>
        </div>
        <div class="mt-12 flex flex-wrap gap-4 border-t border-slate-200 pt-8 text-sm text-graphite">
          <NuxtLink to="/legal/privacy" class="hover:text-gc-600 transition-colors">Privacy Policy</NuxtLink>
          <NuxtLink to="/legal/refunds" class="hover:text-gc-600 transition-colors">Refund Policy</NuxtLink>
          <NuxtLink to="/contact" class="hover:text-gc-600 transition-colors">Contact Us</NuxtLink>
        </div>
      </div>
    </section>

  </div>
</template>
