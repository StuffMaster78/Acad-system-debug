import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { api, apiPath } from "@/api/client";

export interface RegistryEntry {
  key: string;
  config_type: "bool" | "int" | "float" | "str" | "json";
  default: unknown;
  description: string;
  is_runtime_editable: boolean;
  requires_restart: boolean;
  enable_rollout: boolean;
  cache_ttl_seconds?: number;
}

export interface StoredConfig {
  key: string;
  value: unknown;
  scope: string;
  website_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const useRuntimeConfigStore = defineStore("runtime-config", () => {
  const registry = ref<RegistryEntry[]>([]);
  const stored = ref<Record<string, StoredConfig>>({});
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref("");
  const notice = ref("");

  // Effective value: stored override or default
  function getValue(key: string): unknown {
    if (stored.value[key] !== undefined) return stored.value[key].value;
    const entry = registry.value.find((r) => r.key === key);
    return entry?.default ?? null;
  }

  // Registry grouped by domain prefix
  const byDomain = computed(() => {
    const groups: Record<string, RegistryEntry[]> = {};
    for (const entry of registry.value) {
      const domain = entry.key.split(".")[0];
      if (!groups[domain]) groups[domain] = [];
      groups[domain].push(entry);
    }
    return groups;
  });

  const domains = computed(() => Object.keys(byDomain.value).sort());

  const overriddenKeys = computed(() => new Set(Object.keys(stored.value)));

  async function load() {
    isLoading.value = true;
    error.value = "";
    try {
      const [regRes, storedRes] = await Promise.allSettled([
        api.get<RegistryEntry[]>(apiPath("/runtime-config/registry/")),
        api.get<StoredConfig[]>(apiPath("/runtime-config/")),
      ]);
      if (regRes.status === "fulfilled") registry.value = regRes.value.data;
      if (storedRes.status === "fulfilled") {
        const map: Record<string, StoredConfig> = {};
        for (const item of storedRes.value.data) map[item.key] = item;
        stored.value = map;
      }
    } catch {
      error.value = "Failed to load runtime configs.";
    } finally {
      isLoading.value = false;
    }
  }

  async function save(key: string, value: unknown) {
    isSaving.value = true;
    notice.value = "";
    error.value = "";
    try {
      await api.post(apiPath("/runtime-config/update/"), { key, value });
      // Optimistically update stored
      if (!stored.value[key]) {
        stored.value[key] = {
          key,
          value,
          scope: "global",
          website_id: null,
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      } else {
        stored.value[key] = { ...stored.value[key], value, updated_at: new Date().toISOString() };
      }
      notice.value = `${key} updated.`;
    } catch {
      error.value = `Failed to save ${key}.`;
    } finally {
      isSaving.value = false;
    }
  }

  async function reset(key: string) {
    isSaving.value = true;
    error.value = "";
    try {
      await api.delete(apiPath(`/runtime-config/${key}/delete/`));
      delete stored.value[key];
      notice.value = `${key} reset to default.`;
    } catch {
      error.value = `Failed to reset ${key}.`;
    } finally {
      isSaving.value = false;
    }
  }

  return {
    registry,
    stored,
    isLoading,
    isSaving,
    error,
    notice,
    getValue,
    byDomain,
    domains,
    overriddenKeys,
    load,
    save,
    reset,
  };
});
