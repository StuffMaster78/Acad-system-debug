<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CreditCard,
  FileText,
  Loader2,
  Receipt,
  RefreshCw,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import {
  billingApi,
  type ClientInvoice,
  type ClientPaymentRequest,
  type ReceiptRecord,
} from "@/api/billing";

const activeTab = ref<"invoices" | "payment-requests" | "receipts">("invoices");

const invoices = ref<ClientInvoice[]>([]);
const invoicesLoading = ref(false);
const invoicesError = ref("");
const expandedInvoice = ref<number | null>(null);

const paymentRequests = ref<ClientPaymentRequest[]>([]);
const prLoading = ref(false);
const prError = ref("");

// Installment payment
const payingInstallmentId = ref<number | null>(null);
const installmentPayError = ref<Record<number, string>>({});

// Full invoice payment
const payingInvoiceId = ref<number | null>(null);
const invoicePayError = ref<Record<number, string>>({});

// Payment request payment
const payingPrId = ref<number | null>(null);
const prPayError = ref<Record<number, string>>({});

// Receipts
const receipts = ref<ReceiptRecord[]>([]);
const receiptsLoading = ref(false);
const receiptsError = ref("");

async function payInstallment(installmentId: number, invoiceId: number) {
  payingInstallmentId.value = installmentId;
  installmentPayError.value = { ...installmentPayError.value, [installmentId]: "" };
  try {
    const { data } = await billingApi.prepareInstallmentPayment(installmentId, "stripe");
    if (data.provider_data && (data.provider_data as { checkout_url?: string }).checkout_url) {
      window.location.href = (data.provider_data as { checkout_url: string }).checkout_url;
    } else {
      await fetchInvoices();
    }
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    installmentPayError.value = { ...installmentPayError.value, [installmentId]: detail ?? "Payment failed. Please try again." };
  } finally {
    payingInstallmentId.value = null;
  }
}

async function payInstallmentFromWallet(installmentId: number) {
  payingInstallmentId.value = installmentId;
  installmentPayError.value = { ...installmentPayError.value, [installmentId]: "" };
  try {
    await billingApi.prepareInstallmentPayment(installmentId, "wallet");
    await fetchInvoices();
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    installmentPayError.value = { ...installmentPayError.value, [installmentId]: detail ?? "Payment failed. Please try again." };
  } finally {
    payingInstallmentId.value = null;
  }
}

async function fetchInvoices() {
  invoicesLoading.value = true;
  invoicesError.value = "";
  try {
    const { data } = await billingApi.myInvoices();
    invoices.value = Array.isArray(data) ? data : [];
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    invoicesError.value = detail ?? "Could not load invoices.";
  } finally {
    invoicesLoading.value = false;
  }
}

async function payInvoice(invoiceId: number) {
  payingInvoiceId.value = invoiceId;
  invoicePayError.value = { ...invoicePayError.value, [invoiceId]: "" };
  try {
    const { data } = await billingApi.prepareMyInvoicePayment(invoiceId);
    const checkoutUrl = (data.provider_data as { checkout_url?: string }).checkout_url;
    if (checkoutUrl) {
      window.location.href = checkoutUrl;
    } else {
      await fetchInvoices();
    }
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    invoicePayError.value = { ...invoicePayError.value, [invoiceId]: detail ?? "Payment failed. Please try again." };
  } finally {
    payingInvoiceId.value = null;
  }
}

async function payPaymentRequest(prId: number) {
  payingPrId.value = prId;
  prPayError.value = { ...prPayError.value, [prId]: "" };
  try {
    const { data } = await billingApi.prepareMyPaymentRequestPayment(prId);
    const checkoutUrl = (data.provider_data as { checkout_url?: string }).checkout_url;
    if (checkoutUrl) {
      window.location.href = checkoutUrl;
    } else {
      await fetchPaymentRequests();
    }
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    prPayError.value = { ...prPayError.value, [prId]: detail ?? "Payment failed. Please try again." };
  } finally {
    payingPrId.value = null;
  }
}

async function fetchReceipts() {
  receiptsLoading.value = true;
  receiptsError.value = "";
  try {
    const { data } = await billingApi.myReceipts();
    receipts.value = Array.isArray(data) ? data : [];
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    receiptsError.value = detail ?? "Could not load receipts.";
  } finally {
    receiptsLoading.value = false;
  }
}

async function fetchPaymentRequests() {
  prLoading.value = true;
  prError.value = "";
  try {
    const { data } = await billingApi.myPaymentRequests();
    paymentRequests.value = Array.isArray(data) ? data : [];
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    prError.value = detail ?? "Could not load payment requests.";
  } finally {
    prLoading.value = false;
  }
}

function refresh() {
  fetchInvoices();
  fetchPaymentRequests();
  fetchReceipts();
}

function toggleInvoice(id: number) {
  expandedInvoice.value = expandedInvoice.value === id ? null : id;
}

function statusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  const s = status.toLowerCase();
  if (s === "paid" || s === "completed") return "success";
  if (s === "overdue" || s === "cancelled" || s === "expired") return "danger";
  if (s === "issued" || s === "pending" || s === "draft") return "warning";
  return "neutral";
}

function money(value: string | number, currency = "USD"): string {
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(n);
}

function date(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
}

const isLoading = computed(() => {
  if (activeTab.value === "invoices") return invoicesLoading.value;
  if (activeTab.value === "payment-requests") return prLoading.value;
  return receiptsLoading.value;
});

onMounted(refresh);
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Client</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Billing</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Your invoices and payment requests, including installment schedules and balances.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="isLoading"
        @click="refresh"
      >
        <Loader2 v-if="isLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <!-- Tab bar -->
    <div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 w-fit">
      <button
        class="focus-ring rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'invoices' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="activeTab = 'invoices'"
      >
        Invoices
        <span
          v-if="invoices.length"
          class="ml-1.5 rounded-full bg-slate-200 px-1.5 py-0.5 text-xs"
        >{{ invoices.length }}</span>
      </button>
      <button
        class="focus-ring rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'payment-requests' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="activeTab = 'payment-requests'"
      >
        Payment Requests
        <span
          v-if="paymentRequests.length"
          class="ml-1.5 rounded-full bg-slate-200 px-1.5 py-0.5 text-xs"
        >{{ paymentRequests.length }}</span>
      </button>
      <button
        class="focus-ring rounded-md px-4 py-2 text-sm font-semibold transition-colors"
        :class="activeTab === 'receipts' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        type="button"
        @click="activeTab = 'receipts'"
      >
        Receipts
        <span
          v-if="receipts.length"
          class="ml-1.5 rounded-full bg-slate-200 px-1.5 py-0.5 text-xs"
        >{{ receipts.length }}</span>
      </button>
    </div>

    <!-- ─── INVOICES ───────────────────────────────────────────── -->
    <template v-if="activeTab === 'invoices'">
      <p v-if="invoicesError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {{ invoicesError }}
      </p>

      <div v-if="invoicesLoading && !invoices.length" class="space-y-3">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5">
          <div class="h-4 w-1/3 rounded bg-slate-200" />
          <div class="mt-3 h-3 w-1/2 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!invoices.length" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center">
        <FileText class="mx-auto h-8 w-8 text-slate-300" />
        <p class="mt-3 text-sm font-medium text-ink">No invoices yet</p>
        <p class="mt-1 text-sm text-graphite">Invoices will appear here once issued by the platform.</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="inv in invoices"
          :key="inv.id"
          class="rounded-lg border border-slate-200 bg-white"
        >
          <!-- Invoice header row -->
          <button
            class="focus-ring w-full text-left"
            type="button"
            @click="toggleInvoice(inv.id)"
          >
            <div class="flex items-start gap-4 px-5 py-4">
              <div class="mt-0.5 shrink-0">
                <CheckCircle2
                  v-if="inv.is_fully_paid"
                  class="h-5 w-5 text-signal"
                />
                <Receipt v-else class="h-5 w-5 text-slate-400" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="font-semibold text-ink">{{ inv.title }}</p>
                  <StatusPill :label="inv.status" :tone="statusTone(inv.status)" />
                  <span v-if="inv.is_fully_paid" class="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">Paid in full</span>
                </div>
                <p class="mt-1 text-sm text-graphite">
                  Ref: {{ inv.reference }}
                  <span v-if="inv.issued_at"> · Issued {{ date(inv.issued_at) }}</span>
                  <span v-if="inv.due_at"> · Due {{ date(inv.due_at) }}</span>
                </p>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-lg font-semibold text-ink">{{ money(inv.amount, inv.currency) }}</p>
                <p v-if="!inv.is_fully_paid" class="mt-0.5 text-xs text-graphite">
                  {{ money(inv.remaining_balance, inv.currency) }} remaining
                </p>
                <ChevronDown
                  v-if="expandedInvoice === inv.id"
                  class="ml-auto mt-2 h-4 w-4 text-graphite"
                />
                <ChevronRight v-else class="ml-auto mt-2 h-4 w-4 text-graphite" />
              </div>
            </div>
          </button>

          <!-- Installments expansion -->
          <template v-if="expandedInvoice === inv.id">
            <div class="border-t border-slate-100 px-5 py-4">
              <div v-if="inv.description" class="mb-4 text-sm text-graphite">{{ inv.description }}</div>

              <!-- Payment progress bar -->
              <div class="mb-4">
                <div class="flex items-center justify-between text-xs font-semibold text-graphite mb-1.5">
                  <span>Payment progress</span>
                  <span>{{ money(inv.total_paid, inv.currency) }} of {{ money(inv.amount, inv.currency) }}</span>
                </div>
                <div class="h-2 w-full rounded-full bg-slate-100">
                  <div
                    class="h-2 rounded-full bg-signal transition-all"
                    :style="{
                      width: `${Math.min(100, (Number(inv.total_paid) / Number(inv.amount)) * 100)}%`
                    }"
                  />
                </div>
              </div>

              <div v-if="inv.installments.length" class="space-y-2">
                <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">
                  Installments ({{ inv.installments.length }})
                </p>
                <div
                  v-for="inst in inv.installments"
                  :key="inst.id"
                  class="flex items-center justify-between rounded-md border px-4 py-3 text-sm"
                  :class="inst.is_paid
                    ? 'border-emerald-100 bg-emerald-50'
                    : inst.is_overdue
                      ? 'border-rose-100 bg-rose-50'
                      : 'border-slate-100 bg-slate-50'"
                >
                  <div>
                    <p class="font-medium text-ink">Instalment {{ inst.sequence_number }}</p>
                    <p class="mt-0.5 text-xs text-graphite">
                      Due {{ date(inst.due_at) }}
                      <span v-if="inst.paid_at"> · Paid {{ date(inst.paid_at) }}</span>
                    </p>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="text-right">
                    <p class="font-semibold text-ink">{{ money(inst.amount, inv.currency) }}</p>
                    <p
                      v-if="inst.is_paid"
                      class="mt-0.5 text-xs font-semibold text-signal"
                    >Paid</p>
                    <p
                      v-else-if="inst.is_overdue"
                      class="mt-0.5 text-xs font-semibold text-berry"
                    >Overdue</p>
                    <p
                      v-else-if="inst.is_partially_paid"
                      class="mt-0.5 text-xs text-graphite"
                    >{{ money(inst.remaining_amount, inv.currency) }} left</p>
                  </div>
                    <!-- Pay buttons for pending installments -->
                    <div v-if="!inst.is_paid && !inst.cancelled_at" class="flex flex-col gap-1.5 shrink-0">
                      <button
                        class="inline-flex items-center gap-1.5 rounded-lg bg-signal px-3 py-1.5 text-xs font-semibold text-white hover:bg-signal/90 disabled:opacity-50 transition-colors"
                        type="button"
                        :disabled="payingInstallmentId === inst.id"
                        @click="payInstallment(inst.id, inv.id)"
                      >
                        <CreditCard class="h-3 w-3" />
                        {{ payingInstallmentId === inst.id ? "Processing…" : "Pay by card" }}
                      </button>
                      <button
                        class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50 transition-colors"
                        type="button"
                        :disabled="payingInstallmentId === inst.id"
                        @click="payInstallmentFromWallet(inst.id)"
                      >
                        Wallet
                      </button>
                      <p v-if="installmentPayError[inst.id]" class="text-xs text-rose-600 max-w-[140px] text-right">{{ installmentPayError[inst.id] }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="rounded-md border border-slate-100 bg-slate-50 px-4 py-3 text-sm text-graphite">
                <div class="flex items-center justify-between gap-4">
                  <span>Single payment — no installment schedule.</span>
                  <div v-if="!inv.is_fully_paid" class="flex gap-2 shrink-0">
                    <button
                      class="inline-flex items-center gap-1.5 rounded-lg bg-signal px-3 py-1.5 text-xs font-semibold text-white hover:bg-signal/90 disabled:opacity-50 transition-colors"
                      type="button"
                      :disabled="payingInvoiceId === inv.id"
                      @click="payInvoice(inv.id)"
                    >
                      <CreditCard class="h-3 w-3" />
                      {{ payingInvoiceId === inv.id ? 'Processing…' : 'Pay by card' }}
                    </button>
                  </div>
                </div>
                <p v-if="invoicePayError[inv.id]" class="mt-2 text-xs text-rose-600">{{ invoicePayError[inv.id] }}</p>
              </div>

              <!-- Next installment callout -->
              <div
                v-if="inv.next_installment && !inv.is_fully_paid"
                class="mt-4 flex items-center gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-semibold text-amber-900">
                    Next payment: {{ money(inv.next_installment.amount, inv.currency) }}
                  </p>
                  <p class="mt-0.5 text-xs text-amber-700">
                    Due {{ date(inv.next_installment.due_at) }} · Instalment {{ inv.next_installment.sequence_number }}
                  </p>
                </div>
                <div class="shrink-0 flex flex-col gap-1.5">
                  <button
                    class="inline-flex items-center gap-1.5 rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-700 disabled:opacity-50 transition-colors"
                    type="button"
                    :disabled="payingInstallmentId === inv.next_installment.id"
                    @click="payInstallment(inv.next_installment.id, inv.id)"
                  >
                    <CreditCard class="h-3 w-3" />
                    {{ payingInstallmentId === inv.next_installment.id ? "Processing…" : "Pay by card" }}
                  </button>
                  <button
                    class="rounded-lg border border-amber-300 px-3 py-1.5 text-xs font-semibold text-amber-800 hover:bg-amber-100 disabled:opacity-50 transition-colors"
                    type="button"
                    :disabled="payingInstallmentId === inv.next_installment.id"
                    @click="payInstallmentFromWallet(inv.next_installment.id)"
                  >
                    Pay from wallet
                  </button>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>

    <!-- ─── PAYMENT REQUESTS ──────────────────────────────────── -->
    <template v-else-if="activeTab === 'payment-requests'">
      <p v-if="prError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {{ prError }}
      </p>

      <div v-if="prLoading && !paymentRequests.length" class="space-y-3">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5">
          <div class="h-4 w-1/3 rounded bg-slate-200" />
          <div class="mt-3 h-3 w-1/2 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!paymentRequests.length" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center">
        <Receipt class="mx-auto h-8 w-8 text-slate-300" />
        <p class="mt-3 text-sm font-medium text-ink">No payment requests</p>
        <p class="mt-1 text-sm text-graphite">Payment requests sent to you will appear here.</p>
      </div>

      <div v-else class="rounded-lg border border-slate-200 bg-white">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-3 py-2">Reference</th>
                <th class="px-3 py-2">Title</th>
                <th class="px-3 py-2">Amount</th>
                <th class="px-3 py-2">Status</th>
                <th class="px-3 py-2">Due</th>
                <th class="px-3 py-2">Balance</th>
                <th class="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="pr in paymentRequests" :key="pr.id" class="hover:bg-slate-50">
                <td class="px-3 py-2.5 font-mono text-xs text-graphite">{{ pr.reference }}</td>
                <td class="px-3 py-2.5">
                  <p class="font-medium text-ink">{{ pr.title }}</p>
                  <p v-if="pr.description" class="mt-0.5 text-xs text-graphite">{{ pr.description }}</p>
                </td>
                <td class="px-3 py-2.5 font-semibold text-ink">{{ money(pr.amount, pr.currency) }}</td>
                <td class="px-3 py-2.5">
                  <StatusPill :label="pr.status" :tone="statusTone(pr.status)" />
                </td>
                <td class="px-3 py-2.5 text-graphite">{{ date(pr.due_at) }}</td>
                <td class="px-3 py-2.5">
                  <span v-if="pr.is_fully_paid" class="text-signal font-semibold">Paid</span>
                  <span v-else class="text-ink">{{ money(pr.remaining_balance, pr.currency) }}</span>
                </td>
                <td class="px-3 py-2.5 text-right">
                  <div v-if="!pr.is_fully_paid && pr.status === 'issued'" class="flex flex-col gap-1 items-end">
                    <button
                      class="inline-flex items-center gap-1 rounded-lg bg-signal px-2.5 py-1 text-xs font-semibold text-white hover:bg-signal/90 disabled:opacity-50 transition-colors"
                      type="button"
                      :disabled="payingPrId === pr.id"
                      @click="payPaymentRequest(pr.id)"
                    >
                      <CreditCard class="h-3 w-3" />
                      {{ payingPrId === pr.id ? 'Processing…' : 'Pay now' }}
                    </button>
                    <p v-if="prPayError[pr.id]" class="text-xs text-rose-600 max-w-[120px] text-right">{{ prPayError[pr.id] }}</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- ─── RECEIPTS ────────────────────────────────────────────── -->
    <template v-else-if="activeTab === 'receipts'">
      <p v-if="receiptsError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {{ receiptsError }}
      </p>

      <div v-if="receiptsLoading && !receipts.length" class="space-y-3">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5">
          <div class="h-4 w-1/3 rounded bg-slate-200" />
          <div class="mt-3 h-3 w-1/2 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!receipts.length" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center">
        <Receipt class="mx-auto h-8 w-8 text-slate-300" />
        <p class="mt-3 text-sm font-medium text-ink">No receipts yet</p>
        <p class="mt-1 text-sm text-graphite">Receipts are issued after each successful payment.</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="rec in receipts"
          :key="rec.id"
          class="rounded-lg border border-slate-200 bg-white px-5 py-4"
        >
          <div class="flex flex-wrap items-start gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="font-semibold text-ink">{{ rec.title_snapshot || 'Payment Receipt' }}</p>
                <StatusPill :label="rec.status" :tone="rec.status === 'issued' ? 'success' : 'neutral'" />
              </div>
              <p class="mt-1 text-sm text-graphite">
                Ref: {{ rec.reference }}
                <span v-if="rec.issued_at"> · {{ date(rec.issued_at) }}</span>
              </p>
              <p v-if="rec.processor_display_name" class="mt-0.5 text-xs text-graphite">
                Processed by {{ rec.processor_display_name }}
                <span v-if="rec.statement_descriptor_snapshot">
                  · Statement: <span class="font-mono">{{ rec.statement_descriptor_snapshot }}</span>
                </span>
              </p>
            </div>
            <div class="shrink-0 text-right">
              <p class="text-lg font-semibold text-ink">{{ money(rec.amount, rec.currency) }}</p>
              <p class="mt-0.5 text-xs text-graphite uppercase tracking-wide">{{ rec.currency }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
