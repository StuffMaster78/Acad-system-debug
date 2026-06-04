import { api, apiPath } from "./client";
import type { CreateReviewPayload, Review, ReviewSummary } from "@/types/reviews";

type ListResponse<T> = T[] | { results: T[]; count?: number };

export const reviewsApi = {
  // Order reviews — submit after completion, fetch existing
  submit: (orderId: number | string, payload: CreateReviewPayload) =>
    api.post<Review>(apiPath(`/orders/orders/${orderId}/review/`), payload),
  forOrder: (orderId: number | string) =>
    api.get<Review | null>(apiPath(`/orders/orders/${orderId}/review/`)),

  // Writer reviews (public listing + aggregated summary)
  forWriter: (registrationId: string, params?: Record<string, unknown>) =>
    api.get<ListResponse<Review>>(
      apiPath(`/writer-management/writers/${registrationId}/reviews/`),
      { params },
    ),
  summary: (registrationId: string) =>
    api.get<ReviewSummary>(
      apiPath(`/writer-management/writers/${registrationId}/reviews/summary/`),
    ),

  // Website review — client rates the platform
  submitWebsiteReview: (payload: { rating: number; comment?: string }) =>
    api.post<Review>(apiPath("/reviews/api/reviews/website-review/"), payload),

  // Admin moderation helpers
  list: (params?: Record<string, unknown>) =>
    api.get<ListResponse<Review>>(apiPath("/reviews/api/reviews/list/"), { params }),
  hide: (reviewId: number | string) =>
    api.post(apiPath(`/reviews/${reviewId}/hide/`), {}),
  unhide: (reviewId: number | string) =>
    api.post(apiPath(`/reviews/${reviewId}/unhide/`), {}),
};
