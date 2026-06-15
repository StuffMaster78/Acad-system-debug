# Privacy Consent Implementation

The platform uses a host-aware cookie consent system for GDPR/PECR-style consent flows across public marketing sites and the main portal.

## Consent Categories

- `necessary`: Always enabled. Required for login, security, checkout, order flow, and storing the consent choice.
- `preferences`: Optional. Used for saved form state, bookmarks, reactions, and display preferences.
- `analytics`: Optional. Required before GA4 or page/funnel analytics scripts load.
- `marketing`: Optional. Required before campaign attribution, advertising pixels, or UTM persistence.

Optional categories must default to off. Analytics and marketing scripts must not load until the relevant category has been accepted.

## Backend Endpoints

All endpoints are under `/api/v1/privacy/`.

- `GET cookie-config/`: returns host-aware consent category metadata and integrations.
- `GET cookie-consent/current/`: returns the current browser/user consent record when known.
- `POST cookie-consent/`: records a new historical consent choice.
- `POST cookie-consent/revoke/`: revokes active consent records and creates a new optional-cookies-off record.

Consent records are stored in `privacy.CookieConsentRecord` with the resolved `website`, optional authenticated `user`, anonymous consent ID, policy/consent versions, category booleans, source, host, and hashed IP/user-agent audit fields.

## Frontend Wiring

Public Nuxt sites use:

- `composables/useCookieConsent.ts`
- `components/privacy/CookieConsentBanner.vue`

The main Vue portal uses:

- `frontend/src/composables/useCookieConsent.ts`
- `frontend/src/components/privacy/CookieConsentBanner.vue`

GA4 loading is consent-aware:

- GradeCrest no longer injects GA4 directly in the server-rendered head.
- NurseMyGrade, ResearchPaperMate, and EssayManiacs no longer inject GA4 eagerly in `app.vue`.
- The main portal `useAnalytics` wrapper ignores events unless analytics consent is granted.
- UTM capture in the main portal runs only after marketing consent is granted.

## Operational Notes

Consent is domain-scoped. Separate root domains should collect consent separately. Once a user is authenticated, backend records can associate future consent choices with the user account while preserving anonymous audit history.
