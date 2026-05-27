import { computed, reactive, ref } from "vue";
import { defineStore } from "pinia";
import { reviewsApi } from "@/api/reviews";
import { useAuthStore } from "@/stores/auth";
import type { CreateReviewPayload, Review, ReviewSummary } from "@/types/reviews";

function normalizeList<T>(data: T[] | { results: T[]; count?: number }): T[] {
  return Array.isArray(data) ? data : data.results;
}

const PREVIEW_REVIEWS: Review[] = [
  {
    id: 1,
    order_id: 4610,
    order_topic: "Reflective essay on clinical leadership",
    writer_id: 22,
    writer_registration_id: "WRT-0022",
    writer_pen_name: "Amina Writer",
    client_id: 42,
    client_username: "client.preview",
    rating: 5,
    title: "Exceptional quality and fast delivery",
    body: "The essay was well-structured, cited correctly in APA 7, and delivered two days early. Will definitely request this writer again.",
    is_public: true,
    is_hidden: false,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString(),
  },
  {
    id: 2,
    order_id: 4520,
    order_topic: "Business analytics report — subscription retention",
    writer_id: 23,
    writer_registration_id: "WRT-0023",
    writer_pen_name: "Jon Writer",
    client_id: 42,
    client_username: "client.preview",
    rating: 3,
    title: "Decent but needed revisions",
    body: "The content was on-topic but the formatting had issues and some citations were missing. Revision was completed promptly.",
    is_public: true,
    is_hidden: false,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 25).toISOString(),
  },
  {
    id: 3,
    order_id: 4780,
    order_topic: "Literature review on ethical AI",
    writer_id: 22,
    writer_registration_id: "WRT-0022",
    writer_pen_name: "Amina Writer",
    client_id: 67,
    client_username: "client.delta",
    rating: 4,
    title: "Thorough and well-researched",
    body: "Strong literature coverage and good academic tone. Minor formatting tweaks needed but overall an excellent piece.",
    is_public: true,
    is_hidden: false,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 8).toISOString(),
  },
];

const PREVIEW_SUMMARY: Record<string, ReviewSummary> = {
  "WRT-0022": {
    writer_registration_id: "WRT-0022",
    writer_pen_name: "Amina Writer",
    total_reviews: 24,
    average_rating: 4.8,
    rating_distribution: { "1": 0, "2": 1, "3": 1, "4": 4, "5": 18 },
  },
  "WRT-0023": {
    writer_registration_id: "WRT-0023",
    writer_pen_name: "Jon Writer",
    total_reviews: 11,
    average_rating: 3.6,
    rating_distribution: { "1": 1, "2": 1, "3": 4, "4": 4, "5": 1 },
  },
};

export const useReviewsStore = defineStore("reviews", () => {
  const writerReviews = ref<Review[]>([]);
  const writerSummary = ref<ReviewSummary | null>(null);
  const allReviews = ref<Review[]>([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref("");
  const notice = ref("");
  const query = ref("");
  const ratingFilter = ref<number | null>(null);

  const submitForm = reactive<CreateReviewPayload & { orderId: number | string }>({
    orderId: "",
    rating: 0,
    title: "",
    body: "",
    is_public: true,
  });

  const showSubmitForm = ref(false);
  const submittedOrderIds = ref<Set<string>>(new Set());

  const filteredAll = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return allReviews.value.filter((r) => {
      if (ratingFilter.value !== null && r.rating !== ratingFilter.value) return false;
      if (!needle) return true;
      return [r.order_topic, r.writer_pen_name, r.client_username, r.title, r.body]
        .some((v) => String(v ?? "").toLowerCase().includes(needle));
    });
  });

  const averageRating = computed(() => {
    if (!writerReviews.value.length) return 0;
    return writerReviews.value.reduce((s, r) => s + r.rating, 0) / writerReviews.value.length;
  });

  async function loadWriterReviews(registrationId: string) {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        writerReviews.value = PREVIEW_REVIEWS.filter(
          (r) => r.writer_registration_id === registrationId,
        );
        writerSummary.value = PREVIEW_SUMMARY[registrationId] ?? null;
        return;
      }
      const [reviewsRes, summaryRes] = await Promise.allSettled([
        reviewsApi.forWriter(registrationId),
        reviewsApi.summary(registrationId),
      ]);
      if (reviewsRes.status === "fulfilled") writerReviews.value = normalizeList(reviewsRes.value.data);
      if (summaryRes.status === "fulfilled") writerSummary.value = summaryRes.value.data;
    } catch {
      error.value = "Unable to load writer reviews.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadAll() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        allReviews.value = PREVIEW_REVIEWS;
        return;
      }
      const { data } = await reviewsApi.list();
      allReviews.value = normalizeList(data);
    } catch {
      error.value = "Unable to load reviews.";
    } finally {
      isLoading.value = false;
    }
  }

  async function submitReview() {
    const auth = useAuthStore();
    if (!submitForm.orderId || submitForm.rating < 1 || submitForm.rating > 5) {
      error.value = "A star rating (1–5) is required.";
      return;
    }
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        const newReview: Review = {
          id: Date.now(),
          order_id: Number(submitForm.orderId),
          order_topic: `Order #${submitForm.orderId}`,
          writer_id: 22,
          writer_registration_id: "WRT-0022",
          writer_pen_name: "Assigned writer",
          client_id: 42,
          client_username: "client.preview",
          rating: submitForm.rating,
          title: submitForm.title || null,
          body: submitForm.body || null,
          is_public: submitForm.is_public ?? true,
          is_hidden: false,
          created_at: new Date().toISOString(),
        };
        writerReviews.value = [newReview, ...writerReviews.value];
        allReviews.value = [newReview, ...allReviews.value];
        submittedOrderIds.value.add(String(submitForm.orderId));
        showSubmitForm.value = false;
        notice.value = "Preview review submitted.";
        resetForm();
        return newReview;
      }
      const { data } = await reviewsApi.submit(submitForm.orderId, {
        rating: submitForm.rating,
        title: submitForm.title || undefined,
        body: submitForm.body || undefined,
        is_public: submitForm.is_public,
      });
      submittedOrderIds.value.add(String(submitForm.orderId));
      showSubmitForm.value = false;
      notice.value = "Review submitted. Thank you.";
      resetForm();
      return data;
    } catch {
      error.value = "Unable to submit review.";
    } finally {
      isSaving.value = false;
    }
  }

  async function toggleHide(review: Review) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        const patch = (r: Review) => r.id === review.id ? { ...r, is_hidden: !r.is_hidden } : r;
        allReviews.value = allReviews.value.map(patch);
        writerReviews.value = writerReviews.value.map(patch);
        return;
      }
      if (review.is_hidden) await reviewsApi.unhide(review.id);
      else await reviewsApi.hide(review.id);
      const patch = (r: Review) => r.id === review.id ? { ...r, is_hidden: !r.is_hidden } : r;
      allReviews.value = allReviews.value.map(patch);
      writerReviews.value = writerReviews.value.map(patch);
    } catch {
      error.value = "Unable to update review visibility.";
    } finally {
      isSaving.value = false;
    }
  }

  function openSubmitForm(orderId: number | string) {
    submitForm.orderId = orderId;
    submitForm.rating = 0;
    submitForm.title = "";
    submitForm.body = "";
    submitForm.is_public = true;
    error.value = "";
    showSubmitForm.value = true;
  }

  function resetForm() {
    submitForm.orderId = "";
    submitForm.rating = 0;
    submitForm.title = "";
    submitForm.body = "";
    submitForm.is_public = true;
  }

  return {
    writerReviews,
    writerSummary,
    allReviews,
    isLoading,
    isSaving,
    error,
    notice,
    query,
    ratingFilter,
    submitForm,
    showSubmitForm,
    submittedOrderIds,
    filteredAll,
    averageRating,
    loadWriterReviews,
    loadAll,
    submitReview,
    toggleHide,
    openSubmitForm,
  };
});
