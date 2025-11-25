<template>
  <div class="card bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow border border-gray-100">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <p class="text-sm font-medium text-gray-600 mb-1">{{ name }}</p>
        <p class="text-3xl font-bold text-gray-900">{{ value }}</p>
        <p v-if="subtitle" class="text-xs text-gray-500 mt-1">{{ subtitle }}</p>
        <p v-if="change !== null && change !== undefined" :class="[
          'text-sm mt-2 flex items-center',
          change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-gray-500'
        ]">
          <span class="mr-1">{{ change > 0 ? '↑' : change < 0 ? '↓' : '→' }}</span>
          {{ Math.abs(change) }}% from last month
        </p>
      </div>
      <div class="p-3 rounded-lg" :class="bgColor || 'bg-primary-100'">
        <span class="text-2xl">{{ icon }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    default: '📊'
  },
  subtitle: {
    type: String,
    default: null
  },
  change: {
    type: Number,
    default: null
  },
  bgColor: {
    type: String,
    default: 'bg-primary-100'
  }
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}
</style>

