<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft } from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import OrderDetailPage from "@/components/orders/detail/OrderDetailPage.vue";
import OrderAdminOpsPanel from "@/components/orders/detail/OrderAdminOpsPanel.vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const orderId = computed(() => Number(route.params.id));
const role = computed(() => (auth.role === "superadmin" ? "superadmin" : "admin") as "admin" | "superadmin");

function goBack() {
  router.push(role.value === "superadmin" ? "/superadmin/orders" : "/admin/orders");
}
</script>

<template>
  <div class="space-y-4">
    <button
      class="inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink"
      @click="goBack"
    >
      <ArrowLeft class="h-3.5 w-3.5" />
      Back to orders
    </button>

    <!-- Admin ops: route / assign / approve / return / revise / cancel — visible to admin & superadmin -->
    <OrderAdminOpsPanel :order-id="orderId" :role="role" />

    <!-- All tabs: details, files, messages, payments, staffing, revisions, quality, timeline, audit -->
    <OrderDetailPage :role="role" />
  </div>
</template>
