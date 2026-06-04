import { ref } from "vue";
import { pricingApi } from "@/api/pricing";
import type {
  PaperQuoteStartResponse,
  PaperQuoteUpdateResponse,
  PriceLine,
  Suggestion,
} from "@/types/orders";

type QuoteType = "paper" | "design" | "diagram";

export function useQuoteSession(
  type: QuoteType,
  getPayload: () => Record<string, unknown>,
) {
  const sessionId     = ref<string | null>(null);
  const estimate      = ref<PaperQuoteStartResponse | null>(null);
  const breakdown     = ref<PaperQuoteUpdateResponse | null>(null);
  const quoteLoading  = ref(false);
  const showBreakdown = ref(false);
  const quoteError    = ref("");
  const suggestions   = ref<Suggestion[]>([]);

  const currency = () =>
    breakdown.value?.currency ?? estimate.value?.currency ?? "USD";

  const estimateRange = (): string | null => {
    if (!estimate.value) return null;
    const lo = Number(estimate.value.estimated_min_price ?? 0);
    const hi = Number(estimate.value.estimated_max_price ?? 0);
    if (!lo && !hi) return null;
    return lo === hi
      ? formatMoney(lo, currency())
      : `${formatMoney(lo, currency())} – ${formatMoney(hi, currency())}`;
  };

  const finalPrice = (): string | null =>
    breakdown.value?.calculated_price != null
      ? formatMoney(Number(breakdown.value.calculated_price), currency())
      : null;

  const visibleLines = (): PriceLine[] =>
    (breakdown.value?.lines ?? []).filter(
      (l) => l.line_type !== "total" && Number(l.amount) !== 0,
    );

  const totalLine = (): PriceLine | null =>
    breakdown.value?.lines.find((l) => l.line_type === "total") ?? null;

  let debounceTimer: ReturnType<typeof setTimeout> | null = null;

  function fetchEstimate() {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      quoteLoading.value = true;
      quoteError.value = "";
      showBreakdown.value = false;
      breakdown.value = null;
      try {
        const { data } = await pricingApi.startQuote(type, getPayload());
        estimate.value = data;
        sessionId.value = data.session_id;
        suggestions.value = data.suggestions ?? [];
      } catch {
        quoteError.value = "Could not fetch price. Please try again.";
      } finally {
        quoteLoading.value = false;
      }
    }, 350);
  }

  async function getExactPrice() {
    if (!sessionId.value) {
      fetchEstimate();
      return;
    }
    quoteLoading.value = true;
    quoteError.value = "";
    try {
      const { data } = await pricingApi.updateQuote(type, sessionId.value, getPayload());
      breakdown.value = data;
      showBreakdown.value = true;
      suggestions.value = data.suggestions ?? [];
    } catch {
      quoteError.value = "Could not calculate price. Please try again.";
    } finally {
      quoteLoading.value = false;
    }
  }

  return {
    sessionId,
    estimate,
    breakdown,
    quoteLoading,
    showBreakdown,
    quoteError,
    suggestions,
    currency,
    estimateRange,
    finalPrice,
    visibleLines,
    totalLine,
    fetchEstimate,
    getExactPrice,
  };
}

// ── Helpers ──────────────────────────────────────────────────────────────────

const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: "$", GBP: "£", EUR: "€", KES: "KSh", AUD: "A$", CAD: "C$",
};

export function formatMoney(amount: number, currency: string): string {
  const symbol = CURRENCY_SYMBOLS[currency] ?? currency + " ";
  return `${symbol}${amount.toFixed(2)}`;
}

export function lineAmountDisplay(amount: string | number, lineType: string): string {
  const n = Number(amount);
  if (lineType === "base") return formatMoney(n, "");
  return n >= 0 ? `+${formatMoney(n, "")}` : `–${formatMoney(Math.abs(n), "")}`;
}
