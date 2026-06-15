import { computed, ref } from "vue";
import { api, apiPath } from "@/api/client";

type ConsentSource = "banner" | "settings" | "footer" | "api";

interface ConsentPreferences {
  necessary: boolean;
  preferences: boolean;
  analytics: boolean;
  marketing: boolean;
}

interface CookieConsentCurrent {
  has_consent: boolean;
  anonymous_id: string | null;
  consent: (ConsentPreferences & {
    id: number;
    consent_version: string;
    policy_version: string;
    source: ConsentSource;
    revoked_at: string | null;
  }) | null;
}

interface CookieConsentRecord {
  anonymous_id: string;
  consent: CookieConsentCurrent["consent"];
}

const CONSENT_ID_KEY = "writing_system.cookie_consent_id";
const DEFAULT_CONSENT: ConsentPreferences = {
  necessary: true,
  preferences: false,
  analytics: false,
  marketing: false,
};

const preferences = ref<ConsentPreferences>({ ...DEFAULT_CONSENT });
const loaded = ref(false);
const bannerOpen = ref(false);
const settingsOpen = ref(false);
const anonymousId = ref<string | null>(localStorage.getItem(CONSENT_ID_KEY));

function rememberConsentId(value: string | null) {
  anonymousId.value = value;
  if (value) localStorage.setItem(CONSENT_ID_KEY, value);
}

export function hasAnalyticsConsent(): boolean {
  return preferences.value.analytics;
}

export function hasMarketingConsent(): boolean {
  return preferences.value.marketing;
}

export function useCookieConsent() {
  const analyticsAllowed = computed(() => preferences.value.analytics);
  const marketingAllowed = computed(() => preferences.value.marketing);

  async function init() {
    if (loaded.value) return;
    try {
      const { data } = await api.get<CookieConsentCurrent>(
        apiPath("/privacy/cookie-consent/current/"),
        {
          headers: anonymousId.value ? { "X-Consent-ID": anonymousId.value } : undefined,
        },
      );
      if (data.has_consent && data.consent) {
        preferences.value = {
          necessary: true,
          preferences: data.consent.preferences,
          analytics: data.consent.analytics,
          marketing: data.consent.marketing,
        };
        rememberConsentId(data.anonymous_id);
        bannerOpen.value = false;
      } else {
        bannerOpen.value = true;
      }
    } catch {
      bannerOpen.value = !anonymousId.value;
    } finally {
      loaded.value = true;
    }
  }

  async function save(next: Partial<ConsentPreferences>, source: ConsentSource = "settings") {
    preferences.value = {
      necessary: true,
      preferences: Boolean(next.preferences),
      analytics: Boolean(next.analytics),
      marketing: Boolean(next.marketing),
    };
    bannerOpen.value = false;
    settingsOpen.value = false;
    const { data } = await api.post<CookieConsentRecord>(
      apiPath("/privacy/cookie-consent/"),
      {
        anonymous_id: anonymousId.value || undefined,
        preferences: Boolean(next.preferences),
        analytics: Boolean(next.analytics),
        marketing: Boolean(next.marketing),
        source,
      },
    );
    rememberConsentId(data.anonymous_id);
    preferences.value = {
      necessary: true,
      preferences: Boolean(data.consent?.preferences),
      analytics: Boolean(data.consent?.analytics),
      marketing: Boolean(data.consent?.marketing),
    };
  }

  return {
    preferences,
    loaded,
    bannerOpen,
    settingsOpen,
    analyticsAllowed,
    marketingAllowed,
    init,
    save,
    acceptAll: () => save({ preferences: true, analytics: true, marketing: true }, "banner"),
    rejectOptional: () => save({ preferences: false, analytics: false, marketing: false }, "banner"),
    openSettings: () => {
      settingsOpen.value = true;
      bannerOpen.value = true;
    },
  };
}
