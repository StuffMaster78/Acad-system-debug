<script setup lang="ts">
useSeoMeta({ title: 'Privacy Policy | ResearchPaperMate', description: 'How ResearchPaperMate collects, uses, stores, and protects your personal information. Your data is never sold.' })
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/privacy' }] })
</script>

<template>
  <div class="bg-white">
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <Breadcrumbs :items="[{ label: 'Privacy Policy' }]" />
        <h1 class="mt-4 font-serif text-3xl font-bold text-slate-900 sm:text-4xl">Privacy Policy</h1>
        <p class="mt-2 text-sm text-slate-400">Last updated: June 2025</p>
        <div class="mt-4 inline-flex items-center gap-2 rounded-full border border-green-200 bg-green-50 px-4 py-1.5 text-sm font-medium text-green-800">
          We never sell your data. Period.
        </div>
      </div>
    </div>
    <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="prose prose-slate max-w-none prose-headings:font-serif prose-headings:font-bold prose-h2:mt-10 prose-h2:text-xl prose-h2:text-slate-900 prose-h3:text-base prose-h3:text-slate-800 prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline prose-strong:text-slate-900">
        <h2>1. Who we are</h2>
        <p>ResearchPaperMate operates at <a href="https://researchpapermate.com">researchpapermate.com</a> and is the data controller for personal information collected through this website. Contact us at <a href="mailto:privacy@researchpapermate.com">privacy@researchpapermate.com</a> for any privacy matter.</p>
        <h2>2. Information we collect</h2>
        <h3>Information you provide directly</h3>
        <ul>
          <li><strong>Account information</strong> — your name and email address when you register.</li>
          <li><strong>Order details</strong> — assignment type, academic level, deadline, rubric, and any files you upload. We collect only what is needed to fulfil your order.</li>
          <li><strong>Communications</strong> — messages sent through the dashboard or to support.</li>
          <li><strong>Writer applications</strong> — name, contact details, qualifications, and credential documents.</li>
        </ul>
        <h3>Information collected automatically</h3>
        <ul>
          <li><strong>Technical data</strong> — IP address, browser type, device type, and pages visited via server logs and analytics.</li>
          <li><strong>Session cookie</strong> — strictly necessary to maintain your login session. We do not use advertising or tracking cookies.</li>
        </ul>
        <h2>3. How we use your information</h2>
        <ul>
          <li><strong>To fulfil orders</strong> — matching you with a writer, processing payment, delivering completed work.</li>
          <li><strong>To communicate with you</strong> — order confirmations, revision updates, support responses, and (with your consent) promotional emails.</li>
          <li><strong>To improve the platform</strong> — aggregated, anonymised usage data to improve the site and matching process.</li>
          <li><strong>To verify writer credentials</strong> — qualifications submitted by applicants are checked against issuing institutions.</li>
        </ul>
        <h2>4. Who we share your information with</h2>
        <p>We never sell, rent, or trade your data. We share only with:</p>
        <ul>
          <li><strong>Your assigned writer</strong> — they receive the order brief only, not your name or contact information.</li>
          <li><strong>Payment processor</strong> — your payment details go directly to our regulated third-party processor. We see only a transaction confirmation.</li>
          <li><strong>Infrastructure providers</strong> — hosting and email delivery under strict data processing agreements.</li>
          <li><strong>Law enforcement</strong> — only when required by a valid legal order.</li>
        </ul>
        <h2>5. Data retention</h2>
        <ul>
          <li><strong>Account data</strong> — retained while active, plus 12 months after closure.</li>
          <li><strong>Order files and messages</strong> — 24 months from completion, then deleted.</li>
          <li><strong>Financial records</strong> — 7 years as required by financial regulations.</li>
        </ul>
        <h2>6. Your rights</h2>
        <p>You have the right to access, correct, delete, and port your personal data, and to object to direct marketing at any time. Email <a href="mailto:privacy@researchpapermate.com">privacy@researchpapermate.com</a> to exercise any right. We respond within 30 days.</p>
        <h2>7. Cookies</h2>
        <p>One strictly necessary session cookie is set when you log in. It is deleted when you close your browser or log out. We do not use advertising cookies or third-party tracking scripts beyond optional analytics.</p>
        <h2>8. Security</h2>
        <p>All data is transmitted over HTTPS/TLS. Passwords are hashed and never stored in plain text. In the event of a breach affecting your data, we will notify you within 72 hours.</p>
        <h2>9. Changes and contact</h2>
        <p>Material changes will be communicated by email. Privacy questions: <a href="mailto:privacy@researchpapermate.com">privacy@researchpapermate.com</a>. General support: <a href="mailto:support@researchpapermate.com">support@researchpapermate.com</a>.</p>
      </div>
    </div>
  </div>
</template>
