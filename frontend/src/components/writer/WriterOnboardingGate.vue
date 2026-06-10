<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";
import {
  AlertCircle, CheckCircle2, ChevronRight, Clock, FileText, GraduationCap, UserCircle,
} from "@lucide/vue";
import type { WriterOnboardingStatus } from "@/types/writer";

const props = defineProps<{
  status: WriterOnboardingStatus;
  rejectionReason?: string | null;
}>();

// ── Step definitions ──────────────────────────────────────────────────────────

interface Step {
  key: string;
  label: string;
  description: string;
  icon: typeof UserCircle;
  to?: string;
  cta?: string;
}

const STEPS: Step[] = [
  {
    key: "profile",
    label: "Complete your profile",
    description: "Add your bio, subjects, and contact details so our team knows who you are.",
    icon: UserCircle,
    to: "/writer/account",
    cta: "Go to profile",
  },
  {
    key: "quizzes",
    label: "Pass the vetting quizzes",
    description: "Take the grammar and subject tests. Some quizzes include an essay reviewed by our editors.",
    icon: GraduationCap,
    to: "/writer/vetting",
    cta: "Take quizzes",
  },
  {
    key: "review",
    label: "Await team review",
    description: "Our team reviews your application and quiz results. This usually takes 1–3 business days.",
    icon: Clock,
  },
];

// Map onboarding_status to which step is currently active (0-indexed)
const ACTIVE_STEP: Record<WriterOnboardingStatus, number> = {
  not_started:       0,
  in_progress:       0,
  documents_pending: 1,
  review_pending:    2,
  rejected:          0, // send back to start
  completed:         3, // all done — gate shouldn't show
};

const activeStep = computed(() => ACTIVE_STEP[props.status] ?? 0);

function stepState(idx: number): "done" | "active" | "upcoming" {
  if (idx < activeStep.value) return "done";
  if (idx === activeStep.value) return "active";
  return "upcoming";
}
</script>

<template>
  <div class="min-h-[60vh] flex flex-col items-center justify-center px-4 py-16">
    <div class="w-full max-w-lg space-y-8">

      <!-- Rejected state ─────────────────────────────────────────────────── -->
      <template v-if="status === 'rejected'">
        <div class="rounded-2xl border border-rose-200 bg-rose-50 p-8 text-center space-y-4">
          <AlertCircle class="mx-auto size-12 text-rose-500" />
          <h2 class="text-xl font-bold text-rose-900">Application not approved</h2>
          <p class="text-sm text-rose-700 max-w-sm mx-auto">
            Unfortunately your application was not approved at this time.
            <template v-if="rejectionReason">
              <br /><span class="font-medium">Reason:</span> {{ rejectionReason }}
            </template>
          </p>
          <p class="text-xs text-rose-600">
            If you believe this was in error, contact support for assistance.
          </p>
        </div>
      </template>

      <!-- Normal onboarding flow ─────────────────────────────────────────── -->
      <template v-else>
        <!-- Header -->
        <div class="text-center space-y-2">
          <FileText class="mx-auto size-10 text-indigo-500" />
          <h1 class="text-2xl font-bold text-neutral-900">
            {{ status === 'review_pending' ? 'Your application is under review' : 'Complete your onboarding' }}
          </h1>
          <p class="text-sm text-neutral-500 max-w-sm mx-auto">
            {{ status === 'review_pending'
              ? 'Our team is reviewing your quiz results. You\'ll be notified once approved.'
              : 'Follow the steps below to get your writer account fully activated.' }}
          </p>
        </div>

        <!-- Stepper ─────────────────────────────────────────────────────── -->
        <div class="space-y-3">
          <div
            v-for="(step, idx) in STEPS"
            :key="step.key"
            class="flex gap-4 rounded-xl border p-4 transition-colors"
            :class="{
              'border-indigo-200 bg-indigo-50':  stepState(idx) === 'active',
              'border-emerald-100 bg-emerald-50/60 opacity-75': stepState(idx) === 'done',
              'border-neutral-100 bg-white':     stepState(idx) === 'upcoming',
            }"
          >
            <!-- Icon / done indicator -->
            <div class="shrink-0 mt-0.5">
              <div
                class="flex size-9 items-center justify-center rounded-full"
                :class="{
                  'bg-indigo-100': stepState(idx) === 'active',
                  'bg-emerald-100': stepState(idx) === 'done',
                  'bg-neutral-100': stepState(idx) === 'upcoming',
                }"
              >
                <CheckCircle2
                  v-if="stepState(idx) === 'done'"
                  class="size-5 text-emerald-600"
                />
                <component
                  :is="step.icon"
                  v-else
                  class="size-5"
                  :class="{
                    'text-indigo-600': stepState(idx) === 'active',
                    'text-neutral-400': stepState(idx) === 'upcoming',
                  }"
                />
              </div>
            </div>

            <!-- Text -->
            <div class="flex-1 min-w-0">
              <p
                class="text-sm font-semibold"
                :class="{
                  'text-indigo-900': stepState(idx) === 'active',
                  'text-emerald-800': stepState(idx) === 'done',
                  'text-neutral-400': stepState(idx) === 'upcoming',
                }"
              >
                <span class="mr-1.5 text-xs opacity-60">{{ idx + 1 }}.</span>{{ step.label }}
              </p>
              <p class="mt-0.5 text-xs text-neutral-500 leading-relaxed">{{ step.description }}</p>

              <RouterLink
                v-if="stepState(idx) === 'active' && step.to && step.cta"
                :to="step.to"
                class="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700 transition-colors"
              >
                {{ step.cta }} <ChevronRight class="size-3.5" />
              </RouterLink>
            </div>
          </div>
        </div>

        <!-- Review pending notice -->
        <div
          v-if="status === 'review_pending'"
          class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 text-center"
        >
          <Clock class="inline size-4 mr-1.5 align-text-bottom" />
          Typical review time is 1–3 business days. We'll email you when a decision is made.
        </div>
      </template>

    </div>
  </div>
</template>
