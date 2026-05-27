export interface Review {
  id: number;
  order_id: number;
  order_topic: string;
  writer_id: number;
  writer_registration_id: string;
  writer_pen_name: string;
  client_id: number;
  client_username: string;
  rating: number;
  title?: string | null;
  body?: string | null;
  is_public: boolean;
  is_hidden: boolean;
  created_at: string;
}

export interface ReviewSummary {
  writer_registration_id: string;
  writer_pen_name: string;
  total_reviews: number;
  average_rating: number;
  rating_distribution: Record<string, number>;
}

export interface CreateReviewPayload {
  rating: number;
  title?: string;
  body?: string;
  is_public?: boolean;
}
