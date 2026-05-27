import { api, apiPath } from "./client";
import type {
  ClassOrder,
  ClassOrderDetail,
  ClassTask,
  ClassInstallment,
  PortalAccess,
  CreateClassOrderPayload,
  SubmitTaskPayload,
  GradeTaskPayload,
} from "@/types/classes";

export const classesApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<ClassOrder[] | { count: number; next: string | null; previous: string | null; results: ClassOrder[] }>(
      apiPath("/classes/"),
      { params },
    ),

  get: (id: number | string) =>
    api.get<ClassOrderDetail>(apiPath(`/classes/${id}/`)),

  create: (payload: CreateClassOrderPayload) =>
    api.post<ClassOrder>(apiPath("/classes/"), payload),

  update: (id: number | string, payload: Partial<CreateClassOrderPayload>) =>
    api.patch<ClassOrder>(apiPath(`/classes/${id}/`), payload),

  assignWriter: (id: number | string, writerId: number) =>
    api.post(apiPath(`/classes/${id}/assign-writer/`), { writer_id: writerId }),

  cancel: (id: number | string, reason?: string) =>
    api.post(apiPath(`/classes/${id}/cancel/`), { reason }),

  tasks: {
    list: (classId: number | string) =>
      api.get<ClassTask[]>(apiPath(`/classes/${classId}/tasks/`)),

    create: (classId: number | string, payload: { title: string; description: string; due_date: string; sequence?: number }) =>
      api.post<ClassTask>(apiPath(`/classes/${classId}/tasks/`), payload),

    submit: (classId: number | string, taskId: number | string, payload: SubmitTaskPayload) =>
      api.post<ClassTask>(apiPath(`/classes/${classId}/tasks/${taskId}/submit/`), payload),

    grade: (classId: number | string, taskId: number | string, payload: GradeTaskPayload) =>
      api.post<ClassTask>(apiPath(`/classes/${classId}/tasks/${taskId}/grade/`), payload),

    requestRevision: (classId: number | string, taskId: number | string, notes: string) =>
      api.post<ClassTask>(apiPath(`/classes/${classId}/tasks/${taskId}/request-revision/`), { notes }),
  },

  installments: {
    list: (classId: number | string) =>
      api.get<ClassInstallment[]>(apiPath(`/classes/${classId}/installments/`)),

    markPaid: (classId: number | string, installmentId: number | string) =>
      api.post<ClassInstallment>(apiPath(`/classes/${classId}/installments/${installmentId}/mark-paid/`), {}),
  },

  portalAccess: {
    get: (classId: number | string) =>
      api.get<PortalAccess>(apiPath(`/classes/${classId}/portal-access/`)),

    update: (classId: number | string, payload: Partial<PortalAccess>) =>
      api.patch<PortalAccess>(apiPath(`/classes/${classId}/portal-access/`), payload),
  },
};
