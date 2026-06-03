<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-4xl space-y-5">
      <div>
        <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
          <ArrowLeft class="size-3.5" />
          Back to Classes
        </button>
        <h1 class="text-2xl font-bold text-ink">Start Class Management</h1>
        <p class="mt-1 text-sm text-graphite">Choose what you need, share the course context, and we will review the scope before pricing.</p>
      </div>

      <div v-if="loadingConfigs" class="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-graphite">
        Loading class options…
      </div>

      <div v-else class="grid gap-5 lg:grid-cols-[1fr_18rem]">
        <div class="space-y-5">
          <section class="rounded-lg border border-slate-200 bg-white p-5">
            <h2 class="text-sm font-semibold uppercase tracking-wide text-graphite">1. Choose support type</h2>
            <div class="mt-3 grid gap-3 sm:grid-cols-2">
              <button
                v-for="cfg in configs"
                :key="cfg.id"
                class="rounded-lg border-2 p-4 text-left transition hover:border-berry"
                :class="selectedConfig?.id === cfg.id ? 'border-berry bg-berry/5' : 'border-slate-200 bg-white'"
                @click="selectConfig(cfg)"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="font-semibold text-ink">{{ cfg.name }}</p>
                    <p class="mt-1 text-xs leading-5 text-graphite">{{ cfg.description }}</p>
                  </div>
                  <Check v-if="selectedConfig?.id === cfg.id" class="size-4 shrink-0 text-berry" />
                </div>
                <p class="mt-3 text-xs font-medium text-graphite">
                  {{ cfg.pricing_mode === "package" ? `From $${cfg.base_price}` : "Quote after review" }}
                </p>
              </button>
            </div>
          </section>

          <section class="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
            <h2 class="text-sm font-semibold uppercase tracking-wide text-graphite">2. Course details</h2>
            <div>
              <label class="mb-1 block text-sm font-medium text-ink">Course / Class Title <span class="text-rose-500">*</span></label>
              <input v-model="form.title" placeholder="e.g. MATH 301 - Linear Algebra" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label class="mb-1 block text-sm font-medium text-ink">Subject Area <span class="text-rose-500">*</span></label>
                <select v-if="subjects.length" v-model="form.subject" class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus-ring">
                  <option value="">Select subject…</option>
                  <option v-for="s in subjects" :key="s.id" :value="s.name">{{ s.name }}</option>
                </select>
                <input v-else v-model="form.subject" placeholder="e.g. Nursing, Business, Statistics" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-ink">Academic Level <span class="text-rose-500">*</span></label>
                <select v-model="form.academic_level" class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus-ring">
                  <option value="">Select level…</option>
                  <template v-if="academicLevels.length">
                    <option v-for="lvl in academicLevels" :key="lvl.id" :value="lvl.name">{{ lvl.name }}</option>
                  </template>
                  <template v-else>
                    <option value="High School">High School</option>
                    <option value="Undergraduate">Undergraduate</option>
                    <option value="Graduate">Graduate</option>
                    <option value="PhD">PhD / Doctoral</option>
                  </template>
                </select>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label class="mb-1 block text-sm font-medium text-ink">Course Start Date <span class="text-rose-500">*</span></label>
                <input v-model="form.start_date" type="date" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-ink">Course End Date <span class="text-rose-500">*</span></label>
                <input v-model="form.end_date" type="date" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
              </div>
            </div>
          </section>

          <section v-if="selectedConfig" class="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
            <h2 class="text-sm font-semibold uppercase tracking-wide text-graphite">3. Scope</h2>

            <div v-if="durationOptions.length">
              <label class="mb-2 block text-sm font-medium text-ink">Course duration</label>
              <div class="grid gap-2 sm:grid-cols-3">
                <button
                  v-for="opt in durationOptions"
                  :key="opt.key"
                  class="rounded-lg border-2 px-3 py-3 text-left text-sm transition hover:border-berry"
                  :class="form.duration_key === opt.key ? 'border-berry bg-berry/5' : 'border-slate-200'"
                  @click="form.duration_key = opt.key"
                >
                  <span class="font-semibold text-ink">{{ opt.label }}</span>
                  <span v-if="opt.description" class="mt-1 block text-xs text-graphite">{{ opt.description }}</span>
                </button>
              </div>
            </div>

            <div v-if="workloadOptions.length">
              <label class="mb-2 block text-sm font-medium text-ink">Expected workload</label>
              <div class="grid gap-2 sm:grid-cols-2">
                <button
                  v-for="opt in workloadOptions"
                  :key="opt.key"
                  class="rounded-lg border-2 px-3 py-3 text-left text-sm transition hover:border-berry"
                  :class="form.workload_key === opt.key ? 'border-berry bg-berry/5' : 'border-slate-200'"
                  @click="form.workload_key = opt.key"
                >
                  <span class="font-semibold text-ink">{{ opt.label }}</span>
                  <span v-if="opt.description" class="mt-1 block text-xs text-graphite">{{ opt.description }}</span>
                  <span v-if="opt.price_hint" class="mt-2 block text-xs font-medium text-graphite">{{ opt.price_hint }}</span>
                </button>
              </div>
            </div>

            <div v-if="taskOptions.length">
              <label class="mb-2 block text-sm font-medium text-ink">Likely work included</label>
              <div class="grid gap-2 sm:grid-cols-2">
                <label
                  v-for="opt in taskOptions"
                  :key="opt.key"
                  class="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-200 px-3 py-3 hover:bg-slate-50"
                  :class="{ 'bg-slate-50': opt.required }"
                  @click.prevent="toggleTask(opt)"
                >
                  <input
                    :checked="form.selected_task_keys.includes(opt.key)"
                    :disabled="opt.required"
                    type="checkbox"
                    class="mt-0.5 size-4 rounded accent-berry disabled:opacity-60"
                  />
                  <span>
                    <span class="block text-sm font-medium text-ink">
                      {{ opt.label }}
                      <span v-if="opt.required" class="font-normal text-graphite">(required)</span>
                    </span>
                    <span v-if="opt.description" class="block text-xs text-graphite">{{ opt.description }}</span>
                  </span>
                </label>
              </div>
            </div>

            <label class="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-200 p-4 hover:bg-slate-50">
              <input v-model="form.portal_access_enabled" type="checkbox" class="mt-0.5 size-4 rounded accent-berry" />
              <span>
                <span class="block text-sm font-medium text-ink">This class uses an online portal / LMS</span>
                <span class="mt-0.5 block text-xs text-graphite">Canvas, Blackboard, Moodle, Pearson, McGraw Hill, or a similar platform.</span>
              </span>
            </label>
          </section>

          <section class="rounded-lg border border-slate-200 bg-white p-5">
            <label class="mb-1 block text-sm font-medium text-ink">Additional Notes <span class="font-normal text-graphite">(optional)</span></label>
            <textarea
              v-model="form.notes"
              rows="5"
              placeholder="Paste syllabus links, grading breakdown, weekly rhythm, platform details, or anything else that helps us price and assign correctly…"
              class="w-full resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
            />
          </section>

          <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

          <div class="flex gap-3">
            <button
              class="rounded-lg bg-berry px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-berry/90 disabled:opacity-60"
              :disabled="isSaving || !isValid"
              @click="submit"
            >
              {{ isSaving ? "Submitting…" : "Submit Class Request" }}
            </button>
            <button class="rounded-lg border border-slate-200 px-5 py-2.5 text-sm text-graphite transition-colors hover:bg-slate-50 hover:text-ink" @click="router.back()">
              Cancel
            </button>
          </div>
        </div>

        <aside class="space-y-4">
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-sm font-semibold text-ink">Selected setup</p>
            <dl class="mt-3 space-y-2 text-sm">
              <div class="flex justify-between gap-3">
                <dt class="text-graphite">Service</dt>
                <dd class="text-right font-medium text-ink">{{ selectedConfig?.name ?? "Not selected" }}</dd>
              </div>
              <div class="flex justify-between gap-3">
                <dt class="text-graphite">Pricing</dt>
                <dd class="text-right font-medium text-ink">{{ pricingLabel }}</dd>
              </div>
              <div v-if="selectedDuration" class="flex justify-between gap-3">
                <dt class="text-graphite">Duration</dt>
                <dd class="text-right font-medium text-ink">{{ selectedDuration.label }}</dd>
              </div>
              <div v-if="selectedWorkload" class="flex justify-between gap-3">
                <dt class="text-graphite">Workload</dt>
                <dd class="text-right font-medium text-ink">{{ selectedWorkload.label }}</dd>
              </div>
              <div class="flex justify-between gap-3">
                <dt class="text-graphite">Deposit</dt>
                <dd class="text-right font-medium text-ink">{{ selectedConfig ? `${selectedConfig.deposit_percentage}%` : "—" }}</dd>
              </div>
              <div class="flex justify-between gap-3">
                <dt class="text-graphite">Installments</dt>
                <dd class="text-right font-medium text-ink">{{ selectedConfig?.allow_installments ? "Allowed" : "Not allowed" }}</dd>
              </div>
            </dl>
            <div v-if="selectedTasks.length" class="mt-4 border-t border-slate-100 pt-3">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Included work</p>
              <div class="mt-2 flex flex-wrap gap-1.5">
                <span
                  v-for="task in selectedTasks"
                  :key="task.key"
                  class="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-graphite"
                >
                  {{ task.label }}
                </span>
              </div>
            </div>
          </div>

          <PaymentDisclosureBanner />

          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-sm font-semibold text-ink">What happens next?</p>
            <div class="mt-3 space-y-2 text-sm text-graphite">
              <p>1. We review the selected scope and course context.</p>
              <p>2. You receive a price proposal based on the configured rules.</p>
              <p>3. Once you approve and pay the required amount, work begins.</p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, Check } from "@lucide/vue";
import PaymentDisclosureBanner from "@/components/payment/PaymentDisclosureBanner.vue";
import { classesApi } from "@/api/classes";
import { orderConfigApi } from "@/api/orderConfig";
import { useAuthStore } from "@/stores/auth";
import type { ClassConfigOption, ClassServiceConfig } from "@/types/classes";
import type { OrderConfigOption } from "@/types/config";

const router = useRouter();
const auth = useAuthStore();

const subjects = ref<OrderConfigOption[]>([]);
const academicLevels = ref<OrderConfigOption[]>([]);
const configs = ref<ClassServiceConfig[]>([]);
const selectedConfig = ref<ClassServiceConfig | null>(null);
const loadingConfigs = ref(true);
const isSaving = ref(false);
const error = ref<string | null>(null);

const fallbackConfigs: ClassServiceConfig[] = [
  {
    id: 0,
    name: "Full class management",
    slug: "full-class-management",
    description: "Ongoing class support for assignments, discussions, quizzes, exams, and routine course tasks.",
    service_type: "full_class",
    pricing_mode: "quote",
    base_price: "0.00",
    currency: "USD",
    duration_options: [
      { key: "4_weeks", label: "4 weeks" },
      { key: "8_weeks", label: "8 weeks" },
      { key: "12_weeks", label: "12 weeks" },
      { key: "semester", label: "Full semester" },
    ],
    workload_options: [
      { key: "light", label: "Light", complexity: "low", description: "A few weekly tasks and low complexity." },
      { key: "standard", label: "Standard", complexity: "medium", description: "Typical weekly assignments and discussions." },
      { key: "heavy", label: "Heavy", complexity: "high", description: "Frequent assignments, quizzes, exams, or papers." },
    ],
    task_options: [
      { key: "assignments", label: "Assignments" },
      { key: "discussions", label: "Discussion posts" },
      { key: "quizzes", label: "Quizzes" },
      { key: "exams", label: "Exams" },
      { key: "papers", label: "Papers / reports" },
      { key: "projects", label: "Projects" },
    ],
    required_fields: [],
    requires_portal_access: true,
    allow_installments: true,
    require_deposit_before_start: true,
    deposit_percentage: "50.00",
    quote_expiry_hours: 72,
    is_active: true,
    display_order: 0,
  },
];

const form = ref({
  title: "",
  subject: "",
  academic_level: "",
  start_date: "",
  end_date: "",
  duration_key: "",
  workload_key: "",
  selected_task_keys: [] as string[],
  notes: "",
  portal_access_enabled: false,
});

const durationOptions = computed<ClassConfigOption[]>(() => selectedConfig.value?.duration_options ?? []);
const workloadOptions = computed<ClassConfigOption[]>(() => selectedConfig.value?.workload_options ?? []);
const taskOptions = computed<ClassConfigOption[]>(() => selectedConfig.value?.task_options ?? []);
const selectedDuration = computed(() =>
  durationOptions.value.find((opt) => opt.key === form.value.duration_key) ?? null,
);
const selectedWorkload = computed(() =>
  workloadOptions.value.find((opt) => opt.key === form.value.workload_key) ?? null,
);
const selectedTasks = computed(() =>
  taskOptions.value.filter((opt) => form.value.selected_task_keys.includes(opt.key)),
);

const pricingLabel = computed(() => {
  if (!selectedConfig.value) return "—";
  if (selectedConfig.value.pricing_mode === "package" && Number(selectedConfig.value.base_price) > 0) {
    return `From $${selectedConfig.value.base_price}`;
  }
  return `Quote expires in ${selectedConfig.value.quote_expiry_hours}h`;
});

const isValid = computed(() =>
  Boolean(
    selectedConfig.value &&
    form.value.title.trim() &&
    form.value.subject.trim() &&
    form.value.academic_level &&
    form.value.start_date &&
    form.value.end_date &&
    (!durationOptions.value.length || form.value.duration_key) &&
    (!workloadOptions.value.length || form.value.workload_key),
  ),
);

function selectConfig(cfg: ClassServiceConfig) {
  selectedConfig.value = cfg;
  form.value.duration_key = cfg.duration_options[0]?.key ?? "";
  form.value.workload_key = cfg.workload_options[0]?.key ?? "";
  form.value.selected_task_keys = cfg.task_options.filter((t) => t.required).map((t) => t.key);
  form.value.portal_access_enabled = cfg.requires_portal_access;
}

function toggleTask(opt: ClassConfigOption) {
  if (opt.required) return;
  const keys = new Set(form.value.selected_task_keys);
  if (keys.has(opt.key)) {
    keys.delete(opt.key);
  } else {
    keys.add(opt.key);
  }
  form.value.selected_task_keys = [...keys];
}

async function submit() {
  if (!isValid.value || !selectedConfig.value) return;
  isSaving.value = true;
  error.value = null;
  try {
    if (auth.isPreviewSession) {
      router.push("/client/classes");
      return;
    }
    const res = await classesApi.create({
      title: form.value.title,
      subject: form.value.subject,
      academic_level: form.value.academic_level,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      notes: form.value.notes || undefined,
      portal_access_enabled: form.value.portal_access_enabled,
      class_config_id: selectedConfig.value.id || undefined,
      duration_key: form.value.duration_key,
      workload_key: form.value.workload_key,
      selected_task_keys: form.value.selected_task_keys,
    });
    router.push(`/client/classes/${res.data.id}`);
  } catch {
    error.value = "Failed to submit your request. Please try again.";
  } finally {
    isSaving.value = false;
  }
}

onMounted(async () => {
  try {
    const [subjectList, levelList, configRes] = await Promise.all([
      orderConfigApi.subjects({ is_active: true }),
      orderConfigApi.academicLevels({ is_active: true }),
      auth.isPreviewSession ? Promise.resolve({ data: fallbackConfigs }) : classesApi.configs(),
    ]);
    subjects.value = subjectList;
    academicLevels.value = levelList;
    configs.value = configRes.data.length ? configRes.data : fallbackConfigs;
    selectConfig(configs.value[0]);
  } catch {
    configs.value = fallbackConfigs;
    selectConfig(fallbackConfigs[0]);
  } finally {
    loadingConfigs.value = false;
  }
});
</script>
