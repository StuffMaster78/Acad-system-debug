<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { CheckCircle2, Clock, Copy, Gift, Loader2, Lock, RefreshCw, Tag, TrendingUp } from "@lucide/vue";
import { api, apiPath } from "@/api/client";

interface AvailableDiscount {
  discount_id: number;
  discount_code: string;
  name: string;
  description: string;
  origin: string;
  discount_type: string;
  discount_value: string;
  usage_remaining: number | null;
  client_usage_remaining: number | null;
  expires_at: string | null;
  reason: string;
  explanation: string;
  frontend_label: string;
  frontend_badge: string;
  cta_label: string;
}

interface SpendTier {
  id: number;
  name: string;
  minimum_lifetime_spend: string;
  discount_value: string;
  discount_code: string;
  discount_type: string;
  unlocked: boolean;
}

interface SpendTierProgress {
  lifetime_spend: string;
  current_tier: SpendTier | null;
  next_tier: SpendTier | null;
  spend_needed_for_next: string;
  progress_pct: number;
  tiers: SpendTier[];
}

// ── Discounts ─────────────────────────────────────────────────────────────────
const discounts = ref<AvailableDiscount[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const copiedCode = ref<string | null>(null);

// ── Spend tier progress ───────────────────────────────────────────────────────
const progress = ref<SpendTierProgress | null>(null);
const progressLoading = ref(false);

async function loadProgress() {
  progressLoading.value = true;
  try {
    const res = await api.get<SpendTierProgress>(apiPath("/discounts/client/spend-tier-progress/"));
    progress.value = res.data;
  } catch {
    // non-critical — tier panel stays hidden
  } finally {
    progressLoading.value = false;
  }
}

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const lifetimeSpend = progress.value?.lifetime_spend ?? "0.00";
    const res = await api.post<AvailableDiscount[]>(
      apiPath("/discounts/client/available/"),
      { subtotal: "100.00", payable_type: "order", has_prior_paid_purchase: false, lifetime_spend: lifetimeSpend },
    );
    discounts.value = res.data;
  } catch {
    error.value = "Could not load your discounts. Please try again.";
  } finally {
    loading.value = false;
  }
}

async function refresh() {
  await loadProgress();
  await load();
}

function copyCode(code: string) {
  navigator.clipboard.writeText(code).catch(() => {});
  copiedCode.value = code;
  setTimeout(() => { copiedCode.value = null; }, 2000);
}

function formatValue(d: AvailableDiscount | SpendTier) {
  if (d.discount_type === "percentage") return `${parseFloat(d.discount_value).toFixed(0)}% off`;
  return `$${d.discount_value} off`;
}

function formatExpiry(dt: string | null) {
  if (!dt) return "No expiry";
  return new Date(dt).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function isExpiringSoon(dt: string | null) {
  if (!dt) return false;
  return (new Date(dt).getTime() - Date.now()) < 3 * 24 * 60 * 60 * 1000;
}

function money(v: string) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(parseFloat(v));
}

const originLabel: Record<string, string> = {
  loyalty: "Loyalty Reward",
  referral: "Referral Bonus",
  first_order: "First Order",
  holiday: "Holiday Deal",
  campaign: "Promotion",
  spend_tier: "Spend Tier",
  manual: "Special Code",
  system: "System Code",
};

const originColor: Record<string, string> = {
  loyalty:     "bg-amber-50 text-amber-700 border-amber-200",
  referral:    "bg-violet-50 text-violet-700 border-violet-200",
  first_order: "bg-emerald-50 text-emerald-700 border-emerald-200",
  holiday:     "bg-red-50 text-red-700 border-red-200",
  campaign:    "bg-blue-50 text-blue-700 border-blue-200",
  spend_tier:  "bg-sky-50 text-sky-700 border-sky-200",
  manual:      "bg-slate-50 text-slate-700 border-slate-200",
  system:      "bg-slate-50 text-slate-700 border-slate-200",
};

const hasDiscounts = computed(() => discounts.value.length > 0);
const hasTiers = computed(() => (progress.value?.tiers.length ?? 0) > 0);

onMounted(async () => {
  await loadProgress();
  await load();
});
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-slate-900">My Discounts</h1>
        <p class="mt-0.5 text-sm text-slate-500">Discount codes and loyalty spend rewards available on your next order.</p>
      </div>
      <button
        class="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
        :disabled="loading || progressLoading"
        @click="refresh"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="{ 'animate-spin': loading || progressLoading }" />
        Refresh
      </button>
    </div>

    <!-- ── Spend Tier Progress ────────────────────────────────────────────────── -->
    <div v-if="hasTiers" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-5">
      <!-- Header row -->
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="flex items-center gap-2">
            <TrendingUp class="h-4 w-4 text-sky-600" />
            <h2 class="text-sm font-bold text-slate-900">Loyalty Spend Tiers</h2>
          </div>
          <p class="mt-0.5 text-xs text-slate-500">
            Unlock permanent discount codes as your lifetime spend grows.
            You've spent <span class="font-semibold text-slate-800">{{ money(progress!.lifetime_spend) }}</span> total.
          </p>
        </div>
        <div v-if="progress!.current_tier" class="shrink-0 text-right">
          <p class="text-[10px] font-semibold uppercase tracking-wide text-slate-400">Current tier</p>
          <p class="text-sm font-bold text-sky-700">{{ progress!.current_tier.name }}</p>
        </div>
      </div>

      <!-- Next tier progress bar -->
      <div v-if="progress!.next_tier" class="space-y-2">
        <div class="flex items-center justify-between text-xs">
          <span class="text-slate-500">
            {{ money(progress!.lifetime_spend) }} spent
          </span>
          <span class="font-semibold text-slate-700">
            {{ money(progress!.spend_needed_for_next) }} more to unlock
            <span class="text-sky-600">{{ progress!.next_tier.name }}</span>
            ({{ progress!.next_tier.discount_value }}% off)
          </span>
        </div>
        <div class="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            class="h-full rounded-full bg-gradient-to-r from-sky-400 to-sky-600 transition-all duration-700"
            :style="{ width: progress!.progress_pct + '%' }"
          />
        </div>
        <p class="text-right text-[10px] text-slate-400">{{ progress!.progress_pct }}% of the way there</p>
      </div>
      <div v-else class="flex items-center gap-2 rounded-xl bg-sky-50 border border-sky-200 px-4 py-3 text-sm text-sky-800">
        <CheckCircle2 class="h-4 w-4 text-sky-500 shrink-0" />
        You've unlocked all spend tiers — maximum loyalty discount active!
      </div>

      <!-- Tier ladder -->
      <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div
          v-for="tier in progress!.tiers"
          :key="tier.id"
          class="flex items-center gap-3 rounded-xl border px-3 py-2.5 transition-all"
          :class="tier.unlocked
            ? 'border-sky-200 bg-sky-50'
            : 'border-slate-100 bg-slate-50 opacity-60'"
        >
          <div
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm"
            :class="tier.unlocked ? 'bg-sky-600 text-white' : 'bg-slate-200 text-slate-400'"
          >
            <CheckCircle2 v-if="tier.unlocked" class="h-4 w-4" />
            <Lock v-else class="h-3.5 w-3.5" />
          </div>
          <div class="min-w-0">
            <p class="truncate text-xs font-semibold" :class="tier.unlocked ? 'text-sky-900' : 'text-slate-500'">{{ tier.name }}</p>
            <p class="text-[10px]" :class="tier.unlocked ? 'text-sky-600' : 'text-slate-400'">
              {{ formatValue(tier) }} · at {{ money(tier.minimum_lifetime_spend) }}
            </p>
            <div v-if="tier.unlocked" class="mt-1 flex items-center gap-1.5">
              <code class="rounded bg-white px-1.5 py-0.5 text-[10px] font-mono font-bold text-sky-800 ring-1 ring-sky-200">{{ tier.discount_code }}</code>
              <button
                class="text-[9px] font-semibold text-sky-600 hover:underline"
                @click="copyCode(tier.discount_code)"
              >{{ copiedCode === tier.discount_code ? 'Copied!' : 'Copy' }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Available Discounts ─────────────────────────────────────────────────── -->
    <div>
      <h2 class="mb-3 text-sm font-semibold text-slate-700">Available Codes</h2>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-12 text-slate-400">
        <Loader2 class="h-6 w-6 animate-spin" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        {{ error }}
      </div>

      <!-- Empty -->
      <div v-else-if="!hasDiscounts" class="rounded-2xl border border-slate-100 bg-white p-10 text-center shadow-sm">
        <Gift class="mx-auto mb-3 h-9 w-9 text-slate-300" />
        <p class="text-sm font-semibold text-slate-700">No discount codes yet</p>
        <p class="mt-1 text-xs text-slate-400 max-w-xs mx-auto">Complete orders to earn loyalty points and unlock spend tier rewards. Referral bonuses and promotions also appear here.</p>
      </div>

      <!-- Cards -->
      <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="d in discounts"
          :key="d.discount_id"
          class="flex flex-col rounded-2xl border border-slate-100 bg-white p-5 shadow-sm"
        >
          <div class="mb-3 flex items-center justify-between gap-2">
            <span
              class="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide"
              :class="originColor[d.origin] ?? 'bg-slate-50 text-slate-700 border-slate-200'"
            >
              <Tag class="h-3 w-3" />
              {{ originLabel[d.origin] ?? d.frontend_badge ?? d.origin }}
            </span>
            <span class="text-base font-bold text-slate-900">{{ formatValue(d) }}</span>
          </div>
          <p class="mb-1 text-sm font-semibold text-slate-900">{{ d.name || d.frontend_label }}</p>
          <p class="mb-4 flex-1 text-xs leading-relaxed text-slate-500">{{ d.explanation || d.description }}</p>
          <div class="mb-4 flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2">
            <code class="flex-1 font-mono text-sm font-bold tracking-widest text-slate-800">{{ d.discount_code }}</code>
            <button
              class="flex items-center gap-1 rounded-lg bg-white px-2.5 py-1 text-xs font-semibold text-slate-600 shadow-sm ring-1 ring-slate-200 transition hover:bg-slate-100"
              @click="copyCode(d.discount_code)"
            >
              <Copy class="h-3 w-3" />
              {{ copiedCode === d.discount_code ? 'Copied!' : 'Copy' }}
            </button>
          </div>
          <div class="flex items-center justify-between text-[11px] text-slate-400">
            <span class="flex items-center gap-1" :class="{ 'text-red-500 font-semibold': isExpiringSoon(d.expires_at) }">
              <Clock class="h-3 w-3" />
              {{ formatExpiry(d.expires_at) }}
            </span>
            <span v-if="d.client_usage_remaining !== null">
              {{ d.client_usage_remaining }} use{{ d.client_usage_remaining === 1 ? '' : 's' }} left
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- How-to hint -->
    <div class="rounded-xl border border-slate-100 bg-slate-50 px-5 py-4 text-sm text-slate-500">
      <span class="font-semibold text-slate-700">How to use: </span>
      Copy any code above and paste it into the "Have a discount code?" field at checkout. Spend tier codes are permanent — they never expire as long as your lifetime spend stays above the threshold.
    </div>

  </div>
</template>
