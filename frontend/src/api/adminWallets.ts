import { api, apiPath } from "./client";
import type {
  AdminWalletAdjustmentPayload,
  AdminWalletEntryRecord,
  AdminWalletHoldPayload,
  AdminWalletHoldRecord,
  AdminWalletRecord,
} from "@/types/adminWallets";

type ListResponse<T> = T[] | { results: T[] };

export const adminWalletsApi = {
  wallets: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminWalletRecord>>(
      apiPath("/wallets/admin/wallets/"),
      { params },
    ),
  wallet: (walletId: number) =>
    api.get<AdminWalletRecord>(
      apiPath(`/wallets/admin/wallets/${walletId}/`),
    ),
  entries: (walletId: number, params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminWalletEntryRecord>>(
      apiPath(`/wallets/admin/wallets/${walletId}/entries/`),
      { params },
    ),
  holds: (walletId: number, params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminWalletHoldRecord>>(
      apiPath(`/wallets/admin/wallets/${walletId}/holds/`),
      { params },
    ),
  fund: (walletId: number, payload: AdminWalletAdjustmentPayload) =>
    api.post<AdminWalletEntryRecord>(
      apiPath(`/wallets/admin/wallets/${walletId}/fund/`),
      payload,
    ),
  debit: (walletId: number, payload: AdminWalletAdjustmentPayload) =>
    api.post<AdminWalletEntryRecord>(
      apiPath(`/wallets/admin/wallets/${walletId}/debit/`),
      payload,
    ),
  createHold: (walletId: number, payload: AdminWalletHoldPayload) =>
    api.post<AdminWalletHoldRecord>(
      apiPath(`/wallets/admin/wallets/${walletId}/holds/create/`),
      payload,
    ),
  releaseHold: (holdId: number) =>
    api.post<AdminWalletHoldRecord>(
      apiPath(`/wallets/admin/holds/${holdId}/release/`),
    ),
  captureHold: (holdId: number) =>
    api.post<AdminWalletHoldRecord>(
      apiPath(`/wallets/admin/holds/${holdId}/capture/`),
    ),
  reconcile: (walletId: number) =>
    api.post<{ status: string; wallet_id: number }>(
      apiPath(`/wallets/admin/wallets/${walletId}/reconcile/`),
    ),
  repair: (walletId: number) =>
    api.post<{ status: string; wallet_id: number }>(
      apiPath(`/wallets/admin/wallets/${walletId}/repair/`),
    ),
};
