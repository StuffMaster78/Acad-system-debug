import { api, apiPath } from "./client";

export type DocType =
  | "terms_of_service"
  | "privacy_policy"
  | "refund_policy"
  | "cookie_policy"
  | "acceptable_use_policy"
  | "writer_agreement"
  | "copyright_policy";

export interface LegalDocument {
  id: number;
  doc_type: DocType;
  doc_type_display: string;
  title: string;
  content: string;
  version: string;
  effective_date: string;
  requires_re_acceptance: boolean;
}

export interface HelpCategory {
  id: number;
  title: string;
  slug: string;
  description: string;
  icon: string;
  audience: string;
  order: number;
  article_count: number;
}

export interface HelpArticleSummary {
  id: number;
  title: string;
  slug: string;
  summary: string;
  audience: string;
  is_featured: boolean;
  category_slug: string;
  category_title: string;
  updated_at: string;
}

export interface HelpArticle extends HelpArticleSummary {
  content: string;
}

export const legalApi = {
  // Legal documents
  list: () =>
    api.get<LegalDocument[]>(apiPath("/legal/")),

  document: (docType: DocType) =>
    api.get<LegalDocument>(apiPath(`/legal/${docType}/`)),

  agree: (docType: DocType) =>
    api.post<{ agreed: boolean; version: string; new: boolean }>(
      apiPath(`/legal/${docType}/agree/`),
      {},
    ),

  // Help center
  categories: () =>
    api.get<HelpCategory[]>(apiPath("/legal/help/categories/")),

  articles: (params?: { category?: string; featured?: boolean }) =>
    api.get<HelpArticleSummary[]>(apiPath("/legal/help/articles/"), { params }),

  article: (slug: string) =>
    api.get<HelpArticle>(apiPath(`/legal/help/articles/${slug}/`)),
};
