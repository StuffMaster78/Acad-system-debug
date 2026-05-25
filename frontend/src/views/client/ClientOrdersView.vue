<script setup lang="ts">
import { onMounted } from "vue";
import { RouterLink } from "vue-router";
import { ClipboardList, Plus } from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useOrderStore } from "@/stores/orders";

const orders = useOrderStore();

onMounted(() => {
  orders.fetchOrders().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-5">
    <section class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Client</p>
        <h1 class="mt-2 text-3xl font-semibold">Orders</h1>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-graphite">
          Track active work, payments, delivery status, revisions, and archived files.
        </p>
      </div>
      <RouterLink
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white"
        to="/client/new-order"
      >
        <Plus class="h-4 w-4" />
        New order
      </RouterLink>
    </section>

    <p
      v-if="orders.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ orders.error }} Showing the workspace shell while the API is unavailable.
    </p>

    <div v-if="orders.orders.length" class="overflow-hidden rounded-md border border-slate-200 bg-white shadow-panel">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
          <tr>
            <th class="px-4 py-3">Order</th>
            <th class="px-4 py-3">Status</th>
            <th class="px-4 py-3">Payment</th>
            <th class="px-4 py-3">Deadline</th>
            <th class="px-4 py-3 text-right">Total</th>
            <th class="px-4 py-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="order in orders.orders" :key="order.id">
            <td class="px-4 py-4">
              <p class="font-semibold text-ink">#{{ order.id }} {{ order.topic }}</p>
              <p class="mt-1 text-xs text-graphite">{{ order.service_code || "paper" }}</p>
            </td>
            <td class="px-4 py-4">
              <StatusPill :label="order.status" />
            </td>
            <td class="px-4 py-4 text-graphite">{{ order.payment_status || "pending" }}</td>
            <td class="px-4 py-4 text-graphite">{{ order.client_deadline || "Not set" }}</td>
            <td class="px-4 py-4 text-right font-semibold">
              {{ order.currency || "USD" }} {{ order.total_price || "0.00" }}
            </td>
            <td class="px-4 py-4 text-right">
              <RouterLink
                class="focus-ring inline-flex items-center justify-center rounded-md border border-slate-300 px-3 py-2 text-xs font-semibold text-ink hover:bg-slate-50"
                :to="`/client/orders/${order.id}`"
              >
                Open
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <EmptyState
      v-else
      :icon="ClipboardList"
      title="No orders loaded"
      message="Create the first order or connect to the backend with a client account to load existing work."
    />
  </div>
</template>
