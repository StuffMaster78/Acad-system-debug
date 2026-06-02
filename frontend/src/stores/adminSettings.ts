import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminSettingsApi,
  type AdminActivityLogRecord,
  type ConfigItem,
  type ScreenedWordStats,
  type ScreenedWordRecord,
  type SpecialDayRecord,
  type SystemHealthResponse,
} from "@/api/adminSettings";
import { useUiStore } from "@/stores/ui";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
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
  const screenedWords = ref<ScreenedWordRecord[]>([]);
  const activityLogs = ref<AdminActivityLogRecord[]>([]);
  const specialDays = ref<SpecialDayRecord[]>([]);
  const systemHealth = ref<SystemHealthResponse>({});
  const systemAlerts = ref<Array<Record<string, unknown> | string>>([]);
  const recommendations = ref<string[]>([]);
  const selectedGroupKey = ref<AdminConfigGroup["key"]>("pricing");
  const query = ref("");
  const screenedWordDraft = ref("spamword, payment outside platform, external contact");
  const defaultPopulationForm = ref({
    website_id: null as number | null,
    default_set: "",
  });
  const specialDayForm = ref({
    name: "Black Friday",
    date: new Date().toISOString().slice(0, 10),
    event_type: "seasonal",
    priority: "high",
    is_annual: true,
    is_international: true,
  });
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

  const selectedGroup = computed(() =>
    groups.value.find((group) => group.key === selectedGroupKey.value) ?? groups.value[0],
  );

  const filteredSelectedItems = computed(() => {
    const needle = query.value.trim().toLowerCase();
    if (!needle) return selectedGroup.value.items;
    return selectedGroup.value.items.filter((item) =>
      [item.name, item.title, item.code, item.website, item.description]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(needle)),
    );
  });

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
      detail: `${systemAlerts.value.length} system alerts currently visible.`,
      tone: systemAlerts.value.length ? "risk" : "neutral",
    },
  ]);

  async function hydrate() {
    const auth = useAuthStore();
    const portal = usePortalContextStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (defaultPopulationForm.value.website_id == null && portal.website?.id) {
        defaultPopulationForm.value.website_id = portal.website.id;
      }

      if (auth.isPreviewSession) {
        pricingConfigs.value = [previewConfig("Academic writing USD"), previewConfig("Urgent deadline matrix")];
        writerConfigs.value = [previewConfig("Default writer eligibility"), previewConfig("Probation thresholds")];
        discountConfigs.value = [previewConfig("Returning client coupon"), previewConfig("First order offer", false)];
        notificationProfiles.value = [previewConfig("Default client notifications"), previewConfig("Writer critical alerts")];
        screenedWords.value = [
          { id: 1, word: "external contact", is_active: true },
          { id: 2, word: "payment outside platform", is_active: true },
        ];
        activityLogs.value = [
          {
            id: 1,
            admin: "admin preview",
            admin_username: "admin.preview",
            action: "Updated pricing configuration",
            timestamp: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
          },
          {
            id: 2,
            admin: "admin preview",
            admin_username: "admin.preview",
            action: "Bulk added screened words",
            timestamp: new Date(Date.now() - 1000 * 60 * 55).toISOString(),
          },
        ];
        specialDays.value = [
          {
            id: 1,
            name: "Black Friday",
            event_type: "seasonal",
            date: "2026-11-27",
            priority: "high",
            is_active: true,
            days_until: 186,
          },
        ];
        systemHealth.value = {
          status: "healthy",
          database: { status: "healthy" },
          performance_metrics: { avg_response_time_ms: 180 },
          financial_health: { status: "stable" },
        };
        systemAlerts.value = [];
        recommendations.value = ["Keep config defaults aligned before launching new tenant websites."];
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
        screenedWordsRes,
        healthRes,
        alertsRes,
        activityRes,
        specialDaysRes,
      ] = await Promise.allSettled([
        adminSettingsApi.configSummary(),
        adminSettingsApi.screenedWordStats(),
        adminSettingsApi.orderConfigUsage(),
        adminSettingsApi.defaultSets(),
        adminSettingsApi.screenedWords(),
        adminSettingsApi.systemHealth(),
        adminSettingsApi.systemAlerts(),
        adminSettingsApi.activityLogs({ page_size: 10 }),
        adminSettingsApi.specialDays({ page_size: 20 }),
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
      if (screenedWordsRes.status === "fulfilled") screenedWords.value = normalizeList(screenedWordsRes.value.data);
      if (healthRes.status === "fulfilled") systemHealth.value = healthRes.value.data;
      if (alertsRes.status === "fulfilled") {
        systemAlerts.value = alertsRes.value.data.alerts ?? [];
        recommendations.value = alertsRes.value.data.recommendations ?? [];
      }
      if (activityRes.status === "fulfilled") activityLogs.value = normalizeList(activityRes.value.data);
      if (specialDaysRes.status === "fulfilled") specialDays.value = normalizeList(specialDaysRes.value.data);
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

  async function populateDefaults() {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        notice.value = "Preview default set populated.";
        ui.toast(notice.value, "success");
        return;
      }
      if (!defaultPopulationForm.value.website_id) {
        error.value = "Choose a website before populating defaults.";
        ui.toast(error.value, "error");
        return;
      }
      await adminSettingsApi.populateDefaults(
        defaultPopulationForm.value.website_id,
        defaultPopulationForm.value.default_set || undefined,
      );
      notice.value = "Default configuration set populated.";
      ui.toast(notice.value, "success");
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function bulkCreateScreenedWords() {
    const auth = useAuthStore();
    const ui = useUiStore();
    const words = screenedWordDraft.value
      .split(/[,\n]/)
      .map((word) => word.trim())
      .filter(Boolean);
    if (!words.length) return;

    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        const created = words.map((word, index) => ({
          id: Date.now() + index,
          word: word.toLowerCase(),
          is_active: true,
          created_at: new Date().toISOString(),
        }));
        screenedWords.value = [...created, ...screenedWords.value];
        screenedWordStats.value.total_screened_words += created.length;
        notice.value = `Preview added ${created.length} screened words.`;
        ui.toast(notice.value, "success");
        return;
      }
      const { data } = await adminSettingsApi.bulkCreateScreenedWords(words);
      notice.value = `Added ${data.created_count ?? 0} screened words.`;
      if (data.errors?.length) {
        error.value = data.errors.join(" ");
        ui.toast(error.value, "warn");
      } else {
        ui.toast(notice.value, "success");
      }
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function createSpecialDay() {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        specialDays.value = [
          {
            id: Date.now(),
            ...specialDayForm.value,
            is_active: true,
            days_until: 30,
          },
          ...specialDays.value,
        ];
        notice.value = "Preview special day created.";
        ui.toast(notice.value, "success");
        return;
      }
      const { data } = await adminSettingsApi.createSpecialDay(specialDayForm.value);
      specialDays.value = [data, ...specialDays.value];
      notice.value = "Special day created.";
      ui.toast(notice.value, "success");
    } finally {
      isMutating.value = false;
    }
  }

  return {
    pricingConfigs,
    writerConfigs,
    discountConfigs,
    notificationProfiles,
    screenedWords,
    activityLogs,
    specialDays,
    systemHealth,
    systemAlerts,
    recommendations,
    screenedWordStats,
    defaultSets,
    orderConfigUsage,
    selectedGroupKey,
    selectedGroup,
    filteredSelectedItems,
    query,
    screenedWordDraft,
    defaultPopulationForm,
    specialDayForm,
    groups,
    metrics,
    isLoading,
    isMutating,
    error,
    notice,
    hydrate,
    checkDefaults,
    populateDefaults,
    bulkCreateScreenedWords,
    createSpecialDay,
  };
});
