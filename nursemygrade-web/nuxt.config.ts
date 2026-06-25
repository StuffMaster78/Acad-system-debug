export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@nuxtjs/sitemap', '@nuxt/image'],

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
        '/nursing-essays',
        '/care-plans',
        '/soap-notes',
        '/capstone-projects',
        '/nursing-research-papers',
        '/nursing-case-studies',
        '/nursing-dissertations',
        '/concept-maps',
        '/nursing-coursework',
        '/online-nursing-classes',
        '/shadow-health',
        '/ihuman-patients',
        // Additional landing pages
        '/buy-nursing-papers',
        '/nursing-report',
        '/nursing-presentation',
        '/bsn-writing',
        '/msn-help',
        '/apa-nursing-papers',
        '/medical-paper-writing',
        '/nursing-homework',
        '/postgrad-nursing',
        '/health-medical-writers',
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
      '/media': {
        target: 'http://localhost:8000',
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

  image: {
    // SSG site — no server-side transformer available at request time.
    // NuxtImg still injects correct width/height/loading/fetchpriority attrs
    // and will auto-switch to a CDN provider when NUXT_IMAGE_PROVIDER is set.
    provider: 'none',
    domains: ['nursemygrade.com'],
    screens: { xs: 320, sm: 640, md: 768, lg: 1024, xl: 1280 },
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
