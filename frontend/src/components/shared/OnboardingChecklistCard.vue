<!--
  OnboardingChecklistCard — shows on the dashboard until all steps are done.
  Fetches from GET /api/v1/accounts/me/onboarding-status/ on mount.
  Auto-hides once all steps are completed.
-->
<template>
  <Transition name="fade">
    <div
      v-if="show && checklist"
      class="rounded-xl border border-signal/20 bg-signal/[0.03] p-5 shadow-sm"
    >
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Rocket class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold text-ink">Getting started</h2>
        </div>
        <div class="flex items-center gap-3">
          <div class="text-xs text-graphite">
            {{ checklist.completed }}/{{ checklist.total }} complete
          </div>
          <button
            class="rounded p-1 text-graphite hover:bg-white/50"
            title="Dismiss"
            @click="dismiss"
          >✕</button>
        </div>
      </div>

      <!-- Progress bar -->
      <div class="mt-3 h-1.5 w-full rounded-full bg-slate-200">
        <div
          class="h-1.5 rounded-full bg-signal transition-all duration-500"
          :style="{ width: `${(checklist.completed / checklist.total) * 100}%` }"
        />
      </div>

      <!-- Steps -->
      <div class="mt-4 grid gap-2 sm:grid-cols-2">
        <RouterLink
          v-for="step in checklist.steps"
          :key="step.key"
          :to="step.link"
          class="flex items-start gap-3 rounded-lg border p-3 transition-colors hover:bg-white/60"
          :class="step.done
            ? 'border-emerald-100 bg-emerald-50/50 opacity-70'
            : 'border-slate-200 bg-white'"
        >
          <span
            class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full"
            :class="step.done ? 'bg-emerald-500 text-white' : 'border-2 border-slate-200'"
          >
            <CheckIcon v-if="step.done" class="h-3 w-3" />
          </span>
          <div class="min-w-0">
            <p class="text-sm font-medium" :class="step.done ? 'text-graphite line-through' : 'text-ink'">
              {{ step.label }}
            </p>
            <p class="mt-0.5 text-xs text-graphite">{{ step.description }}</p>
          </div>
        </RouterLink>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { Check as CheckIcon, Rocket } from "@lucide/vue";
import { api, apiPath } from "@/api/client";

interface OnboardingStep {
  key: string;
  label: string;
  description: string;
  done: boolean;
  link: string;
}

interface OnboardingChecklist {
  role: string;
  steps: OnboardingStep[];
  completed: number;
  total: number;
}

const checklist = ref<OnboardingChecklist | null>(null);
const dismissed = ref(false);

const DISMISS_KEY = "onboarding_dismissed";

const show = computed(() =>
  !dismissed.value && !!checklist.value && checklist.value.completed < checklist.value.total
);

onMounted(async () => {
  if (sessionStorage.getItem(DISMISS_KEY)) {
    dismissed.value = true;
    return;
  }
  try {
    const { data } = await api.get<OnboardingChecklist>(apiPath("/accounts/me/onboarding-status/"));
    checklist.value = data;
  } catch {
    checklist.value = null;
  }
});

function dismiss() {
  dismissed.value = true;
  sessionStorage.setItem(DISMISS_KEY, "1");
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
