import { api, apiPath } from "./client";

const CMS = (path: string) =>
  `/cms-api/newsletters${path}`;

export interface SubscriberCategory {
  id: number;
  name: string;
  slug: string;
}

export interface Subscriber {
  id: number;
  email: string;
  is_active: boolean;
  frequency: "weekly" | "monthly" | "instant";
  source: string;
  source_detail: string;
  categories: SubscriberCategory[];
  consent_marketing: boolean;
  open_count: number;
  click_count: number;
  last_opened_at: string | null;
  last_clicked_at: string | null;
  unsubscribed_at: string | null;
  unsubscribe_reason: string;
  created_at: string;
}

export interface NewsletterAnalytics {
  sent_count: number;
  delivered_count: number;
  open_count: number;
  open_rate: number;
  click_count: number;
  click_rate: number;
  bounce_count: number;
  bounce_rate: number;
  unsubscribe_count: number;
  conversion_count: number;
  conversion_revenue: string;
  winning_subject: string | null;
}

export interface NewsletterSummary {
  id: number;
  title: string;
  subject_line: string;
  preview_text: string;
  status: "draft" | "scheduled" | "sending" | "sent" | "failed";
  scheduled_send_date: string | null;
  sent_at: string | null;
  sender_name: string;
  sender_email: string;
  created_at: string;
  analytics: NewsletterAnalytics | null;
}

export interface NewsletterDetail extends NewsletterSummary {
  subject_line_b: string;
  ab_split_percentage: number;
  category: SubscriberCategory | null;
  created_by_name: string | null;
  updated_at: string;
}

export interface SubscriberStats {
  total: number;
  active: number;
  inactive: number;
  by_source: Record<string, number>;
  by_frequency: Record<string, number>;
}

interface PagedResponse<T> {
  count: number;
  page: number;
  page_size: number;
  results: T[];
}

export const adminNewslettersApi = {
  // Stats overview
  stats: () =>
    api.get<SubscriberStats>(CMS("/stats/")),

  // Subscribers
  subscribers: (params?: Record<string, unknown>) =>
    api.get<PagedResponse<Subscriber>>(CMS("/admin/subscribers/"), { params }),

  deactivateSubscriber: (id: number) =>
    api.post<{ detail: string }>(CMS(`/admin/subscribers/${id}/deactivate/`)),

  reactivateSubscriber: (id: number) =>
    api.post<{ detail: string }>(CMS(`/admin/subscribers/${id}/reactivate/`)),

  // Newsletters
  newsletters: (params?: Record<string, unknown>) =>
    api.get<PagedResponse<NewsletterSummary>>(CMS("/admin/newsletters/"), { params }),

  newsletterDetail: (id: number) =>
    api.get<NewsletterDetail>(CMS(`/admin/newsletters/${id}/`)),

  // Categories
  categories: () =>
    api.get<SubscriberCategory[]>(CMS("/admin/categories/")),

  createCategory: (name: string) =>
    api.post<SubscriberCategory>(CMS("/admin/categories/"), { name }),
};
