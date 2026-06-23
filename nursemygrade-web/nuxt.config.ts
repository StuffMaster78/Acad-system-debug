export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@nuxtjs/sitemap'],

  compatibilityDate: '2026-06-09',

  devServer: { port: 3003 },

  nitro: {
    compressPublicAssets: { gzip: true, brotli: true },
    prerender: {
      crawlLinks: true,
      routes: [
        '/',
        '/services',
        '/order',
        '/quote',
        '/class-support',
        '/pricing',
        '/blog',
        '/authors',
        '/about',
        '/contact',
        '/apply',
        '/faq',
        '/how-it-works',
        '/terms',
        '/privacy',
        '/refunds',
        '/discounts',
        '/login',
        '/register',
        '/auth/magic-link',
        // Core nursing services (crawlLinks discovers most; explicit here for SSG reliability)
        '/services/nursing-essays',
        '/services/care-plans',
        '/services/soap-notes',
        '/services/capstone-projects',
        '/services/nursing-research-papers',
        '/services/nursing-case-studies',
        '/services/nursing-dissertations',
        '/services/concept-maps',
        '/services/nursing-coursework',
        '/services/online-nursing-classes',
        '/services/shadow-health',
        '/services/ihuman-patients',
        // Additional landing pages
        '/services/buy-nursing-papers',
        '/services/nursing-report',
        '/services/nursing-presentation',
        '/services/bsn-writing',
        '/services/msn-help',
        '/services/apa-nursing-papers',
        '/services/medical-paper-writing',
        '/services/nursing-homework',
        '/services/postgrad-nursing',
        '/services/health-medical-writers',
      ],
      failOnError: true,
    },
    devProxy: {
      '/api/v1': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: true,
        headers: { Host: 'nursemygrade.com' },
      },
      '/api/v2': {
        target: 'http://localhost:8000/api/v2',
        changeOrigin: true,
        headers: { Host: 'nursemygrade.com' },
      },
      '/cms-api': {
        target: 'http://localhost:8000/cms-api',
        changeOrigin: true,
        headers: { Host: 'nursemygrade.com' },
      },
    },
  },

  site: {
    url: 'https://nursemygrade.com',
    name: 'NurseMyGrade',
  },

  sitemap: {
    exclude: ['/login', '/register', '/auth/**'],
    sources: ['/api/_sitemap-urls'],
  },

  runtimeConfig: {
    siteHostname: 'nursemygrade.com',
    public: {
      apiBase: '',
      appUrl: '',
      siteUrl: 'https://nursemygrade.com',
      tawktoPropertyId: '',
      tawktoWidgetId: '',
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
        { rel: 'preload', as: 'style', href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap',
        },
      ],
    },
  },
})
