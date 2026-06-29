import { fileURLToPath } from 'node:url'

export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@nuxtjs/sitemap', '@nuxt/image'],

  compatibilityDate: '2026-06-10',

  devServer: { port: 3001 },

  css: ['~/assets/css/main.css'],

  components: [
    { path: '~/components/layout',    prefix: '' },
    { path: '~/components/marketing', prefix: '' },
    { path: '~/components/ui',        prefix: '' },
    { path: '~/components/cms',       prefix: '' },
    { path: '~/components',           prefix: '' },
  ],

  alias: {
    '@lucide/vue': fileURLToPath(new URL('./utils/lucide-icons.ts', import.meta.url)),
  },

  vite: {
    ssr: {
      // Vite otherwise externalizes this module into .nuxt/dist/server without
      // its package.json, so Node cannot resolve Nuxt's private import map.
      noExternal: ['nuxt-site-config'],
    },
  },

  // Hybrid rendering:
  // - Static marketing pages pre-rendered at build time (fast, cacheable)
  // - Service pages rendered per-request so Wagtail edits go live immediately
  routeRules: {
    // Static marketing pages — pre-rendered at build, served as HTML from edge
    '/':              { prerender: true },
    '/pricing':       { prerender: true },
    '/about':         { prerender: true },
    '/how-it-works':  { prerender: true },
    '/writers':       { prerender: true },
    '/reviews':       { prerender: true },
    '/faq':           { prerender: true },
    '/contact':       { prerender: true },
    '/apply':         { prerender: true },
    '/discounts':     { prerender: true },
    '/legal/terms':   { prerender: true },
    '/legal/privacy': { prerender: true },
    '/legal/refunds': { prerender: true },
    // Blog index pre-rendered; post pages ISR so Wagtail edits go live fast
    '/blog':          { prerender: true },
    // Legacy /blog/:slug and /services/:slug — 301 stub pages (fast redirect)
    '/blog/**':       { isr: 86400 },
    '/services/**':   { isr: 86400 },
    // Flat slug catch-all — covers both blog posts and service pages
    '/**':            { isr: 1800 },
  },

  nitro: {
    compressPublicAssets: { gzip: true, brotli: true },
    // Dev proxy: browser API calls route through the Nuxt dev server so
    // Host: gradecrest.com is injected before reaching Django/Wagtail.
    // gradecrest.com must be in Django ALLOWED_HOSTS (backend/.env).
    devProxy: {
      '/api': {
        target: 'http://localhost:8000/api',
        changeOrigin: true,
        headers: { Host: 'gradecrest.com' },
      },
      '/cms-api': {
        target: 'http://localhost:8000/cms-api',
        changeOrigin: true,
        headers: { Host: 'gradecrest.com' },
      },
    },
    prerender: {
      crawlLinks: true,
      ignore: ['/order', '/order/**'],
      routes: [
        '/',
        '/pricing',
        '/discounts',
        '/writers',
        '/how-it-works',
        '/reviews',
        '/faq',
        '/about',
        '/contact',
        '/apply',
        '/blog',
        '/services',
        '/essay-writing',
        '/research-papers',
        '/dissertations',
        '/nursing-essays',
        '/editing-proofreading',
        '/data-analysis',
        '/legal/terms',
        '/legal/privacy',
        '/legal/refunds',
        '/auth/login',
        '/auth/register',
        '/auth/magic-link',
      ],
    },
  },

  runtimeConfig: {
    apiBaseInternal: '', // NUXT_API_BASE_INTERNAL — http://web:8000 (server-only, bypasses nginx)
    // Injected as Host header on SSR $fetch calls so Wagtail resolves the correct
    // multi-tenant site. In production nginx handles this automatically.
    // Requires the domain to be in Django's ALLOWED_HOSTS (set in backend/.env).
    siteHostname: 'gradecrest.com',
    public: {
      apiBase: '',       // NUXT_PUBLIC_API_BASE — https://gradecrest.com (browser-accessible)
      appUrl: '',        // NUXT_PUBLIC_APP_URL  — client portal (for login/register links)
      siteUrl: 'https://gradecrest.com',
      tawktoPropertyId: '',
      tawktoWidgetId: '',
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        headers: { Host: 'gradecrest.com' },
      },
    },
  },

  site: {
    url: 'https://gradecrest.com',
    name: 'GradeCrest',
  },

  app: {
    head: {
      htmlAttrs: { lang: 'en' },
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'preload', as: 'style', href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap',
        },
      ],
    },
  },

  sitemap: {
    exclude: ['/auth/**', '/legal/**'],
    // Pulls all 160 CMS service page slugs at build/generate time
    sources: ['/api/__sitemap__/services'],
  },

  image: {
    // GC runs in hybrid SSR mode — IPX can transform images at request time.
    // Switch provider to 'cloudinary' or 'bunny' when CDN is configured.
    provider: 'ipx',
    domains: ['gradecrest.com'],
    screens: { xs: 320, sm: 640, md: 768, lg: 1024, xl: 1280 },
  },
})
