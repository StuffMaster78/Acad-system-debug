export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@nuxtjs/sitemap'],

  compatibilityDate: '2026-06-09',

  // SSG: pnpm build → .output/public/ → serve with nginx
  nitro: {
    compressPublicAssets: { gzip: true, brotli: true },
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
      failOnError: true,
    },
    // Dev: proxy /api/v1/* to Django so the Host header is localhost:3000
    // (matches the Website/PortalDefinition records seeded for local dev).
    // Production: nginx handles this — API calls go to api.essaymaniacs.com.
    devProxy: {
      '/api/v1': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: true,
        headers: { Host: 'essaymaniacs.com' },
      },
      '/api/v2': {
        target: 'http://localhost:8000/api/v2',
        changeOrigin: true,
        headers: { Host: 'essaymaniacs.com' },
      },
      '/cms-api': {
        target: 'http://localhost:8000/cms-api',
        changeOrigin: true,
        headers: { Host: 'essaymaniacs.com' },
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
    apiBaseInternal: '',
    siteHostname: 'essaymaniacs.com',
    public: {
      apiBase: '',
      appUrl: '',
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
