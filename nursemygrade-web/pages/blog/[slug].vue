<script setup lang="ts">
const route = useRoute()
const { getBySlug, getAll, getByAuthor } = useBlog()

const post = getBySlug(route.params.slug as string)
if (!post) {
  throw createError({ statusCode: 404, message: 'Post not found' })
}

const related = getAll()
  .filter(p => p.slug !== post.slug && p.category === post.category)
  .slice(0, 3)

const byAuthor = post.author
  ? getByAuthor(post.author.slug, post.slug).slice(0, 4)
  : []

const { toc, processedBody } = useToc(post.body)

// Mid-article CTA — nursing-specific, injected after the 4th paragraph.
const inlineCta = `
<div class="not-prose my-8 overflow-hidden rounded-2xl border border-brand-100 shadow-sm">
  <div class="flex flex-col sm:flex-row">
    <div class="bg-brand-600 h-1.5 w-full sm:h-auto sm:w-1.5 shrink-0 rounded-t-2xl sm:rounded-t-none sm:rounded-l-2xl"></div>
    <div class="flex flex-col gap-4 bg-gradient-to-r from-brand-50 to-white px-6 py-5 sm:flex-row sm:items-center sm:justify-between flex-1">
      <div>
        <p class="text-[11px] font-bold uppercase tracking-widest text-brand-600 mb-1">Written by nurses, for nurses</p>
        <p class="font-semibold text-slate-900">Clinical rotations + coursework is a lot. Let a qualified BSN or MSN nurse write this for you.</p>
        <div class="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
          <span>✓ NANDA · SOAP · APA 7th — done right</span>
          <span>✓ From $24/page</span>
          <span>✓ As fast as 3 hours</span>
          <span>✓ Grade guarantee</span>
        </div>
      </div>
      <a href="/order" class="shrink-0 inline-flex items-center justify-center whitespace-nowrap rounded-xl bg-brand-600 px-6 py-2.5 text-sm font-bold text-white transition-colors hover:bg-brand-700">
        Get my nurse writer →
      </a>
    </div>
  </div>
</div>`

const bodyWithInlineCta = computed(() => {
  let count = 0
  let insertAt = -1
  const re = /<\/p>/gi
  let m: RegExpExecArray | null
  while ((m = re.exec(processedBody)) !== null) {
    count++
    if (count === 4) { insertAt = m.index + m[0].length; break }
  }
  if (insertAt === -1) return processedBody
  return processedBody.slice(0, insertAt) + inlineCta + processedBody.slice(insertAt)
})

const fmtDate = (d: string) =>
  new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })

const authorInitials = computed(() => {
  if (!post.author) return '?'
  const w = post.author.name.trim().split(/\s+/)
  return w.length >= 2 ? (w[0][0] + w[w.length - 1][0]).toUpperCase() : post.author.name[0].toUpperCase()
})

const ROLE_BADGE: Record<string, string> = {
  'Senior Writer':         'bg-brand-100 text-brand-700',
  'Subject Matter Expert': 'bg-amber-100 text-amber-700',
  'Writer':                'bg-slate-100 text-slate-600',
  'Editor':                'bg-violet-100 text-violet-700',
}

const config = useRuntimeConfig()
const siteUrl = config.public.siteUrl || 'https://nursemygrade.com'
const canonicalUrl = `${siteUrl}/blog/${post.slug}`

useSeoMeta({
  title: post.title,
  description: post.excerpt,
  ogTitle: post.title,
  ogDescription: post.excerpt,
  articlePublishedTime: post.date,
  articleAuthor: post.author?.name,
})

useHead({
  link: [{ rel: 'canonical', href: canonicalUrl }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: post.title,
      description: post.excerpt,
      datePublished: post.date,
      url: canonicalUrl,
      author: post.author
        ? {
            '@type': 'Person',
            name: post.author.name,
            description: post.author.bio,
            honorificSuffix: post.author.credentials,
            ...(post.author.orcid ? { sameAs: [`https://orcid.org/${post.author.orcid}`] } : {}),
          }
        : { '@type': 'Organization', name: 'NurseMyGrade' },
      publisher: {
        '@type': 'Organization',
        name: 'NurseMyGrade',
        url: 'https://nursemygrade.com',
        logo: { '@type': 'ImageObject', url: 'https://nursemygrade.com/favicon.svg' },
      },
    }),
  }],
})
</script>

<template>
  <div class="section">
    <div class="grid gap-10 lg:grid-cols-[1fr_300px]">

      <!-- ── Left: article content ──────────────────────────────────── -->
      <article class="min-w-0">
        <!-- Breadcrumbs -->
        <div class="mb-6">
          <Breadcrumbs :items="[
            { label: 'Blog', href: '/blog' },
            { label: post.category, href: '/blog' },
            { label: post.title },
          ]" />
        </div>

        <!-- Meta bar -->
        <div class="mb-4 flex flex-wrap items-center gap-3">
          <span class="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
            {{ post.category }}
          </span>
          <span class="text-xs text-slate-400">{{ post.readTime }}</span>
          <time class="text-xs text-slate-400">{{ fmtDate(post.date) }}</time>
        </div>

        <!-- Title + excerpt -->
        <h1 class="font-serif text-3xl font-bold leading-tight text-slate-900 sm:text-4xl">
          {{ post.title }}
        </h1>
        <p class="mt-4 text-lg leading-relaxed text-slate-600">{{ post.excerpt }}</p>

        <!-- Author byline -->
        <div v-if="post.author" class="mt-6 flex items-center gap-3 border-t border-slate-100 pt-5">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-100 text-sm font-bold text-brand-700">
            {{ authorInitials }}
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-900">{{ post.author.name }}</p>
            <p class="text-xs text-slate-500">{{ post.author.credentials }}</p>
          </div>
        </div>

        <!-- Table of contents -->
        <nav
          v-if="toc.length >= 3"
          class="mt-8 rounded-xl border border-slate-200 bg-slate-50 p-5"
          aria-label="Table of contents"
        >
          <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">In this article</p>
          <ol class="space-y-1.5">
            <li
              v-for="item in toc"
              :key="item.anchor"
              :class="item.level === 'h3' ? 'ml-4' : ''"
            >
              <a
                :href="`#${item.anchor}`"
                class="text-sm text-brand-600 hover:underline"
              >{{ item.text }}</a>
            </li>
          </ol>
        </nav>

        <!-- Article body (headings have injected id attrs for anchor nav) -->
        <div
          class="prose prose-slate prose-lg mt-10 max-w-none
                 prose-headings:font-serif prose-headings:font-bold
                 prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                 prose-strong:text-slate-900"
          v-html="bodyWithInlineCta"
        />

        <!-- Share buttons -->
        <div class="mt-10">
          <ClientOnly>
            <ShareButtons :title="post.title" />
          </ClientOnly>
        </div>

        <!-- End-of-article CTA -->
        <div class="mt-10 rounded-2xl bg-brand-900 p-8">
          <div class="sm:flex sm:items-center sm:justify-between sm:gap-8">
            <div>
              <p class="mb-1 text-xs font-bold uppercase tracking-widest text-brand-400">500+ BSN · MSN · DNP nurses available now</p>
              <h2 class="font-serif text-2xl font-bold text-white">Still staring at a blank page?</h2>
              <p class="mt-2 leading-relaxed text-brand-200">
                A real nurse who knows your subject can write your care plan, SOAP note, capstone,
                or essay — from scratch, clinically accurate, from $24/page.
              </p>
              <ul class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-sm text-brand-300">
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Grade or money back</li>
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Zero AI — nurse-written</li>
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> As fast as 3 hours</li>
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Free Turnitin report</li>
              </ul>
            </div>
            <NuxtLink
              to="/order"
              class="mt-6 block shrink-0 rounded-xl bg-white px-8 py-3 text-center text-sm font-bold text-brand-700 transition-colors hover:bg-brand-50 sm:mt-0"
            >
              Order my nursing paper →
            </NuxtLink>
          </div>
        </div>

        <!-- ── Author card ─────────────────────────────────────────── -->
        <div v-if="post.author" class="mt-10 overflow-hidden rounded-2xl border border-slate-200 bg-white">
          <!-- Header band -->
          <div class="flex items-start gap-5 border-b border-slate-100 bg-slate-50 px-6 py-6">
            <!-- Avatar -->
            <div class="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-2xl font-bold text-brand-700 ring-2 ring-white shadow-sm">
              {{ authorInitials }}
            </div>

            <!-- Identity -->
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="text-lg font-bold text-slate-900">{{ post.author.name }}</p>
                <span
                  class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="ROLE_BADGE[post.author.role] ?? 'bg-slate-100 text-slate-600'"
                >
                  {{ post.author.role }}
                </span>
              </div>
              <p class="mt-0.5 text-sm font-medium text-slate-500">{{ post.author.credentials }}</p>

              <!-- Verified credential pills -->
              <div class="mt-2 flex flex-wrap gap-2">
                <a
                  v-if="post.author.orcid"
                  :href="`https://orcid.org/${post.author.orcid}`"
                  target="_blank" rel="noreferrer"
                  class="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 hover:bg-emerald-100 transition-colors"
                >
                  <span class="font-bold">iD</span> ORCID
                </a>
                <a
                  v-if="post.author.scholar"
                  :href="post.author.scholar"
                  target="_blank" rel="noreferrer"
                  class="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700 hover:bg-blue-100 transition-colors"
                >
                  Scholar
                </a>
              </div>
            </div>
          </div>

          <!-- Bio + socials -->
          <div class="px-6 py-5">
            <p class="text-sm leading-7 text-slate-600">{{ post.author.bio }}</p>
            <div class="mt-4 flex flex-wrap gap-2">
              <a
                v-if="post.author.linkedin"
                :href="post.author.linkedin"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 transition-colors hover:border-brand-300 hover:text-brand-700"
              >
                LinkedIn
              </a>
              <a
                v-if="post.author.twitter"
                :href="`https://twitter.com/${post.author.twitter}`"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 transition-colors hover:border-brand-300 hover:text-brand-700"
              >
                @{{ post.author.twitter }}
              </a>
            </div>
          </div>

          <!-- More articles by this author -->
          <div v-if="byAuthor.length" class="border-t border-slate-100 px-6 py-5">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
              More by {{ post.author!.name.split(' ')[0] }}
            </p>
            <ul class="space-y-3">
              <li v-for="p in byAuthor" :key="p.slug">
                <NuxtLink
                  :href="`/blog/${p.slug}`"
                  class="group flex items-start gap-3"
                >
                  <!-- Category colour dot -->
                  <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand-300 group-hover:bg-brand-600 transition-colors" />
                  <div class="min-w-0">
                    <p class="text-sm font-medium leading-snug text-slate-800 group-hover:text-brand-700 transition-colors line-clamp-2">
                      {{ p.title }}
                    </p>
                    <p class="mt-0.5 text-xs text-slate-400">{{ p.category }} · {{ p.readTime }}</p>
                  </div>
                </NuxtLink>
              </li>
            </ul>
            <NuxtLink
              :href="`/authors/${post.author!.slug}`"
              class="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-brand-700 hover:underline"
            >
              All articles by {{ post.author!.name.split(' ').slice(0, 2).join(' ') }} →
            </NuxtLink>
          </div>
        </div>

        <!-- ── Editorial process ───────────────────────────────────── -->
        <div class="mt-6">
          <EditorialProcess :published-at="post.date" />
        </div>

        <!-- Related posts -->
        <div v-if="related.length" class="mt-16">
          <h2 class="mb-6 font-serif text-xl font-bold text-slate-900">More on {{ post.category }}</h2>
          <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <NuxtLink
              v-for="r in related"
              :key="r.slug"
              :href="`/blog/${r.slug}`"
              class="card group flex flex-col transition-shadow hover:border-brand-200 hover:shadow-md"
            >
              <div class="mb-2 flex items-center gap-2">
                <span class="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700">{{ r.category }}</span>
                <span class="text-xs text-slate-400">{{ r.readTime }}</span>
              </div>
              <h3 class="flex-1 font-semibold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">{{ r.title }}</h3>
              <p class="mt-2 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ r.excerpt }}</p>
              <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                <time class="text-xs text-slate-400">{{ new Date(r.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}</time>
                <span class="text-xs font-semibold text-brand-600 group-hover:underline">Read →</span>
              </div>
            </NuxtLink>
          </div>
        </div>
      </article>

      <!-- ── Right: sticky sidebar ──────────────────────────────────── -->
      <div class="lg:sticky lg:top-24 lg:self-start">
        <BlogSidebar />
      </div>

    </div>
  </div>
</template>
