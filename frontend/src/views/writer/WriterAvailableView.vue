<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  BookOpen,
  CheckCircle2,
  Clock3,
  DollarSign,
  FileText,
  GraduationCap,
  Loader2,
  Quote,
  RefreshCw,
  Search,
  Send,
  Tag,
  Zap,
} from "@lucide/vue";
import Pagination from "@/components/ui/Pagination.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";
import { useBidsStore } from "@/stores/bids";
import type { OrderSummary } from "@/types/orders";

const workspace = useWriterWorkspaceStore();
const bids = useBidsStore();

const searchQuery = ref("");
const urgentOnly = ref(false);
const expandedOrderId = ref<number | null>(null);
const interestMessage = ref("");

const filteredOrders = computed(() => {
  let list = workspace.poolOrders;
  if (urgentOnly.value) list = list.filter((o) => o.is_urgent);
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(
      (o) =>
        o.topic.toLowerCase().includes(q) ||
        String(o.academic_level ?? "").toLowerCase().includes(q) ||
        String(o.subject ?? "").toLowerCase().includes(q),
    );
  }
  return list;
});

function deadlineLabel(value: string | null | undefined): string {
  if (!value) return "No deadline";
  const ms = new Date(value).getTime() - Date.now();
  const h = Math.round(ms / 3600000);
  if (h < 0) return `${Math.abs(h)}h overdue`;
  if (h < 24) return `${h}h left`;
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

function compensationLabel(order: OrderSummary): string {
  if (!order.writer_compensation) return "—";
  const n = Number(order.writer_compensation);
  if (Number.isNaN(n)) return String(order.writer_compensation);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: order.currency ?? "USD" }).format(n);
}

function toggleInterestForm(orderId: number) {
  if (expandedOrderId.value === orderId) {
    expandedOrderId.value = null;
    interestMessage.value = "";
    bids.closeBidForm();
  } else {
    expandedOrderId.value = orderId;
    interestMessage.value = "";
    bids.openBidForm(orderId);
  }
}

async function submitBid(order: OrderSummary) {
  await bids.submitBid();
  if (!bids.error) {
    expandedOrderId.value = null;
    interestMessage.value = "";
  }
}

async function submitInterest(order: OrderSummary) {
  await workspace.expressInterest(order.id, interestMessage.value);
  if (!workspace.error) {
    expandedOrderId.value = null;
    interestMessage.value = "";
  }
}

async function handleTakeOrder(order: OrderSummary) {
  await workspace.takeOrder(order.id);
  if (!workspace.error) {
    workspace.removePoolOrder(order.id);
  }
}

function goToPoolPage(page: number) {
  void workspace.fetchPoolOrders(page);
}

onMounted(() => {
  void workspace.fetchPoolOrders(1);
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer marketplace</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Available orders</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Open pool orders ready for staffing. Express interest or take an order directly.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
        type="button"
        :disabled="workspace.isPoolLoading"
        @click="workspace.fetchPoolOrders()"
      >
        <Loader2 v-if="workspace.isPoolLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="workspace.poolError" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.poolError }}
    </div>
    <div v-if="workspace.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </div>
    <div v-if="workspace.error" class="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900">
      {{ workspace.error }}
    </div>

    <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div class="relative flex-1">
        <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          class="focus-ring w-full rounded-md border border-slate-300 py-2 pl-9 pr-3 text-sm"
          placeholder="Search by topic, level, or subject…"
          type="search"
        />
      </div>
      <label class="inline-flex cursor-pointer items-center gap-2 text-sm font-medium text-ink">
        <input v-model="urgentOnly" class="rounded border-slate-300" type="checkbox" />
        Urgent only
      </label>
      <span class="text-sm text-graphite">
        {{ filteredOrders.length }} order{{ filteredOrders.length !== 1 ? "s" : "" }}
      </span>
    </div>

    <div v-if="workspace.isPoolLoading" class="space-y-3">
      <div
        v-for="n in 4"
        :key="n"
        class="animate-pulse rounded-lg border border-slate-200 bg-white p-5"
        aria-hidden="true"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 space-y-2">
            <div class="h-4 w-2/3 rounded bg-slate-200" />
            <div class="h-3 w-1/2 rounded bg-slate-100" />
          </div>
          <div class="h-6 w-16 rounded-full bg-slate-100" />
        </div>
        <div class="mt-4 flex gap-4">
          <div class="h-3 w-20 rounded bg-slate-100" />
          <div class="h-3 w-20 rounded bg-slate-100" />
          <div class="h-3 w-20 rounded bg-slate-100" />
        </div>
      </div>
    </div>

    <div v-else-if="!filteredOrders.length" class="rounded-lg border border-slate-200 bg-white px-6 py-12 text-center">
      <BookOpen class="mx-auto h-8 w-8 text-slate-300" />
      <p class="mt-3 text-sm font-medium text-ink">No available orders</p>
      <p class="mt-1 text-sm text-graphite">
        {{ searchQuery || urgentOnly ? "Try clearing the filters." : "Check back shortly — new orders appear here as they open." }}
      </p>
    </div>

    <div v-else class="space-y-3">
      <article
        v-for="order in filteredOrders"
        :key="order.id"
        class="rounded-lg border border-slate-200 bg-white transition-shadow hover:shadow-md"
      >
        <div class="p-5">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <h2 class="truncate text-base font-semibold text-ink">
                  #{{ order.id }} {{ order.topic }}
                </h2>
                <span
                  v-if="order.is_urgent"
                  class="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700"
                >
                  <Zap class="h-3 w-3" />
                  Urgent
                </span>
              </div>
              <p v-if="order.order_instructions || order.instructions" class="mt-1 line-clamp-2 text-sm text-graphite">
                {{ order.order_instructions ?? order.instructions }}
              </p>
            </div>
            <div class="shrink-0">
              <StatusPill
                :label="deadlineLabel(order.writer_deadline)"
                :tone="deadlineTone(order.writer_deadline)"
              />
            </div>
          </div>

          <dl class="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-sm">
            <div v-if="order.subject_name || order.subject" class="flex items-center gap-1.5 text-graphite">
              <GraduationCap class="h-3.5 w-3.5 shrink-0 text-slate-400" />
              <dt class="sr-only">Subject</dt>
              <dd>{{ order.subject_name ?? order.subject }}</dd>
            </div>
            <div v-if="order.paper_type_name || order.paper_type" class="flex items-center gap-1.5 text-graphite">
              <Tag class="h-3.5 w-3.5 shrink-0 text-slate-400" />
              <dt class="sr-only">Paper type</dt>
              <dd>{{ order.paper_type_name ?? order.paper_type }}</dd>
            </div>
            <div v-if="order.formatting_style_name || order.formatting_style" class="flex items-center gap-1.5 text-graphite">
              <Quote class="h-3.5 w-3.5 shrink-0 text-slate-400" />
              <dt class="sr-only">Citation</dt>
              <dd>{{ order.formatting_style_name ?? order.formatting_style }}</dd>
            </div>
            <div v-if="order.academic_level" class="flex items-center gap-1.5 text-graphite">
              <BookOpen class="h-3.5 w-3.5 shrink-0 text-slate-400" />
              <dt class="sr-only">Level</dt>
              <dd>{{ order.academic_level }}</dd>
            </div>
            <div class="flex items-center gap-1.5 text-graphite">
              <FileText class="h-3.5 w-3.5 shrink-0 text-slate-400" />
              <dt class="sr-only">Pages</dt>
              <dd>{{ pagesLabel(order) }}</dd>
            </div>
            <div v-if="order.writer_deadline" class="flex items-center gap-1.5 text-graphite">
              <Clock3 class="h-3.5 w-3.5 shrink-0 text-slate-400" />
              <dt class="sr-only">Deadline</dt>
              <dd>
                {{
                  new Intl.DateTimeFormat("en", {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  }).format(new Date(order.writer_deadline))
                }}
              </dd>
            </div>
            <div v-if="order.writer_compensation" class="ml-auto font-semibold text-ink">
              {{ compensationLabel(order) }}
            </div>
          </dl>
        </div>

        <div class="border-t border-slate-100 px-5 py-3">
          <!-- Collapsed: action buttons -->
          <div v-if="expandedOrderId !== order.id" class="flex flex-wrap gap-2">
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating || bids.isSaving"
              @click="toggleInterestForm(order.id)"
            >
              <DollarSign class="h-3.5 w-3.5" />
              Submit a bid
            </button>
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-ink disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating"
              @click="handleTakeOrder(order)"
            >
              <Loader2 v-if="workspace.isMutating" class="h-3.5 w-3.5 animate-spin" />
              <CheckCircle2 v-else class="h-3.5 w-3.5" />
              Take order directly
            </button>
          </div>

          <!-- Expanded: full spec summary + bid form -->
          <div v-else class="space-y-3">
            <!-- Full order spec recap so writers have all info before pricing -->
            <div class="rounded-md border border-slate-100 bg-slate-50 p-3 text-sm">
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-graphite">Order specifications</p>
              <dl class="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs sm:grid-cols-3">
                <div v-if="order.paper_type_name ?? order.paper_type">
                  <dt class="text-graphite">Paper type</dt>
                  <dd class="font-medium text-ink">{{ order.paper_type_name ?? order.paper_type }}</dd>
                </div>
                <div v-if="order.subject_name ?? order.subject">
                  <dt class="text-graphite">Subject</dt>
                  <dd class="font-medium text-ink">{{ order.subject_name ?? order.subject }}</dd>
                </div>
                <div v-if="order.academic_level">
                  <dt class="text-graphite">Academic level</dt>
                  <dd class="font-medium text-ink">{{ order.academic_level }}</dd>
                </div>
                <div>
                  <dt class="text-graphite">Pages / qty</dt>
                  <dd class="font-medium text-ink">{{ pagesLabel(order) }}</dd>
                </div>
                <div v-if="order.formatting_style_name ?? order.formatting_style">
                  <dt class="text-graphite">Citation</dt>
                  <dd class="font-medium text-ink">{{ order.formatting_style_name ?? order.formatting_style }}</dd>
                </div>
                <div v-if="order.number_of_refereces">
                  <dt class="text-graphite">Sources</dt>
                  <dd class="font-medium text-ink">{{ order.number_of_refereces }}</dd>
                </div>
              </dl>
              <div v-if="order.order_instructions ?? order.instructions" class="mt-2 border-t border-slate-200 pt-2">
                <dt class="mb-1 text-xs text-graphite">Instructions</dt>
                <dd class="line-clamp-3 text-xs leading-5 text-ink">{{ order.order_instructions ?? order.instructions }}</dd>
              </div>
            </div>

            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Your Bid</p>

            <div class="grid grid-cols-2 gap-3">
              <label class="block">
                <span class="text-xs font-medium text-graphite">Your price ($) *</span>
                <div class="relative mt-1">
                  <DollarSign class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
                  <input
                    v-model="bids.bidForm.price"
                    type="number"
                    min="1"
                    step="0.01"
                    placeholder="e.g. 45.00"
                    class="focus-ring h-9 w-full rounded-md border border-slate-300 pl-8 pr-3 text-sm"
                  />
                </div>
              </label>
              <label class="block">
                <span class="text-xs font-medium text-graphite">Delivery time *</span>
                <select v-model.number="bids.bidForm.delivery_hours" class="focus-ring mt-1 h-9 w-full rounded-md border border-slate-300 px-3 text-sm">
                  <option :value="6">6 hours</option>
                  <option :value="12">12 hours</option>
                  <option :value="24">24 hours</option>
                  <option :value="48">48 hours</option>
                  <option :value="72">3 days</option>
                  <option :value="120">5 days</option>
                </select>
              </label>
            </div>

            <label class="block">
              <span class="text-xs font-medium text-graphite">Pitch message (optional)</span>
              <textarea
                v-model="bids.bidForm.pitch"
                class="focus-ring mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                rows="2"
                placeholder="Why are you the best fit for this order? Keep it brief."
              />
            </label>

            <p v-if="bids.error" class="text-xs text-rose-600">{{ bids.error }}</p>

            <div class="flex gap-2">
              <button
                class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
                type="button"
                :disabled="bids.isSaving || !bids.bidForm.price"
                @click="submitBid(order)"
              >
                <Loader2 v-if="bids.isSaving" class="h-3.5 w-3.5 animate-spin" />
                <Send v-else class="h-3.5 w-3.5" />
                Submit bid
              </button>
              <button
                class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-ink"
                type="button"
                @click="toggleInterestForm(order.id)"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </article>
    </div>

    <Pagination
      v-if="!searchQuery && !urgentOnly"
      :page="workspace.poolPagination.page"
      :page-size="workspace.poolPagination.pageSize"
      :count="workspace.poolPagination.count"
      @update:page="goToPoolPage"
    />
  </div>
</template>
