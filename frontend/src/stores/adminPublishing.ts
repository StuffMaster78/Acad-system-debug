import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminPublishingApi,
  type SeoPagePayload,
  type SeoPageRecord,
  type WagtailPageRecord,
} from "@/api/adminPublishing";
import { useAuthStore } from "@/stores/auth";
import { useWebsitesStore } from "@/stores/websites";
import type {
  PublishingAdminLink,
  PublishingContentType,
  PublishingFlowStep,
  PublishingItem,
  PublishingMetric,
  PublishingRoleResponsibility,
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
  const sites = useWebsitesStore();
  const websiteId = typeof record.website === "number" ? record.website : null;
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
    websiteId,
    websiteName: websiteId ? sites.nameById(websiteId) : undefined,
  };
}

function contentTypeLabel(type: PublishingContentType) {
  if (type === "blog") return "blog article";
  if (type === "service") return "service page";
  return "SEO landing page";
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
    website: null as number | null,
    type: "seo" as PublishingContentType,
    title: "New service landing page",
    slug: "new-service-landing-page",
    primary_keyword: "academic writing help",
    audience: "Clients comparing writing services",
    meta_description: "Describe this service page for search and conversion.",
    cta_label: "Start an order",
    cta_href: "/client/new-order",
    review_notes: "Check keyword intent, internal links, and website fit before publishing.",
    is_published: false,
    publish_date: null as string | null,
  });

  const flowSteps: PublishingFlowStep[] = [
    {
      label: "Plan",
      detail: "Choose website, audience, keyword intent, and page type before drafting.",
      owner: "Admin / support",
    },
    {
      label: "Draft",
      detail: "Write blog articles and rich service pages in Wagtail; use this desk for SEO landing pages.",
      owner: "Editor / support",
    },
    {
      label: "SEO",
      detail: "Set slug, meta title, meta description, CTA, canonical structure, and internal links.",
      owner: "Editor",
    },
    {
      label: "Review",
      detail: "Check accuracy, service claims, brand tone, page ownership, and publishing readiness.",
      owner: "Admin / editor",
    },
    {
      label: "Publish",
      detail: "Publish Wagtail pages through CMS workflow; publish SEO landing pages through the API.",
      owner: "Admin / superadmin",
    },
    {
      label: "Monitor",
      detail: "Track freshness, ranking gaps, conversion quality, and outdated service promises.",
      owner: "Superadmin / admin",
    },
  ];

  const roleResponsibilities: PublishingRoleResponsibility[] = [
    {
      role: "superadmin",
      label: "Superadmin",
      scope: "Cross-tenant publishing strategy and final authority for global pages.",
      actions: ["Approve tenant-wide SEO structures", "Publish or retire sensitive pages", "Audit content coverage"],
    },
    {
      role: "admin",
      label: "Admin",
      scope: "Website-level publishing operations for blogs, services, and landing pages.",
      actions: ["Create SEO pages", "Publish approved pages", "Assign editorial follow-up"],
    },
    {
      role: "editor",
      label: "Editor",
      scope: "Quality, structure, SEO intent, and content readiness before anything goes live.",
      actions: ["Draft and review Wagtail pages", "Fix content quality", "Validate metadata and links"],
    },
    {
      role: "support",
      label: "Support",
      scope: "Operational content requests, help/service updates, and intake from client conversations.",
      actions: ["Request new service pages", "Prepare support-led drafts", "Flag outdated public content"],
    },
  ];

  const adminLinks: PublishingAdminLink[] = [
    {
      label: "Authors",
      href: "/cms-admin/snippets/cms_authors/author/",
      detail: "Create credentialed author records with bio, photo, role, expertise, degrees, licenses, and identity links.",
      owner: "Superadmin / admin",
    },
    {
      label: "Author profile pages",
      href: "/cms-admin/pages/",
      detail: "Create public /authors/<slug>/ pages under the tenant Author Index and attach an Author record.",
      owner: "Editor",
    },
    {
      label: "Blog categories",
      href: "/cms-admin/snippets/cms_core/blogcategory/",
      detail: "Set tenant-scoped blog category names, slugs, descriptions, featured state, ordering, and SEO metadata.",
      owner: "Admin / editor",
    },
    {
      label: "Blog tags",
      href: "/cms-admin/snippets/cms_core/blogtag/",
      detail: "Manage tenant-scoped tags used to group and filter blog articles.",
      owner: "Editor / support",
    },
    {
      label: "Service categories",
      href: "/cms-admin/snippets/cms_core/servicecategory/",
      detail: "Manage tenant-scoped service groupings such as Nursing, Business, Programming, or General.",
      owner: "Admin / support",
    },
  ];

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

  const selectedWritePath = computed(() => {
    if (draft.value.type === "seo") {
      return {
        title: "Direct API publishing",
        detail: "SEO landing pages can be saved or published from this desk through /api/v1/seo-pages/.",
        actionLabel: "Publish SEO page",
      };
    }

    return {
      title: "Wagtail CMS workflow",
      detail: `${contentTypeLabel(draft.value.type)} drafts are created in Wagtail so you get rich blocks, media, preview, revisions, and editorial approvals. The Wagtail editor opens automatically after creation.`,
      actionLabel: "Create in CMS",
    };
  });

  async function hydrate() {
    const auth = useAuthStore();
    const sites = useWebsitesStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        items.value = previewItems();
        return;
      }

      // Pre-load website names so normalizeSeoPage can resolve them synchronously
      await sites.ensure();

      // Auto-select first available website for the draft if not already set
      if (!draft.value.website && sites.list.length > 0) {
        draft.value.website = sites.list[0].id;
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

  function buildSeoPayload(publish = false): SeoPagePayload {
    const now = new Date().toISOString();
    if (!draft.value.website) {
      throw new Error("Select a website before creating an SEO landing page.");
    }

    return {
      website: draft.value.website,
      title: draft.value.title,
      slug: draft.value.slug,
      meta_title: draft.value.title,
      meta_description: draft.value.meta_description,
      is_published: publish,
      publish_date: draft.value.publish_date || (publish ? now : null),
      blocks: [
        {
          type: "hero",
          value: {
            heading: draft.value.title,
            audience: draft.value.audience,
            keyword: draft.value.primary_keyword,
          },
        },
        { type: "paragraph", value: draft.value.meta_description },
        { type: "cta", value: { label: draft.value.cta_label, href: draft.value.cta_href } },
      ],
    };
  }

  function queueCmsDraft(publish = false) {
    const now = new Date().toISOString();
    items.value = [
      {
        id: `queued-${Date.now()}`,
        type: draft.value.type,
        title: draft.value.title,
        slug: draft.value.slug,
        status: publish ? "ready for CMS" : "draft",
        source: "wagtail",
        updatedAt: now,
        publishedAt: null,
        url: "/cms-admin/pages/",
        summary: draft.value.meta_description,
        keyword: draft.value.primary_keyword,
        ownerRole: "editorial",
      },
      ...items.value,
    ];
    notice.value = `${contentTypeLabel(draft.value.type)} queued for Wagtail. Open CMS pages to create the rich page with revisions and approval.`;
  }

  async function createContentDraft(publish = false) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      const now = new Date().toISOString();

      if (draft.value.type !== "seo") {
        if (auth.isPreviewSession) {
          queueCmsDraft(publish);
          return;
        }
        // Create the Wagtail draft via the backend, then redirect to the edit page
        const { data } = await adminPublishingApi.createPageDraft({
          type: draft.value.type as "blog" | "service",
          title: draft.value.title,
          slug: draft.value.slug,
          meta_description: draft.value.meta_description,
          primary_keyword: draft.value.primary_keyword,
          website_id: draft.value.website || null,
        });
        notice.value = `Draft created in Wagtail (page #${data.page_id}). Opening editor…`;
        // Open the Wagtail edit page in the same tab so staff are taken directly
        // to the rich editor with the fields pre-filled.
        window.open(data.edit_url, "_blank", "noopener");
        return;
      }

      const payload = buildSeoPayload(publish);

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
            keyword: draft.value.primary_keyword,
          },
          ...items.value,
        ];
        notice.value = publish ? "Preview SEO page published." : "Preview SEO page drafted.";
        return;
      }

      await adminPublishingApi.createSeoPage(payload);
      notice.value = publish ? "SEO landing page published." : "SEO landing page draft created.";
      await hydrate();
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : "Unable to create publishing draft.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function setPublishState(item: PublishingItem, publish: boolean) {
    const auth = useAuthStore();
    notice.value = "";
    error.value = "";

    if (item.source !== "seo_pages") {
      notice.value = "Blog articles and rich service pages are published inside Wagtail so revisions and approvals stay intact.";
      return;
    }

    isMutating.value = true;
    try {
      const now = new Date().toISOString();
      if (auth.isPreviewSession) {
        item.status = publish ? "published" : "draft";
        item.publishedAt = publish ? now : null;
        item.updatedAt = now;
        notice.value = publish ? "Preview SEO page published." : "Preview SEO page moved back to draft.";
        return;
      }

      await adminPublishingApi.updateSeoPage(Number(item.id), {
        is_published: publish,
        publish_date: publish ? now : null,
      });
      notice.value = publish ? "SEO page published." : "SEO page moved back to draft.";
      await hydrate();
    } catch (caught) {
      error.value = "Unable to update SEO page status.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function createLandingPage(publish = false) {
    draft.value.type = "seo";
    await createContentDraft(publish);
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
    flowSteps,
    roleResponsibilities,
    adminLinks,
    selectedWritePath,
    hydrate,
    createContentDraft,
    createLandingPage,
    setPublishState,
  };
});
