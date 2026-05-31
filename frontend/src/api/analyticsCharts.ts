import { api, apiPath } from "./client";

export interface ChartSeries {
  name: string;
  data: number[];
  type: "line" | "bar";
  stack?: string;
  yAxisIndex?: number;
}

export interface ChartSummary {
  current?: { label: string; value: number };
  previous?: { label: string; value: number };
  change_pct?: number | null;
}

export interface ComparisonData extends ChartData {
  metric: string;
  compare: string;
  current: { label: string; value: number };
  previous: { label: string; value: number };
}

export interface ChartData {
  labels: string[];
  series: ChartSeries[];
  summary: ChartSummary;
}

export interface ChartParams {
  months?: number;
  period?: "month" | "quarter";
  website_id?: number | null;
  top?: number;
}

function analyticsPath(path: string) {
  return apiPath(`/analytics/${path}`);
}

export const analyticsChartsApi = {
  revenue: (params?: ChartParams) =>
    api.get<ChartData>(analyticsPath("charts/revenue/"), { params }),

  orders: (params?: ChartParams) =>
    api.get<ChartData>(analyticsPath("charts/orders/"), { params }),

  clients: (params?: ChartParams) =>
    api.get<ChartData>(analyticsPath("charts/clients/"), { params }),

  revenueByWebsite: (params?: ChartParams) =>
    api.get<ChartData>(analyticsPath("charts/revenue-by-website/"), { params }),

  writerEarnings: (params?: ChartParams) =>
    api.get<ChartData>(analyticsPath("charts/writer-earnings/"), { params }),

  clientSpending: (params?: ChartParams) =>
    api.get<ChartData>(analyticsPath("charts/client-spending/"), { params }),

  comparison: (params: { metric?: string; compare?: "mom" | "qoq" | "yoy"; website_id?: number | null }) =>
    api.get<ComparisonData>(analyticsPath("charts/comparison/"), { params }),

  daily: (params?: { days?: number; website_id?: number | null }) =>
    api.get<ChartData & { summary: { total_revenue: number; total_orders: number; days: number } }>(
      analyticsPath("charts/daily/"), { params }
    ),
};
