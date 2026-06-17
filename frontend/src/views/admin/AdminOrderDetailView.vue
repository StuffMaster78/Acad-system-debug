<script setup lang="ts">
import { computed } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { User } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { useOrderStore } from "@/stores/orders";
import { useWebsitesStore } from "@/stores/websites";
import OrderDetailPage from "@/components/orders/detail/OrderDetailPage.vue";

const route = useRoute();
const auth = useAuthStore();
const orders = useOrderStore();
const websites = useWebsitesStore();

const orderId = computed(() => Number(route.params.id));
const role = computed(() => (auth.role === "superadmin" ? "superadmin" : "admin") as "admin" | "superadmin");

const order = computed(() => orders.selectedOrder);

const clientProfileRoute = computed(() => {
  if (!order.value?.client) return null;
  const prefix = role.value === "superadmin" ? "/superadmin" : "/admin";
  return `${prefix}/clients/${order.value.client}`;
});

const websiteLabel = computed(() => {
  if (!order.value?.website) return null;
  return websites.labelById(order.value.website) || `Site #${order.value.website}`;
});
</script>

<template>
  <div class="space-y-4">
    <!-- Admin client identity strip — shows real email, username, registration ID -->
    <div
      v-if="order && (order.client_email || order.client_username || order.client_registration_id)"
      class="rounded-lg border border-violet-100 bg-violet-50 px-5 py-4"
    >
      <div class="mb-3 flex items-center gap-2">
        <User class="h-4 w-4 text-violet-600" />
        <h3 class="text-sm font-semibold text-ink">Client</h3>
        <RouterLink
          v-if="clientProfileRoute"
          :to="clientProfileRoute"
          class="ml-auto text-xs font-semibold text-violet-700 hover:underline"
        >
          View profile →
        </RouterLink>
      </div>
      <dl class="grid gap-x-6 gap-y-2 sm:grid-cols-2 lg:grid-cols-4">
        <div v-if="order.client_registration_id">
          <dt class="text-xs font-medium text-graphite">Client ID</dt>
          <dd class="mt-0.5 font-mono text-sm font-semibold text-ink">{{ order.client_registration_id }}</dd>
        </div>
        <div v-if="order.client_email">
          <dt class="text-xs font-medium text-graphite">Email</dt>
          <dd class="mt-0.5 truncate text-sm font-semibold text-ink">{{ order.client_email }}</dd>
        </div>
        <div v-if="order.client_username">
          <dt class="text-xs font-medium text-graphite">Username</dt>
          <dd class="mt-0.5 text-sm font-semibold text-ink">{{ order.client_username }}</dd>
        </div>
        <div v-if="websiteLabel">
          <dt class="text-xs font-medium text-graphite">Website</dt>
          <dd class="mt-0.5 text-sm font-semibold text-ink">{{ websiteLabel }}</dd>
        </div>
      </dl>
    </div>

    <!-- Full order detail page — OrderActionsPanel inside handles all staff ops -->
    <OrderDetailPage :role="role" />
  </div>
</template>
