<script setup lang="ts">
useSeoMeta({
  title: 'Terms of Service | Writers Creek',
  description: 'Terms governing participation in the Writers Creek writer network. Read before applying.',
  ogImage:       'https://writerscreek.com/og-default.png',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://writerscreek.com/legal/terms' }],
})
</script>

<template>
  <div class="bg-white">

    <!-- Page header -->
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <Breadcrumbs :items="[{ label: 'Legal', href: '/legal/terms' }, { label: 'Terms of Service' }]" />
        <h1 class="mt-4 font-serif text-3xl font-bold text-slate-900 sm:text-4xl">Terms of Service</h1>
        <p class="mt-2 text-sm text-slate-400">Last updated: June 2025</p>
        <div class="mt-4 inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-4 py-1.5 text-sm font-medium text-amber-800">
          Please read carefully before applying.
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

        <h2>1. About Writers Creek</h2>
        <p>Writers Creek is a writer network operating at <a href="https://writerscreek.com">writerscreek.com</a>. We connect qualified academic writers with clients who require custom academic writing assistance. These terms govern the relationship between Writers Creek and writers who participate in the network.</p>

        <h2>2. Eligibility</h2>
        <p>To participate as a writer you must:</p>
        <ul>
          <li>Be at least 18 years of age.</li>
          <li>Hold a postgraduate degree (Master's or PhD) or an active professional credential (e.g. RN, CPA) in your stated subject areas.</li>
          <li>Provide accurate information in your application and during vetting.</li>
          <li>Pass the Writers Creek vetting assessment.</li>
        </ul>
        <p>Providing false credentials or misrepresenting your qualifications results in immediate removal from the platform and forfeiture of any pending earnings.</p>

        <h2>3. Independent contractor status</h2>
        <p>Writers participating in the Writers Creek network do so as independent contractors, not as employees. Writers Creek does not guarantee a minimum volume of assignments. Writers may accept or decline assignments at their discretion. Writers are responsible for their own tax obligations in their jurisdiction.</p>

        <h2>4. Assignment acceptance and delivery</h2>
        <p>When you accept an assignment you agree to:</p>
        <ul>
          <li>Deliver original work written from scratch for the specific assignment brief.</li>
          <li>Deliver by the deadline specified at acceptance.</li>
          <li>Complete within-scope revisions requested by the client within the revision window.</li>
          <li>Communicate early if circumstances prevent timely delivery.</li>
        </ul>

        <h2>5. Original work requirement</h2>
        <p>All work submitted through Writers Creek must be original and written solely for the specific assignment. You may not:</p>
        <ul>
          <li>Submit AI-generated content.</li>
          <li>Plagiarise from any published source.</li>
          <li>Reuse work previously submitted for another client or another platform.</li>
          <li>Submit work sourced from a third party.</li>
        </ul>
        <p>Breach of the original work requirement results in immediate account suspension, removal from the platform, and forfeiture of all pending earnings for affected assignments.</p>

        <h2>6. Intellectual property</h2>
        <p>Upon delivery and full payment, you assign all intellectual property rights in the delivered work to Writers Creek, which in turn licenses it to the client. You retain no right to reuse, republish, or resell any delivered assignment.</p>

        <h2>7. Earnings and payouts</h2>
        <p>Earnings are based on the per-page rate applicable to your writer level at the time of assignment acceptance. Payouts are processed bi-weekly. Writers Creek reserves the right to withhold payment for assignments that violate these terms. Disputes about earnings must be raised within 30 days of the relevant payout date.</p>

        <h2>8. Confidentiality</h2>
        <p>You agree not to disclose any information about clients, assignments, or platform operations to any third party. Client details, assignment contents, and communications with clients through the platform are confidential.</p>

        <h2>9. Prohibited conduct</h2>
        <p>You agree not to:</p>
        <ul>
          <li>Attempt to contact clients outside the platform dashboard.</li>
          <li>Solicit clients to move business off the platform.</li>
          <li>Misrepresent your credentials, level, or qualifications.</li>
          <li>Use automated tools to bid on or accept assignments.</li>
          <li>Engage in any conduct that damages the reputation or operations of Writers Creek.</li>
        </ul>

        <h2>10. Account suspension and termination</h2>
        <p>Writers Creek may suspend or terminate a writer account at any time for breach of these terms, sustained low quality ratings, repeated missed deadlines, or conduct that harms clients or the platform. Pending earnings for completed, client-approved work are paid out at the next regular payout cycle after termination, subject to verification of compliance with these terms.</p>

        <h2>11. Changes to these terms</h2>
        <p>We may update these terms from time to time. Material changes will be communicated by email. Continued use of the platform after changes are posted constitutes acceptance of the updated terms.</p>

        <h2>12. Governing law</h2>
        <p>These terms are governed by the laws of Kenya. Any disputes shall be resolved first through good-faith negotiation; failing that, through the courts of competent jurisdiction in Nairobi, Kenya.</p>

        <h2>13. Contact</h2>
        <p>Questions about these terms: <a href="mailto:writers@writerscreek.com">writers@writerscreek.com</a>.</p>

      </div>
    </div>

  </div>
</template>
