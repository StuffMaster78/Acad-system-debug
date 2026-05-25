import { api, apiPath } from "./client";
import type { OrderConfigOption, PaginatedResponse } from "@/types/config";

function normalizeList<T>(payload: T[] | PaginatedResponse<T>): T[] {
  return Array.isArray(payload) ? payload : payload.results ?? [];
}

async function list(path: string): Promise<OrderConfigOption[]> {
  const { data } = await api.get<OrderConfigOption[] | PaginatedResponse<OrderConfigOption>>(
    apiPath(path),
  );
  return normalizeList(data);
}

export const orderConfigApi = {
  academicLevels: () => list("/order-configs/academic-levels/"),
  paperTypes: () => list("/order-configs/paper-types/"),
  formattingStyles: () => list("/order-configs/formatting-styles/"),
  subjects: () => list("/order-configs/subjects/"),
  typesOfWork: () => list("/order-configs/types-of-work/"),
  englishTypes: () => list("/order-configs/english-types/"),
};
