<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { LogIn } from "@lucide/vue";
import { roleHome } from "@/config/navigation";
import { useAuthStore } from "@/stores/auth";
import type { UserRole } from "@/types/roles";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const error = ref("");
const form = reactive({
  email: "",
  password: "",
});
const isDev = import.meta.env.DEV;
const previewRoles: UserRole[] = ["client", "writer", "editor", "support", "admin", "superadmin"];

const canSubmit = computed(() => form.email.length > 3 && form.password.length > 0);

async function submit() {
  error.value = "";
  try {
    await auth.login(form);
    const redirect = route.query.redirect?.toString();
    await router.push(redirect || (auth.role ? roleHome[auth.role] : "/client"));
  } catch {
    error.value = "We could not sign you in with those details.";
  }
}

async function preview(role: UserRole) {
  auth.previewAs(role);
  await router.push(roleHome[role]);
}
</script>

<template>
  <div class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-10">
    <section class="w-full max-w-md rounded-md border border-slate-200 bg-white p-6 shadow-panel">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Secure access</p>
        <h1 class="mt-2 text-2xl font-semibold">Sign in</h1>
        <p class="mt-2 text-sm leading-6 text-graphite">
          Use your platform account to open the correct workspace.
        </p>
      </div>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <label class="block">
          <span class="text-sm font-medium text-graphite">Email</span>
          <input
            v-model="form.email"
            class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3"
            autocomplete="email"
            type="email"
          />
        </label>
        <label class="block">
          <span class="text-sm font-medium text-graphite">Password</span>
          <input
            v-model="form.password"
            class="focus-ring mt-1 h-11 w-full rounded-md border border-slate-200 px-3"
            autocomplete="current-password"
            type="password"
          />
        </label>
        <p v-if="error" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
          {{ error }}
        </p>
        <button
          class="focus-ring inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          :disabled="!canSubmit || auth.isLoading"
          type="submit"
        >
          <LogIn class="h-4 w-4" />
          {{ auth.isLoading ? "Signing in" : "Sign in" }}
        </button>
      </form>

      <div v-if="isDev" class="mt-6 border-t border-slate-200 pt-5">
        <p class="text-sm font-semibold text-graphite">Preview workspace</p>
        <div class="mt-3 grid grid-cols-2 gap-2">
          <button
            v-for="roleName in previewRoles"
            :key="roleName"
            class="focus-ring h-10 rounded-md border border-slate-200 bg-slate-50 px-3 text-sm font-medium capitalize hover:bg-white"
            type="button"
            @click="preview(roleName)"
          >
            {{ roleName }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
