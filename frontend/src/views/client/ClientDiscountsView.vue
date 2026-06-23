<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { Clock, Copy, Gift, Loader2, RefreshCw, Tag } from "@lucide/vue";
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

const discounts = ref<AvailableDiscount[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const copiedCode = ref<string | null>(null);

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const res = await api.post<AvailableDiscount[]>(
      apiPath("/discounts/client/available/"),
      { subtotal: "100.00", payable_type: "order", has_prior_paid_purchase: false },
    );
    discounts.value = res.data;
  } catch {
    error.value = "Could not load your discounts. Please try again.";
  } finally {
    loading.value = false;
  }
}

function copyCode(code: string) {
  navigator.clipboard.writeText(code).catch(() => {});
  copiedCode.value = code;
  setTimeout(() => { copiedCode.value = null; }, 2000);
}

function formatValue(d: AvailableDiscount) {
  if (d.discount_type === "percentage") return `${d.discount_value}% off`;
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

onMounted(load);
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-slate-900">My Discounts</h1>
        <p class="mt-0.5 text-sm text-slate-500">Discount codes available on your next order.</p>
      </div>
      <button
        class="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
        :disabled="loading"
        @click="load"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="{ 'animate-spin': loading }" />
        Refresh
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16 text-slate-400">
      <Loader2 class="h-6 w-6 animate-spin" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </div>

    <!-- Empty state -->
    <div v-else-if="!hasDiscounts" class="rounded-2xl border border-slate-100 bg-white p-12 text-center shadow-sm">
      <Gift class="mx-auto mb-4 h-10 w-10 text-slate-300" />
      <p class="text-sm font-semibold text-slate-700">No discount codes yet</p>
      <p class="mt-1.5 text-sm text-slate-400 max-w-xs mx-auto">Complete orders to earn loyalty points and unlock personal discount codes. Referral bonuses also show here.</p>
    </div>

    <!-- Discount cards -->
    <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="d in discounts"
        :key="d.discount_id"
        class="flex flex-col rounded-2xl border border-slate-100 bg-white p-5 shadow-sm"
      >
        <!-- Badge row -->
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

        <!-- Name + description -->
        <p class="mb-1 text-sm font-semibold text-slate-900">{{ d.name || d.frontend_label }}</p>
        <p class="mb-4 flex-1 text-xs leading-relaxed text-slate-500">{{ d.explanation || d.description }}</p>

        <!-- Code block -->
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

        <!-- Expiry / usage -->
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

    <!-- How-to hint -->
    <div class="rounded-xl border border-slate-100 bg-slate-50 px-5 py-4 text-sm text-slate-500">
      <span class="font-semibold text-slate-700">How to use: </span>
      Copy the code above and paste it into the "Have a discount code?" field on the order page. The saving is applied instantly before you pay.
    </div>

  </div>
</template>
