import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useWebsitesStore } from "@/stores/websites";
import * as websitesApi from "@/api/websites";

const MOCK_WEBSITES = [
  { id: 1, name: "EssayBrand", domain: "essaybrand.com", slug: "essaybrand" },
  { id: 2, name: "ResearchHelp", domain: "researchhelp.com", slug: "researchhelp" },
];

describe("websites store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.restoreAllMocks();
  });

  it("starts empty and not loaded", () => {
    const store = useWebsitesStore();
    expect(store.list).toHaveLength(0);
    expect(store.loaded).toBe(false);
  });

  it("nameById returns — for null/undefined", () => {
    const store = useWebsitesStore();
    expect(store.nameById(null)).toBe("—");
    expect(store.nameById(undefined)).toBe("—");
  });

  it("nameById returns Site #N fallback for unknown ID", () => {
    const store = useWebsitesStore();
    expect(store.nameById(99)).toBe("Site #99");
  });

  it("ensure() loads websites and marks loaded", async () => {
    vi.spyOn(websitesApi.websitesApi, "list").mockResolvedValue({
      data: MOCK_WEBSITES,
    } as any);

    const store = useWebsitesStore();
    await store.ensure();

    expect(store.loaded).toBe(true);
    expect(store.list).toHaveLength(2);
    expect(store.list[0].name).toBe("EssayBrand");
  });

  it("ensure() is a no-op on second call (cached)", async () => {
    const spy = vi.spyOn(websitesApi.websitesApi, "list").mockResolvedValue({
      data: MOCK_WEBSITES,
    } as any);

    const store = useWebsitesStore();
    await store.ensure();
    await store.ensure();

    expect(spy).toHaveBeenCalledTimes(1);
  });

  it("nameById returns name after ensure()", async () => {
    vi.spyOn(websitesApi.websitesApi, "list").mockResolvedValue({
      data: MOCK_WEBSITES,
    } as any);

    const store = useWebsitesStore();
    await store.ensure();

    expect(store.nameById(1)).toBe("EssayBrand");
    expect(store.nameById(2)).toBe("ResearchHelp");
  });

  it("byId computed maps id → Website object", async () => {
    vi.spyOn(websitesApi.websitesApi, "list").mockResolvedValue({
      data: MOCK_WEBSITES,
    } as any);

    const store = useWebsitesStore();
    await store.ensure();

    expect(store.byId[1].domain).toBe("essaybrand.com");
    expect(store.byId[2].slug).toBe("researchhelp");
  });

  it("handles fetch failure gracefully — marks loaded, keeps empty list", async () => {
    vi.spyOn(websitesApi.websitesApi, "list").mockRejectedValue(new Error("network"));

    const store = useWebsitesStore();
    await store.ensure();

    expect(store.loaded).toBe(true);
    expect(store.list).toHaveLength(0);
    expect(store.nameById(1)).toBe("Site #1");
  });
});
