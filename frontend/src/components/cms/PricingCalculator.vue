<script setup lang="ts">
/**
 * PricingCalculator — embeddable pricing widget.
 *
 * Used standalone (sidebar, homepage) and as a CMS block renderer
 * for the `calculator` StreamField block type.
 *
 * Flow:
 *   1. Mount → load dropdowns (academic levels, paper types, deadlines)
 *   2. User picks options → debounced startPaperQuote() → show estimate range
 *   3. "Get exact price" → updatePaperQuote() → show full breakdown
 *   4. "Place Order" → redirect to ctaUrl
 */
import { computed, onMounted, ref, watch } from "vue";
import { ArrowRight, Calculator, RefreshCw } from "@lucide/vue";
import { pricingApi, type ConfigOption, type DeadlineConfig } from "@/api/pricing";
import type { PaperQuoteStartResponse, PaperQuoteUpdateResponse, PriceLine } from "@/types/orders";

const props = withDefaults(defineProps<{
  // Config from CMS block (all optional — falls back to sensible defaults)
  title?:                   string;
  subtitle?:                string;
  serviceCode?:             string;
  defaultPages?:            number;
  defaultDeadlineHours?:    number;
  defaultAcademicLevelCode?: string;
  defaultPaperTypeCode?:    string;
  showLineBreakdown?:       boolean;
  ctaText?:                 string;
  ctaUrl?:                  string;
}>(), {
  title:                   "Get your instant price",
  subtitle:                "No account needed — see your price in seconds.",
  serviceCode:             "standard_paper",
  defaultPages:            1,
  defaultDeadlineHours:    48,
  defaultAcademicLevelCode: "",
  defaultPaperTypeCode:    "",
  showLineBreakdown:       true,
  ctaText:                 "Place Order",
  ctaUrl:                  "/auth/register",
});

// ── Config options ────────────────────────────────────────────────────────────
const academicLevels = ref<ConfigOption[]>([]);
const paperTypes     = ref<ConfigOption[]>([]);
const deadlines      = ref<DeadlineConfig[]>([]);
const configLoading  = ref(true);

// ── User selections ───────────────────────────────────────────────────────────
const pages         = ref(props.defaultPages);
const deadlineHours = ref(props.defaultDeadlineHours);
const levelCode     = ref(props.defaultAcademicLevelCode);
const paperCode     = ref(props.defaultPaperTypeCode);
const spacing       = ref<"single" | "double">("double");

// ── Quote state ───────────────────────────────────────────────────────────────
const sessionId      = ref<string | null>(null);
const estimate       = ref<PaperQuoteStartResponse | null>(null);
const breakdown      = ref<PaperQuoteUpdateResponse | null>(null);
const quoteLoading   = ref(false);
const showBreakdown  = ref(false);
const quoteError     = ref("");

// ── Derived display values ────────────────────────────────────────────────────
const currency = computed(() =>
  breakdown.value?.currency ?? estimate.value?.currency ?? "USD",
);

const estimateRange = computed(() => {
  if (!estimate.value) return null;
  const lo = Number(estimate.value.estimated_min_price ?? 0);
  const hi = Number(estimate.value.estimated_max_price ?? 0);
  if (!lo && !hi) return null;
  return lo === hi ? `$${lo.toFixed(2)}` : `$${lo.toFixed(2)} – $${hi.toFixed(2)}`;
});

const finalPrice = computed(() =>
  breakdown.value?.calculated_price != null
    ? `$${Number(breakdown.value.calculated_price).toFixed(2)}`
    : null,
);

const displayedLines = computed<PriceLine[]>(() =>
  props.showLineBreakdown && breakdown.value ? breakdown.value.lines : [],
);

// ── Preset deadline options (fallback if API returns nothing) ─────────────────
const DEADLINE_PRESETS: DeadlineConfig[] = [
  { id: 1, name: "3 hours",  code: "3h",   hours: 3,   is_urgent: true  },
  { id: 2, name: "6 hours",  code: "6h",   hours: 6,   is_urgent: true  },
  { id: 3, name: "12 hours", code: "12h",  hours: 12,  is_urgent: true  },
  { id: 4, name: "24 hours", code: "24h",  hours: 24,  is_urgent: false },
  { id: 5, name: "2 days",   code: "48h",  hours: 48,  is_urgent: false },
  { id: 6, name: "3 days",   code: "72h",  hours: 72,  is_urgent: false },
  { id: 7, name: "5 days",   code: "120h", hours: 120, is_urgent: false },
  { id: 8, name: "7 days",   code: "168h", hours: 168, is_urgent: false },
  { id: 9, name: "14 days",  code: "336h", hours: 336, is_urgent: false },
];

const deadlineOptions = computed(() =>
  deadlines.value.length ? deadlines.value : DEADLINE_PRESETS,
);

// ── Helpers ───────────────────────────────────────────────────────────────────
function buildPayload() {
  return {
    service_code:          props.serviceCode,
    pages:                 pages.value,
    deadline_hours:        deadlineHours.value,
    spacing:               spacing.value,
    paper_type_code:       paperCode.value || (paperTypes.value[0]?.code ?? "essay"),
    work_type_code:        "writing",
    subject_code:          "general",
    academic_level_code:   levelCode.value || (academicLevels.value[0]?.code ?? "undergraduate"),
  };
}

// ── Quote calls ───────────────────────────────────────────────────────────────
let debounceTimer: ReturnType<typeof setTimeout> | null = null;

async function fetchEstimate() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    quoteLoading.value = true;
    quoteError.value = "";
    showBreakdown.value = false;
    breakdown.value = null;
    try {
      const { data } = await pricingApi.startPaperQuote(buildPayload());
      estimate.value = data;
      sessionId.value = data.session_id;
    } catch {
      quoteError.value = "Could not fetch price. Please try again.";
    } finally {
      quoteLoading.value = false;
    }
  }, 350);
}

async function getExactPrice() {
  if (!sessionId.value) { await fetchEstimate(); return; }
  quoteLoading.value = true;
  quoteError.value = "";
  try {
    const { data } = await pricingApi.updatePaperQuote(sessionId.value, buildPayload());
    breakdown.value = data;
    showBreakdown.value = true;
  } catch {
    quoteError.value = "Could not calculate price. Please try again.";
  } finally {
    quoteLoading.value = false;
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const [levelsRes, typesRes, deadlinesRes] = await Promise.allSettled([
      pricingApi.academicLevels(),
      pricingApi.paperTypes(),
      pricingApi.deadlineConfigs(),
    ]);
    if (levelsRes.status === "fulfilled")   academicLevels.value = levelsRes.value.data.filter(o => o.is_active !== false);
    if (typesRes.status === "fulfilled")    paperTypes.value     = typesRes.value.data.filter(o => o.is_active !== false);
    if (deadlinesRes.status === "fulfilled") deadlines.value     = deadlinesRes.value.data.filter(o => o.is_active !== false);

    // Set defaults once options are loaded
    if (!levelCode.value && academicLevels.value.length)
      levelCode.value = academicLevels.value.find(l => l.code === "undergraduate")?.code ?? academicLevels.value[0].code;
    if (!paperCode.value && paperTypes.value.length)
      paperCode.value = paperTypes.value.find(t => t.code === "essay")?.code ?? paperTypes.value[0].code;
  } catch { /* non-fatal — options will be empty, quote will still work */ }
  finally {
    configLoading.value = false;
    fetchEstimate();
  }
});

watch([pages, deadlineHours, levelCode, paperCode, spacing], fetchEstimate);
</script>

<template>
  <div class="not-prose my-8 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

    <!-- Header -->
    <div class="bg-gradient-to-r from-ink to-slate-700 px-6 py-5 text-white">
      <div class="flex items-center gap-3">
        <Calculator class="size-6 shrink-0 text-slate-300" />
        <div>
          <h2 class="text-lg font-bold leading-tight">{{ title }}</h2>
          <p v-if="subtitle" class="mt-0.5 text-sm text-slate-300">{{ subtitle }}</p>
        </div>
      </div>
    </div>

    <!-- Loading config -->
    <div v-if="configLoading" class="flex items-center justify-center gap-2 px-6 py-10 text-sm text-graphite">
      <RefreshCw class="size-4 animate-spin" /> Loading options…
    </div>

    <template v-else>
      <!-- Inputs -->
      <div class="grid gap-4 px-6 py-5 sm:grid-cols-2">

        <!-- Academic level -->
        <label v-if="academicLevels.length" class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Academic level</span>
          <select
            v-model="levelCode"
            class="focus-ring mt-1 h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm"
          >
            <option v-for="l in academicLevels" :key="l.code" :value="l.code">{{ l.name }}</option>
          </select>
        </label>

        <!-- Paper type -->
        <label v-if="paperTypes.length" class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Type of paper</span>
          <select
            v-model="paperCode"
            class="focus-ring mt-1 h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm"
          >
            <option v-for="t in paperTypes" :key="t.code" :value="t.code">{{ t.name }}</option>
          </select>
        </label>

        <!-- Pages -->
        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Pages</span>
          <div class="mt-1 flex items-center gap-2">
            <button
              type="button"
              class="focus-ring flex size-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-lg font-bold text-ink hover:bg-slate-50 disabled:opacity-40"
              :disabled="pages <= 1"
              @click="pages = Math.max(1, pages - 1)"
            >−</button>
            <input
              v-model.number="pages"
              type="number"
              min="1"
              max="500"
              class="focus-ring h-10 w-full rounded-lg border border-slate-200 px-3 text-center text-sm font-semibold"
            />
            <button
              type="button"
              class="focus-ring flex size-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-lg font-bold text-ink hover:bg-slate-50"
              @click="pages = Math.min(500, pages + 1)"
            >+</button>
          </div>
          <p class="text-xs text-graphite">≈ {{ pages * 275 }} words · {{ spacing === 'double' ? 'double' : 'single' }} spaced</p>
        </label>

        <!-- Deadline -->
        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Deadline</span>
          <select
            v-model.number="deadlineHours"
            class="focus-ring mt-1 h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm"
          >
            <option v-for="d in deadlineOptions" :key="d.code" :value="d.hours ?? Number(d.code)">
              {{ d.name }}{{ d.is_urgent ? ' ⚡' : '' }}
            </option>
          </select>
        </label>

      </div>

      <!-- Price display -->
      <div class="border-t border-slate-100 px-6 py-5">

        <!-- Error -->
        <p v-if="quoteError" class="mb-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {{ quoteError }}
        </p>

        <!-- Estimate range (before exact calculation) -->
        <div v-if="!showBreakdown && estimateRange" class="mb-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Estimated price</p>
          <div class="mt-1 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-ink">{{ estimateRange }}</span>
            <span class="text-sm text-graphite">{{ currency }}</span>
            <RefreshCw v-if="quoteLoading" class="size-4 animate-spin text-graphite" />
          </div>
          <p class="mt-1 text-xs text-graphite">Final price may vary by subject and writer level.</p>
        </div>

        <!-- Exact price + line breakdown -->
        <div v-if="showBreakdown && breakdown">
          <div class="mb-3 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-ink">{{ finalPrice }}</span>
            <span class="text-sm text-graphite">{{ currency }}</span>
          </div>

          <ul v-if="displayedLines.length" class="mb-4 divide-y divide-slate-100 rounded-lg border border-slate-200 bg-slate-50">
            <li
              v-for="line in displayedLines"
              :key="line.code"
              class="flex items-center justify-between px-4 py-2 text-sm"
            >
              <span class="text-graphite">{{ line.label }}</span>
              <span class="font-semibold text-ink">${{ Number(line.amount).toFixed(2) }}</span>
            </li>
          </ul>
        </div>

        <!-- Loading spinner when no price yet -->
        <div v-if="quoteLoading && !estimateRange && !finalPrice" class="mb-4 flex items-center gap-2 text-sm text-graphite">
          <RefreshCw class="size-4 animate-spin" /> Calculating…
        </div>

        <!-- Action buttons -->
        <div class="flex flex-col gap-2 sm:flex-row">
          <button
            v-if="!showBreakdown"
            type="button"
            :disabled="quoteLoading"
            class="focus-ring inline-flex h-11 flex-1 items-center justify-center gap-2 rounded-xl border border-ink bg-white px-5 text-sm font-semibold text-ink hover:bg-slate-50 disabled:opacity-50"
            @click="getExactPrice"
          >
            <RefreshCw v-if="quoteLoading" class="size-4 animate-spin" />
            <Calculator v-else class="size-4" />
            Get exact price
          </button>

          <a
            :href="ctaUrl"
            class="focus-ring inline-flex h-11 flex-1 items-center justify-center gap-2 rounded-xl bg-berry px-5 text-sm font-bold text-white shadow-md hover:bg-rose-700 transition-colors"
          >
            {{ ctaText }}
            <ArrowRight class="size-4" />
          </a>
        </div>

        <p class="mt-3 text-center text-xs text-slate-400">
          No credit card required · 100% confidential
        </p>
      </div>
    </template>
  </div>
</template>
