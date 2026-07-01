import { api, apiPath } from "./client";

export interface MFADevice {
  id: number;
  name: string | null;
  method: string;
  is_active: boolean;
  is_verified: boolean;
  is_primary?: boolean;
}

export interface MFAState {
  required: boolean;
  preferred_method: string | null;
  available_methods: string[];
  device_count: number;
}

export interface BackupCodesResponse {
  codes: string[];
}

export interface MFAVerifyDeviceResponse {
  success: boolean;
  device_id: number;
  message: string;
}

export interface TOTPSetupResponse {
  device_id: number;
  name: string;
  secret: string;
  provisioning_uri: string;
  qr_code_base64: string;
}

export const mfaSettingsApi = {
  state: () =>
    api.get<MFAState>(apiPath("/auth/mfa/state/")),

  totpSetup: (name?: string) =>
    api.post<TOTPSetupResponse>(apiPath("/auth/mfa/totp/setup/"), { name }),

  devices: () =>
    api.get<MFADevice[]>(apiPath("/auth/mfa/devices/")),

  registerDevice: (payload: {
    method: string;
    name: string;
    secret?: string;
    phone_number?: string;
    email?: string;
    is_primary?: boolean;
  }) =>
    api.post<MFADevice>(apiPath("/auth/mfa/devices/register/"), payload),

  verifyDevice: (deviceId: number, code: string) =>
    api.post<MFAVerifyDeviceResponse>(apiPath("/auth/mfa/devices/verify/"), {
      device_id: deviceId,
      code,
    }),

  setPrimary: (deviceId: number) =>
    api.post<MFADevice>(apiPath("/auth/mfa/devices/set-primary/"), {
      device_id: deviceId,
    }),

  activate: (deviceId: number) =>
    api.post<MFADevice>(apiPath("/auth/mfa/devices/activate/"), {
      device_id: deviceId,
    }),

  deactivate: (deviceId: number) =>
    api.post<MFADevice>(apiPath("/auth/mfa/devices/deactivate/"), {
      device_id: deviceId,
    }),

  generateBackupCodes: (count?: number) =>
    api.post<BackupCodesResponse>(
      apiPath("/auth/mfa/backup-codes/generate/"),
      count ? { count } : {},
    ),
};
