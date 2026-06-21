import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminClientsApi,
  type AdminClientProfileRecord,
  type AdminUserRecord,
  type BlacklistedEmailRecord,
  type ProfileUpdateRequestRecord,
} from "@/api/adminClients";
import { useAuthStore } from "@/stores/auth";
import type { AdminClient, AdminClientMetric } from "@/types/adminClients";

type ListResponse<T> = T[] | { results: T[] };

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function money(value: string | number | undefined, currency = "USD") {
  if (value === undefined || value === null || value === "") return "$0";
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return String(value);
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

function previewClients(): AdminClient[] {
  const now = Date.now();
  return [
    {
      id: 1,
      userId: 101,
      username: "nadia.m",
      fullName: "Nadia Morgan",
      email: "nadia@example.com",
      website: "WritePro Global",
      country: "Kenya",
      timezone: "Africa/Nairobi",
      walletBalance: "$48",
      totalSpent: "$2,860",
      loyaltyPoints: 1260,
      loyaltyTier: "Gold",
      preferredWriters: ["Amina K.", "Jon M."],
      isActive: true,
      isSuspended: false,
      isBlacklisted: false,
      dateJoined: new Date(now - 1000 * 60 * 60 * 24 * 420).toISOString(),
      lastLogin: new Date(now - 1000 * 60 * 18).toISOString(),
    },
    {
      id: 2,
      userId: 102,
      username: "caleb.r",
      fullName: "Caleb Reed",
      email: "caleb@example.com",
      website: "EssayDesk",
      country: "United States",
      timezone: "America/New_York",
      walletBalance: "$0",
      totalSpent: "$740",
      loyaltyPoints: 310,
      loyaltyTier: "Silver",
      preferredWriters: [],
      isActive: true,
      isSuspended: false,
      isBlacklisted: false,
      dateJoined: new Date(now - 1000 * 60 * 60 * 24 * 110).toISOString(),
      lastLogin: new Date(now - 1000 * 60 * 60 * 5).toISOString(),
    },
    {
      id: 3,
      userId: 103,
      username: "patricia.w",
      fullName: "Patricia Wells",
      email: "patricia@example.com",
      website: "GradHelp Africa",
      country: "South Africa",
      timezone: "Africa/Johannesburg",
      walletBalance: "$12",
      totalSpent: "$1,580",
      loyaltyPoints: 720,
      loyaltyTier: "Silver",
      preferredWriters: ["Mira Draft"],
      isActive: false,
      isSuspended: true,
      isBlacklisted: false,
      dateJoined: new Date(now - 1000 * 60 * 60 * 24 * 220).toISOString(),
      lastLogin: new Date(now - 1000 * 60 * 60 * 24 * 4).toISOString(),
    },
    {
      id: 4,
      userId: 104,
      username: "risk.client",
      fullName: "Risk Client",
      email: "risk@example.com",
      website: "CampusAssist",
      country: "Canada",
      timezone: "America/Toronto",
      walletBalance: "$0",
      totalSpent: "$90",
      loyaltyPoints: 20,
      loyaltyTier: "Starter",
      preferredWriters: [],
      isActive: false,
      isSuspended: false,
      isBlacklisted: true,
      dateJoined: new Date(now - 1000 * 60 * 60 * 24 * 30).toISOString(),
      lastLogin: null,
    },
  ];
}

function mergeClient(
  profile: AdminClientProfileRecord,
  user?: AdminUserRecord,
): AdminClient {
  const website = user?.website?.name ?? user?.website?.domain ?? "Website pending";
  const fullName =
    user?.full_name ||
    [user?.first_name, user?.last_name].filter(Boolean).join(" ") ||
    profile.client_username ||
    user?.username ||
    "Client";

  return {
    id: profile.id,
    userId: profile.user,
    username: user?.username ?? profile.client_username ?? `client-${profile.id}`,
    fullName,
    email: user?.email ?? "No email",
    website,
    country: profile.country ?? "Unknown",
    timezone: profile.timezone ?? "UTC",
    walletBalance: money(profile.wallet_balance),
    totalSpent: money(profile.total_spent),
    loyaltyPoints: profile.loyalty_points ?? 0,
    loyaltyTier: profile.loyalty_tier ?? "Unassigned",
    preferredWriters: profile.preferred_writers ?? [],
    isActive: Boolean(profile.is_active ?? user?.is_active ?? true),
    isSuspended: Boolean(profile.is_suspended ?? user?.is_suspended),
    isBlacklisted: Boolean(user?.is_blacklisted),
    dateJoined: user?.date_joined ?? null,
    lastLogin: user?.last_login ?? null,
  };
}

export const useAdminClientsStore = defineStore("admin-clients", () => {
  const clients = ref<AdminClient[]>([]);
  const profileRequests = ref<ProfileUpdateRequestRecord[]>([]);
  const blacklistedEmails = ref<BlacklistedEmailRecord[]>([]);
  const selectedClient = ref<AdminClient | null>(null);
  const query = ref("");
  const statusFilter = ref<"all" | "active" | "suspended" | "blacklisted">("all");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const filteredClients = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return clients.value.filter((client) => {
      const statusMatches =
        statusFilter.value === "all" ||
        (statusFilter.value === "active" && client.isActive && !client.isSuspended) ||
        (statusFilter.value === "suspended" && client.isSuspended) ||
        (statusFilter.value === "blacklisted" && client.isBlacklisted);
      const textMatches =
        !needle ||
        [
          client.username,
          client.fullName,
          client.email,
          client.website,
          client.country,
          client.loyaltyTier,
        ].some((value) => value.toLowerCase().includes(needle));
      return statusMatches && textMatches;
    });
  });

  const metrics = computed<AdminClientMetric[]>(() => {
    const active = clients.value.filter((client) => client.isActive && !client.isSuspended).length;
    const suspended = clients.value.filter((client) => client.isSuspended).length;
    const blacklisted = clients.value.filter((client) => client.isBlacklisted).length;
    const totalSpent = clients.value.reduce((sum, client) => {
      const numeric = Number(client.totalSpent.replace(/[^0-9.-]/g, ""));
      return sum + (Number.isNaN(numeric) ? 0 : numeric);
    }, 0);

    return [
      {
        label: "Clients",
        value: clients.value.length,
        detail: "Profiles enriched with admin user records.",
        tone: "neutral",
      },
      {
        label: "Active",
        value: active,
        detail: "Ready to order, message, and pay.",
        tone: "good",
      },
      {
        label: "Needs review",
        value: suspended + blacklisted + profileRequests.value.length,
        detail: `${suspended} suspended, ${blacklisted} blacklisted, ${profileRequests.value.length} profile requests.`,
        tone: suspended || blacklisted || profileRequests.value.length ? "risk" : "good",
      },
      {
        label: "Client spend",
        value: money(totalSpent),
        detail: "Visible spend in the current admin slice.",
        tone: "neutral",
      },
    ];
  });

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        clients.value = previewClients();
        profileRequests.value = [
          {
            id: 1,
            client: 1,
            client_username: "nadia.m",
            requested_changes: { email: "nadia.new@example.com" },
            status: "pending",
            created_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
            updated_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
          },
        ];
        blacklistedEmails.value = [
          {
            id: 1,
            email: "risk@example.com",
            reason: "Chargeback abuse",
            date_added: new Date(Date.now() - 1000 * 60 * 60 * 24 * 6).toISOString(),
          },
        ];
        selectedClient.value = selectedClient.value ?? clients.value[0] ?? null;
        return;
      }

      const [profilesRes, usersRes, requestsRes, blacklistRes] = await Promise.allSettled([
        adminClientsApi.profiles({ page_size: 100 }),
        adminClientsApi.users({ role: "client", page_size: 100 }),
        adminClientsApi.profileUpdateRequests(),
        adminClientsApi.blacklist(),
      ]);

      if (profilesRes.status !== "fulfilled") {
        throw new Error("Client profiles unavailable");
      }

      const users =
        usersRes.status === "fulfilled" ? normalizeList(usersRes.value.data) : [];
      const usersById = new Map(users.map((user) => [user.id, user]));
      clients.value = normalizeList(profilesRes.value.data).map((profile) =>
        mergeClient(profile, usersById.get(profile.user)),
      );
      profileRequests.value =
        requestsRes.status === "fulfilled" ? normalizeList(requestsRes.value.data) : [];
      blacklistedEmails.value =
        blacklistRes.status === "fulfilled" ? normalizeList(blacklistRes.value.data) : [];
      selectedClient.value = clients.value[0] ?? null;
    } catch (caught) {
      error.value = "Unable to load client management data.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  function patchClient(clientId: number, patch: Partial<AdminClient>) {
    clients.value = clients.value.map((client) =>
      client.id === clientId ? { ...client, ...patch } : client,
    );
    if (selectedClient.value?.id === clientId) {
      selectedClient.value = { ...selectedClient.value, ...patch };
    }
  }

  async function runClientAction(action: "suspend" | "activate" | "deactivate") {
    const auth = useAuthStore();
    if (!selectedClient.value) return;
    if (isMutating.value) return;
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        patchClient(selectedClient.value.id, {
          isActive: action === "activate",
          isSuspended: action === "suspend" ? true : action === "activate" ? false : selectedClient.value.isSuspended,
        });
        notice.value = `Preview ${action} action applied.`;
        return;
      }

      await adminClientsApi.action(selectedClient.value.id, { action });
      notice.value = `Client ${action} action applied.`;
      await hydrate();
    } catch (caught) {
      error.value = `Unable to ${action} client.`;
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function resetPassword() {
    const auth = useAuthStore();
    if (!selectedClient.value) return;
    if (isMutating.value) return;
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        notice.value = "Preview password reset generated.";
        return;
      }

      await adminClientsApi.resetPassword(selectedClient.value.userId);
      notice.value = "Temporary password reset issued.";
    } catch (caught) {
      error.value = "Unable to reset password.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  return {
    clients,
    profileRequests,
    blacklistedEmails,
    selectedClient,
    query,
    statusFilter,
    isLoading,
    isMutating,
    error,
    notice,
    filteredClients,
    metrics,
    hydrate,
    runClientAction,
    resetPassword,
  };
});
