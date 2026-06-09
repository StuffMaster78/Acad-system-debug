import { api } from "./client";

const BASE = "/cms-api/engagement";

export interface EngagementSummary {
  total_views: number;
  unique_views: number;
  avg_time_on_page: number;
  avg_scroll_depth: number;
  bounce_rate: number;
  thumbs_up_count: number;
  thumbs_down_count: number;
  love_count: number;
  useful_count: number;
  total_shares: number;
  engagement_score: number;
  helpfulness_ratio: number;
  // client-enriched fields
  user_reaction?: string | null;
  user_bookmarked?: boolean;
}

export type ReactionType = "thumbs_up" | "thumbs_down" | "love" | "useful";
export type SharePlatform = "twitter" | "facebook" | "linkedin" | "reddit" | "whatsapp" | "telegram" | "email" | "copy_link";

export const engagementApi = {
  /** Fetch summary by Wagtail page_id (simplest for blog posts). */
  getSummary: (pageId: number) =>
    api.get<EngagementSummary>(`${BASE}/page/`, { params: { page_id: pageId } }),

  /** Fetch summary by explicit content_type + object_id. */
  getSummaryByType: (contentTypeId: number, objectId: number) =>
    api.get<EngagementSummary>(`${BASE}/page/${contentTypeId}/${objectId}/`),

  /** Fire-and-forget page view beacon. */
  trackView: (payload: {
    content_type_id?: number;
    object_id?: number;
    page_id?: number;
    time_on_page?: number;
    scroll_depth?: number;
  }) => api.post(`${BASE}/track-view/`, payload),

  /** Toggle reaction. */
  react: (payload: {
    content_type_id: number;
    object_id: number;
    reaction_type: ReactionType;
  }) =>
    api.post<{ status: string; reaction_type: ReactionType | null }>(
      `${BASE}/react/`,
      payload
    ),

  /** Track a share click. */
  share: (payload: {
    content_type_id: number;
    object_id: number;
    platform: SharePlatform;
  }) => api.post(`${BASE}/share/`, payload),

  /** Toggle bookmark (auth required). */
  bookmark: (payload: { content_type_id: number; object_id: number }) =>
    api.post<{ status: string; bookmarked: boolean }>(
      `${BASE}/bookmark/`,
      payload
    ),
};
