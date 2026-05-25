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
