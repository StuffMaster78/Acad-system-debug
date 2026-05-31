import { api, apiPath } from "./client";

export interface WagtailPageRecord {
  id: number;
  meta?: {
    type?: string;
    detail_url?: string;
    html_url?: string;
    slug?: string;
    first_published_at?: string | null;
  };
  title: string;
  slug?: string;
  live?: boolean;
  last_published_at?: string | null;
  latest_revision_created_at?: string | null;
  [key: string]: unknown;
}

export interface WagtailPageListResponse {
  items: WagtailPageRecord[];
  meta?: {
    total_count?: number;
  };
}

export interface SeoPageRecord {
  id: number;
  website: number;
  title: string;
  slug: string;
  meta_title?: string;
  meta_description?: string;
  blocks: Array<Record<string, unknown>>;
  is_published: boolean;
  publish_date?: string | null;
  created_by?: number | null;
  updated_by?: number | null;
  created_at?: string;
  updated_at?: string;
  is_deleted?: boolean;
}

export interface SeoPagePayload {
  website: number;
  title: string;
  slug: string;
  meta_title: string;
  meta_description: string;
  blocks: Array<Record<string, unknown>>;
  is_published: boolean;
  publish_date?: string | null;
}

type ListResponse<T> = T[] | { results: T[] };

export type ContentHealthFlag =
  | "missing_meta"
  | "missing_author"
  | "stale"
  | "no_cta"
  | "no_service_route"
  | "no_citations";

export interface ContentHealthItem {
  id: number;
  source: "wagtail" | "seo_pages";
  type: "blog" | "service" | "seo";
  title: string;
  slug: string;
  edit_url: string;
  flags: ContentHealthFlag[];
  is_healthy: boolean;
}

export interface ContentHealthSummary {
  total: number;
  healthy: number;
  missing_meta: number;
  missing_author: number;
  stale: number;
  no_cta: number;
  no_service_route: number;
  no_citations: number;
}

export interface ContentHealthReport {
  summary: ContentHealthSummary;
  items: ContentHealthItem[];
}

export const adminPublishingApi = {
  wagtailPages: (params?: Record<string, unknown>) =>
    api.get<WagtailPageListResponse>(apiPath("/api/v2/pages/"), { params }),
  seoPages: (params?: Record<string, unknown>) =>
    api.get<ListResponse<SeoPageRecord>>(
      apiPath("/seo-pages/seo-pages/"),
      { params },
    ),
  createSeoPage: (payload: SeoPagePayload) =>
    api.post<SeoPageRecord>(apiPath("/seo-pages/seo-pages/"), payload),
  updateSeoPage: (id: number, payload: Partial<SeoPagePayload>) =>
    api.patch<SeoPageRecord>(apiPath(`/seo-pages/seo-pages/${id}/`), payload),
  previewSeoPage: (id: number) =>
    api.get(apiPath(`/seo-pages/seo-pages/${id}/preview/`)),
  contentHealth: () =>
    api.get<ContentHealthReport>(apiPath("/cms-api/content-health/")),

  createPageDraft: (payload: {
    type: "blog" | "service";
    title: string;
    slug: string;
    meta_description?: string;
    primary_keyword?: string;
    website_id?: number | null;
  }) =>
    api.post<{ page_id: number; edit_url: string }>(
      apiPath("/cms-api/pages/create-draft/"),
      payload,
    ),
};
