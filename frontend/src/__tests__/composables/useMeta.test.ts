import { describe, it, expect, beforeEach } from "vitest";
import { articleSchema, serviceSchema, webPageSchema } from "@/composables/useMeta";

describe("articleSchema", () => {
  it("returns correct @type and @context", () => {
    const s = articleSchema({ title: "Test", url: "https://example.com" });
    expect(s["@context"]).toBe("https://schema.org");
    expect(s["@type"]).toBe("Article");
  });

  it("maps headline and url", () => {
    const s = articleSchema({ title: "My Post", url: "https://example.com/post" });
    expect(s.headline).toBe("My Post");
    expect(s.url).toBe("https://example.com/post");
  });

  it("includes author when authorName is provided", () => {
    const s = articleSchema({
      title: "Post",
      url: "https://x.com",
      authorName: "Jane Doe",
      authorUrl: "https://x.com/jane",
    });
    expect((s.author as Record<string, string>)?.name).toBe("Jane Doe");
    expect((s.author as Record<string, string>)?.["@type"]).toBe("Person");
  });

  it("omits author when not provided", () => {
    const s = articleSchema({ title: "Post", url: "https://x.com" });
    expect(s.author).toBeUndefined();
  });

  it("sets dateModified to datePublished when updatedAt is absent", () => {
    const s = articleSchema({ title: "P", url: "https://x.com", publishedAt: "2026-01-01" });
    expect(s.dateModified).toBe("2026-01-01");
  });
});

describe("serviceSchema", () => {
  it("returns Service @type", () => {
    const s = serviceSchema({ name: "Essay Writing", url: "https://x.com/essays" });
    expect(s["@type"]).toBe("Service");
  });

  it("includes Offer when pricingFrom is given", () => {
    const s = serviceSchema({ name: "Essay", url: "https://x.com", pricingFrom: "9.99", currency: "USD" });
    const offers = s.offers as Record<string, string> | undefined;
    expect(offers?.price).toBe("9.99");
    expect(offers?.priceCurrency).toBe("USD");
  });

  it("omits offers when pricingFrom is absent", () => {
    const s = serviceSchema({ name: "Essay", url: "https://x.com" });
    expect(s.offers).toBeUndefined();
  });
});

describe("webPageSchema", () => {
  it("returns WebPage @type", () => {
    const s = webPageSchema({ title: "About Us", url: "https://x.com/about" });
    expect(s["@type"]).toBe("WebPage");
  });

  it("includes isPartOf website", () => {
    const s = webPageSchema({ title: "About", url: "https://x.com/about", siteName: "MyPlatform" });
    const isPartOf = s.isPartOf as Record<string, string>;
    expect(isPartOf.name).toBe("MyPlatform");
  });
});

describe("document.title via useMeta (integration)", () => {
  beforeEach(() => {
    document.title = "";
    document.querySelectorAll("meta").forEach((el) => el.remove());
    document.getElementById("page-schema-org")?.remove();
  });

  it("sets document.title with site name suffix", async () => {
    const { useMeta } = await import("@/composables/useMeta");
    const { createApp, defineComponent } = await import("vue");
    const TestApp = defineComponent({
      setup() {
        useMeta({ title: "Orders", siteName: "GradeCrest" });
      },
      template: "<div />",
    });
    const app = createApp(TestApp);
    const div = document.createElement("div");
    document.body.appendChild(div);
    app.mount(div);
    expect(document.title).toBe("Orders — GradeCrest");
    app.unmount();
    div.remove();
  });
});
