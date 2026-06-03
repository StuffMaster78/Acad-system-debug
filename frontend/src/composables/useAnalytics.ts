/**
 * useAnalytics — typed wrapper around Google Analytics 4 (gtag.js).
 *
 * Usage:
 *   const { track } = useAnalytics()
 *   track('purchase', { value: 49.00, currency: 'USD', transaction_id: 'ORD-001' })
 *
 * Script injection happens once at app boot via injectGa4Script().
 * All calls are no-ops when GA4 is not configured or the user is in preview mode.
 */

// ── Types ─────────────────────────────────────────────────────────────────────

type Gtag = (command: string, ...args: unknown[]) => void;

declare global {
  interface Window {
    gtag?: Gtag;
    dataLayer?: unknown[];
  }
}

// GA4 recommended event parameter shapes
export interface PurchaseParams {
  transaction_id: string;
  value: number;
  currency?: string;
  coupon?: string;
  items?: Array<{ item_id?: string; item_name: string; price?: number; quantity?: number }>;
}

export interface SignUpParams {
  method?: string;
}

export interface GenerateLeadParams {
  value?: number;
  currency?: string;
}

// ── Script injection ──────────────────────────────────────────────────────────

let _injected = false;

export function injectGa4Script(measurementId: string): void {
  if (_injected || !measurementId || typeof document === "undefined") return;
  _injected = true;

  // Initialise dataLayer and gtag stub before the script loads
  window.dataLayer = window.dataLayer ?? [];
  window.gtag = function (...args: unknown[]) {
    window.dataLayer!.push(args);
  };
  window.gtag("js", new Date());
  window.gtag("config", measurementId, {
    // Defer page views — we fire them manually on each route change
    // so SPA navigation is tracked correctly.
    send_page_view: false,
  });

  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  document.head.appendChild(script);
}

// ── Composable ────────────────────────────────────────────────────────────────

export function useAnalytics() {
  function _gtag(): Gtag | null {
    if (typeof window !== "undefined" && typeof window.gtag === "function") {
      return window.gtag;
    }
    return null;
  }

  /** Track a page view — call on every route change. */
  function pageView(path: string, title?: string): void {
    _gtag()?.("event", "page_view", {
      page_path:  path,
      page_title: title,
    });
  }

  /** Generic event tracker — thin wrapper around gtag('event', ...). */
  function track(eventName: string, params?: Record<string, unknown>): void {
    _gtag()?.("event", eventName, params);
  }

  /** User completed registration. */
  function signUp(method = "email"): void {
    track("sign_up", { method });
  }

  /** User placed an order. */
  function purchase(params: PurchaseParams): void {
    track("purchase", {
      currency:       params.currency ?? "USD",
      value:          params.value,
      transaction_id: params.transaction_id,
      coupon:         params.coupon,
      items:          params.items,
    });
  }

  /** User triggered a price quote (begin of checkout funnel). */
  function beginCheckout(value: number, currency = "USD"): void {
    track("begin_checkout", { value, currency });
  }

  /** Writer submitted an application. */
  function writerApplicationSubmitted(): void {
    track("generate_lead", { event_category: "writer_application" });
  }

  /** Writer completed a vetting quiz. */
  function quizCompleted(quizType: string, passed: boolean): void {
    track("quiz_completed", { quiz_type: quizType, passed });
  }

  return {
    pageView,
    track,
    signUp,
    purchase,
    beginCheckout,
    writerApplicationSubmitted,
    quizCompleted,
  };
}
