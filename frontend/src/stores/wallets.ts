import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { walletsApi } from "@/api/wallets";
import { useAuthStore } from "@/stores/auth";
import type {
  PayoutRequest,
  PayoutRequestPayload,
  WalletBalance,
  WalletEntry,
  WalletHold,
} from "@/types/wallet";

type ListResponse<T> = T[] | { results: T[] };

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function previewWallet(): WalletBalance {
  return {
    id: 1,
    wallet_type: "preview",
    currency: "USD",
    status: "active",
    available_balance: "240.00",
    pending_balance: "48.00",
    total_credited: "1280.00",
    total_debited: "1040.00",
    last_activity_at: new Date().toISOString(),
  };
}

export const useWalletStore = defineStore("wallets", () => {
  const wallet = ref<WalletBalance | null>(null);
  const entries = ref<WalletEntry[]>([]);
  const holds = ref<WalletHold[]>([]);
  const payoutRequests = ref<PayoutRequest[]>([]);
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");

  const currency = computed(() => wallet.value?.currency ?? "USD");
  const availableBalance = computed(() => Number(wallet.value?.available_balance ?? 0));
  const pendingBalance = computed(() => Number(wallet.value?.pending_balance ?? 0));

  async function fetchWallet() {
    const auth = useAuthStore();
    if (!auth.isAuthenticated) return null;
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        wallet.value = previewWallet();
        return wallet.value;
      }
      const { data } = await walletsApi.me();
      wallet.value = data;
      return data;
    } catch (caught) {
      error.value = "Unable to load wallet.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchEntries(params?: Record<string, unknown>) {
    const auth = useAuthStore();
    if (auth.isPreviewSession) {
      entries.value = [
        {
          id: 1,
          entry_type: "preview_credit",
          direction: "credit",
          status: "posted",
          amount: "120.00",
          balance_after: "240.00",
          description: "Preview wallet credit",
          created_at: new Date().toISOString(),
        },
      ];
      return entries.value;
    }
    const { data } = await walletsApi.entries(params);
    entries.value = normalizeList(data);
    return entries.value;
  }

  async function fetchHolds(params?: Record<string, unknown>) {
    const auth = useAuthStore();
    if (auth.isPreviewSession) {
      holds.value = [];
      return holds.value;
    }
    const { data } = await walletsApi.holds(params);
    holds.value = normalizeList(data);
    return holds.value;
  }

  async function fetchPayoutRequests(params?: Record<string, unknown>) {
    const auth = useAuthStore();
    if (auth.isPreviewSession) {
      payoutRequests.value = [];
      return payoutRequests.value;
    }
    const { data } = await walletsApi.payoutRequests(params);
    payoutRequests.value = normalizeList(data);
    return payoutRequests.value;
  }

  async function hydrate() {
    await fetchWallet();
    await Promise.allSettled([
      fetchEntries({ page_size: 10 }),
      fetchHolds({ page_size: 10 }),
      fetchPayoutRequests({ page_size: 10 }),
    ]);
  }

  async function requestPayout(payload: PayoutRequestPayload) {
    const auth = useAuthStore();
    isMutating.value = true;
    try {
      if (auth.isPreviewSession) {
        payoutRequests.value = [
          {
            id: Date.now(),
            amount: payload.amount,
            reason: payload.reason,
            status: "pending",
            workflow_status: "pending_review",
            created_at: new Date().toISOString(),
          },
          ...payoutRequests.value,
        ];
        return;
      }
      const { data } = await walletsApi.requestPayout(payload);
      payoutRequests.value = [data, ...payoutRequests.value];
      await fetchWallet();
    } finally {
      isMutating.value = false;
    }
  }

  return {
    wallet,
    entries,
    holds,
    payoutRequests,
    isLoading,
    isMutating,
    error,
    currency,
    availableBalance,
    pendingBalance,
    fetchWallet,
    fetchEntries,
    fetchHolds,
    fetchPayoutRequests,
    hydrate,
    requestPayout,
  };
});
