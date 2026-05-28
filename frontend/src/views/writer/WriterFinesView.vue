<script setup lang="ts">
import { onMounted, ref } from "vue";
import { AlertTriangle, CheckCircle2, Loader2, RefreshCw } from "@lucide/vue";
import { finesApi, type FineRecord } from "@/api/fines";
import StatusPill from "@/components/ui/StatusPill.vue";

const fines = ref<FineRecord[]>([]);
const finesLoading = ref(false);
const disputingFineId = ref<number | null>(null);
const disputeReason = ref("");
const disputeError = ref("");
const disputeSubmitting = ref(false);

async function fetchFines() {
  finesLoading.value = true;
  try {
    const { data } = await finesApi.list({ page_size: 50 });
    fines.value = Array.isArray(data) ? data : (data as { results: FineRecord[] }).results ?? [];
  } catch {
    // non-critical
  } finally {
    finesLoading.value = false;
  }
}

function openDisputeForm(fineId: number) {
  disputingFineId.value = fineId;
  disputeReason.value = "";
  disputeError.value = "";
}

function closeDisputeForm() {
  disputingFineId.value = null;
  disputeReason.value = "";
  disputeError.value = "";
}

async function submitDispute(fineId: number) {
  disputeError.value = "";
  if (!disputeReason.value.trim()) {
    disputeError.value = "Please explain why you are disputing this fine.";
    return;
  }
  disputeSubmitting.value = true;
  try {
    const { data } = await finesApi.dispute(fineId, disputeReason.value.trim());
    const idx = fines.value.findIndex((f) => f.id === fineId);
    if (idx !== -1) fines.value[idx] = data;
    closeDisputeForm();
  } catch {
    disputeError.value = "Dispute submission failed. Try again shortly.";
  } finally {
    disputeSubmitting.value = false;
  }
}

function fineStatusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (status === "waived") return "success";
  if (status === "disputed" || status === "escalated" || status === "appealed") return "warning";
  if (status === "issued") return "danger";
  return "neutral";
}

function money(value: string): string {
  const n = Number(value);
  if (Number.isNaN(n)) return value;
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
}

function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

onMounted(fetchFines);
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Fines</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Fines issued against your account. Dispute any fine you believe was applied in error.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
        type="button"
        :disabled="finesLoading"
        @click="fetchFines"
      >
        <Loader2 v-if="finesLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="finesLoading && !fines.length" class="space-y-3">
      <div v-for="n in 4" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5" aria-hidden="true">
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 space-y-2">
            <div class="h-4 w-2/5 rounded bg-slate-200" />
            <div class="h-3 w-1/3 rounded bg-slate-100" />
          </div>
          <div class="h-6 w-20 rounded-full bg-slate-100" />
        </div>
      </div>
    </div>

    <div v-else-if="!fines.length" class="rounded-lg border border-slate-200 bg-white px-6 py-14 text-center">
      <AlertTriangle class="mx-auto h-8 w-8 text-slate-300" />
      <p class="mt-3 text-sm font-medium text-ink">No fines on record</p>
      <p class="mt-1 text-sm text-graphite">Any fines applied to your account will appear here.</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="fine in fines"
        :key="fine.id"
        class="rounded-lg border border-slate-200 bg-white p-5"
      >
        <div class="flex items-start gap-4">
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <p class="text-base font-semibold text-ink">{{ money(fine.amount) }}</p>
              <span v-if="fine.fine_type_name" class="text-sm text-graphite">— {{ fine.fine_type_name }}</span>
            </div>
            <p v-if="fine.order_topic" class="mt-1 text-sm text-graphite">Order: {{ fine.order_topic }}</p>
            <p v-if="fine.reason" class="mt-1 text-sm text-graphite">{{ fine.reason }}</p>
            <p class="mt-1 text-xs text-slate-400">{{ formatDate(fine.imposed_at) }}</p>
          </div>
          <div class="flex shrink-0 flex-col items-end gap-2">
            <StatusPill :label="fine.status" :tone="fineStatusTone(fine.status)" />
            <button
              v-if="fine.can_dispute"
              class="focus-ring text-xs font-semibold text-signal underline-offset-2 hover:underline"
              type="button"
              @click="openDisputeForm(fine.id)"
            >
              Dispute
            </button>
          </div>
        </div>

        <!-- Inline dispute form -->
        <div v-if="disputingFineId === fine.id" class="mt-4 space-y-3 rounded-md border border-amber-200 bg-amber-50 p-4">
          <p class="text-xs font-semibold text-amber-900">Dispute this fine</p>
          <textarea
            v-model="disputeReason"
            class="focus-ring w-full rounded-md border border-amber-200 bg-white px-3 py-2 text-sm"
            rows="3"
            placeholder="Explain why you believe this fine was issued in error…"
          />
          <p v-if="disputeError" class="text-xs text-berry">{{ disputeError }}</p>
          <div class="flex gap-2">
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-ink px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="disputeSubmitting"
              @click="submitDispute(fine.id)"
            >
              <Loader2 v-if="disputeSubmitting" class="h-3 w-3 animate-spin" />
              <CheckCircle2 v-else class="h-3 w-3" />
              Submit dispute
            </button>
            <button
              class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink"
              type="button"
              @click="closeDisputeForm"
            >
              Cancel
            </button>
          </div>
        </div>

        <!-- Existing appeal outcome -->
        <div v-else-if="fine.appeal" class="mt-3 rounded-md bg-slate-50 px-4 py-3">
          <p class="text-xs font-medium text-graphite">
            Dispute
            <span v-if="fine.appeal.accepted === true" class="text-signal"> accepted</span>
            <span v-else-if="fine.appeal.accepted === false" class="text-berry"> rejected</span>
            <span v-else> under review</span>
          </p>
          <p v-if="fine.appeal.resolution_notes" class="mt-1 text-xs text-graphite">{{ fine.appeal.resolution_notes }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
