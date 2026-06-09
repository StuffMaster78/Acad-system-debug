<script setup lang="ts">
const testimonials = [
  {
    name: 'Amara O.',
    subject: 'MSc Finance, UK',
    rating: 5,
    text: "Submitted a 6,000-word dissertation chapter with 48 hours to go. The writer nailed my university's referencing style and my supervisor had zero complaints. Genuinely impressed.",
    platform: 'Trustpilot',
  },
  {
    name: 'James T.',
    subject: 'Undergraduate Biology, USA',
    rating: 5,
    text: "I'd been going back and forth on my lit review for weeks. Got it back in 24 hours, properly structured and cited. Saved my semester.",
    platform: 'Sitejabber',
  },
  {
    name: 'Priya M.',
    subject: 'MBA, Australia',
    rating: 5,
    text: 'The case study came back exactly to the brief. Real business school quality — specific, analytical, no fluff. Will use again for the next module.',
    platform: 'Trustpilot',
  },
  {
    name: 'David K.',
    subject: 'Law LLB, Canada',
    rating: 5,
    text: 'My writer clearly knew contract law. The essay was properly argued with relevant case citations, not just padded out. Very pleased.',
    platform: 'Sitejabber',
  },
  {
    name: 'Sofia R.',
    subject: 'Nursing BSc, Ireland',
    rating: 5,
    text: "First time using a service like this. Was worried, but the paper was original, properly formatted in APA, and submitted on time. Grade: B+.",
    platform: 'Trustpilot',
  },
  {
    name: 'Mohammed A.',
    subject: 'PhD Engineering, Germany',
    rating: 5,
    text: 'Needed a methodology chapter polished to near-publication standard. The writer knew MATLAB and quantitative methods. Highly recommend for postgrad work.',
    platform: 'Sitejabber',
  },
]
</script>

<template>
  <section class="bg-white">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">What students say</h2>
        <p class="section-sub">
          4.8 / 5 average rating · Verified reviews from Trustpilot and Sitejabber
        </p>
      </div>

      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <blockquote
          v-for="t in testimonials"
          :key="t.name"
          class="card flex flex-col justify-between transition-shadow hover:shadow-md"
        >
          <div>
            <!-- Stars -->
            <div class="mb-3 flex items-center justify-between">
              <div class="flex gap-0.5">
                <svg v-for="i in 5" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
              </div>
              <span class="rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700 ring-1 ring-green-200">
                ✓ Verified · {{ t.platform }}
              </span>
            </div>
            <p class="text-sm text-slate-600 leading-relaxed">"{{ t.text }}"</p>
          </div>
          <footer class="mt-4 border-t border-slate-100 pt-4">
            <p class="text-sm font-semibold text-slate-900">{{ t.name }}</p>
            <p class="text-xs text-slate-400">{{ t.subject }}</p>
          </footer>
        </blockquote>
      </div>
    </div>
  </section>
</template>
