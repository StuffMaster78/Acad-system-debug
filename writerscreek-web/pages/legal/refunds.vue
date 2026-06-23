<script setup lang="ts">
useSeoMeta({
  title: 'Earnings & Dispute Policy | Writers Creek',
  description: 'How Writers Creek handles earning disputes, revision requests, and payout adjustments for writers.',
  ogImage:       'https://writerscreek.com/og-default.png',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://writerscreek.com/legal/refunds' }],
})
</script>

<template>
  <div class="bg-white">

    <!-- Page header -->
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <Breadcrumbs :items="[{ label: 'Legal', href: '/legal/refunds' }, { label: 'Earnings & Dispute Policy' }]" />
        <h1 class="mt-4 font-serif text-3xl font-bold text-slate-900 sm:text-4xl">Earnings & Dispute Policy</h1>
        <p class="mt-2 text-sm text-slate-400">Last updated: June 2025</p>

        <div class="mt-5 flex flex-wrap gap-3">
          <span class="inline-flex items-center gap-1.5 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
            <span class="text-brand-500">✓</span> Bi-weekly payouts, every time
          </span>
          <span class="inline-flex items-center gap-1.5 rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
            <span class="text-green-500">✓</span> Revision scope protection
          </span>
          <span class="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
            <span class="text-amber-500">✓</span> Dispute resolution within 3 days
          </span>
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

        <h2>1. Payout schedule</h2>
        <p>Earnings for client-approved assignments are included in the next bi-weekly payout cycle. Payout dates are fixed and published in your writer dashboard at the start of each month. Payments are not delayed for any reason within our control.</p>

        <h2>2. Earning disputes</h2>
        <p>If you believe your earnings for a completed assignment are incorrect:</p>
        <ul>
          <li>Raise a dispute within <strong>30 days</strong> of the relevant payout date.</li>
          <li>Email <a href="mailto:writers@writerscreek.com">writers@writerscreek.com</a> with your assignment ID, the expected amount, and the amount received.</li>
          <li>We will review and resolve within 3 business days.</li>
        </ul>
        <p>Disputes raised after 30 days may not be eligible for adjustment.</p>

        <h2>3. Revision scope</h2>
        <p>Writers are required to complete revisions that fall within the original assignment brief. Revisions are considered in-scope if:</p>
        <ul>
          <li>The request addresses the same research question or topic stated in the original brief.</li>
          <li>The request does not expand the word count beyond the originally specified page count.</li>
          <li>The request does not introduce a new section, chapter, or argument not mentioned in the original brief.</li>
        </ul>
        <p>If a client requests out-of-scope revisions, raise a scope dispute in the dashboard immediately. We will review and either confirm the revision is in-scope or authorise additional compensation for the expanded work.</p>

        <h2>4. Payout withholding</h2>
        <p>Writers Creek may withhold payment for an assignment if:</p>
        <ul>
          <li>The delivered work is found to contain plagiarised content.</li>
          <li>The delivered work is found to be AI-generated.</li>
          <li>The delivered work is found to have been sourced from a third party.</li>
          <li>The writer's account is under active suspension review.</li>
        </ul>
        <p>In all other circumstances, payment is released on schedule.</p>

        <h2>5. Client-initiated refunds</h2>
        <p>If a client is granted a partial or full refund by Writers Creek (due to late delivery or quality failure attributable to the writer), the corresponding amount may be deducted from the writer's next payout. Writers are notified before any deduction is applied and have the right to dispute the finding.</p>

        <h2>6. Account closure and pending earnings</h2>
        <p>If a writer account is closed — either by the writer or by Writers Creek — any earnings for completed, client-approved assignments will be paid at the next regular payout cycle, subject to verification that the assignments comply with these terms. Earnings for assignments under active dispute or quality review will be held pending resolution.</p>

        <h2>7. Contact</h2>
        <p>Payout questions or disputes: <a href="mailto:writers@writerscreek.com">writers@writerscreek.com</a>. We respond within one business day.</p>

      </div>
    </div>

  </div>
</template>
