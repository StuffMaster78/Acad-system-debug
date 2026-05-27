import { api, apiPath } from "./client";
import type { CreateReviewPayload, Review, ReviewSummary } from "@/types/reviews";

type ListResponse<T> = T[] | { results: T[]; count?: number };

export const reviewsApi = {
  submit: (orderId: number | string, payload: CreateReviewPayload) =>
    api.post<Review>(apiPath(`/orders/${orderId}/review/`), payload),
  forOrder: (orderId: number | string) =>
    api.get<Review>(apiPath(`/orders/${orderId}/review/`)),
  forWriter: (registrationId: string, params?: Record<string, unknown>) =>
    api.get<ListResponse<Review>>(
      apiPath(`/writer-management/writers/${registrationId}/reviews/`),
      { params },
    ),
  summary: (registrationId: string) =>
    api.get<ReviewSummary>(
      apiPath(`/writer-management/writers/${registrationId}/reviews/summary/`),
    ),
  list: (params?: Record<string, unknown>) =>
    api.get<ListResponse<Review>>(apiPath("/reviews/"), { params }),
  hide: (reviewId: number | string) =>
    api.post(apiPath(`/reviews/${reviewId}/hide/`), {}),
  unhide: (reviewId: number | string) =>
    api.post(apiPath(`/reviews/${reviewId}/unhide/`), {}),
};
