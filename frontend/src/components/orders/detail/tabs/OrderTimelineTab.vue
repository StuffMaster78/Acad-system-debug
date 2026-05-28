<template>
  <OrderTimeline :order-id="orderId" />
</template>

<script setup lang="ts">
import OrderTimeline from "@/components/orders/OrderTimeline.vue";

defineProps<{ orderId: string }>();
</script>
