import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { usePortalContextStore } from "@/stores/portalContext";
import * as portalContextApi from "@/api/portalContext";

function mockContext(overrides = {}) {
  return {
    surface: "client" as const,
    portal: null,
    website: { id: 12, name: "EssayBrand", slug: "essaybrand", domain: "essaybrand.com" },
    branding: {
      brand_name: "EssayBrand",
      tagline: "Your essay partner",
      logo_url: "",
      favicon_url: "",
      primary_color: "#2563eb",
      secondary_color: "#0f172a",
      accent_color: "#14b8a6",
    },
    payment_disclosure: {
      processor_name: "OrderBridge Payments",
      statement_descriptor: "ORDERBRIDGE PAYMENTS",
      text: "Processed by OrderBridge Payments.",
      pre_payment_notice: "EssayBrand uses OrderBridge Payments.",
    },
    allowed_roles: ["client"],
    ...overrides,
  };
}

describe("portalContext store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.restoreAllMocks();
  });

  it("defaults to client surface before init", () => {
    const store = usePortalContextStore();
    expect(store.surface).toBe("client");
    expect(store.ready).toBe(false);
  });

  it("sets surface, website, and disclosure after successful init", async () => {
    vi.spyOn(portalContextApi, "fetchPortalContext").mockResolvedValue(mockContext());

    const store = usePortalContextStore();
    await store.init();

    expect(store.surface).toBe("client");
    expect(store.website?.name).toBe("EssayBrand");
    expect(store.paymentDisclosure?.processor_name).toBe("OrderBridge Payments");
    expect(store.allowedRoles).toEqual(["client"]);
    expect(store.ready).toBe(true);
  });

  it("sets homeRoute to home for client surface", async () => {
    vi.spyOn(portalContextApi, "fetchPortalContext").mockResolvedValue(mockContext());

    const store = usePortalContextStore();
    await store.init();

    expect(store.homeRoute).toEqual({ name: "home" });
  });

  it("sets homeRoute to writer-dashboard for writer surface", async () => {
    vi.spyOn(portalContextApi, "fetchPortalContext").mockResolvedValue(
      mockContext({ surface: "writer", website: null, branding: null, allowed_roles: ["writer"] })
    );

    const store = usePortalContextStore();
    await store.init();

    expect(store.homeRoute).toEqual({ name: "writer-dashboard" });
  });

  it("sets homeRoute to admin-dashboard for staff surface", async () => {
    vi.spyOn(portalContextApi, "fetchPortalContext").mockResolvedValue(
      mockContext({
        surface: "staff",
        website: null,
        branding: null,
        payment_disclosure: null,
        allowed_roles: ["superadmin", "admin", "editor", "support"],
      })
    );

    const store = usePortalContextStore();
    await store.init();

    expect(store.homeRoute).toEqual({ name: "admin-dashboard" });
  });

  it("falls back to client surface when fetch fails", async () => {
    vi.spyOn(portalContextApi, "fetchPortalContext").mockRejectedValue(
      new Error("Network error")
    );

    const store = usePortalContextStore();
    await store.init();

    expect(store.surface).toBe("client");
    expect(store.ready).toBe(true);
    expect(store.homeRoute).toEqual({ name: "home" });
  });

  it("sets payment_disclosure to null for writer surface", async () => {
    vi.spyOn(portalContextApi, "fetchPortalContext").mockResolvedValue(
      mockContext({ surface: "writer", website: null, branding: null, payment_disclosure: null, allowed_roles: ["writer"] })
    );

    const store = usePortalContextStore();
    await store.init();

    expect(store.paymentDisclosure).toBeNull();
  });
});
