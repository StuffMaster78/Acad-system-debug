<template>
  <div class="space-y-4">
    <!-- Header with masked identities, status badges, approve banner -->
    <OrderHeader
      :order-id="orderId"
      :order="order"
      :lifecycle="lifecycle"
      :role="role"
      :is-mutating="orders.isMutating"
      @approve="orders.approveOrder(orderId)"
    />

    <!-- Global store feedback -->
    <div v-if="orders.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ orders.error }}</div>
    <div v-if="orders.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{{ orders.notice }}</div>

    <!-- Loading skeleton -->
    <div v-if="orders.isLoading && !order" class="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-graphite">
      Loading order workspace…
    </div>

    <template v-else-if="order">
      <!-- Summary cards -->
      <OrderSummaryCards :order="order" :lifecycle="lifecycle" :role="role" />

      <!-- Tab navigation -->
      <OrderTabs :role="role" v-model="activeTab" />

      <!-- Tab content -->
      <div class="min-h-64">
        <OrderDetailsTab
          v-if="activeTab === 'details'"
          :order-id="orderId"
          :order="order"
          :lifecycle="lifecycle"
          :role="role"
        />
        <OrderFilesTab
          v-else-if="activeTab === 'files'"
          :order-id="orderId"
          :order="order"
          :lifecycle="lifecycle"
          :role="role"
        />
        <OrderMessagesTab
          v-else-if="activeTab === 'messages'"
          :order-id="orderId"
          :order="order"
          :role="role"
        />
        <OrderPaymentsTab
          v-else-if="activeTab === 'payments'"
          :order-id="orderId"
          :order="order"
          :role="role"
        />
        <OrderStaffingTab
          v-else-if="activeTab === 'staffing'"
          :order-id="orderId"
          :order="order"
          :lifecycle="lifecycle"
          :role="role"
          @refresh="orders.fetchOrder(orderId)"
        />
        <OrderRevisionsTab
          v-else-if="activeTab === 'revisions'"
          :order-id="orderId"
          :lifecycle="lifecycle"
          :role="role"
        />
        <OrderQualityTab
          v-else-if="activeTab === 'quality'"
          :order-id="orderId"
          :order="order"
          :lifecycle="lifecycle"
          :role="role"
          @refresh="orders.fetchOrder(orderId)"
        />
        <OrderTimelineTab
          v-else-if="activeTab === 'timeline'"
          :order-id="orderId"
        />
        <OrderAuditTab
          v-else-if="activeTab === 'audit'"
          :order-id="orderId"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import type { UserRole } from "@/types/roles";
import { useOrderStore } from "@/stores/orders";
import { useFilesStore } from "@/stores/files";
import { useCommunicationsStore } from "@/stores/communications";
import { ROLE_TABS } from "./types";

import OrderHeader from "./OrderHeader.vue";
import OrderSummaryCards from "./OrderSummaryCards.vue";
import OrderTabs from "./OrderTabs.vue";
import OrderDetailsTab from "./tabs/OrderDetailsTab.vue";
import OrderFilesTab from "./tabs/OrderFilesTab.vue";
import OrderMessagesTab from "./tabs/OrderMessagesTab.vue";
import OrderPaymentsTab from "./tabs/OrderPaymentsTab.vue";
import OrderStaffingTab from "./tabs/OrderStaffingTab.vue";
import OrderRevisionsTab from "./tabs/OrderRevisionsTab.vue";
import OrderQualityTab from "./tabs/OrderQualityTab.vue";
import OrderTimelineTab from "./tabs/OrderTimelineTab.vue";
import OrderAuditTab from "./tabs/OrderAuditTab.vue";

const props = defineProps<{ role: UserRole }>();

const route = useRoute();
const orderId = computed(() => String(route.params.id));

const orders = useOrderStore();
const files = useFilesStore();
const comms = useCommunicationsStore();

const order = computed(() => orders.selectedOrder);
const lifecycle = computed(() => orders.selectedLifecycle);

// Start on the first tab the role can see
const activeTab = ref(ROLE_TABS[props.role]?.[0] ?? "details");

onMounted(async () => {
  files.clearMessages();
  files.uploadQueue.splice(0);
  await orders.fetchOrder(orderId.value);
  await Promise.all([
    files.fetchOrderAttachments(orderId.value),
    comms.loadOrderThread(orderId.value).catch(() => undefined),
  ]);
});
</script>
