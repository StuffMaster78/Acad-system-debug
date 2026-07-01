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
  subjectInput: "",
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
    const subjects = form.subjectInput.split(",").map((s) => s.trim()).filter(Boolean);
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
    await api.post(apiPath("/writer-management/applications/submit/"), body);
    step.value = "success";
    writerApplicationSubmitted();
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    serverError.value = detail ?? "Submission failed. Please try again.";
  } finally {
    isSubmitting.value = false;
  }
}

// ─── Starfield ───────────────────────────────────────────────────────────────
function hr(seed: number) { const s = Math.sin(seed) * 43758.5453123; return s - Math.floor(s); }
const STARS = Array.from({ length: 120 }, (_, i) => ({
  x: hr(i * 127.1) * 100, y: hr(i * 311.7) * 100,
  r: [1, 1, 1, 1, 1.5, 2][Math.floor(hr(i * 52.7) * 6)],
  op: 0.3 + hr(i * 231.3) * 0.6,
  dur: `${3 + hr(i * 79.3) * 5}s`, del: `${hr(i * 193.1) * 8}s`,
}));
</script>

<template>
  <div class="relative min-h-screen overflow-x-hidden bg-[#04060f] font-sans">

    <!-- ── Starfield ─────────────────────────────────────────────────── -->
    <div class="pointer-events-none fixed inset-0 z-0" aria-hidden="true">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" class="absolute inset-0">
        <circle
          v-for="(s, i) in STARS" :key="i"
          :cx="`${s.x}%`" :cy="`${s.y}%`" :r="s.r"
          fill="white" :fill-opacity="s.op"
          :style="{ animation: `wink ${s.dur} ${s.del} ease-in-out infinite` }"
        />
      </svg>
    </div>

    <!-- ── Ambient glows ──────────────────────────────────────────────── -->
    <div class="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div class="absolute -left-20 top-0 h-80 w-80 rounded-full bg-[#7c3aed]/15 blur-[120px]" />
      <div class="absolute -right-20 top-1/2 h-72 w-72 rounded-full bg-[#06b6d4]/12 blur-[100px]" />
      <div class="absolute bottom-0 left-1/3 h-60 w-[500px] rounded-full bg-[#8b5cf6]/8 blur-[120px]" />
    </div>

    <!-- ── Grid overlay ───────────────────────────────────────────────── -->
    <div
      class="pointer-events-none fixed inset-0 z-0 opacity-[0.025]"
      style="background-image: linear-gradient(rgba(139,92,246,0.5) 1px,transparent 1px),linear-gradient(90deg,rgba(139,92,246,0.5) 1px,transparent 1px);background-size:56px 56px;"
      aria-hidden="true"
    />

    <!-- ── Page content ───────────────────────────────────────────────── -->
    <div class="relative z-10">

      <!-- ─── Success state ─────────────────────────────────────────── -->
      <div v-if="step === 'success'" class="flex min-h-screen items-center justify-center px-5 py-16">
        <div class="w-full max-w-lg text-center space-y-8">
          <!-- Orbit animation -->
          <div class="relative mx-auto h-28 w-28">
            <div class="absolute inset-0 rounded-full bg-[#7c3aed]/20 animate-ping" style="animation-duration:2s;" />
            <div class="absolute inset-2 rounded-full bg-[#7c3aed]/30 animate-ping" style="animation-duration:2.5s;animation-delay:0.5s;" />
            <div class="relative flex h-28 w-28 items-center justify-center rounded-full bg-gradient-to-br from-[#7c3aed] to-[#06b6d4]">
              <CheckCircle2 class="h-14 w-14 text-white" />
            </div>
          </div>

          <div class="space-y-3">
            <p class="font-mono text-xs font-semibold uppercase tracking-[0.3em] text-[#06b6d4]">// transmission received</p>
            <h2 class="text-4xl font-black text-white">Application<br/>received.</h2>
            <p class="text-base text-white/55 max-w-sm mx-auto leading-relaxed">
              We have your signal. Our team reviews every submission personally and will respond to
              <strong class="text-white/80">{{ form.email }}</strong> within 3–5 business days.
            </p>
          </div>

          <div class="flex flex-col items-center gap-3">
            <RouterLink
              to="/"
              class="cosmos-btn inline-flex items-center gap-2 rounded-xl px-8 py-3.5 text-sm font-bold text-white"
            >
              Return to home base <ArrowRight class="h-4 w-4" />
            </RouterLink>
            <RouterLink to="/writer/login" class="text-xs text-white/35 hover:text-white/55 transition-colors">
              Already have access? Sign in →
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- ─── Application form ──────────────────────────────────────── -->
      <div v-else class="mx-auto max-w-3xl px-5 py-14">

        <!-- Page header -->
        <div class="mb-12 text-center space-y-4">
          <div class="inline-flex items-center gap-2 rounded-full border border-[#7c3aed]/30 bg-[#7c3aed]/10 px-4 py-1.5">
            <span class="h-1.5 w-1.5 rounded-full bg-[#06b6d4] animate-pulse" />
            <span class="font-mono text-xs font-semibold uppercase tracking-widest text-[#06b6d4]">Applications open</span>
          </div>
          <h1 class="text-5xl font-black leading-tight text-white">
            Join the<br/>
            <span class="bg-gradient-to-r from-[#8b5cf6] via-[#06b6d4] to-white bg-clip-text text-transparent">writer collective</span>
          </h1>
          <p class="mx-auto max-w-md text-base text-white/50">
            Share your skills. Our team personally reviews every application and gets back to you within 3–5 days.
          </p>
        </div>

        <!-- Trust badges -->
        <div class="mb-10 grid grid-cols-3 gap-4">
          <div
            v-for="b in [
              { icon: '⚡', title: 'Fast review', sub: '3–5 business days' },
              { icon: '💰', title: 'Weekly pay', sub: 'Earnings in USD' },
              { icon: '🌍', title: 'Remote', sub: 'Work anywhere' },
            ]"
            :key="b.title"
            class="rounded-xl border border-white/8 bg-white/4 p-4 text-center backdrop-blur-sm"
          >
            <p class="text-xl mb-1.5">{{ b.icon }}</p>
            <p class="text-xs font-semibold text-white/80">{{ b.title }}</p>
            <p class="text-[11px] text-white/35 mt-0.5">{{ b.sub }}</p>
          </div>
        </div>

        <!-- Server error -->
        <div v-if="serverError" class="mb-6 flex items-center gap-3 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          <span class="shrink-0 text-base">⚠</span>{{ serverError }}
        </div>

        <form class="space-y-5" @submit.prevent="submit">

          <!-- Personal info -->
          <div class="cosmos-card space-y-5 rounded-2xl border border-white/10 bg-[#0c1225]/60 p-7 backdrop-blur-xl">
            <div class="flex items-center gap-3 mb-1">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-[#7c3aed]/20">
                <span class="text-sm">👤</span>
              </div>
              <div>
                <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.25em] text-[#06b6d4]">// 01</p>
                <h2 class="text-sm font-bold text-white">Personal information</h2>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="space-y-1.5">
                <label class="block text-[10px] font-semibold uppercase tracking-widest text-white/45" for="ap-name">
                  Full name <span class="text-[#ec4899]">*</span>
                </label>
                <input
                  id="ap-name"
                  v-model="form.full_name"
                  type="text" autocomplete="name" placeholder="Jane Smith"
                  class="cosmos-input h-11 w-full rounded-xl border px-4 text-sm transition-all"
                  :class="errors.full_name ? 'border-red-400/50 bg-red-400/5' : 'border-white/10 bg-white/5'"
                />
                <p v-if="errors.full_name" class="text-xs text-red-400">{{ errors.full_name }}</p>
              </div>

              <div class="space-y-1.5">
                <label class="block text-[10px] font-semibold uppercase tracking-widest text-white/45" for="ap-email">
                  Email <span class="text-[#ec4899]">*</span>
                </label>
                <input
                  id="ap-email"
                  v-model="form.email"
                  type="email" autocomplete="email" placeholder="jane@example.com"
                  class="cosmos-input h-11 w-full rounded-xl border px-4 text-sm transition-all"
                  :class="errors.email ? 'border-red-400/50 bg-red-400/5' : 'border-white/10 bg-white/5'"
                />
                <p v-if="errors.email" class="text-xs text-red-400">{{ errors.email }}</p>
              </div>

              <div class="space-y-1.5">
                <label class="block text-[10px] font-semibold uppercase tracking-widest text-white/45" for="ap-phone">Phone</label>
                <input
                  id="ap-phone"
                  v-model="form.phone_number"
                  type="tel" autocomplete="tel" placeholder="+1 555 000 0000"
                  class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm transition-all"
                />
              </div>

              <div class="space-y-1.5">
                <label class="block text-[10px] font-semibold uppercase tracking-widest text-white/45" for="ap-country">Country</label>
                <input
                  id="ap-country"
                  v-model="form.country"
                  type="text" placeholder="United States"
                  class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm transition-all"
                />
              </div>
            </div>
          </div>

          <!-- Qualifications -->
          <div class="cosmos-card space-y-5 rounded-2xl border border-white/10 bg-[#0c1225]/60 p-7 backdrop-blur-xl">
            <div class="flex items-center gap-3 mb-1">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-[#06b6d4]/20">
                <span class="text-sm">🎓</span>
              </div>
              <div>
                <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.25em] text-[#06b6d4]">// 02</p>
                <h2 class="text-sm font-bold text-white">Qualifications</h2>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="space-y-1.5">
                <label class="block text-[10px] font-semibold uppercase tracking-widest text-white/45" for="ap-edu">Highest education</label>
                <select
                  id="ap-edu"
                  v-model="form.education_level"
                  class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-[#0c1225] px-4 text-sm text-white transition-all appearance-none"
                >
                  <option value="" class="bg-[#0c1225]">— select —</option>
                  <option value="High School" class="bg-[#0c1225]">High School</option>
                  <option value="Associate's Degree" class="bg-[#0c1225]">Associate's Degree</option>
                  <option value="Bachelor's Degree" class="bg-[#0c1225]">Bachelor's Degree</option>
                  <option value="Master's Degree" class="bg-[#0c1225]">Master's Degree</option>
                  <option value="PhD / Doctorate" class="bg-[#0c1225]">PhD / Doctorate</option>
                </select>
              </div>

              <div class="space-y-1.5">
                <label class="block text-[10px] font-semibold uppercase tracking-widest text-white/45" for="ap-exp">Years of experience</label>
                <input
                  id="ap-exp"
                  v-model.number="form.years_of_experience"
                  type="number" min="0" max="50"
                  class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm transition-all"
                />
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="block text-[10px] font-semibold uppercase tracking-widest text-white/45" for="ap-subjects">Subject areas <span class="normal-case font-normal text-white/25">(comma-separated)</span></label>
              <input
                id="ap-subjects"
                v-model="form.subjectInput"
                type="text" placeholder="Nursing, Business, Psychology, Computer Science…"
                class="cosmos-input h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm transition-all"
              />
              <p class="text-[11px] text-white/25">List the subjects you're confident writing in.</p>
            </div>
          </div>

          <!-- Cover letter -->
          <div class="cosmos-card space-y-5 rounded-2xl border border-white/10 bg-[#0c1225]/60 p-7 backdrop-blur-xl">
            <div class="flex items-center gap-3 mb-1">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-[#8b5cf6]/20">
                <span class="text-sm">✍️</span>
              </div>
              <div>
                <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.25em] text-[#06b6d4]">// 03</p>
                <h2 class="text-sm font-bold text-white">Your story</h2>
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="block text-[10px] font-semibold uppercase tracking-widest text-white/45" for="ap-letter">
                Tell us about yourself <span class="text-[#ec4899]">*</span>
              </label>
              <textarea
                id="ap-letter"
                v-model="form.application_text"
                rows="6"
                placeholder="Describe your writing background, areas of expertise, writing style, and what draws you to academic writing. Minimum 50 characters."
                class="cosmos-input w-full rounded-xl border px-4 py-3 text-sm transition-all resize-none leading-relaxed"
                :class="errors.application_text ? 'border-red-400/50 bg-red-400/5' : 'border-white/10 bg-white/5'"
              />
              <div class="flex items-start justify-between">
                <p v-if="errors.application_text" class="text-xs text-red-400">{{ errors.application_text }}</p>
                <p class="ml-auto text-[11px]" :class="form.application_text.trim().length >= 50 ? 'text-[#06b6d4]' : 'text-white/25'">
                  {{ form.application_text.trim().length }} / 50 min
                </p>
              </div>
            </div>
          </div>

          <!-- File uploads -->
          <div class="cosmos-card space-y-5 rounded-2xl border border-white/10 bg-[#0c1225]/60 p-7 backdrop-blur-xl">
            <div class="flex items-center gap-3 mb-1">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-[#f59e0b]/20">
                <span class="text-sm">📎</span>
              </div>
              <div>
                <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.25em] text-[#06b6d4]">// 04</p>
                <h2 class="text-sm font-bold text-white">Documents <span class="text-[11px] font-normal text-white/30">(optional, strongly recommended)</span></h2>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <!-- Resume -->
              <div class="space-y-2">
                <p class="text-[10px] font-semibold uppercase tracking-widest text-white/45">Resume / CV</p>
                <input ref="resumeInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="onFileChange('resume', $event)" />
                <div v-if="resumeFile" class="flex items-center gap-2 rounded-xl border border-[#06b6d4]/20 bg-[#06b6d4]/10 px-3 py-2.5 text-sm">
                  <CheckCircle2 class="h-4 w-4 shrink-0 text-[#06b6d4]" />
                  <span class="truncate text-white/80 text-xs">{{ resumeFile.name }}</span>
                  <button type="button" class="ml-auto text-white/30 hover:text-white/60 transition-colors" @click="clearFile('resume')">
                    <X class="h-3.5 w-3.5" />
                  </button>
                </div>
                <button
                  v-else
                  type="button"
                  class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl border border-dashed border-white/15 bg-white/3 py-4 text-sm text-white/35 hover:border-[#7c3aed]/30 hover:bg-[#7c3aed]/5 hover:text-white/60 transition-all"
                  @click="pickFile('resume')"
                >
                  <Upload class="h-4 w-4" />
                  <span class="text-xs">PDF, DOC, DOCX</span>
                </button>
              </div>

              <!-- Sample work -->
              <div class="space-y-2">
                <p class="text-[10px] font-semibold uppercase tracking-widest text-white/45">Writing sample</p>
                <input ref="sampleInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="onFileChange('sample', $event)" />
                <div v-if="sampleFile" class="flex items-center gap-2 rounded-xl border border-[#06b6d4]/20 bg-[#06b6d4]/10 px-3 py-2.5 text-sm">
                  <CheckCircle2 class="h-4 w-4 shrink-0 text-[#06b6d4]" />
                  <span class="truncate text-white/80 text-xs">{{ sampleFile.name }}</span>
                  <button type="button" class="ml-auto text-white/30 hover:text-white/60 transition-colors" @click="clearFile('sample')">
                    <X class="h-3.5 w-3.5" />
                  </button>
                </div>
                <button
                  v-else
                  type="button"
                  class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl border border-dashed border-white/15 bg-white/3 py-4 text-sm text-white/35 hover:border-[#7c3aed]/30 hover:bg-[#7c3aed]/5 hover:text-white/60 transition-all"
                  @click="pickFile('sample')"
                >
                  <Upload class="h-4 w-4" />
                  <span class="text-xs">PDF, DOC, DOCX</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Submit -->
          <div class="space-y-4 pt-2">
            <button
              type="submit"
              :disabled="isSubmitting"
              class="cosmos-btn w-full rounded-2xl py-4 text-base font-black text-white disabled:opacity-40 transition-all"
            >
              <span v-if="isSubmitting">Transmitting application…</span>
              <span v-else class="flex items-center justify-center gap-2.5">
                Launch my application <ArrowRight class="h-5 w-5" />
              </span>
            </button>

            <p class="text-center text-xs text-white/30">
              Already have writer access?
              <RouterLink to="/writer/login" class="ml-1 font-semibold text-[#06b6d4] hover:underline">Sign in →</RouterLink>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes wink {
  0%, 100% { opacity: var(--op, 0.5); }
  50%       { opacity: calc(var(--op, 0.5) * 0.15); }
}

.cosmos-input {
  color: rgba(255, 255, 255, 0.85);
  caret-color: #06b6d4;
  outline: none;
}
.cosmos-input:focus {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.12);
}
.cosmos-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}
.cosmos-input option {
  background: #0c1225;
  color: rgba(255, 255, 255, 0.85);
}

.cosmos-btn {
  background: linear-gradient(135deg, #7c3aed 0%, #2563c8 55%, #06b6d4 100%);
  box-shadow: 0 0 32px rgba(124, 58, 237, 0.4), 0 8px 24px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
}
.cosmos-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.14) 0%, transparent 55%);
  pointer-events: none;
}
.cosmos-btn:hover:not(:disabled) {
  box-shadow: 0 0 48px rgba(124, 58, 237, 0.55), 0 12px 32px rgba(0, 0, 0, 0.6);
  filter: brightness(1.1);
}
.cosmos-btn:active:not(:disabled) {
  transform: scale(0.985);
}
</style>
