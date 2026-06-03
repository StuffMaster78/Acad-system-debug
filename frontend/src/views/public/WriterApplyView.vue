<script setup lang="ts">
import { reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { ArrowRight, CheckCircle2, Upload, X } from "@lucide/vue";
import { api, apiPath } from "@/api/client";
import { usePortalContextStore } from "@/stores/portalContext";
import { useAnalytics } from "@/composables/useAnalytics";

const { writerApplicationSubmitted } = useAnalytics();

const portalCtx = usePortalContextStore();

type Step = "form" | "success";
const step = ref<Step>("form");
const isSubmitting = ref(false);
const serverError = ref("");

const form = reactive({
  full_name: "",
  email: "",
  phone_number: "",
  country: "",
  education_level: "",
  years_of_experience: 0,
  application_text: "",
  subjectInput: "",       // raw comma-separated input
});

const resumeFile    = ref<File | null>(null);
const sampleFile    = ref<File | null>(null);
const resumeInput   = ref<HTMLInputElement | null>(null);
const sampleInput   = ref<HTMLInputElement | null>(null);

function pickFile(which: "resume" | "sample") {
  if (which === "resume") resumeInput.value?.click();
  else sampleInput.value?.click();
}

function onFileChange(which: "resume" | "sample", e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0] ?? null;
  if (which === "resume") resumeFile.value = file;
  else sampleFile.value = file;
}

function clearFile(which: "resume" | "sample") {
  if (which === "resume") { resumeFile.value = null; if (resumeInput.value) resumeInput.value.value = ""; }
  else { sampleFile.value = null; if (sampleInput.value) sampleInput.value.value = ""; }
}

const errors = reactive<Record<string, string>>({});

function validate(): boolean {
  Object.keys(errors).forEach((k) => delete (errors as Record<string, string>)[k]);
  if (!form.full_name.trim()) errors.full_name = "Full name is required.";
  if (!form.email.trim() || !form.email.includes("@")) errors.email = "Valid email is required.";
  if (!form.application_text.trim() || form.application_text.trim().length < 50)
    errors.application_text = "Please write at least 50 characters about yourself.";
  return Object.keys(errors).length === 0;
}

async function submit() {
  if (!validate()) return;
  isSubmitting.value = true;
  serverError.value = "";

  try {
    const subjects = form.subjectInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const body = new FormData();
    body.append("full_name",           form.full_name.trim());
    body.append("email",               form.email.trim());
    body.append("phone_number",        form.phone_number.trim());
    body.append("country",             form.country.trim());
    body.append("education_level",     form.education_level.trim());
    body.append("years_of_experience", String(form.years_of_experience));
    body.append("application_text",    form.application_text.trim());
    subjects.forEach((s) => body.append("subjects", s));
    if (resumeFile.value)  body.append("resume",      resumeFile.value);
    if (sampleFile.value)  body.append("sample_work", sampleFile.value);

    // Do NOT set Content-Type manually — axios detects FormData and adds
    // the correct multipart boundary automatically. Explicit header breaks it.
    await api.post(apiPath("/writer-management/applications/submit/"), body);

    step.value = "success";
    writerApplicationSubmitted();
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })
      ?.response?.data?.detail;
    serverError.value = detail ?? "Submission failed. Please try again.";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Header -->
    <div class="bg-white border-b border-slate-200 px-6 py-12 text-center">
      <p class="text-sm font-semibold uppercase tracking-wide text-signal mb-2">Join the team</p>
      <h1 class="text-4xl font-extrabold text-ink">
        Apply to write with {{ portalCtx.branding?.brand_name ?? 'us' }}
      </h1>
      <p class="mt-3 max-w-xl mx-auto text-lg text-graphite">
        Share your skills and experience. Our team reviews every application within 3–5 business days.
      </p>
    </div>

    <div class="mx-auto max-w-2xl px-6 py-12">

      <!-- Success state -->
      <div v-if="step === 'success'" class="rounded-2xl bg-white border border-slate-200 p-10 text-center space-y-4">
        <CheckCircle2 class="mx-auto size-16 text-emerald-500" />
        <h2 class="text-2xl font-bold text-ink">Application received!</h2>
        <p class="text-graphite max-w-sm mx-auto">
          Thank you for applying. We'll review your submission and get back to you at <strong>{{ form.email }}</strong> within 3–5 business days.
        </p>
        <RouterLink
          to="/"
          class="mt-4 inline-flex items-center gap-2 rounded-xl bg-ink px-6 py-3 text-sm font-semibold text-white hover:opacity-90 transition-opacity"
        >
          Back to home <ArrowRight class="size-4" />
        </RouterLink>
      </div>

      <!-- Form -->
      <form v-else class="space-y-6" @submit.prevent="submit">

        <!-- Server error -->
        <div v-if="serverError" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
          {{ serverError }}
        </div>

        <!-- Personal info -->
        <section class="rounded-xl bg-white border border-slate-200 p-6 space-y-4">
          <h2 class="text-base font-semibold text-ink">Personal information</h2>

          <div class="grid gap-4 sm:grid-cols-2">
            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Full name <span class="text-berry">*</span></span>
              <input
                v-model="form.full_name"
                type="text"
                autocomplete="name"
                placeholder="Jane Smith"
                class="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
                :class="{ 'border-rose-400': errors.full_name }"
              />
              <p v-if="errors.full_name" class="text-xs text-rose-600">{{ errors.full_name }}</p>
            </label>

            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Email <span class="text-berry">*</span></span>
              <input
                v-model="form.email"
                type="email"
                autocomplete="email"
                placeholder="jane@example.com"
                class="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
                :class="{ 'border-rose-400': errors.email }"
              />
              <p v-if="errors.email" class="text-xs text-rose-600">{{ errors.email }}</p>
            </label>

            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Phone number</span>
              <input
                v-model="form.phone_number"
                type="tel"
                autocomplete="tel"
                placeholder="+1 555 000 0000"
                class="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
              />
            </label>

            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Country</span>
              <input
                v-model="form.country"
                type="text"
                placeholder="United States"
                class="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
              />
            </label>
          </div>
        </section>

        <!-- Qualifications -->
        <section class="rounded-xl bg-white border border-slate-200 p-6 space-y-4">
          <h2 class="text-base font-semibold text-ink">Qualifications</h2>

          <div class="grid gap-4 sm:grid-cols-2">
            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Highest education level</span>
              <select
                v-model="form.education_level"
                class="mt-1 block w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
              >
                <option value="">— select —</option>
                <option value="High School">High School</option>
                <option value="Associate's Degree">Associate's Degree</option>
                <option value="Bachelor's Degree">Bachelor's Degree</option>
                <option value="Master's Degree">Master's Degree</option>
                <option value="PhD / Doctorate">PhD / Doctorate</option>
              </select>
            </label>

            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Years of writing experience</span>
              <input
                v-model.number="form.years_of_experience"
                type="number"
                min="0"
                max="50"
                class="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
              />
            </label>
          </div>

          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Subject areas (comma-separated)</span>
            <input
              v-model="form.subjectInput"
              type="text"
              placeholder="Nursing, Business, Psychology, Literature…"
              class="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ink"
            />
            <p class="text-xs text-slate-400">List the subjects you're confident writing in.</p>
          </label>
        </section>

        <!-- Cover letter -->
        <section class="rounded-xl bg-white border border-slate-200 p-6 space-y-4">
          <h2 class="text-base font-semibold text-ink">Cover letter</h2>

          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">
              Tell us about yourself <span class="text-berry">*</span>
            </span>
            <textarea
              v-model="form.application_text"
              rows="6"
              placeholder="Describe your writing experience, areas of expertise, and why you'd be a great fit. Minimum 50 characters."
              class="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ink resize-none"
              :class="{ 'border-rose-400': errors.application_text }"
            />
            <div class="flex items-center justify-between">
              <p v-if="errors.application_text" class="text-xs text-rose-600">{{ errors.application_text }}</p>
              <p class="text-xs text-slate-400 ml-auto">{{ form.application_text.trim().length }} characters</p>
            </div>
          </label>
        </section>

        <!-- File uploads -->
        <section class="rounded-xl bg-white border border-slate-200 p-6 space-y-4">
          <h2 class="text-base font-semibold text-ink">Documents <span class="text-xs font-normal text-graphite">(optional but recommended)</span></h2>

          <!-- Resume -->
          <div class="space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Resume / CV</span>
            <input ref="resumeInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="onFileChange('resume', $event)" />
            <div v-if="resumeFile" class="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm">
              <CheckCircle2 class="size-4 text-emerald-600 shrink-0" />
              <span class="truncate text-emerald-800">{{ resumeFile.name }}</span>
              <button type="button" class="ml-auto text-emerald-500 hover:text-emerald-800" @click="clearFile('resume')">
                <X class="size-4" />
              </button>
            </div>
            <button
              v-else
              type="button"
              class="flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-slate-300 bg-slate-50 py-3 text-sm text-graphite hover:border-slate-400 hover:bg-white transition-colors"
              @click="pickFile('resume')"
            >
              <Upload class="size-4" /> Upload resume (PDF, DOC, DOCX)
            </button>
          </div>

          <!-- Sample work -->
          <div class="space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Sample writing</span>
            <input ref="sampleInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="onFileChange('sample', $event)" />
            <div v-if="sampleFile" class="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm">
              <CheckCircle2 class="size-4 text-emerald-600 shrink-0" />
              <span class="truncate text-emerald-800">{{ sampleFile.name }}</span>
              <button type="button" class="ml-auto text-emerald-500 hover:text-emerald-800" @click="clearFile('sample')">
                <X class="size-4" />
              </button>
            </div>
            <button
              v-else
              type="button"
              class="flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-slate-300 bg-slate-50 py-3 text-sm text-graphite hover:border-slate-400 hover:bg-white transition-colors"
              @click="pickFile('sample')"
            >
              <Upload class="size-4" /> Upload a writing sample (PDF, DOC, DOCX)
            </button>
          </div>
        </section>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-ink py-4 text-base font-bold text-white hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          <span v-if="isSubmitting">Submitting…</span>
          <template v-else>
            Submit application <ArrowRight class="size-5" />
          </template>
        </button>

        <p class="text-center text-xs text-slate-400">
          Already have an account?
          <RouterLink to="/auth/login" class="text-ink hover:underline font-medium">Sign in</RouterLink>
        </p>
      </form>
    </div>
  </div>
</template>
