import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminPublishingApi,
  type SeoPagePayload,
  type SeoPageRecord,
  type WagtailPageRecord,
} from "@/api/adminPublishing";
import { useAuthStore } from "@/stores/auth";
import type {
  PublishingContentType,
  PublishingItem,
  PublishingMetric,
} from "@/types/adminPublishing";

type ListResponse<T> = T[] | { results: T[] };

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function typeFromWagtail(record: WagtailPageRecord): PublishingContentType {
  const modelType = record.meta?.type?.toLowerCase() ?? "";
  if (modelType.includes("blog")) return "blog";
  if (modelType.includes("service")) return "service";
  return "seo";
}

function normalizeWagtailPage(record: WagtailPageRecord): PublishingItem {
  const slug = record.slug || record.meta?.slug || record.title.toLowerCase().replace(/\s+/g, "-");
  return {
    id: record.id,
    type: typeFromWagtail(record),
    title: record.title,
    slug,
    status: record.live === false ? "draft" : "published",
    source: "wagtail",
    updatedAt: record.latest_revision_created_at ?? record.last_published_at ?? null,
    publishedAt: record.last_published_at ?? record.meta?.first_published_at ?? null,
    url: record.meta?.html_url,
    summary: record.meta?.type,
  };
}

function normalizeSeoPage(record: SeoPageRecord): PublishingItem {
  return {
    id: record.id,
    type: "seo",
    title: record.title,
    slug: record.slug,
    status: record.is_published ? "published" : "draft",
    source: "seo_pages",
    updatedAt: record.updated_at ?? null,
    publishedAt: record.publish_date ?? null,
    summary: record.meta_description,
  };
}

function previewItems(): PublishingItem[] {
  const now = Date.now();
  return [
    {
      id: 201,
      type: "blog",
      title: "How to plan a capstone paper without panic",
      slug: "capstone-paper-planning",
      status: "published",
      source: "wagtail",
      updatedAt: new Date(now - 1000 * 60 * 60 * 7).toISOString(),
      publishedAt: new Date(now - 1000 * 60 * 60 * 24 * 5).toISOString(),
      url: "/blog/capstone-paper-planning/",
      summary: "cms_blog.BlogPostPage",
    },
    {
      id: 202,
      type: "service",
      title: "Nursing essay writing service",
      slug: "nursing-essay-writing-service",
      status: "draft",
      source: "wagtail",
      updatedAt: new Date(now - 1000 * 60 * 40).toISOString(),
      publishedAt: null,
      url: "/services/nursing-essay-writing-service/",
      summary: "cms_service_pages.ServicePage",
    },
    {
      id: 301,
      type: "seo",
      title: "Best online class help",
      slug: "best-online-class-help",
      status: "published",
      source: "seo_pages",
      updatedAt: new Date(now - 1000 * 60 * 60 * 2).toISOString(),
      publishedAt: new Date(now - 1000 * 60 * 60 * 2).toISOString(),
      summary: "Landing page managed through the SEO pages API.",
    },
  ];
}

export const useAdminPublishingStore = defineStore("admin-publishing", () => {
  const items = ref<PublishingItem[]>([]);
  const activeType = ref<PublishingContentType | "all">("all");
  const query = ref("");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const draft = ref({
    website: 1,
    title: "New service landing page",
    slug: "new-service-landing-page",
    meta_description: "Describe this service page for search and conversion.",
    is_published: false,
  });

  const filteredItems = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return items.value.filter((item) => {
      const typeMatches = activeType.value === "all" || item.type === activeType.value;
      const textMatches =
        !needle ||
        [item.title, item.slug, item.status, item.source, item.summary]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(needle));
      return typeMatches && textMatches;
    });
  });

  const metrics = computed<PublishingMetric[]>(() => {
    const published = items.value.filter((item) => item.status === "published").length;
    const drafts = items.value.filter((item) => item.status !== "published").length;
    const blogs = items.value.filter((item) => item.type === "blog").length;
    const services = items.value.filter((item) => item.type === "service" || item.type === "seo").length;
    return [
      {
        label: "Content items",
        value: items.value.length,
        detail: "Wagtail pages plus writable SEO landing pages.",
        tone: "neutral",
      },
      {
        label: "Published",
        value: published,
        detail: "Live pages visible to frontend/public APIs.",
        tone: "good",
      },
      {
        label: "Drafts",
        value: drafts,
        detail: "Pages needing staff review or Wagtail publishing.",
        tone: drafts ? "warn" : "good",
      },
      {
        label: "Blog / service",
        value: `${blogs} / ${services}`,
        detail: "Editorial posts and service/landing pages.",
        tone: "neutral",
      },
    ];
  });

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        items.value = previewItems();
        return;
      }

      const [blogRes, serviceRes, seoRes] = await Promise.allSettled([
        adminPublishingApi.wagtailPages({
          type: "cms_blog.BlogPostPage",
          fields: "*",
          limit: 50,
        }),
        adminPublishingApi.wagtailPages({
          type: "cms_service_pages.ServicePage",
          fields: "*",
          limit: 50,
        }),
        adminPublishingApi.seoPages({ page_size: 50 }),
      ]);

      const next: PublishingItem[] = [];
      if (blogRes.status === "fulfilled") {
        next.push(...blogRes.value.data.items.map(normalizeWagtailPage));
      }
      if (serviceRes.status === "fulfilled") {
        next.push(...serviceRes.value.data.items.map(normalizeWagtailPage));
      }
      if (seoRes.status === "fulfilled") {
        next.push(...normalizeList(seoRes.value.data).map(normalizeSeoPage));
      }

      items.value = next;
    } catch (caught) {
      error.value = "Unable to load publishing data.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function createLandingPage(publish = false) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      const now = new Date().toISOString();
      const payload: SeoPagePayload = {
        website: draft.value.website,
        title: draft.value.title,
        slug: draft.value.slug,
        meta_title: draft.value.title,
        meta_description: draft.value.meta_description,
        is_published: publish,
        publish_date: publish ? now : null,
        blocks: [
          { type: "hero", value: { heading: draft.value.title } },
          { type: "paragraph", value: draft.value.meta_description },
          { type: "cta", value: { label: "Start an order", href: "/client/new-order" } },
        ],
      };

      if (auth.isPreviewSession) {
        items.value = [
          {
            id: Date.now(),
            type: "seo",
            title: payload.title,
            slug: payload.slug,
            status: publish ? "published" : "draft",
            source: "seo_pages",
            updatedAt: now,
            publishedAt: payload.publish_date ?? null,
            summary: payload.meta_description,
          },
          ...items.value,
        ];
        notice.value = publish ? "Preview landing page published." : "Preview landing page drafted.";
        return;
      }

      await adminPublishingApi.createSeoPage(payload);
      notice.value = publish ? "Landing page published." : "Landing page draft created.";
      await hydrate();
    } catch (caught) {
      error.value = "Unable to create landing page.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  return {
    items,
    activeType,
    query,
    draft,
    isLoading,
    isMutating,
    error,
    notice,
    filteredItems,
    metrics,
    hydrate,
    createLandingPage,
  };
});
