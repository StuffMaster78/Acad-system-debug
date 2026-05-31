import { defineStore } from "pinia";
import { ref } from "vue";
import { fetchPortalContext, type PortalContext, type PortalBranding, type PaymentDisclosure } from "@/api/portalContext";

type Surface = "client" | "writer" | "staff";

export const usePortalContextStore = defineStore("portalContext", () => {
  const surface = ref<Surface>("client");
  const portal = ref<PortalContext["portal"]>(null);
  const website = ref<PortalContext["website"]>(null);
  const branding = ref<PortalBranding | null>(null);
  const paymentDisclosure = ref<PaymentDisclosure | null>(null);
  const allowedRoles = ref<string[]>([]);
  const ready = ref(false);

  const homeRoute = ref<{ name: string }>({ name: "home" });

  async function init() {
    try {
      const ctx = await fetchPortalContext();
      surface.value = ctx.surface;
      portal.value = ctx.portal;
      website.value = ctx.website;
      branding.value = ctx.branding;
      paymentDisclosure.value = ctx.payment_disclosure;
      allowedRoles.value = ctx.allowed_roles;

      homeRoute.value =
        ctx.surface === "writer"
          ? { name: "writer-dashboard" }
          : ctx.surface === "staff"
            ? { name: "admin-dashboard" }
            : { name: "home" };

      if (ctx.branding) {
        applyBrandingToCss(ctx.branding);
      }
    } catch {
      // Network failure or dev environment without the endpoint — default to client surface.
      surface.value = "client";
      allowedRoles.value = ["client"];
      homeRoute.value = { name: "home" };
    } finally {
      ready.value = true;
    }
  }

  function applyBrandingToCss(b: PortalBranding) {
    const root = document.documentElement;
    if (b.primary_color) root.style.setProperty("--color-primary", b.primary_color);
    if (b.secondary_color) root.style.setProperty("--color-secondary", b.secondary_color);
    if (b.accent_color) root.style.setProperty("--color-accent", b.accent_color);
    if (b.favicon_url) {
      const link = document.querySelector<HTMLLinkElement>("link[rel~='icon']");
      if (link) link.href = b.favicon_url;
    }
  }

  return {
    surface,
    portal,
    website,
    branding,
    paymentDisclosure,
    allowedRoles,
    ready,
    homeRoute,
    init,
  };
});
