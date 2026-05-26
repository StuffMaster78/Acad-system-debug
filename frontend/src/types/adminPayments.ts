export interface AdminPaymentMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}

export interface AdminPaymentFeedItem {
  id: number | string;
  source: "client" | "writer" | "refund" | "wallet";
  title: string;
  subtitle: string;
  amount: string | number;
  status: string;
  date?: string | null;
}

export type FinanceOpsSource = "refund" | "dispute" | "milestone" | "deposit" | "tip";

export interface FinanceOpsItem {
  id: number | string;
  source: FinanceOpsSource;
  title: string;
  subtitle: string;
  amount?: string | number;
  status: string;
  date?: string | null;
  meta?: Record<string, unknown>;
}

export interface FinanceOpsSummary {
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}
