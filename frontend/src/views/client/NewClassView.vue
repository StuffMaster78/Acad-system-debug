<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-2xl space-y-6">

      <!-- Back + heading -->
      <div>
        <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
          <ArrowLeft class="size-3.5" />
          Back to Classes
        </button>
        <h1 class="text-2xl font-bold text-ink">Start Class Management</h1>
        <p class="mt-1 text-sm text-graphite">Tell us about your course and we'll assign an expert and send a quote.</p>
      </div>

      <!-- Form card -->
      <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-panel space-y-5">

        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-ink mb-1">
            Course / Class Title <span class="text-rose-500">*</span>
          </label>
          <input
            v-model="form.title"
            placeholder="e.g. MATH 301 – Linear Algebra or Intro to Psychology"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
          />
        </div>

        <!-- Subject -->
        <div>
          <label class="block text-sm font-medium text-ink mb-1">
            Subject Area <span class="text-rose-500">*</span>
          </label>
          <input
            v-model="form.subject"
            placeholder="e.g. Mathematics, Business Ethics, Nursing"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring"
          />
        </div>

        <!-- Academic level -->
        <div>
          <label class="block text-sm font-medium text-ink mb-1">
            Academic Level <span class="text-rose-500">*</span>
          </label>
          <select v-model="form.academic_level" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring bg-white">
            <option value="">Select level…</option>
            <option value="High School">High School</option>
            <option value="Undergraduate">Undergraduate</option>
            <option value="Graduate">Graduate (Master's)</option>
            <option value="PhD">PhD / Doctoral</option>
          </select>
        </div>

        <!-- Dates -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-ink mb-1">
              Course Start Date <span class="text-rose-500">*</span>
            </label>
            <input v-model="form.start_date" type="date" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink mb-1">
              Course End Date <span class="text-rose-500">*</span>
            </label>
            <input v-model="form.end_date" type="date" class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring" />
          </div>
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-sm font-medium text-ink mb-1">Additional Notes <span class="text-graphite font-normal">(optional)</span></label>
          <textarea
            v-model="form.notes"
            rows="4"
            placeholder="Paste syllabus link, grading breakdown, platform details, weekly task schedule, or any other helpful context…"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring resize-none"
          />
        </div>

        <!-- Portal access -->
        <label class="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-200 p-4 hover:bg-slate-50">
          <input v-model="form.portal_access_enabled" type="checkbox" class="mt-0.5 size-4 rounded accent-berry" />
          <div>
            <p class="text-sm font-medium text-ink">I'll need to share portal / LMS credentials</p>
            <p class="mt-0.5 text-xs text-graphite">Check this if the course uses Blackboard, Canvas, Moodle, or a similar platform. You can share credentials securely after submission.</p>
          </div>
        </label>

        <!-- Error -->
        <div v-if="error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {{ error }}
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-1">
          <button
            class="rounded-lg bg-berry px-6 py-2.5 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60 transition-colors"
            :disabled="isSaving || !isValid"
            @click="submit"
          >
            {{ isSaving ? "Submitting…" : "Submit Request" }}
          </button>
          <button
            class="rounded-lg border border-slate-200 px-5 py-2.5 text-sm text-graphite hover:text-ink hover:bg-slate-50 transition-colors"
            @click="router.back()"
          >
            Cancel
          </button>
        </div>

      </div>

      <!-- What happens next -->
      <div class="rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-panel space-y-2">
        <p class="text-sm font-semibold text-ink">What happens next?</p>
        <div class="space-y-1.5 text-sm text-graphite">
          <div class="flex items-start gap-2">
            <span class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-berry/10 text-xs font-bold text-berry">1</span>
            Our team reviews your request and matches you with a qualified expert.
          </div>
          <div class="flex items-start gap-2">
            <span class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-berry/10 text-xs font-bold text-berry">2</span>
            You receive a detailed price quote — usually within a few hours.
          </div>
          <div class="flex items-start gap-2">
            <span class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-berry/10 text-xs font-bold text-berry">3</span>
            Once you approve and complete the first payment, your expert gets started.
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { ArrowLeft } from "@lucide/vue";
import { classesApi } from "@/api/classes";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();

const form = ref({
  title: "",
  subject: "",
  academic_level: "",
  start_date: "",
  end_date: "",
  notes: "",
  portal_access_enabled: false,
});

const isSaving = ref(false);
const error = ref<string | null>(null);

const isValid = computed(() =>
  form.value.title.trim() &&
  form.value.subject.trim() &&
  form.value.academic_level &&
  form.value.start_date &&
  form.value.end_date,
);

async function submit() {
  if (!isValid.value) return;
  isSaving.value = true;
  error.value = null;
  try {
    if (auth.isPreviewSession) {
      router.push("/client/classes");
      return;
    }
    const res = await classesApi.create({
      title: form.value.title,
      subject: form.value.subject,
      academic_level: form.value.academic_level,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      notes: form.value.notes || undefined,
      portal_access_enabled: form.value.portal_access_enabled || undefined,
    });
    router.push(`/client/classes/${res.data.id}`);
  } catch {
    error.value = "Failed to submit your request. Please try again.";
  } finally {
    isSaving.value = false;
  }
}
</script>
