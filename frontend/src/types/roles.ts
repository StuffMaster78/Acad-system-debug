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
}
