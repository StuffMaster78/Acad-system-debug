import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminGrowthApi,
  type CampaignCreatePayload,
  type CampaignClonePayload,
  type DiscountClonePayload,
  type DiscountCreatePayload,
  type DiscountSummaryResponse,
  type GrowthApiRecord,
  type ListResponse,
} from "@/api/adminGrowth";
import { useAuthStore } from "@/stores/auth";
import type {
  GrowthLane,
  GrowthMetric,
  GrowthRecord,
  GrowthWorkflowStep,
} from "@/types/adminGrowth";

function normalizeList(data: ListResponse<GrowthApiRecord>): GrowthApiRecord[] {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.results)) return data.results;
  if (Array.isArray(data.items)) return data.items;
  if (Array.isArray(data.data)) return data.data;
  return [];
}

function recordName(record: GrowthApiRecord, fallback: string) {
  return String(record.name ?? record.title ?? record.code ?? fallback);
}

function recordStatus(record: GrowthApiRecord) {
  if (record.status) return String(record.status);
  if (record.is_active === false || record.active === false) return "inactive";
  return "active";
}

function recordValue(record: GrowthApiRecord) {
  return record.value ?? record.percentage ?? record.amount;
}

function normalizeRecord(
  record: GrowthApiRecord,
  source: GrowthRecord["source"],
  fallback: string,
): GrowthRecord {
  return {
    id: record.id ?? `${source}-${recordName(record, fallback)}`,
    name: recordName(record, fallback),
    status: recordStatus(record),
    category: String(record.campaign_type ?? record.discount_type ?? source),
    value: recordValue(record),
    startsAt: record.starts_at ?? record.start_date ?? record.date ?? null,
    endsAt: record.ends_at ?? record.end_date ?? null,
    owner: String(record.website ?? record.site ?? record.owner ?? "Global"),
    source,
    raw: record,
  };
}

function previewRecord(
  id: number,
  source: GrowthRecord["source"],
  name: string,
  status = "active",
  category = "global",
  value?: string | number,
): GrowthRecord {
  return {
    id,
    source,
    name,
    status,
    category,
    value,
    owner: "WritePro Global",
    startsAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
    endsAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 12).toISOString(),
  };
}

export const useAdminGrowthStore = defineStore("admin-growth", () => {
  const summary = ref<DiscountSummaryResponse>({});
  const discounts = ref<GrowthRecord[]>([]);
  const expiring = ref<GrowthRecord[]>([]);
  const unused = ref<GrowthRecord[]>([]);
  const campaigns = ref<GrowthRecord[]>([]);
  const referralConfigs = ref<GrowthRecord[]>([]);
  const referralStats = ref<GrowthRecord[]>([]);
  const loyaltyTiers = ref<GrowthRecord[]>([]);
  const redemptionRequests = ref<GrowthRecord[]>([]);
  const holidayCampaigns = ref<GrowthRecord[]>([]);
  const specialDays = ref<GrowthRecord[]>([]);
  const referralReport = ref<Record<string, unknown>>({});
  const loyaltyAnalytics = ref<Record<string, unknown>>({});
  const selectedLane = ref<GrowthLane["key"]>("discounts");
  const query = ref("");
  const discountForm = ref({
    name: "Returning client save",
    description: "Retention offer for selected clients or all clients on this website.",
    discount_code: "RETURN10",
    generate_code: false,
    code_prefix: "SAVE",
    campaign_id: null as number | null,
    discount_type: "percentage" as DiscountCreatePayload["discount_type"],
    discount_value: 10,
    max_discount_amount: null as number | null,
    min_payable_amount: 0,
    starts_at: new Date().toISOString().slice(0, 16),
    ends_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 14).toISOString().slice(0, 16),
    usage_limit: null as number | null,
    per_client_usage_limit: 1,
    first_order_only: false,
    origin: "manual" as NonNullable<DiscountCreatePayload["origin"]>,
    is_active: true,
    audience: "all" as "all" | "clients",
    eligible_client_ids: "",
  });
  const campaignForm = ref({
    name: "Summer class help",
    slug: "summer-class-help",
    description: "Seasonal acquisition campaign for class help and urgent orders.",
    starts_at: new Date().toISOString().slice(0, 16),
    ends_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 21).toISOString().slice(0, 16),
    is_active: false,
  });
  const cloneForm = ref({
    mode: "discount" as "discount" | "campaign",
    source_discount_id: null as number | null,
    source_campaign_id: null as number | null,
    target_website_id: null as number | null,
    new_code: "",
    target_campaign_id: null as number | null,
    new_name: "",
    new_slug: "",
  });
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const workflow: GrowthWorkflowStep[] = [
    {
      label: "Configure",
      detail: "Set discount rules, referral bonuses, loyalty tiers, redemption options, and holiday dates.",
      owner: "Admin",
    },
    {
      label: "Launch",
      detail: "Activate campaigns only when dates, targeting, eligibility, and budget impact are clear.",
      owner: "Admin / superadmin",
    },
    {
      label: "Monitor",
      detail: "Watch expiring offers, unused discounts, referral abuse, loyalty liability, and redemption queues.",
      owner: "Ops",
    },
    {
      label: "Adjust",
      detail: "Pause weak campaigns, tune thresholds, award loyalty manually, or retire stale incentives.",
      owner: "Superadmin",
    },
  ];

  const lanes = computed<GrowthLane[]>(() => [
    {
      key: "discounts",
      label: "Discounts & campaigns",
      description: "Coupons, campaign windows, first-order offers, spend tiers, expiring and unused discounts.",
      endpoint: "/api/v1/discounts/",
      records: [...campaigns.value, ...discounts.value, ...expiring.value, ...unused.value],
    },
    {
      key: "referrals",
      label: "Referrals",
      description: "Referral codes, bonus rules, tracking reports, abuse review, and manual award paths.",
      endpoint: "/api/v1/referrals/",
      records: [...referralConfigs.value, ...referralStats.value],
    },
    {
      key: "loyalty",
      label: "Loyalty & redemptions",
      description: "Tiers, milestones, point conversion, redemption requests, award/transfer/deduct actions.",
      endpoint: "/api/v1/loyalty-management/",
      records: [...loyaltyTiers.value, ...redemptionRequests.value],
    },
    {
      key: "holidays",
      label: "Holiday campaigns",
      description: "Special days, seasonal reminders, auto-generated discounts, and holiday campaign schedules.",
      endpoint: "/api/v1/holidays/",
      records: [...holidayCampaigns.value, ...specialDays.value],
    },
  ]);

  const activeLane = computed(() =>
    lanes.value.find((lane) => lane.key === selectedLane.value) ?? lanes.value[0],
  );

  const filteredRecords = computed(() => {
    const needle = query.value.trim().toLowerCase();
    if (!needle) return activeLane.value.records;
    return activeLane.value.records.filter((record) =>
      [record.name, record.status, record.category, record.owner, record.value]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(needle)),
    );
  });

  const metrics = computed<GrowthMetric[]>(() => [
    {
      label: "Active discounts",
      value: summary.value.active_discounts ?? discounts.value.length,
      detail: `${summary.value.total_discounts ?? discounts.value.length} total discount records visible.`,
      tone: "good",
    },
    {
      label: "Expiring soon",
      value: summary.value.expiring_soon ?? expiring.value.length,
      detail: "Offers needing renewal, pause, or replacement decisions.",
      tone: expiring.value.length ? "warn" : "neutral",
    },
    {
      label: "Referral configs",
      value: referralConfigs.value.length,
      detail: "Bonus and tracking rules available to the referral engine.",
      tone: "neutral",
    },
    {
      label: "Redemption queue",
      value: redemptionRequests.value.length,
      detail: "Client loyalty requests waiting for operations handling.",
      tone: redemptionRequests.value.length ? "warn" : "good",
    },
  ]);

  const campaignOptions = computed(() =>
    campaigns.value
      .filter((campaign) => typeof campaign.id === "number")
      .map((campaign) => ({
        id: Number(campaign.id),
        name: campaign.name,
      })),
  );

  function parseClientIds(value: string) {
    return value
      .split(/[,\n]/)
      .map((item) => Number(item.trim()))
      .filter((item) => Number.isInteger(item) && item > 0);
  }

  function toIsoOrNull(value: string) {
    if (!value) return null;
    return new Date(value).toISOString();
  }

  function buildDiscountPayload(): DiscountCreatePayload {
    const eligibleClientIds =
      discountForm.value.audience === "clients"
        ? parseClientIds(discountForm.value.eligible_client_ids)
        : [];

    return {
      name: discountForm.value.name,
      description: discountForm.value.description,
      discount_code: discountForm.value.generate_code ? "" : discountForm.value.discount_code,
      generate_code: discountForm.value.generate_code,
      code_prefix: discountForm.value.generate_code ? discountForm.value.code_prefix : "",
      campaign_id: discountForm.value.campaign_id,
      is_campaign_managed: Boolean(discountForm.value.campaign_id),
      discount_type: discountForm.value.discount_type,
      discount_value: discountForm.value.discount_value,
      max_discount_amount: discountForm.value.max_discount_amount,
      min_payable_amount: discountForm.value.min_payable_amount,
      starts_at: toIsoOrNull(discountForm.value.starts_at),
      ends_at: toIsoOrNull(discountForm.value.ends_at),
      usage_limit: discountForm.value.usage_limit,
      per_client_usage_limit: discountForm.value.per_client_usage_limit,
      first_order_only: discountForm.value.first_order_only,
      origin: discountForm.value.origin,
      is_active: discountForm.value.is_active,
      eligible_client_ids: eligibleClientIds,
    };
  }

  function buildCampaignPayload(): CampaignCreatePayload {
    return {
      name: campaignForm.value.name,
      slug: campaignForm.value.slug,
      description: campaignForm.value.description,
      starts_at: toIsoOrNull(campaignForm.value.starts_at),
      ends_at: toIsoOrNull(campaignForm.value.ends_at),
      is_active: campaignForm.value.is_active,
    };
  }

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        summary.value = {
          active_discounts: 8,
          total_discounts: 14,
          expiring_soon: 3,
          unused_discounts: 2,
          total_redemptions: 128,
          revenue_impact: "$18.4k",
        };
        discounts.value = [
          previewRecord(1, "discounts", "First order welcome", "active", "first_order", "15%"),
          previewRecord(2, "discounts", "Returning client save", "active", "retention", "10%"),
        ];
        expiring.value = [
          previewRecord(3, "discounts", "May urgency boost", "active", "deadline", "8%"),
        ];
        unused.value = [
          previewRecord(4, "discounts", "Dormant STEM coupon", "inactive", "reactivation", "12%"),
        ];
        campaigns.value = [
          previewRecord(10, "campaigns", "Summer class help", "active", "seasonal", "20%"),
          previewRecord(11, "campaigns", "Nursing paper week", "draft", "service", "15%"),
        ];
        referralConfigs.value = [
          previewRecord(20, "referrals", "Client referral bonus", "active", "bonus", "$25"),
          previewRecord(21, "referrals", "Writer invite credit", "active", "bonus", "$15"),
        ];
        referralStats.value = [
          previewRecord(22, "referrals", "Referral code performance", "active", "analytics", "42 conversions"),
        ];
        loyaltyTiers.value = [
          previewRecord(30, "loyalty", "Gold clients", "active", "tier", "3x points"),
          previewRecord(31, "loyalty", "Platinum clients", "active", "tier", "5x points"),
        ];
        redemptionRequests.value = [
          previewRecord(32, "loyalty", "Wallet credit redemption", "pending", "redemption", "$40"),
        ];
        holidayCampaigns.value = [
          previewRecord(40, "holidays", "Black Friday academic push", "scheduled", "seasonal", "25%"),
        ];
        specialDays.value = [
          previewRecord(41, "holidays", "Cyber Monday", "active", "special_day", "2026-11-30"),
        ];
        referralReport.value = { conversions: 42, suspicious_referrals: 2 };
        loyaltyAnalytics.value = { points_liability: 128400, redemptions_this_month: 18 };
        return;
      }

      const [
        summaryRes,
        workingRes,
        expiringRes,
        unusedRes,
        campaignsRes,
        referralReportsRes,
        referralConfigsRes,
        referralStatsRes,
        loyaltyAnalyticsRes,
        loyaltyTiersRes,
        redemptionRes,
        holidayCampaignsRes,
        specialDaysRes,
      ] = await Promise.allSettled([
        adminGrowthApi.discountSummary(),
        adminGrowthApi.workingDiscounts(),
        adminGrowthApi.expiringDiscounts(),
        adminGrowthApi.unusedDiscounts(),
        adminGrowthApi.campaigns(),
        adminGrowthApi.referralReports(),
        adminGrowthApi.referralConfigs(),
        adminGrowthApi.referralStats(),
        adminGrowthApi.loyaltyAnalytics(),
        adminGrowthApi.loyaltyTiers(),
        adminGrowthApi.redemptionRequests(),
        adminGrowthApi.holidayCampaigns(),
        adminGrowthApi.specialDays(),
      ]);

      if (summaryRes.status === "fulfilled") summary.value = summaryRes.value.data;
      if (workingRes.status === "fulfilled") {
        discounts.value = normalizeList(workingRes.value.data).map((record, index) =>
          normalizeRecord(record, "discounts", `Discount ${index + 1}`),
        );
      }
      if (expiringRes.status === "fulfilled") {
        expiring.value = normalizeList(expiringRes.value.data).map((record, index) =>
          normalizeRecord(record, "discounts", `Expiring discount ${index + 1}`),
        );
      }
      if (unusedRes.status === "fulfilled") {
        unused.value = normalizeList(unusedRes.value.data).map((record, index) =>
          normalizeRecord(record, "discounts", `Unused discount ${index + 1}`),
        );
      }
      if (campaignsRes.status === "fulfilled") {
        campaigns.value = normalizeList(campaignsRes.value.data).map((record, index) =>
          normalizeRecord(record, "campaigns", `Campaign ${index + 1}`),
        );
      }
      if (referralReportsRes.status === "fulfilled") referralReport.value = referralReportsRes.value.data;
      if (referralConfigsRes.status === "fulfilled") {
        referralConfigs.value = normalizeList(referralConfigsRes.value.data).map((record, index) =>
          normalizeRecord(record, "referrals", `Referral config ${index + 1}`),
        );
      }
      if (referralStatsRes.status === "fulfilled") {
        referralStats.value = normalizeList(referralStatsRes.value.data).map((record, index) =>
          normalizeRecord(record, "referrals", `Referral stat ${index + 1}`),
        );
      }
      if (loyaltyAnalyticsRes.status === "fulfilled") loyaltyAnalytics.value = loyaltyAnalyticsRes.value.data;
      if (loyaltyTiersRes.status === "fulfilled") {
        loyaltyTiers.value = normalizeList(loyaltyTiersRes.value.data).map((record, index) =>
          normalizeRecord(record, "loyalty", `Loyalty tier ${index + 1}`),
        );
      }
      if (redemptionRes.status === "fulfilled") {
        redemptionRequests.value = normalizeList(redemptionRes.value.data).map((record, index) =>
          normalizeRecord(record, "loyalty", `Redemption request ${index + 1}`),
        );
      }
      if (holidayCampaignsRes.status === "fulfilled") {
        holidayCampaigns.value = normalizeList(holidayCampaignsRes.value.data).map((record, index) =>
          normalizeRecord(record, "holidays", `Holiday campaign ${index + 1}`),
        );
      }
      if (specialDaysRes.status === "fulfilled") {
        specialDays.value = normalizeList(specialDaysRes.value.data).map((record, index) =>
          normalizeRecord(record, "holidays", `Special day ${index + 1}`),
        );
      }
    } catch (caught) {
      error.value = "Unable to load growth and retention data.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function setCampaignState(campaign: GrowthRecord, active: boolean) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        campaign.status = active ? "active" : "inactive";
        notice.value = active ? "Preview campaign activated." : "Preview campaign deactivated.";
        return;
      }

      if (active) {
        await adminGrowthApi.activateCampaign(campaign.id);
      } else {
        await adminGrowthApi.deactivateCampaign(campaign.id);
      }
      notice.value = active ? "Campaign activated." : "Campaign deactivated.";
      await hydrate();
    } catch (caught) {
      error.value = "Unable to update campaign state.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function createDiscount() {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      const payload = buildDiscountPayload();
      if (auth.isPreviewSession) {
        discounts.value = [
          {
            id: Date.now(),
            source: "discounts",
            name: payload.name,
            status: payload.is_active ? "active" : "draft",
            category: payload.origin ?? "manual",
            value: payload.discount_type === "percentage" ? `${payload.discount_value}%` : `$${payload.discount_value}`,
            owner: payload.eligible_client_ids?.length ? `${payload.eligible_client_ids.length} selected clients` : "All users on current website",
            startsAt: payload.starts_at ?? null,
            endsAt: payload.ends_at ?? null,
          },
          ...discounts.value,
        ];
        selectedLane.value = "discounts";
        notice.value = payload.eligible_client_ids?.length
          ? "Preview targeted discount created for selected clients."
          : "Preview discount created for all users on this website.";
        return;
      }

      await adminGrowthApi.createDiscount(payload);
      notice.value = payload.eligible_client_ids?.length
        ? "Targeted discount created for selected clients."
        : "Discount created for all users on the current website.";
      selectedLane.value = "discounts";
      await hydrate();
    } catch (caught) {
      error.value = "Unable to create discount.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function createCampaign() {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      const payload = buildCampaignPayload();
      if (auth.isPreviewSession) {
        campaigns.value = [
          {
            id: Date.now(),
            source: "campaigns",
            name: payload.name,
            status: payload.is_active ? "active" : "draft",
            category: "campaign",
            value: "Campaign",
            owner: "Current website",
            startsAt: payload.starts_at ?? null,
            endsAt: payload.ends_at ?? null,
          },
          ...campaigns.value,
        ];
        selectedLane.value = "discounts";
        notice.value = "Preview campaign created.";
        return;
      }

      await adminGrowthApi.createCampaign(payload);
      notice.value = "Campaign created for the current website.";
      selectedLane.value = "discounts";
      await hydrate();
    } catch (caught) {
      error.value = "Unable to create campaign.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function cloneToWebsite() {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      if (!cloneForm.value.target_website_id) {
        throw new Error("Target website ID is required.");
      }

      if (auth.isPreviewSession) {
        notice.value =
          cloneForm.value.mode === "discount"
            ? "Preview discount cloned to target website."
            : "Preview campaign cloned to target website.";
        return;
      }

      if (cloneForm.value.mode === "discount") {
        if (!cloneForm.value.source_discount_id) throw new Error("Source discount ID is required.");
        const payload: DiscountClonePayload = {
          source_discount_id: cloneForm.value.source_discount_id,
          target_website_id: cloneForm.value.target_website_id,
          new_code: cloneForm.value.new_code || undefined,
          target_campaign_id: cloneForm.value.target_campaign_id,
        };
        await adminGrowthApi.cloneDiscount(payload);
        notice.value = "Discount cloned to target website.";
      } else {
        if (!cloneForm.value.source_campaign_id) throw new Error("Source campaign ID is required.");
        const payload: CampaignClonePayload = {
          source_campaign_id: cloneForm.value.source_campaign_id,
          target_website_id: cloneForm.value.target_website_id,
          new_name: cloneForm.value.new_name || undefined,
          new_slug: cloneForm.value.new_slug || undefined,
        };
        await adminGrowthApi.cloneCampaign(payload);
        notice.value = "Campaign cloned to target website.";
      }

      await hydrate();
    } catch (caught) {
      error.value = caught instanceof Error ? caught.message : "Unable to clone to target website.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  return {
    summary,
    discounts,
    expiring,
    unused,
    campaigns,
    referralConfigs,
    referralStats,
    loyaltyTiers,
    redemptionRequests,
    holidayCampaigns,
    specialDays,
    referralReport,
    loyaltyAnalytics,
    selectedLane,
    query,
    discountForm,
    campaignForm,
    cloneForm,
    isLoading,
    isMutating,
    error,
    notice,
    workflow,
    lanes,
    activeLane,
    filteredRecords,
    metrics,
    campaignOptions,
    hydrate,
    setCampaignState,
    createDiscount,
    createCampaign,
    cloneToWebsite,
  };
});
