<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import PaymentDisclosureBanner from "@/components/payment/PaymentDisclosureBanner.vue";
import { specialOrdersApi } from "@/api/specialOrders";
import { useAuthStore } from "@/stores/auth";
import type { SpecialOrderQuoteConfig } from "@/types/specialOrders";

const router = useRouter();
const auth = useAuthStore();

const title = ref("");
const description = ref("");
const deadline = ref("");
const budget = ref("");
const selectedTemplateId = ref<number | "">("");
const quoteConfig = ref<SpecialOrderQuoteConfig | null>(null);
const isLoadingConfig = ref(true);
const isSaving = ref(false);
const error = ref<string | null>(null);
const paymentDisclosureAccepted = ref(false);

const selectedTemplate = computed(() =>
  quoteConfig.value?.milestone_templates.find((t) => t.id === selectedTemplateId.value) ?? null,
);

const policySummary = computed(() => {
  const settings = quoteConfig.value?.settings;
  if (!settings) return "We will review your request and send a custom quote.";
  const deposit = `${settings.default_deposit_percentage}% deposit`;
  const installments = settings.allow_installments ? "installments available" : "full payment after quote";
  const expiry = `${settings.quote_expiry_hours}h quote window`;
  return `${deposit}, ${installments}, ${expiry}.`;
});

async function submit() {
  if (!title.value.trim() || !description.value.trim()) return;
  isSaving.value = true;
  error.value = null;
  try {
    if (auth.isPreviewSession) {
      router.push("/client/special-orders");
      return;
    }
    const details = [
      description.value,
      deadline.value ? `Preferred deadline: ${deadline.value}` : "",
      selectedTemplate.value ? `Preferred milestone style: ${selectedTemplate.value.name}` : "",
    ].filter(Boolean).join("\n\n");
    const res = await specialOrdersApi.createQuoted({
      title: title.value,
      inquiry_details: details,
      budget: budget.value || undefined,
    });
    router.push(`/client/special-orders/${res.data.id}`);
  } catch {
    error.value = "Failed to submit request. Please try again.";
  } finally {
    isSaving.value = false;
  }
}

onMounted(async () => {
  try {
    if (!auth.isPreviewSession) {
      const res = await specialOrdersApi.quoteConfig();
      quoteConfig.value = res.data;
      selectedTemplateId.value = res.data.milestone_templates[0]?.id ?? "";
    }
  } catch {
    quoteConfig.value = null;
  } finally {
    isLoadingConfig.value = false;
  }
});
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-2xl space-y-4">

      <div>
        <h1 class="text-xl font-bold text-ink">Request a Special Order</h1>
        <p class="text-sm text-graphite">Describe the custom work and we will send a scoped quote based on this website's configured payment rules.</p>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <div class="rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-800">
          <p class="font-semibold text-blue-950">Quote policy</p>
          <p class="mt-0.5">{{ isLoadingConfig ? "Loading quote policy…" : policySummary }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-ink mb-1">Project Title <span class="text-rose-500">*</span></label>
          <input
            v-model="title"
            placeholder="e.g. Dissertation Editing + Formatting"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
          />
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-ink mb-1">Budget range <span class="font-normal text-graphite">(optional)</span></label>
            <input
              v-model="budget"
              inputmode="decimal"
              placeholder="e.g. 250"
              class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink mb-1">Deadline (optional)</label>
            <input
              v-model="deadline"
              type="date"
              class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
            />
          </div>
        </div>

        <div v-if="quoteConfig?.milestone_templates.length">
          <label class="block text-sm font-medium text-ink mb-1">Preferred milestone style <span class="font-normal text-graphite">(optional)</span></label>
          <select v-model="selectedTemplateId" class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus-ring">
            <option value="">Let staff decide</option>
            <option v-for="template in quoteConfig.milestone_templates" :key="template.id" :value="template.id">
              {{ template.name }}
            </option>
          </select>
          <div v-if="selectedTemplate" class="mt-2 rounded-lg border border-slate-100 bg-slate-50 p-3">
            <p v-if="selectedTemplate.description" class="text-xs text-graphite">{{ selectedTemplate.description }}</p>
            <div class="mt-2 grid gap-1 text-xs text-graphite">
              <div v-for="item in selectedTemplate.items" :key="item.id" class="flex justify-between gap-3">
                <span>{{ item.label }}</span>
                <span class="font-medium text-ink">{{ item.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-ink mb-1">Project Description <span class="text-rose-500">*</span></label>
          <textarea
            v-model="description"
            rows="6"
            placeholder="Describe what you need in as much detail as possible. Include scope, requirements, formatting style, and any other relevant information…"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring resize-none"
          />
        </div>

        <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {{ error }}
        </div>

        <PaymentDisclosureBanner
          v-model="paymentDisclosureAccepted"
          context="special_order_request"
        />

        <div class="flex gap-3">
          <button
            class="rounded-lg bg-berry px-5 py-2 text-sm font-medium text-white hover:bg-berry/90 disabled:opacity-60"
            :disabled="isSaving || !title.trim() || !description.trim() || !paymentDisclosureAccepted"
            @click="submit"
          >
            {{ isSaving ? "Submitting…" : "Submit Request" }}
          </button>
          <button
            class="rounded-lg border border-slate-200 px-5 py-2 text-sm text-graphite hover:text-ink"
            @click="router.back()"
          >
            Cancel
          </button>
        </div>

      </div>

      <div class="rounded-lg border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-graphite space-y-1">
        <p class="font-medium text-ink">What happens next?</p>
        <p>1. We review your scope, budget, timeline, and preferred milestone style.</p>
        <p>2. You receive a detailed quote with payment requirements.</p>
        <p>3. Approve the quote to kick off your project.</p>
      </div>

    </div>
  </div>
</template>
