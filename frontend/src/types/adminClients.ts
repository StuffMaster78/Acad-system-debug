export interface AdminClient {
  id: number;
  userId: number;
  username: string;
  fullName: string;
  email: string;
  website: string;
  country: string;
  timezone: string;
  walletBalance: string;
  totalSpent: string;
  loyaltyPoints: number;
  loyaltyTier: string;
  preferredWriters: string[];
  isActive: boolean;
  isSuspended: boolean;
  isBlacklisted: boolean;
  dateJoined: string | null;
  lastLogin: string | null;
}

export interface AdminClientMetric {
  label: string;
  value: string | number;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}
