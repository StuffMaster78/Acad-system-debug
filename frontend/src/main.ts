import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import { router } from "./router";
import "./styles/main.css";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia);

  // Resolve portal surface before the router starts so the navigation guard
  // can make synchronous surface decisions on the first navigation.
  const portalStore = usePortalContextStore();
  await portalStore.init();

  // NOTE: websites.ensure() is intentionally NOT called here.
  // Calling it at boot with no auth token hits /websites/ → 401 → the 401
  // interceptor calls window.location.replace('/auth/login') → infinite reload
  // loop (153 navigations per 8 seconds observed). Instead, each authenticated
  // view calls websites.ensure() after login when a token is present.

  app.use(router).mount("#app");
}

bootstrap();

// ── Back-Forward Cache (bfcache) guard ───────────────────────────────────────
// When the browser restores a page from bfcache (event.persisted = true),
// the Pinia auth store still holds the previous session's state in memory.
// If the user logged out and presses Back, the bfcache would restore an
// "authenticated" app state even though localStorage is clear.
// We detect this and force a real reload so the app starts fresh.
window.addEventListener("pageshow", (event) => {
  if (event.persisted) {
    // Page was restored from bfcache. Check whether stored auth matches reality.
    const storedToken = window.localStorage.getItem("writing_system.access");
    if (!storedToken) {
      // localStorage says no session but bfcache JS state may say otherwise.
      // Force a clean reload so the app re-bootstraps without stale auth.
      window.location.reload();
    }
  }
});
