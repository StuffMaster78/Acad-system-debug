import { api, apiPath } from "./client";

export interface Installment {
  id: number;
  invoice: number;
  sequence_number: number;
  amount: string;
  amount_paid: string;
  remaining_amount: string;
  due_at: string | null;
  paid_at: string | null;
  cancelled_at: string | null;
  is_paid: boolean;
  is_partially_paid: boolean;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientInvoice {
  id: number;
  reference: string;
  title: string;
  description: string | null;
  amount: string;
  currency: string;
  status: string;
  due_at: string | null;
  issued_at: string | null;
  paid_at: string | null;
  installments: Installment[];
  total_paid: string;
  remaining_balance: string;
  is_fully_paid: boolean;
  next_installment: Installment | null;
}

export interface ClientPaymentRequest {
  id: number;
  reference: string;
  title: string;
  description: string | null;
  amount: string;
  currency: string;
  status: string;
  due_at: string | null;
  issued_at: string | null;
  paid_at: string | null;
  payment_intent_reference: string | null;
  remaining_balance: string;
  is_fully_paid: boolean;
}

export const billingApi = {
  myInvoices: () =>
    api.get<ClientInvoice[]>(apiPath("/billing/my/invoices/")),
  myInvoice: (id: number) =>
    api.get<ClientInvoice>(apiPath(`/billing/my/invoices/${id}/`)),
  myPaymentRequests: () =>
    api.get<ClientPaymentRequest[]>(apiPath("/billing/my/payment-requests/")),
  myPaymentRequest: (id: number) =>
    api.get<ClientPaymentRequest>(apiPath(`/billing/my/payment-requests/${id}/`)),
};
