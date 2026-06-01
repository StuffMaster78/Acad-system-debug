<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  AlertTriangle,
  ArrowLeft,
  Award,
  CheckCircle2,
  Clock,
  MessageSquare,
  ShieldAlert,
  Star,
  UserCircle,
  XCircle,
} from "@lucide/vue";
import StarRating from "@/components/ui/StarRating.vue";
import { useAdminWritersStore } from "@/stores/adminWriters";
import { useReviewsStore } from "@/stores/reviews";

const route = useRoute();
const router = useRouter();
const writerStore = useAdminWritersStore();
const reviewStore = useReviewsStore();

const activeTab = ref<"overview" | "reviews" | "discipline">("overview");
const registrationId = route.params.id as string;
const localLoading = ref(true);

const tabs = [
  { key: "overview", label: "Overview" },
  { key: "reviews", label: "Reviews" },
  { key: "discipline", label: "Discipline" },
] as const;

onMounted(async () => {
  localLoading.value = true;
  await writerStore.selectWriter(registrationId);
  await reviewStore.loadWriterReviews(registrationId);
  localLoading.value = false;
});

const writer = computed(() => writerStore.selectedWriter);
const discipline = computed(() => writerStore.discipline);

function formatDate(iso?: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function disciplineColor(state: boolean) {
  return state ? "text-rose-600" : "text-emerald-600";
}

function ratingBarWidth(count: number) {
  const max = Math.max(...Object.values(reviewStore.writerSummary?.rating_distribution ?? {}), 1);
  return `${Math.max((count / max) * 100, 2).toFixed(0)}%`;
}

const levelColor = computed(() => {
  const level = (writer.value?.level_name ?? "").toLowerCase();
  if (level.includes("senior") || level.includes("expert")) return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (level.includes("standard")) return "bg-blue-50 text-blue-700 border-blue-200";
  return "bg-slate-100 text-graphite border-slate-200";
});
</script>

<template>
  <div class="space-y-4">
    <!-- Back -->
    <button
      class="inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink transition-colors"
      type="button"
      @click="router.push('/admin/writers')"
    >
      <ArrowLeft class="h-4 w-4" />
      Writers
    </button>

    <!-- Loading -->
    <div v-if="localLoading" class="space-y-4">
      <div class="h-24 rounded-xl bg-slate-100 animate-pulse" />
      <div class="h-48 rounded-xl bg-slate-100 animate-pulse" />
    </div>

    <template v-else-if="writer">
      <!-- Header card -->
      <div class="rounded-lg border border-slate-200 bg-white p-6">
        <div class="flex items-start gap-4">
          <div class="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 shrink-0">
            <UserCircle class="h-8 w-8 text-graphite" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h1 class="text-xl font-bold text-ink">{{ writer.pen_name || writer.full_name }}</h1>
              <span
                v-if="writer.level_name"
                class="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
                :class="levelColor"
              >
                <Award class="h-3 w-3" />
                {{ writer.level_name }}
              </span>
              <span
                v-if="writer.is_suspended"
                class="rounded-full bg-rose-50 border border-rose-200 px-2 py-0.5 text-xs font-medium text-rose-700"
              >
                Suspended
              </span>
              <span
                v-else-if="writer.is_on_probation"
                class="rounded-full bg-amber-50 border border-amber-200 px-2 py-0.5 text-xs font-medium text-amber-700"
              >
                On probation
              </span>
              <span
                v-else-if="writer.is_verified"
                class="rounded-full bg-emerald-50 border border-emerald-200 px-2 py-0.5 text-xs font-medium text-emerald-700"
              >
                Verified
              </span>
            </div>
            <p class="text-sm text-graphite mt-0.5">{{ writer.email }}</p>
            <div class="mt-1 flex items-center gap-3 text-xs text-graphite">
              <span class="font-mono">{{ writer.registration_id }}</span>
              <span v-if="writer.timezone">{{ writer.timezone }}</span>
              <span v-if="writer.years_of_experience">{{ writer.years_of_experience }} yrs experience</span>
            </div>
          </div>
          <div v-if="reviewStore.writerSummary" class="text-right shrink-0">
            <StarRating :rating="reviewStore.writerSummary.average_rating" size="md" />
            <p class="text-xs text-graphite mt-1">{{ reviewStore.writerSummary.total_reviews }} reviews</p>
          </div>
        </div>

        <!-- Quick stats -->
        <div class="mt-5 grid grid-cols-4 gap-4 border-t border-slate-100 pt-4">
          <div class="text-center">
            <p class="text-xs text-graphite">Active orders</p>
            <p class="text-lg font-bold text-ink">{{ writer.active_orders_count ?? 0 }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-graphite">Joined</p>
            <p class="text-sm font-semibold text-ink">{{ formatDate(writer.joined_at) }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-graphite">Accepting orders</p>
            <p class="text-sm font-semibold" :class="writer.is_accepting_orders ? 'text-emerald-600' : 'text-graphite'">
              {{ writer.is_accepting_orders ? "Yes" : "No" }}
            </p>
          </div>
          <div class="text-center">
            <p class="text-xs text-graphite">Status</p>
            <p class="text-sm font-semibold text-ink capitalize">{{ writer.onboarding_status }}</p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="flex-1 rounded-lg py-2 text-xs font-semibold transition-colors"
          :class="activeTab === tab.key ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
          type="button"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
          <span
            v-if="tab.key === 'reviews' && reviewStore.writerSummary"
            class="ml-1.5 rounded-full bg-slate-200 px-1.5 py-0.5 text-xs"
          >
            {{ reviewStore.writerSummary.total_reviews }}
          </span>
        </button>
      </div>

      <!-- Overview tab -->
      <div v-if="activeTab === 'overview'" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <!-- Writer info -->
          <div class="rounded-lg border border-slate-200 bg-white p-5">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Profile</p>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-graphite">Full name</span>
                <span class="font-medium text-ink">{{ writer.full_name || "—" }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-graphite">Verification</span>
                <span class="font-medium" :class="writer.is_verified ? 'text-emerald-600' : 'text-amber-600'">
                  {{ writer.verification_status }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-graphite">Onboarding</span>
                <span class="font-medium text-ink capitalize">{{ writer.onboarding_status.replace(/_/g, " ") }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-graphite">Timezone</span>
                <span class="font-medium text-ink">{{ writer.timezone || "—" }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-graphite">Experience</span>
                <span class="font-medium text-ink">{{ writer.years_of_experience ? `${writer.years_of_experience} years` : "—" }}</span>
              </div>
            </div>
          </div>

          <!-- Capacity -->
          <div class="rounded-lg border border-slate-200 bg-white p-5">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Capacity</p>
            <div class="space-y-2 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-graphite">Can take orders</span>
                <component
                  :is="writer.can_take_orders ? CheckCircle2 : XCircle"
                  class="h-4 w-4"
                  :class="writer.can_take_orders ? 'text-emerald-500' : 'text-rose-400'"
                />
              </div>
              <div class="flex items-center justify-between">
                <span class="text-graphite">Accepting orders</span>
                <component
                  :is="writer.is_accepting_orders ? CheckCircle2 : Clock"
                  class="h-4 w-4"
                  :class="writer.is_accepting_orders ? 'text-emerald-500' : 'text-graphite'"
                />
              </div>
              <div class="flex justify-between">
                <span class="text-graphite">Active orders</span>
                <span class="font-semibold text-ink">{{ writer.active_orders_count ?? 0 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-graphite">Warnings</span>
                <span class="font-semibold" :class="(writer.active_warning_count ?? 0) > 0 ? 'text-amber-600' : 'text-ink'">
                  {{ writer.active_warning_count ?? 0 }} active
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-graphite">Strikes</span>
                <span class="font-semibold" :class="(writer.active_strike_count ?? 0) > 0 ? 'text-rose-600' : 'text-ink'">
                  {{ writer.active_strike_count ?? 0 }} active
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Bio -->
        <div v-if="writer.bio" class="rounded-lg border border-slate-200 bg-white p-5">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">Bio</p>
          <p class="text-sm text-ink leading-relaxed">{{ writer.bio }}</p>
        </div>
      </div>

      <!-- Reviews tab -->
      <div v-else-if="activeTab === 'reviews'" class="space-y-4">
        <!-- Summary card -->
        <div v-if="reviewStore.writerSummary" class="rounded-lg border border-slate-200 bg-white p-5">
          <div class="flex items-center gap-6">
            <div class="text-center">
              <p class="text-4xl font-bold text-ink">{{ reviewStore.writerSummary.average_rating.toFixed(1) }}</p>
              <StarRating :rating="reviewStore.writerSummary.average_rating" size="md" />
              <p class="text-xs text-graphite mt-1">{{ reviewStore.writerSummary.total_reviews }} reviews</p>
            </div>
            <div class="flex-1 space-y-1.5">
              <div
                v-for="star in [5, 4, 3, 2, 1]"
                :key="star"
                class="flex items-center gap-2"
              >
                <span class="text-xs text-graphite w-4 text-right">{{ star }}</span>
                <div class="flex-1 h-2 rounded-full bg-slate-100">
                  <div
                    class="h-2 rounded-full bg-saffron transition-all"
                    :style="{ width: ratingBarWidth(reviewStore.writerSummary?.rating_distribution?.[String(star)] ?? 0) }"
                  />
                </div>
                <span class="text-xs text-graphite w-4">{{ reviewStore.writerSummary?.rating_distribution?.[String(star)] ?? 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Review list -->
        <div v-if="reviewStore.isLoading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="h-20 rounded-xl bg-slate-100 animate-pulse" />
        </div>

        <div
          v-else-if="!reviewStore.writerReviews.length"
          class="flex flex-col items-center gap-3 rounded-lg border border-slate-200 py-12 text-center"
        >
          <Star class="h-7 w-7 text-graphite" />
          <p class="text-sm text-graphite">No reviews yet.</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="review in reviewStore.writerReviews"
            :key="review.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
            :class="review.is_hidden ? 'opacity-60' : ''"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-ink">{{ review.order_topic }}</p>
                <p class="text-xs text-graphite mt-0.5">by {{ review.client_username }} · {{ formatDate(review.created_at) }}</p>
              </div>
              <StarRating :rating="review.rating" size="sm" />
            </div>
            <p v-if="review.title" class="mt-2 text-sm font-medium text-ink">{{ review.title }}</p>
            <p v-if="review.body" class="mt-1 text-sm text-graphite leading-relaxed">{{ review.body }}</p>
            <div class="mt-3 flex items-center gap-2">
              <span v-if="!review.is_public" class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite">Private</span>
              <span v-if="review.is_hidden" class="rounded-full bg-rose-50 border border-rose-200 px-2 py-0.5 text-xs text-rose-700">Hidden</span>
              <button
                class="text-xs text-graphite hover:text-rose-600 underline transition-colors ml-auto"
                type="button"
                :disabled="reviewStore.isSaving"
                @click="reviewStore.toggleHide(review)"
              >
                {{ review.is_hidden ? "Unhide" : "Hide" }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Discipline tab -->
      <div v-else-if="activeTab === 'discipline'" class="space-y-4">
        <div v-if="!discipline" class="rounded-lg border border-slate-200 bg-white p-6 text-center text-sm text-graphite">
          No discipline record loaded.
        </div>
        <template v-else>
          <!-- Status flags -->
          <div class="grid grid-cols-2 gap-4">
            <div class="rounded-lg border border-slate-200 bg-white p-5">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Status flags</p>
              <div class="space-y-2">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-graphite">Suspended</span>
                  <span :class="disciplineColor(discipline.is_suspended)" class="font-semibold">
                    {{ discipline.is_suspended ? "Yes" : "No" }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-graphite">On probation</span>
                  <span :class="disciplineColor(discipline.is_on_probation)" class="font-semibold">
                    {{ discipline.is_on_probation ? "Yes" : "No" }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-graphite">Blacklisted</span>
                  <span :class="disciplineColor(discipline.is_blacklisted)" class="font-semibold">
                    {{ discipline.is_blacklisted ? "Yes" : "No" }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-graphite">Restricted</span>
                  <span :class="disciplineColor(discipline.is_restricted)" class="font-semibold">
                    {{ discipline.is_restricted ? "Yes" : "No" }}
                  </span>
                </div>
              </div>
            </div>

            <div class="rounded-lg border border-slate-200 bg-white p-5">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Strike & warning record</p>
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-graphite">Active strikes</span>
                  <span class="font-semibold" :class="discipline.active_strike_count > 0 ? 'text-rose-600' : 'text-ink'">
                    {{ discipline.active_strike_count }}
                  </span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-graphite">Lifetime strikes</span>
                  <span class="font-semibold text-ink">{{ discipline.lifetime_strike_count }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-graphite">Active warnings</span>
                  <span class="font-semibold" :class="discipline.active_warning_count > 0 ? 'text-amber-600' : 'text-ink'">
                    {{ discipline.active_warning_count }}
                  </span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-graphite">Lifetime warnings</span>
                  <span class="font-semibold text-ink">{{ discipline.lifetime_warning_count }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Timelines -->
          <div class="rounded-lg border border-slate-200 bg-white p-5">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Timeline</p>
            <div class="space-y-2 text-sm">
              <div v-if="discipline.suspension_ends_at" class="flex justify-between">
                <span class="text-graphite">Suspension ends</span>
                <span class="font-semibold text-rose-600">{{ formatDate(discipline.suspension_ends_at) }}</span>
              </div>
              <div v-if="discipline.probation_ends_at" class="flex justify-between">
                <span class="text-graphite">Probation ends</span>
                <span class="font-semibold text-amber-600">{{ formatDate(discipline.probation_ends_at) }}</span>
              </div>
              <div v-if="discipline.last_discipline_event_at" class="flex justify-between">
                <span class="text-graphite">Last event</span>
                <span class="font-semibold text-ink">{{ formatDate(discipline.last_discipline_event_at) }}</span>
              </div>
              <p
                v-if="!discipline.suspension_ends_at && !discipline.probation_ends_at && !discipline.last_discipline_event_at"
                class="text-graphite"
              >
                No recent discipline events.
              </p>
            </div>
          </div>

          <!-- Suspension banner -->
          <div v-if="discipline.is_suspended" class="rounded-xl border border-rose-200 bg-rose-50 p-4 flex items-start gap-3">
            <AlertTriangle class="h-5 w-5 text-rose-500 shrink-0 mt-0.5" />
            <div>
              <p class="text-sm font-semibold text-rose-800">Writer is suspended</p>
              <p v-if="discipline.suspension_ends_at" class="text-xs text-rose-700 mt-0.5">
                Suspension ends {{ formatDate(discipline.suspension_ends_at) }}
              </p>
            </div>
          </div>
        </template>
      </div>
    </template>

    <div v-else-if="!localLoading" class="rounded-xl border border-rose-200 bg-rose-50 p-6 text-center">
      <p class="text-sm font-semibold text-rose-800">Writer not found.</p>
      <button
        class="mt-3 text-sm text-rose-700 underline"
        type="button"
        @click="router.push('/admin/writers')"
      >
        Back to writers
      </button>
    </div>
  </div>
</template>
