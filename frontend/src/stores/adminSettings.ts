import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminSettingsApi,
  type ConfigItem,
  type ScreenedWordStats,
} from "@/api/adminSettings";
import { useAuthStore } from "@/stores/auth";
import type {
  AdminConfigGroup,
  AdminSettingsMetric,
} from "@/types/adminSettings";

type ListResponse<T> = T[] | { results: T[] };

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function previewConfig(name: string, active = true): ConfigItem {
  return {
    id: Math.floor(Math.random() * 10000),
    name,
    is_active: active,
    website: "WritePro Global",
    updated_at: new Date().toISOString(),
  };
}

export const useAdminSettingsStore = defineStore("admin-settings", () => {
  const pricingConfigs = ref<ConfigItem[]>([]);
  const writerConfigs = ref<ConfigItem[]>([]);
  const discountConfigs = ref<ConfigItem[]>([]);
  const notificationProfiles = ref<ConfigItem[]>([]);
  const screenedWordStats = ref<ScreenedWordStats>({
    total_screened_words: 0,
    total_flagged_messages: 0,
    flagged_last_7_days: 0,
  });
  const defaultSets = ref<string[]>([]);
  const orderConfigUsage = ref({
    total_configs: 0,
    used_configs: 0,
    unused_configs: 0,
    usage_percentage: 0,
  });
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const groups = computed<AdminConfigGroup[]>(() => [
    {
      key: "pricing",
      label: "Pricing",
      description: "Base prices, pricing rules, writer-level modifiers, and quote behavior.",
      count: pricingConfigs.value.length,
      items: pricingConfigs.value,
    },
    {
      key: "writer",
      label: "Writer rules",
      description: "Eligibility, assignment, warning, and capacity settings.",
      count: writerConfigs.value.length,
      items: writerConfigs.value,
    },
    {
      key: "discount",
      label: "Discounts",
      description: "Coupon behavior, limits, windows, and campaign discounts.",
      count: discountConfigs.value.length,
      items: discountConfigs.value,
    },
    {
      key: "notifications",
      label: "Notifications",
      description: "Notification preference profiles and delivery defaults.",
      count: notificationProfiles.value.length,
      items: notificationProfiles.value,
    },
  ]);

  const metrics = computed<AdminSettingsMetric[]>(() => [
    {
      label: "Config groups",
      value: groups.value.length,
      detail: "Pricing, writer, discount, and notification profiles.",
      tone: "neutral",
    },
    {
      label: "Order configs",
      value: orderConfigUsage.value.total_configs,
      detail: `${orderConfigUsage.value.usage_percentage}% currently used by orders.`,
      tone: orderConfigUsage.value.unused_configs ? "warn" : "good",
    },
    {
      label: "Screened words",
      value: screenedWordStats.value.total_screened_words,
      detail: `${screenedWordStats.value.flagged_last_7_days} flags in the last 7 days.`,
      tone: screenedWordStats.value.flagged_last_7_days ? "risk" : "neutral",
    },
    {
      label: "Default sets",
      value: defaultSets.value.length,
      detail: "Available bootstrap sets for tenant/order configuration.",
      tone: "neutral",
    },
  ]);

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        pricingConfigs.value = [previewConfig("Academic writing USD"), previewConfig("Urgent deadline matrix")];
        writerConfigs.value = [previewConfig("Default writer eligibility"), previewConfig("Probation thresholds")];
        discountConfigs.value = [previewConfig("Returning client coupon"), previewConfig("First order offer", false)];
        notificationProfiles.value = [previewConfig("Default client notifications"), previewConfig("Writer critical alerts")];
        screenedWordStats.value = {
          total_screened_words: 42,
          total_flagged_messages: 8,
          flagged_last_7_days: 3,
        };
        orderConfigUsage.value = {
          total_configs: 188,
          used_configs: 143,
          unused_configs: 45,
          usage_percentage: 76,
        };
        defaultSets.value = ["academic_default", "technical_writing", "class_management"];
        return;
      }

      const [
        summaryRes,
        screenedRes,
        usageRes,
        defaultSetsRes,
      ] = await Promise.allSettled([
        adminSettingsApi.configSummary(),
        adminSettingsApi.screenedWordStats(),
        adminSettingsApi.orderConfigUsage(),
        adminSettingsApi.defaultSets(),
      ]);

      if (summaryRes.status === "fulfilled") {
        pricingConfigs.value = (summaryRes.value.data.pricing_configs ?? []) as ConfigItem[];
        writerConfigs.value = (summaryRes.value.data.writer_configs ?? []) as ConfigItem[];
        discountConfigs.value = (summaryRes.value.data.discount_configs ?? []) as ConfigItem[];
        notificationProfiles.value = (summaryRes.value.data.notification_profiles ?? []) as ConfigItem[];
      } else {
        const [pricingRes, writerRes, discountRes, notificationRes] = await Promise.allSettled([
          adminSettingsApi.pricingConfigs(),
          adminSettingsApi.writerConfigs(),
          adminSettingsApi.discountConfigs(),
          adminSettingsApi.notificationProfiles(),
        ]);
        if (pricingRes.status === "fulfilled") pricingConfigs.value = normalizeList(pricingRes.value.data);
        if (writerRes.status === "fulfilled") writerConfigs.value = normalizeList(writerRes.value.data);
        if (discountRes.status === "fulfilled") discountConfigs.value = normalizeList(discountRes.value.data);
        if (notificationRes.status === "fulfilled") notificationProfiles.value = normalizeList(notificationRes.value.data);
      }

      if (screenedRes.status === "fulfilled") screenedWordStats.value = screenedRes.value.data;
      if (usageRes.status === "fulfilled") {
        const summary = usageRes.value.data.summary ?? {};
        orderConfigUsage.value = {
          total_configs: summary.total_configs ?? 0,
          used_configs: summary.used_configs ?? 0,
          unused_configs: summary.unused_configs ?? 0,
          usage_percentage: summary.usage_percentage ?? 0,
        };
      }
      if (defaultSetsRes.status === "fulfilled") {
        const data = defaultSetsRes.value.data;
        defaultSets.value = data.default_sets ?? data.available_sets ?? data.sets ?? [];
      }
    } catch (caught) {
      error.value = "Unable to load admin configuration data.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function checkDefaults() {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        notice.value = "Preview defaults check complete.";
        return;
      }
      await adminSettingsApi.checkDefaults();
      notice.value = "Default configuration check complete.";
    } finally {
      isMutating.value = false;
    }
  }

  return {
    pricingConfigs,
    writerConfigs,
    discountConfigs,
    notificationProfiles,
    screenedWordStats,
    defaultSets,
    orderConfigUsage,
    groups,
    metrics,
    isLoading,
    isMutating,
    error,
    notice,
    hydrate,
    checkDefaults,
  };
});
