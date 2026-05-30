import { api, apiPath } from "./client";

export interface ReferralCodeRecord {
  id: number;
  code: string;
  referral_link: string | null;
  created_at: string;
  usage_stats: {
    total_referrals: number;
    successful_referrals: number;
    flagged_referrals: number;
    voided_referrals: number;
    orders_placed: number;
    conversion_rate: number;
    is_active: boolean;
  } | null;
}

export interface ReferralRecord {
  id: number;
  referee: { id: number; username: string; email: string } | null;
  referral_code: string | null;
  created_at: string;
  bonus_awarded: boolean;
}

export interface InvitationResult {
  sent: boolean;
  referee_email: string;
  invitation_sent: boolean;
}

export const referralsApi = {
  myCode: () => api.get<ReferralCodeRecord>(apiPath("/referrals/referral-codes/my-code/")),
  myReferrals: () =>
    api.get<ReferralRecord[] | { results: ReferralRecord[]; count: number }>(
      apiPath("/referrals/referrals/"),
    ),
  sendInvitation: (email: string) =>
    api.post<InvitationResult>(apiPath("/referrals/send-invitation/"), { email }),
};
