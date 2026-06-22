import type { ConfigDomainMeta, ConfigDefinition, ConfigSectionMeta } from "@/types/config";

// ── Domain registry ───────────────────────────────────────────────────────────

export const DOMAINS: ConfigDomainMeta[] = [
  {
    key: "order-management",
    label: "Order Management",
    iconName: "ClipboardList",
    requiredScope: "admin",
    sections: [
      { key: "order-rules", label: "Order Rules", requiredScope: "admin" },
      { key: "academic-levels", label: "Academic Levels", requiredScope: "admin", isCrud: true, crudCollection: "academic-levels" },
      { key: "deadlines", label: "Deadline Rules", requiredScope: "admin" },
      { key: "types-of-work", label: "Types of Work", requiredScope: "admin", isCrud: true, crudCollection: "types-of-work" },
      { key: "paper-subjects", label: "Paper Subjects", requiredScope: "admin", isCrud: true, crudCollection: "subjects" },
      { key: "paper-types", label: "Paper Types", requiredScope: "admin", isCrud: true, crudCollection: "paper-types" },
      { key: "writer-preferences", label: "Writer Preferences", requiredScope: "admin" },
      { key: "unpaid-orders", label: "Unpaid Orders", requiredScope: "admin" },
      { key: "client-order-policy",label: "Client Order Policy", requiredScope: "admin" },
    ],
  },
  {
    key: "pricing",
    label: "Pricing",
    iconName: "DollarSign",
    requiredScope: "admin",
    sections: [
      { key: "base-rates", label: "Base Rates", requiredScope: "superadmin", panel: "pricing-profile" },
      { key: "deadline-bands", label: "Deadline Bands", requiredScope: "admin", panel: "pricing-deadlines" },
      { key: "academic-level-rates", label: "Academic Level Rates", requiredScope: "admin", panel: "pricing-academic-levels" },
      { key: "paper-type-rates", label: "Paper Type Rates", requiredScope: "admin", panel: "pricing-paper-types" },
      { key: "subject-rates", label: "Subject Rates", requiredScope: "admin", panel: "pricing-subject-rates" },
      { key: "work-type-rates", label: "Work Type Rates", requiredScope: "admin", panel: "pricing-work-types" },
      { key: "writer-level-rates", label: "Writer Level Rates", requiredScope: "admin", panel: "pricing-writer-levels" },
      { key: "diagram-complexity", label: "Diagram Complexity", requiredScope: "admin", panel: "pricing-diagram-complexity" },
      { key: "service-catalog", label: "Service Catalog", requiredScope: "admin", panel: "pricing-service-catalog" },
      { key: "service-addons", label: "Add-ons & Upsells", requiredScope: "admin", panel: "pricing-addons" },
      { key: "subject-multipliers", label: "Subject Multipliers", requiredScope: "admin" },
      { key: "writer-preference-fees", label: "Writer Preference Fees", requiredScope: "admin" },
      { key: "revision-pricing", label: "Revision Pricing", requiredScope: "admin" },
    ],
  },
  {
    key: "discounts",
    label: "Discounts & Referrals",
    iconName: "Tag",
    requiredScope: "admin",
    sections: [
      { key: "discount-codes", label: "Discount Codes", requiredScope: "admin", isCrud: true },
      { key: "referral-system", label: "Referral System", requiredScope: "admin" },
      { key: "first-order-discount",label: "First Order Discount", requiredScope: "admin" },
      { key: "loyalty-rules", label: "Loyalty Rules", requiredScope: "admin" },
    ],
  },
  {
    key: "marketing",
    label: "Marketing",
    iconName: "Megaphone",
    requiredScope: "admin",
    sections: [
      { key: "marketing-email", label: "Marketing Email", requiredScope: "admin" },
      { key: "email-templates", label: "Email Templates", requiredScope: "admin", pendingBackend: true },
      { key: "notification-rules", label: "Notification Rules", requiredScope: "admin" },
    ],
  },
  {
    key: "writer-management",
    label: "Writer Management",
    iconName: "PenTool",
    requiredScope: "admin",
    sections: [
      { key: "writer-registration", label: "Registration", requiredScope: "admin" },
      { key: "grammar-test", label: "Grammar Test", requiredScope: "admin" },
      { key: "time-management", label: "Time Management", requiredScope: "admin" },
      { key: "fines", label: "Fines & Penalties", requiredScope: "admin" },
      { key: "writer-policy", label: "Writer Policy", requiredScope: "admin" },
      { key: "writer-hierarchy", label: "Writer Hierarchy", requiredScope: "admin" },
      { key: "capacity-rules", label: "Capacity Rules", requiredScope: "admin" },
      { key: "payout-rules", label: "Payout Rules", requiredScope: "admin" },
    ],
  },
  {
    key: "payments",
    label: "Payments",
    iconName: "CreditCard",
    requiredScope: "admin",
    sections: [
      { key: "payment-gateway", label: "Payment Gateway", requiredScope: "superadmin" },
      { key: "wallet-rules", label: "Wallet Rules", requiredScope: "admin" },
      { key: "withdrawal-window", label: "Withdrawal Window", requiredScope: "admin" },
      { key: "refund-rules", label: "Refund Rules", requiredScope: "admin" },
    ],
  },
  {
    key: "communication",
    label: "Communication & Moderation",
    iconName: "MessageSquare",
    requiredScope: "support",
    sections: [
      { key: "message-policies", label: "Message Policies", requiredScope: "admin" },
      { key: "whatsapp-filters", label: "WhatsApp Filters", requiredScope: "admin" },
      { key: "disallowed-words", label: "Disallowed Words", requiredScope: "admin" },
      { key: "message-templates", label: "Message Templates", requiredScope: "support", pendingBackend: true },
      { key: "attachment-rules", label: "Attachment Rules", requiredScope: "admin" },
    ],
  },
  {
    key: "cms-seo",
    label: "CMS & SEO",
    iconName: "FileText",
    requiredScope: "editor",
    sections: [
      { key: "blog-categories", label: "Blog & Page Categories", requiredScope: "editor", isCrud: true },
      { key: "blog-persona", label: "Blog Persona", requiredScope: "editor" },
      { key: "seo-defaults", label: "SEO Defaults", requiredScope: "admin" },
      { key: "publishing-checklist", label: "Publishing Checklist", requiredScope: "editor" },
      { key: "content-rules", label: "Content Rules", requiredScope: "editor" },
    ],
  },
  {
    key: "security",
    label: "Security & Integrations",
    iconName: "ShieldCheck",
    requiredScope: "superadmin",
    sections: [
      { key: "api-keys", label: "API Keys", requiredScope: "superadmin", isCrud: true },
      { key: "webhooks", label: "Webhooks", requiredScope: "superadmin", pendingBackend: true },
      { key: "2fa-rules", label: "2FA Requirements", requiredScope: "superadmin" },
      { key: "session-rules", label: "Session Rules", requiredScope: "superadmin" },
      { key: "ip-restrictions",label: "IP Restrictions", requiredScope: "superadmin", pendingBackend: true },
    ],
  },
  {
    key: "system",
    label: "System",
    iconName: "Cpu",
    requiredScope: "superadmin",
    sections: [
      { key: "feature-flags", label: "Feature Flags", requiredScope: "superadmin" },
      { key: "rate-limits", label: "Rate Limits", requiredScope: "superadmin" },
      { key: "audit-policy", label: "Audit Policy", requiredScope: "superadmin" },
      { key: "maintenance", label: "Maintenance Mode", requiredScope: "superadmin" },
    ],
  },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

export function getDomain(key: string): ConfigDomainMeta | undefined {
  return DOMAINS.find((d) => d.key === key);
}

export function getSection(domainKey: string, sectionKey: string): ConfigSectionMeta | undefined {
  return getDomain(domainKey)?.sections.find((s) => s.key === sectionKey);
}

export function getSettingsForSection(domainKey: string, sectionKey: string): ConfigDefinition[] {
  return ALL_SETTINGS.filter((s) => s.domain === domainKey && s.section === sectionKey);
}

// Scope ranks for permission checks
const SCOPE_RANK: Record<string, number> = {
  support: 1, editor: 2, admin: 3, superadmin: 4,
};
export function scopeAllows(userScope: string, requiredScope: string): boolean {
  return (SCOPE_RANK[userScope] ?? 0) >= (SCOPE_RANK[requiredScope] ?? 99);
}

// ── All config definitions ────────────────────────────────────────────────────

export const ALL_SETTINGS: ConfigDefinition[] = [

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: order-management
  // ══════════════════════════════════════════════════════════════

  // Section: order-rules
  { key: "order_auto_complete_days", label: "Auto-complete after (days)", description: "Orders marked delivered auto-complete after this many days with no client action.", domain: "order-management", section: "order-rules", dataType: "number", defaultValue: 3, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "order_approval_mode", label: "Order approval mode", description: "Whether new orders are auto-approved or require manual admin review.", domain: "order-management", section: "order-rules", dataType: "select", defaultValue: "manual", requiredScope: "admin", websiteOverrideAllowed: true, options: [{ label: "Auto-approve", value: "auto" }, { label: "Manual review", value: "manual" }] },
  { key: "order_cancellation_window_hours",label: "Cancellation window (hours)", description: "How long a client can cancel an unassigned order for a full refund.", domain: "order-management", section: "order-rules", dataType: "number", defaultValue: 24, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "order_max_active_per_client", label: "Max active orders per client", description: "Caps how many open orders a single client account can hold.", domain: "order-management", section: "order-rules", dataType: "number", defaultValue: 10, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "order_require_brief_attachment",label: "Require brief attachment", description: "Force clients to upload at least one file when placing an order.", domain: "order-management", section: "order-rules", dataType: "boolean", defaultValue: false, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "order_brief_min_words", label: "Brief minimum words", description: "Minimum word count in the order brief before submission is allowed.", domain: "order-management", section: "order-rules", dataType: "number", defaultValue: 50, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: deadlines
  { key: "deadline_min_hours", label: "Minimum deadline (hours)", description: "Shortest deadline clients can select. Orders below this are blocked.", domain: "order-management", section: "deadlines", dataType: "number", defaultValue: 6, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "deadline_max_days", label: "Maximum deadline (days)", description: "Longest deadline clients can select.", domain: "order-management", section: "deadlines", dataType: "number", defaultValue: 60, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "deadline_urgency_threshold_hours",label: "Urgency threshold (hours)", description: "Orders below this deadline are flagged as urgent and may apply urgency pricing.", domain: "order-management", section: "deadlines", dataType: "number", defaultValue: 24, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "deadline_standard_threshold_hours",label: "Standard threshold (hours)", description: "Orders above this are considered standard (no urgency surcharge).", domain: "order-management", section: "deadlines", dataType: "number", defaultValue: 72, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "unpaid_order_auto_cancel_hours", label: "Auto-cancel unpaid after (hours)",description: "Unpaid orders are automatically cancelled after this window.", domain: "order-management", section: "deadlines", dataType: "number", defaultValue: 48, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "unpaid_order_reminder_interval", label: "Payment reminder interval (hours)",description: "How often to send payment reminders for unpaid orders.", domain: "order-management", section: "deadlines", dataType: "number", defaultValue: 12, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: writer-preferences
  { key: "preferred_writer_enabled", label: "Allow preferred writer", description: "Let clients request a specific writer on repeat orders.", domain: "order-management", section: "writer-preferences", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "preferred_writer_fee_percent", label: "Preferred writer fee (%)", description: "Extra fee charged when a client requests a preferred writer.", domain: "order-management", section: "writer-preferences", dataType: "percentage", defaultValue: 20, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "preferred_writer_window_days", label: "Preference window (days)", description: "How many days after an order is completed a client can lock in the same writer.", domain: "order-management", section: "writer-preferences", dataType: "number", defaultValue: 30, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "preferred_writer_max_active_orders", label: "Max parallel preferred orders", description: "How many preferred-writer orders can a writer handle simultaneously.", domain: "order-management", section: "writer-preferences", dataType: "number", defaultValue: 3, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: unpaid-orders
  { key: "unpaid_max_payment_attempts", label: "Max payment attempts", description: "Number of payment retry attempts before the order is marked failed.", domain: "order-management", section: "unpaid-orders", dataType: "number", defaultValue: 3, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "unpaid_hold_duration_hours", label: "Order hold duration (hours)", description: "How long an unpaid order stays in a reserved state awaiting payment.", domain: "order-management", section: "unpaid-orders", dataType: "number", defaultValue: 24, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "unpaid_notify_admin_after_hours",label: "Notify admin after (hours)", description: "Alert admins when an unpaid order has been waiting longer than this.", domain: "order-management", section: "unpaid-orders", dataType: "number", defaultValue: 6, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: client-order-policy
  { key: "client_max_daily_orders", label: "Max daily orders per client", description: "Cap on how many orders a single client can place in one day.", domain: "order-management", section: "client-order-policy", dataType: "number", defaultValue: 5, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "client_cancellation_before_assign_refund_percent", label: "Refund % before assignment", description: "Percentage of order value refunded on cancellation before writer assignment.", domain: "order-management", section: "client-order-policy", dataType: "percentage", defaultValue: 100, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "client_cancellation_after_assign_refund_percent", label: "Refund % after assignment", description: "Percentage of order value refunded after a writer has been assigned.", domain: "order-management", section: "client-order-policy", dataType: "percentage", defaultValue: 50, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "client_revision_window_days", label: "Revision window (days)", description: "How long after delivery a client can request a free revision.", domain: "order-management", section: "client-order-policy", dataType: "number", defaultValue: 7, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "client_max_revisions_per_order", label: "Max free revisions per order", description: "Maximum number of free revision cycles allowed per order.", domain: "order-management", section: "client-order-policy", dataType: "number", defaultValue: 3, requiredScope: "admin", websiteOverrideAllowed: true },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: pricing
  // ══════════════════════════════════════════════════════════════

  // Section: base-rates
  { key: "pricing_base_price_per_page", label: "Base price per page", description: "Starting price per page at standard academic level with no urgency.", domain: "pricing", section: "base-rates", dataType: "currency", defaultValue: 12.00, requiredScope: "superadmin", websiteOverrideAllowed: true },
  { key: "pricing_min_order_price", label: "Minimum order price", description: "Floor price — no order can be placed below this amount.", domain: "pricing", section: "base-rates", dataType: "currency", defaultValue: 10.00, requiredScope: "superadmin", websiteOverrideAllowed: true },
  { key: "pricing_currency", label: "Default currency", description: "Primary currency for the website. Affects display and checkout.", domain: "pricing", section: "base-rates", dataType: "select", defaultValue: "USD", requiredScope: "superadmin", websiteOverrideAllowed: true, options: [{ label: "USD $", value: "USD" }, { label: "GBP £", value: "GBP" }, { label: "EUR €", value: "EUR" }, { label: "CAD $", value: "CAD" }] },
  { key: "pricing_words_per_page", label: "Words per page", description: "Word count that constitutes a single page for pricing purposes.", domain: "pricing", section: "base-rates", dataType: "number", defaultValue: 275, requiredScope: "superadmin", websiteOverrideAllowed: false },

  // Section: deadline-bands
  { key: "pricing_urgency_6h_multiplier", label: "6h deadline uplift (%)", description: "Price premium applied to orders with a 6-hour deadline.", domain: "pricing", section: "deadline-bands", dataType: "percentage", defaultValue: 100, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_urgency_12h_multiplier", label: "12h deadline uplift (%)", description: "Price premium for 12-hour deadlines.", domain: "pricing", section: "deadline-bands", dataType: "percentage", defaultValue: 75, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_urgency_24h_multiplier", label: "24h deadline uplift (%)", description: "Price premium for 24-hour deadlines.", domain: "pricing", section: "deadline-bands", dataType: "percentage", defaultValue: 50, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_urgency_48h_multiplier", label: "48h deadline uplift (%)", description: "Price premium for 48-hour deadlines.", domain: "pricing", section: "deadline-bands", dataType: "percentage", defaultValue: 25, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_standard_multiplier", label: "Standard (72h+) uplift (%)",description: "Surcharge for standard deadlines (no uplift by default).", domain: "pricing", section: "deadline-bands", dataType: "percentage", defaultValue: 0, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: academic-level-rates
  { key: "pricing_high_school_multiplier", label: "High School multiplier (%)", description: "Price adjustment for high school level orders.", domain: "pricing", section: "academic-level-rates", dataType: "percentage", defaultValue: 0, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_undergrad_multiplier", label: "Undergraduate multiplier (%)", description: "Price adjustment for undergraduate level orders.", domain: "pricing", section: "academic-level-rates", dataType: "percentage", defaultValue: 10, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_masters_multiplier", label: "Masters multiplier (%)", description: "Price adjustment for master's level orders.", domain: "pricing", section: "academic-level-rates", dataType: "percentage", defaultValue: 25, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_phd_multiplier", label: "PhD multiplier (%)", description: "Price adjustment for doctoral level orders.", domain: "pricing", section: "academic-level-rates", dataType: "percentage", defaultValue: 40, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: subject-multipliers
  { key: "pricing_technical_subject_uplift",label: "Technical subject uplift (%)", description: "Extra % added for STEM, law, and other technical subjects.", domain: "pricing", section: "subject-multipliers", dataType: "percentage", defaultValue: 15, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_medical_subject_uplift", label: "Medical subject uplift (%)", description: "Extra % added for nursing, medicine, and health sciences.", domain: "pricing", section: "subject-multipliers", dataType: "percentage", defaultValue: 20, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: writer-preference-fees
  { key: "pricing_preferred_writer_fee", label: "Preferred writer fee (%)", description: "Fee added when a client specifically requests a writer by name.", domain: "pricing", section: "writer-preference-fees", dataType: "percentage", defaultValue: 20, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_top_rated_fee", label: "Top-rated writer fee (%)", description: "Fee added when the assigned writer is top-rated tier.", domain: "pricing", section: "writer-preference-fees", dataType: "percentage", defaultValue: 30, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_expert_fee", label: "Expert writer fee (%)", description: "Fee added when the assigned writer is expert tier.", domain: "pricing", section: "writer-preference-fees", dataType: "percentage", defaultValue: 40, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: revision-pricing
  { key: "pricing_free_revisions_included", label: "Free revisions included", description: "Number of revisions included in the base price.", domain: "pricing", section: "revision-pricing", dataType: "number", defaultValue: 1, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_paid_revision_price", label: "Paid revision price", description: "Price charged for each revision beyond the free allowance.", domain: "pricing", section: "revision-pricing", dataType: "currency", defaultValue: 5.00, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "pricing_scope_check_required", label: "Require scope check", description: "Force admins to verify revision scope before marking it paid.", domain: "pricing", section: "revision-pricing", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: discounts
  // ══════════════════════════════════════════════════════════════

  // Section: referral-system
  { key: "referral_enabled", label: "Referral programme enabled", description: "Turn the entire referral programme on or off.", domain: "discounts", section: "referral-system", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "referral_reward_type", label: "Reward type", description: "How the referrer is rewarded when a referred client places their first order.", domain: "discounts", section: "referral-system", dataType: "select", defaultValue: "credit", requiredScope: "admin", websiteOverrideAllowed: true, options: [{ label: "Wallet credit", value: "credit" }, { label: "Discount % off next order", value: "discount_percent" }, { label: "Fixed cash", value: "fixed" }] },
  { key: "referral_reward_amount", label: "Reward amount", description: "The value of the reward (credit amount, % or fixed cash).", domain: "discounts", section: "referral-system", dataType: "number", defaultValue: 10, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "referral_referee_discount_percent", label: "Referee first-order discount (%)",description: "Discount given to the referred client on their first order.", domain: "discounts", section: "referral-system", dataType: "percentage",defaultValue: 10, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "referral_max_per_user", label: "Max referrals per user", description: "Cap on how many successful referrals one user can earn rewards for.", domain: "discounts", section: "referral-system", dataType: "number", defaultValue: 20, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "referral_reward_on_first_order_only",label: "Reward on first order only",description: "Only pay the referral reward when the referred user completes their first order.", domain: "discounts", section: "referral-system", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: first-order-discount
  { key: "first_order_discount_enabled", label: "First-order discount enabled",description: "Automatically apply a discount to each new client's first order.", domain: "discounts", section: "first-order-discount", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "first_order_discount_type", label: "Discount type", description: "Whether the discount is a flat percentage or a fixed currency amount.", domain: "discounts", section: "first-order-discount", dataType: "select", defaultValue: "percentage", requiredScope: "admin", websiteOverrideAllowed: true, options: [{ label: "Percentage off", value: "percentage" }, { label: "Fixed amount off", value: "fixed" }] },
  { key: "first_order_discount_value", label: "Discount value", description: "The size of the first-order discount (% or currency depending on type).", domain: "discounts", section: "first-order-discount", dataType: "number", defaultValue: 15, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "first_order_min_pages", label: "Minimum pages to qualify", description: "Order must be at least this many pages for the first-order discount to apply.", domain: "discounts", section: "first-order-discount", dataType: "number", defaultValue: 2, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: loyalty-rules
  { key: "loyalty_enabled", label: "Loyalty programme enabled", description: "Enable tiered loyalty rewards for repeat clients.", domain: "discounts", section: "loyalty-rules", dataType: "boolean", defaultValue: false, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "loyalty_threshold_orders", label: "Loyalty threshold (orders)", description: "Number of completed orders needed to enter the first loyalty tier.", domain: "discounts", section: "loyalty-rules", dataType: "number", defaultValue: 10, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "loyalty_discount_percent", label: "Loyalty discount (%)", description: "Standing discount applied to all orders once a client reaches the loyalty threshold.", domain: "discounts", section: "loyalty-rules", dataType: "percentage", defaultValue: 5, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "loyalty_tier_names", label: "Tier names", description: "Comma-separated tier labels (Bronze, Silver, Gold, Platinum).", domain: "discounts", section: "loyalty-rules", dataType: "text", defaultValue: "Bronze,Silver,Gold,Platinum", requiredScope: "admin", websiteOverrideAllowed: true },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: marketing
  // ══════════════════════════════════════════════════════════════

  // Section: marketing-email
  { key: "email_from_name", label: "From name", description: "Name shown in the email 'From' field.", domain: "marketing", section: "marketing-email", dataType: "text", defaultValue: "", requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "email_from_address", label: "From address", description: "Sending email address for all marketing emails.", domain: "marketing", section: "marketing-email", dataType: "text", defaultValue: "",requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "email_reply_to", label: "Reply-to address", description: "Where replies are routed when a recipient replies to a marketing email.", domain: "marketing", section: "marketing-email", dataType: "text", defaultValue: "",requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "email_max_per_week", label: "Max marketing emails/week",description: "Rate cap on marketing emails per client per week.", domain: "marketing", section: "marketing-email", dataType: "number", defaultValue: 2, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "email_marketing_enabled", label: "Marketing email enabled", description: "Global toggle for all outbound marketing emails.", domain: "marketing", section: "marketing-email", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: notification-rules
  { key: "notify_order_placed", label: "Notify: order placed", description: "Send email notification when a new order is placed.", domain: "marketing", section: "notification-rules", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "notify_writer_assigned", label: "Notify: writer assigned", description: "Send notification when a writer is assigned to an order.", domain: "marketing", section: "notification-rules", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "notify_order_delivered", label: "Notify: order delivered", description: "Send notification when an order is delivered.", domain: "marketing", section: "notification-rules", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "notify_revision_requested", label: "Notify: revision requested",description: "Send notification to writer when client requests a revision.", domain: "marketing", section: "notification-rules", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "notify_payment_received", label: "Notify: payment received", description: "Send notification when a payment is confirmed.", domain: "marketing", section: "notification-rules", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "notify_digest_enabled", label: "Daily digest enabled", description: "Send a daily summary email instead of individual notifications.", domain: "marketing", section: "notification-rules", dataType: "boolean", defaultValue: false, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "notify_digest_frequency", label: "Digest frequency", description: "How often the digest email is sent.", domain: "marketing", section: "notification-rules", dataType: "select", defaultValue: "daily", requiredScope: "admin", websiteOverrideAllowed: true, options: [{ label: "Daily", value: "daily" }, { label: "Weekly", value: "weekly" }] },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: writer-management
  // ══════════════════════════════════════════════════════════════

  // Section: writer-registration
  { key: "writer_reg_require_portfolio", label: "Require portfolio upload", description: "Writer must submit writing samples during registration.", domain: "writer-management", section: "writer-registration", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_reg_require_grammar_test",label: "Require grammar test", description: "Writer must pass the grammar test before their account is activated.", domain: "writer-management", section: "writer-registration", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_reg_require_interview", label: "Require interview", description: "Writer must complete a staff interview before approval.", domain: "writer-management", section: "writer-registration", dataType: "boolean", defaultValue: false, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_reg_auto_approve", label: "Auto-approve writers", description: "Skip manual admin review — writers are approved automatically on passing all tests.", domain: "writer-management", section: "writer-registration", dataType: "boolean", defaultValue: false, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_reg_min_education", label: "Minimum education level", description: "The lowest academic qualification accepted during writer registration.", domain: "writer-management", section: "writer-registration", dataType: "select", defaultValue: "undergraduate", requiredScope: "admin", websiteOverrideAllowed: false, options: [{ label: "High School", value: "high_school" }, { label: "Undergraduate", value: "undergraduate" }, { label: "Masters", value: "masters" }, { label: "PhD", value: "phd" }] },

  // Section: grammar-test
  { key: "grammar_test_enabled", label: "Grammar test enabled", description: "Enable the built-in grammar test as part of writer onboarding.", domain: "writer-management", section: "grammar-test", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "grammar_test_pass_score", label: "Pass score (%)", description: "Minimum percentage score to pass the grammar test.", domain: "writer-management", section: "grammar-test", dataType: "percentage", defaultValue: 75, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "grammar_test_max_attempts", label: "Max attempts", description: "How many times a writer can retake the test before being blocked.", domain: "writer-management", section: "grammar-test", dataType: "number", defaultValue: 3, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "grammar_test_duration_minutes", label: "Test duration (minutes)", description: "Time limit for each grammar test session.", domain: "writer-management", section: "grammar-test", dataType: "number", defaultValue: 30, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "grammar_test_retake_cooldown_days",label: "Retake cooldown (days)", description: "How long a writer must wait before retaking the test.", domain: "writer-management", section: "grammar-test", dataType: "number", defaultValue: 14, requiredScope: "admin", websiteOverrideAllowed: false },

  // Section: time-management
  { key: "writer_warning_threshold_hours", label: "Warning threshold (hours)", description: "Send a warning to the writer when this many hours remain before deadline.", domain: "writer-management", section: "time-management", dataType: "number", defaultValue: 12, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_grace_period_hours", label: "Grace period (hours)", description: "Buffer added after deadline before a late submission penalty is applied.", domain: "writer-management", section: "time-management", dataType: "number", defaultValue: 2, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_late_trigger_hours", label: "Late penalty trigger (hours)", description: "Hours past deadline before the formal late-submission fine is applied.", domain: "writer-management", section: "time-management", dataType: "number", defaultValue: 1, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_auto_reassign_hours", label: "Auto-reassign after (hours)", description: "Hours past deadline after which the order is automatically reassigned.", domain: "writer-management", section: "time-management", dataType: "number", defaultValue: 4, requiredScope: "admin", websiteOverrideAllowed: false },

  // Section: fines
  { key: "fine_late_submission_percent", label: "Late submission fine (%)", description: "Percentage deducted from the writer's payout for a late delivery.", domain: "writer-management", section: "fines", dataType: "percentage", defaultValue: 10, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "fine_revision_failure_percent", label: "Revision failure fine (%)", description: "Percentage deducted when a writer fails to address revision notes.", domain: "writer-management", section: "fines", dataType: "percentage", defaultValue: 5, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "fine_dispute_ruling_percent", label: "Dispute ruling fine (%)", description: "Deducted from the writer's payout when a dispute is ruled against them.", domain: "writer-management", section: "fines", dataType: "percentage", defaultValue: 20, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "fine_plagiarism_percent", label: "Plagiarism fine (%)", description: "Deducted from the writer's payout when plagiarism is confirmed.", domain: "writer-management", section: "fines", dataType: "percentage", defaultValue: 50, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "fine_min_amount", label: "Minimum fine amount", description: "Floor on fines — no fine can be less than this regardless of order size.", domain: "writer-management", section: "fines", dataType: "currency", defaultValue: 1.00, requiredScope: "admin", websiteOverrideAllowed: false },

  // Section: writer-policy
  { key: "writer_policy_text", label: "Writer policy text", description: "Full policy shown to writers during onboarding and accessible from their dashboard.", domain: "writer-management", section: "writer-policy", dataType: "textarea", defaultValue: "", requiredScope: "admin", websiteOverrideAllowed: false },

  // Section: writer-hierarchy
  { key: "writer_level_names", label: "Level names", description: "Comma-separated tier labels from lowest to highest.", domain: "writer-management", section: "writer-hierarchy", dataType: "text", defaultValue: "Beginner,Standard,Expert,Elite", requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_level_threshold_2", label: "Standard threshold (orders)",description: "Completed orders required to be promoted to Standard.", domain: "writer-management", section: "writer-hierarchy", dataType: "number", defaultValue: 20, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_level_threshold_3", label: "Expert threshold (orders)", description: "Completed orders required to be promoted to Expert.", domain: "writer-management", section: "writer-hierarchy", dataType: "number", defaultValue: 50, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_level_threshold_4", label: "Elite threshold (orders)", description: "Completed orders required to be promoted to Elite.", domain: "writer-management", section: "writer-hierarchy", dataType: "number", defaultValue: 100, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_level_min_rating", label: "Min rating for promotion", description: "Average rating a writer must maintain to be eligible for promotion.", domain: "writer-management", section: "writer-hierarchy", dataType: "number", defaultValue: 4.5, requiredScope: "admin", websiteOverrideAllowed: false },

  // Section: capacity-rules
  { key: "writer_capacity_beginner", label: "Beginner max active orders", description: "Maximum simultaneous active orders for Beginner tier writers.", domain: "writer-management", section: "capacity-rules", dataType: "number", defaultValue: 3, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_capacity_standard", label: "Standard max active orders", description: "Maximum simultaneous active orders for Standard tier writers.", domain: "writer-management", section: "capacity-rules", dataType: "number", defaultValue: 6, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_capacity_expert", label: "Expert max active orders", description: "Maximum simultaneous active orders for Expert tier writers.", domain: "writer-management", section: "capacity-rules", dataType: "number", defaultValue: 10, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_capacity_elite", label: "Elite max active orders", description: "Maximum simultaneous active orders for Elite tier writers.", domain: "writer-management", section: "capacity-rules", dataType: "number", defaultValue: 15, requiredScope: "admin", websiteOverrideAllowed: false },

  // Section: payout-rules
  { key: "writer_payout_schedule", label: "Payout schedule", description: "How often writers receive their accumulated earnings.", domain: "writer-management", section: "payout-rules", dataType: "select", defaultValue: "weekly", requiredScope: "admin", websiteOverrideAllowed: false, options: [{ label: "Instant", value: "instant" }, { label: "Weekly", value: "weekly" }, { label: "Bi-weekly", value: "biweekly" }, { label: "Monthly", value: "monthly" }] },
  { key: "writer_payout_min_amount", label: "Minimum payout amount", description: "Writers must accumulate at least this balance before a payout is processed.", domain: "writer-management", section: "payout-rules", dataType: "currency", defaultValue: 20.00, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_payout_processing_days", label: "Processing time (days)", description: "Business days taken to process a payout once triggered.", domain: "writer-management", section: "payout-rules", dataType: "number", defaultValue: 3, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "writer_payout_base_percent", label: "Writer base payout (%)", description: "Percentage of the order value paid to the writer. Sensitive — superadmin only.", domain: "writer-management", section: "payout-rules", dataType: "percentage", defaultValue: 70, requiredScope: "superadmin", websiteOverrideAllowed: false, isSensitive: true },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: payments
  // ══════════════════════════════════════════════════════════════

  // Section: payment-gateway
  { key: "payment_gateway_provider", label: "Gateway provider", description: "Primary payment processor used for client transactions.", domain: "payments", section: "payment-gateway", dataType: "select", defaultValue: "stripe", requiredScope: "superadmin", websiteOverrideAllowed: false, options: [{ label: "Stripe", value: "stripe" }, { label: "PayPal", value: "paypal" }, { label: "Flutterwave", value: "flutterwave" }] },
  { key: "payment_gateway_mode", label: "Gateway mode", description: "Test mode uses sandbox credentials; live mode charges real cards.", domain: "payments", section: "payment-gateway", dataType: "select", defaultValue: "test", requiredScope: "superadmin", websiteOverrideAllowed: false, options: [{ label: "Test (sandbox)", value: "test" }, { label: "Live", value: "live" }] },
  { key: "payment_public_key", label: "Public / publishable key",description: "Client-facing API key (safe to expose in frontend).", domain: "payments", section: "payment-gateway", dataType: "text", defaultValue: "", requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "payment_secret_key", label: "Secret key", description: "Server-side secret key. Never logged or exposed.", domain: "payments", section: "payment-gateway", dataType: "text", defaultValue: "", requiredScope: "superadmin", websiteOverrideAllowed: false, isSensitive: true },
  { key: "payment_webhook_url", label: "Webhook endpoint URL", description: "URL where the gateway sends payment event notifications.", domain: "payments", section: "payment-gateway", dataType: "text", defaultValue: "", requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "payment_currency", label: "Payment currency", description: "Currency accepted at checkout. Must match the gateway's supported currencies.", domain: "payments", section: "payment-gateway", dataType: "select", defaultValue: "USD", requiredScope: "superadmin", websiteOverrideAllowed: true, options: [{ label: "USD $", value: "USD" }, { label: "GBP £", value: "GBP" }, { label: "EUR €", value: "EUR" }, { label: "KES", value: "KES" }] },

  // Section: wallet-rules
  { key: "wallet_enabled", label: "Wallet enabled", description: "Allow clients to maintain a prepaid wallet balance.", domain: "payments", section: "wallet-rules", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "wallet_min_balance", label: "Minimum balance", description: "Wallet cannot go below this amount (0 = no floor).", domain: "payments", section: "wallet-rules", dataType: "currency", defaultValue: 0, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "wallet_low_balance_threshold", label: "Low balance alert", description: "Send a low-balance alert when wallet drops below this amount.", domain: "payments", section: "wallet-rules", dataType: "currency", defaultValue: 5.00, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "wallet_auto_top_up_enabled", label: "Auto top-up enabled", description: "Automatically top up the wallet from a saved payment method.", domain: "payments", section: "wallet-rules", dataType: "boolean", defaultValue: false, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "wallet_auto_top_up_amount", label: "Auto top-up amount", description: "Amount to add when auto top-up is triggered.", domain: "payments", section: "wallet-rules", dataType: "currency", defaultValue: 20.00, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: withdrawal-window
  { key: "withdrawal_min_amount", label: "Minimum withdrawal", description: "Writers must request at least this amount per withdrawal.", domain: "payments", section: "withdrawal-window", dataType: "currency", defaultValue: 10.00, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "withdrawal_max_amount", label: "Maximum withdrawal", description: "Cap on single withdrawal requests.", domain: "payments", section: "withdrawal-window", dataType: "currency", defaultValue: 1000.00,requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "withdrawal_processing_days", label: "Processing time (days)", description: "Business days to process an approved withdrawal.", domain: "payments", section: "withdrawal-window", dataType: "number", defaultValue: 3, requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "withdrawal_allowed_days", label: "Allowed request days", description: "Comma-separated weekdays when withdrawal requests can be submitted.", domain: "payments", section: "withdrawal-window", dataType: "text", defaultValue: "Monday,Tuesday,Wednesday,Thursday,Friday", requiredScope: "admin", websiteOverrideAllowed: false },
  { key: "withdrawal_fee_percent", label: "Withdrawal fee (%)", description: "Platform fee deducted from each withdrawal.", domain: "payments", section: "withdrawal-window", dataType: "percentage", defaultValue: 2, requiredScope: "admin", websiteOverrideAllowed: false },

  // Section: refund-rules
  { key: "refund_window_days", label: "Refund window (days)", description: "How long after order completion a client can request a refund.", domain: "payments", section: "refund-rules", dataType: "number", defaultValue: 14, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "refund_auto_approve_under", label: "Auto-approve under", description: "Refund requests below this amount are automatically approved.", domain: "payments", section: "refund-rules", dataType: "currency", defaultValue: 20.00,requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "refund_partial_enabled", label: "Allow partial refunds", description: "Allow admins to issue refunds for less than the full order amount.", domain: "payments", section: "refund-rules", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "refund_max_percent_after_delivery",label: "Max refund % after delivery", description: "Maximum refund percentage allowed once the order has been delivered.", domain: "payments", section: "refund-rules", dataType: "percentage",defaultValue: 50, requiredScope: "admin", websiteOverrideAllowed: true },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: communication
  // ══════════════════════════════════════════════════════════════

  // Section: message-policies
  { key: "message_max_length", label: "Max message length (chars)", description: "Maximum characters allowed in a single message.", domain: "communication", section: "message-policies", dataType: "number", defaultValue: 5000, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "message_attachments_enabled", label: "Attachments enabled", description: "Allow files to be attached to messages.", domain: "communication", section: "message-policies", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "message_max_attachments", label: "Max attachments per message", description: "Number of files allowed per message.", domain: "communication", section: "message-policies", dataType: "number", defaultValue: 5, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "message_link_allowed", label: "External links allowed", description: "Allow messages to contain external URLs.", domain: "communication", section: "message-policies", dataType: "boolean", defaultValue: false,requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "message_read_receipts", label: "Read receipts enabled", description: "Show senders when their message has been read.", domain: "communication", section: "message-policies", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "message_escalation_auto_hours", label: "Auto-escalation (hours)", description: "Unresolved threads are automatically escalated after this many hours.", domain: "communication", section: "message-policies", dataType: "number", defaultValue: 72, requiredScope: "admin", websiteOverrideAllowed: true },

  // Section: attachment-rules
  { key: "attachment_max_size_mb", label: "Max attachment size (MB)", description: "Maximum file size allowed per attachment.", domain: "communication", section: "attachment-rules", dataType: "number", defaultValue: 50, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "attachment_allowed_types", label: "Allowed file types", description: "Comma-separated list of allowed extensions.", domain: "communication", section: "attachment-rules", dataType: "text", defaultValue: "pdf,doc,docx,txt,jpg,png,zip", requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "attachment_virus_scan_enabled",label: "Virus scan on upload", description: "Scan all uploaded files before storing.", domain: "communication", section: "attachment-rules", dataType: "boolean", defaultValue: true, requiredScope: "superadmin", websiteOverrideAllowed: false },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: cms-seo
  // ══════════════════════════════════════════════════════════════

  // Section: blog-persona
  { key: "blog_author_name", label: "Default author name", description: "Name used for blog posts without a specific author assigned.", domain: "cms-seo", section: "blog-persona", dataType: "text", defaultValue: "", requiredScope: "editor", websiteOverrideAllowed: true },
  { key: "blog_author_bio", label: "Default author bio", description: "Short bio shown under blog posts from the default author.", domain: "cms-seo", section: "blog-persona", dataType: "textarea", defaultValue: "", requiredScope: "editor", websiteOverrideAllowed: true },

  // Section: seo-defaults
  { key: "seo_title_suffix", label: "Title suffix", description: "Appended to every page title (e.g. ' | NurseMyGrade').", domain: "cms-seo", section: "seo-defaults", dataType: "text", defaultValue: "", requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "seo_meta_desc_max_length", label: "Meta description max length", description: "Warn editors when meta descriptions exceed this character count.", domain: "cms-seo", section: "seo-defaults", dataType: "number", defaultValue: 160, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "seo_canonical_enabled", label: "Canonical tags enabled", description: "Add canonical link elements to all published pages.", domain: "cms-seo", section: "seo-defaults", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },
  { key: "seo_noindex_draft_pages", label: "No-index draft pages", description: "Prevent draft/unpublished pages from being indexed.", domain: "cms-seo", section: "seo-defaults", dataType: "boolean", defaultValue: true, requiredScope: "editor", websiteOverrideAllowed: true },

  // Section: publishing-checklist
  { key: "cms_min_word_count", label: "Minimum word count", description: "Posts shorter than this are flagged before publishing.", domain: "cms-seo", section: "publishing-checklist", dataType: "number", defaultValue: 300, requiredScope: "editor", websiteOverrideAllowed: true },
  { key: "cms_require_featured_image", label: "Featured image required", description: "Block publishing if no featured image is attached.", domain: "cms-seo", section: "publishing-checklist", dataType: "boolean", defaultValue: true, requiredScope: "editor", websiteOverrideAllowed: true },
  { key: "cms_require_meta_description", label: "Meta description required", description: "Block publishing if the meta description is empty.", domain: "cms-seo", section: "publishing-checklist", dataType: "boolean", defaultValue: true, requiredScope: "editor", websiteOverrideAllowed: true },
  { key: "cms_require_category", label: "Category required", description: "Block publishing if no category is assigned.", domain: "cms-seo", section: "publishing-checklist", dataType: "boolean", defaultValue: true, requiredScope: "editor", websiteOverrideAllowed: true },
  { key: "cms_freshness_threshold_days", label: "Content freshness (days)", description: "Flag content for review when it has not been updated in this many days.", domain: "cms-seo", section: "publishing-checklist", dataType: "number", defaultValue: 180, requiredScope: "editor", websiteOverrideAllowed: true },

  // Section: content-rules
  { key: "cms_min_word_count_warning", label: "Short post warning threshold", description: "Show a warning (not a block) when content is below this word count.", domain: "cms-seo", section: "content-rules", dataType: "number", defaultValue: 500, requiredScope: "editor", websiteOverrideAllowed: true },
  { key: "cms_image_compression_enabled",label: "Compress uploaded images", description: "Automatically compress images on upload to reduce page load times.", domain: "cms-seo", section: "content-rules", dataType: "boolean", defaultValue: true, requiredScope: "admin", websiteOverrideAllowed: true },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: security
  // ══════════════════════════════════════════════════════════════

  // Section: 2fa-rules
  { key: "security_require_2fa_superadmin",label: "Require 2FA: Superadmin", description: "All superadmin accounts must have 2FA enabled.", domain: "security", section: "2fa-rules", dataType: "boolean", defaultValue: true, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "security_require_2fa_admin", label: "Require 2FA: Admin", description: "All admin accounts must have 2FA enabled.", domain: "security", section: "2fa-rules", dataType: "boolean", defaultValue: true, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "security_require_2fa_editor", label: "Require 2FA: Editor", description: "All editor accounts must have 2FA enabled.", domain: "security", section: "2fa-rules", dataType: "boolean", defaultValue: false, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "security_require_2fa_support", label: "Require 2FA: Support", description: "All support accounts must have 2FA enabled.", domain: "security", section: "2fa-rules", dataType: "boolean", defaultValue: false, requiredScope: "superadmin", websiteOverrideAllowed: false },

  // Section: session-rules
  { key: "security_session_lifetime_hours", label: "Session lifetime (hours)", description: "Authenticated sessions expire after this duration of inactivity.", domain: "security", section: "session-rules", dataType: "number", defaultValue: 24, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "security_remember_me_days", label: "Remember me duration (days)", description: "Lifetime of 'remember me' tokens.", domain: "security", section: "session-rules", dataType: "number", defaultValue: 30, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "security_max_concurrent_sessions", label: "Max concurrent sessions", description: "Maximum number of active sessions allowed per user.", domain: "security", section: "session-rules", dataType: "number", defaultValue: 3, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "security_idle_timeout_minutes", label: "Idle timeout (minutes)", description: "Automatically log out a session that has been idle for this long.", domain: "security", section: "session-rules", dataType: "number", defaultValue: 60, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "security_login_max_attempts", label: "Max login attempts", description: "Lock an account after this many consecutive failed login attempts.", domain: "security", section: "session-rules", dataType: "number", defaultValue: 5, requiredScope: "superadmin", websiteOverrideAllowed: false },

  // Section: webhooks
  { key: "webhook_retry_attempts", label: "Retry attempts", description: "How many times a failed webhook delivery is retried.", domain: "security", section: "webhooks", dataType: "number", defaultValue: 3, requiredScope: "superadmin", websiteOverrideAllowed: false, pendingBackend: true },
  { key: "webhook_timeout_seconds", label: "Timeout (seconds)", description: "Maximum seconds to wait for a webhook endpoint to respond.", domain: "security", section: "webhooks", dataType: "number", defaultValue: 30, requiredScope: "superadmin", websiteOverrideAllowed: false, pendingBackend: true },
  { key: "webhook_signature_enabled", label: "Signature verification",description: "Sign all outbound webhook payloads and require verification.", domain: "security", section: "webhooks", dataType: "boolean", defaultValue: true, requiredScope: "superadmin", websiteOverrideAllowed: false, pendingBackend: true },

  // ══════════════════════════════════════════════════════════════
  // DOMAIN: system
  // ══════════════════════════════════════════════════════════════

  // Section: feature-flags
  { key: "flag_maintenance_mode", label: "Maintenance mode", description: "Take the site offline and show a maintenance page to all visitors.", domain: "system", section: "feature-flags", dataType: "boolean", defaultValue: false, requiredScope: "superadmin", websiteOverrideAllowed: true },
  { key: "flag_new_order_flow_v2", label: "New order flow v2", description: "Enable the redesigned multi-step order placement flow.", domain: "system", section: "feature-flags", dataType: "boolean", defaultValue: false, requiredScope: "superadmin", websiteOverrideAllowed: true },
  { key: "flag_writer_bidding", label: "Writer bidding", description: "Allow writers to bid on orders instead of auto-assignment.", domain: "system", section: "feature-flags", dataType: "boolean", defaultValue: false, requiredScope: "superadmin", websiteOverrideAllowed: true },
  { key: "flag_live_chat", label: "Live chat widget", description: "Show the live chat widget on the client portal.", domain: "system", section: "feature-flags", dataType: "boolean", defaultValue: false, requiredScope: "superadmin", websiteOverrideAllowed: true },
  { key: "flag_ai_writing_assist", label: "AI writing assist", description: "Enable AI-powered writing suggestions in the order brief editor.", domain: "system", section: "feature-flags", dataType: "boolean", defaultValue: false, requiredScope: "superadmin", websiteOverrideAllowed: false },

  // Section: rate-limits
  { key: "rate_limit_api_per_minute", label: "API rate limit (per minute)",description: "Maximum API requests allowed per authenticated user per minute.", domain: "system", section: "rate-limits", dataType: "number", defaultValue: 60, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "rate_limit_burst", label: "Burst limit", description: "Short-window request spike allowed beyond the per-minute rate.", domain: "system", section: "rate-limits", dataType: "number", defaultValue: 20, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "rate_limit_login_attempts", label: "Login rate limit", description: "Max login attempts per IP per 15 minutes before throttling.", domain: "system", section: "rate-limits", dataType: "number", defaultValue: 5, requiredScope: "superadmin", websiteOverrideAllowed: false },

  // Section: audit-policy
  { key: "audit_retention_days", label: "Audit log retention (days)", description: "How long audit entries are stored before automatic purge.", domain: "system", section: "audit-policy", dataType: "number", defaultValue: 365, requiredScope: "superadmin", websiteOverrideAllowed: false },
  { key: "audit_log_level", label: "Log level", description: "Controls verbosity of the audit trail.", domain: "system", section: "audit-policy", dataType: "select", defaultValue: "standard", requiredScope: "superadmin", websiteOverrideAllowed: false, options: [{ label: "Minimal", value: "minimal" }, { label: "Standard", value: "standard" }, { label: "Verbose", value: "verbose" }] },
  { key: "audit_sensitive_logging", label: "Log sensitive data", description: "Include sensitive field values in audit records (e.g. payment keys). Use with extreme caution.", domain: "system", section: "audit-policy", dataType: "boolean", defaultValue: false, requiredScope: "superadmin", websiteOverrideAllowed: false, isSensitive: true },

  // Section: maintenance
  { key: "maintenance_message", label: "Maintenance message", description: "Message shown to users while the site is in maintenance mode.", domain: "system", section: "maintenance", dataType: "textarea", defaultValue: "We are performing scheduled maintenance. Please check back shortly.", requiredScope: "superadmin", websiteOverrideAllowed: true },
  { key: "maintenance_allowed_ips", label: "Allowlist IPs", description: "Comma-separated IP addresses that bypass maintenance mode.", domain: "system", section: "maintenance", dataType: "textarea", defaultValue: "", requiredScope: "superadmin", websiteOverrideAllowed: true },
  { key: "maintenance_eta_minutes", label: "Estimated downtime (min)", description: "Shown in the maintenance page to inform users how long to expect.", domain: "system", section: "maintenance", dataType: "number", defaultValue: 30, requiredScope: "superadmin", websiteOverrideAllowed: true },
];
