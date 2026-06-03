<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  AlertCircle, CheckCircle2, ChevronRight, Clock,
  GraduationCap, RefreshCw, XCircle,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import {
  writerVettingApi,
  type AttemptAnswer, type WriterAttempt, type WriterQuizCard, type WriterQuizQuestion,
} from "@/api/writerVetting";

// ── State ─────────────────────────────────────────────────────────────────────
const quizzes = ref<WriterQuizCard[]>([]);
const loading  = ref(true);
const notice   = ref<{ type: "success" | "error"; msg: string } | null>(null);

// Active quiz-taking session
const activeAttempt  = ref<WriterAttempt | null>(null);
const activeQuestions = ref<WriterQuizQuestion[]>([]);
const answers        = ref<Record<number, AttemptAnswer>>({});  // keyed by question_id
const submitting     = ref(false);
const result         = ref<WriterAttempt | null>(null);
const timerLeft      = ref<number | null>(null);
let timerInterval: ReturnType<typeof setInterval> | null = null;

function toast(type: "success" | "error", msg: string) {
  notice.value = { type, msg };
  setTimeout(() => { notice.value = null; }, 5000);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const STATUS_TONE: Record<string, "success" | "warning" | "neutral" | "danger"> = {
  in_progress:    "neutral",
  submitted:      "warning",
  passed:         "success",
  failed:         "danger",
  pending_review: "warning",
};
const STATUS_LABEL: Record<string, string> = {
  in_progress:    "In Progress",
  submitted:      "Submitted",
  passed:         "Passed ✓",
  failed:         "Failed",
  pending_review: "Under Review",
};
const QUIZ_TYPE_LABEL: Record<string, string> = {
  grammar: "Grammar Test",
  subject: "Subject Knowledge",
  essay:   "Essay Prompt",
};

function fmtDate(v?: string | null) {
  if (!v) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(v));
}

const totalPoints = computed(() =>
  activeQuestions.value.reduce((s, q) => s + q.points, 0),
);
const answeredCount = computed(() => Object.keys(answers.value).length);

// ── Load ──────────────────────────────────────────────────────────────────────
async function load() {
  loading.value = true;
  try {
    const { data } = await writerVettingApi.myQuizzes();
    quizzes.value = data;
  } catch { toast("error", "Could not load quizzes."); }
  finally { loading.value = false; }
}

onMounted(load);

// ── Start quiz ────────────────────────────────────────────────────────────────
async function startQuiz(quizId: number) {
  try {
    const { data } = await writerVettingApi.startAttempt(quizId);
    activeAttempt.value = data;
    activeQuestions.value = data.quiz_detail?.questions ?? [];
    answers.value = {};
    result.value = null;

    // Initialise empty answers
    for (const q of activeQuestions.value) {
      answers.value[q.id] = { question_id: q.id };
    }

    // Start timer if quiz has a time limit
    const limit = quizzes.value.find(q => q.id === quizId)?.time_limit_minutes ?? 0;
    if (limit > 0) startTimer(limit * 60);
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    toast("error", detail ?? "Could not start quiz.");
  }
}

function startTimer(seconds: number) {
  timerLeft.value = seconds;
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    if (timerLeft.value === null) return;
    timerLeft.value--;
    if (timerLeft.value <= 0) {
      clearInterval(timerInterval!);
      submitQuiz(); // auto-submit when time runs out
    }
  }, 1000);
}

function fmtTimer(s: number) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

// ── Answer selection ──────────────────────────────────────────────────────────
function selectChoice(questionId: number, choiceId: number) {
  answers.value = {
    ...answers.value,
    [questionId]: { question_id: questionId, selected_choice_id: choiceId },
  };
}

function setEssay(questionId: number, text: string) {
  answers.value = {
    ...answers.value,
    [questionId]: { question_id: questionId, essay_response: text },
  };
}

// ── Submit ────────────────────────────────────────────────────────────────────
async function submitQuiz() {
  if (!activeAttempt.value) return;
  submitting.value = true;
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
  try {
    const payload = Object.values(answers.value);
    const { data } = await writerVettingApi.submitAttempt(activeAttempt.value.id, payload);
    result.value = data;
    activeAttempt.value = null;
    activeQuestions.value = [];
    await load(); // refresh quiz cards with updated attempt status
  } catch { toast("error", "Submission failed. Please try again."); }
  finally { submitting.value = false; }
}

function closeResult() {
  result.value = null;
}
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold text-neutral-900">Vetting Quizzes</h1>
        <p class="mt-0.5 text-sm text-neutral-500">Complete the required quizzes to unlock your writer account.</p>
      </div>
      <button
        class="flex items-center gap-1.5 rounded-lg border border-neutral-200 px-3 py-2 text-sm hover:bg-neutral-50"
        @click="load"
      >
        <RefreshCw class="size-4" :class="loading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <!-- Notice -->
    <div
      v-if="notice"
      class="rounded-lg px-4 py-3 text-sm font-medium"
      :class="notice.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
    >{{ notice.msg }}</div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <RefreshCw class="size-7 text-neutral-300 animate-spin" />
    </div>

    <!-- Empty -->
    <div v-else-if="!quizzes.length" class="flex flex-col items-center py-16 text-neutral-400">
      <GraduationCap class="size-12 mb-3" />
      <p class="text-sm font-medium">No quizzes assigned yet.</p>
      <p class="text-xs mt-1">Check back once your application is under review.</p>
    </div>

    <!-- Quiz cards -->
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="quiz in quizzes"
        :key="quiz.id"
        class="rounded-xl border bg-white p-5 space-y-3"
        :class="quiz.latest_attempt?.status === 'passed'
          ? 'border-green-200 bg-green-50'
          : quiz.latest_attempt?.status === 'failed'
          ? 'border-red-100'
          : 'border-neutral-200'"
      >
        <!-- Type chip + title -->
        <div class="flex items-start justify-between gap-2">
          <div>
            <span class="inline-block rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 mb-1.5">
              {{ QUIZ_TYPE_LABEL[quiz.quiz_type] ?? quiz.quiz_type }}
            </span>
            <h2 class="font-semibold text-neutral-900 leading-tight">{{ quiz.title }}</h2>
          </div>
          <CheckCircle2 v-if="quiz.latest_attempt?.status === 'passed'" class="size-6 text-green-500 flex-shrink-0 mt-0.5" />
          <XCircle v-else-if="quiz.latest_attempt?.status === 'failed'" class="size-6 text-red-400 flex-shrink-0 mt-0.5" />
        </div>

        <!-- Meta -->
        <div class="flex flex-wrap gap-3 text-xs text-neutral-500">
          <span class="flex items-center gap-1">
            <GraduationCap class="size-3.5" /> {{ quiz.question_count }} question{{ quiz.question_count !== 1 ? 's' : '' }}
          </span>
          <span v-if="quiz.quiz_type !== 'essay'" class="flex items-center gap-1">
            ✓ Pass: {{ quiz.pass_score }}%
          </span>
          <span v-if="quiz.time_limit_minutes" class="flex items-center gap-1">
            <Clock class="size-3.5" /> {{ quiz.time_limit_minutes }} min
          </span>
        </div>

        <!-- Attempt status -->
        <div v-if="quiz.latest_attempt" class="flex items-center justify-between">
          <StatusPill
            :status="quiz.latest_attempt.status"
            :tone="STATUS_TONE[quiz.latest_attempt.status]"
            :label="STATUS_LABEL[quiz.latest_attempt.status]"
          />
          <span v-if="quiz.latest_attempt.score != null" class="text-sm font-semibold text-neutral-700">
            {{ quiz.latest_attempt.score }}%
          </span>
        </div>

        <!-- Attempts used -->
        <p v-if="quiz.max_attempts > 0" class="text-xs text-neutral-400">
          {{ quiz.attempts_used }} / {{ quiz.max_attempts }} attempts used
        </p>

        <!-- CTA -->
        <button
          v-if="quiz.can_attempt"
          class="w-full flex items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors"
          @click="startQuiz(quiz.id)"
        >
          {{ quiz.latest_attempt ? 'Retake quiz' : 'Start quiz' }}
          <ChevronRight class="size-4" />
        </button>
        <p v-else-if="!quiz.can_attempt && !quiz.latest_attempt" class="text-xs text-neutral-400 text-center">
          No attempts remaining
        </p>
      </div>
    </div>

    <!-- ── QUIZ TAKING MODAL ─────────────────────────────────────────────── -->
    <div v-if="activeAttempt" class="fixed inset-0 z-50 overflow-y-auto bg-black/50 flex items-start justify-center py-8 px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl">

        <!-- Header -->
        <div class="sticky top-0 bg-white rounded-t-2xl border-b border-neutral-100 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 class="font-semibold text-neutral-900">{{ activeAttempt.quiz_title }}</h2>
            <p class="text-xs text-neutral-500 mt-0.5">
              {{ answeredCount }} / {{ activeQuestions.length }} answered
            </p>
          </div>
          <div class="flex items-center gap-3">
            <span v-if="timerLeft !== null" class="flex items-center gap-1.5 text-sm font-mono font-semibold" :class="timerLeft < 60 ? 'text-red-600' : 'text-neutral-700'">
              <Clock class="size-4" /> {{ fmtTimer(timerLeft) }}
            </span>
            <span class="text-xs text-neutral-500">{{ totalPoints }} pts total</span>
          </div>
        </div>

        <!-- Questions -->
        <div class="px-6 py-6 space-y-8">
          <div
            v-for="(q, idx) in activeQuestions"
            :key="q.id"
            class="space-y-3"
          >
            <div class="flex items-start gap-3">
              <span class="flex size-7 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-xs font-bold text-indigo-700">
                {{ idx + 1 }}
              </span>
              <p class="text-sm font-medium text-neutral-900 leading-relaxed">{{ q.text }}</p>
            </div>

            <!-- MCQ / True-False choices -->
            <div v-if="q.question_type !== 'essay'" class="space-y-2 pl-10">
              <label
                v-for="choice in q.choices"
                :key="choice.id"
                class="flex items-center gap-3 rounded-lg border p-3 cursor-pointer transition-colors"
                :class="answers[q.id]?.selected_choice_id === choice.id
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-neutral-200 hover:border-indigo-300 hover:bg-indigo-50/50'"
              >
                <input
                  type="radio"
                  :name="`q_${q.id}`"
                  :value="choice.id"
                  :checked="answers[q.id]?.selected_choice_id === choice.id"
                  class="text-indigo-600"
                  @change="selectChoice(q.id, choice.id)"
                />
                <span class="text-sm text-neutral-800">{{ choice.text }}</span>
              </label>
            </div>

            <!-- Essay textarea -->
            <div v-else class="pl-10">
              <textarea
                :value="answers[q.id]?.essay_response ?? ''"
                rows="6"
                placeholder="Write your response here…"
                class="w-full rounded-lg border border-neutral-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                @input="setEssay(q.id, ($event.target as HTMLTextAreaElement).value)"
              />
              <p class="mt-1 text-xs text-neutral-400">{{ (answers[q.id]?.essay_response ?? '').length }} characters</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="sticky bottom-0 bg-white rounded-b-2xl border-t border-neutral-100 px-6 py-4 flex items-center justify-between gap-4">
          <p class="text-xs text-neutral-400">
            <AlertCircle class="size-3.5 inline mr-1" />
            Once submitted you cannot change your answers.
          </p>
          <button
            :disabled="submitting"
            class="flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            @click="submitQuiz"
          >
            <RefreshCw v-if="submitting" class="size-4 animate-spin" />
            {{ submitting ? 'Submitting…' : 'Submit quiz' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── RESULT MODAL ──────────────────────────────────────────────────── -->
    <div v-if="result" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 text-center space-y-4">
        <component
          :is="result.status === 'passed' ? CheckCircle2 : result.status === 'pending_review' ? GraduationCap : XCircle"
          class="mx-auto size-16"
          :class="result.status === 'passed' ? 'text-green-500' : result.status === 'pending_review' ? 'text-indigo-500' : 'text-red-400'"
        />

        <h2 class="text-2xl font-bold text-neutral-900">
          {{ result.status === 'passed' ? 'You passed!' : result.status === 'pending_review' ? 'Submitted for review' : 'Not quite there' }}
        </h2>

        <div v-if="result.score !== null" class="text-4xl font-extrabold" :class="result.status === 'passed' ? 'text-green-600' : 'text-red-500'">
          {{ result.score }}%
        </div>

        <p class="text-sm text-neutral-500">
          <template v-if="result.status === 'passed'">
            Congratulations — your quiz is complete. Your application will be reviewed shortly.
          </template>
          <template v-else-if="result.status === 'pending_review'">
            Your essay response has been submitted and will be reviewed by our team.
          </template>
          <template v-else>
            You scored {{ result.score }}% — a pass score of {{ result.pass_score }}% is required.
            <span v-if="(quizzes.find(q => q.id === result!.quiz)?.attempts_used ?? 0) < (quizzes.find(q => q.id === result!.quiz)?.max_attempts ?? 0)">
              You can retake the quiz.
            </span>
          </template>
        </p>

        <button
          class="w-full rounded-xl bg-indigo-600 py-3 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors"
          @click="closeResult"
        >
          Done
        </button>
      </div>
    </div>
  </div>
</template>
