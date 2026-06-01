import { ref, computed, reactive } from "vue";
import { defineStore } from "pinia";
import { DOMAINS, ALL_SETTINGS, getSettingsForSection, scopeAllows } from "@/config/configDefinitions";
import type { AuditEntry, ConfigRuntimeValue, ConfigDomainMeta } from "@/types/config";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";

// ── Preview data ──────────────────────────────────────────────────────────────

function buildPreviewValues(): Record<string, ConfigRuntimeValue> {
  const result: Record<string, ConfigRuntimeValue> = {};
  const changedAt = new Date(Date.now() - 3600000 * 2).toISOString();
  for (const def of ALL_SETTINGS) {
    result[def.key] = {
      globalValue: def.defaultValue,
      websiteValues: {},
      lastChangedBy: null,
      lastChangedAt: null,
    };
  }
  // Sprinkle some "already configured" entries
  const overrides: Record<string, unknown> = {
    deadline_min_hours: 8,
    order_auto_complete_days: 5,
    pricing_base_price_per_page: 14.00,
    preferred_writer_fee_percent: 25,
    writer_payout_base_percent: 72,
    flag_maintenance_mode: false,
  };
  for (const [key, val] of Object.entries(overrides)) {
    if (result[key]) {
      result[key].globalValue = val;
      result[key].lastChangedBy = "Eva Admin";
      result[key].lastChangedAt = changedAt;
    }
  }
  return result;
}

function buildPreviewAudit(sectionKey: string): AuditEntry[] {
  const now = Date.now();
  return [
    { id: 1, key: "deadline_min_hours", label: "Minimum deadline (hours)", section: sectionKey, oldValue: 6, newValue: 8, changedBy: "Eva Admin", changedAt: new Date(now - 3600000 * 2).toISOString(), website: null },
    { id: 2, key: "deadline_min_hours", label: "Minimum deadline (hours)", section: sectionKey, oldValue: 12, newValue: 6, changedBy: "Super Admin", changedAt: new Date(now - 86400000 * 3).toISOString(), website: null },
    { id: 3, key: "order_auto_complete_days", label: "Auto-complete after (days)", section: sectionKey, oldValue: 3, newValue: 5, changedBy: "Eva Admin", changedAt: new Date(now - 86400000 * 7).toISOString(), website: "WritePro" },
  ];
}

// ── Store ─────────────────────────────────────────────────────────────────────

export const useAdminMasterConfigStore = defineStore("admin-master-config", () => {
  const auth = useAuthStore();
  const ui = useUiStore();

  // ── Navigation ──────────────────────────────────────────────────────────────
  const activeDomain = ref<string>("order-management");
  const activeSection = ref<string>("order-rules");

  function navigate(domain: string, section: string) {
    activeDomain.value = domain;
    activeSection.value = section;
  }

  // ── Website scope ───────────────────────────────────────────────────────────
  const websites = ref<string[]>(["WritePro", "EssayMasters"]);
  const selectedWebsite = ref<string | null>(null); // null = Global

  // ── Search ──────────────────────────────────────────────────────────────────
  const searchQuery = ref("");

  const searchResults = computed(() => {
    const q = searchQuery.value.trim().toLowerCase();
    if (!q) return [];
    return ALL_SETTINGS.filter(
      (s) =>
        s.label.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q) ||
        s.key.toLowerCase().includes(q),
    );
  });

  const isSearching = computed(() => searchQuery.value.trim().length > 0);

  // ── Config values ───────────────────────────────────────────────────────────
  const configValues = ref<Record<string, ConfigRuntimeValue>>({});
  const isLoadingValues = ref(false);

  function getEffectiveValue(key: string): unknown {
    const entry = configValues.value[key];
    if (!entry) return undefined;
    if (selectedWebsite.value && entry.websiteValues[selectedWebsite.value] !== undefined) {
      return entry.websiteValues[selectedWebsite.value];
    }
    return entry.globalValue;
  }

  function isWebsiteOverridden(key: string): boolean {
    if (!selectedWebsite.value) return false;
    const entry = configValues.value[key];
    return entry?.websiteValues[selectedWebsite.value] !== undefined;
  }

  async function loadConfigValues() {
    isLoadingValues.value = true;
    try {
      if (auth.isPreviewSession) {
        configValues.value = buildPreviewValues();
        return;
      }
      // const { data } = await configApi.getAll({ website: selectedWebsite.value });
      // configValues.value = data;
    } catch {
      ui.toast("Failed to load config values.", "error");
    } finally {
      isLoadingValues.value = false;
    }
  }

  // ── Dirty tracking ──────────────────────────────────────────────────────────
  // Key: `${domain}:${section}` → { configKey: newValue }
  const dirtyMap = reactive<Record<string, Record<string, unknown>>>({});

  function markDirty(domain: string, section: string, key: string, value: unknown) {
    const id = `${domain}:${section}`;
    if (!dirtyMap[id]) dirtyMap[id] = {};
    // Check if value equals current saved value
    const saved = getEffectiveValue(key);
    if (value === saved) {
      delete dirtyMap[id][key];
      if (Object.keys(dirtyMap[id]).length === 0) delete dirtyMap[id];
    } else {
      dirtyMap[id][key] = value;
    }
  }

  function getDirtyValue(domain: string, section: string, key: string): unknown {
    return dirtyMap[`${domain}:${section}`]?.[key];
  }

  function isSectionDirty(domain: string, section: string): boolean {
    const id = `${domain}:${section}`;
    return Boolean(dirtyMap[id] && Object.keys(dirtyMap[id]).length > 0);
  }

  const totalDirtyCount = computed(() =>
    Object.values(dirtyMap).filter((s) => Object.keys(s).length > 0).length,
  );

  function discardSection(domain: string, section: string) {
    delete dirtyMap[`${domain}:${section}`];
  }

  // ── Save ────────────────────────────────────────────────────────────────────
  const savingSection = ref<string | null>(null);

  async function saveSection(domain: string, section: string) {
    const id = `${domain}:${section}`;
    const dirty = dirtyMap[id];
    if (!dirty || !Object.keys(dirty).length) return;

    savingSection.value = id;
    try {
      if (auth.isPreviewSession) {
        await new Promise((r) => setTimeout(r, 500));
        for (const [key, value] of Object.entries(dirty)) {
          if (configValues.value[key]) {
            if (selectedWebsite.value) {
              configValues.value[key].websiteValues[selectedWebsite.value] = value;
            } else {
              configValues.value[key].globalValue = value;
            }
            configValues.value[key].lastChangedBy = auth.user?.full_name ?? "Admin";
            configValues.value[key].lastChangedAt = new Date().toISOString();
          }
        }
        delete dirtyMap[id];
        ui.toast(`${getSection(domain, section)?.label ?? section} saved.`, "success");
        return;
      }
      // const payload = Object.entries(dirty).map(([key, value]) => ({ key, value, website: selectedWebsite.value }));
      // await configApi.bulkUpdate(payload);
      delete dirtyMap[id];
      ui.toast("Section saved.", "success");
    } catch {
      ui.toast("Failed to save section.", "error");
    } finally {
      savingSection.value = null;
    }
  }

  async function saveAll() {
    const ids = Object.keys(dirtyMap).filter((id) => Object.keys(dirtyMap[id]).length > 0);
    for (const id of ids) {
      const [domain, section] = id.split(":");
      await saveSection(domain, section);
    }
  }

  // ── Reset section to defaults ───────────────────────────────────────────────
  async function resetSection(domain: string, section: string) {
    const defs = getSettingsForSection(domain, section);
    if (auth.isPreviewSession) {
      for (const def of defs) {
        if (configValues.value[def.key]) {
          if (selectedWebsite.value) {
            delete configValues.value[def.key].websiteValues[selectedWebsite.value];
          } else {
            configValues.value[def.key].globalValue = def.defaultValue;
          }
        }
      }
      discardSection(domain, section);
      ui.toast("Section reset to defaults.", "success");
    }
  }

  // ── Audit drawer ────────────────────────────────────────────────────────────
  const auditSection = ref<string | null>(null); // `${domain}:${section}`
  const auditEntries = ref<AuditEntry[]>([]);
  const isLoadingAudit = ref(false);

  async function openAudit(domain: string, section: string) {
    auditSection.value = `${domain}:${section}`;
    isLoadingAudit.value = true;
    try {
      if (auth.isPreviewSession) {
        await new Promise((r) => setTimeout(r, 300));
        auditEntries.value = buildPreviewAudit(section);
        return;
      }
      // const { data } = await configApi.auditLog({ domain, section });
      // auditEntries.value = data;
    } catch {
      auditEntries.value = [];
    } finally {
      isLoadingAudit.value = false;
    }
  }

  function closeAudit() {
    auditSection.value = null;
    auditEntries.value = [];
  }

  // ── Domain visibility by role ───────────────────────────────────────────────
  const visibleDomains = computed<ConfigDomainMeta[]>(() => {
    const role = auth.role ?? "support";
    return DOMAINS.filter((d) => scopeAllows(role, d.requiredScope));
  });

  function getSection(domain: string, section: string) {
    return DOMAINS.find((d) => d.key === domain)?.sections.find((s) => s.key === section);
  }

  // ── Export config ───────────────────────────────────────────────────────────
  function exportConfig() {
    const snapshot = {
      exportedAt: new Date().toISOString(),
      website: selectedWebsite.value ?? "global",
      values: Object.fromEntries(
        Object.entries(configValues.value).map(([key, v]) => [
          key,
          selectedWebsite.value ? (v.websiteValues[selectedWebsite.value] ?? v.globalValue) : v.globalValue,
        ]),
      ),
    };
    const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `config-${snapshot.website}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    ui.toast("Config exported.", "success");
  }

  return {
    // navigation
    activeDomain,
    activeSection,
    navigate,
    // website
    websites,
    selectedWebsite,
    // search
    searchQuery,
    searchResults,
    isSearching,
    // values
    configValues,
    isLoadingValues,
    getEffectiveValue,
    isWebsiteOverridden,
    loadConfigValues,
    // dirty
    dirtyMap,
    markDirty,
    getDirtyValue,
    isSectionDirty,
    totalDirtyCount,
    discardSection,
    // save
    savingSection,
    saveSection,
    saveAll,
    resetSection,
    // audit
    auditSection,
    auditEntries,
    isLoadingAudit,
    openAudit,
    closeAudit,
    // domains
    visibleDomains,
    getSection,
    // export
    exportConfig,
  };
});
