<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-5xl space-y-4">

      <div v-if="store.isLoadingDetail" class="py-24 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else-if="store.detail">
        <!-- Back + header -->
        <div>
          <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
            <ArrowLeft class="size-3.5" /> Classes
          </button>
          <div class="rounded-lg border border-slate-200 bg-white p-6">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass(store.detail.status)">
                    {{ statusLabel(store.detail.status) }}
                  </span>
                  <span class="font-mono text-xs text-graphite">{{ store.detail.reference }}</span>
                </div>
                <h1 class="mt-2 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
                <p class="mt-0.5 text-sm text-graphite">{{ store.detail.subject }} · {{ store.detail.academic_level }}</p>
                <div class="mt-3 flex flex-wrap items-center gap-4 text-xs text-graphite">
                  <span class="flex items-center gap-1.5">
                    <Calendar class="size-3.5" />
                    {{ fmtDate(store.detail.start_date) }} — {{ fmtDate(store.detail.end_date) }}
                  </span>
                  <span class="flex items-center gap-1.5">
                    <UserCheck class="size-3.5" />
                    Client: <strong class="text-ink">{{ store.detail.client_username }}</strong>
                  </span>
                  <span v-if="store.detail.writer_username" class="flex items-center gap-1.5 text-emerald-700">
                    <Check class="size-3.5" />
                    Writer: {{ store.detail.writer_username }}
                  </span>
                  <span v-else class="flex items-center gap-1.5 text-amber-600">
                    <AlertCircle class="size-3.5" />
                    Unassigned
                  </span>
                </div>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-2xl font-bold text-ink">${{ store.detail.total_price }}</p>
                <p class="mt-0.5 text-xs capitalize text-graphite">{{ store.detail.payment_status }}</p>
              </div>
            </div>

            <!-- Progress bar -->
            <div class="mt-5">
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span class="text-graphite">{{ store.detail.completed_tasks }} of {{ store.detail.total_tasks }} tasks done</span>
                <span class="font-semibold text-ink">{{ progressPct }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="progressPct === 100 ? 'bg-emerald-500' : 'bg-berry'"
                  :style="{ width: `${progressPct}%` }"
                />
              </div>
            </div>

            <!-- Lifecycle actions (admin/superadmin only — support is view-only) -->
            <div v-if="canManage" class="mt-5 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
              <button
                v-if="!store.detail.writer_username"
                class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
                :disabled="store.isSaving"
                @click="showAssign = !showAssign"
              >
                <UserPlus class="size-3.5" />
                Assign Writer
              </button>
              <template v-if="['pending', 'active'].includes(store.detail.status)">
                <template v-if="pendingCancelClass">
                  <button
                    class="inline-flex items-center gap-1.5 rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-rose-700 disabled:opacity-60"
                    :disabled="store.isSaving"
                    type="button"
                    @click="cancelClass"
                  >Confirm cancel</button>
                  <button
                    class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50"
                    type="button"
                    @click="pendingCancelClass = false"
                  >Keep class</button>
                </template>
                <button
                  v-else
                  class="inline-flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-60"
                  :disabled="store.isSaving"
                  @click="cancelClass"
                >
                  <XCircle class="size-3.5" />
                  Cancel Class
                </button>
              </template>
            </div>

            <!-- Assign writer inline form -->
            <div v-if="showAssign" class="mt-4 flex items-end gap-3 rounded-lg bg-slate-50 p-4">
              <div class="flex-1">
                <label class="block text-xs font-medium text-graphite mb-1">Writer ID</label>
                <input v-model="writerIdInput" type="number" placeholder="e.g. 42" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
              </div>
              <button
                class="inline-flex items-center gap-1.5 rounded-lg bg-berry px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-60"
                :disabled="store.isSaving || !writerIdInput"
                @click="confirmAssign"
              >
                <Check class="size-4" /> Assign
              </button>
              <button class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-graphite hover:text-ink" @click="showAssign = false">
                Cancel
              </button>
            </div>
          </div>
        </div>

        <!-- Summary cards -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Total</p>
            <p class="mt-1 text-lg font-bold text-ink">${{ store.detail.total_price }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Tasks</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.completed_tasks }}<span class="text-sm font-normal text-graphite">/{{ store.detail.total_tasks }}</span></p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Payment</p>
            <p class="mt-1 text-sm font-semibold capitalize text-graphite">{{ store.detail.payment_status }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Portal access</p>
            <p class="mt-1 text-sm font-semibold" :class="store.detail.portal_access_enabled ? 'text-emerald-700' : 'text-graphite'">
              {{ store.detail.portal_access_enabled ? 'Enabled' : 'Not set' }}
            </p>
          </div>
        </div>

        <section v-if="pricingSnapshot" class="rounded-lg border border-slate-200 bg-white p-5">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Scope & pricing preset</p>
              <h2 class="mt-1 text-base font-semibold text-ink">{{ pricingSnapshot.config_name || "Configured class request" }}</h2>
              <p class="mt-1 text-sm text-graphite">
                {{ snapshotPricingLabel }}
              </p>
            </div>
            <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-graphite">
              {{ labelize(String(pricingSnapshot.pricing_mode || "quote")) }}
            </span>
          </div>

          <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-3">
              <p class="text-xs text-graphite">Duration</p>
              <p class="mt-1 font-semibold text-ink">{{ pricingSnapshot.selected_duration?.label || "Not selected" }}</p>
              <p v-if="pricingSnapshot.selected_duration?.description" class="mt-1 text-xs text-graphite">{{ pricingSnapshot.selected_duration.description }}</p>
            </div>
            <div class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-3">
              <p class="text-xs text-graphite">Workload</p>
              <p class="mt-1 font-semibold text-ink">{{ pricingSnapshot.selected_workload?.label || "Not selected" }}</p>
              <p v-if="pricingSnapshot.selected_workload?.description" class="mt-1 text-xs text-graphite">{{ pricingSnapshot.selected_workload.description }}</p>
            </div>
            <div class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-3">
              <p class="text-xs text-graphite">Deposit</p>
              <p class="mt-1 font-semibold text-ink">{{ pricingSnapshot.payment_policy?.deposit_percentage || "0.00" }}%</p>
              <p class="mt-1 text-xs text-graphite">{{ pricingSnapshot.payment_policy?.require_deposit_before_start ? "Required before start" : "Flexible start policy" }}</p>
            </div>
            <div class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-3">
              <p class="text-xs text-graphite">Portal access</p>
              <p class="mt-1 font-semibold" :class="pricingSnapshot.portal_access_enabled ? 'text-emerald-700' : 'text-graphite'">
                {{ pricingSnapshot.portal_access_enabled ? "Expected" : "Not expected" }}
              </p>
              <p class="mt-1 text-xs text-graphite">{{ pricingSnapshot.payment_policy?.allow_installments ? "Installments allowed" : "No installments" }}</p>
            </div>
          </div>

          <div v-if="snapshotTasks.length" class="mt-4 border-t border-slate-100 pt-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Selected work</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <span
                v-for="task in snapshotTasks"
                :key="task.key"
                class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-graphite"
              >
                {{ task.label }}<span v-if="task.required"> · required</span>
              </span>
            </div>
          </div>
        </section>

        <!-- Tabs -->
        <div class="flex gap-1 rounded-lg border border-slate-200 bg-white p-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition-colors"
            :class="activeTab === tab.key ? 'bg-berry text-white shadow-sm' : 'text-graphite hover:text-ink'"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <!-- Tasks tab -->
        <div v-if="activeTab === 'tasks'" class="space-y-3">
          <div v-if="!store.detail.tasks.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            No tasks yet.
          </div>
          <div
            v-for="task in store.detail.tasks"
            :key="task.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs text-graphite">#{{ task.sequence }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="taskStatusClass(task.status)">
                    {{ taskStatusLabel(task.status) }}
                  </span>
                </div>
                <h3 class="mt-1.5 font-semibold text-ink">{{ task.title }}</h3>
                <p class="mt-0.5 text-sm text-graphite">{{ task.description }}</p>
              </div>
              <p class="shrink-0 text-xs text-graphite">Due {{ fmtDate(task.due_date) }}</p>
            </div>

            <div v-if="task.submission_notes" class="mt-3 rounded-lg bg-slate-50 px-4 py-2.5 text-sm text-graphite">
              <span class="font-medium text-ink">Submission notes:</span> {{ task.submission_notes }}
            </div>

            <!-- Existing grade -->
            <div v-if="task.grade" class="mt-3 flex items-center gap-2 text-sm">
              <span class="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700">Grade: {{ task.grade }}</span>
              <span v-if="task.grade_feedback" class="text-graphite">{{ task.grade_feedback }}</span>
            </div>

            <!-- Grade inline form -->
            <div v-if="gradingTaskId === task.id" class="mt-4 space-y-2.5">
              <div class="flex gap-2">
                <input v-model="gradeValue" placeholder="Grade (e.g. A, B+, 92%)" class="w-40 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
                <input v-model="gradeFeedback" placeholder="Feedback (optional)" class="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
              </div>
              <div class="flex gap-2">
                <button
                  class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
                  :disabled="store.isSaving || !gradeValue.trim()"
                  @click="confirmGrade(task.id)"
                >
                  <Check class="size-4" /> Save Grade
                </button>
                <button class="rounded-lg border border-slate-200 px-4 py-1.5 text-sm text-graphite hover:text-ink" @click="gradingTaskId = null">Cancel</button>
              </div>
            </div>

            <div v-else-if="task.status === 'submitted'" class="mt-4">
              <button
                class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-700 hover:bg-emerald-100 transition-colors"
                @click="startGrade(task.id)"
              >
                <Award class="size-4" /> Grade Task
              </button>
            </div>
          </div>
        </div>

        <!-- Installments tab -->
        <div v-else-if="activeTab === 'installments'" class="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <div v-if="!store.detail.installments.length" class="py-14 text-center text-sm text-graphite">
            No installment schedule set.
          </div>
          <PaymentDisclosureBanner v-else class="m-4 mb-0" />
          <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-3 py-2 text-left">Payment</th>
                <th class="px-3 py-2 text-left">Due</th>
                <th class="px-3 py-2 text-right">Amount</th>
                <th class="px-3 py-2 text-center">Status</th>
                <th class="px-3 py-2 text-left">Reference</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="inst in store.detail.installments" :key="inst.id">
                <td class="px-3 py-2.5 font-medium text-ink">{{ inst.label }}</td>
                <td class="px-3 py-2.5 text-graphite">{{ fmtDate(inst.due_date) }}</td>
                <td class="px-3 py-2.5 text-right font-bold text-ink">${{ inst.amount }}</td>
                <td class="px-3 py-2.5 text-center">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="installmentStatusClass(inst.status)">
                    {{ inst.status }}
                  </span>
                </td>
                <td class="px-3 py-2.5 font-mono text-xs text-graphite">{{ inst.payment_reference ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>

        <!-- Portal Access tab -->
        <div v-else-if="activeTab === 'portal'" class="rounded-lg border border-slate-200 bg-white p-6">
          <div class="flex items-center gap-2 mb-4">
            <Globe class="size-4 text-blue-600" />
            <h3 class="font-semibold text-ink">Portal / LMS Access</h3>
          </div>
          <div v-if="store.detail.portal_access" class="space-y-3 rounded-lg bg-slate-50 px-5 py-4 text-sm">
            <div class="flex items-center gap-3">
              <span class="w-36 shrink-0 text-graphite">Status</span>
              <span :class="store.detail.portal_access.enabled ? 'text-emerald-700 font-semibold' : 'text-graphite'">
                {{ store.detail.portal_access.enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
            <div v-if="store.detail.portal_access.portal_url" class="flex items-center gap-3">
              <span class="w-36 shrink-0 text-graphite">URL</span>
              <a :href="store.detail.portal_access.portal_url" target="_blank" rel="noreferrer" class="flex items-center gap-1 text-berry hover:underline break-all">
                {{ store.detail.portal_access.portal_url }}
                <ExternalLink class="size-3 shrink-0" />
              </a>
            </div>
            <div v-if="store.detail.portal_access.username" class="flex items-center gap-3">
              <span class="w-36 shrink-0 text-graphite">Username</span>
              <span class="font-mono text-ink">{{ store.detail.portal_access.username }}</span>
            </div>
            <div v-if="store.detail.portal_access.password_hint" class="flex items-center gap-3">
              <span class="w-36 shrink-0 text-graphite">Password hint</span>
              <span class="text-ink">{{ store.detail.portal_access.password_hint }}</span>
            </div>
            <div v-if="store.detail.portal_access.notes" class="flex items-start gap-3">
              <span class="w-36 shrink-0 text-graphite">Notes</span>
              <span class="text-ink">{{ store.detail.portal_access.notes }}</span>
            </div>
            <div v-if="store.detail.portal_access.last_accessed_at" class="flex items-center gap-3 border-t border-slate-200 pt-3">
              <span class="w-36 shrink-0 text-graphite">Last accessed</span>
              <span class="text-graphite">{{ fmtDateTime(store.detail.portal_access.last_accessed_at) }}</span>
            </div>
          </div>
          <div v-else class="mt-4 rounded-lg border border-dashed border-slate-200 bg-slate-50 p-5 text-center">
            <p class="text-sm text-graphite">Portal access is not loaded.</p>
            <button
              class="focus-ring mt-3 inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
              :disabled="store.isSaving"
              @click="store.loadPortalAccess(store.detail.id).catch(() => undefined)"
            >
              {{ store.isSaving ? "Loading..." : "View access details" }}
            </button>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AlertCircle, ArrowLeft, Award, Calendar, Check, ExternalLink, Globe, UserCheck, UserPlus, XCircle } from "@lucide/vue";
import { useClassesStore } from "@/stores/classes";
import { useAuthStore } from "@/stores/auth";
import PaymentDisclosureBanner from "@/components/payment/PaymentDisclosureBanner.vue";
import type { ClassConfigOption, ClassPricingSnapshot, ClassStatus, ClassTaskStatus, InstallmentStatus } from "@/types/classes";

const route = useRoute();
const router = useRouter();
const store = useClassesStore();
const auth = useAuthStore();

// Support can view but cannot assign writers or modify the class — ops are admin-only.
const canManage = computed(() =>
  auth.role === "admin" || auth.role === "superadmin" || auth.isPreviewSession,
);

onMounted(() => store.loadDetail(route.params.id as string));

const tabs = [
  { key: "tasks", label: "Tasks" },
  { key: "installments", label: "Installments" },
  { key: "portal", label: "Portal Access" },
];
const activeTab = ref("tasks");

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
  pending: "Pending Review",
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

const taskStatusLabels: Partial<Record<ClassTaskStatus, string>> = {
  pending: "Pending",
  assigned: "Assigned",
  in_progress: "In Progress",
  submitted: "Submitted",
  revision_requested: "Revision",
  approved: "Approved",
  completed: "Completed",
  cancelled: "Cancelled",
};

const taskStatusClasses: Partial<Record<ClassTaskStatus, string>> = {
  pending: "bg-slate-100 text-graphite",
  assigned: "bg-blue-100 text-blue-700",
  in_progress: "bg-amber-100 text-amber-700",
  submitted: "bg-purple-100 text-purple-700",
  revision_requested: "bg-rose-100 text-rose-700",
  approved: "bg-emerald-100 text-emerald-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
};

const installmentStatusClasses: Partial<Record<InstallmentStatus, string>> = {
  pending: "bg-amber-100 text-amber-700",
  due: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  overdue: "bg-rose-100 text-rose-700",
  waived: "bg-slate-100 text-graphite",
  cancelled: "bg-slate-100 text-slate-400",
};

function labelize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function statusLabel(status: ClassStatus): string {
  return statusLabels[status] ?? labelize(status);
}

function statusClass(status: ClassStatus): string {
  return statusClasses[status] ?? "bg-slate-100 text-graphite";
}

function taskStatusLabel(status: ClassTaskStatus): string {
  return taskStatusLabels[status] ?? labelize(status);
}

function taskStatusClass(status: ClassTaskStatus): string {
  return taskStatusClasses[status] ?? "bg-slate-100 text-graphite";
}

function installmentStatusClass(status: InstallmentStatus): string {
  return installmentStatusClasses[status] ?? "bg-slate-100 text-graphite";
}

function formatMoney(amount: string | number, currency = "USD"): string {
  const numeric = Number(amount);
  if (!Number.isFinite(numeric)) return `${currency} ${amount}`;
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

const progressPct = computed(() => {
  const d = store.detail;
  if (!d || !d.total_tasks) return 0;
  return Math.round((d.completed_tasks / d.total_tasks) * 100);
});

const pricingSnapshot = computed<ClassPricingSnapshot | null>(() => {
  const snapshot = store.detail?.pricing_snapshot;
  return snapshot && Object.keys(snapshot).length ? snapshot : null;
});

const snapshotTasks = computed<ClassConfigOption[]>(() =>
  pricingSnapshot.value?.selected_tasks ?? [],
);

const snapshotPricingLabel = computed(() => {
  const snapshot = pricingSnapshot.value;
  if (!snapshot) return "";
  const currency = snapshot.currency || store.detail?.currency || "USD";
  const basePrice = Number(snapshot.base_price || 0);
  const quoteHours = snapshot.payment_policy?.quote_expiry_hours;
  if (snapshot.pricing_mode === "package" && basePrice > 0) {
    return `Package estimate starts at ${formatMoney(basePrice, currency)}.`;
  }
  if (quoteHours) return `Quote after review, valid for ${quoteHours} hours.`;
  return "Quote after review.";
});

// Grading
const gradingTaskId = ref<number | null>(null);
const gradeValue = ref("");
const gradeFeedback = ref("");

function startGrade(taskId: number) {
  gradingTaskId.value = taskId;
  gradeValue.value = "";
  gradeFeedback.value = "";
}

async function confirmGrade(taskId: number) {
  if (!store.detail) return;
  await store.gradeTask(store.detail.id, taskId, { grade: gradeValue.value, grade_feedback: gradeFeedback.value });
  gradingTaskId.value = null;
}

// Assign writer
const showAssign = ref(false);
const writerIdInput = ref<number | "">("");
const pendingCancelClass = ref(false);

async function confirmAssign() {
  if (!store.detail || !writerIdInput.value) return;
  await store.assignWriter(store.detail.id, Number(writerIdInput.value));
  showAssign.value = false;
  writerIdInput.value = "";
}

async function cancelClass() {
  if (!store.detail) return;
  if (!pendingCancelClass.value) { pendingCancelClass.value = true; return; }
  pendingCancelClass.value = false;
  await store.cancelClass(store.detail.id);
}

function fmtDate(v: string): string {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}

function fmtDateTime(v: string): string {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}
</script>
