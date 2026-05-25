export type AdminWorkKind = "order" | "special_order" | "class_order";

export type AdminWorkTone = "neutral" | "success" | "warning" | "danger";

export interface AdminWorkItem {
  id: number;
  kind: AdminWorkKind;
  reference: string;
  title: string;
  status: string;
  paymentStatus?: string;
  website: string;
  client: string;
  assignedWriter: string;
  deadline: string | null;
  createdAt: string | null;
  amount?: string;
  currency?: string;
  priority?: string;
  subject?: string;
  notes?: string;
  isPaused?: boolean;
}

export interface AdminWorkSummary {
  total: number;
  normalOrders: number;
  specialOrders: number;
  classOrders: number;
  unassigned: number;
  atRisk: number;
}

export interface AdminWorkMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}
