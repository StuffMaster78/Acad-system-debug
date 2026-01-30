<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Tickets</h1>
      <router-link to="/tickets/new" class="btn btn-primary">New Ticket</router-link>
    </div>

    <div class="card p-4 space-y-4">
      <form @submit.prevent="applyFilters" class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <input v-model="filters.search" type="text" placeholder="Search subject" class="border rounded px-3 py-2" />
        <input v-model.number="filters.order_id" type="number" min="1" placeholder="Order ID" class="border rounded px-3 py-2" />
        <select v-model="filters.status" class="border rounded px-3 py-2">
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="pending">Pending</option>
          <option value="closed">Closed</option>
        </select>
        <button class="px-4 py-2 bg-gray-100 rounded">Filter</button>
      </form>

      <div v-if="loading" class="text-sm text-gray-500">Loading...</div>
      <div v-else>
        <div v-if="!tickets.length" class="text-sm text-gray-500">No tickets found.</div>
        <ul class="divide-y divide-gray-200">
          <li v-for="t in tickets" :key="t.id" class="py-3 flex items-center justify-between">
            <div>
              <div class="font-medium">#{{ t.id }} · {{ t.subject || 'Ticket' }}</div>
              <div class="text-xs text-gray-500">
                <span :class="badgeClass(t.status)" class="inline-block px-2 py-0.5 rounded mr-2">{{ t.status }}</span>
                <span v-if="t.order_id">Order: #{{ t.order_id }}</span>
                · Created: {{ new Date(t.created_at).toLocaleString() }}
              </div>
            </div>
            <router-link :to="`/tickets/${t.id}`" class="text-primary-600 text-sm">Open</router-link>
          </li>
        </ul>
        <div v-if="pagination.count" class="mt-4 flex items-center justify-between text-sm text-gray-600">
          <div>{{ pagination.count }} total</div>
          <div class="flex gap-2">
            <button
              :disabled="!pagination.previous"
              @click="loadPage(pagination.previous)"
              class="px-3 py-1.5 rounded border disabled:opacity-50"
            >
              Previous
            </button>
            <button
              :disabled="!pagination.next"
              @click="loadPage(pagination.next)"
              class="px-3 py-1.5 rounded border disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ticketsAPI from '@/api/tickets'
import apiClient from '@/api/client'

const loading = ref(true)
const tickets = ref([])
const filters = ref({ search: '', status: '', order_id: null })
const pagination = ref({ next: null, previous: null, count: 0 })

const fetchTickets = async (url = null) => {
  loading.value = true
  try {
    let res
    if (url) {
      const urlObj = new URL(url)
      const path = urlObj.pathname + urlObj.search
      res = await apiClient.get(path)
    } else {
      const params = { page_size: 50 }
      if (filters.value.search) params.search = filters.value.search
      if (filters.value.status) params.status = filters.value.status
      if (filters.value.order_id) params.order_id = filters.value.order_id
      res = await ticketsAPI.list(params)
    }
    tickets.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
    pagination.value = {
      next: res.data?.next || null,
      previous: res.data?.previous || null,
      count: res.data?.count || tickets.value.length,
    }
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  fetchTickets()
}

const loadPage = (url) => {
  if (!url) return
  fetchTickets(url)
}

const badgeClass = (status) => {
  if (status === 'open') return 'bg-green-100 text-green-700'
  if (status === 'pending') return 'bg-yellow-100 text-yellow-700'
  if (status === 'closed') return 'bg-gray-100 text-gray-700'
  return 'bg-gray-100 text-gray-700'
}

onMounted(fetchTickets)
</script>


