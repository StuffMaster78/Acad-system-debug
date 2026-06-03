import { ref, computed } from "vue";
import { api, apiPath } from "@/api/client";
import { getStoredUtm } from "@/composables/useUtm";

export interface PersonalizationRule {
  id: number;
  persona: string;
  persona_display: string;
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  hero_headline: string;
  hero_subheadline: string;
  cta_label: string;
  cta_url: string;
  trust_badge: string;
  is_active: boolean;
  priority: number;
}

const _rules = ref<PersonalizationRule[]>([]);
const _loaded = ref(false);

async function ensureLoaded() {
  if (_loaded.value) return;
  try {
    const { data } = await api.get<PersonalizationRule[]>(
      apiPath("/cms/intelligence/personalization/active/"),
    );
    _rules.value = Array.isArray(data) ? data : [];
  } catch {
    _rules.value = [];
  }
  _loaded.value = true;
}

function _utmToPersona(utm: ReturnType<typeof getStoredUtm>): string {
  if (!utm) return "direct";
  const src  = (utm.utm_source  ?? "").toLowerCase();
  const med  = (utm.utm_medium  ?? "").toLowerCase();
  if (med === "email" || src === "email")          return "email";
  if (med === "affiliate" || src === "affiliate")   return "affiliate";
  if (med === "cpc" || med === "ppc" || med === "paid") return "paid_search";
  if (med === "social" || ["facebook","instagram","tiktok","twitter","linkedin"].includes(src))
    return "social";
  if (med === "referral")  return "referral";
  if (med === "organic" || src === "google" || src === "bing" || src === "duckduckgo")
    return "organic_search";
  return "direct";
}

function _ruleMatches(rule: PersonalizationRule, utm: ReturnType<typeof getStoredUtm>): boolean {
  if (!rule.is_active) return false;
  if (rule.persona !== _utmToPersona(utm)) return false;
  if (rule.utm_source   && rule.utm_source   !== (utm?.utm_source  ?? "")) return false;
  if (rule.utm_medium   && rule.utm_medium   !== (utm?.utm_medium  ?? "")) return false;
  if (rule.utm_campaign && rule.utm_campaign !== (utm?.utm_campaign ?? "")) return false;
  return true;
}

export function usePersonalization() {
  const utm = getStoredUtm();

  const activeRule = computed<PersonalizationRule | null>(() => {
    const rules = [..._rules.value].sort((a, b) => b.priority - a.priority);
    return rules.find(r => _ruleMatches(r, utm)) ?? null;
  });

  const headline     = computed(() => activeRule.value?.hero_headline    ?? "");
  const subheadline  = computed(() => activeRule.value?.hero_subheadline ?? "");
  const ctaLabel     = computed(() => activeRule.value?.cta_label        ?? "");
  const ctaUrl       = computed(() => activeRule.value?.cta_url          ?? "");
  const trustBadge   = computed(() => activeRule.value?.trust_badge      ?? "");

  return { activeRule, headline, subheadline, ctaLabel, ctaUrl, trustBadge, ensureLoaded };
}
