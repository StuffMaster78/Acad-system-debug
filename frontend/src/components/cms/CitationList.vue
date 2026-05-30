<template>
  <section class="mt-10 border-t border-slate-200 pt-8">
    <h2 class="mb-4 text-sm font-bold uppercase tracking-wider text-graphite">
      {{ modeLabel }}
    </h2>

    <!-- Sources list (simple numbered) -->
    <ol v-if="mode === 'sources_list'" class="space-y-2">
      <li
        v-for="(citation, i) in citations"
        :key="citation.id"
        class="flex gap-3 text-sm text-graphite"
      >
        <span class="shrink-0 font-semibold text-ink w-6">{{ i + 1 }}.</span>
        <span>
          {{ citation.reference.title }}.
          <a
            v-if="citation.reference.doi"
            :href="`https://doi.org/${citation.reference.doi}`"
            target="_blank"
            rel="noreferrer"
            class="text-berry hover:underline"
          >https://doi.org/{{ citation.reference.doi }}</a>
          <a
            v-else-if="citation.reference.url"
            :href="citation.reference.url"
            target="_blank"
            rel="noreferrer"
            class="text-berry hover:underline"
          >{{ citation.reference.url }}</a>
        </span>
      </li>
    </ol>

    <!-- Formal citations -->
    <ol v-else class="space-y-3">
      <li
        v-for="(citation, i) in citations"
        :key="citation.id"
        class="flex gap-3 text-sm text-graphite"
      >
        <span class="shrink-0 font-semibold text-ink w-6">{{ i + 1 }}.</span>
        <span v-html="formatCitation(citation.reference)" />
      </li>
    </ol>
  </section>
</template>

<script setup lang="ts">
import type { Citation, Reference } from "@/api/cms";

const props = defineProps<{
  citations: Citation[];
  mode: string;
}>();

const LABELS: Record<string, string> = {
  sources_list:   "Sources",
  formal_apa7:    "References (APA 7th Edition)",
  formal_mla9:    "Works Cited (MLA 9th Edition)",
  formal_chicago: "Bibliography (Chicago Style)",
};

const modeLabel = LABELS[props.mode] ?? "References";

// ── Citation formatters ───────────────────────────────────────────────────

function authors(ref: Reference): string {
  if (!ref.authors?.length) return "";
  return ref.authors.map((a) => `${a.family}, ${a.given ?? ""}`.trim()).join(", & ");
}

function authorsReversed(ref: Reference, max = 20): string {
  if (!ref.authors?.length) return "";
  const list = ref.authors.slice(0, max).map(
    (a, i) => i === 0 ? `${a.family}, ${a.given ?? ""}`.trim() : `${a.given ?? ""} ${a.family}`.trim(),
  );
  if (ref.authors.length > max) list.push("et al.");
  return list.join(", ");
}

function doiLink(ref: Reference): string {
  if (!ref.doi) return ref.url ? ` ${ref.url}` : "";
  return ` https://doi.org/${ref.doi}`;
}

function apa7(ref: Reference): string {
  const au   = authors(ref);
  const year  = ref.publication_year ? `(${ref.publication_year}).` : "";
  const title = `${ref.title}.`;
  if (ref.reference_type === "journal_article") {
    const journal = ref.journal_name ? `<em>${ref.journal_name}</em>,` : "";
    const vol     = ref.journal_volume ? ` <em>${ref.journal_volume}</em>` : "";
    const iss     = ref.journal_issue ? `(${ref.journal_issue})` : "";
    const pages   = ref.pages ? `, ${ref.pages}.` : ".";
    return `${au} ${year} ${title} ${journal}${vol}${iss}${pages}${doiLink(ref)}`;
  }
  if (ref.reference_type === "book") {
    const pub = [ref.publisher_location, ref.publisher].filter(Boolean).join(": ");
    return `${au} ${year} ${title} ${pub}.`;
  }
  return `${au} ${year} ${title}${doiLink(ref)}`;
}

function mla9(ref: Reference): string {
  if (!ref.authors?.length) return `"${ref.title}." ${doiLink(ref).trim()}`;
  const au    = authorsReversed(ref);
  const title = `"${ref.title}."`;
  if (ref.reference_type === "journal_article") {
    const journal = ref.journal_name ? `<em>${ref.journal_name}</em>,` : "";
    const vol     = ref.journal_volume ? ` vol. ${ref.journal_volume},` : "";
    const iss     = ref.journal_issue ? ` no. ${ref.journal_issue},` : "";
    const year    = ref.publication_year ? ` ${ref.publication_year},` : "";
    const pages   = ref.pages ? ` pp. ${ref.pages}.` : ".";
    return `${au}. ${title} ${journal}${vol}${iss}${year}${pages}${doiLink(ref)}`;
  }
  const pub  = ref.publisher ? ` ${ref.publisher},` : "";
  const year = ref.publication_year ? ` ${ref.publication_year}.` : ".";
  return `${au}. <em>${ref.title}.</em>${pub}${year}`;
}

function chicago(ref: Reference): string {
  if (!ref.authors?.length) return `"${ref.title}." ${doiLink(ref).trim()}`;
  const au    = authorsReversed(ref);
  if (ref.reference_type === "journal_article") {
    const journal = ref.journal_name ? `"${ref.title}." <em>${ref.journal_name}</em>` : `"${ref.title}."`;
    const vol     = ref.journal_volume ? ` ${ref.journal_volume}` : "";
    const iss     = ref.journal_issue ? `, no. ${ref.journal_issue}` : "";
    const year    = ref.publication_year ? ` (${ref.publication_year})` : "";
    const pages   = ref.pages ? `: ${ref.pages}.` : ".";
    return `${au}. ${journal}${vol}${iss}${year}${pages}${doiLink(ref)}`;
  }
  const pub  = [ref.publisher_location, ref.publisher].filter(Boolean).join(": ");
  const year = ref.publication_year ? `, ${ref.publication_year}.` : ".";
  return `${au}. <em>${ref.title}.</em> ${pub}${year}`;
}

function formatCitation(ref: Reference): string {
  switch (props.mode) {
    case "formal_apa7":    return apa7(ref);
    case "formal_mla9":    return mla9(ref);
    case "formal_chicago": return chicago(ref);
    default:               return ref.title;
  }
}
</script>
