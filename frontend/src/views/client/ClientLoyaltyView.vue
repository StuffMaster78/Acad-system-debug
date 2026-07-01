<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { CheckCircle2, ChevronDown, ChevronUp, Clock, Info, Loader2, RefreshCw, Star, TrendingUp, Wallet } from "@lucide/vue";

const showGuide = ref(false);
import { api, apiPath } from "@/api/client";

interface LoyaltySummary {
  loyalty_points: number;
  wallet_balance: string;
  tier: string;
  conversion_rate: string;
}

interface LoyaltyTransaction {
  id: number;
  points: number;
  transaction_type: string;
  reason: string | null;
  timestamp: string;
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
const activeTab = ref<"convert" | "redeem" | "history">("convert");

const convertPoints = ref("");
const convertError = ref("");
const convertSubmitting = ref(false);
const convertSuccess = ref<{ converted: number; amount: string } | null>(null);

const redemptionItems = ref<RedemptionItem[]>([]);
const redemptionLoading = ref(false);
const redeemingId = ref<number | null>(null);
const redeemError = ref("");
const redeemSuccess = ref<string | null>(null);

const history = ref<LoyaltyTransaction[]>([]);
const historyLoading = ref(false);
const historyPage = ref(1);
const historyTotal = ref(0);
const HISTORY_PAGE_SIZE = 20;
const historyTotalPages = computed(() => Math.max(1, Math.ceil(historyTotal.value / HISTORY_PAGE_SIZE)));

const tierColor = computed(() => {
  const t = (loyalty.value?.tier ?? "").toLowerCase();
  if (t.includes("gold") || t.includes("platinum") || t.includes("elite")) return "text-amber-600 bg-amber-50 border-amber-200";
  if (t.includes("silver") || t.includes("pro")) return "text-slate-600 bg-slate-100 border-slate-300";
  if (t.includes("diamond") || t.includes("vip")) return "text-violet-600 bg-violet-50 border-violet-200";
  return "text-emerald-700 bg-emerald-50 border-emerald-200";
});

async function fetchLoyalty() {
  loyaltyLoading.value = true;
  try {
    const { data } = await api.get<LoyaltySummary>(apiPath("/loyalty-management/loyalty/summary/"));
    loyalty.value = data;
  } catch {
    // loyalty may not be enabled
  } finally {
    loyaltyLoading.value = false;
  }
}

async function fetchRedemptionItems() {
  redemptionLoading.value = true;
  try {
    const { data } = await api.get<RedemptionItem[] | { results: RedemptionItem[] }>(
      apiPath("/loyalty-management/redemption-items/"),
    );
    redemptionItems.value = Array.isArray(data) ? data : (data as { results: RedemptionItem[] }).results ?? [];
  } catch {
    // non-critical
  } finally {
    redemptionLoading.value = false;
  }
}

async function fetchHistory() {
  historyLoading.value = true;
  try {
    const { data } = await api.get<LoyaltyTransaction[] | { count: number; results: LoyaltyTransaction[] }>(
      apiPath("/loyalty-management/loyalty/transactions/"),
      { params: { page: historyPage.value, page_size: HISTORY_PAGE_SIZE } },
    );
    if (Array.isArray(data)) {
      history.value = data;
      historyTotal.value = data.length;
    } else {
      history.value = data.results ?? [];
      historyTotal.value = data.count ?? 0;
    }
  } catch {
    // non-critical
  } finally {
    historyLoading.value = false;
  }
}

async function convertLoyaltyPoints() {
  convertError.value = "";
  convertSuccess.value = null;
  const pts = parseInt(convertPoints.value, 10);
  if (!pts || pts <= 0) { convertError.value = "Enter a valid number of points."; return; }
  if (loyalty.value && pts > loyalty.value.loyalty_points) {
    convertError.value = "You don't have that many points."; return;
  }
  convertSubmitting.value = true;
  try {
    const { data } = await api.post<{ converted: number; amount: string }>(
      apiPath("/loyalty-management/loyalty/convert/"),
      { points: pts },
    );
    convertSuccess.value = data;
    convertPoints.value = "";
    await fetchLoyalty();
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string; points?: string[] } } })?.response?.data;
    convertError.value = detail?.detail ?? detail?.points?.[0] ?? "Conversion failed. Try again.";
  } finally {
    convertSubmitting.value = false;
  }
}

async function redeemItem(itemId: number) {
  redeemError.value = "";
  redeemSuccess.value = null;
  redeemingId.value = itemId;
  try {
    await api.post(apiPath("/loyalty-management/redemption-requests/"), { item_id: itemId });
    redeemSuccess.value = "Redemption request submitted — we'll process it shortly.";
    await fetchLoyalty();
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    redeemError.value = detail ?? "Redemption failed. Please try again.";
  } finally {
    redeemingId.value = null;
  }
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

function onTabChange(tab: "convert" | "redeem" | "history") {
  activeTab.value = tab;
  if (tab === "history" && !history.value.length) fetchHistory();
  if (tab === "redeem" && !redemptionItems.value.length) fetchRedemptionItems();
}

onMounted(() => {
  fetchLoyalty();
  fetchRedemptionItems();
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Client</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Loyalty & Rewards</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">Your points balance, tier, and available rewards.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold"
          type="button"
          @click="showGuide = !showGuide"
        >
          <Info class="h-4 w-4" />
          How points work
          <ChevronUp v-if="showGuide" class="h-3.5 w-3.5" />
          <ChevronDown v-else class="h-3.5 w-3.5" />
        </button>
        <button
          class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
          type="button"
          :disabled="loyaltyLoading"
          @click="fetchLoyalty"
        >
          <Loader2 v-if="loyaltyLoading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
          Refresh
        </button>
      </div>
    </section>

    <!-- In-portal guide -->
    <div v-if="showGuide" class="rounded-xl border border-amber-100 bg-amber-50 p-5 space-y-4 text-sm">
      <h2 class="font-semibold text-amber-900 flex items-center gap-2"><Info class="size-4" /> How Loyalty Points Work</h2>
      <div class="grid gap-4 sm:grid-cols-2">
        <div class="space-y-1">
          <p class="font-semibold text-amber-800">⭐ Earning Points</p>
          <p class="text-amber-700">You earn points every time you place a paid order. The amount depends on your current loyalty tier — higher tiers earn more points per dollar spent.</p>
        </div>
        <div class="space-y-1">
          <p class="font-semibold text-amber-800">🏷 Your Tier</p>
          <p class="text-amber-700">Tiers unlock automatically as your cumulative points grow. Higher tiers get bonus multipliers, exclusive rewards, and priority processing on orders.</p>
        </div>
        <div class="space-y-1">
          <p class="font-semibold text-amber-800">💱 Converting Points</p>
          <p class="text-amber-700">Convert your points into wallet credit (e.g., 100 pts = $1.00). Wallet credit can be used on any future order at checkout. Go to the "Convert" tab to redeem.</p>
        </div>
        <div class="space-y-1">
          <p class="font-semibold text-amber-800">🎁 Redeeming Rewards</p>
          <p class="text-amber-700">The "Redeem" tab lists special reward items (gift vouchers, priority slots, etc.). Submit a redemption request — our team will process it within 24 hours.</p>
        </div>
        <div class="space-y-1">
          <p class="font-semibold text-amber-800">🏁 Milestones</p>
          <p class="text-amber-700">Complete milestones (e.g., first order, 10th order) to earn bonus points automatically. Milestone rewards appear in your transaction history.</p>
        </div>
        <div class="space-y-1">
          <p class="font-semibold text-amber-800">📋 Transaction History</p>
          <p class="text-amber-700">Every point earned, spent, or adjusted is logged. Check the "History" tab for a full breakdown of your points activity.</p>
        </div>
      </div>
    </div>

    <div v-if="loyaltyLoading && !loyalty" class="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-graphite">
      Loading loyalty data…
    </div>

    <div v-else-if="!loyalty" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center">
      <Star class="mx-auto h-8 w-8 text-slate-300" />
      <p class="mt-3 text-sm font-medium text-ink">Loyalty programme not active</p>
      <p class="mt-1 text-sm text-graphite">Place more orders to unlock loyalty rewards.</p>
    </div>

    <template v-else>
      <!-- Hero summary card -->
      <section class="rounded-xl border border-slate-200 bg-white p-6">
        <div class="flex flex-col gap-5 sm:flex-row sm:items-center sm:gap-8">
          <!-- Points -->
          <div class="flex items-center gap-4">
            <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-saffron/10">
              <Star class="h-7 w-7 text-saffron" />
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Points balance</p>
              <p class="mt-0.5 text-3xl font-bold text-ink">{{ loyalty.loyalty_points.toLocaleString() }}</p>
            </div>
          </div>

          <div class="hidden h-12 w-px bg-slate-200 sm:block" />

          <!-- Tier badge -->
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Current tier</p>
            <span
              class="mt-1.5 inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-semibold"
              :class="tierColor"
            >
              <Star class="h-3.5 w-3.5" />
              {{ loyalty.tier }}
            </span>
          </div>

          <div class="hidden h-12 w-px bg-slate-200 sm:block" />

          <!-- Conversion rate -->
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Conversion rate</p>
            <div class="mt-1 flex items-center gap-1.5">
              <Wallet class="h-4 w-4 text-signal" />
              <span class="text-sm font-semibold text-ink">{{ loyalty.conversion_rate }} pts = $1.00</span>
            </div>
            <p class="mt-0.5 text-xs text-graphite">wallet credit</p>
          </div>
        </div>
      </section>

      <!-- Tab panel -->
      <section class="rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center gap-1 border-b border-slate-200 px-5 py-3">
          <button
            class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
            :class="activeTab === 'convert' ? 'bg-slate-100 text-ink' : 'text-graphite hover:text-ink'"
            type="button"
            @click="onTabChange('convert')"
          >
            Convert to credits
          </button>
          <button
            class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
            :class="activeTab === 'redeem' ? 'bg-slate-100 text-ink' : 'text-graphite hover:text-ink'"
            type="button"
            @click="onTabChange('redeem')"
          >
            Redeem rewards
          </button>
          <button
            class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
            :class="activeTab === 'history' ? 'bg-slate-100 text-ink' : 'text-graphite hover:text-ink'"
            type="button"
            @click="onTabChange('history')"
          >
            Points history
          </button>
        </div>

        <!-- Convert tab -->
        <div v-if="activeTab === 'convert'" class="space-y-4 p-6">
          <p class="text-sm text-graphite">
            Convert loyalty points directly into wallet credits. {{ loyalty.conversion_rate }} points = $1.00.
          </p>
          <div class="flex max-w-sm gap-2">
            <input
              v-model="convertPoints"
              class="focus-ring h-10 flex-1 rounded-md border border-slate-200 px-3 text-sm"
              type="number"
              min="1"
              :max="loyalty.loyalty_points"
              placeholder="Points to convert"
            />
            <button
              class="focus-ring inline-flex h-10 items-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="convertSubmitting || loyalty.loyalty_points === 0"
              @click="convertLoyaltyPoints"
            >
              <Loader2 v-if="convertSubmitting" class="h-4 w-4 animate-spin" />
              <CheckCircle2 v-else class="h-4 w-4" />
              Convert
            </button>
          </div>
          <p v-if="convertError" class="text-sm text-berry">{{ convertError }}</p>
          <p v-if="convertSuccess" class="text-sm font-semibold text-signal">
            Converted {{ convertSuccess.converted }} pts &#8594; ${{ convertSuccess.amount }} added to wallet
          </p>
        </div>

        <!-- Redeem tab -->
        <div v-else-if="activeTab === 'redeem'" class="space-y-4 p-6">
          <p v-if="redeemError" class="text-sm text-berry">{{ redeemError }}</p>
          <p v-if="redeemSuccess" class="text-sm font-semibold text-signal">{{ redeemSuccess }}</p>

          <div v-if="redemptionLoading" class="flex items-center justify-center py-8">
            <Loader2 class="h-6 w-6 animate-spin text-slate-400" />
          </div>
          <div v-else-if="!redemptionItems.length" class="rounded-lg border border-slate-200 bg-slate-50 py-10 text-center">
            <Star class="mx-auto h-7 w-7 text-slate-300" />
            <p class="mt-3 text-sm text-graphite">No reward items available right now.</p>
          </div>
          <div v-else class="grid gap-4 sm:grid-cols-2">
            <div
              v-for="item in redemptionItems"
              :key="item.id"
              class="rounded-lg border p-4 transition-colors"
              :class="item.can_redeem?.can_redeem ? 'border-slate-200 bg-white' : 'border-slate-100 bg-slate-50 opacity-70'"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="font-semibold text-ink">{{ item.name }}</p>
                  <p v-if="item.description" class="mt-1 text-sm text-graphite">{{ item.description }}</p>
                </div>
                <span class="shrink-0 rounded-full bg-saffron/10 px-2.5 py-1 text-xs font-semibold text-saffron">
                  {{ item.points_required.toLocaleString() }} pts
                </span>
              </div>
              <div class="mt-3 flex items-center justify-between gap-3">
                <p v-if="item.can_redeem && !item.can_redeem.can_redeem" class="text-xs text-graphite">
                  {{ item.can_redeem.message }}
                </p>
                <span v-else class="text-xs text-graphite">{{ item.redemption_type.replace(/_/g, " ") }}</span>
                <button
                  v-if="item.can_redeem?.can_redeem"
                  class="focus-ring inline-flex shrink-0 items-center gap-1.5 rounded-md bg-ink px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
                  type="button"
                  :disabled="redeemingId === item.id"
                  @click="redeemItem(item.id)"
                >
                  <Loader2 v-if="redeemingId === item.id" class="h-3 w-3 animate-spin" />
                  <CheckCircle2 v-else class="h-3 w-3" />
                  Redeem
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- History tab -->
        <div v-else class="p-6">
          <div v-if="historyLoading && !history.length" class="flex items-center justify-center py-8">
            <Loader2 class="h-6 w-6 animate-spin text-slate-400" />
          </div>
          <div v-else-if="!history.length" class="rounded-lg border border-slate-100 bg-slate-50 py-10 text-center">
            <TrendingUp class="mx-auto h-7 w-7 text-slate-300" />
            <p class="mt-3 text-sm text-graphite">No point transactions yet.</p>
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
                <tr>
                  <th class="px-4 py-3 text-left">Type</th>
                  <th class="px-4 py-3 text-left">Reason</th>
                  <th class="px-4 py-3 text-right">Points</th>
                  <th class="px-4 py-3 text-right">Date</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="tx in history" :key="tx.id" class="hover:bg-slate-50">
                  <td class="px-4 py-3">
                    <span
                      class="rounded-full px-2 py-0.5 text-xs font-medium"
                      :class="tx.points > 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'"
                    >
                      {{ tx.transaction_type.replace(/_/g, " ") }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-graphite">{{ tx.reason || "—" }}</td>
                  <td class="px-4 py-3 text-right font-semibold" :class="tx.points > 0 ? 'text-emerald-700' : 'text-rose-600'">
                    {{ tx.points > 0 ? "+" : "" }}{{ tx.points.toLocaleString() }}
                  </td>
                  <td class="px-4 py-3 text-right text-graphite">
                    <span class="flex items-center justify-end gap-1">
                      <Clock class="h-3 w-3 shrink-0" />
                      {{ fmtDate(tx.timestamp) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="historyTotalPages > 1" class="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
            <p class="text-xs text-graphite">Page {{ historyPage }} of {{ historyTotalPages }}</p>
            <div class="flex gap-2">
              <button
                class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40"
                :disabled="historyPage <= 1"
                @click="historyPage--; fetchHistory()"
              >&#8592;</button>
              <button
                class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white disabled:opacity-40"
                :disabled="historyPage >= historyTotalPages"
                @click="historyPage++; fetchHistory()"
              >&#8594;</button>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>
