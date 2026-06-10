export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@nuxtjs/sitemap'],

  compatibilityDate: '2026-06-09',

  // SSG: pnpm build → .output/public/ → serve with nginx
  nitro: {
    prerender: {
      crawlLinks: true,
      routes: [
        '/',
        '/services',
        // Individual service slugs are discovered via crawlLinks: true
        // from the /services index page — no need to hardcode them.
        '/pricing',
        '/blog',
        '/authors',
        '/authors/sarah-kimani',
        '/authors/emily-chen',
        '/authors/james-whitfield',
        '/authors/michael-torres',
        '/about',
        '/contact',
        '/apply',
        '/faq',
        '/how-it-works',
        '/terms',
        '/privacy',
        '/refunds',
        '/login',
        '/register',
        '/auth/magic-link',
      ],
      failOnError: false,
    },
    // Dev: proxy /api/v1/* to Django so the Host header is localhost:3000
    // (matches the Website/PortalDefinition records seeded for local dev).
    // Production: nginx handles this — API calls go to api.essaymaniacs.com.
    devProxy: {
      // Nitro strips the matched prefix, then appends remainder to target.
      '/api/v1': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: false, // keeps Host: localhost:3000 so Django resolves the right tenant
      },
      // Wagtail API v2 — service pages, blog pages, images
      '/api/v2': {
        target: 'http://localhost:8000/api/v2',
        changeOrigin: false,
      },
      // Custom CMS API — attachments, authors, engagement, blog history
      '/cms-api': {
        target: 'http://localhost:8000/cms-api',
        changeOrigin: false,
      },
    },
  },

  // Sitemap — auto-discovers all pre-rendered URLs from crawlLinks
  // Dynamic routes (blog, authors, services) are included via URL sources
  site: {
    url: 'https://essaymaniacs.com',
    name: 'EssayManiacs',
  },

  sitemap: {
    exclude: ['/login', '/register', '/auth/**'],
    // Server route translates Wagtail API responses into [{loc}] format
    sources: ['/api/_sitemap-urls'],
  },

  runtimeConfig: {
    public: {
      apiBase: '',   // override with NUXT_PUBLIC_API_BASE in .env
      appUrl: '',    // override with NUXT_PUBLIC_APP_URL in .env
      siteUrl: 'https://essaymaniacs.com',
    },
  },

  components: [
    { path: '~/components/layout', prefix: '' },
    { path: '~/components/marketing', prefix: '' },
    { path: '~/components/ui', prefix: '' },
    { path: '~/components/cms', prefix: '' },
    { path: '~/components', prefix: '' },
  ],

  css: ['~/assets/css/main.css'],

  app: {
    head: {
      htmlAttrs: { lang: 'en' },
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap',
        },
      ],
    },
  },
})
