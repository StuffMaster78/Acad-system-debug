/**
 * Sanitizes staff/admin-authored HTML before it is bound via v-html.
 *
 * Prevents stored XSS: a compromised admin/support account cannot inject
 * executable script payloads into other authenticated users' browsers by
 * writing malicious content in broadcasts, announcements, support replies,
 * or changelog entries.
 *
 * Uses DOMPurify with a restrictive allowlist: only safe formatting tags
 * and a narrow set of attributes. Script, iframe, object, and event
 * handler attributes are always stripped.
 */

import DOMPurify, { type Config } from "dompurify";

const SANITIZE_CONFIG: Config = {
  ALLOWED_TAGS: [
    "p", "br", "b", "strong", "i", "em", "u", "s", "strike",
    "ul", "ol", "li",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "pre", "code",
    "a", "span", "div",
    "table", "thead", "tbody", "tr", "th", "td",
    "hr",
  ],
  ALLOWED_ATTR: ["href", "target", "rel", "class", "style"],
  // Force all links to be safe
  FORCE_BODY: true,
};

// Ensure links from staff content open in a new tab with noopener
DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "A") {
    node.setAttribute("target", "_blank");
    node.setAttribute("rel", "noopener noreferrer");
  }
});

export function sanitize(html: string | null | undefined): string {
  if (!html) return "";
  return DOMPurify.sanitize(html, SANITIZE_CONFIG) as unknown as string;
}
