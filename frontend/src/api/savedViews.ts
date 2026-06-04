import { api, apiPath } from "./client";

export interface SavedView {
  id: number;
  view_type: string;
  name: string;
  filters: Record<string, unknown>;
  is_default: boolean;
  created_at: string;
}

export const savedViewsApi = {
  list: (viewType?: string) =>
    api.get<SavedView[]>(apiPath("/saved-views/"), { params: viewType ? { view_type: viewType } : {} }),
  save: (payload: { view_type: string; name: string; filters: Record<string, unknown>; is_default?: boolean }) =>
    api.post<SavedView>(apiPath("/saved-views/"), payload),
  update: (id: number, payload: Partial<{ name: string; filters: Record<string, unknown>; is_default: boolean }>) =>
    api.patch<SavedView>(apiPath(`/saved-views/${id}/`), payload),
  delete: (id: number) =>
    api.delete(apiPath(`/saved-views/${id}/`)),
};
