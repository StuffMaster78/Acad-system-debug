<template>
  <!-- Trigger button -->
  <button
    class="focus-ring inline-flex items-center gap-2 rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-xs font-semibold text-blue-700 hover:bg-blue-100"
    @click="open = true"
  >
    <BookOpen class="size-3.5" />
    Wagtail publishing guide
  </button>

  <!-- Modal -->
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 px-4 py-10"
      @click.self="open = false"
    >
      <div class="w-full max-w-3xl rounded-2xl border border-slate-200 bg-white shadow-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-5">
          <div class="flex items-center gap-3">
            <div class="flex size-9 items-center justify-center rounded-lg bg-blue-600 text-white text-sm font-extrabold">W</div>
            <div>
              <h2 class="font-bold text-ink">How to publish content in Wagtail</h2>
              <p class="text-xs text-graphite">Step-by-step guide for blog posts, service pages, and authors.</p>
            </div>
          </div>
          <button class="rounded p-1 text-graphite hover:text-ink" @click="open = false">
            <X class="size-5" />
          </button>
        </div>

        <!-- Content -->
        <div class="divide-y divide-slate-100 overflow-y-auto" style="max-height: 70vh">

          <!-- Quick access -->
          <div class="bg-blue-50 px-6 py-4">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-blue-700">Quick access</p>
            <div class="flex flex-wrap gap-2">
              <a
                href="/cms/"
                target="_blank"
                class="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-xs font-bold text-white hover:bg-blue-700"
              >
                <ExternalLink class="size-3.5" /> Open Wagtail Admin
              </a>
              <a
                href="/cms/pages/"
                target="_blank"
                class="inline-flex items-center gap-1.5 rounded-lg border border-blue-200 bg-white px-3 py-2 text-xs font-semibold text-blue-700 hover:bg-blue-50"
              >
                <FileText class="size-3.5" /> Page tree
              </a>
              <a
                href="/cms/snippets/"
                target="_blank"
                class="inline-flex items-center gap-1.5 rounded-lg border border-blue-200 bg-white px-3 py-2 text-xs font-semibold text-blue-700 hover:bg-blue-50"
              >
                <Users class="size-3.5" /> Authors & categories
              </a>
            </div>
          </div>

          <!-- Steps -->
          <div class="space-y-0 divide-y divide-slate-100">

            <!-- Step 1 -->
            <div class="px-6 py-5">
              <div class="flex gap-4">
                <StepBadge n="1" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-ink">Set up authors first</h3>
                  <p class="mt-1 text-sm text-graphite leading-6">
                    Every blog post requires an author. Go to
                    <code class="rounded bg-slate-100 px-1 text-xs">Snippets → Authors</code>
                    and create author profiles before writing posts. Fill in name, bio, credentials, ORCID, and profile photo — these appear on published posts and feed the Schema.org Person markup.
                  </p>
                  <a href="/cms/snippets/cms_authors/author/" target="_blank" class="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:underline">
                    Manage authors <ExternalLink class="size-3" />
                  </a>
                </div>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="px-6 py-5">
              <div class="flex gap-4">
                <StepBadge n="2" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-ink">Create categories and tags</h3>
                  <p class="mt-1 text-sm text-graphite leading-6">
                    Go to <code class="rounded bg-slate-100 px-1 text-xs">Snippets → Blog categories</code> to add topic groupings (e.g., "Essay writing", "APA formatting"). Tags are more granular keywords. Both appear as filters on the public blog and improve topic clustering.
                  </p>
                </div>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="px-6 py-5">
              <div class="flex gap-4">
                <StepBadge n="3" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-ink">Find your site's page tree</h3>
                  <p class="mt-1 text-sm text-graphite leading-6">
                    Go to <code class="rounded bg-slate-100 px-1 text-xs">Pages</code> and navigate to your site's home page (TenantHomePage). Under it you'll find:
                  </p>
                  <div class="mt-2 rounded-lg bg-slate-50 p-3 font-mono text-xs text-graphite space-y-0.5">
                    <p>📁 <strong>YourSite Home</strong></p>
                    <p class="ml-4">📁 Blog <span class="font-normal">(BlogIndexPage)</span></p>
                    <p class="ml-8">📄 Blog posts go here</p>
                    <p class="ml-4">📁 Services <span class="font-normal">(ServiceIndexPage)</span></p>
                    <p class="ml-8">📄 Service pages go here</p>
                    <p class="ml-4">📁 Authors <span class="font-normal">(AuthorIndexPage)</span></p>
                    <p class="ml-4">📁 Resources <span class="font-normal">(ResourceIndexPage)</span></p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 4 -->
            <div class="px-6 py-5">
              <div class="flex gap-4">
                <StepBadge n="4" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-ink">Write a blog post</h3>
                  <p class="mt-1 text-sm text-graphite leading-6">
                    Inside the Blog page, click <strong>Add child page → Blog Post Page</strong>. Fill in:
                  </p>
                  <ul class="mt-2 space-y-1 text-sm text-graphite">
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Title</strong> — shown as H1 and in SERP</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Primary author</strong> — required; drives Schema.org authorship</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Featured image</strong> — appears in blog index and OG tags</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Excerpt</strong> — 1–2 sentences; used as meta description</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Body</strong> — StreamField with 15 block types (Heading, Paragraph, FAQ, CTA, etc.)</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Primary service</strong> — the service page this post funnels traffic to</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Citation mode</strong> — APA 7 / MLA 9 / Chicago / sources list / none</span></li>
                  </ul>
                  <div class="mt-3 rounded-lg border border-blue-200 bg-blue-50 p-3 text-xs text-blue-800">
                    <strong>Tip — paste import:</strong> use <code class="rounded bg-blue-100 px-1">/cms-api/paste/</code> to convert pasted HTML or Word content into StreamField blocks automatically.
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 5 -->
            <div class="px-6 py-5">
              <div class="flex gap-4">
                <StepBadge n="5" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-ink">Create a service page</h3>
                  <p class="mt-1 text-sm text-graphite leading-6">
                    Inside the Services page, click <strong>Add child page → Service Page</strong>. Key fields:
                  </p>
                  <ul class="mt-2 space-y-1 text-sm text-graphite">
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Service category</strong> — groups services in the listing</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Pricing from / to</strong> — shown on cards and in structured data</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Turnaround hours</strong> — fastest and standard deadlines</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Primary CTA text/URL</strong> — the sticky bar button at bottom of page</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Body</strong> — StreamField with 16 blocks including Hero, TrustStrip, FeatureGrid, PricingTable</span></li>
                    <li class="flex gap-2"><CheckCircle class="mt-0.5 size-4 shrink-0 text-signal" /><span><strong>Reviewer</strong> — expert who reviewed this page (appears in reviewer card + Schema.org)</span></li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Step 6 -->
            <div class="px-6 py-5">
              <div class="flex gap-4">
                <StepBadge n="6" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-ink">Connect content to the funnel</h3>
                  <p class="mt-1 text-sm text-graphite leading-6">
                    Every blog post should connect to the revenue funnel. In the <strong>Promotions</strong> tab on a blog post:
                  </p>
                  <ul class="mt-2 space-y-1 text-sm text-graphite">
                    <li class="flex gap-2"><ArrowRight class="mt-0.5 size-4 shrink-0 text-berry" /><span>Set <strong>Primary service</strong> — the service this post leads to</span></li>
                    <li class="flex gap-2"><ArrowRight class="mt-0.5 size-4 shrink-0 text-berry" /><span>Set <strong>Content pillar</strong> — the topical cluster this post belongs to</span></li>
                    <li class="flex gap-2"><ArrowRight class="mt-0.5 size-4 shrink-0 text-berry" /><span>The <strong>Content Graph</strong> dashboard (admin sidebar) shows funnel performance once data accumulates</span></li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Step 7 -->
            <div class="px-6 py-5">
              <div class="flex gap-4">
                <StepBadge n="7" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-ink">Publish</h3>
                  <p class="mt-1 text-sm text-graphite leading-6">
                    At the bottom of any page editor, click <strong>Save draft</strong> to save without publishing, or use the <strong>Publish</strong> button to make it live immediately. To schedule a publish, use the <strong>Set schedule</strong> option — enter a go-live date and time.
                  </p>
                  <div class="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                    <strong>Pre-publish validation:</strong> Wagtail runs automatic checks before publish — it will warn you if the post has no primary service linked, fewer than 2 internal links, or a missing author. Blockers must be fixed before the page can go live.
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 8 -->
            <div class="px-6 py-5 bg-slate-50">
              <div class="flex gap-4">
                <StepBadge n="8" color="emerald" />
                <div class="min-w-0 flex-1">
                  <h3 class="font-semibold text-ink">Multi-site publishing</h3>
                  <p class="mt-1 text-sm text-graphite leading-6">
                    Each website has its own page tree. When you're in Wagtail admin, you must select the correct site from the <strong>Sites</strong> menu (top-right globe icon) before navigating the page tree. Content created under site A is completely separate from site B — authors, categories, tags, and pages are all tenant-scoped.
                  </p>
                  <div class="mt-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-900">
                    <strong>Pro tip:</strong> The Content Management section in this portal (sidebar → Content) also respects site scoping. Superadmins see a site switcher at the top.
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between border-t border-slate-200 px-6 py-4">
          <p class="text-xs text-graphite">Questions? Contact your platform administrator or open a support ticket.</p>
          <button
            class="focus-ring rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-graphite hover:bg-slate-50"
            @click="open = false"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { defineComponent, h, ref } from "vue";
import { ArrowRight, BookOpen, CheckCircle, ExternalLink, FileText, Users, X } from "@lucide/vue";

const open = ref(false);

// Inline StepBadge to keep component self-contained
const StepBadge = defineComponent({
  props: { n: String, color: { default: "blue" } },
  render() {
    const colors: Record<string, string> = {
      blue:    "bg-blue-600 text-white",
      emerald: "bg-emerald-600 text-white",
    };
    return h(
      "div",
      {
        class: `flex size-8 shrink-0 items-center justify-center rounded-full text-sm font-extrabold ${colors[this.color] ?? colors["blue"]}`,
      },
      this.n,
    );
  },
});
</script>
