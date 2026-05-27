<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { Search, CheckCircle, XCircle, Star, Clock, DollarSign } from "@lucide/vue";
import { useBidsStore } from "@/stores/bids";
import type { BidStatus } from "@/types/bids";

const store = useBidsStore();

onMounted(() => store.loadAllBids());

const search = ref("");
const statusFilter = ref<BidStatus | "">("");

const statusLabel: Record<BidStatus, string> = {
  pending: "Pending",
  accepted: "Accepted",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
  expired: "Expired",
};

const statusClass: Record<BidStatus, string> = {
  pending: "bg-amber-100 text-amber-700",
  accepted: "bg-emerald-100 text-emerald-700",
  rejected: "bg-rose-100 text-rose-700",
  withdrawn: "bg-slate-100 text-graphite",
  expired: "bg-slate-100 text-slate-400",
};

// Group bids by order_id
const grouped = computed(() => {
  let list = store.allBids;
  if (statusFilter.value) list = list.filter((b) => b.status === statusFilter.value);
  if (search.value.trim()) {
    const q = search.value.toLowerCase();
    list = list.filter(
      (b) =>
        b.order_topic.toLowerCase().includes(q) ||
        b.writer_username.toLowerCase().includes(q) ||
        String(b.order_id).includes(q),
    );
  }

  const map = new Map<number, typeof list>();
  for (const bid of list) {
    if (!map.has(bid.order_id)) map.set(bid.order_id, []);
    map.get(bid.order_id)!.push(bid);
  }
  return [...map.entries()].map(([orderId, bids]) => ({
    orderId,
    topic: bids[0].order_topic,
    bids,
    pendingCount: bids.filter((b) => b.status === "pending").length,
  }));
});

const rejectingBidId = ref<number | null>(null);
const rejectReason = ref("");

function startReject(bidId: number) {
  rejectingBidId.value = bidId;
  rejectReason.value = "";
}

async function confirmReject(orderId: number, bidId: number) {
  await store.rejectBid(orderId, bidId, rejectReason.value || undefined);
  rejectingBidId.value = null;
}
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Writer Bids</h1>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-graphite">
          Review writer bids by order. Accept the best fit or reject bids with a note.
        </p>
      </div>
    </section>

    <div v-if="store.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ store.notice }}
    </div>
    <div v-if="store.error" class="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
      {{ store.error }}
    </div>

    <!-- Filters -->
    <div class="flex gap-3">
      <div class="relative flex-1">
        <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          v-model="search"
          class="focus-ring w-full rounded-md border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm"
          placeholder="Search by order topic, writer, or ID…"
        />
      </div>
      <select v-model="statusFilter" class="focus-ring rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-graphite">
        <option value="">All statuses</option>
        <option v-for="s in ['pending','accepted','rejected','withdrawn','expired']" :key="s" :value="s">
          {{ statusLabel[s as BidStatus] }}
        </option>
      </select>
    </div>

    <div v-if="store.isLoading" class="py-16 text-center text-graphite animate-pulse">Loading bids…</div>

    <div v-else-if="!grouped.length" class="py-16 text-center rounded-lg border border-slate-200 bg-white shadow-panel">
      <DollarSign class="mx-auto mb-3 h-10 w-10 text-slate-300" />
      <p class="text-graphite">No bids found.</p>
    </div>

    <div v-else class="space-y-6">
      <section
        v-for="group in grouped"
        :key="group.orderId"
        class="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-panel"
      >
        <!-- Order header -->
        <div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-5 py-3">
          <div>
            <span class="text-xs font-mono text-graphite">#{{ group.orderId }}</span>
            <h2 class="text-sm font-semibold text-ink">{{ group.topic }}</h2>
          </div>
          <span
            class="rounded-full px-2 py-0.5 text-xs font-semibold"
            :class="group.pendingCount > 0 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-graphite'"
          >
            {{ group.pendingCount }} pending · {{ group.bids.length }} total
          </span>
        </div>

        <!-- Bid rows -->
        <div class="divide-y divide-slate-100">
          <div v-for="bid in group.bids" :key="bid.id" class="px-5 py-4">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-ink">{{ bid.writer_username }}</span>
                  <div v-if="bid.writer_rating" class="flex items-center gap-0.5 text-xs text-amber-500">
                    <Star class="h-3.5 w-3.5 fill-current" />
                    {{ bid.writer_rating }}
                  </div>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass[bid.status]">
                    {{ statusLabel[bid.status] }}
                  </span>
                </div>

                <div class="mt-2 flex flex-wrap gap-4 text-sm">
                  <span class="flex items-center gap-1 font-semibold text-ink">
                    <DollarSign class="h-3.5 w-3.5 text-slate-400" />
                    ${{ bid.price }}
                  </span>
                  <span class="flex items-center gap-1 text-graphite">
                    <Clock class="h-3.5 w-3.5 text-slate-400" />
                    {{ bid.delivery_hours }}h delivery
                  </span>
                </div>

                <p v-if="bid.pitch" class="mt-2 text-sm text-graphite italic">
                  "{{ bid.pitch }}"
                </p>
                <p class="mt-1 text-xs text-slate-400">
                  {{ new Date(bid.created_at).toLocaleString() }}
                </p>
                <p v-if="bid.rejection_reason" class="mt-1 text-xs text-rose-600">
                  Rejected: {{ bid.rejection_reason }}
                </p>
              </div>

              <!-- Actions (only for pending bids) -->
              <div v-if="bid.status === 'pending'" class="shrink-0 space-y-2">
                <button
                  class="flex w-full items-center gap-1.5 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800 hover:bg-emerald-100 disabled:opacity-60"
                  :disabled="store.isSaving"
                  @click="store.acceptBid(bid.order_id, bid.id)"
                >
                  <CheckCircle class="h-3.5 w-3.5" />
                  Accept bid
                </button>

                <div v-if="rejectingBidId === bid.id" class="space-y-1">
                  <input
                    v-model="rejectReason"
                    placeholder="Reason (optional)"
                    class="focus-ring h-8 w-full rounded border border-slate-200 px-2 text-xs"
                  />
                  <div class="flex gap-1">
                    <button
                      class="flex-1 rounded bg-rose-600 py-1 text-xs font-semibold text-white hover:bg-rose-700 disabled:opacity-60"
                      :disabled="store.isSaving"
                      @click="confirmReject(bid.order_id, bid.id)"
                    >Confirm</button>
                    <button
                      class="rounded border border-slate-200 px-2 py-1 text-xs text-graphite hover:text-ink"
                      @click="rejectingBidId = null"
                    >✕</button>
                  </div>
                </div>
                <button
                  v-else
                  class="flex w-full items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:text-rose-600"
                  @click="startReject(bid.id)"
                >
                  <XCircle class="h-3.5 w-3.5" />
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

  </div>
</template>
