<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  FileText,
  Loader2,
  Receipt,
  RefreshCw,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { billingApi, type ClientInvoice, type ClientPaymentRequest } from "@/api/billing";

const activeTab = ref<"invoices" | "payment-requests">("invoices");

const invoices = ref<ClientInvoice[]>([]);
const invoicesLoading = ref(false);
const invoicesError = ref("");
const expandedInvoice = ref<number | null>(null);

const paymentRequests = ref<ClientPaymentRequest[]>([]);
const prLoading = ref(false);
const prError = ref("");

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

const isLoading = computed(() =>
  activeTab.value === "invoices" ? invoicesLoading.value : prLoading.value,
);

onMounted(refresh);
</script>

<template>
  <div class="space-y-6">
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
    </div>

    <!-- ─── INVOICES ───────────────────────────────────────────── -->
    <template v-if="activeTab === 'invoices'">
      <p v-if="invoicesError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {{ invoicesError }}
      </p>

      <div v-if="invoicesLoading && !invoices.length" class="space-y-3">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
          <div class="h-4 w-1/3 rounded bg-slate-200" />
          <div class="mt-3 h-3 w-1/2 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!invoices.length" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center shadow-panel">
        <FileText class="mx-auto h-8 w-8 text-slate-300" />
        <p class="mt-3 text-sm font-medium text-ink">No invoices yet</p>
        <p class="mt-1 text-sm text-graphite">Invoices will appear here once issued by the platform.</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="inv in invoices"
          :key="inv.id"
          class="rounded-lg border border-slate-200 bg-white shadow-panel"
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
                </div>
              </div>

              <div v-else class="rounded-md border border-slate-100 bg-slate-50 px-4 py-3 text-sm text-graphite">
                Single payment — no installment schedule.
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
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>

    <!-- ─── PAYMENT REQUESTS ──────────────────────────────────── -->
    <template v-else>
      <p v-if="prError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {{ prError }}
      </p>

      <div v-if="prLoading && !paymentRequests.length" class="space-y-3">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
          <div class="h-4 w-1/3 rounded bg-slate-200" />
          <div class="mt-3 h-3 w-1/2 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!paymentRequests.length" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center shadow-panel">
        <Receipt class="mx-auto h-8 w-8 text-slate-300" />
        <p class="mt-3 text-sm font-medium text-ink">No payment requests</p>
        <p class="mt-1 text-sm text-graphite">Payment requests sent to you will appear here.</p>
      </div>

      <div v-else class="rounded-lg border border-slate-200 bg-white shadow-panel">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-5 py-3">Reference</th>
                <th class="px-5 py-3">Title</th>
                <th class="px-5 py-3">Amount</th>
                <th class="px-5 py-3">Status</th>
                <th class="px-5 py-3">Due</th>
                <th class="px-5 py-3">Balance</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="pr in paymentRequests" :key="pr.id" class="hover:bg-slate-50">
                <td class="px-5 py-4 font-mono text-xs text-graphite">{{ pr.reference }}</td>
                <td class="px-5 py-4">
                  <p class="font-medium text-ink">{{ pr.title }}</p>
                  <p v-if="pr.description" class="mt-0.5 text-xs text-graphite">{{ pr.description }}</p>
                </td>
                <td class="px-5 py-4 font-semibold text-ink">{{ money(pr.amount, pr.currency) }}</td>
                <td class="px-5 py-4">
                  <StatusPill :label="pr.status" :tone="statusTone(pr.status)" />
                </td>
                <td class="px-5 py-4 text-graphite">{{ date(pr.due_at) }}</td>
                <td class="px-5 py-4">
                  <span v-if="pr.is_fully_paid" class="text-signal font-semibold">Paid</span>
                  <span v-else class="text-ink">{{ money(pr.remaining_balance, pr.currency) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
