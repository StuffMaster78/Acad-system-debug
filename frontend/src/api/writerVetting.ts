import { api, apiPath } from "./client";

const BASE = "/writer-vetting";

export type QuizType = "grammar" | "subject" | "essay";
export type QuestionType = "multiple_choice" | "true_false" | "essay";

export interface VettingChoice {
  id?: number;
  text: string;
  is_correct: boolean;
  order: number;
}

export interface VettingQuestion {
  id: number;
  quiz: number;
  question_type: QuestionType;
  text: string;
  explanation: string;
  points: number;
  order: number;
  is_active: boolean;
  choices: VettingChoice[];
  created_at: string;
  updated_at: string;
}

export interface VettingQuizSummary {
  id: number;
  quiz_type: QuizType;
  title: string;
  description: string;
  pass_score: number;
  time_limit_minutes: number;
  max_attempts: number;
  is_active: boolean;
  is_required_for_approval: boolean;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface VettingQuizDetail extends VettingQuizSummary {
  instructions: string;
  questions: VettingQuestion[];
}

export interface ApplicationQuizStatus {
  quiz_id: number;
  quiz_title: string;
  quiz_type: QuizType;
  pass_score: number;
  required: boolean;
  passed: boolean | null;
  attempt: { id: number; status: string; score: string | null; passed: boolean | null; submitted_at: string | null } | null;
}

export interface ApplicationQuizStatusResponse {
  required_quizzes: ApplicationQuizStatus[];
  all_required_passed: boolean;
  has_required_quizzes: boolean;
}

export interface QuizPayload {
  quiz_type: QuizType;
  title: string;
  description?: string;
  instructions?: string;
  pass_score?: number;
  time_limit_minutes?: number;
  max_attempts?: number;
  is_active?: boolean;
  is_required_for_approval?: boolean;
}

export interface QuestionPayload {
  question_type: QuestionType;
  text: string;
  explanation?: string;
  points?: number;
  order?: number;
  is_active?: boolean;
  choices?: VettingChoice[];
}

// ── Writer-facing types ───────────────────────────────────────────────────────

export interface WriterQuizChoice {
  id: number;
  text: string;
  order: number;
}

export interface WriterQuizQuestion {
  id: number;
  question_type: QuestionType;
  text: string;
  order: number;
  points: number;
  choices: WriterQuizChoice[];
}

export interface WriterQuizCard {
  id: number;
  quiz_type: QuizType;
  title: string;
  description: string;
  instructions: string;
  pass_score: number;
  time_limit_minutes: number;
  max_attempts: number;
  question_count: number;
  latest_attempt: WriterAttempt | null;
  attempts_used: number;
  can_attempt: boolean;
}

export type AttemptStatus = "in_progress" | "submitted" | "passed" | "failed" | "pending_review";

export interface WriterAttempt {
  id: number;
  quiz: number;
  quiz_title: string;
  quiz_type: QuizType;
  pass_score: number;
  attempt_number: number;
  status: AttemptStatus;
  score: string | null;
  passed: boolean | null;
  started_at: string;
  submitted_at: string | null;
  reviewer_notes: string;
  quiz_detail?: {
    id: number; title: string; instructions: string;
    questions: WriterQuizQuestion[];
  };
}

export interface AttemptAnswer {
  question_id: number;
  selected_choice_id?: number | null;
  essay_response?: string;
}

export const writerVettingApi = {
  // Quizzes
  quizzes: (params?: Record<string, unknown>) =>
    api.get<VettingQuizSummary[]>(apiPath(`${BASE}/quizzes/`), { params }),

  quiz: (id: number) =>
    api.get<VettingQuizDetail>(apiPath(`${BASE}/quizzes/${id}/`)),

  createQuiz: (payload: QuizPayload) =>
    api.post<VettingQuizSummary>(apiPath(`${BASE}/quizzes/`), payload),

  updateQuiz: (id: number, payload: Partial<QuizPayload>) =>
    api.patch<VettingQuizSummary>(apiPath(`${BASE}/quizzes/${id}/`), payload),

  deleteQuiz: (id: number) =>
    api.delete(apiPath(`${BASE}/quizzes/${id}/`)),

  // Questions
  questions: (quizId: number) =>
    api.get<VettingQuestion[]>(apiPath(`${BASE}/quizzes/${quizId}/questions/`)),

  createQuestion: (quizId: number, payload: QuestionPayload) =>
    api.post<VettingQuestion>(apiPath(`${BASE}/quizzes/${quizId}/questions/`), payload),

  updateQuestion: (id: number, payload: Partial<QuestionPayload>) =>
    api.patch<VettingQuestion>(apiPath(`${BASE}/questions/${id}/`), payload),

  deleteQuestion: (id: number) =>
    api.delete(apiPath(`${BASE}/questions/${id}/`)),

  // ── Writer-facing ─────────────────────────────────────────────────────────
  myQuizzes: () =>
    api.get<WriterQuizCard[]>(apiPath(`${BASE}/my/quizzes/`)),

  myAttempts: () =>
    api.get<WriterAttempt[]>(apiPath(`${BASE}/my/attempts/`)),

  startAttempt: (quizId: number) =>
    api.post<WriterAttempt>(apiPath(`${BASE}/quizzes/${quizId}/start/`)),

  submitAttempt: (attemptId: number, answers: AttemptAnswer[]) =>
    api.post<WriterAttempt>(apiPath(`${BASE}/attempts/${attemptId}/submit/`), { answers }),

  attemptDetail: (attemptId: number) =>
    api.get<WriterAttempt>(apiPath(`${BASE}/attempts/${attemptId}/`)),

  // Admin: quiz status for a specific applicant (by email)
  applicationQuizStatus: (email: string, websiteId?: number) =>
    api.get<ApplicationQuizStatusResponse>(apiPath(`${BASE}/admin/application-status/`), {
      params: { email, ...(websiteId ? { website_id: websiteId } : {}) },
    }),
};
