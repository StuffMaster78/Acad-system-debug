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

  // JSON-LD
  if (opts.schema) {
    injectJsonLd(opts.schema);
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
