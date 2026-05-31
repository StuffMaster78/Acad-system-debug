import { describe, it, expect } from "vitest";
import { analyticsChartsApi } from "@/api/analyticsCharts";

describe("analyticsChartsApi", () => {
  it("exports all expected methods", () => {
    expect(typeof analyticsChartsApi.revenue).toBe("function");
    expect(typeof analyticsChartsApi.orders).toBe("function");
    expect(typeof analyticsChartsApi.clients).toBe("function");
    expect(typeof analyticsChartsApi.revenueByWebsite).toBe("function");
    expect(typeof analyticsChartsApi.writerEarnings).toBe("function");
    expect(typeof analyticsChartsApi.clientSpending).toBe("function");
    expect(typeof analyticsChartsApi.comparison).toBe("function");
  });
});
