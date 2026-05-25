import type { UserRole } from "@/types/roles";

export interface MetricDefinition {
  label: string;
  value: string;
  detail: string;
  tone: "neutral" | "good" | "warn" | "risk";
}

export interface WorkItem {
  title: string;
  meta: string;
  status: string;
}

export interface DashboardDefinition {
  title: string;
  subtitle: string;
  primaryAction: string;
  metrics: MetricDefinition[];
  work: WorkItem[];
  panels: string[];
}

export const dashboards: Record<UserRole, DashboardDefinition> = {
  superadmin: {
    title: "Platform command",
    subtitle: "Cross-tenant health, revenue, security, and operational drift.",
    primaryAction: "Review system health",
    metrics: [
      { label: "Active sites", value: "12", detail: "2 pending review", tone: "neutral" },
      { label: "Queue health", value: "96%", detail: "Celery and API nominal", tone: "good" },
      { label: "Risk flags", value: "7", detail: "2 require decision", tone: "warn" },
      { label: "Revenue today", value: "$18.4k", detail: "Across all tenants", tone: "good" },
    ],
    work: [
      { title: "Review tenant configuration drift", meta: "Sites and feature flags", status: "Due today" },
      { title: "Audit admin access changes", meta: "Security review", status: "Open" },
      { title: "Confirm payout reconciliation", meta: "Finance", status: "Ready" },
    ],
    panels: ["Tenant operations", "Security posture", "Revenue controls"],
  },
  admin: {
    title: "Operations center",
    subtitle: "Orders, staffing, payments, quality, and support in one place.",
    primaryAction: "Create admin order",
    metrics: [
      { label: "Open orders", value: "284", detail: "36 need staffing", tone: "warn" },
      { label: "QA queue", value: "18", detail: "6 near SLA", tone: "warn" },
      { label: "Support load", value: "42", detail: "9 escalated", tone: "risk" },
      { label: "Paid today", value: "$9.8k", detail: "Wallet and checkout", tone: "good" },
    ],
    work: [
      { title: "Assign high-priority technical orders", meta: "Writer staffing", status: "Now" },
      { title: "Approve refund exception", meta: "Payments", status: "Review" },
      { title: "Resolve disputed delivery", meta: "Client success", status: "Escalated" },
    ],
    panels: ["Order flow", "Writer workload", "Financial controls"],
  },
  writer: {
    title: "Writer workspace",
    subtitle: "Assignments, deadlines, files, messages, and earnings.",
    primaryAction: "Find available work",
    metrics: [
      { label: "Active assignments", value: "5", detail: "2 due within 24h", tone: "warn" },
      { label: "Available capacity", value: "35%", detail: "Based on workload", tone: "neutral" },
      { label: "Earnings", value: "$742", detail: "This week", tone: "good" },
      { label: "Unread messages", value: "11", detail: "3 from support", tone: "warn" },
    ],
    work: [
      { title: "Literature review draft", meta: "Due 18:00", status: "In progress" },
      { title: "Revision request", meta: "Client notes attached", status: "Action" },
      { title: "Preferred writer invitation", meta: "Expires in 2h", status: "Respond" },
    ],
    panels: ["Deadline calendar", "Assignment files", "Earnings ledger"],
  },
  client: {
    title: "Client portal",
    subtitle: "Create, track, revise, pay, and message around every order.",
    primaryAction: "Start new order",
    metrics: [
      { label: "Active orders", value: "4", detail: "1 awaiting payment", tone: "warn" },
      { label: "Completed", value: "28", detail: "3 eligible for revision", tone: "good" },
      { label: "Wallet", value: "$320", detail: "Available balance", tone: "neutral" },
      { label: "Messages", value: "6", detail: "2 unread", tone: "warn" },
    ],
    work: [
      { title: "Confirm payment for order #1842", meta: "Checkout pending", status: "Pay" },
      { title: "Review completed essay", meta: "Free revision window active", status: "Review" },
      { title: "Upload style references", meta: "Order draft", status: "Draft" },
    ],
    panels: ["Order creation", "Revision tracking", "Wallet activity"],
  },
  editor: {
    title: "Editor desk",
    subtitle: "QA workload, delivery readiness, and revision quality.",
    primaryAction: "Open QA queue",
    metrics: [
      { label: "QA items", value: "16", detail: "4 high priority", tone: "warn" },
      { label: "Avg review time", value: "42m", detail: "Down 8%", tone: "good" },
      { label: "Returned drafts", value: "5", detail: "Need writer follow-up", tone: "warn" },
      { label: "Ready delivery", value: "12", detail: "Awaiting approval", tone: "neutral" },
    ],
    work: [
      { title: "Check plagiarism report", meta: "Order #1902", status: "QA" },
      { title: "Approve client delivery", meta: "Order #1899", status: "Ready" },
      { title: "Send writer correction notes", meta: "Order #1887", status: "Action" },
    ],
    panels: ["QA queue", "Workload analytics", "Revision quality"],
  },
  support: {
    title: "Support cockpit",
    subtitle: "Tickets, escalations, client rescue, and operations triage.",
    primaryAction: "Open ticket queue",
    metrics: [
      { label: "Open tickets", value: "38", detail: "7 nearing SLA", tone: "warn" },
      { label: "Escalations", value: "9", detail: "2 payment-related", tone: "risk" },
      { label: "Avg first reply", value: "6m", detail: "Target under 10m", tone: "good" },
      { label: "Saved replies", value: "54", detail: "12 recently used", tone: "neutral" },
    ],
    work: [
      { title: "Payment confirmation issue", meta: "Ticket #8221", status: "Escalated" },
      { title: "Writer missed deadline", meta: "Order #1875", status: "Triage" },
      { title: "Client asks for revision window", meta: "Ticket #8217", status: "Reply" },
    ],
    panels: ["Ticket queue", "Escalation board", "Communication history"],
  },
};
