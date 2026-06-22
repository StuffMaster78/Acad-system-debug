import { api, apiPath } from "./client";

const base = (path = "") => apiPath(`/users/subscriptions${path}`);

export type SubscriptionType =
  | "newsletter"
  | "blog_posts"
  | "coupon_updates"
  | "marketing_messages"
  | "unread_messages"
  | "transactional_messages"
  | "notifications"
  | "order_updates"
  | "promotional_offers"
  | "product_updates"
  | "security_alerts"
  | "account_updates";

export type DeliveryChannel = "email" | "sms" | "push" | "in_app";
export type Frequency = "immediate" | "daily" | "weekly" | "monthly";

export interface SubscriptionItem {
  subscription_type: SubscriptionType;
  is_subscribed: boolean;
  subscribed_at: string | null;
  unsubscribed_at: string | null;
  frequency: Frequency;
  preferred_channels: DeliveryChannel[];
}

export interface SubscriptionPreferences {
  id?: number;
  all_subscriptions_enabled: boolean;
  marketing_consent: boolean;
  marketing_consent_date: string | null;
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  in_app_enabled: boolean;
  dnd_enabled: boolean;
  dnd_start_hour: number;
  dnd_end_hour: number;
  transactional_enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

export const subscriptionsApi = {
  listAll: () =>
    api.get<SubscriptionItem[]>(base("/list-all/")),

  preferences: () =>
    api.get<SubscriptionPreferences>(base("/preferences/")),

  subscribe: (payload: {
    subscription_type: SubscriptionType;
    frequency?: Frequency;
    preferred_channels?: DeliveryChannel[];
  }) => api.post(base("/subscribe/"), payload),

  unsubscribe: (subscription_type: SubscriptionType) =>
    api.post(base("/unsubscribe/"), { subscription_type }),

  updateFrequency: (subscription_type: SubscriptionType, frequency: Frequency) =>
    api.put(base("/update-frequency/"), { subscription_type, frequency }),

  updateChannels: (subscription_type: SubscriptionType, preferred_channels: DeliveryChannel[]) =>
    api.put(base("/update-channels/"), { subscription_type, preferred_channels }),

  updatePreferences: (data: Partial<SubscriptionPreferences>) =>
    api.put(base("/update-preferences/"), data),
};
