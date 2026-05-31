import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { websitesApi, type Website } from "@/api/websites";

export const useWebsitesStore = defineStore("websites", () => {
  const list = ref<Website[]>([]);
  const loaded = ref(false);

  async function ensure() {
    if (loaded.value) return;
    try {
      const { data } = await websitesApi.list({ is_active: true, limit: 100 });
      list.value = Array.isArray(data) ? data : (data as { results: Website[] }).results ?? [];
    } catch { /* non-fatal — callers fall back to raw ID */ }
    finally { loaded.value = true; }
  }

  function nameById(id: number | null | undefined): string {
    if (!id) return "—";
    const ws = list.value.find((w) => w.id === id);
    return ws?.name ?? ws?.domain ?? `Site #${id}`;
  }

  const byId = computed(() =>
    Object.fromEntries(list.value.map((w) => [w.id, w])) as Record<number, Website>
  );

  return { list, loaded, ensure, nameById, byId };
});
