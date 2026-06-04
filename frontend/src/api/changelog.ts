import { api, apiPath } from "./client";

export interface ChangelogEntry {
  id: number;
  portal_surface: "client" | "writer" | "staff" | "public";
  entry_type: "feature" | "improvement" | "fix" | "maintenance" | "notice";
  version: string;
  title: string;
  body: string;
  is_pinned: boolean;
  published_at: string | null;
}

export const changelogApi = {
  list: (params?: { surface?: string; website?: number; limit?: number }) =>
    api.get<ChangelogEntry[]>(apiPath("/changelog/"), { params }),
};
