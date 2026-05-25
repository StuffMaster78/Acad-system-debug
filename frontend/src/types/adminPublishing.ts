export type PublishingContentType = "blog" | "service" | "seo";

export interface PublishingItem {
  id: number;
  type: PublishingContentType;
  title: string;
  slug: string;
  status: string;
  source: "wagtail" | "seo_pages";
  updatedAt: string | null;
  publishedAt: string | null;
  url?: string;
  summary?: string;
}

export interface PublishingMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}
