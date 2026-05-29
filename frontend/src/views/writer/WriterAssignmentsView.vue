<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  BookOpen,
  CheckCircle2,
  Clock3,
  ExternalLink,
  FileText,
  Loader2,
  RefreshCw,
  Send,
  X,
  Zap,
} from "@lucide/vue";
import { RouterLink } from "vue-router";
import EmptyState from "@/components/ui/EmptyState.vue";
import Pagination from "@/components/ui/Pagination.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useBidsStore } from "@/stores/bids";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";
import type { OrderSummary } from "@/types/orders";

const workspace = useWriterWorkspaceStore();
const bids = useBidsStore();

type StatusTab = "active" | "submitted" | "completed";

const activeTab = ref<StatusTab>("active");

const tabDefs: Array<{ key: StatusTab; label: string; statuses: string[] }> = [
  { key: "active", label: "Active", statuses: ["in_progress", "revision_requested"] },
  { key: "submitted", label: "Submitted", statuses: ["submitted", "awaiting_approval"] },
  { key: "completed", label: "Completed", statuses: ["completed", "cancelled", "archived"] },
];

const statusParam = computed(() => tabDefs.find((t) => t.key === activeTab.value)?.statuses.join(","));

function statusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (["completed"].includes(status)) return "success";
  if (["revision_requested"].includes(status)) return "warning";
  if (["cancelled"].includes(status)) return "danger";
  return "neutral";
}

function deadlineLabel(value: string | null | undefined): string {
  if (!value) return "No deadline";
  const h = (new Date(value).getTime() - Date.now()) / 3600000;
  if (h < 0) return `${Math.round(Math.abs(h))}h overdue`;
  if (h < 24) return `${Math.round(h)}h left`;
  return `${Math.round(h / 24)}d left`;
}

function deadlineTone(value: string | null | undefined): "danger" | "warning" | "neutral" {
  if (!value) return "neutral";
  const h = (new Date(value).getTime() - Date.now()) / 3600000;
  if (h < 0) return "danger";
  if (h < 12) return "warning";
  return "neutral";
}

function pagesLabel(order: OrderSummary): string {
  const pages = order.number_of_pages;
  if (!pages) return "—";
  const spacing = order.spacing ? ` (${order.spacing})` : "";
  return `${pages} page${Number(pages) !== 1 ? "s" : ""}${spacing}`;
}

function compensation(order: OrderSummary): string {
  if (!order.writer_compensation) return "—";
  const n = Number(order.writer_compensation);
  if (Number.isNaN(n)) return String(order.writer_compensation);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: order.currency ?? "USD",
  }).format(n);
}

function bidStatusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (status === "accepted") return "success";
  if (status === "pending") return "warning";
  if (status === "rejected" || status === "expired") return "danger";
  return "neutral";
}

function bidMoney(price: string, currency: string): string {
  const n = Number(price);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: currency ?? "USD" }).format(n);
}

async function switchTab(tab: StatusTab) {
  activeTab.value = tab;
  await workspace.fetchAssignments(1, tabDefs.find((t) => t.key === tab)?.statuses.join(","));
}

function goToPage(page: number) {
  void workspace.fetchAssignments(page, statusParam.value);
}

onMounted(() => {
  void workspace.fetchAssignments(1, statusParam.value);
  void bids.loadMyBids();
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">My assignments</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Orders assigned to you across all stages — active work, submitted deliverables, and completed orders.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
        type="button"
        :disabled="workspace.isAssignmentsLoading"
        @click="void workspace.fetchAssignments(workspace.assignmentsPagination.page, statusParam)"
      >
        <Loader2 v-if="workspace.isAssignmentsLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="workspace.assignmentsError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.assignmentsError }}
    </div>
    <div v-if="workspace.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </div>

    <div class="flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
      <button
        v-for="tab in tabDefs"
        :key="tab.key"
        class="flex-1 rounded-md py-2 text-sm font-medium transition-colors"
        :class="activeTab === tab.key
          ? 'bg-white text-ink shadow-sm'
          : 'text-graphite hover:text-ink'"
        type="button"
        @click="switchTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="workspace.isAssignmentsLoading" class="space-y-3">
      <div
        v-for="n in 4"
        :key="n"
        class="animate-pulse rounded-lg border border-slate-200 bg-white p-5"
        aria-hidden="true"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 space-y-2">
            <div class="h-4 w-2/3 rounded bg-slate-200" />
            <div class="h-3 w-1/3 rounded bg-slate-100" />
          </div>
          <div class="h-6 w-20 rounded-full bg-slate-100" />
        </div>
        <div class="mt-4 flex gap-4">
          <div class="h-3 w-16 rounded bg-slate-100" />
          <div class="h-3 w-20 rounded bg-slate-100" />
          <div class="h-3 w-16 rounded bg-slate-100" />
        </div>
      </div>
    </div>

    <div v-else-if="!workspace.assignments.length" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center">
      <EmptyState
        :icon="BookOpen"
        :title="`No ${activeTab} assignments`"
        :message="activeTab === 'active'
          ? 'No orders are currently assigned to you. Browse the available orders pool to pick up work.'
          : 'Nothing here yet.'"
      />
    </div>

    <div v-else class="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <!-- Mobile card list -->
      <div class="divide-y divide-slate-100 sm:hidden">
        <div
          v-for="order in workspace.assignments"
          :key="order.id"
          class="px-4 py-3"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0 flex-1">
              <p class="truncate font-semibold text-ink">#{{ order.id }} {{ order.topic }}</p>
              <p v-if="order.academic_level" class="mt-0.5 text-xs text-graphite">{{ order.academic_level }}</p>
            </div>
            <div class="flex shrink-0 flex-col items-end gap-1">
              <StatusPill :label="order.status" :tone="statusTone(order.status)" />
              <span v-if="order.is_urgent" class="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
                <Zap class="h-3 w-3" />Urgent
              </span>
            </div>
          </div>
          <div class="mt-2 flex flex-wrap items-center gap-3 text-xs text-graphite">
            <span class="flex items-center gap-1"><FileText class="h-3 w-3" />{{ pagesLabel(order) }}</span>
            <span class="flex items-center gap-1">
              <Clock3 class="h-3 w-3" />
              <StatusPill :label="deadlineLabel(order.writer_deadline ?? order.client_deadline)" :tone="deadlineTone(order.writer_deadline ?? order.client_deadline)" />
            </span>
            <span class="font-semibold text-ink">{{ compensation(order) }}</span>
          </div>
          <RouterLink
            class="focus-ring mt-3 inline-flex w-full items-center justify-center gap-1.5 rounded-md border border-slate-200 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
            :to="`/writer/orders/${order.id}`"
          >
            <ExternalLink class="h-3 w-3" />
            Open order
          </RouterLink>
        </div>
      </div>

      <!-- Desktop table -->
      <div class="hidden overflow-x-auto sm:block">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-3 py-2">Order</th>
              <th class="px-3 py-2">Status</th>
              <th class="px-3 py-2">Pages</th>
              <th class="px-3 py-2">Deadline</th>
              <th class="px-3 py-2 text-right">Compensation</th>
              <th class="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="order in workspace.assignments"
              :key="order.id"
              class="hover:bg-slate-50"
            >
              <td class="px-3 py-2.5">
                <div class="flex items-center gap-2">
                  <p class="font-semibold text-ink">#{{ order.id }} {{ order.topic }}</p>
                  <span
                    v-if="order.is_urgent"
                    class="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700"
                  >
                    <Zap class="h-3 w-3" />
                    Urgent
                  </span>
                </div>
                <p v-if="order.academic_level" class="mt-0.5 text-xs text-graphite">
                  {{ order.academic_level }}
                </p>
              </td>
              <td class="px-3 py-2.5">
                <StatusPill :label="order.status" :tone="statusTone(order.status)" />
              </td>
              <td class="px-3 py-2.5 text-graphite">
                <div class="flex items-center gap-1.5">
                  <FileText class="h-3.5 w-3.5 shrink-0 text-slate-400" />
                  {{ pagesLabel(order) }}
                </div>
              </td>
              <td class="px-3 py-2.5">
                <div class="flex items-center gap-1.5">
                  <Clock3 class="h-3.5 w-3.5 shrink-0 text-slate-400" />
                  <StatusPill
                    :label="deadlineLabel(order.writer_deadline ?? order.client_deadline)"
                    :tone="deadlineTone(order.writer_deadline ?? order.client_deadline)"
                  />
                </div>
              </td>
              <td class="px-3 py-2.5 text-right font-semibold text-ink">
                {{ compensation(order) }}
              </td>
              <td class="px-3 py-2.5 text-right">
                <RouterLink
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
                  :to="`/writer/orders/${order.id}`"
                >
                  <ExternalLink class="h-3 w-3" />
                  Open
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Pagination
        :page="workspace.assignmentsPagination.page"
        :page-size="workspace.assignmentsPagination.pageSize"
        :count="workspace.assignmentsPagination.count"
        @update:page="goToPage"
      />
    </div>
    <!-- My bids -->
    <section class="rounded-lg border border-slate-200 bg-white">
      <div class="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
        <div class="flex items-center gap-2">
          <Send class="h-4 w-4 text-signal" />
          <h2 class="text-base font-semibold text-ink">My bids</h2>
        </div>
        <button
          class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink"
          type="button"
          :disabled="bids.isLoading"
          @click="bids.loadMyBids()"
        >
          <Loader2 v-if="bids.isLoading" class="h-3 w-3 animate-spin" />
          <RefreshCw v-else class="h-3 w-3" />
          Refresh
        </button>
      </div>

      <div v-if="bids.isLoading && !bids.myBids.length" class="px-5 py-8 text-center text-sm text-graphite">
        Loading bids…
      </div>

      <div v-else-if="!bids.myBids.length" class="px-5 py-8">
        <EmptyState
          :icon="Send"
          title="No bids yet"
          message="Bids you submit on available orders will appear here."
        />
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div
          v-for="bid in bids.myBids"
          :key="bid.id"
          class="flex items-center gap-4 px-5 py-4"
        >
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-ink">
              #{{ bid.order_id }} {{ bid.order_topic }}
            </p>
            <p class="mt-0.5 text-xs text-graphite">
              {{ bidMoney(bid.price, bid.currency) }} · {{ bid.delivery_hours }}h delivery
              <template v-if="bid.pitch">· "{{ bid.pitch.slice(0, 60) }}{{ bid.pitch.length > 60 ? '…' : '' }}"</template>
            </p>
            <p v-if="bid.rejection_reason && bid.status === 'rejected'" class="mt-0.5 text-xs text-berry">
              {{ bid.rejection_reason }}
            </p>
          </div>
          <StatusPill :label="bid.status" :tone="bidStatusTone(bid.status)" />
          <button
            v-if="bid.status === 'pending'"
            class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:border-rose-300 hover:text-berry disabled:opacity-50"
            type="button"
            :disabled="bids.isSaving"
            @click="bids.withdrawBid(bid.id)"
          >
            <Loader2 v-if="bids.isSaving" class="h-3 w-3 animate-spin" />
            <X v-else class="h-3 w-3" />
            Withdraw
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
