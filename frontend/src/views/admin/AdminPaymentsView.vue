<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  CalendarClock,
  CheckCircle2,
  CreditCard,
  FileText,
  Loader2,
  Plus,
  Receipt,
  RefreshCw,
  Search,
  Send,
  WalletCards,
  XCircle,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import SavedViewPresets from "@/components/admin/SavedViewPresets.vue";
import { useAdminPaymentsStore } from "@/stores/adminPayments";
import { useWebsitesStore } from "@/stores/websites";
import {
  billingApi,
  type AdminInvoice,
  type AdminPaymentRequest,
  type CreateInvoicePayload,
  type CreatePaymentRequestPayload,
} from "@/api/billing";

const payments = useAdminPaymentsStore();

// ─── Billing: invoices & payment requests ────────────────────────────────────
const invoices = ref<AdminInvoice[]>([]);
const invoicesLoading = ref(false);
const invoicesError = ref("");

const prList = ref<AdminPaymentRequest[]>([]);
const prLoading = ref(false);

const billingTab = ref<"invoices" | "payment-requests">("invoices");
const showInvForm = ref(false);
const showPrForm = ref(false);
const billingMutating = ref(false);
const billingSuccess = ref("");
const billingError = ref("");

const invForm = ref<CreateInvoicePayload>({
  title: "",
  purpose: "",
  amount: "",
  due_at: "",
  description: "",
  recipient_email: "",
  recipient_name: "",
  currency: "USD",
});

const prForm = ref<CreatePaymentRequestPayload>({
  title: "",
  purpose: "",
  amount: "",
  due_at: "",
  description: "",
  recipient_email: "",
  recipient_name: "",
});

async function fetchInvoices() {
  invoicesLoading.value = true;
  invoicesError.value = "";
  try {
    const { data } = await billingApi.invoices({ ordering: "-created_at" });
    invoices.value = Array.isArray(data) ? data : (data as { results: AdminInvoice[] }).results ?? [];
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    invoicesError.value = detail ?? "Could not load invoices.";
  } finally {
    invoicesLoading.value = false;
  }
}

async function fetchPaymentRequests() {
  prLoading.value = true;
  try {
    const { data } = await billingApi.paymentRequests({ ordering: "-created_at" });
    prList.value = Array.isArray(data) ? data : (data as { results: AdminPaymentRequest[] }).results ?? [];
  } catch {
    // non-critical
  } finally {
    prLoading.value = false;
  }
}

async function createInvoice() {
  billingMutating.value = true;
  billingError.value = "";
  billingSuccess.value = "";
  try {
    const { data } = await billingApi.createInvoice(invForm.value);
    invoices.value.unshift(data);
    billingSuccess.value = `Invoice "${data.reference}" created as draft.`;
    showInvForm.value = false;
    invForm.value = { title: "", purpose: "", amount: "", due_at: "", description: "", recipient_email: "", recipient_name: "", currency: "USD" };
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string; title?: string[] } } })?.response?.data;
    billingError.value = detail?.detail ?? detail?.title?.[0] ?? "Failed to create invoice.";
  } finally {
    billingMutating.value = false;
  }
}

async function issueInvoice(inv: AdminInvoice) {
  billingMutating.value = true;
  billingError.value = "";
  billingSuccess.value = "";
  try {
    const { data } = await billingApi.issueInvoice(inv.id);
    const idx = invoices.value.findIndex((i) => i.id === inv.id);
    if (idx !== -1) invoices.value[idx] = data;
    billingSuccess.value = `Invoice ${data.reference} issued.`;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    billingError.value = detail ?? "Issue failed.";
  } finally {
    billingMutating.value = false;
  }
}

async function createPaymentRequest() {
  billingMutating.value = true;
  billingError.value = "";
  billingSuccess.value = "";
  try {
    const { data } = await billingApi.createPaymentRequest(prForm.value);
    prList.value.unshift(data);
    billingSuccess.value = `Payment request "${data.reference}" created.`;
    showPrForm.value = false;
    prForm.value = { title: "", purpose: "", amount: "", due_at: "", description: "", recipient_email: "", recipient_name: "" };
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    billingError.value = detail ?? "Failed to create payment request.";
  } finally {
    billingMutating.value = false;
  }
}

async function issuePaymentRequest(pr: AdminPaymentRequest) {
  billingMutating.value = true;
  billingError.value = "";
  try {
    const { data } = await billingApi.issuePaymentRequest(pr.id);
    const idx = prList.value.findIndex((p) => p.id === pr.id);
    if (idx !== -1) prList.value[idx] = data;
    billingSuccess.value = `Payment request ${data.reference} issued.`;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    billingError.value = detail ?? "Issue failed.";
  } finally {
    billingMutating.value = false;
  }
}
// ─── End Billing ─────────────────────────────────────────────────────────────

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const filterOptions = [
  { key: "all", label: "All" },
  { key: "client", label: "Client payments" },
  { key: "writer", label: "Writer payouts" },
  { key: "refund", label: "Refunds" },
] as const;

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatAmount(value: string | number, currency = "USD") {
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return String(value);
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

function statusTone(status?: string | null) {
  const normalized = (status ?? "").toLowerCase();
  if (normalized.includes("failed") || normalized.includes("rejected") || normalized.includes("cancel")) {
    return "danger";
  }
  if (normalized.includes("pending") || normalized.includes("held") || normalized.includes("review")) {
    return "warning";
  }
  if (normalized.includes("complete") || normalized.includes("approved") || normalized.includes("released") || normalized.includes("posted") || normalized.includes("captured")) {
    return "success";
  }
  return "neutral";
}

const websites = useWebsitesStore();
onMounted(() => {
  payments.hydrate().catch(() => undefined);
  websites.ensure();
  fetchInvoices();
  fetchPaymentRequests();
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Payments</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Client payments, wallet balances, refund queues, and writer payout
          operations separated from the communications desk.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        @click="payments.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="payments.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ payments.error }} Preview mode will still show the layout.
    </p>

    <p
      v-if="payments.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ payments.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in payments.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <!-- Writer payment cycle breakdown -->
    <section v-if="payments.cycleBreakdown.length" class="rounded-md border border-slate-200 bg-white p-5">
      <div class="flex items-center gap-2">
        <CalendarClock class="h-5 w-5 text-signal" />
        <h2 class="text-base font-semibold text-ink">Writer payment cycles</h2>
      </div>
      <p class="mt-1 text-sm text-graphite">Disbursements classified by payment window cycle.</p>
      <div class="mt-4 grid gap-3 sm:grid-cols-3">
        <div
          v-for="row in payments.cycleBreakdown"
          :key="row.cycle"
          class="rounded-md border p-4 text-center"
          :class="row.cycle === 'BIWEEKLY' ? 'border-sky-200 bg-sky-50' : row.cycle === 'MONTHLY' ? 'border-violet-200 bg-violet-50' : 'border-slate-200 bg-slate-50'"
        >
          <p
            class="text-xs font-semibold uppercase tracking-wide"
            :class="row.cycle === 'BIWEEKLY' ? 'text-sky-700' : row.cycle === 'MONTHLY' ? 'text-violet-700' : 'text-graphite'"
          >
            {{ row.cycle === "BIWEEKLY" ? "Bi-weekly" : row.cycle === "MONTHLY" ? "Monthly" : row.cycle }}
          </p>
          <p class="mt-2 text-2xl font-semibold text-ink">{{ formatAmount(row.writerTotal) }}</p>
          <p class="mt-1 text-xs text-graphite">{{ row.count }} payout(s) to writers</p>
          <p class="mt-0.5 text-xs text-graphite">{{ formatAmount(row.margin) }} platform margin</p>
        </div>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.8fr)]">
      <div class="rounded-xl border border-slate-200 bg-white">
        <div class="flex items-center gap-2 border-b border-slate-200 px-5 py-4">
          <CreditCard class="h-5 w-5 text-signal" />
          <div>
            <h2 class="text-base font-semibold text-ink">Payment activity</h2>
            <p class="text-xs text-graphite">Client inflows, writer payouts, and refunds.</p>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 bg-slate-50 px-5 py-3">
          <div class="flex flex-wrap gap-1">
            <button
              v-for="option in filterOptions"
              :key="option.key"
              class="focus-ring h-8 rounded-lg px-3 text-xs font-semibold transition-colors"
              :class="payments.filter === option.key ? 'bg-ink text-white shadow-sm' : 'bg-white border border-slate-200 text-graphite hover:border-slate-300 hover:text-ink'"
              type="button"
              @click="payments.filter = option.key"
            >
              {{ option.label }}
            </button>
          </div>
          <label class="relative ml-auto block w-52">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <input
              v-model="payments.query"
              class="focus-ring h-8 w-full rounded-lg border border-slate-200 bg-white pl-8 pr-3 text-xs"
              type="search"
              placeholder="Search payments…"
            />
          </label>
          <SavedViewPresets
            view-type="payments"
            :current-filters="{ query: payments.query }"
            @load="(f) => { payments.query = String(f.query ?? ''); }"
          />
        </div>

        <div v-if="payments.feed.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-3 py-2">Record</th>
                <th class="px-3 py-2">Type</th>
                <th class="px-3 py-2">Amount</th>
                <th class="px-3 py-2">Status</th>
                <th class="px-3 py-2">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in payments.feed" :key="item.id">
                <td class="px-3 py-2.5">
                  <p class="font-semibold text-ink">{{ item.title }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ item.subtitle }}</p>
                </td>
                <td class="px-3 py-2.5 capitalize text-graphite">{{ item.source }}</td>
                <td class="px-3 py-2.5 font-semibold text-ink">{{ formatAmount(item.amount) }}</td>
                <td class="px-3 py-2.5">
                  <StatusPill :label="item.status" :tone="statusTone(item.status)" />
                </td>
                <td class="px-3 py-2.5 text-graphite">{{ formatDate(item.date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="CreditCard"
            title="No payment records"
            message="Payment records will appear here once wallet, refund, and payout endpoints respond."
          />
        </div>
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white">
          <div class="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 px-4">
            <div class="flex items-center gap-2">
              <WalletCards class="h-5 w-5 text-signal" />
              <div>
                <h2 class="text-base font-semibold">Writer payout ops</h2>
                <p class="text-sm text-graphite">Approve, process, or reject payout holds.</p>
              </div>
            </div>
          </div>

          <div v-if="payments.payouts.length" class="divide-y divide-slate-100">
            <article
              v-for="payout in payments.payouts"
              :key="payout.id"
              class="px-4 py-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">{{ payout.writer_email || `Writer #${payout.writer_id}` }}</p>
                  <p class="mt-1 text-sm text-graphite">{{ payout.reason || payout.reference || "Payout request" }}</p>
                </div>
                <p class="font-semibold text-ink">{{ formatAmount(payout.amount) }}</p>
              </div>
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <StatusPill :label="payout.workflow_status || payout.status" :tone="statusTone(payout.workflow_status || payout.status)" />
                <span class="text-xs text-graphite">{{ formatDate(payout.created_at) }}</span>
              </div>
              <div class="mt-4 grid gap-2 sm:grid-cols-3">
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
                  type="button"
                  :disabled="payments.isMutating"
                  @click="payments.approvePayout(payout.id).catch(() => undefined)"
                >
                  <CheckCircle2 class="h-4 w-4" />
                  Approve
                </button>
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
                  type="button"
                  :disabled="payments.isMutating"
                  @click="payments.processPayout(payout.id).catch(() => undefined)"
                >
                  <Send class="h-4 w-4" />
                  Process
                </button>
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-3 text-xs font-semibold text-rose-700"
                  type="button"
                  :disabled="payments.isMutating"
                  @click="payments.rejectPayout(payout.id).catch(() => undefined)"
                >
                  <XCircle class="h-4 w-4" />
                  Reject
                </button>
              </div>
            </article>
          </div>

          <div v-else class="p-4">
            <EmptyState
              :icon="WalletCards"
              title="No writer payout requests"
              message="Writer payout requests from wallet holds will appear here."
            />
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <WalletCards class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Wallet balances</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Client and writer wallet state from the canonical wallets app.</p>
          </div>

          <div v-if="payments.wallets.length" class="divide-y divide-slate-100">
            <article
              v-for="wallet in payments.wallets"
              :key="wallet.id"
              class="grid gap-2 px-4 py-4 sm:grid-cols-[1fr_auto]"
            >
              <div>
                <p class="font-semibold text-ink capitalize">{{ wallet.wallet_type }} wallet #{{ wallet.id }}</p>
                <p class="mt-1 text-xs text-graphite">
                  Owner #{{ wallet.owner_user_id || "n/a" }} · {{ websites.nameById(wallet.website_id) }}
                </p>
              </div>
              <div class="sm:text-right">
                <p class="font-semibold text-ink">{{ formatAmount(wallet.available_balance || 0, wallet.currency || "USD") }}</p>
                <StatusPill :label="wallet.status || 'unknown'" :tone="statusTone(wallet.status)" />
              </div>
            </article>
          </div>

          <div v-else class="p-4">
            <EmptyState
              :icon="WalletCards"
              title="No wallets loaded"
              message="Admin wallet records will appear here when the backend is connected."
            />
          </div>
        </section>
      </aside>
    </section>

    <!-- ─── Billing: Invoices & Payment Requests ──────────────────────────── -->
    <section class="space-y-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 class="text-lg font-semibold text-ink">Invoices & Payment Requests</h2>
        <div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
          <button
            class="focus-ring rounded-md px-4 py-2 text-xs font-semibold transition-colors"
            :class="billingTab === 'invoices' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
            type="button"
            @click="billingTab = 'invoices'"
          >
            Invoices
            <span v-if="invoices.length" class="ml-1 text-xs text-graphite">({{ invoices.length }})</span>
          </button>
          <button
            class="focus-ring rounded-md px-4 py-2 text-xs font-semibold transition-colors"
            :class="billingTab === 'payment-requests' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
            type="button"
            @click="billingTab = 'payment-requests'"
          >
            Payment Requests
            <span v-if="prList.length" class="ml-1 text-xs text-graphite">({{ prList.length }})</span>
          </button>
        </div>
      </div>

      <p v-if="billingError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ billingError }}</p>
      <p v-if="billingSuccess" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{{ billingSuccess }}</p>

      <!-- INVOICES TAB -->
      <template v-if="billingTab === 'invoices'">
        <div class="flex justify-end">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white"
            type="button"
            @click="showInvForm = !showInvForm"
          >
            <Plus class="h-4 w-4" />
            {{ showInvForm ? "Cancel" : "New Invoice" }}
          </button>
        </div>

        <!-- Create invoice form -->
        <div v-if="showInvForm" class="rounded-lg border border-slate-200 bg-white p-5">
          <h3 class="mb-4 text-sm font-semibold text-ink">Create draft invoice</h3>
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="block sm:col-span-2">
              <span class="text-xs font-semibold uppercase text-graphite">Title</span>
              <input v-model="invForm.title" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="Invoice title" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Purpose</span>
              <input v-model="invForm.purpose" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="e.g. order_payment" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Amount</span>
              <input v-model="invForm.amount" type="number" step="0.01" min="0" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="0.00" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Due date</span>
              <input v-model="invForm.due_at" type="datetime-local" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Currency</span>
              <input v-model="invForm.currency" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="USD" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Recipient email</span>
              <input v-model="invForm.recipient_email" type="email" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Recipient name</span>
              <input v-model="invForm.recipient_name" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block sm:col-span-2">
              <span class="text-xs font-semibold uppercase text-graphite">Description</span>
              <textarea v-model="invForm.description" rows="2" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
            </label>
          </div>
          <div class="mt-4">
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="billingMutating || !invForm.title || !invForm.amount || !invForm.due_at"
              @click="createInvoice"
            >
              <Loader2 v-if="billingMutating" class="h-4 w-4 animate-spin" />
              <FileText v-else class="h-4 w-4" />
              Create Invoice
            </button>
          </div>
        </div>

        <div v-if="invoicesError" class="text-sm text-berry">{{ invoicesError }}</div>

        <div v-if="invoicesLoading && !invoices.length" class="space-y-2">
          <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-4">
            <div class="h-3 w-1/3 rounded bg-slate-200" />
            <div class="mt-2 h-3 w-1/2 rounded bg-slate-100" />
          </div>
        </div>

        <div v-else-if="!invoices.length" class="rounded-lg border border-slate-200 bg-white p-8">
          <EmptyState :icon="FileText" title="No invoices" message="Create the first invoice above." />
        </div>

        <div v-else class="rounded-lg border border-slate-200 bg-white overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-3 py-2">Reference</th>
                <th class="px-3 py-2">Title</th>
                <th class="px-3 py-2">Recipient</th>
                <th class="px-3 py-2">Amount</th>
                <th class="px-3 py-2">Status</th>
                <th class="px-3 py-2">Due</th>
                <th class="px-3 py-2" />
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="inv in invoices" :key="inv.id" class="hover:bg-slate-50">
                <td class="px-3 py-2 font-mono text-xs text-graphite">{{ inv.reference }}</td>
                <td class="px-3 py-2 font-medium text-ink">{{ inv.title }}</td>
                <td class="px-3 py-2 text-graphite">{{ inv.recipient_email ?? "—" }}</td>
                <td class="px-3 py-2 font-semibold text-ink">{{ formatAmount(inv.amount, inv.currency) }}</td>
                <td class="px-3 py-2"><StatusPill :label="inv.status" :tone="statusTone(inv.status)" /></td>
                <td class="px-3 py-2 text-graphite">{{ inv.due_at ? formatDate(inv.due_at) : "—" }}</td>
                <td class="px-3 py-2">
                  <button
                    v-if="inv.status === 'draft'"
                    class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold hover:bg-slate-50 disabled:opacity-60"
                    type="button"
                    :disabled="billingMutating"
                    @click="issueInvoice(inv)"
                  >
                    <Send class="h-3.5 w-3.5" />
                    Issue
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- PAYMENT REQUESTS TAB -->
      <template v-else>
        <div class="flex justify-end">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white"
            type="button"
            @click="showPrForm = !showPrForm"
          >
            <Plus class="h-4 w-4" />
            {{ showPrForm ? "Cancel" : "New Payment Request" }}
          </button>
        </div>

        <div v-if="showPrForm" class="rounded-lg border border-slate-200 bg-white p-5">
          <h3 class="mb-4 text-sm font-semibold text-ink">Create payment request</h3>
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="block sm:col-span-2">
              <span class="text-xs font-semibold uppercase text-graphite">Title</span>
              <input v-model="prForm.title" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="Payment request title" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Purpose</span>
              <input v-model="prForm.purpose" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Amount</span>
              <input v-model="prForm.amount" type="number" step="0.01" min="0" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="0.00" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Due date</span>
              <input v-model="prForm.due_at" type="datetime-local" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Recipient email</span>
              <input v-model="prForm.recipient_email" type="email" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Recipient name</span>
              <input v-model="prForm.recipient_name" type="text" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block sm:col-span-2">
              <span class="text-xs font-semibold uppercase text-graphite">Description</span>
              <textarea v-model="prForm.description" rows="2" class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" />
            </label>
          </div>
          <div class="mt-4">
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="billingMutating || !prForm.title || !prForm.amount || !prForm.due_at"
              @click="createPaymentRequest"
            >
              <Loader2 v-if="billingMutating" class="h-4 w-4 animate-spin" />
              <Receipt v-else class="h-4 w-4" />
              Create
            </button>
          </div>
        </div>

        <div v-if="prLoading && !prList.length" class="space-y-2">
          <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-4">
            <div class="h-3 w-1/3 rounded bg-slate-200" />
          </div>
        </div>

        <div v-else-if="!prList.length" class="rounded-lg border border-slate-200 bg-white p-8">
          <EmptyState :icon="Receipt" title="No payment requests" message="Create the first payment request above." />
        </div>

        <div v-else class="rounded-lg border border-slate-200 bg-white overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-3 py-2">Reference</th>
                <th class="px-3 py-2">Title</th>
                <th class="px-3 py-2">Recipient</th>
                <th class="px-3 py-2">Amount</th>
                <th class="px-3 py-2">Status</th>
                <th class="px-3 py-2">Due</th>
                <th class="px-3 py-2" />
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="pr in prList" :key="pr.id" class="hover:bg-slate-50">
                <td class="px-3 py-2 font-mono text-xs text-graphite">{{ pr.reference }}</td>
                <td class="px-3 py-2 font-medium text-ink">{{ pr.title }}</td>
                <td class="px-3 py-2 text-graphite">{{ pr.recipient_email ?? "—" }}</td>
                <td class="px-3 py-2 font-semibold text-ink">{{ formatAmount(pr.amount, pr.currency) }}</td>
                <td class="px-3 py-2"><StatusPill :label="pr.status" :tone="statusTone(pr.status)" /></td>
                <td class="px-3 py-2 text-graphite">{{ pr.due_at ? formatDate(pr.due_at) : "—" }}</td>
                <td class="px-3 py-2">
                  <button
                    v-if="pr.status === 'draft'"
                    class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold hover:bg-slate-50 disabled:opacity-60"
                    type="button"
                    :disabled="billingMutating"
                    @click="issuePaymentRequest(pr)"
                  >
                    <Send class="h-3.5 w-3.5" />
                    Issue
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </section>
  </div>
</template>
