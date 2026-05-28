<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  Bell,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Globe,
  Loader2,
  MapPin,
  Percent,
  Plus,
  RefreshCw,
  Send,
  Star,
  Tag,
  Trash2,
  X,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { holidaysApi } from "@/api/holidays";
import type { HolidayDiscountCampaign, HolidayReminder, SpecialDay } from "@/api/holidays";

// ── Tabs ─────────────────────────────────────────────────────────────────────

type Tab = "special-days" | "reminders" | "campaigns";
const activeTab = ref<Tab>("special-days");

// ── Special Days ──────────────────────────────────────────────────────────────

const specialDays = ref<SpecialDay[]>([]);
const specialDaysLoading = ref(false);
const pendingDeleteDayId = ref<number | null>(null);
const upcomingSpecialDays = ref<SpecialDay[]>([]);

const filterEventType = ref("");
const filterActive = ref<"" | "true" | "false">("");
const filterUpcoming = ref(false);

const showCreateForm = ref(false);
const createLoading = ref(false);
const createError = ref("");
const createForm = ref({
  name: "",
  slug: "",
  date: "",
  event_type: "holiday",
  description: "",
  is_annual: true,
  is_international: false,
  is_active: true,
  priority: 5,
  countries: "",
});

const generatingDiscountFor = ref<number | null>(null);

async function loadSpecialDays() {
  specialDaysLoading.value = true;
  try {
    const params: Record<string, unknown> = {};
    if (filterEventType.value) params.event_type = filterEventType.value;
    if (filterActive.value !== "") params.is_active = filterActive.value;
    if (filterUpcoming.value) params.upcoming = "true";
    const { data } = await holidaysApi.specialDays(params);
    specialDays.value = Array.isArray(data) ? data : (data as { results: SpecialDay[] }).results ?? [];
  } finally {
    specialDaysLoading.value = false;
  }
}

async function loadUpcoming() {
  const { data } = await holidaysApi.upcomingSpecialDays(60);
  upcomingSpecialDays.value = data;
}

async function submitCreateSpecialDay() {
  createError.value = "";
  if (!createForm.value.name || !createForm.value.date) {
    createError.value = "Name and date are required.";
    return;
  }
  createLoading.value = true;
  try {
    const countries = createForm.value.countries
      ? createForm.value.countries.split(",").map((c) => c.trim().toUpperCase()).filter(Boolean)
      : [];
    await holidaysApi.createSpecialDay({
      name: createForm.value.name,
      slug: createForm.value.slug || createForm.value.name.toLowerCase().replace(/\s+/g, "-"),
      date: createForm.value.date,
      event_type: createForm.value.event_type,
      description: createForm.value.description || undefined,
      is_annual: createForm.value.is_annual,
      is_international: createForm.value.is_international,
      is_active: createForm.value.is_active,
      priority: createForm.value.priority,
      countries,
    });
    showCreateForm.value = false;
    createForm.value = { name: "", slug: "", date: "", event_type: "holiday", description: "", is_annual: true, is_international: false, is_active: true, priority: 5, countries: "" };
    await loadSpecialDays();
    await loadUpcoming();
  } catch {
    createError.value = "Failed to create special day.";
  } finally {
    createLoading.value = false;
  }
}

async function deleteSpecialDay(id: number) {
  if (pendingDeleteDayId.value !== id) { pendingDeleteDayId.value = id; return; }
  pendingDeleteDayId.value = null;
  await holidaysApi.deleteSpecialDay(id);
  await loadSpecialDays();
}

async function generateDiscount(id: number) {
  generatingDiscountFor.value = id;
  try {
    await holidaysApi.generateDiscount(id);
    await loadCampaigns();
    activeTab.value = "campaigns";
  } finally {
    generatingDiscountFor.value = null;
  }
}

function daysUntilTone(days: number): string {
  if (days < 0) return "text-neutral-400";
  if (days <= 7) return "text-berry-600 font-semibold";
  if (days <= 30) return "text-amber-600 font-medium";
  return "text-signal-600";
}

// ── Reminders ────────────────────────────────────────────────────────────────

const reminders = ref<HolidayReminder[]>([]);
const remindersLoading = ref(false);
const filterReminderStatus = ref("");
const markingId = ref<number | null>(null);
const discountCreatingId = ref<number | null>(null);
const checkingReminders = ref(false);
const notifyingAdmins = ref(false);
const reminderFeedback = ref("");

async function loadReminders() {
  remindersLoading.value = true;
  try {
    const params: Record<string, unknown> = {};
    if (filterReminderStatus.value) params.status = filterReminderStatus.value;
    const { data } = await holidaysApi.reminders(params);
    reminders.value = Array.isArray(data) ? data : (data as { results: HolidayReminder[] }).results ?? [];
  } finally {
    remindersLoading.value = false;
  }
}

async function markSent(id: number) {
  markingId.value = id;
  try {
    await holidaysApi.markReminderSent(id);
    await loadReminders();
  } finally {
    markingId.value = null;
  }
}

async function createReminderDiscount(id: number) {
  discountCreatingId.value = id;
  try {
    const { data } = await holidaysApi.createReminderDiscount(id);
    reminderFeedback.value = `Discount created: ${data.discount_code}`;
    await loadReminders();
  } finally {
    discountCreatingId.value = null;
  }
}

async function checkAndCreate() {
  checkingReminders.value = true;
  reminderFeedback.value = "";
  try {
    const { data } = await holidaysApi.checkAndCreateReminders();
    reminderFeedback.value = data.message;
    await loadReminders();
  } finally {
    checkingReminders.value = false;
  }
}

async function notifyAdmins() {
  notifyingAdmins.value = true;
  reminderFeedback.value = "";
  try {
    const { data } = await holidaysApi.notifyAdmins();
    reminderFeedback.value = data.message;
  } finally {
    notifyingAdmins.value = false;
  }
}

function reminderStatusTone(status: string): "success" | "warning" | "neutral" {
  if (status === "sent") return "success";
  if (status === "pending") return "warning";
  return "neutral";
}

// ── Campaigns ────────────────────────────────────────────────────────────────

const campaigns = ref<HolidayDiscountCampaign[]>([]);
const campaignsLoading = ref(false);
const filterYear = ref(String(new Date().getFullYear()));
const filterCampaignActive = ref<"" | "true" | "false">("");

async function loadCampaigns() {
  campaignsLoading.value = true;
  try {
    const params: Record<string, unknown> = {};
    if (filterYear.value) params.year = filterYear.value;
    if (filterCampaignActive.value !== "") params.is_active = filterCampaignActive.value;
    const { data } = await holidaysApi.campaigns(params);
    campaigns.value = Array.isArray(data) ? data : (data as { results: HolidayDiscountCampaign[] }).results ?? [];
  } finally {
    campaignsLoading.value = false;
  }
}

// ── Upcoming banner data ──────────────────────────────────────────────────────

const soonDays = computed(() =>
  upcomingSpecialDays.value.filter((d) => d.days_until >= 0 && d.days_until <= 14),
);

// ── Init ─────────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([loadSpecialDays(), loadReminders(), loadCampaigns(), loadUpcoming()]);
});
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-neutral-900">Holiday Management</h1>
        <p class="text-sm text-neutral-500 mt-0.5">Special days, reminder campaigns, and seasonal discount campaigns</p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors"
        @click="loadSpecialDays(); loadReminders(); loadCampaigns(); loadUpcoming()"
      >
        <RefreshCw class="size-4" />
        Refresh
      </button>
    </div>

    <!-- Upcoming soon banner -->
    <div v-if="soonDays.length" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
      <div class="flex items-center gap-2 mb-2">
        <Bell class="size-4 text-amber-600" />
        <span class="text-sm font-semibold text-amber-800">Coming up in the next 14 days</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="d in soonDays"
          :key="d.id"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-medium"
        >
          <CalendarDays class="size-3" />
          {{ d.name }} — {{ d.days_until === 0 ? "today" : `in ${d.days_until}d` }}
        </span>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-neutral-200 gap-6">
      <button
        v-for="tab in [
          { key: 'special-days', label: 'Special Days', icon: CalendarDays },
          { key: 'reminders', label: 'Reminders', icon: Bell },
          { key: 'campaigns', label: 'Discount Campaigns', icon: Percent },
        ]"
        :key="tab.key"
        class="flex items-center gap-1.5 pb-3 text-sm font-medium border-b-2 transition-colors -mb-px"
        :class="activeTab === tab.key
          ? 'border-neutral-900 text-neutral-900'
          : 'border-transparent text-neutral-500 hover:text-neutral-700'"
        @click="activeTab = tab.key as Tab"
      >
        <component :is="tab.icon" class="size-4" />
        {{ tab.label }}
      </button>
    </div>

    <!-- ── SPECIAL DAYS ─────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'special-days'">
      <!-- Filters + create -->
      <div class="flex flex-wrap items-center gap-3">
        <select
          v-model="filterEventType"
          class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 bg-white"
          @change="loadSpecialDays()"
        >
          <option value="">All types</option>
          <option value="holiday">Holiday</option>
          <option value="observance">Observance</option>
          <option value="cultural">Cultural</option>
          <option value="promotional">Promotional</option>
          <option value="religious">Religious</option>
        </select>
        <select
          v-model="filterActive"
          class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 bg-white"
          @change="loadSpecialDays()"
        >
          <option value="">All statuses</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
        <label class="flex items-center gap-2 text-sm text-neutral-600">
          <input v-model="filterUpcoming" type="checkbox" class="rounded" @change="loadSpecialDays()" />
          Upcoming only
        </label>
        <div class="ml-auto">
          <button
            class="inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 transition-colors"
            @click="showCreateForm = !showCreateForm"
          >
            <Plus class="size-4" />
            Add special day
          </button>
        </div>
      </div>

      <!-- Create form -->
      <div v-if="showCreateForm" class="bg-white rounded-lg border border-neutral-200 p-5 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-neutral-900">New Special Day</h3>
          <button class="text-neutral-400 hover:text-neutral-600" @click="showCreateForm = false">
            <X class="size-4" />
          </button>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <label class="col-span-2 space-y-1">
            <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Name *</span>
            <input v-model="createForm.name" type="text" placeholder="e.g. Christmas Day"
              class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
          </label>
          <label class="space-y-1">
            <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Date *</span>
            <input v-model="createForm.date" type="date"
              class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
          </label>
          <label class="space-y-1">
            <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Type</span>
            <select v-model="createForm.event_type"
              class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 bg-white">
              <option value="holiday">Holiday</option>
              <option value="observance">Observance</option>
              <option value="cultural">Cultural</option>
              <option value="promotional">Promotional</option>
              <option value="religious">Religious</option>
            </select>
          </label>
          <label class="space-y-1">
            <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Priority (1–10)</span>
            <input v-model.number="createForm.priority" type="number" min="1" max="10"
              class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
          </label>
          <label class="space-y-1">
            <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Country codes (comma-sep)</span>
            <input v-model="createForm.countries" type="text" placeholder="US, GB, CA"
              class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900" />
          </label>
          <label class="col-span-2 space-y-1">
            <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">Description</span>
            <textarea v-model="createForm.description" rows="2"
              class="w-full text-sm px-3 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none" />
          </label>
          <div class="col-span-2 flex flex-wrap gap-4 text-sm">
            <label class="flex items-center gap-2">
              <input v-model="createForm.is_annual" type="checkbox" class="rounded" />
              Annual event
            </label>
            <label class="flex items-center gap-2">
              <input v-model="createForm.is_international" type="checkbox" class="rounded" />
              International
            </label>
            <label class="flex items-center gap-2">
              <input v-model="createForm.is_active" type="checkbox" class="rounded" />
              Active
            </label>
          </div>
        </div>
        <p v-if="createError" class="text-sm text-berry-600">{{ createError }}</p>
        <button
          class="inline-flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-50 transition-colors"
          :disabled="createLoading"
          @click="submitCreateSpecialDay"
        >
          <Loader2 v-if="createLoading" class="size-4 animate-spin" />
          <Plus v-else class="size-4" />
          Create
        </button>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-lg border border-neutral-200 overflow-hidden">
        <div v-if="specialDaysLoading" class="p-8 flex justify-center">
          <Loader2 class="size-7 text-neutral-300 animate-spin" />
        </div>
        <div v-else-if="specialDays.length === 0" class="p-8 text-center text-neutral-400 text-sm">
          No special days found.
        </div>
        <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-neutral-50 border-b border-neutral-100">
            <tr>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Name</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Date</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Type</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Countries</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Days Until</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Status</th>
              <th class="px-3 py-2" />
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-50">
            <tr v-for="day in specialDays" :key="day.id" class="hover:bg-neutral-50 transition-colors">
              <td class="px-3 py-2">
                <div class="font-medium text-neutral-900">{{ day.name }}</div>
                <div v-if="day.description" class="text-xs text-neutral-400 truncate max-w-[200px]">{{ day.description }}</div>
              </td>
              <td class="px-3 py-2 text-neutral-600">
                <div>{{ new Date(day.event_date_this_year).toLocaleDateString("en-US", { month: "short", day: "numeric" }) }}</div>
                <div v-if="day.is_annual" class="text-xs text-neutral-400">Annual</div>
              </td>
              <td class="px-3 py-2">
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-neutral-100 text-neutral-700 text-xs capitalize">
                  <Tag class="size-3" />
                  {{ day.event_type }}
                </span>
              </td>
              <td class="px-3 py-2">
                <div v-if="day.is_international" class="flex items-center gap-1 text-xs text-signal-600">
                  <Globe class="size-3.5" />
                  International
                </div>
                <div v-else-if="day.countries_display?.length" class="flex items-center gap-1 text-xs text-neutral-600">
                  <MapPin class="size-3.5" />
                  {{ day.countries_display.slice(0, 3).join(", ") }}
                  <span v-if="day.countries_display.length > 3" class="text-neutral-400">+{{ day.countries_display.length - 3 }}</span>
                </div>
                <span v-else class="text-xs text-neutral-400">—</span>
              </td>
              <td class="px-3 py-2">
                <span :class="daysUntilTone(day.days_until)">
                  {{ day.days_until < 0 ? "Passed" : day.days_until === 0 ? "Today" : `${day.days_until}d` }}
                </span>
              </td>
              <td class="px-3 py-2">
                <StatusPill :label="day.is_active ? 'active' : 'inactive'" :tone="day.is_active ? 'success' : 'neutral'" />
              </td>
              <td class="px-3 py-2">
                <div class="flex items-center gap-2">
                  <button
                    class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors text-neutral-600 disabled:opacity-50"
                    :disabled="generatingDiscountFor === day.id"
                    :title="`Generate ${new Date().getFullYear()} discount campaign`"
                    @click="generateDiscount(day.id)"
                  >
                    <Loader2 v-if="generatingDiscountFor === day.id" class="size-3 animate-spin" />
                    <Percent v-else class="size-3" />
                    Discount
                  </button>
                  <template v-if="pendingDeleteDayId === day.id">
                    <button class="focus-ring rounded bg-rose-600 px-2 py-0.5 text-xs font-semibold text-white" type="button" @click="deleteSpecialDay(day.id)">Confirm</button>
                    <button class="focus-ring rounded border border-slate-200 px-2 py-0.5 text-xs text-graphite" type="button" @click="pendingDeleteDayId = null">Cancel</button>
                  </template>
                  <button
                    v-else
                    class="p-1 rounded hover:bg-red-50 text-neutral-400 hover:text-berry-600 transition-colors"
                    @click="deleteSpecialDay(day.id)"
                  >
                    <Trash2 class="size-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </template>

    <!-- ── REMINDERS ──────────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'reminders'">
      <div class="flex flex-wrap items-center gap-3">
        <select
          v-model="filterReminderStatus"
          class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 bg-white"
          @change="loadReminders()"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="sent">Sent</option>
        </select>
        <div class="flex items-center gap-2 ml-auto">
          <button
            class="inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors disabled:opacity-50"
            :disabled="checkingReminders"
            @click="checkAndCreate"
          >
            <Loader2 v-if="checkingReminders" class="size-4 animate-spin" />
            <CheckCircle2 v-else class="size-4" />
            Check &amp; auto-create
          </button>
          <button
            class="inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 transition-colors disabled:opacity-50"
            :disabled="notifyingAdmins"
            @click="notifyAdmins"
          >
            <Loader2 v-if="notifyingAdmins" class="size-4 animate-spin" />
            <Bell v-else class="size-4" />
            Notify admins
          </button>
        </div>
      </div>

      <div v-if="reminderFeedback" class="flex items-center justify-between px-4 py-2 rounded-lg bg-signal-50 border border-signal-200 text-sm text-signal-800">
        {{ reminderFeedback }}
        <button class="text-signal-500 hover:text-signal-700" @click="reminderFeedback = ''"><X class="size-4" /></button>
      </div>

      <div class="bg-white rounded-lg border border-neutral-200 overflow-hidden">
        <div v-if="remindersLoading" class="p-8 flex justify-center">
          <Loader2 class="size-7 text-neutral-300 animate-spin" />
        </div>
        <div v-else-if="reminders.length === 0" class="p-8 text-center text-neutral-400 text-sm">
          No reminders found. Use "Check &amp; auto-create" to scan for upcoming holidays.
        </div>
        <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-neutral-50 border-b border-neutral-100">
            <tr>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Special Day</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Reminder Date</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Sent To</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Status</th>
              <th class="text-left px-3 py-2 font-medium text-neutral-500 text-xs uppercase tracking-wide">Discount</th>
              <th class="px-3 py-2" />
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-50">
            <tr v-for="r in reminders" :key="r.id" class="hover:bg-neutral-50 transition-colors">
              <td class="px-3 py-2">
                <div class="font-medium text-neutral-900">{{ r.special_day_name }}</div>
                <div v-if="r.special_day_date" class="text-xs text-neutral-400">
                  {{ new Date(r.special_day_date).toLocaleDateString("en-US", { month: "short", day: "numeric" }) }}
                </div>
              </td>
              <td class="px-3 py-2 text-neutral-600">
                <div class="flex items-center gap-1">
                  <Clock3 class="size-3.5 text-neutral-400" />
                  {{ new Date(r.reminder_date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) }}
                </div>
              </td>
              <td class="px-3 py-2 text-neutral-500 text-xs">{{ r.sent_to_username ?? "—" }}</td>
              <td class="px-3 py-2">
                <StatusPill :label="r.status" :tone="reminderStatusTone(r.status)" />
              </td>
              <td class="px-3 py-2">
                <span v-if="r.discount_created" class="inline-flex items-center gap-1 text-xs text-signal-700 font-medium">
                  <CheckCircle2 class="size-3.5" />
                  {{ r.discount_code }}
                </span>
                <span v-else class="text-xs text-neutral-400">None yet</span>
              </td>
              <td class="px-3 py-2">
                <div class="flex items-center gap-2">
                  <button
                    v-if="r.status === 'pending'"
                    class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors text-neutral-600 disabled:opacity-50"
                    :disabled="markingId === r.id"
                    @click="markSent(r.id)"
                  >
                    <Loader2 v-if="markingId === r.id" class="size-3 animate-spin" />
                    <Send v-else class="size-3" />
                    Mark sent
                  </button>
                  <button
                    v-if="!r.discount_created"
                    class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors text-neutral-600 disabled:opacity-50"
                    :disabled="discountCreatingId === r.id"
                    @click="createReminderDiscount(r.id)"
                  >
                    <Loader2 v-if="discountCreatingId === r.id" class="size-3 animate-spin" />
                    <Percent v-else class="size-3" />
                    Create discount
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </template>

    <!-- ── CAMPAIGNS ─────────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'campaigns'">
      <div class="flex flex-wrap items-center gap-3">
        <input
          v-model="filterYear"
          type="number"
          min="2020"
          max="2030"
          class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 bg-white w-28"
          placeholder="Year"
          @change="loadCampaigns()"
        />
        <select
          v-model="filterCampaignActive"
          class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 bg-white"
          @change="loadCampaigns()"
        >
          <option value="">All statuses</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <div class="bg-white rounded-lg border border-neutral-200 overflow-hidden">
        <div v-if="campaignsLoading" class="p-8 flex justify-center">
          <Loader2 class="size-7 text-neutral-300 animate-spin" />
        </div>
        <div v-else-if="campaigns.length === 0" class="p-8 text-center text-neutral-400 text-sm">
          No discount campaigns for this period. Generate one via a special day or reminder.
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
          <div
            v-for="c in campaigns"
            :key="c.id"
            class="rounded-xl border p-4 space-y-3"
            :class="c.is_active ? 'border-signal-200 bg-signal-50' : 'border-neutral-200 bg-white'"
          >
            <div class="flex items-start justify-between gap-2">
              <div>
                <p class="text-sm font-semibold text-neutral-900">{{ c.special_day_name }}</p>
                <p class="text-xs text-neutral-400">{{ c.year }}</p>
              </div>
              <StatusPill :label="c.is_active ? 'active' : 'inactive'" :tone="c.is_active ? 'success' : 'neutral'" />
            </div>
            <div class="space-y-1.5">
              <div v-if="c.discount_code" class="flex items-center gap-2">
                <Tag class="size-3.5 text-neutral-400" />
                <code class="text-xs font-mono bg-neutral-100 px-2 py-0.5 rounded">{{ c.discount_code }}</code>
              </div>
              <div v-if="c.discount_percentage" class="flex items-center gap-2">
                <Percent class="size-3.5 text-neutral-400" />
                <span class="text-sm font-medium text-neutral-800">{{ c.discount_percentage }}% off</span>
              </div>
              <div v-if="c.created_by_username" class="flex items-center gap-2">
                <Star class="size-3.5 text-neutral-400" />
                <span class="text-xs text-neutral-500">by {{ c.created_by_username }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
