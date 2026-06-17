<template>
  <section class="rounded-lg border border-slate-200 bg-white">
    <div class="grid gap-0 lg:grid-cols-[minmax(0,1fr)_340px]">
      <div class="p-5">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Writer brief</p>
            <h2 class="mt-1 text-xl font-semibold text-ink">{{ order.topic || "Untitled order" }}</h2>
            <p class="mt-1 text-sm text-graphite">
              Order {{ displayReference }} · {{ serviceLabel }}
            </p>
          </div>
          <span
            class="rounded-full px-3 py-1 text-xs font-semibold capitalize"
            :class="deadlineTone.badge"
          >
            {{ deadlineTone.label }}
          </span>
        </div>

        <div class="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <BriefMetric label="Pages" :value="pagesLabel" />
          <BriefMetric label="Slides" :value="slidesLabel" />
          <BriefMetric label="Designs" :value="designsLabel" />
          <BriefMetric label="Diagrams" :value="diagramsLabel" />
          <BriefMetric label="Citation" :value="citationLabel" />
          <BriefMetric label="Subject" :value="subjectLabel" />
          <BriefMetric label="Paper type" :value="paperTypeLabel" />
          <BriefMetric label="Academic level" :value="academicLevelLabel" />
          <BriefMetric label="Sources" :value="sourcesLabel" />
          <BriefMetric label="Your deadline" :value="writerDeadlineLabel" />
        </div>

        <div class="mt-5">
          <div class="flex items-center justify-between gap-3 text-xs font-semibold text-graphite">
            <span>Deadline progress</span>
            <span>{{ deadlineProgressLabel }}</span>
          </div>
          <div class="mt-2 h-2 rounded-full bg-slate-100">
            <div class="h-2 rounded-full transition-all" :class="deadlineTone.bar" :style="{ width: `${deadlineProgress}%` }" />
          </div>
        </div>

        <div class="mt-5 rounded-lg border border-slate-100 bg-slate-50 p-4">
          <div class="flex items-center gap-2">
            <FileText class="h-4 w-4 text-signal" />
            <p class="text-sm font-semibold text-ink">Full client instructions</p>
          </div>
          <div
            v-if="fullInstructions"
            class="mt-3 max-h-80 overflow-auto whitespace-pre-wrap rounded-md border border-slate-200 bg-white p-4 text-sm leading-6 text-ink"
          >
            {{ fullInstructions }}
          </div>
          <p v-else class="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            No typed or pasted instructions were attached. Check files, rubric, and messages before starting.
          </p>
        </div>

        <div class="mt-5 grid gap-3 lg:grid-cols-2">
          <div class="rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div class="flex items-center gap-2">
              <BookOpen class="h-4 w-4 text-signal" />
              <p class="text-sm font-semibold text-ink">Delivery expectations</p>
            </div>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="item in expectationChips"
                :key="item"
                class="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-graphite"
              >
                {{ item }}
              </span>
            </div>
          </div>

          <div class="rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div class="flex items-center gap-2">
              <ListChecks class="h-4 w-4 text-signal" />
              <p class="text-sm font-semibold text-ink">Addons to provide</p>
            </div>
            <div v-if="addonLabels.length" class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="addon in addonLabels"
                :key="addon"
                class="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-graphite"
              >
                {{ addon }}
              </span>
            </div>
            <p v-else class="mt-3 text-sm text-graphite">No explicit addons were attached to this brief.</p>
          </div>
        </div>

        <div class="mt-5 rounded-lg border border-slate-100 bg-slate-50 p-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <BookMarked class="h-4 w-4 text-signal" />
              <p class="text-sm font-semibold text-ink">Writer guides and resources</p>
            </div>
            <span v-if="files.isLoadingAttachments" class="text-xs font-medium text-graphite">Loading...</span>
          </div>
          <div v-if="writerGuides.length" class="mt-3 grid gap-2">
            <button
              v-for="guide in writerGuides"
              :key="guide.id"
              class="focus-ring flex w-full items-center justify-between gap-3 rounded-md border border-slate-200 bg-white px-3 py-2 text-left hover:border-signal/40 hover:bg-signal/5"
              type="button"
              @click="openGuide(guide)"
            >
              <span class="min-w-0">
                <span class="block truncate text-sm font-semibold text-ink">{{ guideTitle(guide) }}</span>
                <span class="mt-0.5 block text-xs capitalize text-graphite">
                  {{ String(guide.purpose).replace(/_/g, " ") }} · {{ guideKind(guide) }}
                </span>
              </span>
              <ExternalLink v-if="guide.external_link?.url" class="h-4 w-4 shrink-0 text-graphite" />
              <Download v-else class="h-4 w-4 shrink-0 text-graphite" />
            </button>
          </div>
          <p v-else class="mt-3 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-graphite">
            No writer-only guides are attached yet. Use the files tab for general references and uploaded rubrics.
          </p>
        </div>
      </div>

      <aside class="border-t border-slate-200 p-5 lg:border-l lg:border-t-0">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Your payout</p>
          <p class="mt-1 text-2xl font-semibold text-ink">{{ money(writerTotal) }}</p>
          <p class="mt-1 text-xs text-graphite">Shown as your payable amount only.</p>
        </div>

        <dl class="mt-4 space-y-2 text-sm">
          <div v-if="ratePerPage" class="flex items-center justify-between gap-3">
            <dt class="text-graphite">Per page</dt>
            <dd class="font-semibold text-ink">{{ moneyValue(ratePerPage) }}</dd>
          </div>
          <div v-if="ratePerSlide" class="flex items-center justify-between gap-3">
            <dt class="text-graphite">Per slide</dt>
            <dd class="font-semibold text-ink">{{ moneyValue(ratePerSlide) }}</dd>
          </div>
          <div v-if="ratePerDesign" class="flex items-center justify-between gap-3">
            <dt class="text-graphite">Per design</dt>
            <dd class="font-semibold text-ink">{{ moneyValue(ratePerDesign) }}</dd>
          </div>
          <div v-if="ratePerDiagram" class="flex items-center justify-between gap-3">
            <dt class="text-graphite">Per diagram</dt>
            <dd class="font-semibold text-ink">{{ moneyValue(ratePerDiagram) }}</dd>
          </div>
        </dl>

        <div class="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-3">
          <div class="flex items-start gap-2">
            <AlertTriangle class="mt-0.5 h-4 w-4 shrink-0 text-amber-700" />
            <p class="text-xs leading-5 text-amber-900">
              If the uploaded rubric requires more work than this brief shows, request a scope change before proceeding.
            </p>
          </div>
        </div>

        <div v-if="activeAdjustment" class="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Active scope request</p>
              <p class="mt-1 text-sm font-semibold text-ink">{{ activeAdjustment.title || adjustmentTypeLabel(activeAdjustment.adjustment_type) }}</p>
            </div>
            <span class="rounded-full px-2 py-1 text-[11px] font-semibold capitalize" :class="adjustmentStatusTone(activeAdjustment.status)">
              {{ String(activeAdjustment.status).replace(/_/g, " ") }}
            </span>
          </div>
          <dl class="mt-3 space-y-1.5 text-xs">
            <div class="flex items-center justify-between gap-3">
              <dt class="text-graphite">Requested</dt>
              <dd class="font-semibold text-ink">{{ activeAdjustment.requested_quantity ?? "N/A" }} {{ activeAdjustment.unit_type || "units" }}</dd>
            </div>
            <div v-if="activeAdjustment.countered_quantity" class="flex items-center justify-between gap-3">
              <dt class="text-graphite">Client counter</dt>
              <dd class="font-semibold text-ink">{{ activeAdjustment.countered_quantity }} {{ activeAdjustment.unit_type || "units" }}</dd>
            </div>
            <div class="flex items-center justify-between gap-3">
              <dt class="text-graphite">Your request pay</dt>
              <dd class="font-semibold text-ink">{{ adjustmentMoney(activeAdjustment.request_writer_compensation_amount) }}</dd>
            </div>
            <div v-if="activeAdjustment.counter_writer_compensation_amount" class="flex items-center justify-between gap-3">
              <dt class="text-graphite">Counter pay</dt>
              <dd class="font-semibold text-ink">{{ adjustmentMoney(activeAdjustment.counter_writer_compensation_amount) }}</dd>
            </div>
          </dl>

          <p v-if="hasBlockingAdjustment" class="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
            Resolve this request before creating another scope change for the same order.
          </p>

          <button
            v-if="canEscalateAdjustment"
            class="focus-ring mt-3 inline-flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-ink"
            type="button"
            @click="showEscalation = !showEscalation"
          >
            <ShieldAlert class="h-3.5 w-3.5" />
            Escalate to staff
          </button>

          <form v-if="showEscalation" class="mt-3 space-y-2" @submit.prevent="submitEscalation">
            <textarea
              v-model.trim="escalationReason"
              rows="3"
              class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
              placeholder="Explain why staff should review this scope decision."
            />
            <p v-if="escalationError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">{{ escalationError }}</p>
            <p v-if="escalationNotice" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">{{ escalationNotice }}</p>
            <button
              class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
              type="submit"
              :disabled="escalationBusy || escalationReason.length < 8"
            >
              <Loader2 v-if="escalationBusy" class="h-3.5 w-3.5 animate-spin" />
              <Send v-else class="h-3.5 w-3.5" />
              Send escalation
            </button>
          </form>
        </div>

        <button
          class="focus-ring mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white"
          type="button"
          :disabled="hasBlockingAdjustment"
          @click="showRequest = !showRequest"
        >
          <Plus class="h-4 w-4" />
          {{ hasBlockingAdjustment ? "Scope request pending" : showRequest ? "Close request" : "Request scope change" }}
        </button>

        <form v-if="showRequest && !hasBlockingAdjustment" class="mt-4 space-y-3" @submit.prevent="submitRequest">
          <label class="block">
            <span class="text-xs font-semibold text-graphite">Change type</span>
            <select v-model="requestForm.adjustment_type" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm">
              <option v-for="option in requestOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </label>

          <label class="block">
            <span class="text-xs font-semibold text-graphite">Quantity needed</span>
            <input v-model.number="requestForm.requested_quantity" min="1" type="number" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm" />
          </label>

          <label class="block">
            <span class="text-xs font-semibold text-graphite">Short title</span>
            <input v-model.trim="requestForm.title" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm" placeholder="Additional pages required" />
          </label>

          <label class="block">
            <span class="text-xs font-semibold text-graphite">Reason</span>
            <textarea v-model.trim="requestForm.writer_justification" rows="3" class="focus-ring mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Explain what changed and why it affects scope." />
          </label>

          <p v-if="requestError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">{{ requestError }}</p>
          <p v-if="requestNotice" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">{{ requestNotice }}</p>

          <button
            class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-md bg-signal px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="submit"
            :disabled="requestBusy || hasBlockingAdjustment || !requestForm.title || !requestForm.requested_quantity"
          >
            <Loader2 v-if="requestBusy" class="h-4 w-4 animate-spin" />
            <Send v-else class="h-4 w-4" />
            Submit request
          </button>
        </form>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, reactive, ref, watch } from "vue";
import { AlertTriangle, BookMarked, BookOpen, Download, ExternalLink, FileText, ListChecks, Loader2, Plus, Send, ShieldAlert } from "@lucide/vue";
import { adjustmentsApi } from "@/api/adjustments";
import type { FileAttachment } from "@/api/files";
import { useFilesStore } from "@/stores/files";
import type { AdjustmentRequest, AdjustmentStatus, AdjustmentType, ScopeUnitType } from "@/types/adjustments";
import type { OrderLifecycle, OrderSummary } from "@/types/orders";
import { dateLabel } from "./types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  lifecycle: OrderLifecycle | null;
}>();

const emit = defineEmits<{
  refresh: [];
}>();

const BriefMetric = defineComponent({
  props: {
    label: { type: String, required: true },
    value: { type: String, required: true },
  },
  template: `
    <div class="rounded-lg border border-slate-100 bg-slate-50 p-3">
      <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">{{ label }}</dt>
      <dd class="mt-1 truncate text-sm font-semibold text-ink" :title="value">{{ value }}</dd>
    </div>
  `,
});

const requestOptions: { value: AdjustmentType; label: string; unit: ScopeUnitType }[] = [
  { value: "page_increase", label: "Page increment", unit: "page" },
  { value: "slide_increase", label: "Slide increment", unit: "slide" },
  { value: "diagram_increase", label: "Diagram increment", unit: "diagram" },
  { value: "design_concept_increase", label: "Design increment", unit: "design_concept" },
  { value: "scope_expansion", label: "General scope expansion", unit: "other" },
];

const showRequest = ref(false);
const requestBusy = ref(false);
const requestError = ref("");
const requestNotice = ref("");
const activeAdjustment = ref<AdjustmentRequest | null>(null);
const adjustmentLoading = ref(false);
const showEscalation = ref(false);
const escalationReason = ref("");
const escalationBusy = ref(false);
const escalationError = ref("");
const escalationNotice = ref("");
const requestForm = reactive({
  adjustment_type: "page_increase" as AdjustmentType,
  requested_quantity: 1,
  title: "",
  writer_justification: "",
});
const files = useFilesStore();

const displayReference = computed(() =>
  props.order.reference || props.order.public_order_number || String(props.order.id),
);

const serviceLabel = computed(() => {
  const family = props.order.service_family || "order";
  const code = props.order.service_code ? ` · ${String(props.order.service_code).replace(/_/g, " ")}` : "";
  return `${String(family).replace(/_/g, " ")}${code}`;
});

const fullInstructions = computed(() =>
  (props.order.order_instructions || props.order.instructions || "").trim(),
);

function numeric(value: unknown): number {
  const n = Number(value ?? 0);
  return Number.isFinite(n) ? n : 0;
}

const pages = computed(() => numeric(props.order.number_of_pages ?? props.order.base_quantity));
const slides = computed(() => numeric(props.order.number_of_slides));
const designs = computed(() => numeric(props.order.number_of_designs));
const diagrams = computed(() => numeric(props.order.number_of_diagrams));
const writerTotal = computed(() => numeric(props.order.writer_pay_breakdown?.total ?? props.order.writer_compensation));
const designCount = computed(() => designs.value || (props.order.service_code?.includes("design") ? numeric(props.order.base_quantity ?? 1) || 1 : 0));
const diagramCount = computed(() => diagrams.value || (props.order.service_code?.includes("diagram") ? numeric(props.order.base_quantity ?? 1) || 1 : 0));

const ratePerPage = computed(() => numeric(props.order.writer_pay_breakdown?.rates?.page) || (pages.value > 0 ? writerTotal.value / pages.value : 0));
const ratePerSlide = computed(() => numeric(props.order.writer_pay_breakdown?.rates?.slide) || (slides.value > 0 ? writerTotal.value / slides.value : 0));
const ratePerDesign = computed(() => numeric(props.order.writer_pay_breakdown?.rates?.design) || (designCount.value > 0 ? writerTotal.value / designCount.value : 0));
const ratePerDiagram = computed(() => numeric(props.order.writer_pay_breakdown?.rates?.diagram) || (diagramCount.value > 0 ? writerTotal.value / diagramCount.value : 0));

const pagesLabel = computed(() => pages.value > 0 ? `${pages.value}${props.order.spacing ? ` · ${props.order.spacing}` : ""}` : "Not set");
const slidesLabel = computed(() => slides.value > 0 ? String(slides.value) : "None");
const designsLabel = computed(() => designs.value > 0 ? String(designs.value) : "None");
const diagramsLabel = computed(() => diagrams.value > 0 ? String(diagrams.value) : "None");
const citationLabel = computed(() => props.order.formatting_style_name || String(props.order.formatting_style || "Not set"));
const subjectLabel = computed(() => props.order.subject_name || String(props.order.subject || "Not set"));
const paperTypeLabel = computed(() => props.order.paper_type_name || String(props.order.paper_type || "Not set"));
const academicLevelLabel = computed(() => props.order.academic_level_name || String(props.order.academic_level || "Not set"));
const sourcesLabel = computed(() => {
  const sources = numeric(props.order.number_of_refereces);
  return sources > 0 ? `${sources} source${sources === 1 ? "" : "s"}` : "Check brief";
});
const writerDeadlineLabel = computed(() => props.order.writer_deadline ? dateLabel(props.order.writer_deadline) : "Not set");

const addonLabels = computed(() => {
  const raw = [
    ...(props.order.addon_names ?? []),
    ...(props.order.selected_addon_codes ?? []),
  ];
  if (Array.isArray(props.order.additional_services)) raw.push(...props.order.additional_services.map(String));
  return Array.from(new Set(raw.map((item) => item.replace(/_/g, " ")).filter(Boolean)));
});

const writerGuides = computed(() =>
  files.attachments.filter((attachment) =>
    attachment.is_active !== false && ["writer_guide", "style_reference"].includes(String(attachment.purpose)),
  ),
);

const expectationChips = computed(() => {
  const chips = [
    props.order.requires_editing ? "Editor review expected" : "Writer-ready draft",
    props.order.is_urgent ? "Urgent handling" : "Standard handling",
    props.order.subject_is_technical ? "Technical subject" : "",
    numeric(props.order.number_of_refereces) > 0 ? "References required" : "Confirm sources in brief",
    sourceCopiesRequired.value ? "Copies of sources required" : "Source copies not flagged",
  ];
  return chips.filter(Boolean);
});

const sourceCopiesRequired = computed(() => {
  if (props.order.copies_of_sources_required === true) return true;
  const flags = (props.order.flags ?? []).map((flag) => String(flag).toLowerCase());
  const addons = addonLabels.value.map((addon) => addon.toLowerCase());
  return [...flags, ...addons].some((item) =>
    item.includes("copy") || item.includes("source") || item.includes("bibliography"),
  );
});

const deadlineProgress = computed(() => {
  if (!props.order.created_at || !props.order.writer_deadline) return 0;
  const start = new Date(props.order.created_at).getTime();
  const end = new Date(props.order.writer_deadline).getTime();
  const now = Date.now();
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return 0;
  return Math.min(100, Math.max(0, Math.round(((now - start) / (end - start)) * 100)));
});

const deadlineProgressLabel = computed(() => {
  if (!props.order.writer_deadline) return "No writer deadline";
  const end = new Date(props.order.writer_deadline).getTime();
  const hours = Math.ceil((end - Date.now()) / 36e5);
  if (hours < 0) return "Past writer deadline";
  if (hours === 0) return "Due within the hour";
  return `${hours}h remaining`;
});

const deadlineTone = computed(() => {
  if (deadlineProgress.value >= 90) return { label: "Critical", badge: "bg-rose-100 text-rose-700", bar: "bg-rose-500" };
  if (deadlineProgress.value >= 70) return { label: "Tight", badge: "bg-amber-100 text-amber-700", bar: "bg-amber-500" };
  return { label: "On track", badge: "bg-emerald-100 text-emerald-700", bar: "bg-emerald-500" };
});

function money(value: number): string {
  return moneyValue(value);
}

function moneyValue(value: number | string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: props.order.writer_pay_breakdown?.currency || props.order.currency || "USD",
  }).format(numeric(value));
}

function adjustmentMoney(value: string | number | null): string {
  if (value === null || value === undefined || value === "") return "Pending quote";
  return moneyValue(value);
}

function selectedUnit(): ScopeUnitType {
  return requestOptions.find((option) => option.value === requestForm.adjustment_type)?.unit ?? "other";
}

function defaultQuantityFor(type: AdjustmentType): number {
  if (type === "page_increase") return Math.max(1, pages.value + 1);
  if (type === "slide_increase") return Math.max(1, slides.value + 1);
  if (type === "diagram_increase") return Math.max(1, diagramCount.value + 1);
  if (type === "design_concept_increase") return Math.max(1, designCount.value + 1);
  return 1;
}

function adjustmentTypeLabel(type: AdjustmentType | null): string {
  return requestOptions.find((option) => option.value === type)?.label ?? "Scope expansion";
}

function applyRequestDefaults(type: AdjustmentType) {
  const label = adjustmentTypeLabel(type);
  requestForm.requested_quantity = defaultQuantityFor(type);
  if (!requestForm.title || requestOptions.some((option) => requestForm.title === option.label)) {
    requestForm.title = label;
  }
}

const terminalAdjustmentStatuses = new Set<AdjustmentStatus>([
  "declined",
  "funded",
  "counter_funded_final",
  "approved_by_staff",
  "rejected_by_client",
  "rejected_by_staff",
  "cancelled",
  "expired",
  "reversed",
]);

const hasBlockingAdjustment = computed(() =>
  Boolean(activeAdjustment.value && !terminalAdjustmentStatuses.has(activeAdjustment.value.status)),
);

const canEscalateAdjustment = computed(() =>
  Boolean(activeAdjustment.value && ["client_countered", "declined", "rejected_by_client"].includes(activeAdjustment.value.status)),
);

async function loadActiveAdjustment() {
  adjustmentLoading.value = true;
  try {
    const id = props.lifecycle?.latest_adjustment_request_id;
    if (id) {
      const { data } = await adjustmentsApi.getDetail(id);
      activeAdjustment.value = data;
      return;
    }
    const { data } = await adjustmentsApi.getLatest(props.orderId).catch(() => ({ data: null as AdjustmentRequest | null }));
    activeAdjustment.value = data;
  } finally {
    adjustmentLoading.value = false;
  }
}

function adjustmentStatusTone(status: AdjustmentStatus): string {
  if (["funded", "approved_by_staff", "counter_funded_final"].includes(status)) return "bg-emerald-100 text-emerald-700";
  if (["declined", "rejected_by_client", "rejected_by_staff", "cancelled", "expired", "reversed"].includes(status)) return "bg-rose-100 text-rose-700";
  if (["client_countered", "funding_pending"].includes(status)) return "bg-amber-100 text-amber-700";
  return "bg-signal/10 text-signal";
}

function guideTitle(guide: FileAttachment): string {
  return guide.display_name || guide.external_link?.title || guide.managed_file?.original_filename || `Resource ${guide.id}`;
}

function guideKind(guide: FileAttachment): string {
  if (guide.external_link?.url) return "external link";
  return guide.managed_file?.file_extension || guide.managed_file?.mime_type || "file";
}

async function openGuide(guide: FileAttachment) {
  const url = guide.external_link?.url;
  if (url) {
    window.open(url, "_blank", "noopener,noreferrer");
    return;
  }
  await files.downloadFile(props.orderId, guide.id);
}

watch(
  () => props.lifecycle?.latest_adjustment_request_id,
  () => {
    void loadActiveAdjustment();
  },
  { immediate: true },
);

watch(
  () => requestForm.adjustment_type,
  (type) => applyRequestDefaults(type),
  { immediate: true },
);

async function submitRequest() {
  if (hasBlockingAdjustment.value) {
    requestError.value = "Resolve the existing scope request before creating another.";
    return;
  }
  requestBusy.value = true;
  requestError.value = "";
  requestNotice.value = "";
  try {
    await adjustmentsApi.createScopeIncrement(props.orderId, {
      adjustment_type: requestForm.adjustment_type,
      unit_type: selectedUnit(),
      requested_quantity: Number(requestForm.requested_quantity || 1),
      title: requestForm.title,
      writer_justification: requestForm.writer_justification,
      description: requestForm.writer_justification,
    });
    requestNotice.value = "Scope request submitted for review.";
    requestForm.title = "";
    requestForm.writer_justification = "";
    applyRequestDefaults(requestForm.adjustment_type);
    await loadActiveAdjustment();
    emit("refresh");
  } catch {
    requestError.value = "Unable to submit the scope request.";
  } finally {
    requestBusy.value = false;
  }
}

async function submitEscalation() {
  if (!activeAdjustment.value) return;
  escalationBusy.value = true;
  escalationError.value = "";
  escalationNotice.value = "";
  try {
    await adjustmentsApi.escalate(activeAdjustment.value.id, escalationReason.value);
    escalationNotice.value = "Escalation sent to staff.";
    escalationReason.value = "";
    await loadActiveAdjustment();
    emit("refresh");
  } catch {
    escalationError.value = "Unable to escalate this request.";
  } finally {
    escalationBusy.value = false;
  }
}
</script>
