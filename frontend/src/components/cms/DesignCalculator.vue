<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { AlertTriangle, ArrowRight, Calculator, RefreshCw } from "@lucide/vue";
import { pricingApi, type DeadlineConfig } from "@/api/pricing";
import { useQuoteSession, formatMoney, lineAmountDisplay } from "@/composables/useQuoteSession";
import type { ServiceAddon } from "@/types/orders";

const props = withDefaults(defineProps<{
  title?:               string;
  subtitle?:            string;
  serviceCode?:         string;
  unitLabel?:           string;   // e.g. "slides", "pages", "pieces"
  defaultQuantity?:     number;
  defaultDeadlineHours?: number;
  showLineBreakdown?:   boolean;
  ctaText?:             string;
  ctaUrl?:              string;
}>(), {
  title:               "Get your design price",
  subtitle:            "No account needed — see your price instantly.",
  serviceCode:         "presentation_design",
  unitLabel:           "slides",
  defaultQuantity:     10,
  defaultDeadlineHours: 48,
  showLineBreakdown:   true,
  ctaText:             "Place Order",
  ctaUrl:              "/auth/register",
});

// ── State ─────────────────────────────────────────────────────────────────
const quantity     = ref(props.defaultQuantity);
const deadlineHours = ref(props.defaultDeadlineHours);
const addonCodes   = ref<string[]>([]);
const deadlines    = ref<DeadlineConfig[]>([]);
const addons       = ref<ServiceAddon[]>([]);
const configLoading = ref(true);

// ── Fallback deadlines ─────────────────────────────────────────────────────
const DEADLINE_PRESETS: DeadlineConfig[] = [
  { id: 1, name: "24 hours", code: "24h",  hours: 24,  is_urgent: false },
  { id: 2, name: "2 days",   code: "48h",  hours: 48,  is_urgent: false },
  { id: 3, name: "3 days",   code: "72h",  hours: 72,  is_urgent: false },
  { id: 4, name: "5 days",   code: "120h", hours: 120, is_urgent: false },
  { id: 5, name: "7 days",   code: "168h", hours: 168, is_urgent: false },
];
const deadlineOptions = () => deadlines.value.length ? deadlines.value : DEADLINE_PRESETS;

// ── Quote session ──────────────────────────────────────────────────────────
const {
  quoteLoading, showBreakdown, quoteError, suggestions,
  estimateRange, finalPrice, visibleLines, totalLine,
  fetchEstimate, getExactPrice, sessionId,
} = useQuoteSession("design", () => ({
  service_code:          props.serviceCode,
  quantity:              quantity.value,
  slides:                quantity.value,
  deadline_hours:        deadlineHours.value,
  selected_addon_codes:  addonCodes.value,
}));

// ── Init ───────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const [deadlinesRes, addonsRes] = await Promise.allSettled([
      pricingApi.deadlineConfigs(),
      pricingApi.addons(props.serviceCode),
    ]);
    if (deadlinesRes.status === "fulfilled")
      deadlines.value = deadlinesRes.value.data.filter((d) => d.is_active !== false);
    if (addonsRes.status === "fulfilled")
      addons.value = addonsRes.value.data;
  } catch { /* non-fatal */ }
  finally {
    configLoading.value = false;
    fetchEstimate();
  }
});

watch([quantity, deadlineHours, addonCodes], fetchEstimate);

// ── Deadline urgency helper ────────────────────────────────────────────────
function isUrgentDeadline(): boolean {
  const d = deadlineOptions().find((o) => (o.hours ?? 0) === deadlineHours.value);
  return d?.is_urgent ?? false;
}

function toggleAddon(code: string) {
  addonCodes.value = addonCodes.value.includes(code)
    ? addonCodes.value.filter((c) => c !== code)
    : [...addonCodes.value, code];
}

const deadlineWarning = () =>
  suggestions.value.find((s) => s.type === "deadline_adjustment") ?? null;

const ctaHref = () => {
  if (!sessionId.value) return props.ctaUrl;
  const sep = props.ctaUrl.includes("?") ? "&" : "?";
  return `${props.ctaUrl}${sep}session_id=${sessionId.value}`;
};
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

    <!-- Loading -->
    <div v-if="configLoading" class="flex items-center justify-center gap-2 px-6 py-10 text-sm text-graphite">
      <RefreshCw class="size-4 animate-spin" /> Loading options…
    </div>

    <template v-else>
      <!-- Inputs -->
      <div class="grid gap-4 px-6 py-5 sm:grid-cols-2">

        <!-- Quantity stepper -->
        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-graphite">
            Number of {{ unitLabel }}
          </span>
          <div class="mt-1 flex items-center gap-2">
            <button
              type="button"
              class="focus-ring flex size-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-lg font-bold text-ink hover:bg-slate-50 disabled:opacity-40"
              :disabled="quantity <= 1"
              @click="quantity = Math.max(1, quantity - 1)"
            >−</button>
            <input
              v-model.number="quantity"
              type="number"
              min="1"
              max="500"
              class="focus-ring h-10 w-full rounded-lg border border-slate-200 px-3 text-center text-sm font-semibold"
            />
            <button
              type="button"
              class="focus-ring flex size-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-lg font-bold text-ink hover:bg-slate-50"
              @click="quantity = Math.min(500, quantity + 1)"
            >+</button>
          </div>
        </label>

        <!-- Deadline -->
        <label class="block space-y-1">
          <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Deadline</span>
          <select
            v-model.number="deadlineHours"
            class="focus-ring mt-1 h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm"
          >
            <option v-for="d in deadlineOptions()" :key="d.code" :value="d.hours ?? Number(d.code)">
              {{ d.name }}{{ d.is_urgent ? " ⚡" : "" }}
            </option>
          </select>
        </label>

      </div>

      <!-- Add-ons -->
      <div v-if="addons.length" class="border-t border-slate-100 px-6 pb-5">
        <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Add-ons</p>
        <div class="divide-y divide-slate-100 rounded-lg border border-slate-200">
          <label
            v-for="addon in addons"
            :key="addon.addon_code"
            class="flex cursor-pointer items-start gap-3 px-4 py-3 transition-colors hover:bg-slate-50"
            :class="addonCodes.includes(addon.addon_code) ? 'bg-signal/5' : ''"
          >
            <input
              type="checkbox"
              class="mt-0.5 h-4 w-4 rounded border-slate-300 text-signal"
              :checked="addonCodes.includes(addon.addon_code)"
              @change="toggleAddon(addon.addon_code)"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center justify-between gap-2">
                <span class="text-sm font-medium text-ink">{{ addon.name }}</span>
                <span class="shrink-0 text-sm font-semibold text-graphite">+{{ formatMoney(Number(addon.flat_amount), "USD") }}</span>
              </div>
              <p v-if="addon.description" class="mt-0.5 text-xs text-graphite">{{ addon.description }}</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Price zone -->
      <div class="border-t border-slate-100 px-6 py-5">

        <!-- Error -->
        <p v-if="quoteError" class="mb-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {{ quoteError }}
        </p>

        <!-- Tight deadline warning -->
        <div v-if="deadlineWarning()" class="mb-4 flex items-start gap-2.5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
          <AlertTriangle class="mt-0.5 size-4 shrink-0 text-saffron" />
          <div class="flex-1 text-sm text-amber-800">
            <p>{{ deadlineWarning()!.message }}</p>
            <button
              v-if="deadlineWarning()!.recommended_deadline_hours"
              class="mt-1.5 text-xs font-semibold underline"
              type="button"
              @click="deadlineHours = deadlineWarning()!.recommended_deadline_hours!"
            >Use {{ deadlineWarning()!.recommended_deadline_hours }}h deadline</button>
          </div>
        </div>

        <!-- Estimate range -->
        <div v-if="!showBreakdown && estimateRange()" class="mb-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Estimated price</p>
          <div class="mt-1 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-ink">{{ estimateRange() }}</span>
            <RefreshCw v-if="quoteLoading" class="size-4 animate-spin text-graphite" />
          </div>
          <p class="mt-1 text-xs text-graphite">Final price may vary. Get an exact quote below.</p>
        </div>

        <!-- Exact price + breakdown -->
        <div v-if="showBreakdown">
          <div class="mb-3 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-ink">{{ finalPrice() }}</span>
            <RefreshCw v-if="quoteLoading" class="size-4 animate-spin text-graphite" />
          </div>
          <ul v-if="showLineBreakdown && visibleLines().length" class="mb-4 divide-y divide-slate-100 rounded-lg border border-slate-200 bg-slate-50">
            <li
              v-for="line in visibleLines()"
              :key="line.code"
              class="flex items-center justify-between px-4 py-2 text-sm"
            >
              <span class="text-graphite">
                {{ line.label }}
                <span v-if="line.line_type === 'multiplier' && line.metadata?.multiplier" class="ml-1 text-xs text-slate-400">(×{{ line.metadata.multiplier }})</span>
              </span>
              <span
                class="font-semibold"
                :class="Number(line.amount) < 0 ? 'text-emerald-600' : (line.code === 'deadline' && isUrgentDeadline()) ? 'text-amber-600' : 'text-ink'"
              >{{ lineAmountDisplay(line.amount, line.line_type) }}</span>
            </li>
            <li v-if="totalLine()" class="flex items-center justify-between px-4 py-2.5 text-sm font-bold text-ink">
              <span>{{ totalLine()!.label }}</span>
              <span>{{ formatMoney(Number(totalLine()!.amount), "") }}</span>
            </li>
          </ul>
        </div>

        <!-- Calculating spinner (initial) -->
        <div v-if="quoteLoading && !estimateRange() && !finalPrice()" class="mb-4 flex items-center gap-2 text-sm text-graphite">
          <RefreshCw class="size-4 animate-spin" /> Calculating…
        </div>

        <!-- Actions -->
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
            :href="ctaHref()"
            class="focus-ring inline-flex h-11 flex-1 items-center justify-center gap-2 rounded-xl bg-berry px-5 text-sm font-bold text-white shadow-md transition-colors hover:bg-rose-700"
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
