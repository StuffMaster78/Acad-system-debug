<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
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

onMounted(() => {
  wallets.hydrate().catch(() => undefined);
  fetchReferralCode();
  fetchLoyalty();
  fetchRedemptionItems();
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Client</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Wallet</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Your platform balance, transaction history, and active holds.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="wallets.isLoading"
        @click="wallets.hydrate().catch(() => undefined)"
      >
        <RefreshCw class="h-4 w-4" :class="wallets.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <div v-if="wallets.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ wallets.error }}
    </div>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2">
          <Banknote class="h-4 w-4 text-signal" />
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Available</p>
        </div>
        <p class="mt-3 text-2xl font-semibold text-ink">
          {{ money(wallets.wallet?.available_balance) }}
        </p>
        <p class="mt-1 text-xs text-graphite">Ready to use for orders</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2">
          <Clock3 class="h-4 w-4 text-saffron" />
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Pending</p>
        </div>
        <p class="mt-3 text-2xl font-semibold text-ink">
          {{ money(wallets.wallet?.pending_balance) }}
        </p>
        <p class="mt-1 text-xs text-graphite">Processing — not yet available</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2">
          <ArrowDownLeft class="h-4 w-4 text-emerald-500" />
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Total credited</p>
        </div>
        <p class="mt-3 text-2xl font-semibold text-ink">
          {{ money(wallets.wallet?.total_credited) }}
        </p>
        <p class="mt-1 text-xs text-graphite">All-time funds added</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2">
          <ArrowUpRight class="h-4 w-4 text-rose-400" />
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Total spent</p>
        </div>
        <p class="mt-3 text-2xl font-semibold text-ink">
          {{ money(wallets.wallet?.total_debited) }}
        </p>
        <p class="mt-1 text-xs text-graphite">All-time funds used</p>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-[1fr_360px]">
      <section class="rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
          <TrendingUp class="h-5 w-5 text-signal" />
          <div>
            <h2 class="text-base font-semibold text-ink">Transaction ledger</h2>
            <p class="text-sm text-graphite">Credits and debits on your wallet account.</p>
          </div>
        </div>

        <div v-if="wallets.isLoading && !wallets.entries.length" class="space-y-px">
          <div
            v-for="n in 5"
            :key="n"
            class="animate-pulse border-b border-slate-100 px-5 py-4"
            aria-hidden="true"
          >
            <div class="flex items-center justify-between gap-4">
              <div class="flex-1 space-y-2">
                <div class="h-4 w-1/2 rounded bg-slate-200" />
                <div class="h-3 w-1/3 rounded bg-slate-100" />
              </div>
              <div class="h-4 w-20 rounded bg-slate-100" />
            </div>
          </div>
        </div>

        <div v-else-if="!wallets.entries.length" class="p-8">
          <EmptyState
            :icon="TrendingUp"
            title="No transactions yet"
            message="Wallet entries will appear here once funds are added or orders are placed."
          />
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="entry in wallets.entries"
            :key="entry.id"
            class="grid gap-4 px-5 py-4 lg:grid-cols-[minmax(0,1fr)_auto_auto]"
          >
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <component
                  :is="entry.direction === 'credit' ? ArrowDownLeft : ArrowUpRight"
                  class="h-3.5 w-3.5 shrink-0"
                  :class="entry.direction === 'credit' ? 'text-emerald-500' : 'text-rose-400'"
                />
                <p class="truncate font-semibold text-ink">
                  {{ entry.description || entry.entry_type || (entry.direction === "credit" ? "Credit" : "Debit") }}
                </p>
                <StatusPill :label="entry.status ?? 'posted'" :tone="entryTone(entry.direction)" />
              </div>
              <p class="mt-1 text-xs text-graphite">
                {{ entry.reference_type ? `${entry.reference_type} · ` : "" }}{{ dateLabel(entry.created_at) }}
              </p>
            </div>
            <div class="text-right">
              <p
                class="font-semibold"
                :class="entry.direction === 'credit' ? 'text-emerald-700' : 'text-rose-700'"
              >
                {{ entry.direction === "credit" ? "+" : "−" }}{{ money(entry.amount) }}
              </p>
              <p v-if="entry.balance_after != null" class="mt-0.5 text-xs text-graphite">
                Balance: {{ money(entry.balance_after) }}
              </p>
            </div>
          </div>
        </div>
      </section>

      <aside class="space-y-4">
        <section class="rounded-lg border border-slate-200 bg-white">
          <div class="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
            <Lock class="h-4 w-4 text-signal" />
            <h2 class="text-base font-semibold text-ink">Active holds</h2>
          </div>

          <div v-if="!wallets.holds.length" class="px-5 py-8">
            <EmptyState
              :icon="Lock"
              title="No holds"
              message="Funds reserved for pending orders appear here."
            />
          </div>

          <div v-else class="divide-y divide-slate-100">
            <div
              v-for="hold in wallets.holds"
              :key="hold.id"
              class="px-5 py-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-ink">{{ money(hold.amount) }}</p>
                  <p v-if="hold.reason" class="mt-0.5 text-xs text-graphite">{{ hold.reason }}</p>
                  <p class="mt-0.5 text-xs text-graphite">{{ dateLabel(hold.created_at) }}</p>
                  <p v-if="hold.expires_at" class="mt-0.5 text-xs text-graphite">
                    Expires {{ dateLabel(hold.expires_at) }}
                  </p>
                </div>
                <StatusPill :label="hold.status" :tone="holdStatusTone(hold.status)" />
              </div>
            </div>
          </div>
        </section>

        <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <div class="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
            <CreditCard class="h-4 w-4 text-signal" />
            <h2 class="text-base font-semibold text-ink">Top up wallet</h2>
          </div>

          <!-- Preview success -->
          <div v-if="previewSuccess" class="space-y-4 px-5 py-6">
            <div class="flex items-center gap-3 rounded-md border border-emerald-200 bg-emerald-50 p-4">
              <CheckCircle2 class="h-5 w-5 shrink-0 text-signal" />
              <p class="text-sm font-semibold text-ink">Wallet topped up (preview mode)</p>
            </div>
            <button
              class="focus-ring w-full rounded-md border border-slate-200 px-4 py-2.5 text-sm font-semibold text-graphite hover:bg-slate-50"
              type="button"
              @click="previewSuccess = false"
            >
              Top up again
            </button>
          </div>

          <!-- Checkout form -->
          <div v-else-if="!previewSuccess" class="space-y-4 px-5 py-5">
            <!-- Amount presets -->
            <div>
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-graphite">Amount</p>
              <div class="grid grid-cols-5 gap-1.5">
                <button
                  v-for="preset in PRESETS"
                  :key="preset"
                  class="focus-ring rounded-md border py-2 text-sm font-semibold transition-colors"
                  :class="topup.preset === preset
                    ? 'border-ink bg-ink text-white'
                    : 'border-slate-200 bg-white text-ink hover:border-slate-400'"
                  type="button"
                  @click="selectPreset(preset)"
                >
                  {{ preset }}
                </button>
              </div>
              <div class="relative mt-2">
                <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm font-semibold text-graphite">
                  {{ wallets.currency }}
                </span>
                <input
                  v-model="topup.custom"
                  class="focus-ring h-10 w-full rounded-md border border-slate-200 pl-14 pr-3 text-sm"
                  :class="topup.preset === null && topup.custom ? 'border-ink ring-1 ring-ink' : ''"
                  type="number"
                  min="1"
                  step="0.01"
                  placeholder="Custom amount"
                  @input="onCustomInput"
                />
              </div>
            </div>

            <!-- Payment method -->
            <div>
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-graphite">Pay with</p>
              <div class="space-y-2">
                <label
                  class="flex cursor-pointer items-center gap-3 rounded-md border p-3 transition-colors"
                  :class="topup.provider === 'stripe' ? 'border-ink bg-slate-50 ring-1 ring-ink' : 'border-slate-200 hover:border-slate-400'"
                >
                  <input v-model="topup.provider" class="sr-only" type="radio" value="stripe" />
                  <CreditCard class="h-4 w-4 shrink-0 text-graphite" />
                  <div class="min-w-0 flex-1">
                    <p class="text-sm font-semibold text-ink">Card</p>
                    <p class="text-xs text-graphite">Visa, Mastercard — you'll be redirected to checkout</p>
                  </div>
                  <CheckCircle2 v-if="topup.provider === 'stripe'" class="h-4 w-4 shrink-0 text-ink" />
                </label>

                <label
                  v-if="isDev"
                  class="flex cursor-pointer items-center gap-3 rounded-md border p-3 transition-colors"
                  :class="topup.provider === 'mock' ? 'border-ink bg-slate-50 ring-1 ring-ink' : 'border-slate-200 hover:border-slate-400'"
                >
                  <input v-model="topup.provider" class="sr-only" type="radio" value="mock" />
                  <Smartphone class="h-4 w-4 shrink-0 text-graphite" />
                  <div class="min-w-0 flex-1">
                    <p class="text-sm font-semibold text-ink">Mock <span class="text-xs font-normal text-graphite">(dev only)</span></p>
                    <p class="text-xs text-graphite">Simulates checkout without a real payment</p>
                  </div>
                  <CheckCircle2 v-if="topup.provider === 'mock'" class="h-4 w-4 shrink-0 text-ink" />
                </label>
              </div>
            </div>

            <p v-if="topupError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
              {{ topupError }}
            </p>

            <button
              class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="wallets.isMutating"
              @click="checkout"
            >
              <Loader2 v-if="wallets.isMutating" class="h-4 w-4 animate-spin" />
              <template v-else>
                {{ topup.provider === "mock" ? "Simulate top-up" : "Proceed to checkout" }}
                <span v-if="topupAmount()">— {{ wallets.currency }} {{ topupAmount() }}</span>
              </template>
            </button>
          </div>
        </section>

        <!-- Loyalty points -->
        <section v-if="loyalty || loyaltyLoading" class="rounded-lg border border-slate-200 bg-white">
          <div class="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
            <Star class="h-4 w-4 text-saffron" />
            <h2 class="text-base font-semibold text-ink">Loyalty points</h2>
          </div>

          <div v-if="loyaltyLoading" class="flex items-center justify-center px-5 py-6">
            <Loader2 class="h-5 w-5 animate-spin text-slate-400" />
          </div>

          <div v-else-if="loyalty" class="space-y-4 px-5 py-5">
            <div class="flex items-end justify-between gap-3">
              <div>
                <p class="text-3xl font-semibold text-ink">{{ loyalty.loyalty_points.toLocaleString() }}</p>
                <p class="mt-0.5 text-xs text-graphite">points available</p>
              </div>
              <span class="inline-block rounded-full border border-saffron/30 bg-saffron/10 px-3 py-1 text-xs font-semibold text-saffron">
                {{ loyalty.tier }}
              </span>
            </div>

            <!-- Tab switcher -->
            <div class="flex gap-1 rounded-md border border-slate-200 bg-slate-50 p-1">
              <button
                class="flex-1 rounded py-1.5 text-xs font-semibold transition-colors"
                :class="loyaltyTab === 'convert' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
                type="button"
                @click="loyaltyTab = 'convert'"
              >
                Convert
              </button>
              <button
                class="flex-1 rounded py-1.5 text-xs font-semibold transition-colors"
                :class="loyaltyTab === 'redeem' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
                type="button"
                @click="loyaltyTab = 'redeem'"
              >
                Redeem
              </button>
            </div>

            <!-- Convert tab -->
            <template v-if="loyaltyTab === 'convert'">
              <p class="text-xs text-graphite">{{ loyalty.conversion_rate }} points = $1.00 wallet credit</p>
              <div class="space-y-2">
                <div class="flex gap-2">
                  <input
                    id="loyalty-pts"
                    v-model="loyaltyConvertPoints"
                    class="focus-ring h-9 flex-1 rounded-md border border-slate-200 px-3 text-sm"
                    type="number"
                    min="1"
                    :max="loyalty.loyalty_points"
                    placeholder="Points to convert"
                  />
                  <button
                    class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-md bg-ink px-3 text-xs font-semibold text-white disabled:opacity-60"
                    type="button"
                    :disabled="loyaltyConvertSubmitting || loyalty.loyalty_points === 0"
                    @click="convertLoyaltyPoints"
                  >
                    <Loader2 v-if="loyaltyConvertSubmitting" class="h-3 w-3 animate-spin" />
                    <CheckCircle2 v-else class="h-3 w-3" />
                    Convert
                  </button>
                </div>
                <p v-if="loyaltyConvertError" class="text-xs text-berry">{{ loyaltyConvertError }}</p>
                <p v-if="loyaltyConvertSuccess" class="text-xs font-semibold text-signal">
                  Converted {{ loyaltyConvertSuccess.converted }} pts → ${{ loyaltyConvertSuccess.amount }} added
                </p>
              </div>
            </template>

            <!-- Redeem tab -->
            <template v-else>
              <p v-if="redemptionError" class="text-xs text-berry">{{ redemptionError }}</p>
              <p v-if="redemptionSuccess" class="text-xs font-semibold text-signal">{{ redemptionSuccess }}</p>

              <div v-if="redemptionLoading" class="flex items-center justify-center py-4">
                <Loader2 class="h-4 w-4 animate-spin text-slate-400" />
              </div>
              <div v-else-if="!redemptionItems.length" class="py-4 text-center text-xs text-graphite">
                No rewards available right now.
              </div>
              <div v-else class="space-y-2">
                <div
                  v-for="item in redemptionItems"
                  :key="item.id"
                  class="flex items-start gap-3 rounded-md border border-slate-200 p-3"
                  :class="item.can_redeem?.can_redeem ? 'bg-white' : 'bg-slate-50 opacity-70'"
                >
                  <div class="min-w-0 flex-1">
                    <p class="text-xs font-semibold text-ink">{{ item.name }}</p>
                    <p v-if="item.description" class="mt-0.5 text-xs text-graphite">{{ item.description }}</p>
                    <p class="mt-1 text-xs font-semibold text-saffron">{{ item.points_required.toLocaleString() }} pts</p>
                    <p v-if="item.can_redeem && !item.can_redeem.can_redeem" class="mt-0.5 text-xs text-graphite">
                      {{ item.can_redeem.message }}
                    </p>
                  </div>
                  <button
                    v-if="item.can_redeem?.can_redeem"
                    class="focus-ring mt-0.5 inline-flex shrink-0 items-center gap-1 rounded-md bg-ink px-2.5 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
                    type="button"
                    :disabled="redeemingItemId === item.id"
                    @click="redeemItem(item.id)"
                  >
                    <Loader2 v-if="redeemingItemId === item.id" class="h-3 w-3 animate-spin" />
                    <CheckCircle2 v-else class="h-3 w-3" />
                    Redeem
                  </button>
                </div>
              </div>
            </template>
          </div>
        </section>

        <!-- Refer a friend -->
        <section v-if="referralCode || referralCodeLoading" class="rounded-lg border border-slate-200 bg-white">
          <div class="flex items-center gap-3 border-b border-slate-200 px-5 py-4">
            <Gift class="h-4 w-4 text-amber-500" />
            <h2 class="text-base font-semibold text-ink">Refer a friend</h2>
          </div>

          <div v-if="referralCodeLoading" class="flex items-center justify-center px-5 py-6">
            <Loader2 class="h-5 w-5 animate-spin text-slate-400" />
          </div>

          <div v-else-if="referralCode" class="px-5 py-5 space-y-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Your referral code</p>
              <div class="mt-2 flex items-center gap-2">
                <code class="flex-1 rounded-md bg-slate-100 px-3 py-2 text-base font-bold tracking-widest text-ink">
                  {{ referralCode.code }}
                </code>
                <button
                  class="focus-ring inline-flex h-9 items-center gap-1.5 rounded-md border border-slate-200 px-3 text-xs font-semibold text-ink transition-colors hover:bg-slate-50"
                  type="button"
                  @click="copyReferralCode"
                >
                  <Copy class="h-3.5 w-3.5" />
                  {{ referralCodeCopied ? "Copied!" : "Copy" }}
                </button>
              </div>
            </div>

            <div v-if="referralCode.usage_stats" class="flex gap-4 text-sm">
              <div>
                <span class="font-semibold text-ink">{{ referralCode.usage_stats.total_referrals ?? 0 }}</span>
                <span class="ml-1 text-graphite">referred</span>
              </div>
              <div>
                <span class="font-semibold text-ink">{{ referralCode.usage_stats.successful_referrals ?? 0 }}</span>
                <span class="ml-1 text-graphite">converted</span>
              </div>
            </div>

            <p class="text-xs text-graphite leading-5">
              Share your code and earn a bonus when friends place their first order.
            </p>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>
