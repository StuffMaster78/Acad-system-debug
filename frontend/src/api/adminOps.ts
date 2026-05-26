import { api, apiPath } from "./client";
import type {
  CompressionStats,
  DuplicateGroup,
  DuplicateStats,
  PerformanceStats,
  RateLimitStats,
  RateLimitTopResponse,
  SlowEndpointResponse,
  UnifiedSearchResultGroup,
} from "@/types/adminOps";

export const adminOpsApi = {
  search: (params: { q: string; types?: string; limit?: number }) =>
    api.get<UnifiedSearchResultGroup>(
      apiPath("/admin-management/unified-search/search/"),
      { params },
    ),
  duplicates: (params?: Record<string, unknown>) =>
    api.get<{ count: number; results: DuplicateGroup[] }>(
      apiPath("/admin-management/duplicate-detection/detect/"),
      { params },
    ),
  duplicateStats: () =>
    api.get<DuplicateStats>(
      apiPath("/admin-management/duplicate-detection/stats/"),
    ),
  rateLimitStats: (params?: Record<string, unknown>) =>
    api.get<RateLimitStats>(
      apiPath("/admin-management/rate-limiting/stats/"),
      { params },
    ),
  topRateLimitedEndpoints: (limit = 10) =>
    api.get<RateLimitTopResponse>(
      apiPath("/admin-management/rate-limiting/top-endpoints/"),
      { params: { limit } },
    ),
  topRateLimitedUsers: (limit = 10) =>
    api.get<RateLimitTopResponse>(
      apiPath("/admin-management/rate-limiting/top-users/"),
      { params: { limit } },
    ),
  topRateLimitedIps: (limit = 10) =>
    api.get<RateLimitTopResponse>(
      apiPath("/admin-management/rate-limiting/top-ips/"),
      { params: { limit } },
    ),
  clearRateLimitStats: () =>
    api.post(apiPath("/admin-management/rate-limiting/clear-stats/"), {}),
  performanceStats: () =>
    api.get<PerformanceStats>(
      apiPath("/admin-management/performance/stats/"),
    ),
  slowEndpoints: (threshold = 500) =>
    api.get<SlowEndpointResponse>(
      apiPath("/admin-management/performance/slow-endpoints/"),
      { params: { threshold } },
    ),
  highQueryEndpoints: (threshold = 10) =>
    api.get<SlowEndpointResponse>(
      apiPath("/admin-management/performance/high-query-endpoints/"),
      { params: { threshold } },
    ),
  compressionStats: () =>
    api.get<CompressionStats>(
      apiPath("/admin-management/compression/stats/"),
    ),
  exportReport: (kind: "orders" | "payments" | "users" | "financial-report", params: Record<string, unknown>) =>
    api.get<Blob>(
      apiPath(`/admin-management/exports/${kind}/`),
      { params, responseType: "blob" },
    ),
};
