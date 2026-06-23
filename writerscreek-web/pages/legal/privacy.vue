<script setup lang="ts">
useSeoMeta({
  title: 'Privacy Policy | Writers Creek',
  description: 'How Writers Creek collects, uses, stores, and protects your personal information. Writer credentials and personal data are never shared with clients.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://writerscreek.com/legal/privacy' }],
})
</script>

<template>
  <div class="bg-white">

    <!-- Page header -->
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <Breadcrumbs :items="[{ label: 'Legal', href: '/legal/privacy' }, { label: 'Privacy Policy' }]" />
        <h1 class="mt-4 font-serif text-3xl font-bold text-slate-900 sm:text-4xl">Privacy Policy</h1>
        <p class="mt-2 text-sm text-slate-400">Last updated: June 2025</p>
        <div class="mt-4 inline-flex items-center gap-2 rounded-full border border-green-200 bg-green-50 px-4 py-1.5 text-sm font-medium text-green-800">
          We never sell your data. Period.
        </div>
      </div>
    </div>

    <!-- Body -->
    <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="prose prose-slate max-w-none
                  prose-headings:font-serif prose-headings:font-bold
                  prose-h2:mt-10 prose-h2:text-xl prose-h2:text-slate-900
                  prose-h3:text-base prose-h3:text-slate-800
                  prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                  prose-strong:text-slate-900">

        <h2>1. Who we are</h2>
        <p>Writers Creek operates at <a href="https://writerscreek.com">writerscreek.com</a> and is the data controller responsible for personal information collected through this website and the connected writer platform. For any privacy-related matter, contact us at <a href="mailto:privacy@writerscreek.com">privacy@writerscreek.com</a>.</p>

        <h2>2. Information we collect</h2>

        <h3>Information you provide directly</h3>
        <ul>
          <li><strong>Account information</strong> — your name and email address when you register as a writer.</li>
          <li><strong>Application details</strong> — your academic background, subject specialisms, qualification level, and writing sample or portfolio link submitted during the application process.</li>
          <li><strong>Credential documents</strong> — qualification certificates, professional licences, or other credential documents you upload for vetting. These are used solely for verification and are not shared with clients.</li>
          <li><strong>Communications</strong> — messages you send through the dashboard or to support.</li>
        </ul>

        <h3>Information collected automatically</h3>
        <ul>
          <li><strong>Technical data</strong> — IP address, browser type, device type, and pages visited, collected via server logs and analytics.</li>
          <li><strong>Session data</strong> — a strictly necessary session cookie is set when you log in to maintain your session.</li>
          <li><strong>Analytics</strong> — if analytics is active, aggregate usage data (page views, session duration) may be collected anonymously. No personally identifiable data is sent to third-party analytics providers.</li>
        </ul>

        <h2>3. How we use your information</h2>
        <ul>
          <li><strong>To process your writer application</strong> — reviewing credentials, running the vetting assessment, and activating approved accounts.</li>
          <li><strong>To match and deliver assignments</strong> — routing assignments to writers with the relevant credentials and subject background.</li>
          <li><strong>To process earnings and payouts</strong> — maintaining accurate payout records and processing bi-weekly transfers.</li>
          <li><strong>To communicate with you</strong> — assignment notifications, payout confirmations, and support responses.</li>
          <li><strong>To improve the platform</strong> — aggregated, anonymised usage data helps us improve assignment matching and writer experience.</li>
          <li><strong>To comply with legal obligations</strong> — we retain financial records as required by applicable law.</li>
        </ul>

        <h2>4. Who we share your information with</h2>
        <p>We never sell, rent, or trade your personal data. We share information only with:</p>
        <ul>
          <li><strong>Clients</strong> — clients are never given your real name, credentials, or contact details. They see only your writer profile name.</li>
          <li><strong>Payment processor</strong> — your payment details are handled by our regulated third-party payment processor. We receive only a transaction confirmation.</li>
          <li><strong>Service providers</strong> — infrastructure and email delivery providers who process data on our behalf under strict data processing agreements.</li>
          <li><strong>Law enforcement</strong> — only when required by a valid legal order.</li>
        </ul>

        <h2>5. Data retention</h2>
        <ul>
          <li><strong>Account data</strong> — retained for as long as your writer account is active, plus 12 months after closure.</li>
          <li><strong>Assignment records</strong> — retained for 24 months from completion.</li>
          <li><strong>Financial records</strong> — retained for 7 years as required by financial regulations.</li>
          <li><strong>Credential documents</strong> — retained for the duration of the writer relationship, then securely deleted.</li>
        </ul>

        <h2>6. Your rights</h2>
        <p>You have the right to access, correct, delete, or export your personal data. To exercise any right, email <a href="mailto:privacy@writerscreek.com">privacy@writerscreek.com</a>. We respond within 30 days.</p>

        <h2>7. Cookies</h2>
        <p>We use one strictly necessary session cookie to keep you logged in. This cookie is deleted when you close your browser or log out. We do not use advertising cookies or retargeting pixels without your consent.</p>

        <h2>8. Security</h2>
        <p>All data is transmitted over HTTPS/TLS. Passwords are hashed and never stored in plain text. Access to production databases is restricted to authorised personnel only.</p>

        <h2>9. Changes to this policy</h2>
        <p>We may update this policy as our practices evolve. Material changes will be communicated by email. The "Last updated" date at the top always reflects the current version.</p>

        <h2>10. Contact</h2>
        <p>Privacy questions or data requests: <a href="mailto:privacy@writerscreek.com">privacy@writerscreek.com</a>. General support: <a href="mailto:writers@writerscreek.com">writers@writerscreek.com</a>.</p>

      </div>
    </div>

  </div>
</template>
