<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import { Sparkles, Search } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import type { SpecialOrderStatus } from "@/types/specialOrders";

const store = useSpecialOrdersStore();
const router = useRouter();

onMounted(() => store.loadOrders());

const search = ref("");
const statusFilter = ref<SpecialOrderStatus | "">("");

const statusLabel: Record<SpecialOrderStatus, string> = {
  draft: "Draft",
  pending_quote: "Awaiting Quote",
  quote_sent: "Quote Sent",
  quote_accepted: "Accepted",
  quote_rejected: "Rejected",
  in_progress: "In Progress",
  completed: "Completed",
  cancelled: "Cancelled",
};

const statusClass: Record<SpecialOrderStatus, string> = {
  draft: "bg-slate-100 text-graphite",
  pending_quote: "bg-amber-100 text-amber-700",
  quote_sent: "bg-blue-100 text-blue-700",
  quote_accepted: "bg-emerald-100 text-emerald-700",
  quote_rejected: "bg-rose-100 text-rose-700",
  in_progress: "bg-purple-100 text-purple-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
};

const filtered = computed(() => {
  let list = store.orders;
  if (statusFilter.value) list = list.filter((o) => o.status === statusFilter.value);
  if (search.value.trim()) {
    const q = search.value.toLowerCase();
    list = list.filter(
      (o) =>
        o.title.toLowerCase().includes(q) ||
        o.reference.toLowerCase().includes(q) ||
        o.client_username.toLowerCase().includes(q),
    );
  }
  return list;
});

function progress(total: number, done: number) {
  if (!total) return 0;
  return Math.round((done / total) * 100);
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-5xl space-y-6">

      <div>
        <h1 class="text-xl font-bold text-ink">Special Orders</h1>
        <p class="text-sm text-graphite">Custom quote-based and milestone projects</p>
      </div>

      <!-- Filters -->
      <div class="flex gap-3">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-2.5 size-4 text-graphite" />
          <input
            v-model="search"
            placeholder="Search by title, reference, or client…"
            class="w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 py-2 text-sm focus-ring"
          />
        </div>
        <select
          v-model="statusFilter"
          class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-graphite focus-ring"
        >
          <option value="">All statuses</option>
          <option v-for="s in Object.keys(statusLabel)" :key="s" :value="s">{{ statusLabel[s as SpecialOrderStatus] }}</option>
        </select>
      </div>

      <div v-if="store.isLoading" class="py-16 text-center text-graphite animate-pulse">Loading…</div>

      <div v-else-if="!filtered.length" class="py-16 text-center rounded-xl border border-slate-200 bg-white shadow-panel">
        <Sparkles class="mx-auto mb-3 size-10 text-slate-300" />
        <p class="text-graphite">No special orders found.</p>
      </div>

      <div v-else class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-panel">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-5 py-3 text-left">Reference</th>
              <th class="px-5 py-3 text-left">Title</th>
              <th class="px-5 py-3 text-left">Client</th>
              <th class="px-5 py-3 text-left">Writer</th>
              <th class="px-5 py-3 text-center">Milestones</th>
              <th class="px-5 py-3 text-right">Quote</th>
              <th class="px-5 py-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr
              v-for="order in filtered"
              :key="order.id"
              class="cursor-pointer hover:bg-slate-50 transition-colors"
              @click="router.push(`/admin/special-orders/${order.id}`)"
            >
              <td class="px-5 py-3 font-mono text-xs text-graphite">{{ order.reference }}</td>
              <td class="px-5 py-3 font-medium text-ink max-w-xs truncate">{{ order.title }}</td>
              <td class="px-5 py-3 text-graphite">{{ order.client_username }}</td>
              <td class="px-5 py-3 text-graphite">{{ order.writer_username ?? '—' }}</td>
              <td class="px-5 py-3">
                <div v-if="order.total_milestones" class="flex items-center gap-2">
                  <div class="flex-1 h-1.5 rounded-full bg-slate-100">
                    <div class="h-full rounded-full bg-berry" :style="{ width: `${progress(order.total_milestones, order.completed_milestones)}%` }" />
                  </div>
                  <span class="text-xs text-graphite whitespace-nowrap">{{ order.completed_milestones }}/{{ order.total_milestones }}</span>
                </div>
                <span v-else class="text-xs text-graphite">—</span>
              </td>
              <td class="px-5 py-3 text-right font-semibold text-ink">
                {{ order.quoted_price ? `$${order.quoted_price}` : '—' }}
              </td>
              <td class="px-5 py-3 text-center">
                <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass[order.status]">
                  {{ statusLabel[order.status] }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>
