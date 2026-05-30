import { api, apiPath } from "./client";

const base = (path: string) => apiPath(`/reputation${path}`);

export interface WriterSnapshot {
  writer_id: string;
  rating: string;
  review_count: number;
  verified_review_count: number;
  trust_score: string;
  metadata: Record<string, unknown>;
  updated_at: string | null;
}

export interface WebsiteSnapshot {
  website_id: string;
  rating: string;
  review_count: number;
  updated_at: string | null;
}

export interface LeaderboardEntry {
  rank: number;
  writer_id: string;
  rating: string;
  review_count: number;
  trust_score: string;
}

export interface WriterRank {
  writer_id: string;
  rank: number | null;
  percentile: string | null;
}

export interface LeaderboardResponse {
  results: LeaderboardEntry[];
  count: number;
}

export const reputationApi = {
  leaderboard: (limit = 50) =>
    api.get<LeaderboardResponse>(base("/leaderboard/"), { params: { limit } }),

  writerSnapshot: (writerId: string) =>
    api.get<WriterSnapshot>(base(`/writers/${writerId}/`)),

  writerRank: (writerId: string) =>
    api.get<WriterRank>(base(`/writers/${writerId}/rank/`)),

  websiteSnapshot: (websiteId: string) =>
    api.get<WebsiteSnapshot>(base(`/websites/${websiteId}/`)),
};
