import { api, apiPath } from "./client";

export const walletsApi = {
  me: () => api.get(apiPath("/wallets/me/")),
  entries: (params?: Record<string, unknown>) =>
    api.get(apiPath("/wallets/me/entries/"), { params }),
  holds: (params?: Record<string, unknown>) =>
    api.get(apiPath("/wallets/me/holds/"), { params }),
  payoutRequests: (params?: Record<string, unknown>) =>
    api.get(apiPath("/wallets/me/payout-requests/"), { params }),
  requestPayout: (payload: Record<string, unknown>) =>
    api.post(apiPath("/wallets/me/payout-requests/"), payload),
};
