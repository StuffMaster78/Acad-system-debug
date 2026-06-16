<script setup lang="ts">
useSeoMeta({
  title: 'Privacy Policy | GradeCrest',
  description: 'GradeCrest Privacy Policy — how we collect, use, and protect your personal data. Your information is never sold or shared with third parties.',
})
useSeoBase('https://gradecrest.com/legal/privacy')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Privacy Policy', url: 'https://gradecrest.com/legal/privacy' },
])

const sections = [
  {
    title: '1. Who we are',
    body: `GradeCrest ("we", "our", "us") operates the academic writing service at gradecrest.com. This Privacy Policy explains what personal data we collect, how we use it, and your rights regarding that data.`,
  },
  {
    title: '2. Data we collect',
    body: `When you register or place an order, we collect your name, email address, and payment details (processed securely by our payment provider — we do not store full card numbers). We also collect order details, files you upload, and messages you send through the platform. We automatically collect usage data such as IP address, browser type, and pages visited to improve our service.`,
  },
  {
    title: '3. How we use your data',
    body: `We use your data to process and fulfil your orders, communicate with you about your account and orders, improve our service and website, send service-related notifications, and comply with legal obligations. We do not use your data for automated decision-making or profiling.`,
  },
  {
    title: '4. Marketing communications',
    body: `We may occasionally send you information about offers and updates if you have opted in to marketing communications. You can unsubscribe at any time by clicking the unsubscribe link in any email or by contacting us directly at support@gradecrest.com.`,
  },
  {
    title: '5. Data sharing',
    body: `We do not sell, rent, or trade your personal data with any third party for their marketing purposes. We share data only with: (a) service providers who help us operate the platform (hosting, payment processing, email delivery) under strict confidentiality agreements; and (b) law enforcement or regulatory bodies if required by applicable law.`,
  },
  {
    title: '6. Data security',
    body: `We use industry-standard security measures including 256-bit SSL encryption, secure servers, and access controls to protect your personal data. No method of transmission over the internet is completely secure, but we take all reasonable steps to protect your information.`,
  },
  {
    title: '7. Data retention',
    body: `We retain your personal data for as long as your account is active or as needed to provide our services and comply with legal obligations. Order records are retained for up to seven years for legal and tax purposes. You may request deletion of your account data at any time (subject to legal retention requirements).`,
  },
  {
    title: '8. Your rights',
    body: `Depending on your location, you may have rights to access, correct, delete, or port your personal data, or to restrict or object to its processing. To exercise any of these rights, contact us at support@gradecrest.com. We will respond within 30 days. You also have the right to lodge a complaint with your national data protection authority.`,
  },
  {
    title: '9. Cookies',
    body: `We use essential cookies to keep you logged in and make the site function correctly. We use analytics cookies (with your consent) to understand how visitors use our site. You can manage cookie preferences through your browser settings. Disabling cookies may affect some site functionality.`,
  },
  {
    title: '10. Children',
    body: `GradeCrest is not directed at children under 18. We do not knowingly collect personal data from anyone under 18. If you believe a minor has provided us with personal data, please contact us and we will delete it promptly.`,
  },
  {
    title: '11. Changes to this policy',
    body: `We may update this Privacy Policy periodically. We will notify you of significant changes by email or by a prominent notice on our website. The date at the top of this page reflects when the policy was last updated.`,
  },
  {
    title: '12. Contact',
    body: `For any privacy-related questions or requests, email us at support@gradecrest.com or write to us at the address on our contact page.`,
  },
]
</script>

<template>
  <div class="pt-16">

    <section class="bg-forest-950 py-14 relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gc-400 mb-3">Legal</p>
        <h1 class="text-3xl font-bold text-white sm:text-4xl">Privacy Policy</h1>
        <p class="mt-3 text-slate-400 text-sm">Effective date: 1 January 2024</p>
      </div>
    </section>

    <section class="bg-white py-14">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="space-y-8">
          <div v-for="sec in sections" :key="sec.title">
            <h2 class="text-base font-bold text-ink mb-2">{{ sec.title }}</h2>
            <p class="text-sm text-graphite leading-relaxed">{{ sec.body }}</p>
          </div>
        </div>
        <div class="mt-12 flex flex-wrap gap-4 border-t border-slate-200 pt-8 text-sm text-graphite">
          <NuxtLink to="/legal/terms" class="hover:text-gc-600 transition-colors">Terms of Service</NuxtLink>
          <NuxtLink to="/legal/refunds" class="hover:text-gc-600 transition-colors">Refund Policy</NuxtLink>
          <NuxtLink to="/contact" class="hover:text-gc-600 transition-colors">Contact Us</NuxtLink>
        </div>
      </div>
    </section>

  </div>
</template>
