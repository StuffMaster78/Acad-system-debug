import { api, apiPath } from "./client";

type PageResponse<T> = { count: number; next: string | null; previous: string | null; results: T[] } | T[];

const base = (path: string) => apiPath(`/writer-compensation${path}`);

// ── Interfaces ──────────────────────────────────────────────────────────────

export interface LeaderboardEntry {
  writer_id: string;
  writer_name: string;
  rating: string;
  review_count: number;
  percentile_rank: string;
  trust_score: string;
  leaderboard_position: number;
  completed_orders: number;
  badges: string[];
}

export interface RewardRule {
  id: number;
  website: number;
  name: string;
  slug: string;
  description: string | null;
  rule_type: string;
  reward_type: string;
  minimum_avg_rating: string | null;
  minimum_review_count: number | null;
  minimum_percentile_rank: string | null;
  minimum_trust_score: string | null;
  minimum_completed_orders: number | null;
  maximum_lateness_rate: string | null;
  maximum_dispute_rate: string | null;
  reward_amount: string;
  trust_score_bonus: string | null;
  badge_name: string | null;
  priority_boost_multiplier: string | null;
  cooldown_days: number | null;
  max_rewards_per_period: number | null;
  is_active: boolean;
  is_repeatable: boolean;
  created_at: string;
  updated_at: string;
}

export interface RewardAnalyticsOverview {
  total_rewards: number;
  issued_rewards: number;
  revoked_rewards: number;
  total_reward_amount: string;
  average_reward_amount: string;
  top_reward_rules: { reward_rule__name: string; total: number }[];
  top_writers: { writer__id: number; writer__display_name: string; total_rewards: number; total_amount: string }[];
}

export interface RewardMetrics {
  [key: string]: unknown;
}

export interface ReconciliationReport {
  id: number;
  website: number;
  payout_batch: number;
  total_ledger_amount: string;
  total_payout_amount: string;
  total_cleared_amount: string;
  mismatch_amount: string;
  status: string;
  created_at: string;
}

// ── API ─────────────────────────────────────────────────────────────────────

export const adminRewardsApi = {
  // ── Leaderboard ────────────────────────────────────────────────────────────
  leaderboard: (limit = 100) =>
    api.get<LeaderboardEntry[]>(base("/rewards/leaderboard/"), { params: { limit } }),

  // ── Reward rules ───────────────────────────────────────────────────────────
  rules: (websiteId?: number) =>
    api.get<PageResponse<RewardRule>>(base("/rewards/rules/"), {
      params: websiteId ? { website_id: websiteId } : undefined,
    }),

  // ── Analytics & metrics ───────────────────────────────────────────────────
  analyticsOverview: (websiteId?: number) =>
    api.get<RewardAnalyticsOverview>(base("/rewards/analytics/"), {
      params: websiteId ? { website_id: websiteId } : undefined,
    }),
  metrics: (websiteId?: number) =>
    api.get<RewardMetrics>(base("/rewards/metrics/"), {
      params: websiteId ? { website_id: websiteId } : undefined,
    }),

  // ── Reconciliation ─────────────────────────────────────────────────────────
  reconciliationReports: () =>
    api.get<PageResponse<ReconciliationReport>>(base("/reconciliation/")),
  runReconciliation: (payload: {
    website_id: number;
    payout_batch_id: number;
    ledger_total: string;
    payout_total: string;
    cleared_total: string;
  }) => api.post<ReconciliationReport>(base("/reconciliation/run/"), payload),
};
