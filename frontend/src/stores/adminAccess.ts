import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { adminAccessApi } from "@/api/adminAccess";
import type { CreateUserPayload } from "@/api/adminAccess";
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";
import type {
  AdminAccessMetric,
  AdminManagedUser,
  AdminUserStats,
  BlacklistedEmailRecord,
  DuplicateAccountGroup,
  DuplicateStatsResponse,
  ImpersonationStatusResponse,
  ProfileUpdateRequestRecord,
} from "@/types/adminAccess";
import type { UserRole } from "@/types/roles";

type ListResponse<T> = T[] | { results: T[] };
type AccessFilter = "all" | UserRole | "suspended" | "blacklisted" | "probation";

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function previewUsers(): AdminManagedUser[] {
  const now = Date.now();
  return [
    {
      id: 1,
      username: "amina.admin",
      email: "amina.admin@preview.local",
      full_name: "Amina Admin",
      role: "admin",
      role_display: "Admin",
      is_active: true,
      is_staff: true,
      is_suspended: false,
      is_blacklisted: false,
      is_on_probation: false,
      website: { id: 1, name: "NurseMyGrade", domain: "nursemygrade.com" },
      date_joined: new Date(now - 1000 * 60 * 60 * 24 * 500).toISOString(),
      last_login: new Date(now - 1000 * 60 * 12).toISOString(),
    },
    {
      id: 101,
      username: "nadia.m",
      email: "nadia@example.com",
      full_name: "Nadia Morgan",
      role: "client",
      role_display: "Client",
      is_active: true,
      is_suspended: false,
      is_blacklisted: false,
      is_on_probation: false,
      website: { id: 1, name: "NurseMyGrade", domain: "nursemygrade.com" },
      date_joined: new Date(now - 1000 * 60 * 60 * 24 * 420).toISOString(),
      last_login: new Date(now - 1000 * 60 * 18).toISOString(),
    },
    {
      id: 8,
      username: "amina.writer",
      email: "amina.writer@preview.local",
      full_name: "Amina Writer",
      role: "writer",
      role_display: "Writer",
      is_active: true,
      is_suspended: false,
      is_blacklisted: false,
      is_on_probation: true,
      website: { id: 1, name: "NurseMyGrade", domain: "nursemygrade.com" },
      date_joined: new Date(now - 1000 * 60 * 60 * 24 * 250).toISOString(),
      last_login: new Date(now - 1000 * 60 * 60 * 2).toISOString(),
    },
    {
      id: 204,
      username: "risk.client",
      email: "risk@example.com",
      full_name: "Risk Client",
      role: "client",
      role_display: "Client",
      is_active: false,
      is_suspended: true,
      is_blacklisted: true,
      is_on_probation: false,
      website: { id: 2, name: "EssayManiacs", domain: "essaymaniacs.com" },
      date_joined: new Date(now - 1000 * 60 * 60 * 24 * 80).toISOString(),
      last_login: null,
    },
  ];
}

function summarize(users: AdminManagedUser[]): AdminUserStats {
  const roles: UserRole[] = ["client", "writer", "editor", "support", "admin", "superadmin"];
  return {
    total_users: users.length,
    by_role: Object.fromEntries(roles.map((role) => [role, users.filter((user) => user.role === role).length])),
    active_users: users.filter((user) => user.is_active).length,
    suspended_users: users.filter((user) => user.is_suspended).length,
    blacklisted_users: users.filter((user) => user.is_blacklisted).length,
    on_probation: users.filter((user) => user.is_on_probation).length,
  };
}

export const useAdminAccessStore = defineStore("admin-access", () => {
  const users = ref<AdminManagedUser[]>([]);
  const stats = ref<AdminUserStats>({});
  const impersonationStatus = ref<ImpersonationStatusResponse>({
    is_impersonating: false,
    impersonator: null,
  });
  const duplicateGroups = ref<DuplicateAccountGroup[]>([]);
  const duplicateStats = ref<DuplicateStatsResponse>({});
  const profileUpdateRequests = ref<ProfileUpdateRequestRecord[]>([]);
  const blacklistedEmails = ref<BlacklistedEmailRecord[]>([]);
  const selectedUserId = ref<number | null>(null);
  const query = ref("");
  const filter = ref<AccessFilter>("all");
  const reason = ref("Admin support review from access console.");
  const newRole = ref<UserRole>("support");
  const generatedToken = ref("");
  const createUserForm = ref<CreateUserPayload>({
    username: "new.support",
    email: "new.support@example.com",
    role: "support",
    password: "",
    first_name: "New",
    last_name: "Support",
    website: null,
    send_invite: true,
  });
  const lastInviteLink = ref<string | null>(null);
  const blacklistForm = ref({
    email: "risk@example.com",
    reason: "Chargeback, abuse, or duplicate-risk review.",
  });
  const duplicateFilters = ref({
    role: "",
    min_confidence: "medium",
    limit: 10,
  });
  const isLoading = ref(false);
  const isDuplicatesLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const duplicatesError = ref("");
  const notice = ref("");

  const selectedUser = computed(() =>
    users.value.find((user) => user.id === selectedUserId.value) ?? null,
  );

  // Unique websites derived from loaded users — used for the website selector
  const websites = computed(() => {
    const seen = new Map<number, { id: number; name: string; domain?: string }>();
    for (const user of users.value) {
      if (user.website?.id && !seen.has(user.website.id)) {
        seen.set(user.website.id, user.website);
      }
    }
    return [...seen.values()].sort((a, b) => a.name.localeCompare(b.name));
  });

  const filteredUsers = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return users.value.filter((user) => {
      const filterMatches =
        filter.value === "all" ||
        user.role === filter.value ||
        (filter.value === "suspended" && user.is_suspended) ||
        (filter.value === "blacklisted" && user.is_blacklisted) ||
        (filter.value === "probation" && user.is_on_probation);
      const textMatches =
        !needle ||
        [
          user.id,
          user.username,
          user.email,
          user.full_name,
          user.role,
          user.website?.name,
          user.website?.domain,
        ].some((value) => String(value ?? "").toLowerCase().includes(needle));
      return filterMatches && textMatches;
    });
  });

  const metrics = computed<AdminAccessMetric[]>(() => [
    {
      label: "Users",
      value: stats.value.total_users ?? users.value.length,
      detail: `${stats.value.active_users ?? users.value.filter((user) => user.is_active).length} active accounts.`,
      tone: "neutral",
    },
    {
      label: "Staff",
      value: ["admin", "support", "editor"].reduce(
        (sum, role) => sum + (stats.value.by_role?.[role as UserRole] ?? users.value.filter((user) => user.role === role).length),
        0,
      ),
      detail: "Admins, support, and editor operators.",
      tone: "good",
    },
    {
      label: "Restricted",
      value: (stats.value.suspended_users ?? 0) + (stats.value.blacklisted_users ?? 0),
      detail: `${stats.value.suspended_users ?? 0} suspended, ${stats.value.blacklisted_users ?? 0} blacklisted.`,
      tone: (stats.value.suspended_users || stats.value.blacklisted_users) ? "risk" : "neutral",
    },
    {
      label: "Probation",
      value: stats.value.on_probation ?? users.value.filter((user) => user.is_on_probation).length,
      detail: "Accounts with active probation state.",
      tone: (stats.value.on_probation ?? 0) ? "warn" : "neutral",
    },
  ]);

  const lifecycleMetrics = computed<AdminAccessMetric[]>(() => [
    {
      label: "Duplicate groups",
      value: duplicateStats.value.total?.suspected_groups ?? duplicateGroups.value.length,
      detail: `${duplicateStats.value.total?.users_involved ?? 0} users involved in duplicate signals.`,
      tone: duplicateGroups.value.length ? "warn" : "neutral",
    },
    {
      label: "Profile requests",
      value: profileUpdateRequests.value.length,
      detail: "Pending or historical profile change requests visible to staff.",
      tone: profileUpdateRequests.value.length ? "warn" : "neutral",
    },
    {
      label: "Email blacklist",
      value: blacklistedEmails.value.length,
      detail: "Emails blocked from client registration or reuse.",
      tone: blacklistedEmails.value.length ? "risk" : "neutral",
    },
  ]);

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        users.value = previewUsers();
        stats.value = summarize(users.value);
        impersonationStatus.value = { is_impersonating: false, impersonator: null };
        selectedUserId.value = selectedUserId.value ?? users.value[1]?.id ?? users.value[0]?.id ?? null;
        return;
      }

      const [usersRes, statsRes, impersonationRes] = await Promise.allSettled([
        adminAccessApi.users({ page_size: 100 }),
        adminAccessApi.stats(),
        adminAccessApi.impersonationStatus(),
      ]);

      if (usersRes.status === "fulfilled") users.value = normalizeList(usersRes.value.data);
      if (statsRes.status === "fulfilled") stats.value = statsRes.value.data;
      else stats.value = summarize(users.value);
      if (impersonationRes.status === "fulfilled") impersonationStatus.value = impersonationRes.value.data;
      selectedUserId.value = selectedUserId.value ?? users.value[0]?.id ?? null;
    } catch (caught) {
      error.value = "Unable to load admin access data.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function hydrateLifecycle() {
    const auth = useAuthStore();
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        duplicateStats.value = {
          total: { suspected_groups: 2, users_involved: 5 },
          clients: { suspected_groups: 1, users_involved: 3 },
          writers: { suspected_groups: 1, users_involved: 2 },
        };
        duplicateGroups.value = [
          {
            user_ids: [101, 204],
            users: [previewUsers()[1], previewUsers()[3]].map((user) => ({
              id: user.id,
              username: user.username,
              email: user.email,
              role: user.role,
              website: user.website,
              is_active: user.is_active,
              is_suspended: user.is_suspended,
              is_blacklisted: user.is_blacklisted,
            })),
            confidence: "high",
            signals: ["shared payment fingerprint", "similar email pattern"],
            detection_types: ["payment", "email"],
            match_count: 2,
          },
        ];
        profileUpdateRequests.value = [
          {
            id: 1,
            user: { email: "nadia@example.com", role: "client" },
            requested_changes: { phone_number: "+1 555 0188", country: "US" },
            status: "pending",
            created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
          },
        ];
        blacklistedEmails.value = [
          { id: 1, email: "risk@example.com", reason: "Chargeback review", date_added: new Date().toISOString() },
        ];
        return;
      }

      const [duplicateStatsRes, duplicatesRes, profileRes, blacklistRes] = await Promise.allSettled([
        adminAccessApi.duplicateStats(),
        adminAccessApi.detectDuplicates(duplicateFilters.value),
        adminAccessApi.profileUpdateRequests({ page_size: 20 }),
        adminAccessApi.blacklistedEmails(),
      ]);

      if (duplicateStatsRes.status === "fulfilled") duplicateStats.value = duplicateStatsRes.value.data;
      if (duplicatesRes.status === "fulfilled") duplicateGroups.value = duplicatesRes.value.data.results;
      if (profileRes.status === "fulfilled") profileUpdateRequests.value = normalizeList(profileRes.value.data);
      if (blacklistRes.status === "fulfilled") blacklistedEmails.value = normalizeList(blacklistRes.value.data);
    } catch (caught) {
      error.value = "Unable to load lifecycle operations data.";
      throw caught;
    }
  }

  async function scanDuplicates() {
    const auth = useAuthStore();
    isDuplicatesLoading.value = true;
    duplicatesError.value = "";

    try {
      if (auth.isPreviewSession) {
        await new Promise((r) => setTimeout(r, 600));
        duplicateGroups.value = [
          {
            user_ids: [101, 204],
            users: [previewUsers()[1], previewUsers()[3]].map((user) => ({
              id: user.id,
              username: user.username,
              email: user.email,
              role: user.role,
              website: user.website,
              is_active: user.is_active,
              is_suspended: user.is_suspended,
              is_blacklisted: user.is_blacklisted,
            })),
            confidence: "high",
            signals: ["shared payment fingerprint", "similar email pattern"],
            detection_types: ["payment", "email"],
            match_count: 2,
          },
        ];
        return;
      }

      // Strip empty-string role so the backend doesn't filter on ""
      const params: Record<string, unknown> = {
        min_confidence: duplicateFilters.value.min_confidence,
        limit: duplicateFilters.value.limit,
      };
      if (duplicateFilters.value.role) {
        params.role = duplicateFilters.value.role;
      }

      const { data } = await adminAccessApi.detectDuplicates(params);
      // Backend returns { count, results } or plain array
      duplicateGroups.value = Array.isArray(data)
        ? data
        : (data as { results?: typeof duplicateGroups.value }).results ?? [];
    } catch {
      duplicatesError.value = "Scan failed. Check backend logs for details.";
    } finally {
      isDuplicatesLoading.value = false;
    }
  }

  function patchSelected(patch: Partial<AdminManagedUser>) {
    if (!selectedUserId.value) return;
    users.value = users.value.map((user) =>
      user.id === selectedUserId.value ? { ...user, ...patch } : user,
    );
    stats.value = summarize(users.value);
  }

  async function runUserAction(action: "suspend" | "unsuspend" | "reset" | "unlock" | "kickout" | "role" | "promote") {
    const auth = useAuthStore();
    const ui = useUiStore();
    const user = selectedUser.value;
    if (!user) return;
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        if (action === "suspend") patchSelected({ is_suspended: true, is_active: false });
        if (action === "unsuspend" || action === "unlock") patchSelected({ is_suspended: false, is_active: true });
        if (action === "role") patchSelected({ role: newRole.value, role_display: newRole.value });
        if (action === "promote") patchSelected({ role: "admin", role_display: "Admin", is_staff: true });
        notice.value = `Preview ${action} action completed for ${user.email}.`;
        ui.toast(notice.value, "success");
        return;
      }

      if (action === "suspend") await adminAccessApi.suspend(user.id, reason.value);
      if (action === "unsuspend") await adminAccessApi.unsuspend(user.id, reason.value);
      if (action === "reset") await adminAccessApi.resetPassword(user.id);
      if (action === "unlock") await adminAccessApi.unlockUser(user.id);
      if (action === "kickout") await adminAccessApi.kickoutUser(user.id, reason.value);
      if (action === "role") await adminAccessApi.changeRole(user.id, newRole.value);
      if (action === "promote") await adminAccessApi.promoteToAdmin(user.id);

      notice.value = `${action} action completed for ${user.email}.`;
      ui.toast(notice.value, "success");
      await hydrate();
    } catch (caught) {
      error.value = `Unable to complete ${action} action.`;
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function createUser() {
    const auth = useAuthStore();
    const ui = useUiStore();
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        const id = Date.now();
        users.value = [
          {
            id,
            username: createUserForm.value.username,
            email: createUserForm.value.email,
            full_name: `${createUserForm.value.first_name ?? ""} ${createUserForm.value.last_name ?? ""}`.trim(),
            role: createUserForm.value.role,
            role_display: createUserForm.value.role,
            is_active: true,
            is_suspended: false,
            is_blacklisted: false,
            is_on_probation: false,
            website: createUserForm.value.website
              ? { id: createUserForm.value.website, name: `Website #${createUserForm.value.website}` }
              : null,
            date_joined: new Date().toISOString(),
            last_login: null,
          },
          ...users.value,
        ];
        stats.value = summarize(users.value);
        selectedUserId.value = id;
        notice.value = `Preview user ${createUserForm.value.email} created.`;
        ui.toast(notice.value, "success");
        return;
      }

      const res = await adminAccessApi.createUser(createUserForm.value);
      const data = res.data;
      const alreadyExisted = data.already_existed === true;
      lastInviteLink.value = data.invite_link ?? null;
      notice.value = alreadyExisted
        ? `User ${data.email} already exists — showing their profile.`
        : `User ${data.email} created.${lastInviteLink.value ? " Invite link ready." : ""}`;
      ui.toast(notice.value, alreadyExisted ? "info" : "success");
      await hydrate();
      selectedUserId.value = data.id;
    } catch (caught) {
      error.value = "Unable to create user.";
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function addBlacklistedEmail() {
    const auth = useAuthStore();
    const ui = useUiStore();
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        blacklistedEmails.value = [
          {
            id: Date.now(),
            email: blacklistForm.value.email,
            reason: blacklistForm.value.reason,
            date_added: new Date().toISOString(),
          },
          ...blacklistedEmails.value.filter((item) => item.email !== blacklistForm.value.email),
        ];
        notice.value = `Preview blacklisted ${blacklistForm.value.email}.`;
        ui.toast(notice.value, "success");
        return;
      }

      await adminAccessApi.addBlacklistedEmail(blacklistForm.value.email, blacklistForm.value.reason);
      notice.value = `${blacklistForm.value.email} added to blacklist.`;
      ui.toast(notice.value, "success");
      await hydrateLifecycle();
    } catch (caught) {
      error.value = "Unable to add email to blacklist.";
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function removeBlacklistedEmail(email: string) {
    const auth = useAuthStore();
    const ui = useUiStore();
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        blacklistedEmails.value = blacklistedEmails.value.filter((item) => item.email !== email);
        notice.value = `Preview removed ${email} from blacklist.`;
        ui.toast(notice.value, "success");
        return;
      }

      await adminAccessApi.removeBlacklistedEmail(email);
      notice.value = `${email} removed from blacklist.`;
      ui.toast(notice.value, "success");
      await hydrateLifecycle();
    } catch (caught) {
      error.value = "Unable to remove email from blacklist.";
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function createImpersonationToken() {
    const auth = useAuthStore();
    const ui = useUiStore();
    const user = selectedUser.value;
    if (!user) return;
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        generatedToken.value = `preview-token-for-${user.id}`;
        notice.value = `Preview impersonation token generated for ${user.email}.`;
        ui.toast(notice.value, "success");
        return;
      }

      const { data } = await adminAccessApi.createImpersonationToken(user.id, reason.value);
      generatedToken.value = data.token;
      notice.value = `Impersonation token generated. It expires in ${data.expires_in_hours} hours.`;
      ui.toast(notice.value, "success");
    } catch (caught) {
      error.value = "Unable to create impersonation token.";
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function startImpersonation() {
    const auth = useAuthStore();
    const ui = useUiStore();
    const user = selectedUser.value;
    if (!user || !generatedToken.value) return;
    if (isMutating.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        notice.value = `Preview impersonation would start for ${user.email}.`;
        ui.toast(notice.value, "success");
        return;
      }

      const { data } = await adminAccessApi.startImpersonation(generatedToken.value, reason.value);
      auth.adoptSession(
        { access: data.access_token, refresh: data.refresh_token },
        {
          id: data.user.id,
          email: data.user.email,
          full_name: data.user.full_name,
          role: data.user.role,
        },
      );
      notice.value = `Now impersonating ${data.user.email}.`;
      ui.toast(notice.value, "success");
    } catch (caught) {
      error.value = "Unable to start impersonation.";
      ui.toast(error.value, "error");
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function endImpersonation(endReason = "Admin ended session") {
    const auth = useAuthStore();
    const ui = useUiStore();
    if (isMutating.value) return;
    isMutating.value = true;
    try {
      if (auth.isPreviewSession) {
        auth.restoreFromImpersonation();
        ui.toast("Preview impersonation ended.", "info");
        return;
      }
      const { data } = await adminAccessApi.endImpersonation(endReason);
      if (data.access_token && data.refresh_token && data.user) {
        auth.restoreFromImpersonation({
          access: data.access_token,
          refresh: data.refresh_token,
          user: {
            id: data.user.id,
            email: data.user.email,
            full_name: data.user.full_name,
            role: data.user.role,
          },
        });
      } else {
        auth.restoreFromImpersonation();
      }
      impersonationStatus.value = { is_impersonating: false, impersonator: null };
      ui.toast("Impersonation ended. Your session has been restored.", "success");
    } catch {
      ui.toast("Unable to end impersonation.", "error");
    } finally {
      isMutating.value = false;
    }
  }

  return {
    users,
    stats,
    impersonationStatus,
    duplicateGroups,
    duplicateStats,
    profileUpdateRequests,
    blacklistedEmails,
    selectedUserId,
    selectedUser,
    websites,
    query,
    filter,
    reason,
    newRole,
    generatedToken,
    createUserForm,
    lastInviteLink,
    blacklistForm,
    duplicateFilters,
    isLoading,
    isDuplicatesLoading,
    isMutating,
    error,
    duplicatesError,
    notice,
    filteredUsers,
    metrics,
    lifecycleMetrics,
    hydrate,
    hydrateLifecycle,
    scanDuplicates,
    runUserAction,
    createUser,
    addBlacklistedEmail,
    removeBlacklistedEmail,
    createImpersonationToken,
    startImpersonation,
    endImpersonation,
  };
});
