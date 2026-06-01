import { api, apiPath } from "./client";

export type DocType =
  | "terms_of_service"
  | "privacy_policy"
  | "refund_policy"
  | "cookie_policy"
  | "acceptable_use_policy"
  | "writer_agreement"
  | "copyright_policy";

export const DOC_TYPE_LABELS: Record<DocType, string> = {
  terms_of_service: "Terms of Service",
  privacy_policy: "Privacy Policy",
  refund_policy: "Refund Policy",
  cookie_policy: "Cookie Policy",
  acceptable_use_policy: "Acceptable Use Policy",
  writer_agreement: "Writer Agreement",
  copyright_policy: "Copyright Policy",
};

export const ALL_DOC_TYPES: DocType[] = Object.keys(DOC_TYPE_LABELS) as DocType[];

export interface LegalDocument {
  id: number;
  doc_type: DocType;
  doc_type_display: string;
  title: string;
  content: string;
  version: string;
  effective_date: string;
  is_active?: boolean;
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
  is_active?: boolean;
  article_count: number;
}

export interface HelpArticleSummary {
  id: number;
  title: string;
  slug: string;
  summary: string;
  audience: string;
  is_featured: boolean;
  is_published?: boolean;
  category?: number;
  category_slug: string;
  category_title: string;
  updated_at: string;
}

export interface HelpArticle extends HelpArticleSummary {
  content: string;
}

export const legalApi = {
  // ── Public read ────────────────────────────────────────────────────────────
  list: () =>
    api.get<LegalDocument[]>(apiPath("/legal/")),

  document: (docType: DocType) =>
    api.get<LegalDocument>(apiPath(`/legal/${docType}/`)),

  agree: (docType: DocType) =>
    api.post<{ agreed: boolean; version: string; new: boolean }>(
      apiPath(`/legal/${docType}/agree/`),
      {},
    ),

  categories: () =>
    api.get<HelpCategory[]>(apiPath("/legal/help/categories/")),

  articles: (params?: { category?: string; featured?: boolean }) =>
    api.get<HelpArticleSummary[]>(apiPath("/legal/help/articles/"), { params }),

  article: (slug: string) =>
    api.get<HelpArticle>(apiPath(`/legal/help/articles/${slug}/`)),

  // ── Admin CRUD (staff only) ────────────────────────────────────────────────
  admin: {
    // Legal documents
    listDocuments: (params?: { doc_type?: string; website_id?: number }) =>
      api.get<LegalDocument[]>(apiPath("/legal/admin/documents/"), { params }),
    createDocument: (payload: Partial<LegalDocument>) =>
      api.post<LegalDocument>(apiPath("/legal/admin/documents/"), payload),
    updateDocument: (id: number, payload: Partial<LegalDocument>) =>
      api.put<LegalDocument>(apiPath(`/legal/admin/documents/${id}/`), payload),
    deleteDocument: (id: number) =>
      api.delete(apiPath(`/legal/admin/documents/${id}/`)),
    activateDocument: (id: number) =>
      api.post<LegalDocument>(apiPath(`/legal/admin/documents/${id}/activate/`), {}),

    // Help categories
    listCategories: () =>
      api.get<HelpCategory[]>(apiPath("/legal/admin/help/categories/")),
    createCategory: (payload: Partial<HelpCategory>) =>
      api.post<HelpCategory>(apiPath("/legal/admin/help/categories/"), payload),
    updateCategory: (id: number, payload: Partial<HelpCategory>) =>
      api.put<HelpCategory>(apiPath(`/legal/admin/help/categories/${id}/`), payload),
    deleteCategory: (id: number) =>
      api.delete(apiPath(`/legal/admin/help/categories/${id}/`)),

    // Help articles
    listArticles: (params?: { category?: number }) =>
      api.get<HelpArticle[]>(apiPath("/legal/admin/help/articles/"), { params }),
    createArticle: (payload: Partial<HelpArticle>) =>
      api.post<HelpArticle>(apiPath("/legal/admin/help/articles/"), payload),
    updateArticle: (id: number, payload: Partial<HelpArticle>) =>
      api.put<HelpArticle>(apiPath(`/legal/admin/help/articles/${id}/`), payload),
    deleteArticle: (id: number) =>
      api.delete(apiPath(`/legal/admin/help/articles/${id}/`)),
  },
};
