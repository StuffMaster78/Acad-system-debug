export type UserRole =
  | "superadmin"
  | "admin"
  | "writer"
  | "client"
  | "editor"
  | "support";

export interface AuthUser {
  id: number;
  email: string;
  full_name?: string;
  role: UserRole;
  avatar_url?: string | null;
  bio?: string | null;
  phone?: string | null;
  location?: string | null;
  timezone?: string | null;
}
