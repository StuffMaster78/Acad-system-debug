import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { adminWalletsApi } from "@/api/adminWallets";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import { usePortalContextStore } from "@/stores/portalContext";
import type {
  AdminWalletAdjustmentPayload,
  AdminEnsureWalletPayload,
  AdminWalletEntryRecord,
  AdminWalletHoldPayload,
  AdminWalletHoldRecord,
  AdminWalletMetric,
  AdminWalletRecord,
} from "@/types/adminWallets";

type ListResponse<T> = T[] | { results: T[] };
type WalletFilter = "all" | "client" | "writer" | "system" | "attention";

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function numeric(value: string | number | undefined | null) {
  if (value === undefined || value === null || value === "") return 0;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function money(value: string | number | undefined | null, currency = "USD") {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric(value));
}

function needsAttention(wallet: AdminWalletRecord) {
  const status = `${wallet.status ?? ""}`.toLowerCase();
  return !wallet.is_active || status.includes("suspend") || status.includes("lock") || numeric(wallet.pending_balance) > 0;
}

function previewWallets(): AdminWalletRecord[] {
  const now = Date.now();
  return [
    {
      id: 31,
      website_id: 1,
      owner_user_id: 101,
      wallet_type: "client",
      currency: "USD",
      status: "active",
      is_active: true,
      available_balance: "148.00",
      pending_balance: "0.00",
      total_credited: "3100.00",
      total_debited: "2952.00",
      last_activity_at: new Date(now - 1000 * 60 * 22).toISOString(),
    },
    {
      id: 42,
      website_id: 1,
      owner_user_id: 8,
      wallet_type: "writer",
      currency: "USD",
      status: "active",
      is_active: true,
      available_balance: "420.00",
      pending_balance: "186.00",
      total_credited: "5240.00",
      total_debited: "4634.00",
      last_activity_at: new Date(now - 1000 * 60 * 65).toISOString(),
    },
    {
      id: 43,
      website_id: 2,
      owner_user_id: 9,
      wallet_type: "writer",
      currency: "USD",
      status: "suspended",
      is_active: false,
      available_balance: "186.00",
      pending_balance: "0.00",
      total_credited: "1980.00",
      total_debited: "1794.00",
      last_activity_at: new Date(now - 1000 * 60 * 60 * 4).toISOString(),
    },
  ];
}

function previewEntries(walletId: number): AdminWalletEntryRecord[] {
  const now = Date.now();
  return [
    {
      id: 901,
      wallet_id: walletId,
      website_id: 1,
      entry_type: "client_payment",
      direction: "credit",
      status: "completed",
      amount: "240.00",
      balance_before: "88.00",
      balance_after: "328.00",
      reference: "ORD-1042",
      reference_type: "order_payment",
      description: "Client payment for policy brief",
      created_at: new Date(now - 1000 * 60 * 38).toISOString(),
    },
    {
      id: 902,
      wallet_id: walletId,
      website_id: 1,
      entry_type: "writer_earning",
      direction: "credit",
      status: "posted",
      amount: "120.00",
      balance_before: "300.00",
      balance_after: "420.00",
      reference: "ORD-1042",
      reference_type: "writer_earning",
      description: "Writer earning posted after approval",
      created_at: new Date(now - 1000 * 60 * 60 * 3).toISOString(),
    },
    {
      id: 903,
      wallet_id: walletId,
      website_id: 1,
      entry_type: "admin_debit",
      direction: "debit",
      status: "completed",
      amount: "42.00",
      balance_before: "462.00",
      balance_after: "420.00",
      reference: "ADJ-42",
      reference_type: "admin_debit",
      description: "Adjustment for duplicate earning",
      created_at: new Date(now - 1000 * 60 * 60 * 9).toISOString(),
    },
  ];
}

function previewHolds(walletId: number): AdminWalletHoldRecord[] {
  const now = Date.now();
  return [
    {
      id: 501,
      wallet_id: walletId,
      website_id: 1,
      amount: "186.00",
      status: "active",
      reason: "Writer payout under review",
      reference: "PAY-501",
      reference_type: "writer_payout",
      created_at: new Date(now - 1000 * 60 * 44).toISOString(),
      expires_at: new Date(now + 1000 * 60 * 60 * 24 * 2).toISOString(),
    },
  ];
}

function resolvedWebsiteParams(extra: Record<string, unknown> = {}, selectedWebsiteId?: number | null) {
  const portalCtx = usePortalContextStore();
  const websiteId = selectedWebsiteId || portalCtx.website?.id;
  return websiteId ? { ...extra, website_id: websiteId } : extra;
}

function resolvedWebsitePayload<T extends Record<string, unknown>>(
  payload: T,
  selectedWebsiteId?: number | null,
): T & { website_id?: number } {
  const portalCtx = usePortalContextStore();
  const websiteId = selectedWebsiteId || portalCtx.website?.id;
  return websiteId ? { ...payload, website_id: websiteId } : payload;
}

export const useAdminWalletsStore = defineStore("admin-wallets", () => {
  const wallets = ref<AdminWalletRecord[]>([]);
  const entries = ref<AdminWalletEntryRecord[]>([]);
  const holds = ref<AdminWalletHoldRecord[]>([]);
  const selectedWalletId = ref<number | null>(null);
  const selectedHoldId = ref<number | null>(null);
  const selectedWebsiteId = ref<number | null>(null);
  const query = ref("");
  const filter = ref<WalletFilter>("all");
  const isLoading = ref(false);
  const isLoadingDetail = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");
  const adjustmentForm = ref({
    amount: 25,
    description: "Admin balance adjustment",
    reference: "",
    reference_type: "admin_adjustment",
  });
  const ensureForm = ref({
    user_id: null as number | null,
    user_lookup: "",
    wallet_type: "client" as "client" | "writer",
    currency: "USD",
  });
  const holdForm = ref({
    amount: 25,
    reason: "Manual admin hold",
    reference: "",
    reference_type: "admin_hold",
    expires_at: "",
  });

  const selectedWallet = computed(() =>
    wallets.value.find((wallet) => wallet.id === selectedWalletId.value) ?? null,
  );

  const selectedHold = computed(() =>
    holds.value.find((hold) => hold.id === selectedHoldId.value) ?? null,
  );

  const filteredWallets = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return wallets.value.filter((wallet) => {
      const filterMatches =
        filter.value === "all" ||
        (filter.value === "attention" ? needsAttention(wallet) : wallet.wallet_type === filter.value);
      const textMatches =
        !needle ||
        [
          wallet.id,
          wallet.owner_user_id,
          wallet.owner_user_email,
          wallet.owner_user_name,
          wallet.owner_user_role,
          wallet.website_id,
          wallet.wallet_type,
          wallet.status,
          wallet.currency,
        ].some((value) => String(value ?? "").toLowerCase().includes(needle));
      return filterMatches && textMatches;
    });
  });

  const metrics = computed<AdminWalletMetric[]>(() => {
    const currency = wallets.value[0]?.currency ?? "USD";
    const clientTotal = wallets.value
      .filter((wallet) => wallet.wallet_type === "client")
      .reduce((sum, wallet) => sum + numeric(wallet.available_balance), 0);
    const writerTotal = wallets.value
      .filter((wallet) => wallet.wallet_type === "writer")
      .reduce((sum, wallet) => sum + numeric(wallet.available_balance), 0);
    const pendingTotal = wallets.value.reduce((sum, wallet) => sum + numeric(wallet.pending_balance), 0);
    const attentionCount = wallets.value.filter(needsAttention).length;

    return [
      {
        label: "Client funds",
        value: money(clientTotal, currency),
        detail: "Available client wallet balances across tenant scope.",
        tone: "neutral",
      },
      {
        label: "Writer balances",
        value: money(writerTotal, currency),
        detail: "Writer funds available or awaiting payout actions.",
        tone: "good",
      },
      {
        label: "Pending or held",
        value: money(pendingTotal, currency),
        detail: "Balances that need operational review before movement.",
        tone: pendingTotal ? "warn" : "good",
      },
      {
        label: "Needs attention",
        value: attentionCount,
        detail: "Inactive, suspended, locked, or pending-balance wallets.",
        tone: attentionCount ? "risk" : "neutral",
      },
    ];
  });

  async function hydrate() {
    const auth = useAuthStore();
    const portalCtx = usePortalContextStore();
    if (!selectedWebsiteId.value && portalCtx.website?.id) {
      selectedWebsiteId.value = portalCtx.website.id;
    }
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        wallets.value = previewWallets();
        selectedWalletId.value = selectedWalletId.value ?? wallets.value[0]?.id ?? null;
        if (selectedWalletId.value) {
          entries.value = previewEntries(selectedWalletId.value);
          holds.value = previewHolds(selectedWalletId.value);
          selectedHoldId.value = holds.value[0]?.id ?? null;
        }
        return;
      }

      const { data } = await adminWalletsApi.wallets(
        resolvedWebsiteParams({ page_size: 100 }, selectedWebsiteId.value),
      );
      wallets.value = normalizeList(data);
      if (!selectedWalletId.value || !wallets.value.some((wallet) => wallet.id === selectedWalletId.value)) {
        selectedWalletId.value = wallets.value[0]?.id ?? null;
      }
      if (selectedWalletId.value) await loadWalletDetail(selectedWalletId.value);
    } catch (caught) {
      error.value = "Unable to load wallet operations.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function loadWalletDetail(walletId: number) {
    const auth = useAuthStore();
    selectedWalletId.value = walletId;
    selectedHoldId.value = null;
    isLoadingDetail.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        entries.value = previewEntries(walletId);
        holds.value = previewHolds(walletId);
        selectedHoldId.value = holds.value[0]?.id ?? null;
        return;
      }

      const [entryRes, holdRes] = await Promise.all([
        adminWalletsApi.entries(walletId, resolvedWebsiteParams({ page_size: 50 }, selectedWebsiteId.value)),
        adminWalletsApi.holds(walletId, resolvedWebsiteParams({ page_size: 25 }, selectedWebsiteId.value)),
      ]);
      entries.value = normalizeList(entryRes.data);
      holds.value = normalizeList(holdRes.data);
      selectedHoldId.value = holds.value.find((hold) => `${hold.status ?? ""}`.toLowerCase() === "active")?.id ?? holds.value[0]?.id ?? null;
    } finally {
      isLoadingDetail.value = false;
    }
  }

  function adjustmentPayload(): AdminWalletAdjustmentPayload {
    return resolvedWebsitePayload({
      amount: Number(adjustmentForm.value.amount),
      description: adjustmentForm.value.description,
      reference: adjustmentForm.value.reference,
      reference_type: adjustmentForm.value.reference_type,
    }, selectedWebsiteId.value);
  }

  function holdPayload(): AdminWalletHoldPayload {
    return resolvedWebsitePayload({
      amount: Number(holdForm.value.amount),
      reason: holdForm.value.reason,
      reference: holdForm.value.reference,
      reference_type: holdForm.value.reference_type,
      expires_at: holdForm.value.expires_at ? new Date(holdForm.value.expires_at).toISOString() : null,
    }, selectedWebsiteId.value);
  }

  async function ensureWallet() {
    const auth = useAuthStore();
    const ui = useUiStore();
    const lookup = ensureForm.value.user_lookup.trim();
    if (!ensureForm.value.user_id && !lookup) {
      error.value = "Enter a client or writer user ID, email, username, or name before selecting a wallet.";
      ui.toast(error.value, "error");
      return;
    }
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        const wallet: AdminWalletRecord = {
          id: Date.now(),
          website_id: 1,
          owner_user_id: ensureForm.value.user_id,
          owner_user_email: lookup || `${ensureForm.value.wallet_type}.${ensureForm.value.user_id}@preview.local`,
          owner_user_name: lookup || `Preview ${ensureForm.value.wallet_type} #${ensureForm.value.user_id}`,
          owner_user_role: ensureForm.value.wallet_type,
          wallet_type: ensureForm.value.wallet_type,
          currency: ensureForm.value.currency,
          status: "active",
          is_active: true,
          available_balance: "0.00",
          pending_balance: "0.00",
          total_credited: "0.00",
          total_debited: "0.00",
          last_activity_at: new Date().toISOString(),
        };
        wallets.value = [wallet, ...wallets.value.filter((item) => item.id !== wallet.id)];
        selectedWalletId.value = wallet.id;
        entries.value = [];
        holds.value = [];
        return;
      }

      const payload: AdminEnsureWalletPayload = resolvedWebsitePayload({
        user_id: ensureForm.value.user_id,
        user_lookup: lookup,
        wallet_type: ensureForm.value.wallet_type,
        currency: ensureForm.value.currency,
      }, selectedWebsiteId.value);
      const { data } = await adminWalletsApi.ensureWallet(payload);
      wallets.value = [data, ...wallets.value.filter((item) => item.id !== data.id)];
      selectedWalletId.value = data.id;
      await loadWalletDetail(data.id);
      notice.value = "Wallet selected and ready for top-up.";
      ui.toast(notice.value, "success");
    } catch (caught) {
      error.value = "Could not find or create that wallet. Check the user, role, and website.";
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function setWebsiteId(websiteId: number | null) {
    selectedWebsiteId.value = websiteId;
    selectedWalletId.value = null;
    selectedHoldId.value = null;
    entries.value = [];
    holds.value = [];
    await hydrate();
  }

  async function runWalletAction(action: "fund" | "debit" | "hold" | "reconcile" | "repair") {
    const auth = useAuthStore();
    const walletId = selectedWalletId.value;
    if (!walletId) return;
    const ui = useUiStore();
    if (isMutating.value) return;
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        if (action === "fund" || action === "debit") {
          const amount = Number(adjustmentForm.value.amount);
          const wallet = selectedWallet.value;
          wallets.value = wallets.value.map((item) => {
            if (item.id !== walletId) return item;
            const nextAvailable = action === "fund"
              ? numeric(item.available_balance) + amount
              : Math.max(0, numeric(item.available_balance) - amount);
            return {
              ...item,
              available_balance: nextAvailable.toFixed(2),
              last_activity_at: new Date().toISOString(),
            };
          });
          entries.value = [
            {
              id: Date.now(),
              wallet_id: walletId,
              website_id: wallet?.website_id,
              entry_type: action === "fund" ? "admin_credit" : "admin_debit",
              direction: action === "fund" ? "credit" : "debit",
              status: "completed",
              amount: amount.toFixed(2),
              reference: adjustmentForm.value.reference || `PREVIEW-${Date.now()}`,
              reference_type: adjustmentForm.value.reference_type,
              description: adjustmentForm.value.description,
              created_at: new Date().toISOString(),
            },
            ...entries.value,
          ];
        }

        if (action === "hold") {
          holds.value = [
            {
              id: Date.now(),
              wallet_id: walletId,
              amount: Number(holdForm.value.amount).toFixed(2),
              status: "active",
              reason: holdForm.value.reason,
              reference: holdForm.value.reference,
              reference_type: holdForm.value.reference_type,
              expires_at: holdForm.value.expires_at ? new Date(holdForm.value.expires_at).toISOString() : null,
              created_at: new Date().toISOString(),
            },
            ...holds.value,
          ];
        }

        notice.value = `Preview ${action} action completed.`;
        ui.toast(notice.value, "success");
        return;
      }

      if (action === "fund") await adminWalletsApi.fund(walletId, adjustmentPayload());
      if (action === "debit") await adminWalletsApi.debit(walletId, adjustmentPayload());
      if (action === "hold") await adminWalletsApi.createHold(walletId, holdPayload());
      if (action === "reconcile") await adminWalletsApi.reconcile(walletId);
      if (action === "repair") await adminWalletsApi.repair(walletId);

      notice.value = `Wallet ${action} action completed.`;
      ui.toast(notice.value, "success");
      await hydrate();
    } catch (caught) {
      error.value = "Wallet action failed. Check permissions, amount, and tenant context.";
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function releaseSelectedHold() {
    const auth = useAuthStore();
    const holdId = selectedHoldId.value;
    if (!holdId) return;
    const ui = useUiStore();
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        holds.value = holds.value.map((hold) =>
          hold.id === holdId
            ? { ...hold, status: "released", released_at: new Date().toISOString() }
            : hold,
        );
        notice.value = "Preview hold released.";
        ui.toast(notice.value, "success");
        return;
      }
      await adminWalletsApi.releaseHold(holdId);
      notice.value = "Hold released.";
      ui.toast(notice.value, "success");
      if (selectedWalletId.value) await loadWalletDetail(selectedWalletId.value);
    } finally {
      isMutating.value = false;
    }
  }

  async function captureSelectedHold() {
    const auth = useAuthStore();
    const holdId = selectedHoldId.value;
    if (!holdId) return;
    const ui = useUiStore();
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        holds.value = holds.value.map((hold) =>
          hold.id === holdId
            ? { ...hold, status: "captured", captured_at: new Date().toISOString() }
            : hold,
        );
        notice.value = "Preview hold captured.";
        ui.toast(notice.value, "success");
        return;
      }
      await adminWalletsApi.captureHold(holdId);
      notice.value = "Hold captured.";
      ui.toast(notice.value, "success");
      if (selectedWalletId.value) await loadWalletDetail(selectedWalletId.value);
    } finally {
      isMutating.value = false;
    }
  }

  return {
    wallets,
    entries,
    holds,
    selectedWalletId,
    selectedHoldId,
    selectedWebsiteId,
    selectedWallet,
    selectedHold,
    query,
    filter,
    filteredWallets,
    metrics,
    isLoading,
    isLoadingDetail,
    isMutating,
    error,
    notice,
    adjustmentForm,
    ensureForm,
    holdForm,
    hydrate,
    loadWalletDetail,
    runWalletAction,
    ensureWallet,
    setWebsiteId,
    releaseSelectedHold,
    captureSelectedHold,
  };
});
