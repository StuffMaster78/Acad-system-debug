import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { websitesApi, type Website } from "@/api/websites";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";

type WebsiteLike = Pick<Website, "id" | "name" | "domain" | "slug">;

export const useWebsitesStore = defineStore("websites", () => {
  const list = ref<Website[]>([]);
  const loaded = ref(false);

  function upsertWebsiteSummary(site: WebsiteLike | null | undefined) {
    if (!site?.id) return;
    const existing = list.value.find((w) => w.id === site.id);
    if (existing) {
      existing.name = site.name || existing.name;
      existing.domain = site.domain || existing.domain;
      existing.slug = site.slug || existing.slug;
      return;
    }
    list.value.push({
      id: site.id,
      name: site.name,
      domain: site.domain,
      slug: site.slug,
      is_active: true,
      logo: null,
      theme_color: null,
      contact_email: null,
      contact_phone: null,
      meta_title: null,
      meta_description: null,
      admin_notifications_email: null,
      allow_registration: false,
      allow_guest_checkout: false,
      guest_requires_email_verification: false,
      guest_max_order_amount: null,
      guest_block_urgent_before_hours: null,
      guest_magic_link_ttl_hours: null,
      google_analytics_id: null,
      google_search_console_id: null,
      bing_webmaster_id: null,
      enable_live_chat: false,
      tawkto_widget_id: null,
      tawkto_property_id: null,
      communication_widget_type: null,
      communication_widget_config: null,
      is_deleted: false,
      deleted_at: null,
    });
  }

  async function ensure() {
    const portal = usePortalContextStore();
    upsertWebsiteSummary(portal.website);
    if (loaded.value) return;
    const auth = useAuthStore();
    // Skip entirely when not authenticated — calling /websites/ with no token
    // returns 401, which the interceptor turns into window.location.replace('/auth/login'),
    // creating an infinite reload loop on the login page.
    if ((!auth.isAuthenticated && import.meta.env.MODE !== "test") || auth.isPreviewSession) {
      loaded.value = true;
      return;
    }
    try {
      const { data } = await websitesApi.list({ is_active: true, limit: 100 });
      list.value = Array.isArray(data) ? data : (data as { results: Website[] }).results ?? [];
      upsertWebsiteSummary(portal.website);
    } catch { /* non-fatal — callers fall back to raw ID */ }
    finally { loaded.value = true; }
  }

  function websiteById(id: number | string | null | undefined): Website | null {
    if (id === null || id === undefined || id === "") return null;
    const numericId = Number(id);
    if (!Number.isFinite(numericId)) return null;
    return list.value.find((w) => w.id === numericId) ?? null;
  }

  function nameById(id: number | string | null | undefined): string {
    const ws = websiteById(id);
    if (ws) return ws.name || ws.domain || `Site #${ws.id}`;
    return id ? `Site #${id}` : "—";
  }

  function labelById(id: number | string | null | undefined): string {
    const ws = websiteById(id);
    if (!ws) return id ? `Site #${id}` : "—";
    const domain = ws.domain?.replace(/^https?:\/\//, "");
    return domain ? `${ws.name || domain} (${domain})` : ws.name || `Site #${ws.id}`;
  }

  const byId = computed(() =>
    Object.fromEntries(list.value.map((w) => [w.id, w])) as Record<number, Website>
  );

  const options = computed(() =>
    list.value.map((w) => ({ label: labelById(w.id), value: w.id })),
  );

  return { list, loaded, ensure, upsertWebsiteSummary, websiteById, nameById, labelById, byId, options };
});
