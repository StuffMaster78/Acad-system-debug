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
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface VettingQuizDetail extends VettingQuizSummary {
  instructions: string;
  questions: VettingQuestion[];
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
};
