<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Payments</h1>
    </div>

    <div class="card p-4 space-y-4">
      <form @submit.prevent="applyFilters" class="grid grid-cols-1 md:grid-cols-5 gap-3">
        <input v-model="filters.search" type="text" placeholder="Search ref/order" class="border rounded px-3 py-2" />
        <select v-model="filters.status" class="border rounded px-3 py-2">
          <option value="">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="cancelled">Cancelled</option>
          <option value="pending">Pending</option>
        </select>
        <input v-model.number="filters.order_id" type="number" min="1" placeholder="Order ID" class="border rounded px-3 py-2" />
        <input v-model="filters.reference" type="text" placeholder="Reference" class="border rounded px-3 py-2" />
        <button class="px-4 py-2 bg-gray-100 rounded">Filter</button>
      </form>

      <div v-if="loading" class="text-sm text-gray-500">Loading...</div>
      <div v-else>
        <div v-if="!payments.length" class="text-sm text-gray-500">No payments found.</div>
        <ul class="divide-y divide-gray-200">
          <li v-for="p in payments" :key="p.id" class="py-3 flex items-center justify-between">
            <div>
              <div class="font-medium">#{{ p.id }} · ${{ parseFloat(p.amount || 0).toFixed(2) }} <span :class="badgeClass(p.status)" class="inline-block px-2 py-0.5 rounded ml-2">{{ p.status }}</span></div>
              <div class="text-xs text-gray-500">Order: #{{ p.order }} · Ref: {{ p.reference || p.identifier || '—' }} · {{ toDT(p.created_at) }}</div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import paymentsAPI from '@/api/payments'

const loading = ref(true)
const payments = ref([])
const filters = ref({ status: '', order_id: null, reference: '', search: '' })

const toDT = (v) => (v ? new Date(v).toLocaleString() : '')
const badgeClass = (status) => {
  if (status === 'completed') return 'bg-green-100 text-green-700'
  if (status === 'failed') return 'bg-red-100 text-red-700'
  if (status === 'cancelled') return 'bg-gray-100 text-gray-700'
  if (status === 'pending') return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-700'
}

const fetchPayments = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.order_id) params.order_id = filters.value.order_id
    if (filters.value.reference) params.reference = filters.value.reference
    if (filters.value.search) params.search = filters.value.search
    const res = await paymentsAPI.list(params)
    payments.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } finally {
    loading.value = false
  }
}

const applyFilters = () => fetchPayments()

onMounted(fetchPayments)
</script>


