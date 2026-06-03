/**
 * useMeta — lightweight page meta + Schema.org injection.
 *
 * Sets document.title, <meta> description, Open Graph tags, and
 * a JSON-LD <script> block without requiring an additional package.
 * Called once per page, re-called on navigation via onMounted / watch.
 */
import { onBeforeUnmount } from "vue";

export interface MetaOptions {
  title: string;
  description?: string;
  image?: string;
  url?: string;
  type?: "website" | "article";
  // Pass multiple schemas — injected as @graph array
  schemas?: Record<string, unknown>[];
  siteName?: string;
  publishedAt?: string;
  author?: string;
  schema?: Record<string, unknown> | null;
}

const DEFAULT_SITE_NAME = "WritingSystem";

export function useMeta(options: MetaOptions) {
  apply(options);

  onBeforeUnmount(() => {
    // Remove JSON-LD on page leave to avoid stale structured data
    removeJsonLd();
  });
}

function apply(opts: MetaOptions) {
  const siteName = opts.siteName ?? DEFAULT_SITE_NAME;
  const fullTitle = `${opts.title} — ${siteName}`;
  const url = opts.url ?? (typeof window !== "undefined" ? window.location.href : "");

  // document.title
  document.title = fullTitle;

  // Standard meta
  setMeta("name", "description", opts.description ?? "");

  // Open Graph
  setMeta("property", "og:title", fullTitle);
  setMeta("property", "og:description", opts.description ?? "");
  setMeta("property", "og:type", opts.type ?? "website");
  setMeta("property", "og:url", url);
  setMeta("property", "og:site_name", siteName);
  if (opts.image) setMeta("property", "og:image", opts.image);

  // Article-specific
  if (opts.type === "article") {
    if (opts.publishedAt) setMeta("property", "article:published_time", opts.publishedAt);
    if (opts.author) setMeta("property", "article:author", opts.author);
  }

  // Twitter card
  setMeta("name", "twitter:card", opts.image ? "summary_large_image" : "summary");
  setMeta("name", "twitter:title", fullTitle);
  setMeta("name", "twitter:description", opts.description ?? "");
  if (opts.image) setMeta("name", "twitter:image", opts.image);

  // Canonical
  setLink("canonical", url);

  // JSON-LD — supports single schema or multi-schema @graph
  const schemas = opts.schemas ?? (opts.schema ? [opts.schema] : []);
  if (schemas.length === 1) {
    injectJsonLd(schemas[0]);
  } else if (schemas.length > 1) {
    injectJsonLd({ "@context": "https://schema.org", "@graph": schemas.map(s => ({ ...s, "@context": undefined })) });
  } else {
    removeJsonLd();
  }
}

function setMeta(attr: "name" | "property", key: string, content: string) {
  let el = document.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`);
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attr, key);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function setLink(rel: string, href: string) {
  let el = document.querySelector<HTMLLinkElement>(`link[rel="${rel}"]`);
  if (!el) {
    el = document.createElement("link");
    el.setAttribute("rel", rel);
    document.head.appendChild(el);
  }
  el.setAttribute("href", href);
}

function injectJsonLd(schema: Record<string, unknown>) {
  removeJsonLd();
  const script = document.createElement("script");
  script.type = "application/ld+json";
  script.id = "page-schema-org";
  script.textContent = JSON.stringify(schema);
  document.head.appendChild(script);
}

function removeJsonLd() {
  document.getElementById("page-schema-org")?.remove();
}

// ── Schema.org builders ────────────────────────────────────────────────────

export function articleSchema(opts: {
  title: string;
  description?: string;
  url: string;
  image?: string;
  publishedAt?: string;
  updatedAt?: string;
  authorName?: string;
  authorUrl?: string;
  siteName?: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: opts.title,
    description: opts.description,
    url: opts.url,
    image: opts.image,
    datePublished: opts.publishedAt,
    dateModified: opts.updatedAt ?? opts.publishedAt,
    author: opts.authorName
      ? { "@type": "Person", name: opts.authorName, url: opts.authorUrl }
      : undefined,
    publisher: {
      "@type": "Organization",
      name: opts.siteName ?? DEFAULT_SITE_NAME,
    },
  };
}

export function serviceSchema(opts: {
  name: string;
  description?: string;
  url: string;
  pricingFrom?: string;
  currency?: string;
  providerName?: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "Service",
    name: opts.name,
    description: opts.description,
    url: opts.url,
    provider: {
      "@type": "Organization",
      name: opts.providerName ?? DEFAULT_SITE_NAME,
    },
    offers: opts.pricingFrom
      ? {
          "@type": "Offer",
          price: opts.pricingFrom,
          priceCurrency: opts.currency ?? "USD",
        }
      : undefined,
  };
}

export function webPageSchema(opts: {
  title: string;
  description?: string;
  url: string;
  siteName?: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: opts.title,
    description: opts.description,
    url: opts.url,
    isPartOf: { "@type": "WebSite", name: opts.siteName ?? DEFAULT_SITE_NAME },
  };
}

// ── Item 4: FAQPage ────────────────────────────────────────────────────────

export function faqPageSchema(items: { question: string; answer: string }[]) {
  if (!items.length) return null;
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map(({ question, answer }) => ({
      "@type": "Question",
      name: question,
      acceptedAnswer: { "@type": "Answer", text: answer },
    })),
  };
}

/** Extract FAQ items from a Wagtail StreamField body block array. */
export function extractFaqItems(
  blocks: Array<{ type: string; value: unknown }>,
): { question: string; answer: string }[] {
  const items: { question: string; answer: string }[] = [];
  for (const block of blocks ?? []) {
    if (block.type === "faq") {
      const val = block.value as { items?: Array<{ question?: string; answer?: string }> };
      for (const item of val?.items ?? []) {
        if (item.question && item.answer) {
          // Strip HTML tags from answer for plain-text Schema.org
          items.push({ question: item.question, answer: item.answer.replace(/<[^>]*>/g, "") });
        }
      }
    }
  }
  return items;
}

// ── Item 5: HowTo ──────────────────────────────────────────────────────────

export function howToSchema(opts: {
  name: string;
  description?: string;
  steps: { title: string; text: string }[];
}) {
  if (!opts.steps.length) return null;
  return {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name: opts.name,
    description: opts.description,
    step: opts.steps.map((s, i) => ({
      "@type": "HowToStep",
      position: i + 1,
      name: s.title,
      text: s.text,
    })),
  };
}

/** Extract HowTo steps from a how_it_works block. */
export function extractHowToSteps(
  blocks: Array<{ type: string; value: unknown }>,
): { title: string; text: string }[] {
  for (const block of blocks ?? []) {
    if (block.type === "how_it_works") {
      const val = block.value as { steps?: Array<{ title?: string; body?: string }> };
      if (val?.steps?.length) {
        return val.steps
          .filter(s => s.title)
          .map(s => ({ title: s.title!, text: (s.body ?? "").replace(/<[^>]*>/g, "") }));
      }
    }
  }
  return [];
}

// ── Item 6: BreadcrumbList ─────────────────────────────────────────────────

export function breadcrumbSchema(items: { name: string; url: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

// ── Item 8: Rich Person (author expertise signals) ─────────────────────────

export function personSchema(opts: {
  name: string;
  url?: string;
  bio?: string;
  image?: string;
  jobTitle?: string;
  credentials?: string;
  degrees?: Array<{ degree?: string; institution?: string } | string>;
  areasOfExpertise?: string;
  yearsExperience?: number;
  orcidId?: string;
  googleScholarUrl?: string;
  linkedinUrl?: string;
  personalWebsite?: string;
}) {
  const sameAs = [
    opts.orcidId ? `https://orcid.org/${opts.orcidId}` : null,
    opts.googleScholarUrl,
    opts.linkedinUrl,
    opts.personalWebsite,
  ].filter(Boolean);

  const alumniOf = (opts.degrees ?? []).map(d => {
    if (typeof d === "string") return { "@type": "EducationalOrganization", name: d };
    return {
      "@type": "OrganizationRole",
      alumniOf: { "@type": "EducationalOrganization", name: d.institution ?? "" },
      roleName: d.degree ?? "",
    };
  }).filter(d => (typeof d === "object" && (d as Record<string, unknown>).alumniOf));

  const knowsAbout = opts.areasOfExpertise
    ? opts.areasOfExpertise.split(/[,;]/).map(a => a.trim()).filter(Boolean)
    : [];

  return {
    "@context": "https://schema.org",
    "@type": "Person",
    name: opts.name,
    url: opts.url,
    description: opts.bio,
    image: opts.image,
    jobTitle: opts.jobTitle,
    hasCredential: opts.credentials
      ? { "@type": "EducationalOccupationalCredential", name: opts.credentials }
      : undefined,
    alumniOf: alumniOf.length ? alumniOf : undefined,
    knowsAbout: knowsAbout.length ? knowsAbout : undefined,
    sameAs: sameAs.length ? sameAs : undefined,
  };
}
