export type AdminOpsTone = "neutral" | "good" | "warn" | "risk";

export interface AdminOpsMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: AdminOpsTone;
}

export interface UnifiedSearchResultGroup {
  orders?: Array<Record<string, unknown>>;
  users?: Array<Record<string, unknown>>;
  payments?: Array<Record<string, unknown>>;
  messages?: Array<Record<string, unknown>>;
  references?: WorkReferenceLookupMatch[];
  total_results?: number;
  query?: string;
}

export interface WorkReferenceLookupMatch {
  kind: "normal_order" | "class_order" | "special_order";
  id: number;
  reference: string;
  title: string;
  status: string;
  website_id: number | null;
  client_id: number | null;
  writer_id: number | null;
  created_at: string | null;
}

export interface WorkReferenceLookupResponse {
  reference: string;
  count: number;
  matches: WorkReferenceLookupMatch[];
}

export interface DuplicateUserSummary {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role?: string;
  website?: { id?: number | null; name?: string | null } | null;
  date_joined?: string | null;
  last_login?: string | null;
  is_active?: boolean;
  is_suspended?: boolean;
  is_blacklisted?: boolean;
}

export interface DuplicateGroup {
  user_ids: number[];
  users: DuplicateUserSummary[];
  websites?: Array<{ id?: number | null; name?: string | null }>;
  signals?: Record<string, unknown> | string[];
  detection_types?: string[];
  confidence: "low" | "medium" | "high" | string;
  match_count?: number;
}

export interface DuplicateStats {
  clients?: { suspected_groups?: number; users_involved?: number };
  writers?: { suspected_groups?: number; users_involved?: number };
  total?: { suspected_groups?: number; users_involved?: number };
}

export interface RateLimitStats {
  total_violations?: number;
  violations?: unknown[];
  [key: string]: unknown;
}

export interface RateLimitTopResponse {
  endpoints?: Array<{ endpoint: string; violations: number }>;
  users?: Array<{ user_id: number | string; violations: number }>;
  ips?: Array<{ ip: string; violations: number }>;
}

export interface PerformanceStats {
  endpoints?: Record<string, {
    total_requests?: number;
    avg_response_time?: number;
    avg_query_count?: number;
    max_response_time?: number;
    max_query_count?: number;
  }>;
  cache?: Record<string, unknown>;
  database?: Record<string, unknown>;
  timestamp?: number;
}

export interface SlowEndpointResponse {
  slow_endpoints?: Array<Record<string, unknown>>;
  high_query_endpoints?: Array<Record<string, unknown>>;
  threshold_ms?: number;
  threshold?: number;
}

export interface CompressionStats {
  total_compressions?: number;
  avg_compression_ratio?: number;
  total_bytes_saved?: number;
  total_saved_mb?: number;
  endpoint_stats?: Record<string, Record<string, unknown>>;
  settings?: Record<string, unknown>;
}
