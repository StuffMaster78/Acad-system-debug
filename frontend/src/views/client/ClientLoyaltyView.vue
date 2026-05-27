<script setup lang="ts">
import { onMounted, ref } from "vue";
import { CheckCircle2, Loader2, RefreshCw, Star } from "@lucide/vue";
import { api, apiPath } from "@/api/client";

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
const activeTab = ref<"convert" | "redeem">("convert");

const convertPoints = ref("");
const convertError = ref("");
const convertSubmitting = ref(false);
const convertSuccess = ref<{ converted: number; amount: string } | null>(null);

const redemptionItems = ref<RedemptionItem[]>([]);
const redemptionLoading = ref(false);
const redeemingId = ref<number | null>(null);
const redeemError = ref("");
const redeemSuccess = ref<string | null>(null);

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

async function convertLoyaltyPoints() {
  convertError.value = "";
  convertSuccess.value = null;
  const pts = parseInt(convertPoints.value, 10);
  if (!pts || pts <= 0) {
    convertError.value = "Enter a valid number of points.";
    return;
  }
  if (loyalty.value && pts > loyalty.value.loyalty_points) {
    convertError.value = "You don't have that many points.";
    return;
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

onMounted(() => {
  fetchLoyalty();
  fetchRedemptionItems();
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Client</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Loyalty & Rewards</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Your loyalty points balance, tier, and available rewards.
        </p>
      </div>
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
    </section>

    <div v-if="loyaltyLoading && !loyalty" class="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-graphite shadow-panel">
      Loading loyalty data…
    </div>

    <div v-else-if="!loyalty" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center shadow-panel">
      <Star class="mx-auto h-8 w-8 text-slate-300" />
      <p class="mt-3 text-sm font-medium text-ink">Loyalty programme not active</p>
      <p class="mt-1 text-sm text-graphite">Place more orders to unlock loyalty rewards.</p>
    </div>

    <template v-else>
      <!-- Summary tiles -->
      <section class="grid gap-4 sm:grid-cols-3">
        <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
          <div class="flex items-center gap-2">
            <Star class="h-4 w-4 text-saffron" />
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Points balance</p>
          </div>
          <p class="mt-3 text-3xl font-semibold text-ink">{{ loyalty.loyalty_points.toLocaleString() }}</p>
          <p class="mt-1 text-xs text-graphite">available to use</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
          <div class="flex items-center gap-2">
            <Star class="h-4 w-4 text-saffron" />
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Tier</p>
          </div>
          <p class="mt-3 text-2xl font-semibold text-ink">{{ loyalty.tier }}</p>
          <p class="mt-1 text-xs text-graphite">current loyalty tier</p>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
          <div class="flex items-center gap-2">
            <Star class="h-4 w-4 text-saffron" />
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Conversion rate</p>
          </div>
          <p class="mt-3 text-2xl font-semibold text-ink">{{ loyalty.conversion_rate }} pts</p>
          <p class="mt-1 text-xs text-graphite">per $1.00 wallet credit</p>
        </div>
      </section>

      <!-- Tab panel -->
      <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
        <div class="flex items-center gap-1 border-b border-slate-200 px-5 py-3">
          <button
            class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
            :class="activeTab === 'convert' ? 'bg-slate-100 text-ink' : 'text-graphite hover:text-ink'"
            type="button"
            @click="activeTab = 'convert'"
          >
            Convert to credits
          </button>
          <button
            class="rounded-md px-4 py-2 text-sm font-semibold transition-colors"
            :class="activeTab === 'redeem' ? 'bg-slate-100 text-ink' : 'text-graphite hover:text-ink'"
            type="button"
            @click="activeTab = 'redeem'"
          >
            Redeem rewards
          </button>
        </div>

        <!-- Convert tab -->
        <div v-if="activeTab === 'convert'" class="p-6 space-y-4">
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
            Converted {{ convertSuccess.converted }} pts → ${{ convertSuccess.amount }} added to wallet
          </p>
        </div>

        <!-- Redeem tab -->
        <div v-else class="p-6 space-y-4">
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
              :class="item.can_redeem?.can_redeem
                ? 'border-slate-200 bg-white'
                : 'border-slate-100 bg-slate-50 opacity-70'"
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
      </section>
    </template>
  </div>
</template>
