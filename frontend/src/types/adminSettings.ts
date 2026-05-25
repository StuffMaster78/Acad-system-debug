export interface AdminSettingsMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}

export interface AdminConfigGroup {
  key: string;
  label: string;
  description: string;
  count: number;
  items: Array<Record<string, unknown>>;
}
