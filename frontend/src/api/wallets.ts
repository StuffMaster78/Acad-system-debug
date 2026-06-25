import { api, apiPath } from "./client";
import type {
  PayoutRequest,
  PayoutRequestPayload,
  TopupPayload,
  TopupResponse,
  WalletBalance,
  WalletEntry,
  WalletHold,
} from "@/types/wallet";

export interface PrewarmCheckoutResult {
  reference: string;
  checkout_url: string;
  amount: string;
}

export const paymentsApi = {
  /** Pre-warm a Stripe Checkout Session before the order is submitted.
   *  Call when the client selects "Pay by card" and a quote exists.
   *  Pass the returned reference as preauth_reference on order creation
   *  to skip the second Stripe API call. */
  prewarmOrderCheckout: (amount: number, currency = "USD") =>
    api.post<{ payment_intent: { reference: string; checkout_url: string; amount: string }; provider_data: Record<string, unknown> }>(
      apiPath("/payments/checkout/"),
      { provider: "stripe", purpose: "ORDER", amount, currency },
    ),
};

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
  initiateTopup: (payload: TopupPayload) =>
    api.post<{ payment_intent: TopupResponse["payment_intent"]; provider_data: Record<string, unknown> }>(
      apiPath("/payments/checkout/"),
      {
        provider: payload.provider,
        purpose: "wallet_top_up",
        amount: payload.amount,
        currency: payload.currency ?? "USD",
        metadata: payload.metadata ?? {},
      },
    ),
};
