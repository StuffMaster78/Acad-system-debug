import { api, apiPath } from "./client";
import type {
  PayoutRequest,
  PayoutRequestPayload,
  WalletBalance,
  WalletEntry,
  WalletHold,
} from "@/types/wallet";

type ListResponse<T> = T[] | { results: T[] };

export const walletsApi = {
  me: () => api.get<WalletBalance>(apiPath("/wallets/me/")),
  entries: (params?: Record<string, unknown>) =>
    api.get<ListResponse<WalletEntry>>(apiPath("/wallets/me/entries/"), { params }),
  holds: (params?: Record<string, unknown>) =>
    api.get<ListResponse<WalletHold>>(apiPath("/wallets/me/holds/"), { params }),
  payoutRequests: (params?: Record<string, unknown>) =>
    api.get<ListResponse<PayoutRequest>>(apiPath("/wallets/me/payout-requests/"), { params }),
  requestPayout: (payload: PayoutRequestPayload) =>
    api.post<PayoutRequest>(apiPath("/wallets/me/payout-requests/"), payload),
};
