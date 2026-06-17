<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { AlertTriangle, CheckCircle2, RefreshCw, Search, SlidersHorizontal } from "@lucide/vue";
import { adjustmentsApi } from "@/api/adjustments";
import { useAuthStore } from "@/stores/auth";
import type { AdjustmentStatus, StaffAdjustmentInboxItem } from "@/types/adjustments";

const auth = useAuthStore();
const rows = ref<StaffAdjustmentInboxItem[]>([]);
const count = ref(0);
const next = ref<string | null>(null);
const previous = ref<string | null>(null);
const isLoading = ref(false);
const isMutating = ref(false);
const error = ref("");
const notice = ref("");
const resolvingId = ref<number | null>(null);
const filters = reactive({
  status: "active",
  kind: "",
  escalated: "",
  q: "",
  page: 1,
});
const resolutionForm = reactive({
  resolution: "writer_continue",
  note: "",
});

const attentionCount = computed(() => rows.value.filter((row) => row.requires_staff_attention).length);
const pendingClientCount = computed(() => rows.value.filter((row) => row.status === "pending_client_response").length);
const counteredCount = computed(() => rows.value.filter((row) => row.status === "client_countered").length);

const rolePrefix = computed(() => auth.role || "admin");

onMounted(() => loadInbox());

async function loadInbox(page = filters.page) {
  isLoading.value = true;
  error.value = "";
  notice.value = "";
  try {
    filters.page = page;
    const params = {
      status: filters.status,
      kind: filters.kind || undefined,
      escalated: filters.escalated || undefined,
      q: filters.q || undefined,
      page,
      page_size: 25,
    };
    const { data } = await adjustmentsApi.inbox(params);
    rows.value = data.results ?? [];
    count.value = data.count ?? rows.value.length;
    next.value = data.next;
    previous.value = data.previous;
  } catch {
    error.value = "Unable to load adjustment inbox.";
  } finally {
    isLoading.value = false;
  }
}

function orderPath(item: StaffAdjustmentInboxItem): string {
  return `/${rolePrefix.value}/orders/${item.order_id}`;
}

function statusTone(status: AdjustmentStatus): string {
  if (["funded", "approved_by_staff", "counter_funded_final"].includes(status)) return "border-emerald-200 bg-emerald-50 text-emerald-700";
  if (["declined", "rejected_by_client", "rejected_by_staff", "cancelled", "expired", "reversed"].includes(status)) return "border-rose-200 bg-rose-50 text-rose-700";
  if (["client_countered", "funding_pending", "accepted"].includes(status)) return "border-amber-200 bg-amber-50 text-amber-700";
  return "border-signal/20 bg-signal/10 text-signal";
}

function kindLabel(value: string): string {
  if (value === "scope_increment") return "Scope change";
  if (value === "extra_service") return "Extra service";
  return value.replace(/_/g, " ");
}

function formatStatus(value: string): string {
  return value.replace(/_/g, " ");
}

function formatDate(iso: string | null): string {
  if (!iso) return "Not set";
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function money(value: string | null): string {
  if (!value) return "Pending";
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return value;
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(numeric);
}

function openResolution(item: StaffAdjustmentInboxItem) {
  resolvingId.value = resolvingId.value === item.id ? null : item.id;
  resolutionForm.resolution = "writer_continue";
  resolutionForm.note = "";
  error.value = "";
  notice.value = "";
}

async function resolveEscalation(item: StaffAdjustmentInboxItem) {
  isMutating.value = true;
  error.value = "";
  notice.value = "";
  try {
    await adjustmentsApi.resolveEscalation(item.id, resolutionForm.resolution, resolutionForm.note);
    notice.value = "Escalation resolved.";
    resolvingId.value = null;
    await loadInbox();
  } catch {
    error.value = "Unable to resolve escalation.";
  } finally {
    isMutating.value = false;
  }
}
</script>

<template>
  <div class="space-y-5">
    <div class="flex flex-wrap items-start justify-between gap-4 border-b border-slate-200 pb-5">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Operations</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Adjustment Inbox</h1>
        <p class="mt-2 max-w-3xl text-sm text-graphite">
          Track scope changes, extra services, client counters, funding handoffs, and writer escalations.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-ink"
        type="button"
        :disabled="isLoading"
        @click="loadInbox(1)"
      >
        <RefreshCw class="h-4 w-4" :class="isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <div class="grid gap-3 md:grid-cols-3">
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Needs staff attention</p>
        <p class="mt-2 text-2xl font-semibold text-ink">{{ attentionCount }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Waiting on clients</p>
        <p class="mt-2 text-2xl font-semibold text-ink">{{ pendingClientCount }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Client counters</p>
        <p class="mt-2 text-2xl font-semibold text-ink">{{ counteredCount }}</p>
      </div>
    </div>

    <p v-if="notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{{ notice }}</p>
    <p v-if="error" class="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ error }}</p>

    <section class="rounded-lg border border-slate-200 bg-white">
      <div class="flex flex-wrap items-center gap-3 border-b border-slate-200 px-4 py-3">
        <SlidersHorizontal class="h-4 w-4 text-graphite" />
        <select v-model="filters.status" class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm" @change="loadInbox(1)">
          <option value="active">Active</option>
          <option value="pending_client_response">Pending client response</option>
          <option value="client_countered">Client countered</option>
          <option value="accepted">Accepted</option>
          <option value="funding_pending">Funding pending</option>
          <option value="all">All statuses</option>
        </select>
        <select v-model="filters.kind" class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm" @change="loadInbox(1)">
          <option value="">All kinds</option>
          <option value="scope_increment">Scope changes</option>
          <option value="extra_service">Extra services</option>
        </select>
        <select v-model="filters.escalated" class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm" @change="loadInbox(1)">
          <option value="">All escalation states</option>
          <option value="true">Unresolved escalations</option>
          <option value="false">Not escalated</option>
        </select>
        <form class="relative min-w-[220px] flex-1" @submit.prevent="loadInbox(1)">
          <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
          <input
            v-model.trim="filters.q"
            class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
            placeholder="Search reference, topic, title"
          >
        </form>
      </div>

      <div v-if="isLoading" class="space-y-3 p-4">
        <div v-for="i in 4" :key="i" class="h-24 animate-pulse rounded-md bg-slate-100" />
      </div>

      <div v-else-if="!rows.length" class="flex flex-col items-center gap-3 px-4 py-16 text-center">
        <CheckCircle2 class="h-8 w-8 text-emerald-500" />
        <p class="text-sm font-semibold text-ink">No adjustment requests match these filters.</p>
        <p class="text-xs text-graphite">The queue is clear for this view.</p>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <article v-for="item in rows" :key="item.id" class="p-4">
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <span
                  v-if="item.requires_staff_attention"
                  class="inline-flex items-center gap-1 rounded-full border border-rose-200 bg-rose-50 px-2 py-0.5 text-xs font-semibold text-rose-700"
                >
                  <AlertTriangle class="h-3 w-3" />
                  Staff attention
                </span>
                <span class="rounded-full border px-2 py-0.5 text-xs font-semibold capitalize" :class="statusTone(item.status)">
                  {{ formatStatus(item.status) }}
                </span>
                <span class="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs font-semibold text-graphite">
                  {{ kindLabel(item.adjustment_kind) }}
                </span>
              </div>
              <h2 class="mt-2 truncate text-base font-semibold text-ink">
                {{ item.title || kindLabel(item.adjustment_kind) }}
              </h2>
              <p class="mt-1 text-sm text-graphite">
                <RouterLink class="font-semibold text-signal hover:underline" :to="orderPath(item)">
                  {{ item.order_reference }}
                </RouterLink>
                · {{ item.order_topic }} · {{ item.order_status.replace(/_/g, " ") }}
              </p>
              <p class="mt-1 text-xs text-graphite">
                Client: {{ item.client_name || "Unknown" }}
                · Writer: {{ item.writer_name || "Unassigned" }}
                <template v-if="item.website_name"> · {{ item.website_name }}</template>
              </p>
            </div>

            <div class="min-w-[220px] rounded-md border border-slate-200 bg-slate-50 p-3 text-xs">
              <div class="flex justify-between gap-3">
                <span class="text-graphite">Requested</span>
                <span class="font-semibold text-ink">{{ item.requested_quantity ?? "N/A" }} {{ item.unit_type || "units" }}</span>
              </div>
              <div v-if="item.countered_quantity" class="mt-1 flex justify-between gap-3">
                <span class="text-graphite">Counter</span>
                <span class="font-semibold text-ink">{{ item.countered_quantity }} {{ item.unit_type || "units" }}</span>
              </div>
              <div class="mt-1 flex justify-between gap-3">
                <span class="text-graphite">Writer pay</span>
                <span class="font-semibold text-ink">{{ money(item.counter_writer_compensation_amount || item.request_writer_compensation_amount) }}</span>
              </div>
              <div class="mt-1 flex justify-between gap-3">
                <span class="text-graphite">Updated</span>
                <span class="font-semibold text-ink">{{ formatDate(item.updated_at) }}</span>
              </div>
            </div>
          </div>

          <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p class="text-xs text-graphite">
              {{ item.description || "No additional description supplied." }}
            </p>
            <div class="flex flex-wrap gap-2">
              <button
                v-if="item.requires_staff_attention"
                class="focus-ring inline-flex items-center rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-ink"
                type="button"
                @click="openResolution(item)"
              >
                Resolve escalation
              </button>
              <RouterLink
                class="focus-ring inline-flex items-center rounded-md bg-ink px-3 py-2 text-xs font-semibold text-white"
                :to="orderPath(item)"
              >
                Open order
              </RouterLink>
            </div>
          </div>

          <form
            v-if="resolvingId === item.id"
            class="mt-4 grid gap-3 rounded-md border border-slate-200 bg-slate-50 p-3 md:grid-cols-[220px_minmax(0,1fr)_auto]"
            @submit.prevent="resolveEscalation(item)"
          >
            <select v-model="resolutionForm.resolution" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm">
              <option value="writer_continue">Writer continues</option>
              <option value="reassign_writer">Reassign writer</option>
              <option value="staff_override">Staff override applied</option>
              <option value="cancel_adjustment">Cancel adjustment</option>
            </select>
            <input
              v-model.trim="resolutionForm.note"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
              placeholder="Resolution note"
            >
            <button
              class="focus-ring inline-flex items-center justify-center rounded-md bg-signal px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              type="submit"
              :disabled="isMutating"
            >
              Save
            </button>
          </form>
        </article>
      </div>

      <div v-if="rows.length" class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 px-4 py-3 text-sm">
        <p class="text-graphite">Showing {{ rows.length }} of {{ count }}</p>
        <div class="flex gap-2">
          <button
            class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 font-semibold disabled:opacity-50"
            type="button"
            :disabled="!previous || isLoading"
            @click="loadInbox(filters.page - 1)"
          >
            Previous
          </button>
          <button
            class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 font-semibold disabled:opacity-50"
            type="button"
            :disabled="!next || isLoading"
            @click="loadInbox(filters.page + 1)"
          >
            Next
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
