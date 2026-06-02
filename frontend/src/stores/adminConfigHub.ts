import { reactive, ref } from "vue";
import { defineStore } from "pinia";
import { orderConfigApi, type ConfigCollection, type ConfigOptionPayload } from "@/api/orderConfig";
import { adminSettingsApi, type ScreenedWordRecord, type SpecialDayRecord } from "@/api/adminSettings";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import type { OrderConfigOption } from "@/types/config";

export type HubTab =
  // existing
  | "order-options" | "websites" | "pricing" | "policies" | "content" | "calendar" | "system"
  // order management
  | "deadlines" | "writer-preferences" | "discount-codes" | "referral" | "unpaid-orders" | "marketing-email"
  // collection shortcuts (reuse order-options panel)
  | "col-academic-levels" | "col-types-of-work" | "col-paper-subjects" | "col-paper-types"
  // writer management
  | "writer-registration" | "grammar-test" | "time-management" | "fines" | "writer-policy" | "writer-hierarchy"
  // platform / other
  | "payment-gateway" | "payment-notifications" | "wallet-settings" | "withdrawal-window"
  | "client-policy" | "roles" | "filter-users" | "filter-whatsapp"
  | "api-keys" | "blog-categories" | "blog-persona" | "all-users";

export interface DiscountCode {
  id: number;
  code: string;
  discount_type: "percentage" | "fixed";
  value: number;
  max_uses: number | null;
  uses_count: number;
  expires_at: string | null;
  is_active: boolean;
}

export interface ApiKeyRecord {
  id: number;
  name: string;
  prefix: string;
  created_at: string;
  last_used_at: string | null;
  is_active: boolean;
}

export interface UserRecord {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  date_joined: string;
}

export interface RoleRecord {
  id: number;
  name: string;
  codename: string;
  user_count: number;
}

export interface BlogCategory {
  id: number;
  name: string;
  slug: string;
  post_count: number;
  is_active: boolean;
}

export interface CollectionMeta {
  key: ConfigCollection;
  label: string;
  description: string;
}

export const COLLECTIONS: CollectionMeta[] = [
  { key: "paper-types", label: "Paper types", description: "Essay, research paper, case study…" },
  { key: "academic-levels", label: "Academic levels", description: "High school, undergraduate, masters…" },
  { key: "subjects", label: "Subjects", description: "Business, nursing, literature…" },
  { key: "types-of-work", label: "Types of work", description: "Writing, editing, rewriting…" },
  { key: "formatting-styles", label: "Formatting styles", description: "APA, MLA, Chicago, Harvard…" },
  { key: "english-types", label: "English types", description: "US English, UK English…" },
];

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

export const useAdminConfigHubStore = defineStore("admin-config-hub", () => {
  const auth = useAuthStore();
  const ui = useUiStore();

  const activeTab = ref<HubTab>("order-options");
  const activeCollection = ref<ConfigCollection>("paper-types");

  // ── Order Options ─────────────────────────────────────────────────────────────
  const collectionItems = ref<Record<ConfigCollection, OrderConfigOption[]>>({
    "paper-types": [],
    "academic-levels": [],
    "subjects": [],
    "types-of-work": [],
    "formatting-styles": [],
    "english-types": [],
  });

  const isLoadingCollection = ref(false);
  const isSaving = ref(false);

  const showCreateForm = ref(false);
  const editingId = ref<number | null>(null);
  const categoryFilter = ref<string>("");

  const createForm = reactive<ConfigOptionPayload>({
    name: "",
    code: "",
    website: null,
    is_active: true,
  });

  const editForm = reactive<Partial<ConfigOptionPayload & { id: number }>>({});

  function resetCreate() {
    createForm.name = "";
    createForm.code = "";
    createForm.website = null;
    createForm.is_active = true;
    showCreateForm.value = false;
  }

  function startEdit(item: OrderConfigOption) {
    editingId.value = item.id;
    const raw = item as Record<string, unknown>;
    Object.assign(editForm, {
      id: item.id,
      name: item.name,
      code: item.code ?? "",
      description: raw.description ?? "",
      website: item.website ?? null,
      is_active: item.is_active ?? true,
      display_order: raw.display_order ?? 0,
      category: raw.category ?? "general",
      is_technical: raw.is_technical ?? false,
    });
  }

  function cancelEdit() {
    editingId.value = null;
  }

  function previewItem(name: string): OrderConfigOption {
    return { id: Date.now(), name, code: name.toLowerCase().replace(/\s+/g, "_"), is_active: true };
  }

  async function loadCollection(collection: ConfigCollection) {
    activeCollection.value = collection;
    if (collectionItems.value[collection].length) return;
    isLoadingCollection.value = true;
    try {
      if (auth.isPreviewSession) {
        const samples: Record<ConfigCollection, string[]> = {
          "paper-types": ["Essay", "Research Paper", "Case Study", "Thesis", "Lab Report"],
          "academic-levels": ["High School", "Undergraduate", "Masters", "PhD", "Professional"],
          "subjects": ["Business", "Nursing", "Literature", "History", "Psychology"],
          "types-of-work": ["Writing", "Editing", "Rewriting", "Proofreading"],
          "formatting-styles": ["APA 7", "MLA 9", "Chicago", "Harvard", "Turabian"],
          "english-types": ["US English", "UK English", "Australian English"],
        };
        collectionItems.value[collection] = samples[collection].map((n, i) => ({
          ...previewItem(n),
          id: i + 1,
          is_active: i !== 3,
        }));
        return;
      }
      const params: Record<string, unknown> = {};
      if (collection === "subjects" && categoryFilter.value) {
        params.category = categoryFilter.value;
      }
      const { data } = await orderConfigApi.listCollection(collection, Object.keys(params).length ? params : undefined);
      collectionItems.value[collection] = normalizeList(data as OrderConfigOption[] | { results: OrderConfigOption[] });
    } catch {
      ui.toast("Failed to load config items.", "error");
    } finally {
      isLoadingCollection.value = false;
    }
  }

  async function createOption() {
    if (!createForm.name.trim()) return;
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        collectionItems.value[activeCollection.value].push(previewItem(createForm.name));
        ui.toast(`${createForm.name} added (preview).`, "success");
        resetCreate();
        return;
      }
      const { data } = await orderConfigApi.createOption(activeCollection.value, { ...createForm });
      collectionItems.value[activeCollection.value].unshift(data);
      ui.toast(`${data.name} created.`, "success");
      resetCreate();
    } catch {
      ui.toast("Failed to create option.", "error");
    } finally {
      isSaving.value = false;
    }
  }

  async function saveEdit() {
    if (!editingId.value) return;
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        const col = collectionItems.value[activeCollection.value];
        const idx = col.findIndex((i) => i.id === editingId.value);
        if (idx !== -1) col[idx] = { ...col[idx], ...(editForm as Partial<OrderConfigOption>) };
        ui.toast("Updated (preview).", "success");
        cancelEdit();
        return;
      }
      const { data } = await orderConfigApi.updateOption(activeCollection.value, editingId.value, editForm);
      const col = collectionItems.value[activeCollection.value];
      const idx = col.findIndex((i) => i.id === editingId.value);
      if (idx !== -1) col[idx] = data;
      ui.toast(`${data.name} updated.`, "success");
      cancelEdit();
    } catch {
      ui.toast("Failed to save changes.", "error");
    } finally {
      isSaving.value = false;
    }
  }

  async function toggleActive(item: OrderConfigOption) {
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        item.is_active = !item.is_active;
        ui.toast(`${item.name} ${item.is_active ? "activated" : "deactivated"} (preview).`, "success");
        return;
      }
      const { data } = await orderConfigApi.updateOption(activeCollection.value, item.id, { is_active: !item.is_active });
      const col = collectionItems.value[activeCollection.value];
      const idx = col.findIndex((i) => i.id === item.id);
      if (idx !== -1) col[idx] = data;
      ui.toast(`${data.name} ${data.is_active ? "activated" : "deactivated"}.`, "success");
    } catch {
      ui.toast("Failed to update status.", "error");
    } finally {
      isSaving.value = false;
    }
  }

  async function deleteOption(item: OrderConfigOption) {
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        collectionItems.value[activeCollection.value] = collectionItems.value[activeCollection.value].filter((i) => i.id !== item.id);
        ui.toast(`${item.name} deleted (preview).`, "success");
        return;
      }
      await orderConfigApi.deleteOption(activeCollection.value, item.id);
      collectionItems.value[activeCollection.value] = collectionItems.value[activeCollection.value].filter((i) => i.id !== item.id);
      ui.toast(`${item.name} deleted.`, "success");
    } catch {
      ui.toast("Failed to delete option.", "error");
    } finally {
      isSaving.value = false;
    }
  }

  // ── Content — screened words ───────────────────────────────────────────────
  const screenedWords = ref<ScreenedWordRecord[]>([]);
  const screenedWordDraft = ref("");
  const isLoadingContent = ref(false);

  async function loadScreenedWords() {
    isLoadingContent.value = true;
    try {
      if (auth.isPreviewSession) {
        screenedWords.value = [{ word: "external payment" }, { word: "whatsapp" }, { word: "contact me directly" }];
        return;
      }
      const { data } = await adminSettingsApi.screenedWords();
      screenedWords.value = normalizeList(data);
    } catch {
      // non-fatal
    } finally {
      isLoadingContent.value = false;
    }
  }

  async function bulkCreateScreenedWords() {
    const words = screenedWordDraft.value.split(/[\n,]+/).map((w) => w.trim()).filter(Boolean);
    if (!words.length) return;
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        screenedWords.value = [...screenedWords.value, ...words.map((w) => ({ word: w }))];
        screenedWordDraft.value = "";
        ui.toast(`${words.length} word(s) added (preview).`, "success");
        return;
      }
      await adminSettingsApi.bulkCreateScreenedWords(words);
      screenedWordDraft.value = "";
      await loadScreenedWords();
      ui.toast(`${words.length} word(s) added.`, "success");
    } catch {
      ui.toast("Failed to add screened words.", "error");
    } finally {
      isSaving.value = false;
    }
  }

  // ── Calendar — special days ────────────────────────────────────────────────
  const specialDays = ref<SpecialDayRecord[]>([]);
  const isLoadingCalendar = ref(false);
  const specialDayForm = reactive({
    name: "",
    date: new Date().toISOString().slice(0, 10),
    event_type: "seasonal",
    priority: "medium",
    is_annual: false,
    is_international: false,
  });

  async function loadSpecialDays() {
    isLoadingCalendar.value = true;
    try {
      if (auth.isPreviewSession) {
        specialDays.value = [
          { id: 1, name: "Black Friday", date: "2026-11-27", event_type: "seasonal", priority: "high", is_annual: true, is_international: true },
          { id: 2, name: "New Year", date: "2026-01-01", event_type: "holiday", priority: "high", is_annual: true, is_international: true },
        ];
        return;
      }
      const { data } = await adminSettingsApi.specialDays({ ordering: "date" });
      specialDays.value = normalizeList(data);
    } catch {
      // non-fatal
    } finally {
      isLoadingCalendar.value = false;
    }
  }

  async function createSpecialDay() {
    if (!specialDayForm.name || !specialDayForm.date) return;
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        specialDays.value.push({ ...specialDayForm, id: Date.now() });
        ui.toast(`${specialDayForm.name} added (preview).`, "success");
        return;
      }
      const { data } = await adminSettingsApi.createSpecialDay({ ...specialDayForm });
      specialDays.value.push(data);
      ui.toast(`${data.name} created.`, "success");
    } catch {
      ui.toast("Failed to create special day.", "error");
    } finally {
      isSaving.value = false;
    }
  }

  // ── System health ─────────────────────────────────────────────────────────
  const systemHealth = ref<Record<string, unknown>>({});
  const systemAlerts = ref<Array<string | Record<string, unknown>>>([]);
  const activityLogs = ref<Array<Record<string, unknown>>>([]);
  const isLoadingSystem = ref(false);

  async function loadSystem() {
    isLoadingSystem.value = true;
    try {
      if (auth.isPreviewSession) {
        systemHealth.value = { status: "healthy", timestamp: new Date().toISOString() };
        systemAlerts.value = [];
        activityLogs.value = [
          { id: 1, action: "Populated defaults for site 1", admin_username: "admin@site.com", timestamp: new Date(Date.now() - 3600000).toISOString() },
          { id: 2, action: "Added screened word: external payment", admin_username: "admin@site.com", timestamp: new Date(Date.now() - 7200000).toISOString() },
        ];
        return;
      }
      const [health, alerts, logs] = await Promise.allSettled([
        adminSettingsApi.systemHealth(),
        adminSettingsApi.systemAlerts(),
        adminSettingsApi.activityLogs({ page_size: 20 }),
      ]);
      if (health.status === "fulfilled") systemHealth.value = health.value.data;
      if (alerts.status === "fulfilled") systemAlerts.value = alerts.value.data.alerts ?? [];
      if (logs.status === "fulfilled") activityLogs.value = normalizeList(logs.value.data as unknown as Record<string, unknown>[] | { results: Record<string, unknown>[] });
    } catch {
      // non-fatal
    } finally {
      isLoadingSystem.value = false;
    }
  }

  // ── Policies ──────────────────────────────────────────────────────────────
  const policies = reactive({
    revision_window_days: 7,
    max_revisions_per_order: 3,
    client_daily_order_cap: 5,
    writer_max_active_orders: 10,
    dispute_auto_escalation_hours: 72,
    min_writer_quality_score: "7.0",
    file_size_limit_mb: 50,
  });
  const isSavingPolicies = ref(false);

  async function savePolicies() {
    isSavingPolicies.value = true;
    try {
      // Placeholder: POST to platform settings endpoint when backend exposes it
      await new Promise((r) => setTimeout(r, 600));
      ui.toast("Policies saved (preview — backend endpoint pending).", "success");
    } finally {
      isSavingPolicies.value = false;
    }
  }

  // ── Discount codes ────────────────────────────────────────────────────────
  const discountCodes = ref<DiscountCode[]>([]);
  const isLoadingDiscounts = ref(false);

  async function loadDiscountCodes() {
    isLoadingDiscounts.value = true;
    try {
      if (auth.isPreviewSession) {
        discountCodes.value = [
          { id: 1, code: "WELCOME20", discount_type: "percentage", value: 20, max_uses: 100, uses_count: 34, expires_at: "2026-12-31", is_active: true },
          { id: 2, code: "FLAT10", discount_type: "fixed", value: 10, max_uses: null, uses_count: 7, expires_at: null, is_active: true },
          { id: 3, code: "SUMMER15", discount_type: "percentage", value: 15, max_uses: 50, uses_count: 50, expires_at: "2026-08-31", is_active: false },
        ];
        return;
      }
      // const { data } = await adminSettingsApi.discountCodes();
      // discountCodes.value = normalizeList(data);
    } catch { /* non-fatal */ } finally {
      isLoadingDiscounts.value = false;
    }
  }

  // ── API Keys ──────────────────────────────────────────────────────────────
  const apiKeys = ref<ApiKeyRecord[]>([]);
  const isLoadingApiKeys = ref(false);

  async function loadApiKeys() {
    isLoadingApiKeys.value = true;
    try {
      if (auth.isPreviewSession) {
        apiKeys.value = [
          { id: 1, name: "Production webhook", prefix: "pk_live_abc1", created_at: new Date(Date.now() - 86400000 * 30).toISOString(), last_used_at: new Date(Date.now() - 3600000).toISOString(), is_active: true },
          { id: 2, name: "Staging integration", prefix: "pk_test_xyz9", created_at: new Date(Date.now() - 86400000 * 7).toISOString(), last_used_at: null, is_active: true },
        ];
        return;
      }
      // const { data } = await adminSettingsApi.apiKeys();
      // apiKeys.value = normalizeList(data);
    } catch { /* non-fatal */ } finally {
      isLoadingApiKeys.value = false;
    }
  }

  // ── All users ─────────────────────────────────────────────────────────────
  const allUsers = ref<UserRecord[]>([]);
  const isLoadingUsers = ref(false);
  const userSearch = ref("");

  async function loadAllUsers() {
    isLoadingUsers.value = true;
    try {
      if (auth.isPreviewSession) {
        allUsers.value = [
          { id: 1, username: "alice_w", email: "alice@example.com", role: "writer", is_active: true, date_joined: "2025-01-10" },
          { id: 2, username: "bob_client", email: "bob@example.com", role: "client", is_active: true, date_joined: "2025-03-05" },
          { id: 3, username: "carol_ed", email: "carol@example.com", role: "editor", is_active: true, date_joined: "2025-02-20" },
          { id: 4, username: "dan_sup", email: "dan@example.com", role: "support", is_active: false, date_joined: "2024-11-01" },
          { id: 5, username: "eva_admin", email: "eva@example.com", role: "admin", is_active: true, date_joined: "2024-08-15" },
        ];
        return;
      }
      // const { data } = await adminSettingsApi.allUsers({ search: userSearch.value });
      // allUsers.value = normalizeList(data);
    } catch { /* non-fatal */ } finally {
      isLoadingUsers.value = false;
    }
  }

  // ── Roles ─────────────────────────────────────────────────────────────────
  const roles = ref<RoleRecord[]>([]);
  const isLoadingRoles = ref(false);

  async function loadRoles() {
    isLoadingRoles.value = true;
    try {
      if (auth.isPreviewSession) {
        roles.value = [
          { id: 1, name: "Superadmin", codename: "superadmin", user_count: 1 },
          { id: 2, name: "Admin", codename: "admin", user_count: 3 },
          { id: 3, name: "Editor", codename: "editor", user_count: 8 },
          { id: 4, name: "Support", codename: "support", user_count: 12 },
          { id: 5, name: "Writer", codename: "writer", user_count: 204 },
          { id: 6, name: "Client", codename: "client", user_count: 1840 },
        ];
        return;
      }
    } catch { /* non-fatal */ } finally {
      isLoadingRoles.value = false;
    }
  }

  // ── Blog categories ───────────────────────────────────────────────────────
  const blogCategories = ref<BlogCategory[]>([]);
  const isLoadingBlog = ref(false);
  const newCategoryName = ref("");

  async function loadBlogCategories() {
    isLoadingBlog.value = true;
    try {
      if (auth.isPreviewSession) {
        blogCategories.value = [
          { id: 1, name: "Academic Writing", slug: "academic-writing", post_count: 14, is_active: true },
          { id: 2, name: "Study Tips", slug: "study-tips", post_count: 8, is_active: true },
          { id: 3, name: "Research Methods", slug: "research-methods", post_count: 5, is_active: false },
          { id: 4, name: "Career Advice", slug: "career-advice", post_count: 3, is_active: true },
        ];
        return;
      }
    } catch { /* non-fatal */ } finally {
      isLoadingBlog.value = false;
    }
  }

  async function createBlogCategory() {
    if (!newCategoryName.value.trim()) return;
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        blogCategories.value.push({ id: Date.now(), name: newCategoryName.value, slug: newCategoryName.value.toLowerCase().replace(/\s+/g, "-"), post_count: 0, is_active: true });
        ui.toast(`${newCategoryName.value} added (preview).`, "success");
        newCategoryName.value = "";
        return;
      }
    } catch { ui.toast("Failed to create category.", "error"); } finally {
      isSaving.value = false;
    }
  }

  // ── Generic section save (placeholder for settings sections) ──────────────
  const isSavingSection = ref(false);

  async function saveSection(label: string) {
    isSavingSection.value = true;
    try {
      await new Promise((r) => setTimeout(r, 500));
      ui.toast(`${label} saved (backend endpoint pending).`, "success");
    } finally {
      isSavingSection.value = false;
    }
  }

  // ── Websites (pricing configs as stand-in) ─────────────────────────────────
  const pricingConfigs = ref<Record<string, unknown>[]>([]);
  const isLoadingPricing = ref(false);

  async function loadPricing() {
    isLoadingPricing.value = true;
    try {
      if (auth.isPreviewSession) {
        pricingConfigs.value = [
          { id: 1, name: "Standard — WritePro", website: "WritePro", is_active: true, updated_at: new Date().toISOString() },
          { id: 2, name: "Premium — EssayMasters", website: "EssayMasters", is_active: true, updated_at: new Date().toISOString() },
        ];
        return;
      }
      const { data } = await adminSettingsApi.pricingConfigs();
      pricingConfigs.value = normalizeList(data) as Record<string, unknown>[];
    } catch {
      // non-fatal
    } finally {
      isLoadingPricing.value = false;
    }
  }

  return {
    activeTab,
    activeCollection,
    collectionItems,
    isLoadingCollection,
    isSaving,
    showCreateForm,
    editingId,
    categoryFilter,
    createForm,
    editForm,
    loadCollection,
    createOption,
    saveEdit,
    startEdit,
    cancelEdit,
    toggleActive,
    deleteOption,
    screenedWords,
    screenedWordDraft,
    isLoadingContent,
    loadScreenedWords,
    bulkCreateScreenedWords,
    specialDays,
    specialDayForm,
    isLoadingCalendar,
    loadSpecialDays,
    createSpecialDay,
    systemHealth,
    systemAlerts,
    activityLogs,
    isLoadingSystem,
    loadSystem,
    policies,
    isSavingPolicies,
    savePolicies,
    pricingConfigs,
    isLoadingPricing,
    loadPricing,
    discountCodes,
    isLoadingDiscounts,
    loadDiscountCodes,
    apiKeys,
    isLoadingApiKeys,
    loadApiKeys,
    allUsers,
    isLoadingUsers,
    userSearch,
    loadAllUsers,
    roles,
    isLoadingRoles,
    loadRoles,
    blogCategories,
    isLoadingBlog,
    newCategoryName,
    loadBlogCategories,
    createBlogCategory,
    isSavingSection,
    saveSection,
  };
});
