import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { adminOpsApi } from "@/api/adminOps";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import type {
  AdminOpsMetric,
  CompressionStats,
  DuplicateGroup,
  DuplicateStats,
  PerformanceStats,
  RateLimitStats,
  RateLimitTopResponse,
  SlowEndpointResponse,
  UnifiedSearchResultGroup,
} from "@/types/adminOps";

function numberValue(value: unknown) {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function previewDuplicates(): DuplicateGroup[] {
  return [
    {
      user_ids: [101, 204],
      confidence: "high",
      match_count: 3,
      detection_types: ["email_pattern", "device_overlap", "payment_fingerprint"],
      signals: { shared_ip: "3 sessions", matching_device: true, email_similarity: "84%" },
      websites: [{ id: 1, name: "WritePro Global" }, { id: 2, name: "EssayDesk" }],
      users: [
        {
          id: 101,
          username: "nadia.m",
          email: "nadia@example.com",
          role: "client",
          website: { id: 1, name: "WritePro Global" },
          is_active: true,
        },
        {
          id: 204,
          username: "risk.client",
          email: "risk@example.com",
          role: "client",
          website: { id: 2, name: "EssayDesk" },
          is_active: false,
          is_suspended: true,
        },
      ],
    },
  ];
}

export const useAdminOpsStore = defineStore("admin-ops", () => {
  const searchQuery = ref("nadia");
  const searchTypes = ref("users,orders,payments,messages");
  const searchResults = ref<UnifiedSearchResultGroup>({
    orders: [],
    users: [],
    payments: [],
    messages: [],
    total_results: 0,
  });
  const duplicates = ref<DuplicateGroup[]>([]);
  const duplicateStats = ref<DuplicateStats>({});
  const rateLimitStats = ref<RateLimitStats>({});
  const topEndpoints = ref<RateLimitTopResponse["endpoints"]>([]);
  const topUsers = ref<RateLimitTopResponse["users"]>([]);
  const topIps = ref<RateLimitTopResponse["ips"]>([]);
  const performanceStats = ref<PerformanceStats>({});
  const slowEndpoints = ref<Array<Record<string, unknown>>>([]);
  const highQueryEndpoints = ref<Array<Record<string, unknown>>>([]);
  const compressionStats = ref<CompressionStats>({});
  const exportForm = ref({
    kind: "orders" as "orders" | "payments" | "users" | "financial-report",
    format: "csv" as "csv" | "xlsx",
    date_from: "",
    date_to: "",
    role: "",
    status: "",
  });
  const isLoading = ref(false);
  const isSearching = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const totalSearchResults = computed(() =>
    searchResults.value.total_results ??
    ["orders", "users", "payments", "messages"].reduce((sum, key) => {
      const rows = searchResults.value[key as keyof UnifiedSearchResultGroup];
      return sum + (Array.isArray(rows) ? rows.length : 0);
    }, 0),
  );

  const endpointRows = computed(() =>
    Object.entries(performanceStats.value.endpoints ?? {})
      .map(([endpoint, stats]) => ({ endpoint, ...stats }))
      .sort((a, b) => numberValue(b.avg_response_time) - numberValue(a.avg_response_time))
      .slice(0, 8),
  );

  const compressionRows = computed(() =>
    Object.entries(compressionStats.value.endpoint_stats ?? {})
      .map(([endpoint, stats]) => ({ endpoint, ...stats }) as Record<string, unknown>)
      .sort((a, b) => numberValue(b.total_saved) - numberValue(a.total_saved))
      .slice(0, 6),
  );

  const metrics = computed<AdminOpsMetric[]>(() => [
    {
      label: "Search results",
      value: totalSearchResults.value,
      detail: `For query "${searchResults.value.query ?? searchQuery.value}".`,
      tone: "neutral",
    },
    {
      label: "Duplicate groups",
      value: duplicateStats.value.total?.suspected_groups ?? duplicates.value.length,
      detail: `${duplicateStats.value.total?.users_involved ?? 0} users involved in suspected matches.`,
      tone: (duplicateStats.value.total?.suspected_groups ?? duplicates.value.length) ? "risk" : "good",
    },
    {
      label: "Rate limit hits",
      value: rateLimitStats.value.total_violations ?? 0,
      detail: `${topEndpoints.value?.length ?? 0} hot endpoints visible.`,
      tone: rateLimitStats.value.total_violations ? "warn" : "neutral",
    },
    {
      label: "Compression saved",
      value: `${compressionStats.value.total_saved_mb ?? 0} MB`,
      detail: `${compressionStats.value.avg_compression_ratio ?? 0}% average compression ratio.`,
      tone: "good",
    },
  ]);

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        searchResults.value = {
          query: searchQuery.value,
          users: [{ id: 101, title: "Nadia Morgan", email: "nadia@example.com", role: "client" }],
          orders: [{ id: 1042, title: "Healthcare policy brief", status: "assigned" }],
          payments: [{ id: 77, title: "Wallet payment", amount: "240.00", status: "completed" }],
          messages: [{ id: 18, title: "Support thread", snippet: "Nadia asked about order timing." }],
          total_results: 4,
        };
        duplicates.value = previewDuplicates();
        duplicateStats.value = {
          clients: { suspected_groups: 1, users_involved: 2 },
          writers: { suspected_groups: 0, users_involved: 0 },
          total: { suspected_groups: 1, users_involved: 2 },
        };
        rateLimitStats.value = { total_violations: 18 };
        topEndpoints.value = [
          { endpoint: "/api/v1/auth/login/", violations: 8 },
          { endpoint: "/api/v1/orders/", violations: 5 },
        ];
        topUsers.value = [{ user_id: 204, violations: 6 }];
        topIps.value = [{ ip: "203.0.113.22", violations: 9 }];
        performanceStats.value = {
          endpoints: {
            "/api/v1/admin-management/user-management/": {
              total_requests: 96,
              avg_response_time: 188,
              avg_query_count: 7,
              max_response_time: 590,
              max_query_count: 16,
            },
            "/api/v1/orders/": {
              total_requests: 142,
              avg_response_time: 428,
              avg_query_count: 12,
              max_response_time: 910,
              max_query_count: 28,
            },
          },
          cache: { type: "redis", keyspace_hits: 1480, keyspace_misses: 214 },
          database: { queries_in_session: 24, time_queries: 0.42 },
        };
        slowEndpoints.value = [{ endpoint: "/api/v1/orders/", avg_response_time: 428, request_count: 142 }];
        highQueryEndpoints.value = [{ endpoint: "/api/v1/orders/", avg_query_count: 12, request_count: 142 }];
        compressionStats.value = {
          total_compressions: 260,
          avg_compression_ratio: 72.4,
          total_saved_mb: 18.6,
          endpoint_stats: {
            "/api/v1/orders/": { count: 80, total_saved: 10485760, compression_ratio: 74 },
            "/api/v1/admin-management/user-management/": { count: 45, total_saved: 3145728, compression_ratio: 69 },
          },
        };
        return;
      }

      const [
        duplicateRes,
        duplicateStatsRes,
        rateStatsRes,
        endpointRes,
        userRes,
        ipRes,
        perfStatsRes,
        slowRes,
        highQueryRes,
        compressionRes,
      ] = await Promise.allSettled([
        adminOpsApi.duplicates({ min_confidence: "low", limit: 20 }),
        adminOpsApi.duplicateStats(),
        adminOpsApi.rateLimitStats({ limit: 100 }),
        adminOpsApi.topRateLimitedEndpoints(),
        adminOpsApi.topRateLimitedUsers(),
        adminOpsApi.topRateLimitedIps(),
        adminOpsApi.performanceStats(),
        adminOpsApi.slowEndpoints(),
        adminOpsApi.highQueryEndpoints(),
        adminOpsApi.compressionStats(),
      ]);

      if (duplicateRes.status === "fulfilled") duplicates.value = duplicateRes.value.data.results;
      if (duplicateStatsRes.status === "fulfilled") duplicateStats.value = duplicateStatsRes.value.data;
      if (rateStatsRes.status === "fulfilled") rateLimitStats.value = rateStatsRes.value.data;
      if (endpointRes.status === "fulfilled") topEndpoints.value = endpointRes.value.data.endpoints ?? [];
      if (userRes.status === "fulfilled") topUsers.value = userRes.value.data.users ?? [];
      if (ipRes.status === "fulfilled") topIps.value = ipRes.value.data.ips ?? [];
      if (perfStatsRes.status === "fulfilled") performanceStats.value = perfStatsRes.value.data;
      if (slowRes.status === "fulfilled") slowEndpoints.value = slowRes.value.data.slow_endpoints ?? [];
      if (highQueryRes.status === "fulfilled") highQueryEndpoints.value = highQueryRes.value.data.high_query_endpoints ?? [];
      if (compressionRes.status === "fulfilled") compressionStats.value = compressionRes.value.data;
      await runSearch();
    } catch (caught) {
      error.value = "Unable to load operations intelligence.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function runSearch() {
    const auth = useAuthStore();
    isSearching.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        searchResults.value = {
          ...searchResults.value,
          query: searchQuery.value,
          total_results: totalSearchResults.value || 4,
        };
        return;
      }
      const { data } = await adminOpsApi.search({
        q: searchQuery.value,
        types: searchTypes.value,
        limit: 8,
      });
      searchResults.value = data;
    } finally {
      isSearching.value = false;
    }
  }

  async function clearRateLimits() {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        rateLimitStats.value = { total_violations: 0 };
        topEndpoints.value = [];
        topUsers.value = [];
        topIps.value = [];
        notice.value = "Preview rate-limit stats cleared.";
        ui.toast(notice.value, "success");
        return;
      }
      await adminOpsApi.clearRateLimitStats();
      notice.value = "Rate-limit stats cleared.";
      ui.toast(notice.value, "success");
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function downloadExport() {
    const auth = useAuthStore();
    const ui = useUiStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        notice.value = `Preview ${exportForm.value.kind} export prepared.`;
        ui.toast(notice.value, "success");
        return;
      }
      const params = {
        format: exportForm.value.format,
        date_from: exportForm.value.date_from || undefined,
        date_to: exportForm.value.date_to || undefined,
        role: exportForm.value.role || undefined,
        status: exportForm.value.status || undefined,
      };
      const { data } = await adminOpsApi.exportReport(exportForm.value.kind, params);
      const url = window.URL.createObjectURL(data);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${exportForm.value.kind}.${exportForm.value.format}`;
      anchor.click();
      window.URL.revokeObjectURL(url);
      notice.value = "Export download started.";
      ui.toast(notice.value, "success");
    } catch (caught) {
      error.value = "Unable to generate export.";
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  return {
    searchQuery,
    searchTypes,
    searchResults,
    duplicates,
    duplicateStats,
    rateLimitStats,
    topEndpoints,
    topUsers,
    topIps,
    performanceStats,
    slowEndpoints,
    highQueryEndpoints,
    compressionStats,
    compressionRows,
    endpointRows,
    exportForm,
    isLoading,
    isSearching,
    isMutating,
    error,
    notice,
    totalSearchResults,
    metrics,
    hydrate,
    runSearch,
    clearRateLimits,
    downloadExport,
  };
});
