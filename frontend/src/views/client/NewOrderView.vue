<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { Calculator, Paperclip, Send, X } from "@lucide/vue";
import ConfigSelect from "@/components/forms/ConfigSelect.vue";
import PaymentMethodSelector from "@/components/payment/PaymentMethodSelector.vue";
import type { PaymentMethod } from "@/components/payment/PaymentMethodSelector.vue";
import { useFilesStore } from "@/stores/files";
import { useOrderConfigStore } from "@/stores/orderConfig";
import { useOrderStore } from "@/stores/orders";
import { useWalletStore } from "@/stores/wallets";
import type { PaperQuotePayload } from "@/types/orders";

const router = useRouter();
const orders = useOrderStore();
const config = useOrderConfigStore();
const wallets = useWalletStore();
const files = useFilesStore();

const error = ref("");
const success = ref("");
const paymentMethod = ref<PaymentMethod>("wallet");
const showAdvanced = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

const providerFor: Record<PaymentMethod, { payment_provider?: string; payment_method_code?: string }> = {
  wallet: {},
  stripe: { payment_provider: "stripe", payment_method_code: "card" },
  mock: { payment_provider: "mock", payment_method_code: "mock_card" },
};

function defaultDeadline() {
  return new Date(Date.now() + 72 * 3600 * 1000).toISOString().slice(0, 16);
}

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
  paper_type_id: 1,
  type_of_work_id: 1,
  subject_id: 1,
  academic_level_id: 1,
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

const canQuote = computed(
  () => form.topic.trim().length > 2 && form.order_instructions.trim().length > 10,
);

function optionCode(collection: keyof typeof config.collections, id: number | null) {
  const option = config.collections[collection].find((item) => item.id === id);
  return String(option?.code || (option as { slug?: string })?.slug || option?.name || "").trim();
}

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
  };
}

async function loadConfig() {
  error.value = "";
  try {
    await config.fetchAll();
  } catch {
    showAdvanced.value = true;
  }
  wallets.fetchWallet().catch(() => undefined);
}

async function calculate() {
  error.value = "";
  success.value = "";
  try {
    await orders.pricePaperOrder(quotePayload());
  } catch {
    error.value = "Pricing failed. Check your order details and try again.";
  }
}

async function submit() {
  error.value = "";
  success.value = "";
  try {
    const provider = providerFor[paymentMethod.value];
    const created = await orders.createPaperOrder(quotePayload(), {
      topic: form.topic,
      order_instructions: form.order_instructions,
      client_deadline: new Date(form.client_deadline).toISOString(),
      paper_type_id: form.paper_type_id,
      academic_level_id: form.academic_level_id,
      formatting_style_id: form.formatting_style_id,
      subject_id: form.subject_id,
      type_of_work_id: form.type_of_work_id,
      english_type_id: form.english_type_id,
      writer_level_id: form.writer_level_id,
      is_urgent: deadlineHours.value <= 24,
      ...provider,
    });

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
  files.addToQueue(input.files, { purpose: "order_reference", visibility: "order_participants" });
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

onMounted(loadConfig);
</script>

<template>
  <div class="mx-auto max-w-5xl space-y-5">
    <section>
      <p class="text-sm font-semibold uppercase text-signal">Client</p>
      <h1 class="mt-2 text-3xl font-semibold text-ink">New order</h1>
      <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
        Fill in your order details, attach any reference materials, then calculate a price and submit.
      </p>
    </section>

    <form class="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]" @submit.prevent="submit">
      <div class="space-y-4">
        <!-- Order brief -->
        <section class="space-y-4 rounded-md border border-slate-200 bg-white p-5 shadow-panel">
          <h2 class="text-base font-semibold text-ink">Order brief</h2>

          <label class="block">
            <span class="text-sm font-medium text-graphite">Topic <span class="text-berry">*</span></span>
            <input
              v-model="form.topic"
              required
              class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
              placeholder="e.g. Climate change and food security in Sub-Saharan Africa"
              type="text"
            />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-graphite">Instructions <span class="text-berry">*</span></span>
            <textarea
              v-model="form.order_instructions"
              required
              class="focus-ring mt-1 min-h-36 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              placeholder="Include your assignment prompt, citation style, sources required, and any specific requirements from your instructor…"
            />
          </label>
        </section>

        <!-- Paper specifics -->
        <section class="space-y-4 rounded-md border border-slate-200 bg-white p-5 shadow-panel">
          <h2 class="text-base font-semibold text-ink">Paper specifics</h2>

          <div class="grid gap-4 sm:grid-cols-2">
            <!-- Paper type -->
            <div>
              <ConfigSelect
                v-if="config.collections.paperTypes.length"
                v-model="form.paper_type_id"
                label="Paper type"
                :options="config.collections.paperTypes"
              />
              <label v-else class="block">
                <span class="text-sm font-medium text-graphite">Paper type</span>
                <input v-model="form.paper_type_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="essay" />
              </label>
            </div>

            <!-- Type of work -->
            <div>
              <ConfigSelect
                v-if="config.collections.typesOfWork.length"
                v-model="form.type_of_work_id"
                label="Type of work"
                :options="config.collections.typesOfWork"
              />
              <label v-else class="block">
                <span class="text-sm font-medium text-graphite">Type of work</span>
                <input v-model="form.work_type_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="writing" />
              </label>
            </div>

            <!-- Subject -->
            <div>
              <ConfigSelect
                v-if="config.collections.subjects.length"
                v-model="form.subject_id"
                label="Subject"
                :options="config.collections.subjects"
              />
              <label v-else class="block">
                <span class="text-sm font-medium text-graphite">Subject</span>
                <input v-model="form.subject_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="general" />
              </label>
            </div>

            <!-- Academic level -->
            <div>
              <ConfigSelect
                v-if="config.collections.academicLevels.length"
                v-model="form.academic_level_id"
                label="Academic level"
                :options="config.collections.academicLevels"
              />
              <label v-else class="block">
                <span class="text-sm font-medium text-graphite">Academic level</span>
                <input v-model="form.academic_level_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm" placeholder="undergraduate" />
              </label>
            </div>

            <!-- Formatting style (optional) -->
            <div v-if="config.collections.formattingStyles.length">
              <ConfigSelect
                v-model="form.formatting_style_id"
                label="Formatting style"
                :options="config.collections.formattingStyles"
              />
            </div>
          </div>
        </section>

        <!-- Scope and deadline -->
        <section class="space-y-4 rounded-md border border-slate-200 bg-white p-5 shadow-panel">
          <h2 class="text-base font-semibold text-ink">Scope &amp; deadline</h2>

          <div class="grid gap-4 sm:grid-cols-3">
            <label class="block">
              <span class="text-sm font-medium text-graphite">Pages</span>
              <input
                v-model.number="form.pages"
                class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm"
                min="1"
                max="500"
                type="number"
              />
              <span class="mt-1 block text-xs text-graphite">~{{ form.pages * 275 }} words</span>
            </label>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Spacing</span>
              <select v-model="form.spacing" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3 text-sm">
                <option value="double">Double</option>
                <option value="single">Single</option>
              </select>
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
        <section class="rounded-md border border-slate-200 bg-white p-5 shadow-panel">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-base font-semibold text-ink">Reference materials</h2>
              <p class="mt-1 text-sm text-graphite">Attach your assignment brief, rubric, examples, or any files the writer needs.</p>
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

        <!-- Advanced options -->
        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
          <button
            class="flex w-full items-center justify-between px-5 py-4 text-sm font-semibold text-graphite"
            type="button"
            @click="showAdvanced = !showAdvanced"
          >
            Advanced options
            <span class="text-xs font-normal">{{ showAdvanced ? "Hide" : "Show" }}</span>
          </button>

          <div v-if="showAdvanced" class="grid gap-4 border-t border-slate-100 px-5 pb-5 pt-4 sm:grid-cols-2">
            <label class="block">
              <span class="text-sm font-medium text-graphite">Service code</span>
              <input v-model="form.service_code" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Paper type code</span>
              <input v-model="form.paper_type_code" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Work type code</span>
              <input v-model="form.work_type_code" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Subject code</span>
              <input v-model="form.subject_code" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Academic level code</span>
              <input v-model="form.academic_level_code" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Paper type ID</span>
              <input v-model.number="form.paper_type_id" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" min="1" type="number" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Subject ID</span>
              <input v-model.number="form.subject_id" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" min="1" type="number" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Academic level ID</span>
              <input v-model.number="form.academic_level_id" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm" min="1" type="number" />
            </label>
          </div>
        </section>
      </div>

      <!-- Sidebar -->
      <aside class="space-y-4">
        <div v-if="config.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Config unavailable — using manual fields.
        </div>

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <h2 class="text-base font-semibold text-ink">Price estimate</h2>

          <div v-if="orders.latestQuote" class="mt-3 rounded-md bg-slate-50 p-3">
            <p class="text-xs text-graphite">Calculated total</p>
            <p class="mt-1 text-2xl font-semibold text-ink">
              {{ orders.latestQuote.currency }} {{ orders.latestQuote.calculated_price }}
            </p>
            <p class="mt-1 text-xs text-graphite">{{ form.pages }} page{{ form.pages !== 1 ? "s" : "" }} · {{ deadlineLabel }}</p>
          </div>
          <p v-else class="mt-3 text-sm text-graphite">Fill in the order details and calculate a price.</p>

          <button
            class="focus-ring mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
            :disabled="!canQuote || orders.isLoading"
            type="button"
            @click="calculate"
          >
            <Calculator class="h-4 w-4" />
            {{ orders.isLoading ? "Calculating…" : "Calculate price" }}
          </button>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <h2 class="text-base font-semibold text-ink">Payment</h2>
          <div class="mt-3">
            <PaymentMethodSelector v-model="paymentMethod" :price="quotedPrice" />
          </div>
        </section>

        <div class="space-y-2">
          <button
            class="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-3 text-sm font-semibold text-white disabled:bg-slate-400"
            :disabled="!canQuote || orders.isCreating"
            type="submit"
          >
            <Send class="h-4 w-4" />
            {{ orders.isCreating ? "Placing order…" : "Place order" }}
          </button>

          <p v-if="files.uploadQueue.length" class="text-center text-xs text-graphite">
            {{ files.uploadQueue.length }} file{{ files.uploadQueue.length !== 1 ? "s" : "" }} will be uploaded with your order.
          </p>
        </div>

        <p v-if="error" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">{{ error }}</p>
        <p v-if="success" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">{{ success }}</p>
      </aside>
    </form>
  </div>
</template>
