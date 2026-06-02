import { api, apiPath } from "./client";
import type { OrderConfigOption, PaginatedResponse } from "@/types/config";

export type ConfigCollection = "paper-types" | "academic-levels" | "subjects" | "types-of-work" | "formatting-styles" | "english-types";

export interface ConfigOptionPayload {
  name: string;
  code?: string;
  website?: number | null;
  is_active?: boolean;
  description?: string;
}

function normalizeList<T>(payload: T[] | PaginatedResponse<T>): T[] {
  return Array.isArray(payload) ? payload : payload.results ?? [];
}

async function list(path: string, params?: Record<string, unknown>): Promise<OrderConfigOption[]> {
  const { data } = await api.get<OrderConfigOption[] | PaginatedResponse<OrderConfigOption>>(
    apiPath(path), { params },
  );
  return normalizeList(data);
}

export const orderConfigApi = {
  academicLevels: (params?: Record<string, unknown>) => list("/order-configs/academic-levels/", params),
  paperTypes: (params?: Record<string, unknown>) => list("/order-configs/paper-types/", params),
  formattingStyles: (params?: Record<string, unknown>) => list("/order-configs/formatting-styles/", params),
  subjects: (params?: Record<string, unknown>) => list("/order-configs/subjects/", params),
  typesOfWork: (params?: Record<string, unknown>) => list("/order-configs/types-of-work/", params),
  englishTypes: (params?: Record<string, unknown>) => list("/order-configs/english-types/", params),
  writerLevels: (params?: Record<string, unknown>) => list("/writer-management/level-settings/", params),

  listCollection: (collection: ConfigCollection, params?: Record<string, unknown>) =>
    api.get<OrderConfigOption[] | PaginatedResponse<OrderConfigOption>>(
      apiPath(`/order-configs/${collection}/`), { params },
    ),
  createOption: (collection: ConfigCollection, payload: ConfigOptionPayload) =>
    api.post<OrderConfigOption>(apiPath(`/order-configs/${collection}/`), payload),
  updateOption: (collection: ConfigCollection, id: number, payload: Partial<ConfigOptionPayload>) =>
    api.patch<OrderConfigOption>(apiPath(`/order-configs/${collection}/${id}/`), payload),
  deleteOption: (collection: ConfigCollection, id: number) =>
    api.delete(apiPath(`/order-configs/${collection}/${id}/`)),
};
