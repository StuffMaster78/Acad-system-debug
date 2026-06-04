<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import OrderDetailPage from "@/components/orders/detail/OrderDetailPage.vue";
import OrderAdminOpsPanel from "@/components/orders/detail/OrderAdminOpsPanel.vue";

const route = useRoute();
const auth = useAuthStore();

const orderId = computed(() => Number(route.params.id));
const role = computed(() => (auth.role === "superadmin" ? "superadmin" : "admin") as "admin" | "superadmin");
</script>

<template>
  <div class="space-y-4">
    <!-- Admin ops: route / assign / approve / return / revise / cancel — visible to admin & superadmin -->
    <OrderAdminOpsPanel :order-id="orderId" :role="role" />

    <!-- Full order detail page — includes its own back nav via OrderHeader -->
    <OrderDetailPage :role="role" />
  </div>
</template>
