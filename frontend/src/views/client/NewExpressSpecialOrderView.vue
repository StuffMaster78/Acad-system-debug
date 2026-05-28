<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-3xl space-y-4">

      <!-- Back + heading -->
      <div>
        <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
          <ArrowLeft class="size-3.5" /> Special Orders
        </button>
        <div class="flex items-start justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold text-ink">Express Order</h1>
            <p class="mt-1 text-sm text-graphite">Pick a service, choose your timeline, and get an instant price.</p>
          </div>
          <button
            class="text-sm text-graphite hover:text-ink underline"
            @click="router.push('/client/special-orders/new')"
          >
            Need something custom?
          </button>
        </div>
      </div>

      <!-- Loading configs -->
      <div v-if="loadingConfigs" class="py-16 text-center text-graphite animate-pulse">
        Loading available services…
      </div>

      <!-- No configs -->
      <div v-else-if="!configs.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-16 text-center">
        <Zap class="mx-auto mb-3 size-8 text-slate-300" />
        <p class="text-sm text-graphite">No express services are currently available.</p>
        <button class="mt-3 text-sm font-medium text-berry hover:underline" @click="router.push('/client/special-orders/new')">
          Submit a custom quote request instead
        </button>
      </div>

      <template v-else>
        <!-- Step 1: Pick service -->
        <div class="space-y-3">
          <h2 class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-graphite">
            <span class="flex size-5 items-center justify-center rounded-full bg-berry text-xs font-bold text-white">1</span>
            Choose a Service
          </h2>
          <div class="grid gap-3 sm:grid-cols-2">
            <button
              v-for="cfg in configs"
              :key="cfg.id"
              class="rounded-xl border-2 bg-white p-4 text-left transition-all hover:border-berry hover:shadow-md"
              :class="selectedConfig?.id === cfg.id ? 'border-berry shadow-md' : 'border-slate-200'"
              @click="selectConfig(cfg)"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="font-semibold text-ink">{{ cfg.name }}</p>
                  <p class="mt-0.5 text-xs text-graphite line-clamp-2">{{ cfg.description }}</p>
                </div>
                <div class="shrink-0 text-right">
                  <p class="text-xs text-graphite">from</p>
                  <p class="font-bold text-ink">${{ cheapestDuration(cfg) }}</p>
                </div>
              </div>
              <div v-if="selectedConfig?.id === cfg.id" class="mt-2 flex items-center gap-1 text-xs font-semibold text-berry">
                <Check class="size-3.5" /> Selected
              </div>
            </button>
          </div>
        </div>

        <!-- Step 2: Choose duration (visible once service selected) -->
        <div v-if="selectedConfig" class="space-y-3">
          <h2 class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-graphite">
            <span class="flex size-5 items-center justify-center rounded-full bg-berry text-xs font-bold text-white">2</span>
            Choose Timeline
          </h2>
          <div class="grid gap-2 sm:grid-cols-3">
            <button
              v-for="dur in activeDurations"
              :key="dur.id"
              class="rounded-xl border-2 bg-white p-4 text-center transition-all hover:border-berry"
              :class="selectedDuration?.id === dur.id ? 'border-berry shadow-md' : 'border-slate-200'"
              @click="selectDuration(dur)"
            >
              <p class="text-xl font-bold text-ink">{{ dur.duration_days }}</p>
              <p class="text-xs text-graphite">{{ dur.duration_days === 1 ? 'day' : 'days' }}</p>
              <p class="mt-2 text-sm font-semibold text-ink">${{ dur.price }}</p>
            </button>
          </div>
        </div>

        <!-- Step 3: Price preview + details (visible once duration selected) -->
        <div v-if="selectedDuration" class="space-y-4">
          <h2 class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-graphite">
            <span class="flex size-5 items-center justify-center rounded-full bg-berry text-xs font-bold text-white">3</span>
            Order Details
          </h2>

          <!-- Price preview card -->
          <div class="rounded-lg border border-slate-200 bg-white p-5">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-sm font-medium text-ink">{{ selectedConfig?.name }}</p>
                <p class="mt-0.5 text-xs text-graphite">{{ selectedDuration?.duration_days }}-day delivery</p>
              </div>
              <div class="text-right">
                <div v-if="loadingPreview" class="text-sm text-graphite animate-pulse">Calculating…</div>
                <template v-else-if="pricePreview">
                  <p class="text-2xl font-bold text-ink">${{ pricePreview.final_amount }}</p>
                  <p v-if="Number(pricePreview.discount_amount) > 0" class="text-xs text-emerald-600">
                    Save ${{ pricePreview.discount_amount }}
                  </p>
                  <p v-if="Number(pricePreview.discount_amount) > 0" class="text-xs text-graphite line-through">
                    ${{ pricePreview.gross_amount }}
                  </p>
                </template>
                <p v-else class="text-xl font-bold text-ink">${{ selectedDuration.price }}</p>
              </div>
            </div>

            <!-- Line items -->
            <div v-if="pricePreview?.line_items?.length" class="mt-3 space-y-1 border-t border-slate-100 pt-3">
              <div v-for="(item, i) in pricePreview.line_items" :key="i" class="flex items-center justify-between text-xs text-graphite">
                <span>{{ (item as Record<string, string>).label }}</span>
                <span>${{ (item as Record<string, string>).amount }}</span>
              </div>
            </div>

            <!-- Coupon field -->
            <div class="mt-4 flex gap-2">
              <input
                v-model="couponCode"
                placeholder="Coupon code (optional)"
                class="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring"
                @blur="fetchPreview"
              />
              <button
                class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-graphite hover:text-ink"
                @click="fetchPreview"
              >
                Apply
              </button>
            </div>
          </div>

          <!-- Form card -->
          <div class="rounded-lg border border-slate-200 bg-white p-6 space-y-4">

            <!-- Title (optional) -->
            <div>
              <label class="block text-sm font-medium text-ink mb-1">Project title <span class="font-normal text-graphite">(optional)</span></label>
              <input v-model="form.title" placeholder="e.g. Nursing care plan — COPD patient" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
            </div>

            <!-- Inquiry details -->
            <div>
              <label class="block text-sm font-medium text-ink mb-1">Project details <span class="text-rose-500">*</span></label>
              <textarea
                v-model="form.inquiry_details"
                rows="5"
                placeholder="Describe your specific requirements — course, rubric, formatting style, platform details, special instructions…"
                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring resize-none"
              />
            </div>

            <!-- Platform -->
            <div>
              <label class="block text-sm font-medium text-ink mb-1">Platform / software <span class="font-normal text-graphite">(optional)</span></label>
              <input v-model="form.platform" placeholder="e.g. Shadow Health, SPSS, Excel, Canva" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
            </div>

            <!-- Writer level -->
            <div>
              <label class="block text-sm font-medium text-ink mb-1">Preferred writer level</label>
              <select v-model="form.writer_level" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring bg-white">
                <option value="">Standard</option>
                <option value="advanced">Advanced</option>
                <option value="expert">Expert</option>
              </select>
            </div>

            <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

            <div class="flex gap-3 pt-1">
              <button
                class="flex-1 rounded-lg bg-berry px-5 py-3 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60 transition-colors"
                :disabled="isSaving || !form.inquiry_details.trim()"
                @click="submit"
              >
                <span v-if="isSaving">Placing order…</span>
                <span v-else>Place Order — ${{ pricePreview?.final_amount ?? selectedDuration.price }}</span>
              </button>
              <button class="rounded-lg border border-slate-200 px-4 py-3 text-sm text-graphite hover:text-ink" @click="router.back()">
                Cancel
              </button>
            </div>

          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft, Check, Zap } from "@lucide/vue";
import { specialOrdersApi } from "@/api/specialOrders";
import { useAuthStore } from "@/stores/auth";
import type { PredefinedConfig, PredefinedConfigDuration, FixedPricePreview } from "@/types/specialOrders";

const router = useRouter();
const auth = useAuthStore();

const configs = ref<PredefinedConfig[]>([]);
const loadingConfigs = ref(true);
const selectedConfig = ref<PredefinedConfig | null>(null);
const selectedDuration = ref<PredefinedConfigDuration | null>(null);
const pricePreview = ref<FixedPricePreview | null>(null);
const loadingPreview = ref(false);
const couponCode = ref("");
const isSaving = ref(false);
const error = ref<string | null>(null);

const form = ref({
  title: "",
  inquiry_details: "",
  platform: "",
  writer_level: "",
});

const activeDurations = computed(() =>
  (selectedConfig.value?.durations ?? []).filter((d) => d.is_active).sort((a, b) => a.duration_days - b.duration_days),
);

function cheapestDuration(cfg: PredefinedConfig): string {
  const active = cfg.durations.filter((d) => d.is_active);
  if (!active.length) return "—";
  return active.reduce((min, d) => (Number(d.price) < Number(min.price) ? d : min)).price;
}

function selectConfig(cfg: PredefinedConfig) {
  selectedConfig.value = cfg;
  selectedDuration.value = null;
  pricePreview.value = null;
}

function selectDuration(dur: PredefinedConfigDuration) {
  selectedDuration.value = dur;
  fetchPreview();
}

async function fetchPreview() {
  if (!selectedConfig.value || !selectedDuration.value) return;
  loadingPreview.value = true;
  pricePreview.value = null;
  try {
    if (auth.isPreviewSession) return;
    const res = await specialOrdersApi.previewFixedPrice({
      predefined_config_id: selectedConfig.value.id,
      predefined_duration_id: selectedDuration.value.id,
      coupon_code: couponCode.value || undefined,
    });
    pricePreview.value = res.data;
  } catch {
    // Preview is non-critical — fall back to base price
  } finally {
    loadingPreview.value = false;
  }
}

async function submit() {
  if (!selectedConfig.value || !selectedDuration.value) return;
  isSaving.value = true;
  error.value = null;
  try {
    if (auth.isPreviewSession) {
      router.push("/client/special-orders");
      return;
    }
    const res = await specialOrdersApi.createFixed({
      predefined_config_id: selectedConfig.value.id,
      predefined_duration_id: selectedDuration.value.id,
      title: form.value.title || undefined,
      inquiry_details: form.value.inquiry_details || undefined,
      platform: form.value.platform || undefined,
      writer_level: form.value.writer_level || undefined,
      coupon_code: couponCode.value || undefined,
    });
    router.push(`/client/special-orders/${res.data.id}`);
  } catch {
    error.value = "Failed to place order. Please try again.";
  } finally {
    isSaving.value = false;
  }
}

onMounted(async () => {
  if (auth.isPreviewSession) {
    configs.value = [
      {
        id: 1, name: "Shadow Health Assignment", slug: "shadow-health",
        description: "Complete Shadow Health clinical simulation assignments with accurate assessments and documentation.",
        is_active: true, requires_full_payment: true, allow_wallet_payment: true, allow_external_payment: true, allow_discounts: true,
        durations: [
          { id: 1, duration_days: 1, price: "45.00", is_active: true },
          { id: 2, duration_days: 3, price: "35.00", is_active: true },
          { id: 3, duration_days: 7, price: "28.00", is_active: true },
        ],
      },
      {
        id: 2, name: "SPSS Data Analysis", slug: "spss-analysis",
        description: "Full SPSS statistical analysis including data entry, running tests, and interpretation.",
        is_active: true, requires_full_payment: true, allow_wallet_payment: true, allow_external_payment: true, allow_discounts: true,
        durations: [
          { id: 4, duration_days: 2, price: "65.00", is_active: true },
          { id: 5, duration_days: 5, price: "50.00", is_active: true },
        ],
      },
      {
        id: 3, name: "Nursing Care Plan", slug: "nursing-care-plan",
        description: "Evidence-based nursing care plan with comprehensive assessment, diagnoses, interventions and evaluations.",
        is_active: true, requires_full_payment: true, allow_wallet_payment: true, allow_external_payment: true, allow_discounts: true,
        durations: [
          { id: 6, duration_days: 1, price: "35.00", is_active: true },
          { id: 7, duration_days: 3, price: "28.00", is_active: true },
        ],
      },
      {
        id: 4, name: "Poster / Presentation Design", slug: "poster-design",
        description: "Professional academic poster or presentation slide deck with your content and visuals.",
        is_active: true, requires_full_payment: true, allow_wallet_payment: true, allow_external_payment: true, allow_discounts: true,
        durations: [
          { id: 8, duration_days: 2, price: "55.00", is_active: true },
          { id: 9, duration_days: 5, price: "40.00", is_active: true },
        ],
      },
    ];
    loadingConfigs.value = false;
    return;
  }
  try {
    const res = await specialOrdersApi.listPredefinedConfigs();
    configs.value = res.data;
  } catch {
    configs.value = [];
  } finally {
    loadingConfigs.value = false;
  }
});
</script>
