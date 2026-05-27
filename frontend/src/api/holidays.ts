import { api, apiPath } from "./client";

type PageResponse<T> = { count: number; next: string | null; previous: string | null; results: T[] } | T[];

export interface SpecialDay {
  id: number;
  name: string;
  slug: string;
  date: string;
  event_type: string;
  description: string | null;
  is_annual: boolean;
  is_international: boolean;
  is_active: boolean;
  priority: number;
  countries: string[];
  countries_display: string[];
  event_date_this_year: string;
  days_until: number;
  is_upcoming: boolean;
  created_by: number | null;
  created_by_username: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateSpecialDayPayload {
  name: string;
  slug: string;
  date: string;
  event_type: string;
  description?: string;
  is_annual?: boolean;
  is_international?: boolean;
  is_active?: boolean;
  priority?: number;
  countries?: string[];
}

export interface HolidayReminder {
  id: number;
  special_day: number;
  special_day_name: string;
  special_day_date: string | null;
  sent_to: number | null;
  sent_to_username: string | null;
  status: string;
  reminder_date: string;
  discount_created: boolean;
  discount_code: string | null;
  created_at: string;
  updated_at: string;
}

export interface HolidayDiscountCampaign {
  id: number;
  special_day: number;
  special_day_name: string;
  discount: number | null;
  discount_code: string | null;
  discount_percentage: string | null;
  year: number;
  is_active: boolean;
  created_by: number | null;
  created_by_username: string | null;
  created_at: string;
}

export const holidaysApi = {
  specialDays: (params?: Record<string, unknown>) =>
    api.get<PageResponse<SpecialDay>>(apiPath("/holidays/special-days/"), { params }),
  specialDay: (id: number | string) =>
    api.get<SpecialDay>(apiPath(`/holidays/special-days/${id}/`)),
  createSpecialDay: (payload: CreateSpecialDayPayload) =>
    api.post<SpecialDay>(apiPath("/holidays/special-days/"), payload),
  updateSpecialDay: (id: number | string, payload: Partial<CreateSpecialDayPayload>) =>
    api.patch<SpecialDay>(apiPath(`/holidays/special-days/${id}/`), payload),
  deleteSpecialDay: (id: number | string) =>
    api.delete(apiPath(`/holidays/special-days/${id}/`)),
  generateDiscount: (id: number | string, year?: number) =>
    api.post<HolidayDiscountCampaign>(apiPath(`/holidays/special-days/${id}/generate_discount/`), { year }),
  upcomingSpecialDays: (daysAhead = 30, country?: string) =>
    api.get<SpecialDay[]>(apiPath("/holidays/special-days/upcoming/"), { params: { days_ahead: daysAhead, country } }),

  reminders: (params?: Record<string, unknown>) =>
    api.get<PageResponse<HolidayReminder>>(apiPath("/holidays/reminders/"), { params }),
  markReminderSent: (id: number | string) =>
    api.post<HolidayReminder>(apiPath(`/holidays/reminders/${id}/mark_sent/`), {}),
  createReminderDiscount: (id: number | string, year?: number) =>
    api.post<{ message: string; discount_code: string; discount_id: number }>(
      apiPath(`/holidays/reminders/${id}/create_discount/`),
      { year },
    ),
  checkAndCreateReminders: () =>
    api.post<{ message: string; reminders: HolidayReminder[] }>(
      apiPath("/holidays/reminders/check_and_create/"),
      {},
    ),
  notifyAdmins: () =>
    api.post<{ message: string }>(apiPath("/holidays/reminders/notify_admins/"), {}),

  campaigns: (params?: Record<string, unknown>) =>
    api.get<PageResponse<HolidayDiscountCampaign>>(apiPath("/holidays/campaigns/"), { params }),
};
