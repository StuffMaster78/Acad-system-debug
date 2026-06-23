<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { Star, CheckCircle2, ExternalLink } from "@lucide/vue";
import StarRating from "@/components/ui/StarRating.vue";
import { reviewsApi } from "@/api/reviews";
import { useUiStore } from "@/stores/ui";

const ui = useUiStore();

// ── Rating dimensions ─────────────────────────────────────────────────────────

const DIMENSIONS = [
  {
    key:   "overall",
    label: "Overall satisfaction",
    desc:  "How satisfied are you with the service overall?",
  },
  {
    key:   "quality",
    label: "Quality of work",
    desc:  "How would you rate the quality of the work delivered?",
  },
  {
    key:   "time",
    label: "Adherence to deadline",
    desc:  "Was your work delivered on time?",
  },
  {
    key:   "communication",
    label: "Ease of communication",
    desc:  "How easy was it to communicate with the team?",
  },
  {
    key:   "support",
    label: "Customer service",
    desc:  "How would you rate the support you received?",
  },
  {
    key:   "value",
    label: "Value for money",
    desc:  "How do you rate the value you received for the price?",
  },
] as const

type DimensionKey = (typeof DIMENSIONS)[number]["key"]

const ratings = reactive<Record<DimensionKey, number>>({
  overall:       0,
  quality:       0,
  time:          0,
  communication: 0,
  support:       0,
  value:         0,
})

const reviewText = ref("")
const isPublic   = ref(true)

const averageRating = computed(() => {
  const vals = Object.values(ratings).filter(v => v > 0)
  if (!vals.length) return 0
  return Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 10) / 10
})

const canSubmit = computed(() =>
  ratings.overall > 0 && ratings.quality > 0 && reviewText.value.trim().length >= 10
)

// ── Submit ────────────────────────────────────────────────────────────────────

const submitting = ref(false)
const submitted  = ref(false)
const error      = ref<string | null>(null)

async function submit() {
  if (!canSubmit.value) return
  submitting.value = true
  error.value = null
  try {
    // Encode dimension breakdown in the comment so admins can parse it
    const breakdown = Object.fromEntries(
      DIMENSIONS.filter(d => ratings[d.key] > 0).map(d => [d.key, ratings[d.key]])
    )
    const comment = JSON.stringify({
      ratings: breakdown,
      review: reviewText.value.trim(),
    })
    await reviewsApi.submitWebsiteReview({
      rating:    averageRating.value,
      comment,
      is_public: isPublic.value,
    })
    submitted.value = true
    ui.toast("Thank you for your review!", "success")
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = detail ?? "Something went wrong. Please try again."
  } finally {
    submitting.value = false
  }
}

// ── External review platforms ─────────────────────────────────────────────────

const EXTERNAL_PLATFORMS = [
  {
    name:    "Trustpilot",
    icon:    "⭐",
    color:   "bg-[#00B67A] hover:bg-[#009e6b]",
    url:     "https://www.trustpilot.com/",
    desc:    "Most trusted review site worldwide",
  },
  {
    name:    "Reviews.io",
    icon:    "📋",
    color:   "bg-[#0A2540] hover:bg-[#0e2e50]",
    url:     "https://www.reviews.io/",
    desc:    "Verified customer reviews",
  },
  {
    name:    "ResellerRatings",
    icon:    "🛡️",
    color:   "bg-[#4A90D9] hover:bg-[#357fc4]",
    url:     "https://www.resellerratings.com/",
    desc:    "Business ratings platform",
  },
  {
    name:    "Sitejabber",
    icon:    "💬",
    color:   "bg-[#F26522] hover:bg-[#d85a1a]",
    url:     "https://www.sitejabber.com/",
    desc:    "Consumer reviews & ratings",
  },
  {
    name:    "Google",
    icon:    "🔍",
    color:   "bg-[#4285F4] hover:bg-[#3270d3]",
    url:     "https://maps.google.com/",
    desc:    "Google Business reviews",
  },
]

function starLabel(n: number) {
  return ["", "Poor", "Fair", "Good", "Very good", "Excellent"][n] ?? ""
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-8 space-y-8">

    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-ink">Rate your experience</h1>
      <p class="mt-1 text-sm text-graphite">
        Your feedback helps us improve and lets other students know what to expect.
      </p>
    </div>

    <!-- ── Success state ─────────────────────────────────────────────── -->
    <div v-if="submitted" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center space-y-4">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
        <CheckCircle2 class="h-8 w-8 text-emerald-600" />
      </div>
      <div>
        <h2 class="text-lg font-bold text-emerald-900">Thank you for your review!</h2>
        <p class="mt-1 text-sm text-emerald-700">
          Your feedback has been received. It helps us improve and may be featured on our reviews page.
        </p>
      </div>

      <!-- External platform links shown after internal submission -->
      <div class="pt-2">
        <p class="text-sm font-semibold text-emerald-800 mb-3">
          Want to help even more? Leave a review on one of these platforms:
        </p>
        <div class="flex flex-wrap justify-center gap-2">
          <a
            v-for="p in EXTERNAL_PLATFORMS"
            :key="p.name"
            :href="p.url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-colors"
            :class="p.color"
          >
            <span>{{ p.icon }}</span>
            {{ p.name }}
            <ExternalLink class="h-3 w-3" />
          </a>
        </div>
      </div>
    </div>

    <!-- ── Review form ───────────────────────────────────────────────── -->
    <template v-else>

      <!-- Dimension ratings -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div class="border-b border-slate-100 px-5 py-4">
          <h2 class="text-base font-semibold text-ink">Rate each area</h2>
          <p class="mt-0.5 text-xs text-graphite">Overall and Quality are required</p>
        </div>

        <div class="divide-y divide-slate-100">
          <div
            v-for="dim in DIMENSIONS"
            :key="dim.key"
            class="flex items-center justify-between gap-4 px-5 py-4"
          >
            <div class="min-w-0">
              <p class="text-sm font-semibold text-ink">
                {{ dim.label }}
                <span v-if="dim.key === 'overall' || dim.key === 'quality'" class="text-rose-500 ml-0.5">*</span>
              </p>
              <p class="mt-0.5 text-xs text-graphite">{{ dim.desc }}</p>
            </div>
            <div class="shrink-0 text-right">
              <StarRating
                :rating="ratings[dim.key]"
                :interactive="true"
                size="lg"
                @update:rating="ratings[dim.key] = $event"
              />
              <p class="mt-0.5 text-xs font-medium text-graphite min-h-[1rem]">
                {{ starLabel(ratings[dim.key]) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Average -->
        <div v-if="averageRating > 0" class="border-t border-slate-100 bg-slate-50 px-5 py-3 flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-graphite">Your overall score</span>
          <div class="flex items-center gap-2">
            <StarRating :rating="averageRating" size="sm" />
            <span class="text-sm font-bold text-ink">{{ averageRating }}/5</span>
          </div>
        </div>
      </section>

      <!-- Review text -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm p-5 space-y-4">
        <h2 class="text-base font-semibold text-ink">Write your review <span class="text-rose-500">*</span></h2>
        <textarea
          v-model="reviewText"
          rows="5"
          class="focus-ring w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink placeholder:text-graphite resize-y"
          placeholder="Tell us about your experience — what went well, what could be improved, and anything else you'd like to share…"
          minlength="10"
        />
        <p class="text-xs text-graphite">Minimum 10 characters · {{ reviewText.trim().length }} / 2000</p>

        <!-- Visibility toggle -->
        <label class="flex cursor-pointer items-center gap-3">
          <div class="relative">
            <input v-model="isPublic" type="checkbox" class="sr-only peer" />
            <div class="h-5 w-9 rounded-full bg-slate-200 transition-colors peer-checked:bg-signal" />
            <div class="absolute left-0.5 top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform peer-checked:translate-x-4" />
          </div>
          <span class="text-sm text-graphite">
            <span class="font-medium text-ink">{{ isPublic ? "Public review" : "Private feedback" }}</span>
            — {{ isPublic ? "may appear on our reviews page (anonymised)" : "only visible to our team" }}
          </span>
        </label>
      </section>

      <!-- Error -->
      <p v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
        {{ error }}
      </p>

      <!-- Submit -->
      <div class="flex items-center justify-between gap-4">
        <p class="text-xs text-graphite">
          <span class="text-rose-500">*</span> Required fields
        </p>
        <button
          class="focus-ring inline-flex h-10 items-center gap-2 rounded-lg bg-signal px-6 text-sm font-semibold text-white disabled:opacity-50 transition-colors hover:bg-signal/90"
          :disabled="!canSubmit || submitting"
          @click="submit"
        >
          <span v-if="submitting">Submitting…</span>
          <span v-else class="flex items-center gap-2">
            <Star class="h-4 w-4" />
            Submit review
          </span>
        </button>
      </div>

      <!-- Divider -->
      <div class="relative flex items-center gap-4">
        <div class="flex-1 border-t border-slate-200" />
        <span class="text-xs font-semibold uppercase tracking-wider text-graphite">Or review us externally</span>
        <div class="flex-1 border-t border-slate-200" />
      </div>

      <!-- External platforms -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm p-5 space-y-4">
        <div>
          <h2 class="text-base font-semibold text-ink">Leave a review on a third-party platform</h2>
          <p class="mt-0.5 text-xs text-graphite">External reviews help prospective students make informed decisions.</p>
        </div>
        <div class="grid gap-3 sm:grid-cols-2">
          <a
            v-for="p in EXTERNAL_PLATFORMS"
            :key="p.name"
            :href="p.url"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-3 rounded-xl border border-slate-200 p-4 transition-all hover:border-slate-300 hover:shadow-sm group"
          >
            <span class="text-2xl">{{ p.icon }}</span>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-ink group-hover:text-signal transition-colors">{{ p.name }}</p>
              <p class="text-xs text-graphite">{{ p.desc }}</p>
            </div>
            <ExternalLink class="h-3.5 w-3.5 text-graphite/50 group-hover:text-signal transition-colors shrink-0" />
          </a>
        </div>
      </section>

    </template>
  </div>
</template>
