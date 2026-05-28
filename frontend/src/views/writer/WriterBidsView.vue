<script setup lang="ts">
import { onMounted } from "vue";
import { Loader2, RefreshCw, Send, X } from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useBidsStore } from "@/stores/bids";
import type { Bid } from "@/types/bids";

const bids = useBidsStore();

function bidStatusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (status === "accepted") return "success";
  if (status === "pending") return "warning";
  if (status === "rejected" || status === "expired") return "danger";
  return "neutral";
}

function money(bid: Bid): string {
  const n = Number(bid.price);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: bid.currency ?? "USD" }).format(n);
}

function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

onMounted(() => bids.loadMyBids());
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">My Bids</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Bids submitted on available orders — track status and withdraw pending ones.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
        type="button"
        :disabled="bids.isLoading"
        @click="bids.loadMyBids()"
      >
        <Loader2 v-if="bids.isLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="bids.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ bids.error }}
    </div>

    <div v-if="bids.isLoading && !bids.myBids.length" class="space-y-3">
      <div v-for="n in 4" :key="n" class="animate-pulse rounded-lg border border-slate-200 bg-white p-5" aria-hidden="true">
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 space-y-2">
            <div class="h-4 w-2/3 rounded bg-slate-200" />
            <div class="h-3 w-1/3 rounded bg-slate-100" />
          </div>
          <div class="h-6 w-20 rounded-full bg-slate-100" />
        </div>
      </div>
    </div>

    <div v-else-if="!bids.myBids.length" class="rounded-lg border border-slate-200 bg-white px-6 py-14 text-center">
      <EmptyState
        :icon="Send"
        title="No bids yet"
        message="Bids you submit on available orders will appear here."
      />
    </div>

    <div v-else class="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
          <tr>
            <th class="px-3 py-2">Order</th>
            <th class="px-3 py-2">Price</th>
            <th class="px-3 py-2">Delivery</th>
            <th class="px-3 py-2">Submitted</th>
            <th class="px-3 py-2">Status</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="bid in bids.myBids" :key="bid.id" class="hover:bg-slate-50">
            <td class="px-3 py-2.5">
              <p class="font-semibold text-ink">#{{ bid.order_id }} {{ bid.order_topic }}</p>
              <p v-if="bid.pitch" class="mt-0.5 max-w-xs truncate text-xs text-graphite">{{ bid.pitch }}</p>
              <p v-if="bid.rejection_reason && bid.status === 'rejected'" class="mt-0.5 text-xs text-berry">
                {{ bid.rejection_reason }}
              </p>
            </td>
            <td class="px-3 py-2.5 font-semibold text-ink">{{ money(bid) }}</td>
            <td class="px-3 py-2.5 text-graphite">{{ bid.delivery_hours }}h</td>
            <td class="px-3 py-2.5 text-graphite">{{ formatDate(bid.created_at) }}</td>
            <td class="px-3 py-2.5">
              <StatusPill :label="bid.status" :tone="bidStatusTone(bid.status)" />
            </td>
            <td class="px-3 py-2.5 text-right">
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
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
  </div>
</template>
