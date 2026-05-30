/**
 * CMS API — typed access to Wagtail API v2, custom CMS endpoints,
 * and the public SEO pages API.
 *
 * All page fields are requested explicitly so responses stay lean.
 */
import { api, apiPath } from "./client";

// ── Shared Wagtail primitives ─────────────────────────────────────────────

export interface WagtailImage {
  id: number;
  title: string;
  meta: { download_url: string };
}

export interface WagtailBlock {
  type: string;
  value: unknown;
  id?: string;
}

// ── Author ────────────────────────────────────────────────────────────────

export interface CMSAuthor {
  id: number;
  name: string;
  slug: string;
  bio: string;
  profile_photo?: WagtailImage | null;
  credentials?: string;
  degrees?: string[];
  areas_of_expertise?: string;
  years_experience?: number;
  role?: string;
  linkedin_url?: string;
  orcid_id?: string;
  google_scholar_url?: string;
  personal_website?: string;
  twitter_handle?: string;
}

// ── Blog ──────────────────────────────────────────────────────────────────

export interface BlogCategory {
  id: number;
  name: string;
  slug: string;
}

export interface BlogTag {
  id: number;
  name: string;
  slug: string;
}

export interface BlogPostSummary {
  id: number;
  title: string;
  meta: {
    type: string;
    slug: string;
    html_url?: string;
    first_published_at?: string | null;
  };
  excerpt?: string;
  featured_image?: WagtailImage | null;
  primary_author?: CMSAuthor | null;
  category?: BlogCategory | null;
  tags?: BlogTag[];
  last_substantive_update?: string | null;
  reading_time?: number | null;
  word_count?: number | null;
  last_published_at?: string | null;
}

export interface BlogPost extends BlogPostSummary {
  body: WagtailBlock[];
  contributing_authors?: CMSAuthor[];
  citation_mode?: string;
  toc?: { level: number; text: string; anchor: string }[];
}

// ── Service pages ─────────────────────────────────────────────────────────

export interface ServicePageSummary {
  id: number;
  title: string;
  meta: {
    type: string;
    slug: string;
    html_url?: string;
    first_published_at?: string | null;
  };
  service_category?: { name: string; slug: string } | null;
  pricing_from?: string | null;
  pricing_to?: string | null;
  turnaround_hours_fastest?: number | null;
  turnaround_hours_standard?: number | null;
  primary_cta_text?: string;
  primary_cta_url?: string;
  last_published_at?: string | null;
}

export interface ServicePage extends ServicePageSummary {
  body: WagtailBlock[];
  reviewer?: CMSAuthor | null;
  show_aggregate_rating?: boolean;
}

// ── SEO landing pages ─────────────────────────────────────────────────────

export interface SeoLandingPage {
  id: number;
  title: string;
  slug: string;
  meta_title?: string;
  meta_description?: string;
  blocks: Record<string, unknown>[];
  is_published: boolean;
  publish_date?: string | null;
}

// ── Attachments / downloadable resources ─────────────────────────────────

export interface AttachmentCategory {
  id: number;
  name: string;
  slug: string;
}

export interface AttachmentSummary {
  id: number;
  title: string;
  slug: string;
  description?: string;
  attachment_type: string;
  category?: AttachmentCategory | null;
  academic_level?: string;
  formatting_style?: string;
  file_format?: string;
  file_size_bytes?: number;
  page_count?: number;
  gate_type: "free" | "email" | "account" | "customer" | "paid";
  price?: string | null;
  is_featured?: boolean;
  average_rating?: number;
  rating_count?: number;
  download_count?: number;
  author?: CMSAuthor | null;
  related_service?: { id: number; title: string; slug: string } | null;
}

export interface AccessCheckResult {
  allowed: boolean;
  requires_email?: boolean;
  requires_account?: boolean;
  requires_purchase?: boolean;
  price?: string | null;
  reason?: string;
}

export interface DownloadResult {
  download_url?: string;
  error?: string;
}

// ── References / citations ────────────────────────────────────────────────

export interface ReferenceAuthor {
  family: string;
  given?: string;
  middle?: string;
}

export interface Reference {
  id: number;
  reference_type: string;
  title: string;
  authors: ReferenceAuthor[];
  publication_year?: number | null;
  publication_month?: number | null;
  journal_name?: string;
  journal_volume?: string;
  journal_issue?: string;
  pages?: string;
  publisher?: string;
  publisher_location?: string;
  doi?: string;
  isbn?: string;
  url?: string;
  url_archived?: string;
  is_peer_reviewed?: boolean;
  is_open_access?: boolean;
}

export interface Citation {
  id: number;
  position: number;
  page?: string;
  editor_note?: string;
  reference: Reference;
}

// ── Content graph ─────────────────────────────────────────────────────────

export interface ContentPillar {
  id: number;
  name: string;
  slug: string;
  description: string;
  service_page?: { id: number; title: string; slug: string } | null;
  hub_post?: { id: number; title: string; slug: string } | null;
  spoke_count?: number;
}

// ── Wagtail list response ─────────────────────────────────────────────────

interface WagtailListResponse<T> {
  items: T[];
  meta: { total_count: number };
}

// ── API ───────────────────────────────────────────────────────────────────

const BLOG_FIELDS = [
  "title", "excerpt", "featured_image", "primary_author",
  "category", "tags", "last_substantive_update",
  "reading_time", "word_count", "last_published_at",
].join(",");

const BLOG_DETAIL_FIELDS = [
  BLOG_FIELDS, "body", "contributing_authors",
  "citation_mode", "toc",
].join(",");

const SERVICE_FIELDS = [
  "title", "service_category", "pricing_from", "pricing_to",
  "turnaround_hours_fastest", "turnaround_hours_standard",
  "primary_cta_text", "primary_cta_url", "last_published_at",
].join(",");

const SERVICE_DETAIL_FIELDS = [
  SERVICE_FIELDS, "body", "reviewer", "show_aggregate_rating",
].join(",");

export const cmsApi = {
  // ── Blog ────────────────────────────────────────────────────────────────
  blogPosts: (params?: { category?: string; tag?: string; order?: string; limit?: number; offset?: number }) =>
    api.get<WagtailListResponse<BlogPostSummary>>(apiPath("/api/v2/pages/"), {
      params: {
        type: "cms_blog.BlogPostPage",
        live: true,
        order: "-first_published_at",
        fields: BLOG_FIELDS,
        limit: 12,
        ...params,
      },
    }),

  blogPost: (slug: string) =>
    api.get<WagtailListResponse<BlogPost>>(apiPath("/api/v2/pages/"), {
      params: {
        type: "cms_blog.BlogPostPage",
        slug,
        fields: BLOG_DETAIL_FIELDS,
      },
    }),

  // ── Service pages ────────────────────────────────────────────────────────
  servicePages: (params?: { category?: string; limit?: number }) =>
    api.get<WagtailListResponse<ServicePageSummary>>(apiPath("/api/v2/pages/"), {
      params: {
        type: "cms_service_pages.ServicePage",
        live: true,
        order: "title",
        fields: SERVICE_FIELDS,
        limit: 50,
        ...params,
      },
    }),

  servicePage: (slug: string) =>
    api.get<WagtailListResponse<ServicePage>>(apiPath("/api/v2/pages/"), {
      params: {
        type: "cms_service_pages.ServicePage",
        slug,
        fields: SERVICE_DETAIL_FIELDS,
      },
    }),

  // ── Authors ──────────────────────────────────────────────────────────────
  authors: () =>
    api.get<CMSAuthor[]>(apiPath("/cms-api/authors/")),

  author: (slug: string) =>
    api.get<CMSAuthor>(apiPath(`/cms-api/authors/${slug}/`)),

  authorPosts: (slug: string) =>
    api.get<BlogPostSummary[]>(apiPath(`/cms-api/authors/${slug}/posts/`)),

  // ── SEO landing pages ────────────────────────────────────────────────────
  landingPage: (slug: string) =>
    api.get<SeoLandingPage>(apiPath(`/seo-pages/public/seo-pages/${slug}/`)),

  // ── Attachments / downloadable resources ────────────────────────────────
  attachments: (params?: {
    type?: string;
    category?: string;
    level?: string;
    style?: string;
    featured?: boolean;
    limit?: number;
  }) =>
    api.get<AttachmentSummary[]>(apiPath("/cms-api/attachments/"), { params }),

  attachment: (slug: string) =>
    api.get<AttachmentSummary>(apiPath(`/cms-api/attachments/${slug}/`)),

  checkAccess: (slug: string) =>
    api.get<AccessCheckResult>(apiPath(`/cms-api/attachments/${slug}/check_access/`)),

  download: (slug: string, payload?: { email?: string; consent_marketing?: boolean; consent_newsletter?: boolean }) =>
    api.post<DownloadResult>(apiPath(`/cms-api/attachments/${slug}/download/`), payload ?? {}),

  rateAttachment: (slug: string, rating: number) =>
    api.post(apiPath(`/cms-api/attachments/${slug}/rate/`), { rating }),

  // ── Citations ────────────────────────────────────────────────────────────
  citations: (blogPostId: number) =>
    api.get<Citation[]>(apiPath("/cms-api/citations/"), { params: { blog_post: blogPostId } }),

  // ── Content graph ────────────────────────────────────────────────────────
  pillars: () =>
    api.get<ContentPillar[]>(apiPath("/cms-api/content-graph/pillars/")),

  pillarSpokes: (slug: string) =>
    api.get<BlogPostSummary[]>(apiPath(`/cms-api/content-graph/pillars/${slug}/spokes/`)),
};
