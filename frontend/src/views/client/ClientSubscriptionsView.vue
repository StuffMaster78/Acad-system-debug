<template>
  <div class="space-y-6 px-4 py-6">

    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-ink">Email & Notifications</h1>
        <p class="mt-0.5 text-sm text-graphite">Choose what you hear about and how.</p>
      </div>
      <button
        class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
        :disabled="loading"
        @click="refresh"
      >
        <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': loading }" /> Refresh
      </button>
    </div>

    <div v-if="error" class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ error }}
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 6" :key="n" class="h-14 animate-pulse rounded-xl bg-slate-100" />
    </div>

    <template v-else>
      <!-- ── Global preferences ──────────────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div class="border-b border-slate-100 px-5 py-4">
          <h2 class="text-sm font-semibold text-ink">Global preferences</h2>
          <p class="mt-0.5 text-xs text-graphite">Master controls — turning off here overrides individual subscriptions.</p>
        </div>
        <div class="divide-y divide-slate-100">
          <ToggleRow
            label="All communications"
            description="Master switch — disabling this silences everything."
            :value="prefs.all_subscriptions_enabled"
            @change="savePreference('all_subscriptions_enabled', $event)"
          />
          <ToggleRow
            label="Marketing consent"
            description="Required before we can send promotions, coupons, or marketing messages."
            :value="prefs.marketing_consent"
            @change="savePreference('marketing_consent', $event)"
          />
        </div>
      </section>

      <!-- ── Delivery channels ───────────────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div class="border-b border-slate-100 px-5 py-4">
          <h2 class="text-sm font-semibold text-ink">Delivery channels</h2>
        </div>
        <div class="divide-y divide-slate-100">
          <ToggleRow label="Email" :value="prefs.email_enabled"   @change="savePreference('email_enabled', $event)" />
          <ToggleRow label="SMS"   :value="prefs.sms_enabled"     @change="savePreference('sms_enabled', $event)" />
          <ToggleRow label="Push notifications" :value="prefs.push_enabled" @change="savePreference('push_enabled', $event)" />
          <ToggleRow label="In-app notifications" :value="prefs.in_app_enabled" @change="savePreference('in_app_enabled', $event)" />
        </div>
      </section>

      <!-- ── Do Not Disturb ─────────────────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div class="border-b border-slate-100 px-5 py-4">
          <h2 class="text-sm font-semibold text-ink">Do Not Disturb</h2>
          <p class="mt-0.5 text-xs text-graphite">Security alerts and order updates always bypass DND.</p>
        </div>
        <div class="divide-y divide-slate-100">
          <ToggleRow label="Enable Do Not Disturb" :value="prefs.dnd_enabled" @change="savePreference('dnd_enabled', $event)" />
          <div v-if="prefs.dnd_enabled" class="flex items-center gap-4 px-5 py-3 text-sm">
            <label class="w-24 text-xs font-medium text-graphite">Start hour</label>
            <input type="number" min="0" max="23" v-model.number="prefs.dnd_start_hour"
              class="focus-ring w-20 rounded-md border border-slate-200 px-3 py-1.5 text-sm"
              @change="savePreference('dnd_start_hour', prefs.dnd_start_hour)" />
            <label class="w-24 text-xs font-medium text-graphite">End hour</label>
            <input type="number" min="0" max="23" v-model.number="prefs.dnd_end_hour"
              class="focus-ring w-20 rounded-md border border-slate-200 px-3 py-1.5 text-sm"
              @change="savePreference('dnd_end_hour', prefs.dnd_end_hour)" />
            <span class="text-xs text-graphite">24-hour format</span>
          </div>
        </div>
      </section>

      <!-- ── Individual subscriptions ───────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div class="border-b border-slate-100 px-5 py-4">
          <h2 class="text-sm font-semibold text-ink">Subscription topics</h2>
          <p class="mt-0.5 text-xs text-graphite">Transactional messages (receipts, order updates, security) cannot be disabled.</p>
        </div>
        <div class="divide-y divide-slate-100">
          <div v-for="sub in subscriptions" :key="sub.subscription_type"
            class="flex items-center justify-between px-5 py-3">
            <div>
              <p class="text-sm font-medium text-ink">{{ label(sub.subscription_type) }}</p>
              <p v-if="sub.is_subscribed && sub.subscribed_at" class="text-xs text-graphite">
                Since {{ fmtDate(sub.subscribed_at) }}
              </p>
            </div>
            <div class="flex items-center gap-3">
              <select v-if="sub.is_subscribed && !isTransactional(sub.subscription_type)"
                :value="sub.frequency"
                class="focus-ring h-7 rounded border border-slate-200 bg-white px-2 text-xs"
                @change="changeFrequency(sub.subscription_type, ($event.target as HTMLSelectElement).value as any)"
              >
                <option value="immediate">Immediate</option>
                <option value="daily">Daily digest</option>
                <option value="weekly">Weekly digest</option>
                <option value="monthly">Monthly digest</option>
              </select>
              <button
                v-if="!isTransactional(sub.subscription_type)"
                class="focus-ring inline-flex h-7 min-w-[80px] items-center justify-center rounded-full text-xs font-semibold transition-colors"
                :class="sub.is_subscribed
                  ? 'bg-emerald-100 text-emerald-700 hover:bg-red-100 hover:text-red-700'
                  : 'bg-slate-100 text-slate-600 hover:bg-emerald-100 hover:text-emerald-700'"
                :disabled="toggling === sub.subscription_type"
                @click="toggle(sub)"
              >
                <span v-if="toggling === sub.subscription_type">…</span>
                <span v-else>{{ sub.is_subscribed ? 'Subscribed' : 'Subscribe' }}</span>
              </button>
              <span v-else class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-500">Always on</span>
            </div>
          </div>
        </div>
      </section>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { RefreshCw } from "@lucide/vue";
import {
  subscriptionsApi,
  type SubscriptionItem,
  type SubscriptionPreferences,
  type SubscriptionType,
  type Frequency,
} from "@/api/subscriptions";

// ── Inline toggle row component ───────────────────────────────────────────
const ToggleRow = {
  props: { label: String, description: String, value: Boolean },
  emits: ["change"],
  template: `
    <div class="flex items-center justify-between px-5 py-3">
      <div>
        <p class="text-sm font-medium text-ink">{{ label }}</p>
        <p v-if="description" class="text-xs text-graphite">{{ description }}</p>
      </div>
      <button
        role="switch" :aria-checked="value"
        class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-1"
        :class="value ? 'bg-brand-500' : 'bg-slate-200'"
        @click="$emit('change', !value)"
      >
        <span class="inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform"
          :class="value ? 'translate-x-4' : 'translate-x-0.5'" />
      </button>
    </div>
  `,
};

// ── State ─────────────────────────────────────────────────────────────────
const subscriptions = ref<SubscriptionItem[]>([]);
const prefs = ref<SubscriptionPreferences>({
  all_subscriptions_enabled: true,
  marketing_consent: false,
  marketing_consent_date: null,
  email_enabled: true,
  sms_enabled: false,
  push_enabled: false,
  in_app_enabled: true,
  dnd_enabled: false,
  dnd_start_hour: 22,
  dnd_end_hour: 6,
  transactional_enabled: true,
});
const loading = ref(false);
const error = ref("");
const toggling = ref<SubscriptionType | null>(null);

// ── Data loading ──────────────────────────────────────────────────────────
async function refresh() {
  loading.value = true;
  error.value = "";
  try {
    const [subRes, prefRes] = await Promise.all([
      subscriptionsApi.listAll(),
      subscriptionsApi.preferences(),
    ]);
    subscriptions.value = subRes.data;
    prefs.value = prefRes.data;
  } catch {
    error.value = "Failed to load subscription settings.";
  } finally {
    loading.value = false;
  }
}

// ── Actions ───────────────────────────────────────────────────────────────
async function savePreference(key: keyof SubscriptionPreferences, value: unknown) {
  try {
    const res = await subscriptionsApi.updatePreferences({ [key]: value });
    prefs.value = res.data;
  } catch {
    error.value = "Failed to update preference.";
  }
}

async function toggle(sub: SubscriptionItem) {
  toggling.value = sub.subscription_type;
  try {
    if (sub.is_subscribed) {
      await subscriptionsApi.unsubscribe(sub.subscription_type);
    } else {
      await subscriptionsApi.subscribe({ subscription_type: sub.subscription_type });
    }
    await refresh();
  } catch {
    error.value = "Failed to update subscription.";
  } finally {
    toggling.value = null;
  }
}

async function changeFrequency(type: SubscriptionType, frequency: Frequency) {
  try {
    await subscriptionsApi.updateFrequency(type, frequency);
    const match = subscriptions.value.find((s) => s.subscription_type === type);
    if (match) match.frequency = frequency;
  } catch {
    error.value = "Failed to update frequency.";
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────
const LABELS: Record<SubscriptionType, string> = {
  newsletter: "Newsletter",
  blog_posts: "Blog post updates",
  coupon_updates: "Coupon & discount alerts",
  marketing_messages: "Marketing messages",
  unread_messages: "Unread message reminders",
  transactional_messages: "Transactional messages",
  notifications: "Notifications",
  order_updates: "Order status updates",
  promotional_offers: "Promotional offers",
  product_updates: "Product updates",
  security_alerts: "Security alerts",
  account_updates: "Account updates",
};

const TRANSACTIONAL: SubscriptionType[] = [
  "transactional_messages",
  "order_updates",
  "security_alerts",
  "account_updates",
];

function label(type: SubscriptionType) { return LABELS[type] ?? type; }
function isTransactional(type: SubscriptionType) { return TRANSACTIONAL.includes(type); }
function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

onMounted(refresh);
</script>
