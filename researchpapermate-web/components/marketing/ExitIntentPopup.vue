<script setup lang="ts">
import { X } from '@lucide/vue'

const popup = useExitPopup()
const cfg   = computed(() => popup.config.value)

function isExternal(url?: string) {
  return !!url && /^https?:\/\//.test(url)
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="popup.open.value && cfg"
        class="fixed inset-0 z-[60] flex items-end justify-center px-4 pb-4 sm:items-center sm:pb-0"
        role="dialog"
        aria-modal="true"
        @click.self="popup.dismiss()"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 -z-10 bg-slate-950/60 backdrop-blur-[2px]"
          @click="popup.dismiss()"
        />

        <!-- Panel -->
        <div class="animate-popup relative w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-slate-950/8">

          <!-- Close -->
          <button
            class="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-slate-400 backdrop-blur-sm transition-colors hover:bg-slate-100 hover:text-slate-800"
            type="button"
            aria-label="Close"
            @click="popup.dismiss()"
          >
            <X class="h-4 w-4" />
          </button>

          <!-- Optional image -->
          <img
            v-if="cfg.image_url"
            :src="cfg.image_url"
            alt=""
            class="h-44 w-full object-cover"
          />

          <!-- Content -->
          <div class="p-6" :class="cfg.image_url ? '' : 'pt-8'">
            <p class="pr-6 text-xl font-bold leading-snug text-slate-900">
              {{ cfg.title }}
            </p>
            <p class="mt-2 text-sm leading-relaxed text-slate-500">
              {{ cfg.body }}
            </p>

            <div class="mt-5 flex flex-col gap-2 sm:flex-row-reverse sm:justify-start">
              <!-- Primary CTA — external href or internal NuxtLink -->
              <a
                v-if="isExternal(cfg.primary_cta_url)"
                :href="cfg.primary_cta_url"
                class="inline-flex items-center justify-center rounded-xl bg-amber-600 px-6 py-2.5 text-sm font-bold text-white shadow-sm transition-colors hover:bg-amber-600"
                @click="popup.dismiss()"
              >{{ cfg.primary_cta_label || 'Get started' }}</a>
              <NuxtLink
                v-else
                :to="cfg.primary_cta_url || '/order'"
                class="inline-flex items-center justify-center rounded-xl bg-amber-600 px-6 py-2.5 text-sm font-bold text-white shadow-sm transition-colors hover:bg-amber-600"
                @click="popup.dismiss()"
              >{{ cfg.primary_cta_label || 'Get started' }}</NuxtLink>

              <!-- Secondary CTA / dismiss -->
              <button
                v-if="cfg.secondary_cta_label"
                class="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-600 transition-colors hover:bg-slate-50"
                type="button"
                @click="popup.dismiss()"
              >{{ cfg.secondary_cta_label }}</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
@keyframes popup-in {
  from { opacity: 0; transform: translateY(10px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)     scale(1);    }
}
.animate-popup { animation: popup-in 0.22s ease-out both; }
</style>
