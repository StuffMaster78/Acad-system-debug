<template>
  <div class="special-order-new">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Create Special Order</h1>
      <p class="text-gray-600 mt-2">Create a rush order, revision, or custom order</p>
    </div>

    <SpecialOrderCreate
      @success="handleSuccess"
      @cancel="handleCancel"
    />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import SpecialOrderCreate from '@/components/orders/SpecialOrderCreate.vue'

const router = useRouter()

const handleSuccess = (orderData) => {
  // Redirect to the order detail page
  if (orderData?.id) {
    router.push(`/orders/${orderData.id}`)
  } else {
    // If no ID, redirect to orders list
    router.push('/orders')
  }
}

const handleCancel = () => {
  router.push('/orders')
}
</script>

<style scoped>
.special-order-new {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}
</style>

