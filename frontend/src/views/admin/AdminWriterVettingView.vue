<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  CheckCircle2, ChevronRight, ClipboardList, GraduationCap,
  Pencil, Plus, RefreshCw, Trash2, X, FileText, ToggleLeft,
  ToggleRight, AlertCircle, Clock, Target,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import {
  writerVettingApi,
  type VettingQuestion, type VettingQuizDetail, type VettingQuizSummary,
  type QuizType, type QuestionType,
} from "@/api/writerVetting";

// ── State ───────────────────────────────────────────────────────────────────
const quizzes    = ref<VettingQuizSummary[]>([]);
const activeQuiz = ref<VettingQuizDetail | null>(null);
const loading    = ref(false);
const saving     = ref(false);
const notice     = ref<{ type: "success" | "error"; msg: string } | null>(null);
type StatusPillTone = "neutral" | "success" | "warning" | "danger";

const typeFilter = ref<QuizType | "all">("all");

const filtered = computed(() =>
  typeFilter.value === "all"
    ? quizzes.value
    : quizzes.value.filter((q) => q.quiz_type === typeFilter.value),
);

function toast(type: "success" | "error", msg: string) {
  notice.value = { type, msg };
  setTimeout(() => { notice.value = null; }, 4000);
}

// ── Quiz list ────────────────────────────────────────────────────────────────
async function loadQuizzes() {
  loading.value = true;
  try {
    const { data } = await writerVettingApi.quizzes();
    quizzes.value = Array.isArray(data) ? data : [];
  } catch { toast("error", "Failed to load quizzes."); }
  finally { loading.value = false; }
}

async function openQuiz(id: number) {
  activeQuiz.value = null;
  try {
    const { data } = await writerVettingApi.quiz(id);
    activeQuiz.value = data;
  } catch { toast("error", "Failed to load quiz."); }
}

// ── Quiz create / edit form ──────────────────────────────────────────────────
const quizForm = ref(false);
const editingQuizId = ref<number | null>(null);
const quizDraft = reactive({
  quiz_type: "grammar" as QuizType,
  title: "",
  description: "",
  instructions: "",
  pass_score: 75,
  time_limit_minutes: 30,
  max_attempts: 3,
});

function openNewQuiz() {
  editingQuizId.value = null;
  Object.assign(quizDraft, {
    quiz_type: "grammar", title: "", description: "", instructions: "",
    pass_score: 75, time_limit_minutes: 30, max_attempts: 3,
  });
  quizForm.value = true;
}

function openEditQuiz(q: VettingQuizSummary) {
  editingQuizId.value = q.id;
  Object.assign(quizDraft, {
    quiz_type: q.quiz_type, title: q.title, description: q.description ?? "",
    instructions: (activeQuiz.value?.instructions ?? ""),
    pass_score: q.pass_score, time_limit_minutes: q.time_limit_minutes,
    max_attempts: q.max_attempts,
  });
  quizForm.value = true;
}

async function saveQuiz() {
  if (!quizDraft.title.trim()) return;
  saving.value = true;
  try {
    if (editingQuizId.value) {
      const { data } = await writerVettingApi.updateQuiz(editingQuizId.value, { ...quizDraft });
      quizzes.value = quizzes.value.map((q) => q.id === editingQuizId.value ? { ...q, ...data } : q);
      if (activeQuiz.value?.id === editingQuizId.value) {
        activeQuiz.value = { ...activeQuiz.value, ...data };
      }
      toast("success", `"${data.title}" updated.`);
    } else {
      const { data } = await writerVettingApi.createQuiz({ ...quizDraft });
      quizzes.value = [data, ...quizzes.value];
      toast("success", `"${data.title}" created.`);
    }
    quizForm.value = false;
  } catch { toast("error", "Failed to save quiz."); }
  finally { saving.value = false; }
}

async function deleteQuiz(id: number) {
  if (!confirm("Delete this quiz and all its questions?")) return;
  try {
    await writerVettingApi.deleteQuiz(id);
    quizzes.value = quizzes.value.filter((q) => q.id !== id);
    if (activeQuiz.value?.id === id) activeQuiz.value = null;
    toast("success", "Quiz deleted.");
  } catch { toast("error", "Failed to delete quiz."); }
}

// ── Question create / edit form ──────────────────────────────────────────────
const qForm = ref(false);
const editingQId = ref<number | null>(null);
const qDraft = reactive({
  question_type: "multiple_choice" as QuestionType,
  text: "",
  explanation: "",
  points: 1,
  order: 0,
  choices: [
    { text: "", is_correct: false, order: 0 },
    { text: "", is_correct: false, order: 1 },
    { text: "", is_correct: false, order: 2 },
    { text: "", is_correct: false, order: 3 },
  ] as { text: string; is_correct: boolean; order: number }[],
});

const needsChoices = computed(
  () => qDraft.question_type === "multiple_choice" || qDraft.question_type === "true_false",
);

function openNewQuestion() {
  editingQId.value = null;
  Object.assign(qDraft, {
    question_type: "multiple_choice", text: "", explanation: "", points: 1,
    order: (activeQuiz.value?.questions.length ?? 0),
    choices: [
      { text: "", is_correct: false, order: 0 },
      { text: "", is_correct: false, order: 1 },
      { text: "", is_correct: false, order: 2 },
      { text: "", is_correct: false, order: 3 },
    ],
  });
  qForm.value = true;
}

function openEditQuestion(q: VettingQuestion) {
  editingQId.value = q.id;
  Object.assign(qDraft, {
    question_type: q.question_type,
    text: q.text,
    explanation: q.explanation ?? "",
    points: q.points,
    order: q.order,
    choices: q.choices.length
      ? q.choices.map((c) => ({ text: c.text, is_correct: c.is_correct, order: c.order }))
      : [
          { text: "", is_correct: false, order: 0 },
          { text: "", is_correct: false, order: 1 },
        ],
  });
  qForm.value = true;
}

function addChoice() {
  qDraft.choices.push({ text: "", is_correct: false, order: qDraft.choices.length });
}

function removeChoice(i: number) {
  qDraft.choices.splice(i, 1);
  qDraft.choices.forEach((c, idx) => { c.order = idx; });
}

function setTrueFalse() {
  qDraft.choices = [
    { text: "True", is_correct: true, order: 0 },
    { text: "False", is_correct: false, order: 1 },
  ];
}

async function saveQuestion() {
  if (!qDraft.text.trim() || !activeQuiz.value) return;
  saving.value = true;
  try {
    const payload = {
      question_type: qDraft.question_type,
      text: qDraft.text.trim(),
      explanation: qDraft.explanation.trim(),
      points: qDraft.points,
      order: qDraft.order,
      choices: needsChoices.value
        ? qDraft.choices.filter((c) => c.text.trim())
        : [],
    };

    if (editingQId.value) {
      const { data } = await writerVettingApi.updateQuestion(editingQId.value, payload);
      if (activeQuiz.value) {
        activeQuiz.value.questions = activeQuiz.value.questions.map((q) =>
          q.id === editingQId.value ? data : q,
        );
      }
      toast("success", "Question updated.");
    } else {
      const { data } = await writerVettingApi.createQuestion(activeQuiz.value.id, payload);
      activeQuiz.value.questions = [...(activeQuiz.value.questions ?? []), data];
      const quiz = quizzes.value.find((q) => q.id === activeQuiz.value!.id);
      if (quiz) quiz.question_count = (quiz.question_count ?? 0) + 1;
      toast("success", "Question added.");
    }
    qForm.value = false;
  } catch { toast("error", "Failed to save question."); }
  finally { saving.value = false; }
}

async function deleteQuestion(q: VettingQuestion) {
  if (!activeQuiz.value) return;
  try {
    await writerVettingApi.deleteQuestion(q.id);
    activeQuiz.value.questions = activeQuiz.value.questions.filter((x) => x.id !== q.id);
    const quiz = quizzes.value.find((qz) => qz.id === activeQuiz.value!.id);
    if (quiz) quiz.question_count = Math.max(0, (quiz.question_count ?? 1) - 1);
    toast("success", "Question removed.");
  } catch { toast("error", "Failed to remove question."); }
}

// ── Helpers ──────────────────────────────────────────────────────────────────
const QUIZ_TYPE_LABELS: Record<QuizType, string> = {
  grammar: "Grammar", subject: "Subject knowledge", essay: "Essay prompt",
};
const QUIZ_TYPE_TONES: Record<QuizType, StatusPillTone> = {
  grammar: "neutral", subject: "success", essay: "warning",
};
const Q_TYPE_LABELS: Record<QuestionType, string> = {
  multiple_choice: "Multiple choice", true_false: "True / False", essay: "Essay",
};

onMounted(loadQuizzes);
</script>

<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-5">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold text-gray-900">Writer Vetting — Quiz &amp; Question Bank</h1>
          <p class="text-sm text-gray-500 mt-0.5">Build grammar tests, subject quizzes, and essay prompts to vet applicants</p>
        </div>
        <div class="flex gap-2">
          <button
            class="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="loadQuizzes"
          >
            <RefreshCw class="w-4 h-4" :class="loading ? 'animate-spin' : ''" /> Refresh
          </button>
          <button
            class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
            @click="openNewQuiz"
          >
            <Plus class="w-4 h-4" /> New quiz
          </button>
        </div>
      </div>

      <!-- Type filter chips -->
      <div class="flex gap-2 mt-4">
        <button
          v-for="opt in [
            { key: 'all', label: 'All' },
            { key: 'grammar', label: 'Grammar' },
            { key: 'subject', label: 'Subject knowledge' },
            { key: 'essay', label: 'Essay prompts' },
          ]"
          :key="opt.key"
          class="px-3 py-1 text-xs font-medium rounded-full border transition-colors"
          :class="typeFilter === opt.key
            ? 'bg-indigo-600 text-white border-indigo-600'
            : 'bg-white text-gray-600 border-gray-300 hover:border-gray-400'"
          @click="typeFilter = opt.key as typeof typeFilter"
        >{{ opt.label }}</button>
      </div>
    </div>

    <!-- Notice -->
    <div
      v-if="notice"
      class="mx-6 mt-4 px-4 py-3 rounded-lg text-sm font-medium"
      :class="notice.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
    >{{ notice.msg }}</div>

    <!-- Body: quiz list + question panel -->
    <div class="flex h-[calc(100vh-185px)]">

      <!-- Quiz list -->
      <div class="w-80 border-r border-gray-200 bg-white overflow-y-auto flex-shrink-0">
        <div v-if="loading" class="flex justify-center py-12">
          <RefreshCw class="w-6 h-6 text-gray-400 animate-spin" />
        </div>
        <div v-else-if="!filtered.length" class="flex flex-col items-center py-12 text-gray-400">
          <ClipboardList class="w-10 h-10 mb-3" />
          <p class="text-sm">No quizzes yet.</p>
          <button class="mt-2 text-xs text-indigo-600 hover:underline" @click="openNewQuiz">Create one →</button>
        </div>
        <div v-else class="divide-y divide-gray-100">
          <button
            v-for="quiz in filtered"
            :key="quiz.id"
            class="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors"
            :class="{ 'bg-indigo-50': activeQuiz?.id === quiz.id }"
            @click="openQuiz(quiz.id)"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="font-medium text-gray-900 truncate">{{ quiz.title }}</span>
              <ChevronRight class="w-4 h-4 text-gray-400 flex-shrink-0" />
            </div>
            <div class="mt-1 flex items-center gap-2 flex-wrap">
              <StatusPill
                :status="quiz.quiz_type"
                :tone="QUIZ_TYPE_TONES[quiz.quiz_type]"
                :label="QUIZ_TYPE_LABELS[quiz.quiz_type]"
              />
              <span class="text-xs text-gray-400">{{ quiz.question_count }} question{{ quiz.question_count !== 1 ? 's' : '' }}</span>
              <span v-if="!quiz.is_active" class="text-xs text-gray-400 italic">inactive</span>
            </div>
          </button>
        </div>
      </div>

      <!-- Question editor panel -->
      <div v-if="activeQuiz" class="flex-1 overflow-y-auto p-6 space-y-4">

        <!-- Quiz header -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <h2 class="text-lg font-semibold text-gray-900">{{ activeQuiz.title }}</h2>
                <StatusPill
                  :status="activeQuiz.quiz_type"
                  :tone="QUIZ_TYPE_TONES[activeQuiz.quiz_type]"
                  :label="QUIZ_TYPE_LABELS[activeQuiz.quiz_type]"
                />
                <StatusPill
                  :status="activeQuiz.is_active ? 'active' : 'inactive'"
                  :tone="activeQuiz.is_active ? 'success' : 'neutral'"
                  :label="activeQuiz.is_active ? 'Active' : 'Inactive'"
                />
              </div>
              <p v-if="activeQuiz.description" class="mt-1 text-sm text-gray-500">{{ activeQuiz.description }}</p>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <button
                class="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-gray-300 rounded-lg hover:bg-gray-50"
                @click="openEditQuiz(activeQuiz)"
              >
                <Pencil class="w-3.5 h-3.5" /> Edit
              </button>
              <button
                class="flex items-center gap-1.5 px-3 py-1.5 text-xs text-red-600 border border-red-200 rounded-lg hover:bg-red-50"
                @click="deleteQuiz(activeQuiz.id)"
              >
                <Trash2 class="w-3.5 h-3.5" /> Delete
              </button>
            </div>
          </div>

          <!-- Quiz stats -->
          <div class="mt-4 flex flex-wrap gap-4 text-sm text-gray-600">
            <span class="flex items-center gap-1.5">
              <Target class="w-4 h-4 text-gray-400" /> Pass: {{ activeQuiz.pass_score }}%
            </span>
            <span class="flex items-center gap-1.5">
              <Clock class="w-4 h-4 text-gray-400" />
              {{ activeQuiz.time_limit_minutes ? `${activeQuiz.time_limit_minutes} min` : 'No limit' }}
            </span>
            <span class="flex items-center gap-1.5">
              <AlertCircle class="w-4 h-4 text-gray-400" />
              {{ activeQuiz.max_attempts ? `${activeQuiz.max_attempts} attempt${activeQuiz.max_attempts !== 1 ? 's' : ''}` : 'Unlimited' }}
            </span>
          </div>

          <div v-if="activeQuiz.instructions" class="mt-3 text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2 italic">
            {{ activeQuiz.instructions }}
          </div>
        </div>

        <!-- Questions -->
        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <h3 class="font-medium text-gray-900">
              Questions
              <span class="ml-1 text-xs text-gray-400">({{ activeQuiz.questions.length }})</span>
            </h3>
            <button
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
              @click="openNewQuestion"
            >
              <Plus class="w-3.5 h-3.5" /> Add question
            </button>
          </div>

          <div v-if="!activeQuiz.questions.length" class="flex flex-col items-center py-12 text-gray-400">
            <FileText class="w-10 h-10 mb-3" />
            <p class="text-sm">No questions yet. Add the first one.</p>
          </div>

          <div v-else class="divide-y divide-gray-100">
            <div
              v-for="(q, idx) in activeQuiz.questions"
              :key="q.id"
              class="px-5 py-4"
            >
              <div class="flex items-start gap-3">
                <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-xs font-bold text-indigo-600">
                  {{ idx + 1 }}
                </span>
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-3">
                    <p class="text-sm font-medium text-gray-900">{{ q.text }}</p>
                    <div class="flex gap-1.5 flex-shrink-0">
                      <button
                        class="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-700"
                        @click="openEditQuestion(q)"
                      >
                        <Pencil class="w-3.5 h-3.5" />
                      </button>
                      <button
                        class="p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-600"
                        @click="deleteQuestion(q)"
                      >
                        <Trash2 class="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <div class="mt-1 flex items-center gap-2 text-xs text-gray-500">
                    <span class="px-1.5 py-0.5 rounded-full bg-gray-100">{{ Q_TYPE_LABELS[q.question_type] }}</span>
                    <span>{{ q.points }} pt{{ q.points !== 1 ? 's' : '' }}</span>
                  </div>

                  <!-- Choices preview -->
                  <ul v-if="q.choices.length" class="mt-2 space-y-0.5">
                    <li
                      v-for="c in q.choices"
                      :key="c.id"
                      class="flex items-center gap-2 text-xs"
                      :class="c.is_correct ? 'text-green-700 font-medium' : 'text-gray-500'"
                    >
                      <CheckCircle2 v-if="c.is_correct" class="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
                      <span v-else class="w-3.5 h-3.5 rounded-full border border-gray-300 flex-shrink-0" />
                      {{ c.text }}
                    </li>
                  </ul>

                  <p v-if="q.explanation" class="mt-1.5 text-xs text-gray-400 italic">
                    Explanation: {{ q.explanation }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state when no quiz selected -->
      <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 p-12">
        <GraduationCap class="w-14 h-14 mb-4" />
        <p class="text-base font-medium text-gray-600">Select a quiz to view its questions</p>
        <p class="mt-1 text-sm">or create a new quiz to get started.</p>
      </div>
    </div>

    <!-- Quiz form modal -->
    <div v-if="quizForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-900">{{ editingQuizId ? 'Edit quiz' : 'New quiz' }}</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="quizForm = false"><X class="w-5 h-5" /></button>
        </div>
        <div class="px-6 py-5 space-y-4 max-h-[70vh] overflow-y-auto">
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Quiz type</span>
            <select v-model="quizDraft.quiz_type" class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="grammar">Grammar test (MCQ / true-false, auto-scored)</option>
              <option value="subject">Subject knowledge (MCQ / true-false, auto-scored)</option>
              <option value="essay">Essay / writing prompt (manual review)</option>
            </select>
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Title <span class="text-red-500">*</span></span>
            <input v-model="quizDraft.title" type="text" placeholder="e.g. Grammar Proficiency Test" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Description</span>
            <textarea v-model="quizDraft.description" rows="2" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
          </label>
          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Writer instructions</span>
            <textarea v-model="quizDraft.instructions" rows="2" placeholder="Instructions shown to the writer before they start…" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
          </label>
          <div v-if="quizDraft.quiz_type !== 'essay'" class="grid grid-cols-3 gap-3">
            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Pass score (%)</span>
              <input v-model.number="quizDraft.pass_score" type="number" min="0" max="100" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Time limit (min)</span>
              <input v-model.number="quizDraft.time_limit_minutes" type="number" min="0" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Max attempts</span>
              <input v-model.number="quizDraft.max_attempts" type="number" min="0" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
          </div>
        </div>
        <div class="flex gap-2 justify-end px-6 py-4 border-t border-gray-100">
          <button class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50" @click="quizForm = false">Cancel</button>
          <button
            :disabled="saving || !quizDraft.title.trim()"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            @click="saveQuiz"
          >
            <RefreshCw v-if="saving" class="w-4 h-4 animate-spin inline mr-1" />
            {{ editingQuizId ? 'Save changes' : 'Create quiz' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Question form modal -->
    <div v-if="qForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-xl mx-4 overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-900">{{ editingQId ? 'Edit question' : 'New question' }}</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="qForm = false"><X class="w-5 h-5" /></button>
        </div>
        <div class="px-6 py-5 space-y-4 max-h-[75vh] overflow-y-auto">
          <div class="grid grid-cols-2 gap-3">
            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Question type</span>
              <select
                v-model="qDraft.question_type"
                class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                @change="qDraft.question_type === 'true_false' && setTrueFalse()"
              >
                <option value="multiple_choice">Multiple choice</option>
                <option value="true_false">True / False</option>
                <option value="essay">Essay (open-ended)</option>
              </select>
            </label>
            <label class="block space-y-1">
              <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Points</span>
              <input v-model.number="qDraft.points" type="number" min="1" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </label>
          </div>

          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Question text <span class="text-red-500">*</span></span>
            <textarea v-model="qDraft.text" rows="3" placeholder="Write the question here…" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
          </label>

          <!-- Choices -->
          <div v-if="needsChoices" class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Answer choices</span>
              <button
                v-if="qDraft.question_type === 'multiple_choice'"
                class="text-xs text-indigo-600 hover:underline"
                type="button"
                @click="addChoice"
              >+ Add choice</button>
            </div>
            <div v-for="(choice, i) in qDraft.choices" :key="i" class="flex items-center gap-2">
              <label class="flex items-center gap-1.5 cursor-pointer flex-shrink-0" :title="choice.is_correct ? 'Correct' : 'Mark as correct'">
                <input
                  type="checkbox"
                  v-model="choice.is_correct"
                  class="rounded border-gray-300 text-green-600"
                />
                <span class="text-xs text-gray-500">Correct</span>
              </label>
              <input
                v-model="choice.text"
                type="text"
                :placeholder="`Option ${i + 1}`"
                :disabled="qDraft.question_type === 'true_false'"
                class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50"
              />
              <button
                v-if="qDraft.question_type === 'multiple_choice' && qDraft.choices.length > 2"
                class="text-gray-400 hover:text-red-500"
                type="button"
                @click="removeChoice(i)"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
            <p class="text-xs text-gray-400">Check the box next to the correct answer(s).</p>
          </div>

          <label class="block space-y-1">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500">Explanation <span class="text-gray-400">(optional — shown after answering)</span></span>
            <textarea v-model="qDraft.explanation" rows="2" placeholder="Explain the correct answer…" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
          </label>
        </div>
        <div class="flex gap-2 justify-end px-6 py-4 border-t border-gray-100">
          <button class="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50" @click="qForm = false">Cancel</button>
          <button
            :disabled="saving || !qDraft.text.trim()"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            @click="saveQuestion"
          >
            <RefreshCw v-if="saving" class="w-4 h-4 animate-spin inline mr-1" />
            {{ editingQId ? 'Save question' : 'Add question' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
