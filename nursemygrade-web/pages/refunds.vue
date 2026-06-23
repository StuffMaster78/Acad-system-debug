<script setup lang="ts">
useSeoMeta({
  title: 'Refund Policy | NurseMyGrade',
  description: 'NurseMyGrade grade-or-money-back guarantee, revision policy, and refund process for nursing paper orders.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/refunds' }],
})
</script>

<template>
  <div class="bg-white">

    <!-- Page header -->
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl">
        <Breadcrumbs :items="[{ label: 'Refund Policy' }]" />
        <h1 class="mt-4 font-serif text-3xl font-bold text-slate-900 sm:text-4xl">Refund Policy</h1>
        <p class="mt-2 text-sm text-slate-400">Last updated: June 2025</p>

        <!-- Guarantee pill row -->
        <div class="mt-5 flex flex-wrap gap-3">
          <span class="inline-flex items-center gap-1.5 rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
            <span class="text-brand-500">✓</span> Grade or money back
          </span>
          <span class="inline-flex items-center gap-1.5 rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
            <span class="text-green-500">✓</span> Unlimited free revisions
          </span>
          <span class="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
            <span class="text-amber-500">✓</span> On-time delivery guarantee
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

        <h2>1. Grade or money-back guarantee</h2>
        <p>If you receive a grade lower than the one specified in your order brief, and the shortfall is attributable to the quality of the work we delivered (not to changes in your submission, added requirements, or institutional circumstances outside our control), you are entitled to a remedy.</p>
        <p>To claim under this guarantee:</p>
        <ul>
          <li>Contact us within <strong>14 days</strong> of receiving your graded work.</li>
          <li>Email <a href="mailto:support@nursemygrade.com">support@nursemygrade.com</a> with your order number, the grade received, the grade stated in your brief, and (where available) your instructor's feedback.</li>
          <li>We will either <strong>rewrite the relevant sections free of charge</strong> or issue a <strong>partial or full refund</strong>, depending on the nature of the shortfall.</li>
        </ul>
        <p>We assess each claim individually and aim to resolve all grade-guarantee cases within 3 business days of receiving the documentation.</p>

        <h2>2. Free revision policy</h2>
        <p>Every order includes <strong>unlimited free revisions</strong> within the revision window. The revision window is equal to the original delivery time (e.g. a 3-day order has a 3-day revision window), with a minimum of 24 hours and a maximum of 30 days from delivery.</p>
        <p>Revisions are free when:</p>
        <ul>
          <li>The request falls within the original scope of the order brief.</li>
          <li>The request is made within the revision window.</li>
          <li>The same nurse writer is available (if not, a qualified replacement is assigned at no cost).</li>
        </ul>
        <p>Revisions that introduce substantially new requirements — a new rubric section, a different clinical scenario, or a significantly expanded word count — may constitute a new order and be charged accordingly. We will always tell you before any charge is applied.</p>

        <h2>3. Cancellation before delivery</h2>
        <h3>Cancelled before a writer starts</h3>
        <p>If you cancel your order before a nurse writer has been assigned or has started work, you are entitled to a <strong>full refund</strong> processed within 3–5 business days.</p>

        <h3>Cancelled after a writer starts</h3>
        <p>If a writer has started work:</p>
        <ul>
          <li>Cancellation within the first 25% of the deadline period — <strong>75% refund</strong>.</li>
          <li>Cancellation within 25–50% of the deadline period — <strong>50% refund</strong>.</li>
          <li>Cancellation after 50% of the deadline period has elapsed — <strong>no refund</strong>, as the writer has completed significant work.</li>
        </ul>

        <h2>4. Late delivery</h2>
        <p>We take deadlines seriously. If we deliver your paper later than the agreed deadline:</p>
        <ul>
          <li>Delays of <strong>1–4 hours</strong> — 10% partial refund.</li>
          <li>Delays of <strong>4–12 hours</strong> — 25% partial refund.</li>
          <li>Delays of <strong>more than 12 hours</strong> — up to 50% partial refund, or a full refund if the delay renders the work unusable.</li>
        </ul>
        <p>Delays caused by client-side factors — late submission of the rubric, delayed response to writer questions, or requested changes to requirements after work has started — do not qualify for this guarantee.</p>

        <h2>5. Simulation and class-help orders</h2>
        <p>Orders for Shadow Health DCE cases, iHuman virtual patients, and full online class management have specific refund terms:</p>
        <ul>
          <li><strong>Shadow Health / iHuman cases</strong> — quoted as a fixed-price package. Refunds are available only if work has not yet been started. Once a writer begins, no refund is available for the individual case, but revision of any written deliverable (subjective, objective, assessment) is included.</li>
          <li><strong>Full class management</strong> — billed in milestone instalments. Each completed milestone is non-refundable. If we are unable to complete a future milestone, you are refunded the unused portion only.</li>
        </ul>

        <h2>6. Duplicate orders</h2>
        <p>If you accidentally place a duplicate order, contact support immediately. Duplicates identified and cancelled <strong>before a writer is assigned</strong> are refunded in full. Duplicates identified after assignment are handled on a case-by-case basis.</p>

        <h2>7. Non-refundable situations</h2>
        <p>Refunds are not available in the following circumstances:</p>
        <ul>
          <li>You provide an inaccurate brief and then request a rewrite to different specifications.</li>
          <li>The grade outcome was affected by factors unrelated to the delivered paper (late submission, plagiarism committed by you, institutional grading anomalies).</li>
          <li>The revision window has expired.</li>
          <li>The order was placed more than 30 days ago and no refund claim was filed within that period.</li>
          <li>You violated the Terms of Use in connection with the order.</li>
        </ul>

        <h2>8. How refunds are processed</h2>
        <p>Approved refunds are returned to the original payment method within <strong>5–10 business days</strong>, depending on your bank or card provider. For M-Pesa payments, refunds are typically processed within 1–2 business days.</p>
        <p>You will receive an email confirmation when a refund is approved and a second email when it has been processed.</p>

        <h2>9. How to request a refund</h2>
        <p>Email <a href="mailto:support@nursemygrade.com">support@nursemygrade.com</a> with:</p>
        <ul>
          <li>Your order number</li>
          <li>The reason for your refund request</li>
          <li>Any supporting evidence (graded paper, instructor feedback, delivery timestamp)</li>
        </ul>
        <p>Our support team responds within <strong>1 business hour</strong> and aims to resolve refund cases within 3 business days of receiving full documentation.</p>

      </div>
    </div>

  </div>
</template>
