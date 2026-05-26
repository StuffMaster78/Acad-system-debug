export interface GrowthMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}

export interface GrowthRecord {
  id: number | string;
  name: string;
  status: string;
  category: string;
  value?: string | number;
  startsAt?: string | null;
  endsAt?: string | null;
  owner?: string;
  source: "discounts" | "campaigns" | "referrals" | "loyalty" | "holidays";
  raw?: Record<string, unknown>;
}

export interface GrowthLane {
  key: "discounts" | "referrals" | "loyalty" | "holidays";
  label: string;
  description: string;
  endpoint: string;
  records: GrowthRecord[];
}

export interface GrowthWorkflowStep {
  label: string;
  detail: string;
  owner: string;
}

export type DiscountAudienceMode = "all" | "clients";
