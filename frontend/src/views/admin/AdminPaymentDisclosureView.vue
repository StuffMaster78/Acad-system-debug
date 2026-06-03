<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { CreditCard, RefreshCw, Save } from "@lucide/vue";
import { websitesApi, type PaymentDisclosureConfig } from "@/api/websites";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";

const auth = useAuthStore();
const portal = usePortalContextStore();
const websites = useWebsitesStore();

const selectedWebsiteId = ref<number | null>(null);
const config = ref<PaymentDisclosureConfig | null>(null);
const isLoading = ref(false);
const isSaving = ref(false);
const error = ref("");
const notice = ref("");

const draft = reactive({
  brand_name: "",
  processor_display_name: "",
  statement_descriptor: "",
  client_disclosure_text: "",
  support_contact: "",
  requires_acknowledgement: true,
});

const isSuperadmin = computed(() => auth.role === "superadmin");
const websiteParams = computed(() =>
  isSuperadmin.value && selectedWebsiteId.value ? { website_id: selectedWebsiteId.value } : undefined,
);
const websiteLabel = computed(() => {
  if (selectedWebsiteId.value) return websites.labelById(selectedWebsiteId.value);
  if (config.value?.website_name || config.value?.website_domain) {
    return config.value.website_domain
      ? `${config.value.website_name || config.value.website_domain} (${config.value.website_domain})`
      : config.value.website_name || "Current website";
  }
  if (portal.website) return `${portal.website.name} (${portal.website.domain})`;
  return "Current website";
});

const previewText = computed(() =>
  draft.client_disclosure_text.trim()
    || `You are placing this order with ${draft.brand_name || "this website"}. Payments are securely processed by ${draft.processor_display_name || "our billing partner"}. Your card statement may show ${draft.statement_descriptor || draft.processor_display_name || "the billing partner name"}.`,
);

function syncDraft(next: PaymentDisclosureConfig) {
  Object.assign(draft, {
    brand_name: next.brand_name || "",
    processor_display_name: next.processor_display_name || "",
    statement_descriptor: next.statement_descriptor || "",
    client_disclosure_text: next.client_disclosure_text || "",
    support_contact: next.support_contact || "",
    requires_acknowledgement: next.requires_acknowledgement,
  });
}

async function load() {
  isLoading.value = true;
  error.value = "";
  notice.value = "";
  try {
    const { data } = await websitesApi.paymentDisclosure(websiteParams.value);
    config.value = data;
    syncDraft(data);
  } catch {
    error.value = "Unable to load payment disclosure settings.";
    config.value = null;
  } finally {
    isLoading.value = false;
  }
}

async function save() {
  isSaving.value = true;
  error.value = "";
  notice.value = "";
  try {
    const { data } = await websitesApi.updatePaymentDisclosure({ ...draft }, websiteParams.value);
    config.value = data;
    syncDraft(data);
    notice.value = "Payment disclosure saved.";
  } catch {
    error.value = "Unable to save payment disclosure.";
  } finally {
    isSaving.value = false;
  }
}

async function switchWebsite() {
  await load();
}

onMounted(async () => {
  await websites.ensure();
  selectedWebsiteId.value = portal.website?.id ?? websites.list[0]?.id ?? null;
  await load();
});
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-5xl space-y-5">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-xl font-bold text-ink">Payment Disclosure</h1>
          <p class="text-sm text-graphite">Control the processor name, card statement descriptor, and client-facing payment notice.</p>
          <p class="mt-1 text-xs font-medium text-graphite">Website: {{ websiteLabel }}</p>
        </div>
        <div class="flex flex-wrap items-center justify-end gap-2">
          <label v-if="isSuperadmin" class="min-w-64 text-xs font-medium text-graphite">
            Manage website
            <select
              v-model.number="selectedWebsiteId"
              class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-ink focus-ring"
              @change="switchWebsite"
            >
              <option v-for="site in websites.options" :key="site.value" :value="site.value">{{ site.label }}</option>
            </select>
          </label>
          <button class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-graphite hover:text-ink" @click="load">
            <RefreshCw class="size-4" :class="{ 'animate-spin': isLoading }" />
            Refresh
          </button>
        </div>
      </div>

      <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>
      <div v-if="notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ notice }}</div>

      <section class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="mb-4 flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <CreditCard class="size-4 text-berry" />
            <h2 class="text-sm font-semibold text-ink">Client payment notice</h2>
          </div>
          <button class="inline-flex items-center gap-2 rounded-lg bg-berry px-4 py-2 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60" :disabled="isSaving" @click="save">
            <Save class="size-4" /> {{ isSaving ? "Saving..." : "Save disclosure" }}
          </button>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <label class="text-sm">
            <span class="mb-1 block font-medium text-ink">Client website/brand name</span>
            <input v-model="draft.brand_name" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
          </label>
          <label class="text-sm">
            <span class="mb-1 block font-medium text-ink">Processor display name</span>
            <input v-model="draft.processor_display_name" placeholder="e.g. OrderBridge Payments" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
          </label>
          <label class="text-sm">
            <span class="mb-1 block font-medium text-ink">Statement descriptor</span>
            <input v-model="draft.statement_descriptor" maxlength="22" placeholder="e.g. ORDERBRIDGE PAY" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
            <span class="mt-1 block text-xs text-graphite">{{ draft.statement_descriptor.length }}/22 characters</span>
          </label>
          <label class="text-sm">
            <span class="mb-1 block font-medium text-ink">Billing support contact</span>
            <input v-model="draft.support_contact" placeholder="billing@example.com" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
          </label>
          <label class="text-sm sm:col-span-2">
            <span class="mb-1 block font-medium text-ink">Custom disclosure text</span>
            <textarea v-model="draft.client_disclosure_text" rows="4" class="w-full rounded-lg border border-slate-200 px-3 py-2 focus-ring" />
          </label>
          <label class="flex items-center gap-2 text-sm text-graphite">
            <input v-model="draft.requires_acknowledgement" type="checkbox" class="rounded accent-berry" />
            Require client acknowledgement before payment
          </label>
        </div>
      </section>

      <section class="rounded-lg border border-slate-200 bg-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Client preview</p>
        <div class="mt-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-graphite">
          <p>{{ previewText }}</p>
          <p v-if="draft.support_contact" class="mt-2 text-xs">Billing support: {{ draft.support_contact }}</p>
          <label v-if="draft.requires_acknowledgement" class="mt-3 flex items-start gap-2 text-xs text-ink">
            <input type="checkbox" disabled class="mt-0.5 rounded accent-berry" />
            I understand what may appear on my card or bank statement.
          </label>
        </div>
      </section>
    </div>
  </div>
</template>
