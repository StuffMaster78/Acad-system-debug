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
};
