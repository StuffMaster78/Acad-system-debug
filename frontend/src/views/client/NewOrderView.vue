<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Calculator, CheckCircle2, Clock, FileText, Loader2, Paperclip, RefreshCw, Send, X } from "@lucide/vue";
import ConfigSelect from "@/components/forms/ConfigSelect.vue";
import PaymentMethodSelector from "@/components/payment/PaymentMethodSelector.vue";
import PaymentDisclosureBanner from "@/components/payment/PaymentDisclosureBanner.vue";
import type { PaymentMethod } from "@/components/payment/PaymentMethodSelector.vue";
import { useFilesStore } from "@/stores/files";
import { useOrderConfigStore } from "@/stores/orderConfig";
import { useOrderStore } from "@/stores/orders";
import { useWalletStore } from "@/stores/wallets";
import type { DesignQuotePayload, DiagramQuotePayload, PaperQuotePayload } from "@/types/orders";
import { useAnalytics } from "@/composables/useAnalytics";

const { purchase, beginCheckout } = useAnalytics();

const route  = useRoute();
const router = useRouter();
const orders = useOrderStore();
const config = useOrderConfigStore();
const wallets = useWalletStore();
const files = useFilesStore();

const error = ref("");
const success = ref("");
const paymentMethod = ref<PaymentMethod>("wallet");
const paymentDisclosureAccepted = ref(false);
const couponCode = ref("");

// ── Add-ons ───────────────────────────────────────────────────────────────────
interface AddonOption { id: number; addon_code: string; name: string; description: string; flat_amount: string }
const availableAddons   = ref<AddonOption[]>([]);
const selectedAddonCodes = ref<string[]>([]);

async function loadAddons() {
  try {
    const { data } = await import("@/api/client").then(({ api, apiPath }) =>
      api.get<AddonOption[]>(apiPath(`/pricing/public/addons/?service_code=${form.service_code}`))
    );
    availableAddons.value = Array.isArray(data) ? data : [];
  } catch { availableAddons.value = []; }
}

function toggleAddon(code: string) {
  const idx = selectedAddonCodes.value.indexOf(code);
  if (idx === -1) selectedAddonCodes.value = [...selectedAddonCodes.value, code];
  else selectedAddonCodes.value = selectedAddonCodes.value.filter(c => c !== code);
}

const addonTotal = computed(() =>
  availableAddons.value
    .filter(a => selectedAddonCodes.value.includes(a.addon_code))
    .reduce((s, a) => s + Number(a.flat_amount), 0),
);
const couponApplied = ref(false);
const couponError = ref("");
const applyingCoupon = ref(false);
interface DiscountPreview { code: string; amount: number; final: number }
const discountPreview = ref<DiscountPreview | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const styleFileInputRef = ref<HTMLInputElement | null>(null);
const attempted = ref(false);
const touched = reactive(new Set<string>());

const topicError = computed(() => {
  const v = form.topic.trim();
  if (!v) return "Topic is required.";
  if (v.length < 3) return "Topic is too short — at least 3 characters.";
  return "";
});
const instructionsError = computed(() => {
  const v = form.order_instructions.trim();
  if (!v) return "Instructions are required.";
  if (v.length < 10) return "Please add more detail — at least 10 characters.";
  return "";
});
function fieldErr(name: string, err: string) {
  return err && (attempted.value || touched.has(name)) ? err : "";
}

const providerFor: Record<PaymentMethod, { payment_provider?: string; payment_method_code?: string }> = {
  wallet: {},
  stripe: { payment_provider: "stripe", payment_method_code: "card" },
  mock: { payment_provider: "mock", payment_method_code: "mock_card" },
};

function defaultDeadline() {
  return new Date(Date.now() + 72 * 3600 * 1000).toISOString().slice(0, 16);
}

// ── Service mode ─────────────────────────────────────────────────────────────
type ServiceMode = "paper" | "design" | "diagram" | "combo_paper_design" | "combo_paper_diagram";

const SERVICE_MODES: { key: ServiceMode; label: string; description: string }[] = [
  { key: "paper",              label: "Writing",               description: "Essay, report, research paper, coursework" },
  { key: "design",             label: "Presentation / Design", description: "PowerPoint slides, infographic, poster" },
  { key: "diagram",            label: "Diagram",               description: "Flowchart, ERD, UML, system architecture" },
  { key: "combo_paper_design", label: "Writing + Design",      description: "Written paper with a presentation" },
  { key: "combo_paper_diagram", label: "Writing + Diagrams",   description: "Written paper with supporting diagrams" },
];

const DESIGN_SERVICES = [
  { code: "presentation_design", label: "Presentation (PPT/Slides)" },
  { code: "infographic_design",  label: "Infographic" },
  { code: "poster_flyer_design", label: "Poster / Flyer" },
];

const DIAGRAM_SERVICES = [
  { code: "flowchart_diagram", label: "Flowchart",                         diagramType: "flowchart"      },
  { code: "erd_diagram",       label: "Entity Relationship Diagram (ERD)", diagramType: "erd"            },
  { code: "uml_diagram",       label: "UML Diagram",                       diagramType: "uml"            },
  { code: "system_diagram",    label: "System Architecture Diagram",       diagramType: "system_diagram" },
];

const DIAGRAM_COMPLEXITIES = [
  { code: "simple",   label: "Simple" },
  { code: "moderate", label: "Moderate" },
  { code: "complex",  label: "Complex" },
];

const serviceMode = ref<ServiceMode>("paper");

const designForm = reactive({
  service_code: "presentation_design",
  slides: 10,
  quantity: 1,
});

const diagramForm = reactive({
  service_code: "flowchart_diagram",
  quantity: 1,
  complexity: "moderate",
});

const isDesignMode   = computed(() => serviceMode.value === "design" || serviceMode.value === "combo_paper_design");
const isDiagramMode  = computed(() => serviceMode.value === "diagram" || serviceMode.value === "combo_paper_diagram");
const isPaperMode    = computed(() => serviceMode.value === "paper" || serviceMode.value === "combo_paper_design" || serviceMode.value === "combo_paper_diagram");
const isComboMode    = computed(() => serviceMode.value === "combo_paper_design" || serviceMode.value === "combo_paper_diagram");
const isStandaloneDesign  = computed(() => serviceMode.value === "design");
const isStandaloneDiagram = computed(() => serviceMode.value === "diagram");

const form = reactive({
  topic: "",
  order_instructions: "",
  client_deadline: defaultDeadline(),
  pages: 1,
  spacing: "double" as "single" | "double",
  service_code: "academic_writing",
  paper_type_code: "essay",
  work_type_code: "writing",
  subject_code: "general",
  academic_level_code: "undergraduate",
  paper_type_id: null as number | null,
  type_of_work_id: null as number | null,
  subject_id: null as number | null,
  academic_level_id: null as number | null,
  formatting_style_id: null as number | null,
  english_type_id: null as number | null,
  writer_level_id: null as number | null,
});

const deadlineHours = computed(() => {
  const diff = new Date(form.client_deadline).getTime() - Date.now();
  return Math.max(1, Math.ceil(diff / (1000 * 60 * 60)));
});

const deadlineLabel = computed(() => {
  const h = deadlineHours.value;
  if (h < 24) return `${h}h`;
  const d = Math.floor(h / 24);
  const rem = h % 24;
  return rem ? `${d}d ${rem}h` : `${d} days`;
});

const quotedPrice = computed(() => {
  const raw = orders.latestQuote?.calculated_price;
  return raw == null ? null : Number(raw);
});

const wordRange = computed(() => {
  if (form.spacing === "single") {
    return { min: form.pages * 550, max: form.pages * 600 };
  }
  return { min: form.pages * 275, max: form.pages * 300 };
});

const canQuote = computed(
  () =>
    form.topic.trim().length > 2 &&
    form.order_instructions.trim().length > 10 &&
    Boolean(form.paper_type_id && form.type_of_work_id && form.academic_level_id),
);

const configSelectionError = computed(() => {
  // Non-paper modes don't require paper config fields
  if (!isPaperMode.value) return "";
  if (form.paper_type_id && form.type_of_work_id && form.academic_level_id) return "";
  return "Choose paper type, type of work, and academic level.";
});

function optionCode(collection: keyof typeof config.collections, id: number | null) {
  const option = config.collections[collection].find((item) => item.id === id);
  return String(option?.code || (option as { slug?: string })?.slug || option?.name || "").trim();
}

function selectedOption(collection: keyof typeof config.collections, id: number | null) {
  return config.collections[collection].find((item) => item.id === id) ?? null;
}

function optionDescription(collection: keyof typeof config.collections, id: number | null) {
  const option = selectedOption(collection, id);
  return String(option?.description || option?.help_text || option?.short_description || "");
}

function applyConfigDefaults() {
  form.paper_type_id ??= config.collections.paperTypes[0]?.id ?? null;
  form.type_of_work_id ??= config.collections.typesOfWork[0]?.id ?? null;
  form.subject_id ??= config.collections.subjects[0]?.id ?? null;
  form.academic_level_id ??= config.collections.academicLevels[0]?.id ?? null;
  form.formatting_style_id ??= config.collections.formattingStyles[0]?.id ?? null;
  form.english_type_id ??= config.collections.englishTypes[0]?.id ?? null;
  form.writer_level_id ??= config.collections.writerLevels[0]?.id ?? null;
}

// Shorthand keys kept for backwards-compat with old marketing links.
// New calculator passes max_hours directly as a numeric string.
const DEADLINE_HOURS: Record<string, number> = {
  '14d': 336, '7d': 168, '5d': 120, '3d': 72, '24h': 24, '12h': 12, '6h': 6,
};

// Marketing-site keys → ordered candidate names in the portal's config.
// Exact match wins; falls back to starts-with so "Bachelor's" matches "Bachelor".
const LEVEL_NAMES: Record<string, string[]> = {
  // Backend AcademicLevelRate codes (from seed_pricing_defaults)
  high_school:   ['High School'],
  undergrad:     ['Undergraduate', "Bachelor's", 'College'],
  masters:       ["Master's"],
  phd:           ['PhD', 'Doctorate'],
  // Legacy keys from old static usePricing.ts constants
  undergrad_1_2: ['College'],
  undergrad_3_4: ["Bachelor's", 'Undergraduate'],
};
const TYPE_NAMES: Record<string, string[]> = {
  // Keys from the marketing calculator (usePricing.ts PAPER_TYPES)
  essay:        ['Essay'],
  research:     ['Research Paper'],
  dissertation: ['Dissertation', 'Thesis'],
  coursework:   ['Coursework'],
  case_study:   ['Case Study'],
  term_paper:   ['Term Paper'],
  admission:    ['Admission Essay'],
  editing:      ['Editing'],
  // Service page slugs passed via ?type=<slug>
  'essay-writing':        ['Essay'],
  'research-papers':      ['Research Paper'],
  'dissertations':        ['Dissertation', 'Thesis'],
  'thesis-writing':       ['Thesis', 'Dissertation'],
  'term-papers':          ['Term Paper'],
  'case-studies':         ['Case Study'],
  'literature-review':    ['Research Paper'],
  'data-analysis':        ['Research Paper'],
  'editing-proofreading': ['Editing'],
  'homework-help':        ['Coursework'],
  'online-class-help':    ['Coursework'],
  'capstone-projects':    ['Capstone Project', 'Research Paper'],
};

function matchOption(items: typeof config.collections.academicLevels, candidates: string[]): number | null {
  for (const name of candidates) {
    const q = name.toLowerCase();
    const item = items.find(i => i.name.toLowerCase() === q)
               ?? items.find(i => i.name.toLowerCase().startsWith(q));
    if (item) return item.id;
  }
  return null;
}

function applyUrlParams() {
  const q = route.query;

  const pages = parseInt(String(q.pages ?? ''), 10);
  if (!isNaN(pages) && pages >= 1 && pages <= 100) form.pages = pages;

  const levelKey = String(q.level ?? '');
  if (levelKey && LEVEL_NAMES[levelKey]) {
    const id = matchOption(config.collections.academicLevels, LEVEL_NAMES[levelKey]);
    if (id !== null) form.academic_level_id = id;
  }

  const typeKey = String(q.type ?? '');
  if (typeKey && TYPE_NAMES[typeKey]) {
    const id = matchOption(config.collections.paperTypes, TYPE_NAMES[typeKey]);
    if (id !== null) form.paper_type_id = id;
  }

  const deadlineRaw = String(q.deadline ?? '');
  // Accept either a shorthand key ('14d', '24h') or numeric hours ('336', '24').
  const hours = DEADLINE_HOURS[deadlineRaw] ?? (parseInt(deadlineRaw, 10) || 0);
  if (hours > 0) {
    form.client_deadline = new Date(Date.now() + hours * 3600 * 1000).toISOString().slice(0, 16);
  }
}

const selectedBrief = computed(() => [
  {
    label: "Paper type",
    value: selectedOption("paperTypes", form.paper_type_id)?.name || "Not selected",
    detail: optionDescription("paperTypes", form.paper_type_id),
  },
  {
    label: "Work type",
    value: selectedOption("typesOfWork", form.type_of_work_id)?.name || "Not selected",
    detail: optionDescription("typesOfWork", form.type_of_work_id),
  },
  {
    label: "Subject",
    value: selectedOption("subjects", form.subject_id)?.name || "General",
    detail: optionDescription("subjects", form.subject_id),
  },
  {
    label: "Academic level",
    value: selectedOption("academicLevels", form.academic_level_id)?.name || "Not selected",
    detail: optionDescription("academicLevels", form.academic_level_id),
  },
]);

const readinessItems = computed(() => [
  { label: "Topic added", done: !topicError.value },
  { label: "Instructions are clear", done: !instructionsError.value },
  { label: "Order category selected", done: !configSelectionError.value },
  { label: "Deadline set", done: Boolean(form.client_deadline) },
]);

function quotePayload(): PaperQuotePayload {
  return {
    service_code: form.service_code,
    pages: form.pages,
    deadline_hours: deadlineHours.value,
    spacing: form.spacing,
    paper_type_code: optionCode("paperTypes", form.paper_type_id) || form.paper_type_code,
    work_type_code: optionCode("typesOfWork", form.type_of_work_id) || form.work_type_code,
    subject_code: optionCode("subjects", form.subject_id) || form.subject_code,
    academic_level_code: optionCode("academicLevels", form.academic_level_id) || form.academic_level_code,
    topic: form.topic,
    instructions: form.order_instructions,
    selected_addon_codes: selectedAddonCodes.value.length ? selectedAddonCodes.value : undefined,
  };
}

async function loadConfig() {
  error.value = "";
  try {
    await config.fetchAll();
    applyConfigDefaults();
    applyUrlParams();
  } catch {
    // error surfaced via config.error
  }
  wallets.fetchWallet().catch(() => undefined);
}

function designPayload(): DesignQuotePayload {
  return {
    service_code: designForm.service_code,
    ...(designForm.service_code === "presentation_design" ? { slides: designForm.slides } : { quantity: designForm.quantity }),
    deadline_hours: deadlineHours.value,
    topic: form.topic,
    instructions: form.order_instructions,
  };
}

function diagramPayload(): DiagramQuotePayload {
  const svc = DIAGRAM_SERVICES.find(s => s.code === diagramForm.service_code);
  return {
    service_code: diagramForm.service_code,
    quantity: diagramForm.quantity,
    deadline_hours: deadlineHours.value,
    diagram_type: svc?.diagramType ?? diagramForm.service_code,
    diagram_complexity: diagramForm.complexity,
  };
}

async function calculate() {
  error.value = "";
  success.value = "";
  discountPreview.value = null;
  couponApplied.value = false;
  try {
    if (serviceMode.value === "paper") {
      await orders.pricePaperOrder(quotePayload());
    } else if (serviceMode.value === "design") {
      await orders.priceDesignOrder(designPayload());
    } else if (serviceMode.value === "diagram") {
      await orders.priceDiagramOrder(diagramPayload());
    } else if (serviceMode.value === "combo_paper_design") {
      await orders.priceComboOrder(quotePayload(), designPayload(), "design");
    } else {
      await orders.priceComboOrder(quotePayload(), diagramPayload(), "diagram");
    }
    if (quotedPrice.value != null) beginCheckout(quotedPrice.value);
  } catch {
    error.value = "Pricing failed. Check your order details and try again.";
  }
}

async function applyDiscount() {
  if (!couponCode.value.trim() || quotedPrice.value == null) return;
  applyingCoupon.value = true;
  couponError.value = "";
  discountPreview.value = null;
  try {
    const { api, apiPath } = await import("@/api/client");
    const { data } = await api.post<{ discount: { discount_code: string; discount_amount: string; final_amount: string } | null }>(
      apiPath("/discounts/client/preview/"),
      {
        subtotal: quotedPrice.value.toFixed(2),
        payable_type: "order",
        entered_code: couponCode.value.trim().toUpperCase(),
        has_prior_paid_purchase: false,
      },
    );
    if (data.discount) {
      discountPreview.value = {
        code: data.discount.discount_code,
        amount: Number(data.discount.discount_amount),
        final: Number(data.discount.final_amount),
      };
      couponApplied.value = true;
    } else {
      couponError.value = "Code not valid for this order.";
    }
  } catch {
    couponError.value = "Could not validate code. Please try again.";
  } finally {
    applyingCoupon.value = false;
  }
}

async function submit() {
  attempted.value = true;
  if (topicError.value || instructionsError.value) return;
  // Paper fields only required for paper-based modes
  if (isPaperMode.value && (!form.paper_type_id || !form.academic_level_id || !form.type_of_work_id)) return;
  if (!paymentDisclosureAccepted.value) {
    error.value = "Please acknowledge the billing statement notice before placing your order.";
    return;
  }
  error.value = "";
  success.value = "";
  try {
    const provider = providerFor[paymentMethod.value];
    const baseOrder = {
      topic: form.topic,
      order_instructions: form.order_instructions,
      client_deadline: new Date(form.client_deadline).toISOString(),
      is_urgent: deadlineHours.value <= 24,
      ...provider,
      ...(couponCode.value.trim() ? { entered_code: couponCode.value.trim() } : {}),
    };

    let created;
    if (serviceMode.value === "paper") {
      created = await orders.createPaperOrder(quotePayload(), {
        ...baseOrder,
        service_family: "paper_order",
        service_code: form.service_code,
        number_of_pages: form.pages,
        paper_type_id: form.paper_type_id,
        academic_level_id: form.academic_level_id,
        formatting_style_id: form.formatting_style_id,
        subject_id: form.subject_id,
        type_of_work_id: form.type_of_work_id,
        english_type_id: form.english_type_id,
        writer_level_id: form.writer_level_id,
      });
    } else if (serviceMode.value === "design") {
      created = await orders.createDesignOrder(designPayload(), {
        ...baseOrder,
        service_family: "design_order",
        service_code: designForm.service_code,
        ...(designForm.service_code === "presentation_design" ? { slides: designForm.slides } : { quantity: designForm.quantity }),
      } as Parameters<typeof orders.createDesignOrder>[1]);
    } else if (serviceMode.value === "diagram") {
      created = await orders.createDiagramOrder(diagramPayload(), {
        ...baseOrder,
        service_family: "diagram_order",
        service_code: diagramForm.service_code,
        quantity: diagramForm.quantity,
      } as Parameters<typeof orders.createDiagramOrder>[1]);
    } else {
      // Combo
      const secondType = serviceMode.value === "combo_paper_design" ? "design" : "diagram";
      const secondPayload = secondType === "design" ? designPayload() : diagramPayload();
      created = await orders.createComboOrder(
        quotePayload(),
        secondPayload,
        secondType,
        {
          ...baseOrder,
          service_family: "combo_order",
          service_code: form.service_code,
          number_of_pages: form.pages,
          paper_type_id: form.paper_type_id,
          academic_level_id: form.academic_level_id,
          formatting_style_id: form.formatting_style_id,
          subject_id: form.subject_id,
          type_of_work_id: form.type_of_work_id,
          english_type_id: form.english_type_id,
          writer_level_id: form.writer_level_id,
        } as Parameters<typeof orders.createComboOrder>[3],
        quotedPrice.value ?? 0,
      );
    }

    if (files.uploadQueue.length) {
      await files.uploadFiles(created.order.id);
    }

    if (created.checkout_started) {
      const checkoutUrl = (created.payment_intent as Record<string, unknown> | null)?.checkout_url;
      if (typeof checkoutUrl === "string") {
        window.location.href = checkoutUrl;
        return;
      }
    }

    // GA4 purchase event
    purchase({
      transaction_id: String(created.order.id),
      value:          quotedPrice.value ?? 0,
      currency:       "USD",
      coupon:         couponCode.value.trim() || undefined,
    });

    await router.push(`/client/orders/${created.order.id}`);
  } catch {
    error.value = "Order creation failed. Complete all required fields and try again.";
  }
}

function pickFiles() {
  fileInputRef.value?.click();
}

function onFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;
  files.addToQueue(input.files, "order_reference");
  input.value = "";
}

function pickStyleFiles() {
  styleFileInputRef.value?.click();
}

function onStyleFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;
  files.addToQueue(input.files, "style_reference");
  input.value = "";
}

function fileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

watch(() => form.paper_type_id, (id) => {
  const code = optionCode("paperTypes", id);
  if (code) form.paper_type_code = code;
});
watch(() => form.type_of_work_id, (id) => {
  const code = optionCode("typesOfWork", id);
  if (code) form.work_type_code = code;
});
watch(() => form.subject_id, (id) => {
  const code = optionCode("subjects", id);
  if (code) form.subject_code = code;
});
watch(() => form.academic_level_id, (id) => {
  const code = optionCode("academicLevels", id);
  if (code) form.academic_level_code = code;
});

onMounted(() => { loadConfig(); loadAddons(); });
watch(() => form.service_code, loadAddons);
</script>

<template>
  <div class="mx-auto max-w-5xl space-y-4">
    <section>
      <p class="text-sm font-semibold uppercase text-signal">Client</p>
      <h1 class="mt-2 text-3xl font-semibold text-ink">New order</h1>
      <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
        Fill in your order details, attach any reference materials, then calculate a price and submit.
      </p>
    </section>

    <form class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]" @submit.prevent="submit" novalidate>
      <div class="space-y-4">

        <!-- Service type selector -->
        <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="text-base font-semibold text-ink">What do you need?</h2>
          <p class="mt-0.5 text-xs text-graphite">Select the type of work — you can mix writing with a presentation or diagrams.</p>
          <div class="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
            <button
              v-for="mode in SERVICE_MODES"
              :key="mode.key"
              type="button"
              class="rounded-lg border-2 px-3 py-3 text-left text-sm transition-colors"
              :class="serviceMode === mode.key
                ? 'border-signal bg-signal/5 text-signal'
                : 'border-slate-200 text-ink hover:border-slate-300'"
              @click="serviceMode = mode.key"
            >
              <p class="font-semibold">{{ mode.label }}</p>
              <p class="mt-0.5 text-xs text-graphite">{{ mode.description }}</p>
            </button>
          </div>
        </section>

        <!-- Order brief -->
        <section class="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Order brief</h2>

          <div>
            <label class="block text-sm font-medium text-ink" for="order-topic">
              Topic <span class="text-rose-500" aria-hidden="true">*</span>
            </label>
            <input
              id="order-topic"
              v-model="form.topic"
              required
              aria-required="true"
              :aria-invalid="fieldErr('topic', topicError) ? 'true' : undefined"
              aria-describedby="topic-error"
              class="focus-ring mt-1.5 h-11 w-full rounded-lg border px-3.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300"
              :class="fieldErr('topic', topicError) ? 'border-rose-300 bg-rose-50/40' : 'border-slate-200'"
              placeholder="e.g. Climate change and food security in Sub-Saharan Africa"
              type="text"
              @blur="touched.add('topic')"
            />
            <p v-if="fieldErr('topic', topicError)" id="topic-error" class="mt-1 text-xs text-berry" role="alert">
              {{ topicError }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-ink" for="order-instructions">
              Instructions <span class="text-rose-500" aria-hidden="true">*</span>
            </label>
            <textarea
              id="order-instructions"
              v-model="form.order_instructions"
              required
              aria-required="true"
              :aria-invalid="fieldErr('instructions', instructionsError) ? 'true' : undefined"
              aria-describedby="instructions-error"
              class="focus-ring mt-1.5 min-h-36 w-full rounded-lg border px-3.5 py-2.5 text-sm placeholder:text-slate-400 transition-colors hover:border-slate-300"
              :class="fieldErr('instructions', instructionsError) ? 'border-rose-300 bg-rose-50/40' : 'border-slate-200'"
              placeholder="Include your assignment prompt, citation style, sources required, and any specific requirements from your instructor…"
              @blur="touched.add('instructions')"
            />
            <p v-if="fieldErr('instructions', instructionsError)" id="instructions-error" class="mt-1 text-xs text-berry" role="alert">
              {{ instructionsError }}
            </p>
          </div>
        </section>

        <!-- Paper specifics — only shown for paper/combo modes -->
        <section v-if="isPaperMode" class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Paper specifics</h2>

          <!-- Loading skeleton -->
          <div v-if="config.isLoading" class="mt-4 grid gap-4 sm:grid-cols-2" aria-hidden="true">
            <div v-for="n in 6" :key="n" class="animate-pulse space-y-1.5">
              <div class="h-3.5 w-24 rounded bg-slate-200" />
              <div class="h-11 rounded-md border border-slate-200 bg-slate-100" />
            </div>
          </div>

          <div v-else-if="config.error && !config.hasLiveOptions" class="mt-4 flex flex-col items-center gap-3 rounded-md border border-dashed border-slate-200 py-8 text-center text-sm text-graphite">
            <p>Could not load paper options. Check your connection and try again.</p>
            <button
              class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-50"
              type="button"
              :disabled="config.isLoading"
              @click="loadConfig"
            >
              <RefreshCw class="h-3.5 w-3.5" :class="config.isLoading ? 'animate-spin' : ''" />
              Retry
            </button>
          </div>

          <div v-else class="mt-4 grid gap-4 sm:grid-cols-2">
            <!-- Core fields -->
            <ConfigSelect
              v-model="form.paper_type_id"
              label="Paper type"
              placeholder="Select paper type"
              :options="config.collections.paperTypes"
              help="Choose the format that best matches your assignment brief."
              required
            />
            <ConfigSelect
              v-model="form.type_of_work_id"
              label="Type of work"
              placeholder="Select type of work"
              :options="config.collections.typesOfWork"
              help="This helps us route the order to the right workflow."
              required
            />
            <ConfigSelect
              v-model="form.subject_id"
              label="Subject / discipline"
              placeholder="Select subject"
              :options="config.collections.subjects"
              help="Pick the closest subject area so the work can be matched properly."
            />
            <ConfigSelect
              v-model="form.academic_level_id"
              label="Academic level"
              placeholder="Select academic level"
              :options="config.collections.academicLevels"
              help="Select the level expected by your institution."
              required
            />
            <!-- Advanced fields -->
            <ConfigSelect
              v-model="form.formatting_style_id"
              label="Formatting / citation style"
              placeholder="None required"
              :options="config.collections.formattingStyles"
              help="Use the style required in your instructions or rubric."
            />
            <ConfigSelect
              v-model="form.english_type_id"
              label="English variant"
              placeholder="Any"
              :options="config.collections.englishTypes"
              help="Choose a language variant only if your assignment requires one."
            />
            <ConfigSelect
              v-if="config.collections.writerLevels.length"
              v-model="form.writer_level_id"
              label="Writer level"
              placeholder="Standard (any level)"
              :options="config.collections.writerLevels"
              help="Higher levels may affect availability and price."
            />
          </div>
          <p
            v-if="fieldErr('config', configSelectionError)"
            class="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700"
            role="alert"
          >
            {{ configSelectionError }}
          </p>
        </section>

        <!-- Design specifics -->
        <section v-if="isDesignMode" class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Design specifics</h2>
          <div class="mt-4 grid gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-sm font-medium text-ink mb-1">Design type</label>
              <select v-model="designForm.service_code" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal">
                <option v-for="s in DESIGN_SERVICES" :key="s.code" :value="s.code">{{ s.label }}</option>
              </select>
            </div>
            <div v-if="designForm.service_code === 'presentation_design'">
              <label class="block text-sm font-medium text-ink mb-1">Number of slides</label>
              <input v-model.number="designForm.slides" type="number" min="1" max="200"
                class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal" />
              <p class="mt-1 text-xs text-graphite">Total slides required including title and reference slides.</p>
            </div>
            <div v-else>
              <label class="block text-sm font-medium text-ink mb-1">Quantity</label>
              <input v-model.number="designForm.quantity" type="number" min="1" max="50"
                class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal" />
              <p class="mt-1 text-xs text-graphite">Number of designs required.</p>
            </div>
          </div>
        </section>

        <!-- Diagram specifics -->
        <section v-if="isDiagramMode" class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Diagram specifics</h2>
          <div class="mt-4 grid gap-4 sm:grid-cols-3">
            <div>
              <label class="block text-sm font-medium text-ink mb-1">Diagram type</label>
              <select v-model="diagramForm.service_code" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal">
                <option v-for="s in DIAGRAM_SERVICES" :key="s.code" :value="s.code">{{ s.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-ink mb-1">Number of diagrams</label>
              <input v-model.number="diagramForm.quantity" type="number" min="1" max="20"
                class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal" />
            </div>
            <div>
              <label class="block text-sm font-medium text-ink mb-1">Complexity</label>
              <select v-model="diagramForm.complexity" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal">
                <option v-for="c in DIAGRAM_COMPLEXITIES" :key="c.code" :value="c.code">{{ c.label }}</option>
              </select>
              <p class="mt-1 text-xs text-graphite">Affects pricing — complex diagrams take longer.</p>
            </div>
          </div>
        </section>

        <!-- Scope and deadline -->
        <section class="space-y-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Scope &amp; deadline</h2>

          <div class="grid gap-4 sm:grid-cols-3">
            <!-- Pages: only for paper-based modes -->
            <label v-if="isPaperMode" class="block">
              <span class="text-sm font-medium text-graphite">Pages</span>
              <input
                v-model.number="form.pages"
                class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
                min="1"
                max="500"
                type="number"
              />
              <span class="mt-1 block text-xs text-graphite">
                ~{{ wordRange.min }}–{{ wordRange.max }} words
              </span>
            </label>

            <!-- Spacing: only for paper-based modes -->
            <label v-if="isPaperMode" class="block">
              <span class="text-sm font-medium text-graphite">Spacing</span>
              <select v-model="form.spacing" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm">
                <option value="double">Double spacing</option>
                <option value="single">Single spacing</option>
              </select>
              <span class="mt-1 block text-xs text-graphite">
                {{ form.spacing === "single" ? "550–600" : "275–300" }} words / page
              </span>
            </label>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Deadline</span>
              <input
                v-model="form.client_deadline"
                class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="datetime-local"
              />
              <span class="mt-1 block text-xs" :class="deadlineHours <= 24 ? 'text-berry font-semibold' : 'text-graphite'">
                {{ deadlineLabel }} from now{{ deadlineHours <= 24 ? " — urgent" : "" }}
              </span>
            </label>
          </div>
        </section>

        <!-- Reference files -->
        <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-base font-semibold text-ink">Reference materials</h2>
              <p class="mt-0.5 text-xs text-graphite">Attach your assignment brief, rubric, examples, or any files the writer needs.</p>
            </div>
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-ink"
              type="button"
              @click="pickFiles"
            >
              <Paperclip class="h-4 w-4" />
              Add files
            </button>
          </div>

          <input
            ref="fileInputRef"
            class="sr-only"
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.txt,.rtf,.png,.jpg,.jpeg,.zip"
            @change="onFilesSelected"
          />

          <div v-if="files.uploadQueue.length" class="mt-4 space-y-2">
            <div
              v-for="item in files.uploadQueue"
              :key="item.id"
              class="flex items-center gap-3 rounded-md border border-slate-100 bg-slate-50 px-3 py-2 text-sm"
            >
              <Paperclip class="h-4 w-4 shrink-0 text-graphite" />
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-ink">{{ item.file.name }}</p>
                <p class="text-xs text-graphite">{{ fileSize(item.file.size) }}</p>
              </div>
              <button
                class="focus-ring rounded p-1 text-graphite hover:text-berry"
                type="button"
                @click="files.removeFromQueue(item.id)"
              >
                <X class="h-4 w-4" />
              </button>
            </div>
          </div>
          <p v-else class="mt-4 rounded-md border border-dashed border-slate-200 px-4 py-5 text-center text-sm text-graphite">
            No files added yet. These are uploaded automatically when you submit.
          </p>
        </section>

        <!-- Style references (designs, diagrams, templates) -->
        <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-base font-semibold text-ink">Style guide / designs</h2>
              <p class="mt-0.5 text-xs text-graphite">Upload diagrams, templates, brand guides, or design files the writer should follow.</p>
            </div>
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-ink"
              type="button"
              @click="pickStyleFiles"
            >
              <Paperclip class="h-4 w-4" />
              Add designs
            </button>
          </div>

          <input
            ref="styleFileInputRef"
            class="sr-only"
            type="file"
            multiple
            accept=".pdf,.png,.jpg,.jpeg,.svg,.fig,.sketch,.ai,.zip,.docx"
            @change="onStyleFilesSelected"
          />

          <div v-if="files.uploadQueue.filter(q => q.purpose === 'style_reference').length" class="mt-4 space-y-2">
            <div
              v-for="item in files.uploadQueue.filter(q => q.purpose === 'style_reference')"
              :key="item.id"
              class="flex items-center gap-3 rounded-md border border-slate-100 bg-slate-50 px-3 py-2 text-sm"
            >
              <Paperclip class="h-4 w-4 shrink-0 text-graphite" />
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-ink">{{ item.file.name }}</p>
                <p class="text-xs text-graphite">{{ fileSize(item.file.size) }}</p>
              </div>
              <button
                class="focus-ring rounded p-1 text-graphite hover:text-berry"
                type="button"
                @click="files.removeFromQueue(item.id)"
              >
                <X class="h-4 w-4" />
              </button>
            </div>
          </div>
          <p v-else class="mt-4 rounded-md border border-dashed border-slate-200 px-4 py-5 text-center text-sm text-graphite">
            No designs added. Optional — skip if not applicable.
          </p>
        </section>

        <!-- Order summary -->
        <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-start gap-3">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-600">
              <FileText class="h-4 w-4" />
            </div>
            <div>
              <h2 class="text-base font-semibold text-ink">Order summary</h2>
              <p class="mt-0.5 text-xs leading-5 text-graphite">
                Review the visible choices before calculating the price.
              </p>
            </div>
          </div>

          <div class="mt-4 grid gap-3 sm:grid-cols-2">
            <div
              v-for="item in selectedBrief"
              :key="item.label"
              class="rounded-md border border-slate-100 bg-slate-50 px-3 py-2.5"
            >
              <p class="text-[11px] font-semibold uppercase text-graphite">{{ item.label }}</p>
              <p class="mt-1 text-sm font-semibold text-ink">{{ item.value }}</p>
              <p v-if="item.detail" class="mt-1 text-xs leading-5 text-graphite">{{ item.detail }}</p>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar -->
      <aside class="space-y-4">
        <div v-if="config.error" class="flex items-center justify-between gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <span>{{ config.error }}</span>
          <button
            class="inline-flex shrink-0 items-center gap-1.5 rounded border border-amber-300 bg-white px-2.5 py-1 text-xs font-semibold text-amber-800 transition-colors hover:bg-amber-50 disabled:opacity-50"
            type="button"
            :disabled="config.isLoading"
            @click="loadConfig"
          >
            <RefreshCw class="h-3 w-3" :class="config.isLoading ? 'animate-spin' : ''" />
            Retry
          </button>
        </div>

        <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Price estimate</h2>

          <div v-if="orders.latestQuote" class="mt-3 rounded-md bg-slate-50 p-3">
            <p class="text-xs text-graphite">Calculated total</p>
            <template v-if="discountPreview">
              <p class="mt-1 text-sm text-graphite line-through">
                {{ orders.latestQuote.currency }} {{ orders.latestQuote.calculated_price }}
              </p>
              <p class="text-2xl font-semibold text-emerald-700">
                {{ orders.latestQuote.currency }} {{ discountPreview.final.toFixed(2) }}
              </p>
              <p class="mt-0.5 text-xs text-emerald-600">
                Code <strong>{{ discountPreview.code }}</strong> saves {{ orders.latestQuote.currency }} {{ discountPreview.amount.toFixed(2) }}
              </p>
            </template>
            <p v-else class="mt-1 text-2xl font-semibold text-ink">
              {{ orders.latestQuote.currency }} {{ orders.latestQuote.calculated_price }}
            </p>
            <p class="mt-1 text-xs text-graphite">
              {{ form.pages }} page{{ form.pages !== 1 ? "s" : "" }} ·
              {{ wordRange.min }}–{{ wordRange.max }} words ·
              {{ deadlineLabel }}
            </p>
          </div>
          <p v-else class="mt-3 text-sm text-graphite">Fill in the order details and calculate a price.</p>

          <div class="mt-3 space-y-2 rounded-md border border-slate-100 bg-white px-3 py-2.5">
            <div class="flex items-center gap-2 text-xs font-semibold text-graphite">
              <Clock class="h-3.5 w-3.5" />
              Deadline window
            </div>
            <p class="text-sm font-semibold text-ink">{{ deadlineLabel }}</p>
            <p class="text-xs leading-5 text-graphite">
              {{ deadlineHours <= 24 ? "This will be treated as urgent." : "There is enough lead time for normal routing." }}
            </p>
          </div>

          <button
            class="focus-ring mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="!canQuote || orders.isLoading"
            type="button"
            @click="calculate"
          >
            <Loader2 v-if="orders.isLoading" class="h-4 w-4 animate-spin" />
            <Calculator v-else class="h-4 w-4" />
            {{ orders.isLoading ? "Calculating…" : "Calculate price" }}
          </button>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Readiness</h2>
          <div class="mt-3 space-y-2">
            <div
              v-for="item in readinessItems"
              :key="item.label"
              class="flex items-center gap-2 text-sm"
              :class="item.done ? 'text-emerald-700' : 'text-graphite'"
            >
              <CheckCircle2 class="h-4 w-4 shrink-0" :class="item.done ? 'text-emerald-500' : 'text-slate-300'" />
              <span>{{ item.label }}</span>
            </div>
          </div>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Discount code</h2>
          <div class="mt-3 flex gap-2">
            <input
              v-model.trim="couponCode"
              type="text"
              placeholder="Enter promo or discount code"
              class="focus-ring min-w-0 flex-1 rounded-lg border px-3 py-2 text-sm font-mono uppercase"
              :class="couponApplied ? 'border-emerald-400 bg-emerald-50' : couponError ? 'border-red-300' : 'border-slate-200'"
              @input="couponApplied = false; couponError = ''; discountPreview = null"
              @keydown.enter.prevent="applyDiscount"
            />
            <button
              v-if="couponCode && !couponApplied"
              type="button"
              :disabled="applyingCoupon || quotedPrice == null"
              class="rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-2 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 disabled:opacity-50"
              @click="applyDiscount"
            >{{ applyingCoupon ? "…" : "Apply" }}</button>
            <button
              v-if="couponCode"
              type="button"
              class="rounded-lg border border-slate-200 px-3 py-2 text-xs text-graphite hover:bg-slate-50"
              @click="couponCode = ''; couponApplied = false; couponError = ''; discountPreview = null"
            >Clear</button>
          </div>
          <p v-if="couponApplied && discountPreview" class="mt-1.5 text-xs text-emerald-700 font-medium">
            ✓ Code applied — price updated above.
          </p>
          <p v-else-if="couponError" class="mt-1.5 text-xs text-red-600">{{ couponError }}</p>
          <p v-else-if="couponCode && quotedPrice == null" class="mt-1.5 text-xs text-graphite">Calculate a price first, then apply your code.</p>
          <p v-else class="mt-1.5 text-xs text-graphite">Applied at checkout if valid for your order.</p>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 class="text-base font-semibold text-ink">Payment</h2>
          <div class="mt-3">
            <PaymentMethodSelector v-model="paymentMethod" :price="quotedPrice" />
          </div>
        </section>

        <!-- ── Add-ons ──────────────────────────────────────────────────── -->
        <section v-if="availableAddons.length" class="rounded-xl border border-slate-200 bg-white p-5">
          <h2 class="text-sm font-semibold text-ink">Optional Add-ons</h2>
          <p class="mt-0.5 text-xs text-graphite">Enhance your order with one or more add-ons.</p>
          <div class="mt-3 space-y-2">
            <label
              v-for="addon in availableAddons"
              :key="addon.addon_code"
              class="flex items-start gap-3 cursor-pointer rounded-lg border p-3 transition-colors"
              :class="selectedAddonCodes.includes(addon.addon_code)
                ? 'border-berry/60 bg-berry/5'
                : 'border-slate-200 hover:border-slate-300'"
            >
              <input
                type="checkbox"
                :checked="selectedAddonCodes.includes(addon.addon_code)"
                class="mt-0.5 rounded accent-berry"
                @change="toggleAddon(addon.addon_code)"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-ink">{{ addon.name }}</p>
                <p v-if="addon.description" class="text-xs text-graphite mt-0.5">{{ addon.description }}</p>
              </div>
              <span class="text-sm font-semibold text-ink shrink-0">+${{ addon.flat_amount }}</span>
            </label>
          </div>
          <p v-if="addonTotal > 0" class="mt-2 text-xs text-graphite text-right">
            Add-ons: <strong class="text-ink">${{ addonTotal.toFixed(2) }}</strong>
          </p>
        </section>

        <div class="space-y-2">
          <PaymentDisclosureBanner v-model="paymentDisclosureAccepted" context="new_order_checkout" />
          <button
            class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="!canQuote || orders.isCreating || !paymentDisclosureAccepted"
            type="submit"
          >
            <Loader2 v-if="orders.isCreating" class="h-4 w-4 animate-spin" />
            <Send v-else class="h-4 w-4" />
            {{ orders.isCreating ? "Placing order…" : "Place order" }}
          </button>

          <p v-if="files.uploadQueue.length" class="text-center text-xs text-graphite">
            {{ files.uploadQueue.length }} file{{ files.uploadQueue.length !== 1 ? "s" : "" }} will be uploaded with your order.
          </p>
        </div>

        <div v-if="error" class="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-3 text-sm text-rose-800" role="alert">
          <span class="shrink-0 font-bold">!</span>
          {{ error }}
        </div>
        <div v-if="success" class="flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3.5 py-3 text-sm text-emerald-800" role="status">
          <span class="shrink-0 font-bold"></span>
          {{ success }}
        </div>
        <PaymentDisclosureBanner v-if="success" variant="post" />
      </aside>
    </form>
  </div>
</template>
