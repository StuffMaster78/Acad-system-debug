<template>
  <router-link :to="to" class="group relative card hover:shadow-lg transition-all duration-300 p-6 text-center transform hover:-translate-y-1">
    <div class="mb-3 flex justify-center">
      <div v-if="iconComponent" class="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
        <component :is="iconComponent" class="w-6 h-6 text-white" />
      </div>
      <div v-else class="text-3xl">{{ icon }}</div>
    </div>
    <div class="font-bold text-gray-900 mb-1">{{ title }}</div>
    <div class="text-sm text-gray-500">{{ description }}</div>
  </router-link>
</template>

<script setup>
// Version: 2.0 - Migrated to Lucide Icons (2026-01-02)
// All Heroicons removed to avoid v2 compatibility issues
import { computed } from 'vue'
import {
  FileText,
  Target,
  DollarSign,
  CreditCard,
  Star,
  Calendar,
  Scale,
  ClipboardList,
  MessageSquare,
  RefreshCw,
  Clock,
  Rocket,
  BarChart3,
  TrendingUp
} from 'lucide-vue-next'

const props = defineProps({
  to: {
    type: [String, Object],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  }
})

// Map emoji to modern Lucide icon components
const iconMap = {
  '📝': FileText,
  '🎯': Target,
  '💰': DollarSign,
  '💳': CreditCard,
  '⭐': Star,
  '📅': Calendar,
  '⚖️': Scale,
  '📋': ClipboardList,
  '💬': MessageSquare,
  '🔁': RefreshCw,
  '⏰': Clock,
  '🚀': Rocket,
  '📊': BarChart3,
  '📈': TrendingUp
}

const iconComponent = computed(() => {
  return iconMap[props.icon] || null
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1rem;
  border: 1px solid #e5e7eb;
  display: block;
  text-decoration: none;
  color: inherit;
}
</style>

