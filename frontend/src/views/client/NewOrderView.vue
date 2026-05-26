<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { Calculator, RefreshCw, Send } from "@lucide/vue";
import ConfigSelect from "@/components/forms/ConfigSelect.vue";
import PaymentMethodSelector from "@/components/payment/PaymentMethodSelector.vue";
import type { PaymentMethod } from "@/components/payment/PaymentMethodSelector.vue";
import { useOrderConfigStore } from "@/stores/orderConfig";
import { useOrderStore } from "@/stores/orders";
import { useWalletStore } from "@/stores/wallets";
import type { PaperQuotePayload } from "@/types/orders";

const router = useRouter();
const orders = useOrderStore();
const config = useOrderConfigStore();
const wallets = useWalletStore();
const error = ref("");
const success = ref("");
const showAdvancedIds = ref(false);
const paymentMethod = ref<PaymentMethod>("wallet");

const providerFor: Record<PaymentMethod, { payment_provider?: string; payment_method_code?: string }> = {
  wallet: {},
  stripe: { payment_provider: "stripe", payment_method_code: "card" },
  mock: { payment_provider: "mock", payment_method_code: "mock_card" },
};

const quotedPrice = computed(() => {
  const raw = orders.latestQuote?.calculated_price;
  if (raw == null) return null;
  return Number(raw);
});

const form = reactive({
  topic: "",
  order_instructions: "",
  client_deadline: "",
  pages: 1,
  deadline_hours: 72,
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

const canQuote = computed(
  () => form.topic.trim().length > 2 && form.order_instructions.trim().length > 10,
);

function optionCode(collection: keyof typeof config.collections, id: number | null) {
  const option = config.collections[collection].find((item) => item.id === id);
  return String(option?.code || option?.slug || option?.name || "").trim();
}

function quotePayload(): PaperQuotePayload {
  return {
    service_code: form.service_code,
    pages: form.pages,
    deadline_hours: form.deadline_hours,
    spacing: form.spacing,
    paper_type_code: optionCode("paperTypes", form.paper_type_id) || form.paper_type_code,
    work_type_code: optionCode("typesOfWork", form.type_of_work_id) || form.work_type_code,
    subject_code: optionCode("subjects", form.subject_id) || form.subject_code,
    academic_level_code:
      optionCode("academicLevels", form.academic_level_id) || form.academic_level_code,
    topic: form.topic,
    instructions: form.order_instructions,
  };
}

async function loadConfig() {
  try {
    await config.fetchAll();
    showAdvancedIds.value = !config.hasLiveOptions;
  } catch {
    showAdvancedIds.value = true;
  }
  wallets.fetchWallet().catch(() => undefined);
}

async function calculate() {
  error.value = "";
  success.value = "";
  try {
    await orders.pricePaperOrder(quotePayload());
    success.value = "Quote calculated.";
  } catch {
    error.value = "Pricing failed. Check the service/config codes and try again.";
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
      client_deadline: new Date(form.client_deadline || Date.now() + form.deadline_hours * 3600000).toISOString(),
      paper_type_id: form.paper_type_id,
      academic_level_id: form.academic_level_id,
      formatting_style_id: form.formatting_style_id,
      subject_id: form.subject_id,
      type_of_work_id: form.type_of_work_id,
      english_type_id: form.english_type_id,
      writer_level_id: form.writer_level_id,
      is_urgent: form.deadline_hours <= 24,
      ...provider,
    });
    if (created.checkout_started) {
      const checkoutUrl = (created.payment_intent as Record<string, unknown> | null)?.checkout_url;
      if (typeof checkoutUrl === "string") {
        window.location.href = checkoutUrl;
        return;
      }
    }
    success.value = created.message;
    await router.push("/client/orders");
  } catch {
    error.value = "Order creation failed. Check that all fields are complete and try again.";
  }
}

watch(
  () => form.paper_type_id,
  (id) => {
    const code = optionCode("paperTypes", id);
    if (code) form.paper_type_code = code;
  },
);

watch(
  () => form.type_of_work_id,
  (id) => {
    const code = optionCode("typesOfWork", id);
    if (code) form.work_type_code = code;
  },
);

watch(
  () => form.subject_id,
  (id) => {
    const code = optionCode("subjects", id);
    if (code) form.subject_code = code;
  },
);

watch(
  () => form.academic_level_id,
  (id) => {
    const code = optionCode("academicLevels", id);
    if (code) form.academic_level_code = code;
  },
);

onMounted(loadConfig);
</script>

<template>
  <div class="mx-auto max-w-5xl space-y-5">
    <section>
      <p class="text-sm font-semibold uppercase text-signal">Client</p>
      <h1 class="mt-2 text-3xl font-semibold">New order</h1>
      <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
        This first version follows the backend quote-to-snapshot-to-order flow.
        Live config options appear when the account can access order configuration.
      </p>
    </section>

    <form class="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]" @submit.prevent="submit">
      <section class="space-y-4 rounded-md border border-slate-200 bg-white p-5 shadow-panel">
        <label class="block">
          <span class="text-sm font-medium text-graphite">Topic</span>
          <input
            v-model="form.topic"
            class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3"
            type="text"
          />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-graphite">Instructions</span>
          <textarea
            v-model="form.order_instructions"
            class="focus-ring mt-1 min-h-36 w-full rounded-md border border-slate-200 px-3 py-2"
          />
        </label>

        <div class="grid gap-4 sm:grid-cols-3">
          <label class="block">
            <span class="text-sm font-medium text-graphite">Pages</span>
            <input v-model.number="form.pages" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3" min="1" type="number" />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-graphite">Deadline hours</span>
            <input v-model.number="form.deadline_hours" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3" min="1" type="number" />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-graphite">Spacing</span>
            <select v-model="form.spacing" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3">
              <option value="double">Double</option>
              <option value="single">Single</option>
            </select>
          </label>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block">
            <span class="text-sm font-medium text-graphite">Service code</span>
            <input v-model="form.service_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3" />
          </label>
          <ConfigSelect
            v-if="config.collections.paperTypes.length"
            v-model="form.paper_type_id"
            label="Paper type"
            :options="config.collections.paperTypes"
          />
          <label class="block">
            <span class="text-sm font-medium text-graphite">Paper type code</span>
            <input v-model="form.paper_type_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3" />
          </label>
          <ConfigSelect
            v-if="config.collections.typesOfWork.length"
            v-model="form.type_of_work_id"
            label="Type of work"
            :options="config.collections.typesOfWork"
          />
          <label class="block">
            <span class="text-sm font-medium text-graphite">Work type code</span>
            <input v-model="form.work_type_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3" />
          </label>
          <ConfigSelect
            v-if="config.collections.subjects.length"
            v-model="form.subject_id"
            label="Subject"
            :options="config.collections.subjects"
          />
          <label class="block">
            <span class="text-sm font-medium text-graphite">Subject code</span>
            <input v-model="form.subject_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3" />
          </label>
          <ConfigSelect
            v-if="config.collections.academicLevels.length"
            v-model="form.academic_level_id"
            label="Academic level"
            :options="config.collections.academicLevels"
          />
          <label class="block">
            <span class="text-sm font-medium text-graphite">Academic level code</span>
            <input v-model="form.academic_level_code" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3" />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-graphite">Client deadline</span>
            <input v-model="form.client_deadline" class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3" type="datetime-local" />
          </label>
        </div>
      </section>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-base font-semibold">Configuration</h2>
              <p class="mt-1 text-sm text-graphite">
                {{ config.hasLiveOptions ? "Live options loaded." : "Advanced fallback fields available." }}
              </p>
            </div>
            <button
              class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200"
              type="button"
              title="Reload configuration"
              @click="loadConfig"
            >
              <RefreshCw class="h-4 w-4" />
            </button>
          </div>
          <p
            v-if="config.error"
            class="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900"
          >
            {{ config.error }}
          </p>
          <button
            class="focus-ring mt-4 h-10 rounded-md border border-slate-200 px-3 text-sm font-semibold"
            type="button"
            @click="showAdvancedIds = !showAdvancedIds"
          >
            {{ showAdvancedIds ? "Hide" : "Show" }} advanced IDs
          </button>
          <div class="mt-4 grid gap-3">
            <template v-if="showAdvancedIds">
            <label class="block">
              <span class="text-sm font-medium text-graphite">Paper type ID</span>
              <input v-model.number="form.paper_type_id" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3" min="1" type="number" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Type of work ID</span>
              <input v-model.number="form.type_of_work_id" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3" min="1" type="number" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Subject ID</span>
              <input v-model.number="form.subject_id" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3" min="1" type="number" />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Academic level ID</span>
              <input v-model.number="form.academic_level_id" class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3" min="1" type="number" />
            </label>
            </template>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <h2 class="text-base font-semibold">Quote</h2>
          <div v-if="orders.latestQuote" class="mt-3 rounded-md bg-slate-50 p-3">
            <p class="text-sm text-graphite">Calculated total</p>
            <p class="mt-1 text-2xl font-semibold">
              {{ orders.latestQuote.currency }} {{ orders.latestQuote.calculated_price }}
            </p>
          </div>
          <div class="mt-4">
            <PaymentMethodSelector v-model="paymentMethod" :price="quotedPrice" />
          </div>
          <div class="mt-4 grid gap-2">
            <button
              class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
              :disabled="!canQuote || orders.isLoading"
              type="button"
              @click="calculate"
            >
              <Calculator class="h-4 w-4" />
              {{ orders.isLoading ? "Calculating" : "Calculate" }}
            </button>
            <button
              class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:bg-slate-400"
              :disabled="!canQuote || orders.isCreating"
              type="submit"
            >
              <Send class="h-4 w-4" />
              {{ orders.isCreating ? "Creating order…" : "Create order" }}
            </button>
          </div>
          <p v-if="error" class="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">{{ error }}</p>
          <p v-if="success" class="mt-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">{{ success }}</p>
        </section>
      </aside>
    </form>
  </div>
</template>
