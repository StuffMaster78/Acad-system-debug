export type ToastType = "success" | "error" | "warn" | "info";

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

export interface ModalConfig {
  name: string;
  payload?: Record<string, unknown>;
}
