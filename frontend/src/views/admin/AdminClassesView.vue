<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import { BookOpen, Search } from "@lucide/vue";
import { useClassesStore } from "@/stores/classes";
import type { ClassStatus } from "@/types/classes";

const store = useClassesStore();
const router = useRouter();

onMounted(() => store.loadOrders());

const search = ref("");
const statusFilter = ref<ClassStatus | "">("");

const statusLabel: Record<ClassStatus, string> = {
  pending: "Pending",
  active: "Active",
  paused: "Paused",
  completed: "Completed",
  cancelled: "Cancelled",
};

const statusClass: Record<ClassStatus, string> = {
  pending: "bg-amber-100 text-amber-700",
  active: "bg-emerald-100 text-emerald-700",
  paused: "bg-slate-100 text-graphite",
  completed: "bg-blue-100 text-blue-700",
  cancelled: "bg-rose-100 text-rose-700",
};

const filtered = computed(() => {
  let list = store.orders;
  if (statusFilter.value) list = list.filter((o) => o.status === statusFilter.value);
  if (search.value.trim()) {
    const q = search.value.toLowerCase();
    list = list.filter(
      (o) =>
        o.title.toLowerCase().includes(q) ||
        o.reference.toLowerCase().includes(q) ||
        o.client_username.toLowerCase().includes(q),
    );
  }
  return list;
});

function progress(total: number, done: number) {
  if (!total) return 0;
  return Math.round((done / total) * 100);
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-5xl space-y-6">

      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-ink">Class Orders</h1>
          <p class="text-sm text-graphite">Semester-based and multi-task class management</p>
        </div>
      </div>

      <!-- Filters -->
      <div class="flex gap-3">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-2.5 size-4 text-graphite" />
          <input
            v-model="search"
            placeholder="Search by title, reference, or client…"
            class="w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 py-2 text-sm focus-ring"
          />
        </div>
        <select
          v-model="statusFilter"
          class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-graphite focus-ring"
        >
          <option value="">All statuses</option>
          <option v-for="s in ['pending','active','paused','completed','cancelled']" :key="s" :value="s">
            {{ statusLabel[s as ClassStatus] }}
          </option>
        </select>
      </div>

      <!-- Loading -->
      <div v-if="store.isLoading" class="py-16 text-center text-graphite animate-pulse">Loading…</div>

      <!-- Empty -->
      <div v-else-if="!filtered.length" class="py-16 text-center rounded-xl border border-slate-200 bg-white shadow-panel">
        <BookOpen class="mx-auto mb-3 size-10 text-slate-300" />
        <p class="text-graphite">No class orders found.</p>
      </div>

      <!-- Table -->
      <div v-else class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-panel">
        <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-5 py-3 text-left">Reference</th>
              <th class="px-5 py-3 text-left">Title</th>
              <th class="px-5 py-3 text-left">Client</th>
              <th class="px-5 py-3 text-left">Writer</th>
              <th class="px-5 py-3 text-center">Progress</th>
              <th class="px-5 py-3 text-right">Price</th>
              <th class="px-5 py-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr
              v-for="cls in filtered"
              :key="cls.id"
              class="cursor-pointer hover:bg-slate-50 transition-colors"
              @click="router.push(`/admin/classes/${cls.id}`)"
            >
              <td class="px-5 py-3 font-mono text-xs text-graphite">{{ cls.reference }}</td>
              <td class="px-5 py-3 font-medium text-ink max-w-xs truncate">{{ cls.title }}</td>
              <td class="px-5 py-3 text-graphite">{{ cls.client_username }}</td>
              <td class="px-5 py-3 text-graphite">{{ cls.writer_username ?? '—' }}</td>
              <td class="px-5 py-3">
                <div class="flex items-center gap-2">
                  <div class="flex-1 h-1.5 rounded-full bg-slate-100">
                    <div
                      class="h-full rounded-full bg-berry"
                      :style="{ width: `${progress(cls.total_tasks, cls.completed_tasks)}%` }"
                    />
                  </div>
                  <span class="text-xs text-graphite whitespace-nowrap">{{ cls.completed_tasks }}/{{ cls.total_tasks }}</span>
                </div>
              </td>
              <td class="px-5 py-3 text-right font-semibold text-ink">${{ cls.total_price }}</td>
              <td class="px-5 py-3 text-center">
                <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass[cls.status]">
                  {{ statusLabel[cls.status] }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

    </div>
  </div>
</template>
