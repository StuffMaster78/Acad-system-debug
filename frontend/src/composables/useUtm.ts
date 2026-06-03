/**
 * useUtm — capture UTM parameters and referrer from the landing URL
 * and persist them in localStorage with a 30-day TTL.
 *
 * Call captureUtmFromUrl() on every page load (done in App.vue).
 * Call getStoredUtm() to retrieve the data when sending to the API
 * (e.g. at registration time).
 */

const STORAGE_KEY = "utm_attribution";
const TTL_MS      = 30 * 24 * 60 * 60 * 1000; // 30 days

export interface UtmAttribution {
  utm_source:   string;
  utm_medium:   string;
  utm_campaign: string;
  utm_content:  string;
  utm_term:     string;
  referrer:     string;
  landing_page: string;
  captured_at:  number; // epoch ms
}

/** Read UTM params from the current URL and save to localStorage.
 *  Only overwrites if this visit has at least one UTM param present
 *  (preserves the first-touch attribution across navigations). */
export function captureUtmFromUrl(): void {
  if (typeof window === "undefined") return;

  const params  = new URLSearchParams(window.location.search);
  const source   = params.get("utm_source")   ?? "";
  const medium   = params.get("utm_medium")   ?? "";
  const campaign = params.get("utm_campaign") ?? "";
  const content  = params.get("utm_content")  ?? "";
  const term     = params.get("utm_term")     ?? "";

  // Only write if at least one UTM param is present — preserves first-touch
  if (!source && !medium && !campaign) return;

  const data: UtmAttribution = {
    utm_source:   source,
    utm_medium:   medium,
    utm_campaign: campaign,
    utm_content:  content,
    utm_term:     term,
    referrer:     document.referrer ?? "",
    landing_page: window.location.href,
    captured_at:  Date.now(),
  };

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch { /* storage full or blocked */ }
}

/** Retrieve the stored UTM attribution (if within TTL). */
export function getStoredUtm(): Partial<UtmAttribution> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const data: UtmAttribution = JSON.parse(raw);
    if (Date.now() - data.captured_at > TTL_MS) {
      localStorage.removeItem(STORAGE_KEY);
      return {};
    }
    return data;
  } catch {
    return {};
  }
}

/** Clear stored attribution (e.g. after successful registration). */
export function clearStoredUtm(): void {
  if (typeof window === "undefined") return;
  try { localStorage.removeItem(STORAGE_KEY); } catch { /* ignore */ }
}

export function useUtm() {
  return { captureUtmFromUrl, getStoredUtm, clearStoredUtm };
}
