<template>
  <div class="p-6 space-y-4">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Financial Audit</h1>
      <p class="text-sm text-gray-500 mt-0.5">Raw compensation event log, writer exposure snapshots, and wallet balances</p>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex gap-6">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'pb-3 text-sm font-medium border-b-2 transition-colors',
            activeTab === tab.key
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700',
          ]"
        >{{ tab.label }}</button>
      </nav>
    </div>

    <!-- ── Financial Events ───────────────────────────────────────────────── -->
    <div v-if="activeTab === 'events'" class="space-y-4">
      <!-- Filters -->
      <div class="flex flex-wrap gap-3 items-end">
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Status</label>
          <select v-model="eventFilters.status" class="input text-sm w-36">
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="mature">Mature</option>
            <option value="settled">Settled</option>
            <option value="reversed">Reversed</option>
            <option value="disputed">Disputed</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Type</label>
          <select v-model="eventFilters.event_type" class="input text-sm w-40">
            <option value="">All types</option>
            <option value="order_bonus">Order Bonus</option>
            <option value="tip">Tip</option>
            <option value="fine">Fine</option>
            <option value="adjustment">Adjustment</option>
            <option value="advance">Advance</option>
            <option value="reversal">Reversal</option>
          </select>
        </div>
        <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
          <input v-model="eventFilters.risky_only" type="checkbox" class="rounded" />
          Risky only
        </label>
        <button @click="loadEvents" :disabled="loadingEvents" class="btn-primary text-sm">Apply</button>
      </div>

      <div v-if="loadingEvents" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!events.length" class="text-center py-10 text-gray-400 text-sm">No events found.</div>
      <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Event</th>
              <th class="px-3 py-2 text-left">Writer</th>
              <th class="px-3 py-2 text-right">Amount</th>
              <th class="px-3 py-2 text-left">Status</th>
              <th class="px-3 py-2 text-left">Flags</th>
              <th class="px-3 py-2 text-left">Date</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="ev in events"
              :key="ev.id"
              class="hover:bg-gray-50 cursor-pointer"
              @click="selectedEvent = ev"
            >
              <td class="px-3 py-2">
                <p class="font-medium text-gray-800 text-xs font-mono">{{ ev.event_type }}</p>
                <p v-if="ev.title" class="text-xs text-gray-500 mt-0.5 max-w-xs truncate">{{ ev.title }}</p>
              </td>
              <td class="px-3 py-2 text-gray-600 text-xs">#{{ ev.writer }}</td>
              <td class="px-3 py-2 text-right font-mono font-semibold text-sm" :class="ev.is_positive ? 'text-green-700' : 'text-red-600'">
                {{ ev.is_positive ? '+' : '-' }}${{ ev.amount }}
              </td>
              <td class="px-3 py-2">
                <span :class="eventStatusClass(ev.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ ev.status }}</span>
              </td>
              <td class="px-3 py-2">
                <div class="flex gap-1">
                  <span v-if="ev.is_risky" class="text-xs bg-red-50 text-red-600 px-1.5 py-0.5 rounded">risky</span>
                  <span v-if="ev.is_locked" class="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">locked</span>
                  <span v-if="ev.reversed_at" class="text-xs bg-amber-50 text-amber-600 px-1.5 py-0.5 rounded">reversed</span>
                </div>
              </td>
              <td class="px-3 py-2 text-xs text-gray-400 whitespace-nowrap">{{ fmtDate(ev.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Event detail panel -->
      <div v-if="selectedEvent" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 space-y-4 max-h-[90vh] overflow-y-auto">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-800">Event #{{ selectedEvent.id }}</h3>
            <button @click="selectedEvent = null" class="text-gray-400 hover:text-gray-600 text-lg leading-none">&times;</button>
          </div>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="col-span-2 flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span class="text-gray-500">Amount</span>
              <span class="font-bold text-lg" :class="selectedEvent.is_positive ? 'text-green-700' : 'text-red-600'">
                {{ selectedEvent.is_positive ? '+' : '-' }}${{ selectedEvent.amount }} {{ selectedEvent.currency }}
              </span>
            </div>
            <detail-row label="Type" :value="selectedEvent.event_type" mono />
            <detail-row label="Status" :value="selectedEvent.status" />
            <detail-row label="Source" :value="selectedEvent.source ?? '—'" />
            <detail-row label="Writer" :value="'#' + selectedEvent.writer" />
            <detail-row v-if="selectedEvent.title" label="Title" :value="selectedEvent.title" class="col-span-2" />
            <detail-row v-if="selectedEvent.description" label="Description" :value="selectedEvent.description" class="col-span-2" />
            <detail-row v-if="selectedEvent.reference" label="Reference" :value="selectedEvent.reference" mono />
            <detail-row v-if="selectedEvent.window_label" label="Window" :value="selectedEvent.window_label" />
            <detail-row label="Visible to Writer" :value="selectedEvent.is_visible_to_writer ? 'Yes' : 'No'" />
            <detail-row label="Created By" :value="selectedEvent.created_by_name ?? '—'" />
            <detail-row label="Created" :value="fmtDatetime(selectedEvent.created_at)" class="col-span-2" />
            <detail-row v-if="selectedEvent.matured_at" label="Matured" :value="fmtDatetime(selectedEvent.matured_at)" />
            <detail-row v-if="selectedEvent.reversed_at" label="Reversed" :value="fmtDatetime(selectedEvent.reversed_at)" />
          </div>
        </div>
      </div>
    </div>

    <!-- ── Exposure Ledger ────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'exposure'" class="space-y-4">
      <p class="text-sm text-gray-500">Per-writer running financial exposure: earnings, settlements, advances, and risk cap.</p>

      <div v-if="loadingExposure" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!exposure.length" class="text-center py-10 text-gray-400 text-sm">No exposure records.</div>
      <div v-else class="bg-white rounded-lg border border-gray-200 overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Writer</th>
              <th class="px-3 py-2 text-right">Earned</th>
              <th class="px-3 py-2 text-right">Settled</th>
              <th class="px-3 py-2 text-right">Paid</th>
              <th class="px-3 py-2 text-right">Advance</th>
              <th class="px-3 py-2 text-right">Recoverable</th>
              <th class="px-3 py-2 text-right">Risk Cap</th>
              <th class="px-3 py-2 text-left">Updated</th>
              <th class="px-3 py-2 text-left"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="ex in exposure" :key="ex.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-gray-700 font-medium">#{{ ex.writer }}</td>
              <td class="px-3 py-2 text-right font-mono text-xs text-gray-700">${{ ex.total_earned }}</td>
              <td class="px-3 py-2 text-right font-mono text-xs text-gray-700">${{ ex.total_settled }}</td>
              <td class="px-3 py-2 text-right font-mono text-xs text-green-700 font-semibold">${{ ex.total_paid }}</td>
              <td class="px-3 py-2 text-right font-mono text-xs" :class="parseFloat(ex.total_advance_taken) > 0 ? 'text-amber-600' : 'text-gray-400'">
                ${{ ex.total_advance_taken }}
              </td>
              <td class="px-3 py-2 text-right font-mono text-xs font-semibold" :class="parseFloat(ex.recoverable_balance) > 0 ? 'text-indigo-700' : 'text-gray-400'">
                ${{ ex.recoverable_balance }}
              </td>
              <td class="px-3 py-2 text-right font-mono text-xs text-gray-500">{{ ex.risk_cap_percentage }}%</td>
              <td class="px-3 py-2 text-xs text-gray-400">{{ fmtDate(ex.last_updated) }}</td>
              <td class="px-3 py-2">
                <button
                  @click="doRecompute(ex.id)"
                  :disabled="actioning"
                  class="text-xs px-2.5 py-1 rounded border border-indigo-200 text-indigo-600 hover:bg-indigo-50 disabled:opacity-50"
                >Recompute</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Wallets ────────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'wallets'" class="space-y-4">
      <p class="text-sm text-gray-500">Writer compensation wallet balances. Use credit/debit for manual adjustments.</p>

      <div v-if="loadingWallets" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!wallets.length" class="text-center py-10 text-gray-400 text-sm">No wallets found.</div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="w in wallets"
          :key="w.id"
          class="bg-white rounded-lg border border-gray-200 p-5 space-y-3"
        >
          <div class="flex items-start justify-between">
            <div>
              <p class="font-semibold text-gray-800 text-sm">Owner #{{ w.owner }}</p>
              <p class="text-xs text-gray-400 font-mono mt-0.5">{{ w.currency }}</p>
            </div>
            <span :class="w.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs font-medium px-2 py-0.5 rounded-full">
              {{ w.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>

          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="bg-gray-50 rounded-lg p-2.5">
              <p class="text-gray-500">Available</p>
              <p class="font-bold text-gray-800 mt-0.5 text-base">${{ w.available_balance }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2.5">
              <p class="text-gray-500">Locked</p>
              <p class="font-semibold text-amber-700 mt-0.5">${{ w.locked_balance }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2.5">
              <p class="text-gray-500">Total In</p>
              <p class="font-semibold text-green-700 mt-0.5">${{ w.total_inflow }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2.5">
              <p class="text-gray-500">Total Out</p>
              <p class="font-semibold text-red-600 mt-0.5">${{ w.total_outflow }}</p>
            </div>
          </div>

          <div class="flex gap-2 pt-1">
            <button @click="openWalletAction(w, 'credit')" class="text-xs px-3 py-1.5 rounded border border-green-200 text-green-600 hover:bg-green-50 flex-1">Credit</button>
            <button @click="openWalletAction(w, 'debit')" class="text-xs px-3 py-1.5 rounded border border-red-200 text-red-500 hover:bg-red-50 flex-1">Debit</button>
          </div>
        </div>
      </div>

      <!-- Credit/debit dialog -->
      <div v-if="walletAction.open" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
          <h3 class="font-semibold text-gray-800 capitalize">{{ walletAction.type }} Wallet — Owner #{{ walletAction.wallet?.owner }}</h3>
          <div class="space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Amount ($)</label>
              <input v-model="walletAction.amount" type="number" step="0.01" min="0.01" class="input" placeholder="0.00" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Entry Type</label>
              <input v-model="walletAction.entry_type" class="input" placeholder="manual" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">Description (optional)</label>
              <input v-model="walletAction.description" class="input" />
            </div>
            <label v-if="walletAction.type === 'debit'" class="flex items-center gap-2 cursor-pointer text-sm text-gray-600">
              <input v-model="walletAction.allow_negative" type="checkbox" class="rounded" />
              Allow negative balance
            </label>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button @click="walletAction.open = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
            <button
              @click="doWalletAction"
              :disabled="actioning || !walletAction.amount"
              :class="walletAction.type === 'credit' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'"
              class="text-sm px-4 py-2 rounded-lg text-white disabled:opacity-50 transition"
            >{{ actioning ? 'Processing…' : (walletAction.type === 'credit' ? 'Credit' : 'Debit') }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div
      v-if="toast"
      class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl shadow-lg text-sm text-white"
      :class="toast.type === 'error' ? 'bg-red-600' : 'bg-green-600'"
    >{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { adminCompensationApi } from "@/api/adminCompensation";
import type { FinancialEvent, ExposureLedger, CompensationWallet } from "@/api/adminCompensation";

// detail-row is an inline render helper — no separate component needed
const DetailRow = {
  props: { label: String, value: String, mono: Boolean },
  template: `<div class="space-y-0.5"><p class="text-xs text-gray-400">{{ label }}</p><p :class="mono ? 'font-mono text-xs' : 'text-sm'" class="text-gray-700 break-all">{{ value }}</p></div>`,
};

const tabs = [
  { key: "events", label: "Financial Events" },
  { key: "exposure", label: "Exposure Ledger" },
  { key: "wallets", label: "Wallets" },
] as const;

const activeTab = ref("events");

// ── Financial events ───────────────────────────────────────────────────────
const events = ref<FinancialEvent[]>([]);
const loadingEvents = ref(false);
const selectedEvent = ref<FinancialEvent | null>(null);

const eventFilters = reactive({
  status: "",
  event_type: "",
  risky_only: false,
});

async function loadEvents() {
  loadingEvents.value = true;
  try {
    const params: Record<string, unknown> = {};
    if (eventFilters.status) params.status = eventFilters.status;
    if (eventFilters.event_type) params.event_type = eventFilters.event_type;
    if (eventFilters.risky_only) params.is_risky = true;
    const resp = await adminCompensationApi.financialEvents(params);
    const data = resp.data;
    events.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load events", "error");
  } finally {
    loadingEvents.value = false;
  }
}

function eventStatusClass(status: string) {
  const map: Record<string, string> = {
    pending: "bg-amber-100 text-amber-700",
    mature: "bg-blue-100 text-blue-700",
    settled: "bg-green-100 text-green-700",
    reversed: "bg-gray-100 text-gray-600",
    disputed: "bg-red-100 text-red-700",
  };
  return map[status] ?? "bg-gray-100 text-gray-600";
}

// ── Exposure ledger ────────────────────────────────────────────────────────
const exposure = ref<ExposureLedger[]>([]);
const loadingExposure = ref(false);
const actioning = ref(false);

async function loadExposure() {
  loadingExposure.value = true;
  try {
    const resp = await adminCompensationApi.exposureLedger();
    const data = resp.data;
    exposure.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load exposure ledger", "error");
  } finally {
    loadingExposure.value = false;
  }
}

async function doRecompute(id: number) {
  actioning.value = true;
  try {
    const resp = await adminCompensationApi.recomputeExposure(id);
    const idx = exposure.value.findIndex((e) => e.id === id);
    if (idx !== -1) exposure.value[idx] = resp.data;
    showToast("Exposure recomputed");
  } catch {
    showToast("Recompute failed", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Wallets ────────────────────────────────────────────────────────────────
const wallets = ref<CompensationWallet[]>([]);
const loadingWallets = ref(false);

const walletAction = reactive({
  open: false,
  type: "credit" as "credit" | "debit",
  wallet: null as CompensationWallet | null,
  amount: "",
  entry_type: "manual",
  description: "",
  allow_negative: false,
});

async function loadWallets() {
  loadingWallets.value = true;
  try {
    const resp = await adminCompensationApi.compWallets();
    const data = resp.data;
    wallets.value = Array.isArray(data) ? data : data.results;
  } catch {
    showToast("Failed to load wallets", "error");
  } finally {
    loadingWallets.value = false;
  }
}

function openWalletAction(w: CompensationWallet, type: "credit" | "debit") {
  walletAction.open = true;
  walletAction.wallet = w;
  walletAction.type = type;
  walletAction.amount = "";
  walletAction.entry_type = "manual";
  walletAction.description = "";
  walletAction.allow_negative = false;
}

async function doWalletAction() {
  if (!walletAction.wallet || !walletAction.amount) return;
  actioning.value = true;
  try {
    const payload = {
      wallet_id: walletAction.wallet.id,
      amount: walletAction.amount,
      entry_type: walletAction.entry_type || "manual",
      description: walletAction.description || undefined,
    };
    if (walletAction.type === "credit") {
      await adminCompensationApi.creditWallet(payload);
    } else {
      await adminCompensationApi.debitWallet({ ...payload, allow_negative: walletAction.allow_negative });
    }
    await loadWallets();
    walletAction.open = false;
    showToast(`Wallet ${walletAction.type}ed`);
  } catch {
    showToast(`${walletAction.type === "credit" ? "Credit" : "Debit"} failed`, "error");
  } finally {
    actioning.value = false;
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const toast = ref<{ message: string; type: "success" | "error" } | null>(null);

function showToast(message: string, type: "success" | "error" = "success") {
  toast.value = { message, type };
  setTimeout(() => (toast.value = null), 3500);
}

function fmtDate(ts: string) {
  return new Date(ts).toLocaleDateString(undefined, { dateStyle: "medium" });
}

function fmtDatetime(ts: string) {
  return new Date(ts).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

onMounted(() => {
  loadEvents();
  loadExposure();
  loadWallets();
});
</script>

<style scoped>
.input {
  @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent;
}
.btn-primary {
  @apply px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition;
}
</style>
