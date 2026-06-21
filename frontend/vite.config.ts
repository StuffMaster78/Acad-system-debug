import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const BACKEND = process.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return;
          // echarts + zrender are ~1 MB minified; only loaded in admin dashboards
          if (id.includes('echarts') || id.includes('vue-echarts') || id.includes('zrender')) {
            return 'vendor-charts';
          }
          // Tiptap + ProseMirror — only in admin/writer compose views
          if (id.includes('@tiptap') || id.includes('prosemirror')) {
            return 'vendor-editor';
          }
          // Lucide icon pack — referenced everywhere but large enough to isolate
          if (id.includes('@lucide')) {
            return 'vendor-icons';
          }
          // Vue core runtime — tiny, cached permanently after first visit
          if (id.includes('/vue/') || id.includes('/vue-router/') || id.includes('/pinia/') || id.includes('@vue/')) {
            return 'vendor-vue';
          }
          // axios, dompurify, and any other small utilities
          return 'vendor';
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Django REST API + Wagtail headless API
      "/api/": { target: BACKEND, changeOrigin: true },
      // Custom CMS API
      "/cms-api/": { target: BACKEND, changeOrigin: true },
      // Wagtail admin UI (staff only)
      "/cms-admin/": { target: BACKEND, changeOrigin: true },
      // SEO pages API
      "/seo-pages/": { target: BACKEND, changeOrigin: true },
      // Django static files (admin CSS/JS, Wagtail UI assets)
      "/static/": { target: BACKEND, changeOrigin: true },
      // User-uploaded media
      "/media/": { target: BACKEND, changeOrigin: true },
      // Health endpoints
      "/health/": { target: BACKEND, changeOrigin: true },
      // Wagtail front-end page serving (CMS public pages)
      "/cms/": { target: BACKEND, changeOrigin: true },
    },
  },
});
