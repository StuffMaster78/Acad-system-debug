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

export interface AdminInvoice {
  id: number;
  reference: string;
  title: string;
  purpose: string;
  description: string | null;
  amount: string;
  currency: string;
  status: string;
  client: number | null;
  recipient_email: string | null;
  recipient_name: string | null;
  order_number: string | null;
  issued_at: string | null;
  due_at: string | null;
  paid_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
  website?: number | null;
  website_id?: number | null;
  website_name?: string | null;
  statement_descriptor_snapshot?: string;
}

export interface CreateInvoicePayload {
  title: string;
  purpose: string;
  amount: string;
  due_at: string;
  description?: string;
  recipient_email?: string;
  recipient_name?: string;
  currency?: string;
  order_number?: string;
}

export interface AdminPaymentRequest {
  id: number;
  reference: string;
  title: string;
  purpose: string;
  description: string | null;
  amount: string;
  currency: string;
  status: string;
  recipient_email: string | null;
  recipient_name: string | null;
  issued_at: string | null;
  due_at: string | null;
  paid_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreatePaymentRequestPayload {
  title: string;
  purpose: string;
  amount: string;
  due_at: string;
  description?: string;
  recipient_email?: string;
  recipient_name?: string;
}

export interface InstallmentScheduleItem {
  sequence_number: number;
  amount: string;
  due_at: string;
}

export interface InstallmentPreparePaymentResult {
  payment_intent_reference: string;
  provider_data: Record<string, unknown>;
  installment_id: number;
  installment_sequence: number;
  amount: string;
  currency: string;
  invoice_reference: string;
}

type ListResponse<T> = T[] | { count: number; next: string | null; previous: string | null; results: T[] };

export const billingApi = {
  // Client-facing
  myInvoices: () =>
    api.get<ClientInvoice[]>(apiPath("/billing/my/invoices/")),
  myInvoice: (id: number) =>
    api.get<ClientInvoice>(apiPath(`/billing/my/invoices/${id}/`)),
  myPaymentRequests: () =>
    api.get<ClientPaymentRequest[]>(apiPath("/billing/my/payment-requests/")),
  myPaymentRequest: (id: number) =>
    api.get<ClientPaymentRequest>(apiPath(`/billing/my/payment-requests/${id}/`)),

  // Admin-facing — invoices
  invoices: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminInvoice>>(apiPath("/billing/invoices/"), { params }),
  createInvoice: (payload: CreateInvoicePayload) =>
    api.post<AdminInvoice>(apiPath("/billing/invoices/"), payload),
  issueInvoice: (id: number) =>
    api.post<AdminInvoice>(apiPath(`/billing/invoices/${id}/issue/`), {}),

  // Admin-facing — payment requests
  paymentRequests: (params?: Record<string, unknown>) =>
    api.get<ListResponse<AdminPaymentRequest>>(apiPath("/billing/payment-requests/"), { params }),
  createPaymentRequest: (payload: CreatePaymentRequestPayload) =>
    api.post<AdminPaymentRequest>(apiPath("/billing/payment-requests/"), payload),
  issuePaymentRequest: (id: number) =>
    api.post<AdminPaymentRequest>(apiPath(`/billing/payment-requests/${id}/issue/`), {}),

  // Installment schedule management (admin)
  invoiceInstallments: (invoiceId: number) =>
    api.get<Installment[]>(apiPath(`/billing/invoices/${invoiceId}/installments/`)),
  createInstallmentSchedule: (invoiceId: number, schedule: InstallmentScheduleItem[]) =>
    api.post<Installment[]>(apiPath(`/billing/invoices/${invoiceId}/installments/`), { schedule }),
  cancelInstallment: (installmentId: number) =>
    api.post<Installment>(apiPath(`/billing/installments/${installmentId}/cancel/`), {}),

  // Installment payment (client + admin)
  prepareInstallmentPayment: (installmentId: number, provider: string) =>
    api.post<InstallmentPreparePaymentResult>(
      apiPath(`/billing/installments/${installmentId}/prepare-payment/`),
      { provider },
    ),
};
