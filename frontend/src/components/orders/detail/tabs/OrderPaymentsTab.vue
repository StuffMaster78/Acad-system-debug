<template>
  <div class="space-y-4">
    <!-- Client: limited payment view -->
    <template v-if="role === 'client'">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <h2 class="text-base font-semibold text-ink">Payment summary</h2>
        <dl class="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Amount paid</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(order.amount_paid, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Balance due</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(order.remaining_balance, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Payment status</dt>
            <dd class="mt-1 text-sm text-ink capitalize">{{ order.payment_status ?? "—" }}</dd>
          </div>
          <div v-if="order.discount_code_used">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Discount applied</dt>
            <dd class="mt-1 font-mono text-sm text-ink">{{ order.discount_code_used }}</dd>
          </div>
        </dl>
        <!-- Pay remaining balance (wallet) -->
        <div
          v-if="parseFloat(String(order.remaining_balance ?? 0)) > 0"
          class="mt-4 border-t border-slate-100 pt-4"
        >
          <p class="mb-3 text-sm font-semibold text-ink">Pay remaining balance</p>
          <div v-if="payError" class="mb-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-berry">{{ payError }}</div>
          <div v-if="paySuccess" class="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-signal">{{ paySuccess }}</div>
          <div class="flex flex-wrap gap-2">
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="isPaying"
              @click="payWithWallet"
            >
              <Loader2 v-if="isPaying" class="h-4 w-4 animate-spin" />
              <Wallet v-else class="h-4 w-4" />
              Pay from wallet
            </button>
            <span class="self-center text-xs text-graphite">
              Balance: {{ walletBalance }}
            </span>
          </div>
        </div>

        <p class="mt-4 text-xs text-graphite">Invoice and receipt available from your billing page.</p>
      </div>
    </template>

    <!-- Support: limited view -->
    <template v-else-if="role === 'support'">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <h2 class="text-base font-semibold text-ink">Payment overview</h2>
        <dl class="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Total</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(order.total_price, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Paid</dt>
            <dd class="mt-1 text-sm text-ink">{{ money(order.amount_paid, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Balance</dt>
            <dd class="mt-1 text-sm text-ink">{{ money(order.remaining_balance, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Status</dt>
            <dd class="mt-1 text-sm capitalize text-ink">{{ order.payment_status ?? "—" }}</dd>
          </div>
        </dl>
        <p class="mt-3 text-xs text-graphite">Full payment trail and gateway details available to admin only.</p>
      </div>
    </template>

    <!-- Admin/superadmin: full payment trail from API -->
    <template v-else>
      <!-- Summary cards -->
      <div class="rounded-lg border border-slate-200 bg-white overflow-hidden">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div>
            <h2 class="text-base font-semibold text-ink">Payment trail</h2>
            <p v-if="summary?.last_payment_at" class="mt-0.5 text-xs text-graphite">
              Last payment {{ fmt(summary.last_payment_at) }}
            </p>
          </div>
          <button
            class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50"
            :disabled="loading"
            @click="load"
          >
            <RefreshCw class="size-3.5" :class="loading ? 'animate-spin' : ''" />
            Refresh
          </button>
        </div>

        <div v-if="loading" class="grid gap-px bg-slate-100 sm:grid-cols-3 lg:grid-cols-6 animate-pulse">
          <div v-for="n in 6" :key="n" class="bg-white px-5 py-4">
            <div class="h-3 w-20 rounded bg-slate-200" />
            <div class="mt-2 h-4 w-16 rounded bg-slate-100" />
          </div>
        </div>

        <dl v-else class="grid gap-px bg-slate-100 sm:grid-cols-3 lg:grid-cols-6">
          <div class="bg-white px-5 py-4">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Order total</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ mc(summary?.order_total ?? order.total_price) }}</dd>
          </div>
          <div class="bg-white px-5 py-4">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Paid</dt>
            <dd class="mt-1 text-sm font-semibold text-emerald-700">{{ mc(summary?.amount_paid ?? order.amount_paid) }}</dd>
          </div>
          <div class="bg-white px-5 py-4">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Balance due</dt>
            <dd class="mt-1 text-sm font-semibold" :class="(parseFloat(String(summary?.balance_due ?? order.remaining_balance ?? 0)) > 0) ? 'text-rose-600' : 'text-ink'">
              {{ mc(summary?.balance_due ?? order.remaining_balance) }}
            </dd>
          </div>
          <div class="bg-white px-5 py-4">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Pending</dt>
            <dd class="mt-1 text-sm text-amber-700">{{ mc(summary?.pending_amount ?? 0) }}</dd>
          </div>
          <div class="bg-white px-5 py-4">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Refunded</dt>
            <dd class="mt-1 text-sm text-ink">{{ mc(summary?.refunded_amount ?? 0) }}</dd>
          </div>
          <div class="bg-white px-5 py-4">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Writer payout</dt>
            <dd class="mt-1 text-sm text-ink">{{ money(order.writer_compensation, order.currency) }}</dd>
          </div>
        </dl>

        <div v-if="order.discount_code_used" class="border-t border-slate-100 px-5 py-3 text-xs text-graphite">
          Discount applied: <span class="font-mono font-semibold text-ink">{{ order.discount_code_used }}</span>
        </div>
      </div>

      <!-- Payment records table -->
      <div class="rounded-lg border border-slate-200 bg-white overflow-hidden">
        <div class="border-b border-slate-200 px-5 py-4">
          <h2 class="text-sm font-semibold text-ink">Payment records</h2>
          <p class="mt-0.5 text-xs text-graphite">All gateway transactions for this order</p>
        </div>

        <div v-if="loading" class="space-y-px">
          <div v-for="n in 3" :key="n" class="animate-pulse px-5 py-4">
            <div class="h-3 w-48 rounded bg-slate-200" />
            <div class="mt-2 h-3 w-32 rounded bg-slate-100" />
          </div>
        </div>

        <div v-else-if="!summary?.payments?.length" class="px-5 py-10 text-center">
          <CreditCard class="mx-auto mb-2 size-7 text-slate-300" />
          <p class="text-sm text-graphite">No payment records found.</p>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="p in summary!.payments"
            :key="p.id"
            class="flex items-start gap-4 px-5 py-4"
          >
            <span
              class="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full text-xs"
              :class="statusDot(p.status)"
            >
              <CheckCircle2 v-if="p.status === 'succeeded'" class="size-4" />
              <Clock v-else-if="p.status === 'pending' || p.status === 'processing'" class="size-4" />
              <XCircle v-else-if="p.status === 'refunded' || p.status === 'partially_refunded'" class="size-4" />
              <AlertCircle v-else class="size-4" />
            </span>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 flex-wrap">
                <p class="text-sm font-semibold text-ink">{{ mc(p.amount) }}</p>
                <span class="rounded-full px-2 py-0.5 text-xs font-semibold capitalize" :class="statusPill(p.status)">
                  {{ p.status.replace(/_/g, " ") }}
                </span>
                <span v-if="p.payment_type" class="text-xs text-graphite capitalize">
                  {{ p.payment_type.replace(/_/g, " ") }}
                </span>
              </div>
              <div class="mt-1 flex flex-wrap gap-3 text-xs text-graphite">
                <span v-if="p.payment_method">via {{ p.payment_method }}</span>
                <span v-if="p.reference_id" class="font-mono">ref: {{ p.reference_id }}</span>
                <span v-if="p.transaction_id" class="font-mono">txn: {{ p.transaction_id }}</span>
              </div>
            </div>
            <div class="shrink-0 text-right text-xs text-graphite">
              <p v-if="p.confirmed_at">{{ fmt(p.confirmed_at) }}</p>
              <p v-else-if="p.created_at" class="text-slate-400">{{ fmt(p.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { AlertCircle, CheckCircle2, Clock, CreditCard, Loader2, RefreshCw, Wallet, XCircle } from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderPaymentSummary, OrderSummary } from "@/types/orders";
import { ordersApi } from "@/api/orders";
import { useWalletStore } from "@/stores/wallets";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  role: UserRole;
}>();

const summary = ref<OrderPaymentSummary | null>(null);

// ── Wallet payment ───────────────────────────────────────────────────────────
const wallets = useWalletStore();
const isPaying = ref(false);
const payError = ref("");
const paySuccess = ref("");

const walletBalance = computed(() =>
  `${wallets.currency} ${wallets.availableBalance.toFixed(2)}`
);

async function payWithWallet() {
  isPaying.value = true;
  payError.value = "";
  paySuccess.value = "";
  try {
    const { data } = await ordersApi.payFromWallet(props.orderId);
    paySuccess.value = data.message ?? "Payment successful.";
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    payError.value = detail ?? "Payment failed. Check your wallet balance and try again.";
  } finally {
    isPaying.value = false;
  }
}
const loading = ref(false);

const isAdmin = () => props.role === "admin" || props.role === "superadmin";

function money(v: string | number | null | undefined, currency = "USD"): string {
  if (v === null || v === undefined || v === "") return `${currency} 0.00`;
  return `${currency} ${Number(v).toFixed(2)}`;
}

function mc(v: string | number | null | undefined): string {
  return money(v, props.order.currency ?? "USD");
}

function fmt(v: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

function statusDot(s: string): string {
  if (s === "succeeded") return "bg-emerald-100 text-emerald-600";
  if (s === "pending" || s === "processing") return "bg-amber-100 text-amber-600";
  if (s === "refunded" || s === "partially_refunded") return "bg-blue-100 text-blue-600";
  return "bg-rose-100 text-rose-600";
}

function statusPill(s: string): string {
  if (s === "succeeded") return "bg-emerald-100 text-emerald-700";
  if (s === "pending" || s === "processing") return "bg-amber-100 text-amber-700";
  if (s === "refunded" || s === "partially_refunded") return "bg-blue-100 text-blue-700";
  return "bg-rose-100 text-rose-700";
}

async function load() {
  if (!isAdmin()) return;
  loading.value = true;
  try {
    const { data } = await ordersApi.paymentSummary(props.orderId);
    summary.value = data;
  } catch {
    summary.value = null;
  } finally {
    loading.value = false;
  }
}

watch(() => props.orderId, load);
onMounted(load);
</script>
