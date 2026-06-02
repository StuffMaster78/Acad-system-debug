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

const base = (path: string) => apiPath(`/class-management${path}`);

export const classesApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<ClassOrder[] | { count: number; next: string | null; previous: string | null; results: ClassOrder[] }>(
      base("/classes/"),
      { params },
    ),

  get: (id: number | string) =>
    api.get<ClassOrderDetail>(base(`/classes/${id}/`)),

  create: (payload: CreateClassOrderPayload) =>
    api.post<ClassOrder>(base("/classes/"), payload),

  update: (id: number | string, payload: Partial<CreateClassOrderPayload>) =>
    api.patch<ClassOrder>(base(`/classes/${id}/`), payload),

  assignWriter: (id: number | string, writerId: number) =>
    api.post(base(`/classes/${id}/assignments/`), { writer_id: writerId }),

  cancel: (id: number | string, reason?: string) =>
    api.post(base(`/classes/${id}/cancel/`), { reason }),

  startWork: (id: number | string) =>
    api.post(base(`/classes/${id}/start-work/`), {}),

  complete: (id: number | string) =>
    api.post(base(`/classes/${id}/complete/`), {}),

  tasks: {
    list: (classId: number | string) =>
      api.get<ClassTask[]>(base(`/classes/${classId}/tasks/`)),

    create: (classId: number | string, payload: { title: string; description: string; due_date: string; sequence?: number }) =>
      api.post<ClassTask>(base(`/classes/${classId}/tasks/`), payload),

    submit: (classId: number | string, taskId: number | string, payload: SubmitTaskPayload) =>
      api.post<ClassTask>(base(`/classes/${classId}/tasks/${taskId}/submit/`), payload),

    grade: (classId: number | string, taskId: number | string, payload: GradeTaskPayload) =>
      api.post<ClassTask>(base(`/classes/${classId}/tasks/${taskId}/complete/`), payload),

    cancel: (classId: number | string, taskId: number | string, notes: string) =>
      api.post<ClassTask>(base(`/classes/${classId}/tasks/${taskId}/cancel/`), { notes }),
  },

  installments: {
    list: (classId: number | string) =>
      api.get<ClassInstallment[]>(base(`/classes/${classId}/payments/installments/`)),

    preparePayment: (
      classId: number | string,
      payload: { amount: string | number; use_wallet?: boolean; installment_id?: number | string },
    ) =>
      api.post(base(`/classes/${classId}/payments/prepare/`), payload),

    waive: (classId: number | string, installmentId: number | string, reason = "") =>
      api.post<ClassInstallment>(base(`/classes/${classId}/payments/installments/${installmentId}/waive/`), { reason }),
  },

  portalAccess: {
    get: (classId: number | string) =>
      api.post<PortalAccess>(base(`/classes/${classId}/access/view-details/`), {
        reason: "Class portal access view",
      }),

    update: (classId: number | string, payload: Partial<PortalAccess>) =>
      api.patch<PortalAccess>(base(`/classes/${classId}/access/details/`), payload),
  },

  timeline: (classId: number | string) =>
    api.get<Array<Record<string, unknown>>>(base(`/classes/${classId}/timeline/`)),
};
