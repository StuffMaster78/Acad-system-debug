<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock3,
  ExternalLink,
  FileText,
  Loader2,
  X,
} from "@lucide/vue";
import { RouterLink } from "vue-router";
import StatusPill from "@/components/ui/StatusPill.vue";
import { writerApi } from "@/api/writer";
import type { OrderSummary } from "@/types/orders";
import type { AvailabilityWindow } from "@/types/writer";

// ── State ────────────────────────────────────────────────────────────────────

const loading = ref(true);
const assignments = ref<OrderSummary[]>([]);
const availabilityWindows = ref<AvailabilityWindow[]>([]);
const today = new Date();
const viewYear = ref(today.getFullYear());
const viewMonth = ref(today.getMonth()); // 0-indexed
const selectedDate = ref<string | null>(null); // "YYYY-MM-DD"
const viewMode = ref<"month" | "week">("month");

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

// ── Data loading ─────────────────────────────────────────────────────────────

async function load() {
  loading.value = true;
  try {
    const [assignRes, availRes] = await Promise.all([
      writerApi.assignments({
        status: "in_progress,revision_requested,submitted,awaiting_approval",
        page_size: 200,
      }),
      writerApi.availability(),
    ]);

    const raw = Array.isArray(assignRes.data)
      ? assignRes.data
      : (assignRes.data as { results: OrderSummary[] }).results ?? [];
    assignments.value = raw.filter((a) => a.writer_deadline);

    const av = availRes.data;
    const windows: AvailabilityWindow[] = [];
    if (av.active_window) windows.push(av.active_window);
    if (av.upcoming_windows?.length) windows.push(...av.upcoming_windows);
    availabilityWindows.value = windows;
  } finally {
    loading.value = false;
  }
}

onMounted(load);

// ── Date helpers ─────────────────────────────────────────────────────────────

function toKey(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function todayKey(): string {
  return toKey(today);
}

function parseKey(key: string): Date {
  const [y, m, d] = key.split("-").map(Number);
  return new Date(y, m - 1, d);
}

// ── Unavailability map ───────────────────────────────────────────────────────

const unavailableDays = computed<Set<string>>(() => {
  const days = new Set<string>();
  for (const w of availabilityWindows.value) {
    const start = new Date(w.start_at as string);
    const end = w.end_at ? new Date(w.end_at as string) : null;
    const cursor = new Date(start);
    cursor.setHours(0, 0, 0, 0);
    const limit = end ? new Date(end) : new Date(start);
    limit.setHours(23, 59, 59, 999);
    while (cursor <= limit) {
      days.add(toKey(cursor));
      cursor.setDate(cursor.getDate() + 1);
    }
  }
  return days;
});

// ── Assignments by date ──────────────────────────────────────────────────────

const assignmentsByDate = computed<Record<string, OrderSummary[]>>(() => {
  const map: Record<string, OrderSummary[]> = {};
  for (const a of assignments.value) {
    if (!a.writer_deadline) continue;
    const key = toKey(new Date(a.writer_deadline));
    if (!map[key]) map[key] = [];
    map[key].push(a);
  }
  return map;
});

// ── Urgency helpers ──────────────────────────────────────────────────────────

function urgencyClass(deadline: string | null | undefined): string {
  if (!deadline) return "bg-neutral-100 text-neutral-600";
  const h = (new Date(deadline).getTime() - Date.now()) / 3600000;
  if (h < 0) return "bg-berry-100 text-berry-700";
  if (h < 12) return "bg-red-100 text-red-700";
  if (h < 36) return "bg-amber-100 text-amber-700";
  return "bg-signal-100 text-signal-700";
}

function urgencyDot(deadline: string | null | undefined): string {
  if (!deadline) return "bg-neutral-400";
  const h = (new Date(deadline).getTime() - Date.now()) / 3600000;
  if (h < 0) return "bg-berry-500";
  if (h < 12) return "bg-red-500";
  if (h < 36) return "bg-amber-400";
  return "bg-signal-500";
}

function deadlineLabel(deadline: string | null | undefined): string {
  if (!deadline) return "No deadline";
  const h = (new Date(deadline).getTime() - Date.now()) / 3600000;
  if (h < 0) return `${Math.round(Math.abs(h))}h overdue`;
  if (h < 24) return `${Math.round(h)}h left`;
  return `${Math.round(h / 24)}d left`;
}

function statusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (["completed"].includes(status)) return "success";
  if (["revision_requested"].includes(status)) return "warning";
  if (["cancelled"].includes(status)) return "danger";
  return "neutral";
}

// ── Month grid ───────────────────────────────────────────────────────────────

interface CalDay {
  key: string;
  date: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  isUnavailable: boolean;
  assignments: OrderSummary[];
}

const calendarDays = computed<CalDay[]>(() => {
  const firstOfMonth = new Date(viewYear.value, viewMonth.value, 1);
  const lastOfMonth = new Date(viewYear.value, viewMonth.value + 1, 0);
  const startOffset = firstOfMonth.getDay(); // 0=Sun

  const days: CalDay[] = [];
  // Leading days from previous month
  for (let i = startOffset - 1; i >= 0; i--) {
    const d = new Date(viewYear.value, viewMonth.value, -i);
    const key = toKey(d);
    days.push({ key, date: d.getDate(), isCurrentMonth: false, isToday: false, isUnavailable: unavailableDays.value.has(key), assignments: assignmentsByDate.value[key] ?? [] });
  }
  // Current month
  for (let d = 1; d <= lastOfMonth.getDate(); d++) {
    const date = new Date(viewYear.value, viewMonth.value, d);
    const key = toKey(date);
    days.push({ key, date: d, isCurrentMonth: true, isToday: key === todayKey(), isUnavailable: unavailableDays.value.has(key), assignments: assignmentsByDate.value[key] ?? [] });
  }
  // Trailing days
  const remainder = 42 - days.length;
  for (let d = 1; d <= remainder; d++) {
    const date = new Date(viewYear.value, viewMonth.value + 1, d);
    const key = toKey(date);
    days.push({ key, date: d, isCurrentMonth: false, isToday: false, isUnavailable: unavailableDays.value.has(key), assignments: assignmentsByDate.value[key] ?? [] });
  }
  return days;
});

// ── Week grid ────────────────────────────────────────────────────────────────

const _initialWeek = new Date(today);
_initialWeek.setDate(_initialWeek.getDate() - _initialWeek.getDay());
const weekStartDate = ref<Date>(_initialWeek);

const weekDays = computed<CalDay[]>(() => {
  const days: CalDay[] = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(weekStartDate.value);
    d.setDate(d.getDate() + i);
    const key = toKey(d);
    days.push({
      key,
      date: d.getDate(),
      isCurrentMonth: d.getMonth() === viewMonth.value,
      isToday: key === todayKey(),
      isUnavailable: unavailableDays.value.has(key),
      assignments: assignmentsByDate.value[key] ?? [],
    });
  }
  return days;
});

// ── Navigation ────────────────────────────────────────────────────────────────

function prevPeriod() {
  if (viewMode.value === "month") {
    if (viewMonth.value === 0) { viewMonth.value = 11; viewYear.value--; }
    else viewMonth.value--;
  } else {
    const d = new Date(weekStartDate.value);
    d.setDate(d.getDate() - 7);
    weekStartDate.value = d;
    viewYear.value = d.getFullYear();
    viewMonth.value = d.getMonth();
  }
}

function nextPeriod() {
  if (viewMode.value === "month") {
    if (viewMonth.value === 11) { viewMonth.value = 0; viewYear.value++; }
    else viewMonth.value++;
  } else {
    const d = new Date(weekStartDate.value);
    d.setDate(d.getDate() + 7);
    weekStartDate.value = d;
    viewYear.value = d.getFullYear();
    viewMonth.value = d.getMonth();
  }
}

function goToToday() {
  viewYear.value = today.getFullYear();
  viewMonth.value = today.getMonth();
  if (viewMode.value === "week") {
    const d = new Date(today);
    d.setDate(d.getDate() - d.getDay());
    weekStartDate.value = d;
  }
}

function switchMode(m: "month" | "week") {
  viewMode.value = m;
  if (m === "week") {
    const d = new Date(today);
    d.setDate(d.getDate() - d.getDay());
    weekStartDate.value = d;
  }
}

// ── Detail panel ─────────────────────────────────────────────────────────────

const selectedAssignments = computed<OrderSummary[]>(() =>
  selectedDate.value ? (assignmentsByDate.value[selectedDate.value] ?? []) : [],
);

function selectDay(key: string) {
  selectedDate.value = selectedDate.value === key ? null : key;
}

// ── Summary metrics ──────────────────────────────────────────────────────────

const overdueCount = computed(() =>
  assignments.value.filter((a) => {
    if (!a.writer_deadline) return false;
    return new Date(a.writer_deadline).getTime() < Date.now();
  }).length,
);

const dueTodayCount = computed(() =>
  (assignmentsByDate.value[todayKey()] ?? []).length,
);

const dueThisWeekCount = computed(() => {
  const start = new Date(today);
  start.setHours(0, 0, 0, 0);
  const end = new Date(start);
  end.setDate(end.getDate() + 7);
  return assignments.value.filter((a) => {
    if (!a.writer_deadline) return false;
    const d = new Date(a.writer_deadline);
    return d >= start && d < end;
  }).length;
});
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-neutral-900">Workload Calendar</h1>
        <p class="text-sm text-neutral-500 mt-0.5">Deadlines, availability, and upcoming work at a glance</p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors"
        @click="load"
      >
        <Loader2 v-if="loading" class="size-4 animate-spin" />
        <CalendarDays v-else class="size-4" />
        Refresh
      </button>
    </div>

    <!-- Summary pills -->
    <div class="flex flex-wrap gap-3">
      <div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-berry-50 border border-berry-200">
        <AlertTriangle class="size-4 text-berry-600" />
        <span class="text-sm font-medium text-berry-800">{{ overdueCount }} overdue</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200">
        <Clock3 class="size-4 text-amber-600" />
        <span class="text-sm font-medium text-amber-800">{{ dueTodayCount }} due today</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-signal-50 border border-signal-200">
        <CheckCircle2 class="size-4 text-signal-600" />
        <span class="text-sm font-medium text-signal-800">{{ dueThisWeekCount }} due this week</span>
      </div>
      <div v-if="availabilityWindows.length" class="flex items-center gap-2 px-3 py-2 rounded-lg bg-neutral-100 border border-neutral-200">
        <CalendarDays class="size-4 text-neutral-500" />
        <span class="text-sm font-medium text-neutral-700">{{ availabilityWindows.length }} unavailability window{{ availabilityWindows.length > 1 ? "s" : "" }}</span>
      </div>
    </div>

    <div class="flex gap-6 items-start">
      <!-- Calendar panel -->
      <div class="flex-1 min-w-0 bg-white rounded-lg border border-neutral-200 overflow-hidden">
        <!-- Toolbar -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-neutral-100">
          <div class="flex items-center gap-2">
            <button
              class="p-1.5 rounded-lg hover:bg-neutral-100 transition-colors"
              @click="prevPeriod"
            >
              <ArrowLeft class="size-4 text-neutral-600" />
            </button>
            <span class="text-sm font-semibold text-neutral-900 min-w-[160px] text-center">
              {{ MONTH_NAMES[viewMonth] }} {{ viewYear }}
            </span>
            <button
              class="p-1.5 rounded-lg hover:bg-neutral-100 transition-colors"
              @click="nextPeriod"
            >
              <ArrowRight class="size-4 text-neutral-600" />
            </button>
            <button
              class="ml-2 text-xs px-2.5 py-1 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors text-neutral-600"
              @click="goToToday"
            >
              Today
            </button>
          </div>
          <!-- View mode toggle -->
          <div class="flex rounded-lg border border-neutral-200 overflow-hidden text-xs">
            <button
              class="px-3 py-1.5 transition-colors"
              :class="viewMode === 'month' ? 'bg-neutral-900 text-white' : 'hover:bg-neutral-50 text-neutral-600'"
              @click="switchMode('month')"
            >
              Month
            </button>
            <button
              class="px-3 py-1.5 transition-colors border-l border-neutral-200"
              :class="viewMode === 'week' ? 'bg-neutral-900 text-white' : 'hover:bg-neutral-50 text-neutral-600'"
              @click="switchMode('week')"
            >
              Week
            </button>
          </div>
        </div>

        <!-- Loading skeleton -->
        <div v-if="loading" class="p-8 flex items-center justify-center">
          <Loader2 class="size-8 text-neutral-300 animate-spin" />
        </div>

        <template v-else>
          <!-- Weekday headers -->
          <div class="grid grid-cols-7 border-b border-neutral-100">
            <div
              v-for="day in WEEKDAYS"
              :key="day"
              class="py-2 text-center text-xs font-medium text-neutral-400 uppercase tracking-wide"
            >
              {{ day }}
            </div>
          </div>

          <!-- Month grid -->
          <div v-if="viewMode === 'month'" class="grid grid-cols-7">
            <div
              v-for="cell in calendarDays"
              :key="cell.key"
              class="min-h-[90px] border-b border-r border-neutral-100 last:border-r-0 p-1.5 cursor-pointer transition-colors"
              :class="[
                !cell.isCurrentMonth ? 'bg-neutral-50' : cell.isUnavailable ? 'bg-red-50' : 'bg-white',
                cell.isToday ? 'ring-2 ring-inset ring-signal-400' : '',
                selectedDate === cell.key ? 'bg-signal-50' : 'hover:bg-neutral-50',
              ]"
              @click="selectDay(cell.key)"
            >
              <!-- Day number -->
              <div class="flex items-center justify-between mb-1">
                <span
                  class="inline-flex items-center justify-center size-6 rounded-full text-xs font-medium"
                  :class="[
                    cell.isToday ? 'bg-signal-500 text-white' : '',
                    !cell.isCurrentMonth ? 'text-neutral-300' : cell.isUnavailable ? 'text-red-400' : 'text-neutral-700',
                  ]"
                >
                  {{ cell.date }}
                </span>
                <span v-if="cell.isUnavailable" class="text-xs text-red-400 font-medium">Off</span>
              </div>

              <!-- Assignment chips -->
              <div class="space-y-0.5">
                <div
                  v-for="a in cell.assignments.slice(0, 3)"
                  :key="a.id"
                  class="flex items-center gap-1 px-1 py-0.5 rounded text-xs truncate"
                  :class="urgencyClass(a.writer_deadline)"
                  :title="a.topic"
                >
                  <span class="size-1.5 rounded-full shrink-0" :class="urgencyDot(a.writer_deadline)" />
                  <span class="truncate">{{ a.topic }}</span>
                </div>
                <div
                  v-if="cell.assignments.length > 3"
                  class="text-xs text-neutral-400 pl-1"
                >
                  +{{ cell.assignments.length - 3 }} more
                </div>
              </div>
            </div>
          </div>

          <!-- Week grid -->
          <div v-else class="grid grid-cols-7 min-h-[400px]">
            <div
              v-for="cell in weekDays"
              :key="cell.key"
              class="border-r border-neutral-100 last:border-r-0 p-2 cursor-pointer transition-colors"
              :class="[
                cell.isUnavailable ? 'bg-red-50' : 'bg-white',
                cell.isToday ? 'ring-2 ring-inset ring-signal-400' : '',
                selectedDate === cell.key ? 'bg-signal-50' : 'hover:bg-neutral-50',
              ]"
              @click="selectDay(cell.key)"
            >
              <div class="flex flex-col items-center gap-1 mb-3">
                <span class="text-xs text-neutral-400">{{ WEEKDAYS[parseKey(cell.key).getDay()] }}</span>
                <span
                  class="inline-flex items-center justify-center size-8 rounded-full text-sm font-semibold"
                  :class="cell.isToday ? 'bg-signal-500 text-white' : 'text-neutral-700'"
                >
                  {{ cell.date }}
                </span>
                <span v-if="cell.isUnavailable" class="text-xs text-red-400">Off</span>
              </div>

              <div class="space-y-1">
                <div
                  v-for="a in cell.assignments"
                  :key="a.id"
                  class="px-2 py-1.5 rounded-lg text-xs space-y-0.5"
                  :class="urgencyClass(a.writer_deadline)"
                >
                  <div class="font-medium truncate">{{ a.topic }}</div>
                  <div class="opacity-75">{{ deadlineLabel(a.writer_deadline) }}</div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Detail panel -->
      <div
        v-if="selectedDate"
        class="w-72 shrink-0 bg-white rounded-lg border border-neutral-200 overflow-hidden"
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-neutral-100">
          <div>
            <p class="text-xs text-neutral-400 font-medium uppercase tracking-wide">
              {{ parseKey(selectedDate).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" }) }}
            </p>
            <p class="text-sm font-semibold text-neutral-900 mt-0.5">
              {{ selectedAssignments.length === 0 ? "No deadlines" : `${selectedAssignments.length} deadline${selectedAssignments.length > 1 ? "s" : ""}` }}
            </p>
          </div>
          <button
            class="p-1 rounded hover:bg-neutral-100 transition-colors text-neutral-400"
            @click="selectedDate = null"
          >
            <X class="size-4" />
          </button>
        </div>

        <!-- Unavailability notice -->
        <div v-if="unavailableDays.has(selectedDate)" class="mx-4 mt-3 px-3 py-2 rounded-lg bg-red-50 border border-red-200">
          <p class="text-xs font-medium text-red-700">Unavailable this day</p>
        </div>

        <!-- No deadlines -->
        <div v-if="selectedAssignments.length === 0" class="px-4 py-6 text-center text-neutral-400 text-sm">
          No assignments due on this date.
        </div>

        <!-- Assignment cards -->
        <div v-else class="divide-y divide-neutral-100 max-h-[560px] overflow-y-auto">
          <div
            v-for="a in selectedAssignments"
            :key="a.id"
            class="px-4 py-3 space-y-2"
          >
            <div class="flex items-start justify-between gap-2">
              <p class="text-sm font-medium text-neutral-900 leading-snug">{{ a.topic }}</p>
              <RouterLink
                :to="`/writer/orders/${a.id}`"
                class="shrink-0 p-1 rounded hover:bg-neutral-100 text-neutral-400"
              >
                <ExternalLink class="size-3.5" />
              </RouterLink>
            </div>

            <div class="flex flex-wrap gap-1.5 items-center">
              <StatusPill :label="a.status ?? 'unknown'" :tone="statusTone(String(a.status ?? ''))" />
              <span
                class="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium"
                :class="urgencyClass(a.writer_deadline)"
              >
                <Clock3 class="size-3" />
                {{ deadlineLabel(a.writer_deadline) }}
              </span>
            </div>

            <div class="grid grid-cols-2 gap-x-3 gap-y-1 text-xs text-neutral-500">
              <div v-if="a.service_code" class="flex items-center gap-1">
                <FileText class="size-3 text-neutral-300" />
                {{ a.service_code }}
              </div>
              <div v-if="a.number_of_pages" class="flex items-center gap-1">
                <ChevronRight class="size-3 text-neutral-300" />
                {{ a.number_of_pages }}pp
              </div>
              <div v-if="a.writer_compensation" class="flex items-center gap-1 col-span-2 font-medium text-signal-700">
                Earn: ${{ Number(a.writer_compensation).toFixed(2) }}
              </div>
            </div>

            <!-- Client deadline note -->
            <div v-if="a.client_deadline" class="text-xs text-neutral-400">
              Client deadline: {{ new Date(a.client_deadline).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex flex-wrap gap-4 text-xs text-neutral-500">
      <div class="flex items-center gap-1.5">
        <span class="size-2 rounded-full bg-berry-500" />
        Overdue
      </div>
      <div class="flex items-center gap-1.5">
        <span class="size-2 rounded-full bg-red-500" />
        Due &lt;12h
      </div>
      <div class="flex items-center gap-1.5">
        <span class="size-2 rounded-full bg-amber-400" />
        Due &lt;36h
      </div>
      <div class="flex items-center gap-1.5">
        <span class="size-2 rounded-full bg-signal-500" />
        On track
      </div>
      <div class="flex items-center gap-1.5">
        <span class="inline-block size-3 rounded bg-red-100 border border-red-200" />
        Unavailable
      </div>
      <div class="flex items-center gap-1.5">
        <span class="inline-block size-3 rounded ring-2 ring-signal-400" />
        Today
      </div>
    </div>
  </div>
</template>
