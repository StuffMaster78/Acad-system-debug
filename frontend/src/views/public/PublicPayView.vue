<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import { CreditCard, Loader2, AlertCircle, ShieldCheck } from "@lucide/vue";
import { billingApi, type PublicInvoice } from "@/api/billing";

const route = useRoute();

// Route: /pay/:type/:token  where type is "invoice" or "payment-request"
const type = computed(() => String(route.params.type ?? "invoice"));
const token = computed(() => String(route.params.token ?? ""));

const doc = ref<PublicInvoice | null>(null);
const loading = ref(false);
const redirecting = ref(false);
const error = ref("");

function money(value: string | number, currency = "USD") {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(Number(value));
}

function date(value: string | null) {
  if (!value) return null;
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
}

async function fetchDetails() {
  // We call prepare immediately to get the checkout URL. The backend is
  // idempotent — if an intent already exists it reuses it.
  loading.value = true;
  error.value = "";
  try {
    let result;
    if (type.value === "invoice") {
      const { data } = await billingApi.publicPrepareInvoicePayment(token.value);
      doc.value = data.invoice;
      result = data;
    } else {
      const { data } = await billingApi.publicPreparePaymentRequestPayment(token.value);
      doc.value = data.payment_request;
      result = data;
    }
    return result;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    error.value = detail ?? "This payment link is invalid or has expired.";
    return null;
  } finally {
    loading.value = false;
  }
}

async function pay() {
  redirecting.value = true;
  error.value = "";
  try {
    let result;
    if (type.value === "invoice") {
      const { data } = await billingApi.publicPrepareInvoicePayment(token.value);
      result = data;
    } else {
      const { data } = await billingApi.publicPreparePaymentRequestPayment(token.value);
      result = data;
    }
    const checkoutUrl = (result.provider_data as { checkout_url?: string }).checkout_url;
    if (checkoutUrl) {
      window.location.href = checkoutUrl;
    } else {
      error.value = "Could not start checkout. Please try again.";
    }
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    error.value = detail ?? "Could not start checkout. Please try again.";
  } finally {
    redirecting.value = false;
  }
}

onMounted(async () => {
  // Pre-fetch so we can show the document details before the user clicks Pay
  await fetchDetails();
});
</script>

<template>
  <div class="flex min-h-[70vh] items-center justify-center px-4 py-16">
    <div class="w-full max-w-md space-y-4">

      <!-- Loading skeleton -->
      <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm animate-pulse space-y-4">
        <div class="h-5 w-1/2 rounded bg-slate-200" />
        <div class="h-4 w-3/4 rounded bg-slate-100" />
        <div class="h-10 rounded-xl bg-slate-100" />
      </div>

      <!-- Error state -->
      <div
        v-else-if="error && !doc"
        class="rounded-2xl border border-rose-200 bg-rose-50 p-8 text-center"
      >
        <AlertCircle class="mx-auto h-8 w-8 text-rose-500" />
        <p class="mt-3 font-semibold text-rose-900">Link unavailable</p>
        <p class="mt-1 text-sm text-rose-700">{{ error }}</p>
      </div>

      <!-- Invoice / payment request card -->
      <template v-else-if="doc">
        <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">
            {{ type === 'invoice' ? 'Invoice' : 'Payment Request' }}
          </p>
          <h1 class="mt-1 text-2xl font-semibold text-ink">{{ doc.title }}</h1>
          <p v-if="doc.description" class="mt-2 text-sm text-graphite">{{ doc.description }}</p>

          <div class="mt-6 rounded-xl border border-slate-100 bg-slate-50 px-5 py-4">
            <div class="flex items-baseline justify-between">
              <span class="text-sm text-graphite">Amount due</span>
              <span class="text-2xl font-bold text-ink">{{ money(doc.amount, doc.currency) }}</span>
            </div>
            <div v-if="doc.due_at" class="mt-1.5 flex items-baseline justify-between text-xs text-graphite">
              <span>Due</span>
              <span>{{ date(doc.due_at) }}</span>
            </div>
          </div>

          <!-- Disclosure -->
          <div v-if="doc.client_disclosure_text" class="mt-4 flex gap-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-graphite">
            <ShieldCheck class="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-500" />
            {{ doc.client_disclosure_text }}
          </div>
          <div v-if="doc.statement_descriptor_snapshot" class="mt-1.5 px-1 text-xs text-slate-400">
            Statement descriptor: <span class="font-mono">{{ doc.statement_descriptor_snapshot }}</span>
          </div>

          <!-- Error inline -->
          <p v-if="error" class="mt-3 text-xs text-rose-600">{{ error }}</p>

          <button
            class="mt-6 w-full inline-flex items-center justify-center gap-2 rounded-xl bg-signal px-6 py-3.5 text-sm font-semibold text-white hover:bg-signal/90 disabled:opacity-60 transition-colors"
            type="button"
            :disabled="redirecting"
            @click="pay"
          >
            <Loader2 v-if="redirecting" class="h-4 w-4 animate-spin" />
            <CreditCard v-else class="h-4 w-4" />
            {{ redirecting ? 'Redirecting to checkout…' : `Pay ${money(doc.amount, doc.currency)} securely` }}
          </button>
        </div>

        <p class="text-center text-xs text-slate-400">
          Secured by Stripe · Your card details are never stored on our servers.
        </p>
      </template>

    </div>
  </div>
</template>
