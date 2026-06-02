<script setup lang="ts">
import { onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { BookOpen, CheckCircle } from "@lucide/vue";
import { useClassesStore } from "@/stores/classes";
import type { ClassStatus } from "@/types/classes";

const store = useClassesStore();
const router = useRouter();

onMounted(() => store.loadOrders());

const statusLabels: Partial<Record<ClassStatus, string>> = {
  draft: "Draft",
  submitted: "Submitted",
  needs_client_info: "Needs Info",
  under_review: "Under Review",
  price_proposed: "Price Proposed",
  negotiating: "Negotiating",
  accepted: "Accepted",
  pending_payment: "Pending Payment",
  partially_paid: "Partially Paid",
  paid: "Paid",
  assigned: "Assigned",
  in_progress: "In Progress",
  pending: "Pending",
  active: "Active",
  paused: "Paused",
  quality_review: "Quality Review",
  completed: "Completed",
  cancelled: "Cancelled",
  archived: "Archived",
};

const statusClasses: Partial<Record<ClassStatus, string>> = {
  draft: "bg-slate-100 text-graphite",
  submitted: "bg-blue-100 text-blue-700",
  needs_client_info: "bg-amber-100 text-amber-700",
  under_review: "bg-violet-100 text-violet-700",
  price_proposed: "bg-blue-100 text-blue-700",
  negotiating: "bg-amber-100 text-amber-700",
  accepted: "bg-emerald-100 text-emerald-700",
  pending_payment: "bg-amber-100 text-amber-700",
  partially_paid: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  assigned: "bg-blue-100 text-blue-700",
  in_progress: "bg-berry/10 text-berry",
  pending: "bg-amber-100 text-amber-700",
  active: "bg-emerald-100 text-emerald-700",
  paused: "bg-slate-100 text-graphite",
  quality_review: "bg-purple-100 text-purple-700",
  completed: "bg-blue-100 text-blue-700",
  cancelled: "bg-rose-100 text-rose-700",
  archived: "bg-slate-100 text-slate-400",
};

const active = computed(() => store.orders.filter((o) => ["active", "pending", "assigned", "in_progress", "quality_review", "submitted"].includes(o.status)));
const past = computed(() => store.orders.filter((o) => !["active", "pending", "assigned", "in_progress", "quality_review", "submitted"].includes(o.status)));

function labelize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function statusLabel(status: ClassStatus): string {
  return statusLabels[status] ?? labelize(status);
}

function statusClass(status: ClassStatus): string {
  return statusClasses[status] ?? "bg-slate-100 text-graphite";
}

function progress(total: number, done: number) {
  if (!total) return 0;
  return Math.round((done / total) * 100);
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-3xl space-y-4">

      <div>
        <h1 class="text-xl font-bold text-ink">My Classes</h1>
        <p class="text-sm text-graphite">Semester-based assignments</p>
      </div>

      <div v-if="store.isLoading" class="py-16 text-center text-graphite animate-pulse">Loading…</div>

      <div v-else-if="!store.orders.length" class="py-16 text-center rounded-lg border border-slate-200 bg-white">
        <BookOpen class="mx-auto mb-3 size-10 text-slate-300" />
        <p class="text-graphite">No class assignments yet.</p>
      </div>

      <template v-else>
        <div v-if="active.length">
          <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Active</h2>
          <div class="space-y-3">
            <div
              v-for="cls in active"
              :key="cls.id"
              class="cursor-pointer rounded-lg border border-slate-200 bg-white p-5 hover:shadow-md transition-shadow"
              @click="router.push(`/writer/classes/${cls.id}`)"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass(cls.status)">
                      {{ statusLabel(cls.status) }}
                    </span>
                    <span class="font-mono text-xs text-graphite">{{ cls.reference }}</span>
                  </div>
                  <h3 class="mt-1.5 font-semibold text-ink truncate">{{ cls.title }}</h3>
                  <p class="text-sm text-graphite">{{ cls.subject }} · {{ cls.academic_level }}</p>
                </div>
                <div class="shrink-0 text-right text-xs text-graphite">
                  <p>{{ cls.start_date }}</p>
                  <p>– {{ cls.end_date }}</p>
                </div>
              </div>
              <div class="mt-4">
                <div class="mb-1 flex justify-between text-xs text-graphite">
                  <span>{{ cls.completed_tasks }} / {{ cls.total_tasks }} tasks</span>
                  <span>{{ progress(cls.total_tasks, cls.completed_tasks) }}%</span>
                </div>
                <div class="h-1.5 overflow-hidden rounded-full bg-slate-100">
                  <div class="h-full rounded-full bg-berry" :style="{ width: `${progress(cls.total_tasks, cls.completed_tasks)}%` }" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="past.length">
          <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Past</h2>
          <div class="space-y-2">
            <div
              v-for="cls in past"
              :key="cls.id"
              class="flex cursor-pointer items-center gap-4 rounded-lg border border-slate-200 bg-white px-5 py-3 hover:shadow-md transition-shadow"
              @click="router.push(`/writer/classes/${cls.id}`)"
            >
              <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass(cls.status)">
                {{ statusLabel(cls.status) }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-ink">{{ cls.title }}</p>
                <p class="text-xs text-graphite">{{ cls.reference }}</p>
              </div>
              <span class="flex items-center gap-1 text-xs text-emerald-700">
                <CheckCircle class="size-3.5" />
                {{ cls.completed_tasks }}/{{ cls.total_tasks }}
              </span>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>
