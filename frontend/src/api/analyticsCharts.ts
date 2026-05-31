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
};
