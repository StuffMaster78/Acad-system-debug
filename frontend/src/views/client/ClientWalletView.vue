<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import PaymentDisclosureBanner from "@/components/payment/PaymentDisclosureBanner.vue";
import {
  ArrowDownLeft,
  ArrowUpRight,
  Banknote,
  CheckCircle2,
  Clock3,
  Copy,
  CreditCard,
  Gift,
  Loader2,
  Lock,
  RefreshCw,
  Smartphone,
  Star,
  TrendingUp,
} from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useWalletStore } from "@/stores/wallets";
import { useAuthStore } from "@/stores/auth";

const wallets = useWalletStore();
const auth = useAuthStore();

const PRESETS = [10, 25, 50, 100, 200];

const isDev = import.meta.env.DEV;

const topup = reactive({
  preset: null as number | null,
  custom: "",
  provider: "stripe" as "stripe" | "mock",
});
const topupError = ref("");
const previewSuccess = ref(false);
const paymentDisclosureAccepted = ref(false);

const topupAmount = () => {
  if (topup.preset !== null) return topup.preset;
  const n = Number(topup.custom);
  return n > 0 ? n : null;
};

function selectPreset(val: number) {
  topup.preset = topup.preset === val ? null : val;
  topup.custom = "";
}

function onCustomInput() {
  topup.preset = null;
}

async function checkout() {
  topupError.value = "";
  previewSuccess.value = false;

  if (!paymentDisclosureAccepted.value) {
    topupError.value = "Please acknowledge the billing statement notice before checkout.";
    return;
  }

  const amount = topupAmount();
  if (!amount) {
    topupError.value = "Select or enter an amount to continue.";
    return;
  }

  try {
    await wallets.initiateTopup({ amount, provider: topup.provider });

    if (auth.isPreviewSession) {
      previewSuccess.value = true;
      topup.preset = null;
      topup.custom = "";
    }
  } catch {
    topupError.value = "Checkout failed. Please try again.";
  }
}

function money(value: string | number | undefined | null, currency = wallets.currency): string {
  if (value === undefined || value === null || value === "") return `${currency} 0.00`;
  const n = Number(value);
  if (Number.isNaN(n)) return `${currency} ${value}`;
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(n);
}

function dateLabel(value: string | undefined | null): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function entryTone(direction?: string): "success" | "danger" | "neutral" {
  if (direction === "credit") return "success";
  if (direction === "debit") return "danger";
  return "neutral";
}

function holdStatusTone(status: string): "warning" | "success" | "neutral" {
  if (status === "active" || status === "pending") return "warning";
  if (status === "released") return "success";
  return "neutral";
}

interface ReferralCode {
  code: string;
  referral_link: string;
  usage_stats?: { total_referrals?: number; successful_referrals?: number };
}

interface LoyaltySummary {
  loyalty_points: number;
  wallet_balance: string;
  tier: string;
  conversion_rate: string;
}

interface RedemptionItem {
  id: number;
  name: string;
  description: string | null;
  points_required: number;
  redemption_type: string;
  is_available: boolean;
  can_redeem: { can_redeem: boolean; message: string } | null;
}

const loyalty = ref<LoyaltySummary | null>(null);
const loyaltyLoading = ref(false);
const loyaltyConvertPoints = ref("");
const loyaltyConvertError = ref("");
const loyaltyConvertSubmitting = ref(false);
const loyaltyConvertSuccess = ref<{ converted: number; amount: string } | null>(null);
const loyaltyTab = ref<"convert" | "redeem">("convert");

const redemptionItems = ref<RedemptionItem[]>([]);
const redemptionLoading = ref(false);
const redeemingItemId = ref<number | null>(null);
const redemptionError = ref("");
const redemptionSuccess = ref<string | null>(null);

async function fetchRedemptionItems() {
  redemptionLoading.value = true;
  try {
    const { data } = await api.get<RedemptionItem[] | { results: RedemptionItem[] }>(
      apiPath("/loyalty-management/redemption-items/"),
    );
    redemptionItems.value = Array.isArray(data) ? data : (data as { results: RedemptionItem[] }).results ?? [];
  } catch {
    // Not critical
  } finally {
    redemptionLoading.value = false;
  }
}

async function redeemItem(itemId: number) {
  redemptionError.value = "";
  redemptionSuccess.value = null;
  redeemingItemId.value = itemId;
  try {
    await api.post(apiPath("/loyalty-management/redemption-requests/"), { item_id: itemId });
    redemptionSuccess.value = "Redemption request submitted! We'll process it shortly.";
    await fetchLoyalty();
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    redemptionError.value = detail ?? "Redemption failed. Please try again.";
  } finally {
    redeemingItemId.value = null;
  }
}

async function fetchLoyalty() {
  loyaltyLoading.value = true;
  try {
    const { data } = await api.get<LoyaltySummary>(apiPath("/loyalty-management/loyalty/summary/"));
    loyalty.value = data;
  } catch {
    // Not all accounts have loyalty enabled
  } finally {
    loyaltyLoading.value = false;
  }
}

async function convertLoyaltyPoints() {
  loyaltyConvertError.value = "";
  loyaltyConvertSuccess.value = null;
  const pts = parseInt(loyaltyConvertPoints.value, 10);
  if (!pts || pts <= 0) {
    loyaltyConvertError.value = "Enter a valid number of points.";
    return;
  }
  if (loyalty.value && pts > loyalty.value.loyalty_points) {
    loyaltyConvertError.value = "You don't have that many points.";
    return;
  }
  loyaltyConvertSubmitting.value = true;
  try {
    const { data } = await api.post<{ converted: number; amount: string }>(
      apiPath("/loyalty-management/loyalty/convert/"),
      { points: pts },
    );
    loyaltyConvertSuccess.value = data;
    loyaltyConvertPoints.value = "";
    // Refresh summary and wallet balance
    await Promise.all([fetchLoyalty(), wallets.hydrate()]);
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string; points?: string[] } } })?.response?.data;
    loyaltyConvertError.value = detail?.detail ?? detail?.points?.[0] ?? "Conversion failed. Try again.";
  } finally {
    loyaltyConvertSubmitting.value = false;
  }
}

const referralCode = ref<ReferralCode | null>(null);
const referralCodeLoading = ref(false);
const referralCodeCopied = ref(false);

async function fetchReferralCode() {
  if (auth.isPreviewSession) {
    referralCode.value = {
      code: "PREVIEW10",
      referral_link: "https://example.com?ref=PREVIEW10",
      usage_stats: { total_referrals: 3, successful_referrals: 1 },
    };
    return;
  }
  referralCodeLoading.value = true;
  try {
    const { data } = await api.get<ReferralCode | ReferralCode[]>(
      apiPath("/referrals/referral-codes/my-code/"),
    );
    referralCode.value = Array.isArray(data) ? data[0] ?? null : data;
  } catch {
    // Not all accounts have referral codes enabled
  } finally {
    referralCodeLoading.value = false;
  }
}

function copyReferralCode() {
  if (!referralCode.value?.code) return;
  navigator.clipboard.writeText(referralCode.value.code).then(() => {
    referralCodeCopied.value = true;
    setTimeout(() => { referralCodeCopied.value = false; }, 2000);
  });
}

type LedgerFilter = "all" | "credits" | "debits";
const ledgerFilter = ref<LedgerFilter>("all");
const filteredEntries = computed(() => {
  if (ledgerFilter.value === "credits")  return wallets.entries.filter(e => e.direction === "credit");
  if (ledgerFilter.value === "debits")   return wallets.entries.filter(e => e.direction === "debit");
  return wallets.entries;
});

type SecondaryTab = "holds" | "loyalty" | "referral";
const secondaryTab = ref<SecondaryTab>("holds");

onMounted(() => {
  wallets.hydrate().catch(() => undefined);
  fetchReferralCode();
  fetchLoyalty();
  fetchRedemptionItems();
});
</script>

<template>
  <div class="space-y-6">

    <!-- ── Page header ──────────────────────────────────────────────────── -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-widest text-signal">Client</p>
        <h1 class="mt-1 text-2xl font-bold text-ink">Wallet</h1>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50"
        type="button"
        :disabled="wallets.isLoading"
        @click="wallets.hydrate().catch(() => undefined)"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="wallets.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <div v-if="wallets.error" class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ wallets.error }}</div>

    <!-- ── Balance hero + top-up ─────────────────────────────────────────── -->
    <section class="relative overflow-hidden rounded-2xl bg-slate-900 text-white">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.025)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.025)_1px,transparent_1px)] bg-[size:32px_32px]" />
      <div class="relative grid gap-0 lg:grid-cols-[1fr_380px]">

        <!-- Balance side -->
        <div class="px-6 py-7 lg:border-r lg:border-white/10">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Available balance</p>
          <p class="mt-2 text-5xl font-extrabold tabular-nums tracking-tight">
            <span v-if="wallets.isLoading" class="inline-block h-12 w-36 animate-pulse rounded-lg bg-white/10" />
            <span v-else>{{ money(wallets.wallet?.available_balance) }}</span>
          </p>
          <p class="mt-1.5 text-xs text-slate-500">Ready to use for orders</p>

          <div class="mt-6 flex flex-wrap gap-5 border-t border-white/10 pt-5">
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Pending</p>
              <p class="mt-1 text-lg font-bold tabular-nums">{{ money(wallets.wallet?.pending_balance) }}</p>
              <p class="text-xs text-slate-500">Processing</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">All-time in</p>
              <p class="mt-1 text-lg font-bold tabular-nums text-emerald-400">{{ money(wallets.wallet?.total_credited) }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">All-time out</p>
              <p class="mt-1 text-lg font-bold tabular-nums text-rose-400">{{ money(wallets.wallet?.total_debited) }}</p>
            </div>
          </div>
        </div>

        <!-- Top-up side -->
        <div class="border-t border-white/10 px-6 py-7 lg:border-t-0">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Add funds</p>

          <!-- Preview success -->
          <div v-if="previewSuccess" class="mt-4 space-y-3">
            <div class="flex items-center gap-3 rounded-xl border border-emerald-400/30 bg-emerald-500/10 p-4">
              <CheckCircle2 class="h-5 w-5 shrink-0 text-emerald-400" />
              <p class="text-sm font-semibold text-emerald-300">Wallet topped up (preview mode)</p>
            </div>
            <button class="focus-ring w-full rounded-xl border border-white/20 py-2.5 text-sm font-semibold text-slate-200 hover:bg-white/10 transition-colors" type="button" @click="previewSuccess = false">
              Top up again
            </button>
          </div>

          <div v-else class="mt-4 space-y-4">
            <!-- Amount presets -->
            <div class="grid grid-cols-5 gap-1.5">
              <button
                v-for="preset in PRESETS" :key="preset"
                class="focus-ring rounded-xl border py-2.5 text-sm font-bold transition-colors"
                :class="topup.preset === preset ? 'border-white bg-white text-slate-900' : 'border-white/20 text-white hover:border-white/50'"
                type="button"
                @click="selectPreset(preset)"
              >{{ preset }}</button>
            </div>
            <div class="relative">
              <span class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">{{ wallets.currency }}</span>
              <input
                v-model="topup.custom"
                class="focus-ring h-10 w-full rounded-xl border border-white/20 bg-white/10 pl-14 pr-3 text-sm text-white placeholder:text-slate-500"
                :class="topup.preset === null && topup.custom ? 'border-white' : ''"
                type="number" min="1" step="0.01" placeholder="Custom amount"
                @input="onCustomInput"
              />
            </div>

            <!-- Payment method -->
            <div class="space-y-1.5">
              <label
                class="flex cursor-pointer items-center gap-3 rounded-xl border p-3 transition-colors"
                :class="topup.provider === 'stripe' ? 'border-white bg-white/10' : 'border-white/20 hover:border-white/40'"
              >
                <input v-model="topup.provider" class="sr-only" type="radio" value="stripe" />
                <CreditCard class="h-4 w-4 shrink-0 text-slate-300" />
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-semibold text-white">Card</p>
                  <p class="text-xs text-slate-400">Visa, Mastercard — redirected to checkout</p>
                </div>
                <CheckCircle2 v-if="topup.provider === 'stripe'" class="h-4 w-4 shrink-0 text-white" />
              </label>
              <label
                v-if="isDev"
                class="flex cursor-pointer items-center gap-3 rounded-xl border p-3 transition-colors"
                :class="topup.provider === 'mock' ? 'border-white bg-white/10' : 'border-white/20 hover:border-white/40'"
              >
                <input v-model="topup.provider" class="sr-only" type="radio" value="mock" />
                <Smartphone class="h-4 w-4 shrink-0 text-slate-300" />
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-semibold text-white">Mock <span class="text-xs font-normal text-slate-400">(dev only)</span></p>
                  <p class="text-xs text-slate-400">Simulates checkout without a real payment</p>
                </div>
                <CheckCircle2 v-if="topup.provider === 'mock'" class="h-4 w-4 shrink-0 text-white" />
              </label>
            </div>

            <p v-if="topupError" class="rounded-xl border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-300">{{ topupError }}</p>

            <PaymentDisclosureBanner v-model="paymentDisclosureAccepted" context="wallet_topup" />

            <button
              class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-xl bg-white py-3 text-sm font-bold text-slate-900 transition-colors hover:bg-slate-100 disabled:opacity-50"
              type="button"
              :disabled="wallets.isMutating || !paymentDisclosureAccepted"
              @click="checkout"
            >
              <Loader2 v-if="wallets.isMutating" class="h-4 w-4 animate-spin" />
              <template v-else>
                {{ topup.provider === "mock" ? "Simulate top-up" : "Proceed to checkout" }}
                <span v-if="topupAmount()" class="opacity-70">— {{ wallets.currency }} {{ topupAmount() }}</span>
              </template>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Transaction ledger ────────────────────────────────────────────── -->
    <section class="rounded-xl border border-slate-200 bg-white">
      <div class="flex items-center justify-between gap-3 border-b border-slate-100 px-5 py-3.5">
        <div class="flex items-center gap-2">
          <TrendingUp class="h-4 w-4 text-signal" />
          <h2 class="text-sm font-semibold text-ink">Transaction ledger</h2>
        </div>
        <div class="flex items-center gap-0.5 rounded-lg border border-slate-200 bg-slate-50 p-0.5 text-xs font-semibold">
          <button
            v-for="tab in ([{ id: 'all', label: 'All' }, { id: 'credits', label: 'Credits' }, { id: 'debits', label: 'Debits' }] as const)"
            :key="tab.id"
            type="button"
            class="rounded-md px-2.5 py-1 transition-colors"
            :class="ledgerFilter === tab.id ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
            @click="ledgerFilter = tab.id"
          >{{ tab.label }}</button>
        </div>
      </div>

      <div v-if="wallets.isLoading && !wallets.entries.length" class="divide-y divide-slate-100">
        <div v-for="n in 5" :key="n" class="flex animate-pulse items-center gap-3 px-5 py-4">
          <div class="h-8 w-8 rounded-full bg-slate-100" />
          <div class="flex-1 space-y-1.5">
            <div class="h-3.5 w-2/5 rounded bg-slate-100" />
            <div class="h-3 w-1/4 rounded bg-slate-100" />
          </div>
          <div class="h-3.5 w-16 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!filteredEntries.length" class="px-5 py-14 text-center">
        <TrendingUp class="mx-auto h-9 w-9 text-slate-200" />
        <p class="mt-3 text-sm font-medium text-ink">
          {{ ledgerFilter === 'all' ? 'No transactions yet' : `No ${ledgerFilter} yet` }}
        </p>
        <p class="mt-1 text-xs text-graphite">Entries appear here once funds are added or orders are placed.</p>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div
          v-for="entry in filteredEntries"
          :key="entry.id"
          class="flex items-center gap-3 px-5 py-4"
        >
          <div
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
            :class="entry.direction === 'credit' ? 'bg-emerald-50' : 'bg-rose-50'"
          >
            <ArrowDownLeft v-if="entry.direction === 'credit'" class="h-3.5 w-3.5 text-emerald-500" />
            <ArrowUpRight v-else class="h-3.5 w-3.5 text-rose-400" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-ink">
              {{ entry.description || entry.entry_type || (entry.direction === "credit" ? "Credit" : "Debit") }}
            </p>
            <p class="mt-0.5 text-xs text-graphite">
              {{ entry.reference_type ? `${entry.reference_type} · ` : "" }}{{ dateLabel(entry.created_at) }}
            </p>
          </div>
          <div class="shrink-0 text-right">
            <p class="text-sm font-semibold tabular-nums" :class="entry.direction === 'credit' ? 'text-emerald-700' : 'text-rose-600'">
              {{ entry.direction === "credit" ? "+" : "−" }}{{ money(entry.amount) }}
            </p>
            <p v-if="entry.balance_after != null" class="mt-0.5 text-xs text-graphite">
              bal. {{ money(entry.balance_after) }}
            </p>
          </div>
          <StatusPill :label="entry.status ?? 'posted'" :tone="entryTone(entry.direction)" />
        </div>
      </div>
    </section>

    <!-- ── Secondary tabs: Holds | Loyalty | Referral ───────────────────── -->
    <section class="rounded-xl border border-slate-200 bg-white">
      <div class="flex gap-0 border-b border-slate-100">
        <button
          v-for="tab in ([
            { id: 'holds',    label: 'Active holds',    icon: Lock },
            { id: 'loyalty',  label: 'Loyalty points',  icon: Star },
            { id: 'referral', label: 'Refer a friend',  icon: Gift },
          ] as const)"
          :key="tab.id"
          type="button"
          class="flex items-center gap-1.5 border-b-2 px-5 py-3 text-sm font-semibold transition-colors"
          :class="secondaryTab === tab.id ? 'border-ink text-ink' : 'border-transparent text-graphite hover:text-ink'"
          @click="secondaryTab = tab.id"
        >
          <component :is="tab.icon" class="h-4 w-4" />
          {{ tab.label }}
        </button>
      </div>

      <!-- Holds -->
      <div v-if="secondaryTab === 'holds'">
        <div v-if="!wallets.holds.length" class="px-5 py-12 text-center">
          <Lock class="mx-auto h-8 w-8 text-slate-200" />
          <p class="mt-2 text-sm text-graphite">No holds. Funds reserved for pending orders appear here.</p>
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="hold in wallets.holds" :key="hold.id" class="flex items-start gap-4 px-5 py-4">
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-ink">{{ money(hold.amount) }}</p>
              <p v-if="hold.reason" class="mt-0.5 text-xs text-graphite">{{ hold.reason }}</p>
              <p class="mt-0.5 text-xs text-graphite">{{ dateLabel(hold.created_at) }}</p>
              <p v-if="hold.expires_at" class="mt-0.5 text-xs text-graphite">Expires {{ dateLabel(hold.expires_at) }}</p>
            </div>
            <StatusPill :label="hold.status" :tone="holdStatusTone(hold.status)" />
          </div>
        </div>
      </div>

      <!-- Loyalty -->
      <div v-if="secondaryTab === 'loyalty'">
        <div v-if="loyaltyLoading" class="flex items-center justify-center py-12">
          <Loader2 class="h-5 w-5 animate-spin text-slate-300" />
        </div>
        <div v-else-if="!loyalty" class="px-5 py-12 text-center">
          <Star class="mx-auto h-8 w-8 text-slate-200" />
          <p class="mt-2 text-sm text-graphite">Loyalty programme not available on your account.</p>
        </div>
        <div v-else class="p-5 space-y-5">
          <div class="flex items-end justify-between gap-3">
            <div>
              <p class="text-4xl font-extrabold text-ink tabular-nums">{{ loyalty.loyalty_points.toLocaleString() }}</p>
              <p class="mt-0.5 text-xs text-graphite">points available</p>
            </div>
            <span class="rounded-full border border-saffron/30 bg-saffron/10 px-3 py-1 text-xs font-semibold text-saffron">{{ loyalty.tier }}</span>
          </div>

          <div class="flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
            <button class="flex-1 rounded-md py-1.5 text-xs font-semibold transition-colors" :class="loyaltyTab === 'convert' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'" type="button" @click="loyaltyTab = 'convert'">Convert</button>
            <button class="flex-1 rounded-md py-1.5 text-xs font-semibold transition-colors" :class="loyaltyTab === 'redeem' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'" type="button" @click="loyaltyTab = 'redeem'">Redeem</button>
          </div>

          <template v-if="loyaltyTab === 'convert'">
            <p class="text-xs text-graphite">{{ loyalty.conversion_rate }} points = $1.00 wallet credit</p>
            <div class="flex gap-2">
              <input v-model="loyaltyConvertPoints" class="focus-ring h-9 flex-1 rounded-lg border border-slate-200 px-3 text-sm" type="number" min="1" :max="loyalty.loyalty_points" placeholder="Points to convert" />
              <button class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-lg bg-ink px-3 text-xs font-semibold text-white disabled:opacity-60" type="button" :disabled="loyaltyConvertSubmitting || loyalty.loyalty_points === 0" @click="convertLoyaltyPoints">
                <Loader2 v-if="loyaltyConvertSubmitting" class="h-3 w-3 animate-spin" /><CheckCircle2 v-else class="h-3 w-3" /> Convert
              </button>
            </div>
            <p v-if="loyaltyConvertError" class="text-xs text-berry">{{ loyaltyConvertError }}</p>
            <p v-if="loyaltyConvertSuccess" class="text-xs font-semibold text-signal">Converted {{ loyaltyConvertSuccess.converted }} pts → ${{ loyaltyConvertSuccess.amount }} added</p>
          </template>

          <template v-else>
            <p v-if="redemptionError" class="text-xs text-berry">{{ redemptionError }}</p>
            <p v-if="redemptionSuccess" class="text-xs font-semibold text-signal">{{ redemptionSuccess }}</p>
            <div v-if="redemptionLoading" class="flex justify-center py-4"><Loader2 class="h-4 w-4 animate-spin text-slate-400" /></div>
            <div v-else-if="!redemptionItems.length" class="py-4 text-center text-xs text-graphite">No rewards available right now.</div>
            <div v-else class="space-y-2">
              <div v-for="item in redemptionItems" :key="item.id" class="flex items-start gap-3 rounded-xl border border-slate-200 p-3" :class="item.can_redeem?.can_redeem ? 'bg-white' : 'bg-slate-50 opacity-70'">
                <div class="min-w-0 flex-1">
                  <p class="text-xs font-semibold text-ink">{{ item.name }}</p>
                  <p v-if="item.description" class="mt-0.5 text-xs text-graphite">{{ item.description }}</p>
                  <p class="mt-1 text-xs font-semibold text-saffron">{{ item.points_required.toLocaleString() }} pts</p>
                  <p v-if="item.can_redeem && !item.can_redeem.can_redeem" class="mt-0.5 text-xs text-graphite">{{ item.can_redeem.message }}</p>
                </div>
                <button v-if="item.can_redeem?.can_redeem" class="focus-ring mt-0.5 inline-flex shrink-0 items-center gap-1 rounded-lg bg-ink px-2.5 py-1.5 text-xs font-semibold text-white disabled:opacity-60" type="button" :disabled="redeemingItemId === item.id" @click="redeemItem(item.id)">
                  <Loader2 v-if="redeemingItemId === item.id" class="h-3 w-3 animate-spin" /><CheckCircle2 v-else class="h-3 w-3" /> Redeem
                </button>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Referral -->
      <div v-if="secondaryTab === 'referral'">
        <div v-if="referralCodeLoading" class="flex justify-center py-12"><Loader2 class="h-5 w-5 animate-spin text-slate-300" /></div>
        <div v-else-if="!referralCode" class="px-5 py-12 text-center">
          <Gift class="mx-auto h-8 w-8 text-slate-200" />
          <p class="mt-2 text-sm text-graphite">No referral code available on your account.</p>
        </div>
        <div v-else class="p-5 space-y-5">
          <div>
            <p class="text-xs font-semibold uppercase tracking-widest text-graphite">Your referral code</p>
            <div class="mt-2 flex items-center gap-2">
              <code class="flex-1 rounded-xl bg-slate-100 px-4 py-3 text-lg font-bold tracking-widest text-ink">{{ referralCode.code }}</code>
              <button class="focus-ring inline-flex h-11 items-center gap-1.5 rounded-xl border border-slate-200 px-4 text-xs font-semibold text-ink transition-colors hover:bg-slate-50" type="button" @click="copyReferralCode">
                <Copy class="h-3.5 w-3.5" />{{ referralCodeCopied ? "Copied!" : "Copy" }}
              </button>
            </div>
          </div>
          <div v-if="referralCode.usage_stats" class="flex gap-6 text-sm">
            <div><span class="text-2xl font-bold text-ink">{{ referralCode.usage_stats.total_referrals ?? 0 }}</span><p class="mt-0.5 text-xs text-graphite">referred</p></div>
            <div><span class="text-2xl font-bold text-ink">{{ referralCode.usage_stats.successful_referrals ?? 0 }}</span><p class="mt-0.5 text-xs text-graphite">converted</p></div>
          </div>
          <p class="text-sm text-graphite leading-relaxed">Share your code and earn a bonus when friends place their first order.</p>
        </div>
      </div>

    </section>

  </div>
</template>
