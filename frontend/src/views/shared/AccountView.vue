<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { AlertTriangle, Camera, CheckCircle2, KeyRound, Loader2, MapPin, Monitor, PenLine, Phone, Plus, Shield, ShieldCheck, ShieldOff, Smartphone, Trash2, User, XCircle } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import UserAvatar from "@/components/ui/UserAvatar.vue";
import { authApi, type AccountDeletionState, type ProfileUpdateRequest } from "@/api/auth";
import { sessionsApi, type LoginSession } from "@/api/sessions";
import { mfaSettingsApi, type MFADevice } from "@/api/mfaSettings";
import { securityEventsApi, type SecurityEvent } from "@/api/securityEvents";
import { useAuthStore } from "@/stores/auth";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";
import type { UserRole } from "@/types/roles";

const props = defineProps<{ role: UserRole }>();

const auth = useAuthStore();
const writerWorkspace = useWriterWorkspaceStore();

const isWriter = computed(() => props.role === "writer");

// ── Sessions ─────────────────────────────────────────────────────────────────
const sessions = ref<LoginSession[]>([]);
const sessionsLoading = ref(false);
const sessionsError = ref("");
const sessionsNotice = ref("");
const revokingId = ref<number | null>(null);

async function loadSessions() {
  sessionsLoading.value = true;
  sessionsError.value = "";
  try {
    const { data } = await sessionsApi.list();
    sessions.value = Array.isArray(data) ? data : [];
  } catch {
    sessionsError.value = "Could not load active sessions.";
  } finally {
    sessionsLoading.value = false;
  }
}

async function revokeSession(id: number) {
  revokingId.value = id;
  try {
    await sessionsApi.revoke(id);
    sessions.value = sessions.value.filter((s) => s.id !== id);
    sessionsNotice.value = "Session revoked.";
  } catch {
    sessionsError.value = "Could not revoke session.";
  } finally {
    revokingId.value = null;
  }
}

async function revokeAllSessions() {
  if (!confirm("Sign out of all other sessions?")) return;
  try {
    await sessionsApi.revokeAll();
    await loadSessions();
    sessionsNotice.value = "All other sessions signed out.";
  } catch {
    sessionsError.value = "Could not sign out all sessions.";
  }
}

function formatDevice(session: LoginSession): string {
  if (session.device_name) return session.device_name;
  const ua = session.user_agent || "";
  if (/iPhone|iPad/.test(ua)) return "iPhone / iPad";
  if (/Android/.test(ua)) return "Android device";
  if (/Macintosh|Mac OS/.test(ua)) return "Mac";
  if (/Windows/.test(ua)) return "Windows PC";
  if (/Linux/.test(ua)) return "Linux";
  return "Unknown device";
}

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(iso));
}

onMounted(loadSessions);

// ── Avatar ──────────────────────────────────────────────────────────────────
const avatarInputRef = ref<HTMLInputElement | null>(null);
const avatarPreview = ref<string | null>(null);
const avatarUploading = ref(false);
const avatarError = ref("");

function triggerAvatarPicker() {
  avatarInputRef.value?.click();
}

async function onAvatarSelected(event: Event) {
  avatarError.value = "";
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    avatarError.value = "Please select an image file.";
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    avatarError.value = "Image must be under 5 MB.";
    return;
  }
  avatarPreview.value = URL.createObjectURL(file);
  avatarUploading.value = true;
  try {
    const { data } = await authApi.uploadAvatar(file);
    auth.updateUser({ avatar_url: data.avatar_url });
    avatarPreview.value = null;
  } catch {
    avatarError.value = "Upload failed. Please try again.";
    avatarPreview.value = null;
  } finally {
    avatarUploading.value = false;
    if (avatarInputRef.value) avatarInputRef.value.value = "";
  }
}

// ── Profile form ─────────────────────────────────────────────────────────────
const profileForm = reactive({
  full_name: auth.user?.full_name ?? "",
  bio: auth.user?.bio ?? "",
  phone: auth.user?.phone ?? "",
  location: auth.user?.location ?? "",
  timezone: auth.user?.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone,
});
const profileSaving = ref(false);
const profileNotice = ref("");
const profileError = ref("");
const profileRequests = ref<ProfileUpdateRequest[]>([]);
const profileRequestsLoading = ref(false);

const latestProfileRequest = computed(() => profileRequests.value[0] ?? null);

watch(() => auth.user, (u) => {
  if (!u) return;
  profileForm.full_name = u.full_name ?? "";
  profileForm.bio = u.bio ?? "";
  profileForm.phone = u.phone ?? "";
  profileForm.location = u.location ?? "";
  profileForm.timezone = u.timezone ?? profileForm.timezone;
}, { deep: true });

async function saveProfile() {
  profileError.value = "";
  profileNotice.value = "";
  profileSaving.value = true;
  try {
    const requested_changes: Record<string, unknown> = {
      display_name: profileForm.full_name || "",
      bio: profileForm.bio || "",
      country: profileForm.location || "",
      timezone: profileForm.timezone || "",
    };
    const { data } = await authApi.requestProfileUpdate({
      requested_changes,
      submitted_note: profileForm.phone
        ? `Phone update requested: ${profileForm.phone}`
        : "Submitted from account profile page.",
    });
    profileRequests.value = [data, ...profileRequests.value];
    profileNotice.value = "Profile change request submitted for staff review.";
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    profileError.value = detail ?? "Could not submit profile change request.";
  } finally {
    profileSaving.value = false;
  }
}

async function loadProfileRequests() {
  profileRequestsLoading.value = true;
  try {
    const { data } = await authApi.profileUpdateRequests();
    profileRequests.value = [...data].sort((a, b) =>
      String(b.created_at ?? "").localeCompare(String(a.created_at ?? "")),
    );
  } catch {
    profileRequests.value = [];
  } finally {
    profileRequestsLoading.value = false;
  }
}

// ── Writer professional profile ───────────────────────────────────────────────
const writerForm = reactive({
  display_name: "",
  bio: "",
});
const writerSaving = ref(false);
const writerNotice = ref("");
const writerError = ref("");

watch(() => writerWorkspace.profile, (p) => {
  if (!p) return;
  writerForm.display_name = (p.display_name as string | undefined) ?? "";
  writerForm.bio = (p.bio as string | undefined) ?? "";
}, { immediate: true, deep: true });

async function saveWriterProfile() {
  writerError.value = "";
  writerNotice.value = "";
  writerSaving.value = true;
  try {
    await writerWorkspace.saveProfile({
      display_name: writerForm.display_name || undefined,
      bio: writerForm.bio || undefined,
    });
    writerNotice.value = "Writer profile updated.";
  } catch {
    writerError.value = "Could not update writer profile.";
  } finally {
    writerSaving.value = false;
  }
}

// ── Password ─────────────────────────────────────────────────────────────────
const passwordForm = reactive({
  current_password: "",
  new_password: "",
  confirm_password: "",
});
const passwordSaving = ref(false);
const passwordNotice = ref("");
const passwordError = ref("");

async function changePassword() {
  passwordError.value = "";
  passwordNotice.value = "";
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = "New passwords do not match.";
    return;
  }
  if (passwordForm.new_password.length < 8) {
    passwordError.value = "New password must be at least 8 characters.";
    return;
  }
  passwordSaving.value = true;
  try {
    await authApi.changePassword({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    });
    passwordNotice.value = "Password changed.";
    passwordForm.current_password = "";
    passwordForm.new_password = "";
    passwordForm.confirm_password = "";
  } catch {
    passwordError.value = "Could not change password. Check your current password and try again.";
  } finally {
    passwordSaving.value = false;
  }
}

// ── Account deletion ───────────────────────────────────────────────────────
const deletionState = ref<AccountDeletionState | null>(null);
const deletionReason = ref("");
const deletionBusy = ref(false);
const deletionNotice = ref("");
const deletionError = ref("");

async function loadDeletionState() {
  try {
    const { data } = await authApi.accountDeletionState();
    deletionState.value = data;
  } catch {
    deletionState.value = null;
  }
}

async function requestDeletion() {
  deletionError.value = "";
  deletionNotice.value = "";
  deletionBusy.value = true;
  try {
    await authApi.requestAccountDeletion(deletionReason.value.trim());
    deletionNotice.value = "Account deletion request created.";
    deletionReason.value = "";
    await loadDeletionState();
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    deletionError.value = detail ?? "Could not create deletion request.";
  } finally {
    deletionBusy.value = false;
  }
}

async function confirmDeletion() {
  if (!confirm("Confirm account deletion scheduling? This action starts the retention and deletion workflow.")) return;
  deletionError.value = "";
  deletionNotice.value = "";
  deletionBusy.value = true;
  try {
    await authApi.confirmAccountDeletion();
    deletionNotice.value = "Account deletion scheduled.";
    await loadDeletionState();
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    deletionError.value = detail ?? "Could not confirm deletion.";
  } finally {
    deletionBusy.value = false;
  }
}

// ── Timezone list ─────────────────────────────────────────────────────────────
const timezones: string[] = (() => {
  try {
    return Intl.supportedValuesOf("timeZone");
  } catch {
    return [
      "UTC",
      "Africa/Nairobi",
      "Africa/Lagos",
      "America/New_York",
      "America/Chicago",
      "America/Denver",
      "America/Los_Angeles",
      "Europe/London",
      "Europe/Paris",
      "Asia/Dubai",
      "Asia/Kolkata",
      "Asia/Singapore",
      "Australia/Sydney",
    ];
  }
})();

onMounted(() => {
  if (isWriter.value && !writerWorkspace.profile) {
    writerWorkspace.hydrate().catch(() => undefined);
  }
  loadProfileRequests();
  loadDeletionState();
  loadMfaDevices();
  loadSecurityEvents();
});

// Current display user for avatar (merges preview)
const displayUser = computed(() => ({
  ...(auth.user ?? { id: 0, email: "", role: "client" as const }),
  avatar_url: avatarPreview.value ?? auth.user?.avatar_url,
}));

// ── MFA devices ──────────────────────────────────────────────────────────────
const mfaDevices = ref<MFADevice[]>([]);
const mfaLoading = ref(false);
const mfaError = ref("");
const mfaNotice = ref("");

const totpSetupStep = ref<"idle" | "scan" | "verify">("idle");
const totpSetupData = ref<{ device_id: number; qr_code_base64: string; secret: string } | null>(null);
const totpDeviceName = ref("Authenticator App");
const totpVerifyCode = ref("");
const totpBusy = ref(false);

async function loadMfaDevices() {
  mfaLoading.value = true;
  mfaError.value = "";
  try {
    const { data } = await mfaSettingsApi.devices();
    mfaDevices.value = Array.isArray(data) ? data : [];
  } catch {
    mfaError.value = "Could not load MFA devices.";
  } finally {
    mfaLoading.value = false;
  }
}

async function startTotpSetup() {
  totpBusy.value = true;
  mfaError.value = "";
  try {
    const { data } = await mfaSettingsApi.totpSetup(totpDeviceName.value || "Authenticator App");
    totpSetupData.value = { device_id: data.device_id, qr_code_base64: data.qr_code_base64, secret: data.secret };
    totpSetupStep.value = "scan";
  } catch {
    mfaError.value = "Could not initialise TOTP setup. Try again.";
  } finally {
    totpBusy.value = false;
  }
}

async function verifyTotpDevice() {
  if (!totpSetupData.value) return;
  totpBusy.value = true;
  mfaError.value = "";
  try {
    await mfaSettingsApi.verifyDevice(totpSetupData.value.device_id, totpVerifyCode.value.trim());
    mfaNotice.value = "Authenticator app linked successfully.";
    totpSetupStep.value = "idle";
    totpSetupData.value = null;
    totpVerifyCode.value = "";
    await loadMfaDevices();
  } catch {
    mfaError.value = "Invalid code — check your app and try again.";
  } finally {
    totpBusy.value = false;
  }
}

function cancelTotpSetup() {
  totpSetupStep.value = "idle";
  totpSetupData.value = null;
  totpVerifyCode.value = "";
  mfaError.value = "";
}

async function setPrimaryDevice(id: number) {
  mfaError.value = "";
  try {
    await mfaSettingsApi.setPrimary(id);
    await loadMfaDevices();
    mfaNotice.value = "Primary device updated.";
  } catch {
    mfaError.value = "Could not update primary device.";
  }
}

async function toggleDevice(device: MFADevice) {
  mfaError.value = "";
  try {
    if (device.is_active) {
      await mfaSettingsApi.deactivate(device.id);
    } else {
      await mfaSettingsApi.activate(device.id);
    }
    await loadMfaDevices();
    mfaNotice.value = `Device ${device.is_active ? "deactivated" : "activated"}.`;
  } catch {
    mfaError.value = "Could not update device.";
  }
}

const backupCodes = ref<string[]>([]);
const backupBusy = ref(false);

async function generateBackupCodes() {
  if (!confirm("Generating new backup codes will invalidate all previous codes. Continue?")) return;
  backupBusy.value = true;
  mfaError.value = "";
  try {
    const { data } = await mfaSettingsApi.generateBackupCodes();
    backupCodes.value = data.codes;
    mfaNotice.value = "Backup codes generated. Save these somewhere safe — they won't be shown again.";
  } catch {
    mfaError.value = "Could not generate backup codes.";
  } finally {
    backupBusy.value = false;
  }
}

function methodLabel(m: string) {
  if (m === "totp") return "Authenticator app";
  if (m === "email") return "Email OTP";
  if (m === "sms") return "SMS OTP";
  return m;
}

// ── Security events ──────────────────────────────────────────────────────────
const securityEvents = ref<SecurityEvent[]>([]);
const securityEventsLoading = ref(false);
const securityEventsError = ref("");

async function loadSecurityEvents() {
  securityEventsLoading.value = true;
  securityEventsError.value = "";
  try {
    const { data } = await securityEventsApi.list();
    securityEvents.value = Array.isArray(data) ? data.slice(0, 50) : [];
  } catch {
    securityEventsError.value = "Could not load security events.";
  } finally {
    securityEventsLoading.value = false;
  }
}

function severityTone(s: string): "success" | "warning" | "danger" | "neutral" {
  if (s === "low" || s === "info") return "neutral";
  if (s === "medium" || s === "warning") return "warning";
  if (s === "high" || s === "critical") return "danger";
  return "neutral";
}

</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <section class="border-b border-slate-200 pb-6">
      <p class="text-sm font-semibold uppercase tracking-wide text-signal">{{ role }}</p>
      <h1 class="mt-2 text-3xl font-semibold text-ink">My profile</h1>
      <p class="mt-2 max-w-2xl text-sm text-graphite">
        Manage your personal information, avatar, and account security.
      </p>
    </section>

    <!-- Avatar + identity hero -->
    <section class="flex flex-col gap-6 sm:flex-row sm:items-end">
      <!-- Avatar upload -->
      <div class="relative w-fit">
        <input
          ref="avatarInputRef"
          class="sr-only"
          type="file"
          accept="image/*"
          @change="onAvatarSelected"
        />
        <div class="relative">
          <UserAvatar :user="displayUser" size="xl" />
          <!-- uploading overlay -->
          <div
            v-if="avatarUploading"
            class="absolute inset-0 flex items-center justify-center rounded-full bg-black/40"
          >
            <Loader2 class="h-8 w-8 animate-spin text-white" />
          </div>
          <!-- hover upload trigger -->
          <button
            v-else
            class="absolute inset-0 flex items-center justify-center rounded-full bg-black/0 transition-colors hover:bg-black/40 focus:outline-none focus-visible:bg-black/40"
            type="button"
            title="Change profile picture"
            @click="triggerAvatarPicker"
          >
            <Camera class="h-7 w-7 text-white opacity-0 transition-opacity group-hover:opacity-100 [button:hover_&]:opacity-100" />
          </button>
        </div>
        <p v-if="avatarError" class="mt-2 text-xs text-berry">{{ avatarError }}</p>
      </div>

      <div>
        <p class="text-xl font-semibold text-ink">{{ auth.user?.full_name || auth.user?.email }}</p>
        <div class="mt-1.5 flex flex-wrap items-center gap-2">
          <StatusPill :label="role" tone="neutral" />
          <span v-if="auth.user?.location" class="flex items-center gap-1 text-xs text-graphite">
            <MapPin class="h-3.5 w-3.5" />{{ auth.user.location }}
          </span>
        </div>
        <p v-if="auth.user?.bio" class="mt-2 max-w-lg text-sm leading-6 text-graphite">{{ auth.user.bio }}</p>
        <button
          class="mt-3 text-xs font-semibold text-signal hover:underline"
          type="button"
          @click="triggerAvatarPicker"
        >
          Change photo
        </button>
      </div>
    </section>

    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Personal information -->
      <section class="overflow-hidden rounded-lg border border-slate-200 bg-white lg:col-span-2">
        <div class="flex items-center gap-3 border-b border-slate-200 px-6 py-4">
          <User class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold text-ink">Personal information</h2>
        </div>

        <div class="grid gap-4 p-6 sm:grid-cols-2">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Email</p>
            <p class="mt-1.5 rounded-md border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-graphite">
              {{ auth.user?.email ?? "—" }}
            </p>
            <p class="mt-1 text-xs text-graphite">Contact an administrator to change your email.</p>
          </div>

          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Role</p>
            <div class="mt-1.5">
              <StatusPill :label="role" tone="neutral" />
            </div>
          </div>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Display name</span>
            <input
              v-model.trim="profileForm.full_name"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="text"
              placeholder="Your full name"
            />
          </label>

          <label class="block">
            <span class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-graphite">
              <Phone class="h-3.5 w-3.5" /> Phone
            </span>
            <input
              v-model.trim="profileForm.phone"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="tel"
              placeholder="+254 700 000 000"
            />
          </label>

          <label class="block sm:col-span-2">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Bio</span>
            <textarea
              v-model.trim="profileForm.bio"
              class="focus-ring mt-1.5 w-full resize-none rounded-md border border-slate-200 px-3 py-2.5 text-sm"
              rows="3"
              maxlength="500"
              placeholder="A brief description about yourself…"
            />
            <span class="mt-0.5 block text-right text-xs text-graphite">{{ profileForm.bio.length }}/500</span>
          </label>

          <label class="block">
            <span class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-graphite">
              <MapPin class="h-3.5 w-3.5" /> Location
            </span>
            <input
              v-model.trim="profileForm.location"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="text"
              placeholder="e.g. Nairobi, Kenya"
            />
          </label>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Timezone</span>
            <select
              v-model="profileForm.timezone"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
            >
              <option v-for="tz in timezones" :key="tz" :value="tz">{{ tz }}</option>
            </select>
          </label>
        </div>

        <div class="flex items-center gap-4 border-t border-slate-200 px-6 py-4">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="profileSaving"
            @click="saveProfile"
          >
            <Loader2 v-if="profileSaving" class="h-4 w-4 animate-spin" />
            Save profile
          </button>
          <p v-if="profileNotice" class="text-sm font-medium text-signal">{{ profileNotice }}</p>
          <p v-if="profileError" class="text-sm font-medium text-berry">{{ profileError }}</p>
        </div>
        <div class="border-t border-slate-100 bg-slate-50 px-6 py-4">
          <div v-if="profileRequestsLoading" class="flex items-center gap-2 text-sm text-graphite">
            <Loader2 class="h-4 w-4 animate-spin" />
            Checking profile requests...
          </div>
          <div v-else-if="latestProfileRequest" class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Latest profile change request</p>
              <p class="mt-1 text-sm text-ink">
                Status:
                <span class="font-semibold capitalize">{{ latestProfileRequest.status.replace(/_/g, " ") }}</span>
              </p>
              <p v-if="latestProfileRequest.review_note" class="mt-1 text-xs text-graphite">{{ latestProfileRequest.review_note }}</p>
            </div>
            <p class="text-xs text-graphite">
              Submitted {{ latestProfileRequest.created_at ? new Date(latestProfileRequest.created_at).toLocaleString() : "recently" }}
            </p>
          </div>
          <p v-else class="text-sm text-graphite">
            Profile edits are submitted for review before they are applied.
          </p>
        </div>
      </section>

      <!-- Writer professional profile -->
      <section
        v-if="isWriter"
        class="overflow-hidden rounded-lg border border-slate-200 bg-white lg:col-span-2"
      >
        <div class="flex items-center gap-3 border-b border-slate-200 px-6 py-4">
          <PenLine class="h-5 w-5 text-signal" />
          <div>
            <h2 class="text-base font-semibold text-ink">Writer profile</h2>
            <p class="text-sm text-graphite">Your pen name and professional bio shown to clients and editors.</p>
          </div>
        </div>

        <div class="grid gap-4 p-6 sm:grid-cols-2">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Writer level</p>
            <div class="mt-1.5">
              <StatusPill
                :label="typeof writerWorkspace.profile?.writer_level === 'object'
                  ? (writerWorkspace.profile.writer_level?.label ?? 'Standard')
                  : ((writerWorkspace.profile?.writer_level as string | undefined) ?? 'Standard')"
                tone="neutral"
              />
            </div>
          </div>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Pen name</span>
            <input
              v-model.trim="writerForm.display_name"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="text"
              placeholder="e.g. Alex Rivera"
            />
          </label>

          <label class="block sm:col-span-2">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Professional bio</span>
            <textarea
              v-model.trim="writerForm.bio"
              class="focus-ring mt-1.5 w-full resize-none rounded-md border border-slate-200 px-3 py-2.5 text-sm"
              rows="4"
              maxlength="300"
              placeholder="Expertise, academic background, writing style — shown on order assignments…"
            />
            <span class="mt-0.5 block text-right text-xs text-graphite">{{ writerForm.bio.length }}/300</span>
          </label>
        </div>

        <div class="flex items-center gap-4 border-t border-slate-200 px-6 py-4">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="writerSaving || writerWorkspace.isMutating"
            @click="saveWriterProfile"
          >
            <Loader2 v-if="writerSaving" class="h-4 w-4 animate-spin" />
            Save writer profile
          </button>
          <p v-if="writerNotice" class="text-sm font-medium text-signal">{{ writerNotice }}</p>
          <p v-if="writerError" class="text-sm font-medium text-berry">{{ writerError }}</p>
        </div>
      </section>

      <!-- Change password -->
      <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center gap-3 border-b border-slate-200 px-6 py-4">
          <KeyRound class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold text-ink">Change password</h2>
        </div>

        <div class="space-y-4 p-6">
          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Current password</span>
            <input
              v-model="passwordForm.current_password"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="password"
              autocomplete="current-password"
            />
          </label>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">New password</span>
            <input
              v-model="passwordForm.new_password"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="password"
              autocomplete="new-password"
            />
          </label>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Confirm new password</span>
            <input
              v-model="passwordForm.confirm_password"
              class="focus-ring mt-1.5 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              type="password"
              autocomplete="new-password"
            />
          </label>

          <p v-if="passwordError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
            {{ passwordError }}
          </p>
          <p v-if="passwordNotice" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">
            {{ passwordNotice }}
          </p>
        </div>

        <div class="border-t border-slate-200 px-6 py-4">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="passwordSaving || !passwordForm.current_password || !passwordForm.new_password"
            @click="changePassword"
          >
            <Loader2 v-if="passwordSaving" class="h-4 w-4 animate-spin" />
            Change password
          </button>
        </div>
      </section>

      <!-- Danger zone: account info -->
      <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="border-b border-slate-200 px-6 py-4">
          <h2 class="text-base font-semibold text-ink">Account details</h2>
        </div>
        <div class="space-y-4 p-6">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">User ID</p>
            <p class="mt-1 font-mono text-sm text-graphite">#{{ auth.user?.id }}</p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Email address</p>
            <p class="mt-1 text-sm text-graphite">{{ auth.user?.email }}</p>
            <p class="mt-0.5 text-xs text-graphite">Email changes require administrator action.</p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Timezone</p>
            <p class="mt-1 text-sm text-graphite">{{ auth.user?.timezone ?? profileForm.timezone }}</p>
          </div>
        </div>
      </section>

      <!-- Active sessions -->
      <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div class="flex items-center gap-3">
            <ShieldCheck class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Active sessions</h2>
          </div>
          <button
            class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50"
            type="button"
            :disabled="sessionsLoading"
            @click="loadSessions"
          >
            Refresh
          </button>
        </div>

        <p v-if="sessionsError" class="px-6 py-3 text-sm text-berry">{{ sessionsError }}</p>
        <p v-if="sessionsNotice" class="px-6 py-3 text-sm text-signal">{{ sessionsNotice }}</p>

        <div v-if="sessionsLoading" class="px-6 py-8 text-center text-sm text-graphite animate-pulse">
          Loading sessions…
        </div>

        <div v-else-if="!sessions.length" class="px-6 py-6 text-center text-sm text-graphite">
          No active sessions found.
        </div>

        <ul v-else class="divide-y divide-slate-100">
          <li
            v-for="session in sessions"
            :key="session.id"
            class="flex items-center gap-4 px-6 py-4"
          >
            <Monitor class="h-8 w-8 shrink-0 rounded-lg border border-slate-200 bg-slate-50 p-1.5 text-graphite" />
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-ink">{{ formatDevice(session) }}</p>
              <p class="mt-0.5 text-xs text-graphite">
                {{ session.ip_address ?? "Unknown IP" }}
                <span v-if="session.logged_in_at"> · Signed in {{ formatDate(session.logged_in_at) }}</span>
              </p>
            </div>
            <button
              class="focus-ring shrink-0 rounded-md border border-slate-200 p-1.5 text-graphite hover:border-rose-200 hover:text-rose-600 disabled:opacity-40 transition-colors"
              type="button"
              :disabled="revokingId === session.id"
              :title="'Sign out this session'"
              @click="revokeSession(session.id)"
            >
              <XCircle class="h-4 w-4" />
            </button>
          </li>
        </ul>

        <div v-if="sessions.length > 1" class="border-t border-slate-100 px-6 py-4">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md border border-rose-200 px-4 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-50 disabled:opacity-60"
            type="button"
            @click="revokeAllSessions"
          >
            Sign out all other sessions
          </button>
        </div>
      </section>

      <!-- MFA devices -->
      <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div class="flex items-center gap-3">
            <Smartphone class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Two-factor authentication</h2>
          </div>
          <button
            v-if="totpSetupStep === 'idle'"
            class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold hover:bg-slate-50 disabled:opacity-60"
            type="button"
            :disabled="totpBusy"
            @click="startTotpSetup"
          >
            <Plus class="h-3.5 w-3.5" />
            Add authenticator app
          </button>
        </div>

        <p v-if="mfaError" class="border-b border-rose-100 bg-rose-50 px-6 py-3 text-sm text-rose-700">{{ mfaError }}</p>
        <p v-if="mfaNotice" class="border-b border-emerald-100 bg-emerald-50 px-6 py-3 text-sm text-signal">{{ mfaNotice }}</p>

        <!-- TOTP setup: step 1 scan -->
        <div v-if="totpSetupStep === 'scan' && totpSetupData" class="space-y-4 p-6">
          <p class="text-sm text-graphite">Scan the QR code below with your authenticator app (Google Authenticator, Authy, 1Password…).</p>
          <div class="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
            <img
              :src="`data:image/png;base64,${totpSetupData.qr_code_base64}`"
              alt="TOTP QR code"
              class="h-44 w-44 rounded-lg border border-slate-200"
            />
            <div class="min-w-0 space-y-2">
              <p class="text-xs font-semibold uppercase text-graphite">Can't scan? Enter this code manually:</p>
              <code class="block rounded-md border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-sm tracking-wider text-ink">{{ totpSetupData.secret }}</code>
              <button
                class="focus-ring mt-2 inline-flex h-9 items-center gap-1.5 rounded-md bg-signal px-4 text-sm font-semibold text-white disabled:opacity-60"
                type="button"
                @click="totpSetupStep = 'verify'"
              >
                I've scanned it — continue
              </button>
              <button
                class="focus-ring ml-2 inline-flex h-9 items-center rounded-md border border-slate-200 px-4 text-sm text-graphite hover:bg-slate-50"
                type="button"
                @click="cancelTotpSetup"
              >Cancel</button>
            </div>
          </div>
        </div>

        <!-- TOTP setup: step 2 verify -->
        <div v-else-if="totpSetupStep === 'verify'" class="space-y-4 p-6">
          <p class="text-sm text-graphite">Enter the 6-digit code shown in your authenticator app to confirm the link.</p>
          <div class="flex items-center gap-3">
            <input
              v-model="totpVerifyCode"
              class="focus-ring h-10 w-32 rounded-md border border-slate-200 px-3 text-center font-mono text-lg tracking-widest"
              type="text"
              maxlength="6"
              placeholder="000000"
              @keyup.enter="verifyTotpDevice"
            />
            <button
              class="focus-ring inline-flex h-10 items-center gap-1.5 rounded-md bg-signal px-4 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="totpBusy || totpVerifyCode.length < 6"
              @click="verifyTotpDevice"
            >
              <Loader2 v-if="totpBusy" class="h-4 w-4 animate-spin" />
              <CheckCircle2 v-else class="h-4 w-4" />
              Verify
            </button>
            <button
              class="focus-ring inline-flex h-10 items-center rounded-md border border-slate-200 px-4 text-sm text-graphite hover:bg-slate-50"
              type="button"
              @click="cancelTotpSetup"
            >Cancel</button>
          </div>
        </div>

        <!-- Device list -->
        <div v-if="mfaLoading" class="px-6 py-8 text-center text-sm text-graphite animate-pulse">Loading devices…</div>
        <ul v-else-if="mfaDevices.length" class="divide-y divide-slate-100">
          <li
            v-for="device in mfaDevices"
            :key="device.id"
            class="flex items-center gap-4 px-6 py-4"
          >
            <div class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50">
              <Smartphone class="h-4 w-4 text-graphite" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-ink">{{ device.name || methodLabel(device.method) }}</p>
              <p class="mt-0.5 text-xs text-graphite">
                {{ methodLabel(device.method) }}
                <span v-if="device.is_primary" class="ml-1.5 rounded-full bg-signal/10 px-2 py-0.5 text-signal">primary</span>
                <span v-if="!device.is_verified" class="ml-1.5 text-amber-600">unverified</span>
              </p>
            </div>
            <div class="flex items-center gap-2">
              <StatusPill
                :label="device.is_active ? 'Active' : 'Inactive'"
                :tone="device.is_active ? 'success' : 'warning'"
              />
              <button
                v-if="!device.is_primary && device.is_verified"
                class="focus-ring rounded-md border border-slate-200 px-2.5 py-1 text-xs font-semibold hover:bg-slate-50"
                type="button"
                @click="setPrimaryDevice(device.id)"
              >Set primary</button>
              <button
                class="focus-ring rounded-md border px-2.5 py-1 text-xs font-semibold"
                :class="device.is_active ? 'border-amber-200 text-amber-700 hover:bg-amber-50' : 'border-emerald-200 text-emerald-700 hover:bg-emerald-50'"
                type="button"
                @click="toggleDevice(device)"
              >{{ device.is_active ? 'Deactivate' : 'Activate' }}</button>
            </div>
          </li>
        </ul>
        <div v-else-if="!mfaLoading && totpSetupStep === 'idle'" class="px-6 py-6 text-center text-sm text-graphite">
          No MFA devices configured. Add an authenticator app to secure your account.
        </div>

        <!-- Backup codes -->
        <div class="border-t border-slate-100 px-6 py-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-ink">Backup codes</p>
              <p class="mt-0.5 text-xs text-graphite">One-time codes to use if you lose access to your authenticator.</p>
            </div>
            <button
              class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-md border border-slate-200 px-3 text-xs font-semibold hover:bg-slate-50 disabled:opacity-60"
              type="button"
              :disabled="backupBusy"
              @click="generateBackupCodes"
            >
              <Loader2 v-if="backupBusy" class="h-3.5 w-3.5 animate-spin" />
              Generate codes
            </button>
          </div>
          <div v-if="backupCodes.length" class="mt-3 grid grid-cols-2 gap-1.5 sm:grid-cols-4">
            <code
              v-for="code in backupCodes"
              :key="code"
              class="rounded-md border border-slate-200 bg-slate-50 px-2 py-1.5 text-center font-mono text-xs text-ink"
            >{{ code }}</code>
          </div>
        </div>
      </section>

      <!-- Security events -->
      <section class="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div class="flex items-center gap-3">
            <Shield class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Security activity</h2>
          </div>
          <button
            class="focus-ring text-xs font-semibold text-signal hover:underline"
            type="button"
            @click="loadSecurityEvents"
          >Refresh</button>
        </div>
        <p v-if="securityEventsError" class="px-6 py-3 text-sm text-berry">{{ securityEventsError }}</p>
        <div v-if="securityEventsLoading" class="px-6 py-8 text-center text-sm text-graphite animate-pulse">Loading events…</div>
        <div v-else-if="!securityEvents.length" class="px-6 py-6 text-center text-sm text-graphite">No security events recorded.</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-6 py-3 text-left">Event</th>
                <th class="px-6 py-3 text-left">Severity</th>
                <th class="px-6 py-3 text-left">Device / IP</th>
                <th class="px-6 py-3 text-left">Time</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="evt in securityEvents" :key="evt.id">
                <td class="px-6 py-3 font-medium text-ink">{{ evt.event_type.replace(/_/g, " ") }}</td>
                <td class="px-6 py-3">
                  <StatusPill :label="evt.severity" :tone="severityTone(evt.severity)" />
                </td>
                <td class="px-6 py-3 text-graphite">
                  <span v-if="evt.device">{{ evt.device }}</span>
                  <span v-if="evt.ip_address" class="ml-1 text-xs">({{ evt.ip_address }})</span>
                  <span v-if="!evt.device && !evt.ip_address">—</span>
                </td>
                <td class="px-6 py-3 text-graphite">{{ formatDate(evt.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="overflow-hidden rounded-lg border border-rose-200 bg-white">
        <div class="flex items-center gap-3 border-b border-rose-100 px-6 py-4">
          <AlertTriangle class="h-5 w-5 text-rose-600" />
          <h2 class="text-base font-semibold text-ink">Account deletion</h2>
        </div>
        <div class="space-y-4 p-6">
          <div v-if="deletionState" class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            <p class="font-semibold">Deletion request: {{ deletionState.status.replace(/_/g, " ") }}</p>
            <p v-if="deletionState.scheduled_deletion_at" class="mt-1 text-xs">
              Scheduled for {{ new Date(deletionState.scheduled_deletion_at).toLocaleString() }}
            </p>
            <p v-if="deletionState.reason" class="mt-1 text-xs">{{ deletionState.reason }}</p>
          </div>
          <p v-else class="text-sm text-graphite">
            Requesting deletion starts a staff-visible account lifecycle. Confirmation is required before the deletion is scheduled.
          </p>

          <label class="block">
            <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Reason</span>
            <textarea
              v-model.trim="deletionReason"
              class="focus-ring mt-1.5 w-full resize-none rounded-md border border-slate-200 px-3 py-2.5 text-sm"
              rows="3"
              placeholder="Optional context for support and compliance review"
            />
          </label>

          <p v-if="deletionNotice" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">
            {{ deletionNotice }}
          </p>
          <p v-if="deletionError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
            {{ deletionError }}
          </p>
        </div>
        <div class="flex flex-wrap gap-3 border-t border-rose-100 px-6 py-4">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md border border-rose-200 px-4 py-2.5 text-sm font-semibold text-rose-700 hover:bg-rose-50 disabled:opacity-60"
            type="button"
            :disabled="deletionBusy"
            @click="requestDeletion"
          >
            <Loader2 v-if="deletionBusy" class="h-4 w-4 animate-spin" />
            <Trash2 v-else class="h-4 w-4" />
            Request deletion
          </button>
          <button
            v-if="deletionState && deletionState.status !== 'scheduled'"
            class="focus-ring inline-flex items-center gap-2 rounded-md bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-60"
            type="button"
            :disabled="deletionBusy"
            @click="confirmDeletion"
          >
            Confirm scheduling
          </button>
        </div>
      </section>
    </div>
  </div>
</template>
