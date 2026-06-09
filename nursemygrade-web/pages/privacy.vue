<script setup lang="ts">
useSeoMeta({
  title: 'Privacy Policy | NurseMyGrade',
  description: 'How NurseMyGrade collects, uses, stores, and protects your personal information. Your data is never sold.',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/privacy' }],
})
</script>

<template>
  <div class="bg-white">

    <!-- Page header -->
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

    <!-- Body -->
    <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="prose prose-slate max-w-none
                  prose-headings:font-serif prose-headings:font-bold
                  prose-h2:mt-10 prose-h2:text-xl prose-h2:text-slate-900
                  prose-h3:text-base prose-h3:text-slate-800
                  prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                  prose-strong:text-slate-900">

        <h2>1. Who we are</h2>
        <p>NurseMyGrade operates at <a href="https://nursemygrade.com">nursemygrade.com</a> and is the data controller responsible for personal information collected through this website and the connected platform. For any privacy-related matter, contact us at <a href="mailto:privacy@nursemygrade.com">privacy@nursemygrade.com</a>.</p>

        <h2>2. Information we collect</h2>

        <h3>Information you provide directly</h3>
        <ul>
          <li><strong>Account information</strong> — your name and email address when you register.</li>
          <li><strong>Order details</strong> — assignment type, academic level, deadline, rubric, clinical scenario notes, and any files you upload. We collect only what is needed to fulfil your order.</li>
          <li><strong>Communications</strong> — messages you send through the dashboard or to support, including chat history with your writer.</li>
          <li><strong>Writer applications</strong> — if you apply to write for us: your name, contact details, nursing qualification, licence number, and uploaded credential documents.</li>
        </ul>

        <h3>Information collected automatically</h3>
        <ul>
          <li><strong>Technical data</strong> — IP address, browser type, device type, and pages visited, collected via server logs and analytics.</li>
          <li><strong>Session data</strong> — a strictly necessary session cookie is set when you log in to maintain your session. We do not use advertising or tracking cookies.</li>
          <li><strong>Analytics</strong> — if GA4 is active on your site, aggregate usage data (page views, session duration) is collected anonymously. No personally identifiable data is sent to Google Analytics.</li>
        </ul>

        <h2>3. How we use your information</h2>
        <ul>
          <li><strong>To fulfil orders</strong> — matching you with a suitable nurse writer, processing payment, delivering completed work.</li>
          <li><strong>To communicate with you</strong> — order confirmations, revision updates, support responses, and (with your consent) promotional emails.</li>
          <li><strong>To improve the platform</strong> — aggregated, anonymised usage data helps us understand how to improve the site and matching process.</li>
          <li><strong>To verify writer credentials</strong> — nursing licences submitted by applicants are checked against issuing bodies. This data is not shared beyond the vetting team.</li>
          <li><strong>To comply with legal obligations</strong> — we retain financial transaction records as required by applicable law.</li>
        </ul>

        <h2>4. Who we share your information with</h2>
        <p>We never sell, rent, or trade your personal data. We share information only with:</p>
        <ul>
          <li><strong>Your assigned nurse writer</strong> — they receive your order brief and can message you through the dashboard. They do not see your full name, email, or payment details.</li>
          <li><strong>Payment processor</strong> — your payment details are handled entirely by our regulated third-party payment processor. We receive only a transaction confirmation; we never see or store your card number.</li>
          <li><strong>Service providers</strong> — infrastructure providers (hosting, email delivery) who process data on our behalf under strict data processing agreements.</li>
          <li><strong>Law enforcement</strong> — only when required by a valid legal order.</li>
        </ul>

        <h2>5. Data retention</h2>
        <ul>
          <li><strong>Account data</strong> — retained for as long as your account is active, plus 12 months after closure.</li>
          <li><strong>Order files and messages</strong> — retained for 24 months from order completion, then deleted from active storage.</li>
          <li><strong>Financial records</strong> — retained for 7 years as required by financial regulations.</li>
          <li><strong>Writer credential documents</strong> — retained for the duration of the writer relationship, then securely deleted.</li>
        </ul>

        <h2>6. Your rights</h2>
        <p>You have the right to:</p>
        <ul>
          <li><strong>Access</strong> — request a copy of the personal data we hold about you.</li>
          <li><strong>Correction</strong> — ask us to correct inaccurate or incomplete data.</li>
          <li><strong>Deletion</strong> — request deletion of your account and associated data. Note that we may retain financial records as required by law.</li>
          <li><strong>Portability</strong> — request your data in a structured, machine-readable format.</li>
          <li><strong>Objection</strong> — object to processing for direct marketing at any time by emailing us or clicking unsubscribe in any marketing email.</li>
          <li><strong>Withdrawal of consent</strong> — where processing is based on consent, you may withdraw it at any time without affecting prior lawful processing.</li>
        </ul>
        <p>To exercise any of these rights, email <a href="mailto:privacy@nursemygrade.com">privacy@nursemygrade.com</a>. We respond within 30 days.</p>

        <h2>7. Cookies</h2>
        <p>We use one strictly necessary session cookie to keep you logged in. This cookie is deleted when you close your browser or log out. We do not use advertising cookies, retargeting pixels, or third-party tracking scripts beyond optional analytics.</p>

        <h2>8. Security</h2>
        <p>All data is transmitted over HTTPS/TLS. Passwords are hashed and never stored in plain text. Access to production databases is restricted to authorised personnel only. We perform regular security reviews and act promptly on reported vulnerabilities.</p>
        <p>In the event of a data breach that affects your personal data, we will notify you within 72 hours of becoming aware of it, in accordance with applicable data protection law.</p>

        <h2>9. Children's privacy</h2>
        <p>NurseMyGrade is intended for users aged 18 and over. We do not knowingly collect personal data from anyone under 18. If you believe a minor has created an account, please contact us immediately.</p>

        <h2>10. Changes to this policy</h2>
        <p>We may update this policy as our practices evolve. Material changes will be communicated by email. The "Last updated" date at the top of this page always reflects the current version.</p>

        <h2>11. Contact</h2>
        <p>Privacy questions, data requests, or concerns: <a href="mailto:privacy@nursemygrade.com">privacy@nursemygrade.com</a>. For general support: <a href="mailto:support@nursemygrade.com">support@nursemygrade.com</a>.</p>

      </div>
    </div>

  </div>
</template>
