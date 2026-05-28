<script setup lang="ts">
import { onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { BookOpen, CheckCircle, Clock, AlertCircle, Plus } from "@lucide/vue";
import { useClassesStore } from "@/stores/classes";
import type { ClassStatus } from "@/types/classes";

const store = useClassesStore();
const router = useRouter();

onMounted(() => store.loadOrders());

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

const activeClasses = computed(() => store.orders.filter((o) => o.status === "active"));
const otherClasses = computed(() => store.orders.filter((o) => o.status !== "active"));

function progress(total: number, done: number) {
  if (!total) return 0;
  return Math.round((done / total) * 100);
}

function open(id: number) {
  router.push(`/client/classes/${id}`);
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-4xl space-y-4">

      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-ink">My Classes</h1>
          <p class="text-sm text-graphite">Semester-long and ongoing class help</p>
        </div>
        <button
          class="inline-flex items-center gap-1.5 rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-berry/90 transition-colors"
          @click="router.push('/client/classes/new')"
        >
          <Plus class="size-4" />
          New Class
        </button>
      </div>

      <!-- Loading -->
      <div v-if="store.isLoading" class="py-16 text-center text-graphite animate-pulse">
        Loading classes…
      </div>

      <!-- Empty -->
      <div
        v-else-if="!store.orders.length"
        class="rounded-lg border border-slate-200 bg-white p-16 text-center"
      >
        <BookOpen class="mx-auto mb-3 size-10 text-slate-300" />
        <p class="font-medium text-ink">No classes yet</p>
        <p class="mt-1 text-sm text-graphite">Contact support to set up a class management plan.</p>
      </div>

      <template v-else>
        <!-- Active -->
        <div v-if="activeClasses.length">
          <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Active</h2>
          <div class="space-y-3">
            <div
              v-for="cls in activeClasses"
              :key="cls.id"
              class="cursor-pointer rounded-lg border border-slate-200 bg-white p-5 transition-shadow hover:shadow-md"
              @click="open(cls.id)"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass[cls.status]">
                      {{ statusLabel[cls.status] }}
                    </span>
                    <span class="text-xs text-graphite font-mono">{{ cls.reference }}</span>
                  </div>
                  <h3 class="mt-1.5 font-semibold text-ink truncate">{{ cls.title }}</h3>
                  <p class="text-sm text-graphite">{{ cls.subject }} · {{ cls.academic_level }}</p>
                </div>
                <div class="shrink-0 text-right text-sm">
                  <p class="font-semibold text-ink">${{ cls.total_price }}</p>
                  <p class="text-xs text-graphite capitalize">{{ cls.payment_status }}</p>
                </div>
              </div>

              <!-- Task progress -->
              <div class="mt-4">
                <div class="mb-1 flex items-center justify-between text-xs text-graphite">
                  <span>{{ cls.completed_tasks }} of {{ cls.total_tasks }} tasks done</span>
                  <span>{{ progress(cls.total_tasks, cls.completed_tasks) }}%</span>
                </div>
                <div class="h-1.5 overflow-hidden rounded-full bg-slate-100">
                  <div
                    class="h-full rounded-full bg-berry transition-all"
                    :style="{ width: `${progress(cls.total_tasks, cls.completed_tasks)}%` }"
                  />
                </div>
              </div>

              <!-- Meta -->
              <div class="mt-3 flex items-center gap-4 text-xs text-graphite">
                <span class="flex items-center gap-1">
                  <Clock class="size-3" />
                  {{ cls.start_date }} – {{ cls.end_date }}
                </span>
                <span v-if="cls.writer_username" class="flex items-center gap-1">
                  <CheckCircle class="size-3 text-emerald-500" />
                  {{ cls.writer_username }}
                </span>
                <span v-else class="flex items-center gap-1 text-amber-600">
                  <AlertCircle class="size-3" />
                  Unassigned
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Past / Other -->
        <div v-if="otherClasses.length">
          <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Other</h2>
          <div class="space-y-2">
            <div
              v-for="cls in otherClasses"
              :key="cls.id"
              class="flex cursor-pointer items-center gap-4 rounded-lg border border-slate-200 bg-white px-5 py-3 hover:shadow-md transition-shadow"
              @click="open(cls.id)"
            >
              <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass[cls.status]">
                {{ statusLabel[cls.status] }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-ink">{{ cls.title }}</p>
                <p class="text-xs text-graphite">{{ cls.reference }} · {{ cls.subject }}</p>
              </div>
              <p class="shrink-0 text-sm font-semibold text-ink">${{ cls.total_price }}</p>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>
