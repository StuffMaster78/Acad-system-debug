export type PublishingContentType = "blog" | "service" | "seo";

export interface PublishingItem {
  id: number | string;
  type: PublishingContentType;
  title: string;
  slug: string;
  status: string;
  source: "wagtail" | "seo_pages";
  updatedAt: string | null;
  publishedAt: string | null;
  url?: string;
  summary?: string;
  keyword?: string;
  ownerRole?: string;
}

export interface PublishingMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}

export interface PublishingFlowStep {
  label: string;
  detail: string;
  owner: string;
}

export interface PublishingRoleResponsibility {
  role: "superadmin" | "admin" | "editor" | "support";
  label: string;
  scope: string;
  actions: string[];
}

export interface PublishingAdminLink {
  label: string;
  href: string;
  detail: string;
  owner: string;
}
