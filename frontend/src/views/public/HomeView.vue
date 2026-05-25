<script setup lang="ts">
import { RouterLink } from "vue-router";
import { ArrowRight, ClipboardCheck, MessageSquare, ShieldCheck } from "@lucide/vue";
</script>

<template>
  <section class="mx-auto grid min-h-[calc(100vh-4rem)] max-w-7xl items-center gap-8 px-4 py-10 lg:grid-cols-[minmax(0,1fr)_420px] lg:px-6">
    <div>
      <p class="text-sm font-semibold uppercase text-signal">Writing System Platform</p>
      <h1 class="mt-3 max-w-3xl text-4xl font-semibold text-ink md:text-5xl">
        Academic writing operations, built around orders.
      </h1>
      <p class="mt-4 max-w-2xl text-base leading-7 text-graphite">
        Clients, writers, editors, support, and admins get focused workspaces
        connected to the same backend workflows.
      </p>
      <div class="mt-6 flex flex-wrap gap-3">
        <RouterLink
          class="focus-ring inline-flex h-11 items-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white"
          to="/auth/login"
        >
          Open workspace
          <ArrowRight class="h-4 w-4" />
        </RouterLink>
        <RouterLink
          class="focus-ring inline-flex h-11 items-center rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
          to="/services"
        >
          View services
        </RouterLink>
      </div>
    </div>

    <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
      <div class="space-y-3">
        <div class="rounded-md bg-slate-50 p-4">
          <ClipboardCheck class="h-5 w-5 text-signal" />
          <h2 class="mt-3 text-sm font-semibold">Order lifecycle</h2>
          <p class="mt-1 text-sm text-graphite">Create, pay, staff, submit, review, revise, and archive.</p>
        </div>
        <div class="rounded-md bg-slate-50 p-4">
          <MessageSquare class="h-5 w-5 text-saffron" />
          <h2 class="mt-3 text-sm font-semibold">Threaded communication</h2>
          <p class="mt-1 text-sm text-graphite">Tickets, messages, escalations, files, and saved replies.</p>
        </div>
        <div class="rounded-md bg-slate-50 p-4">
          <ShieldCheck class="h-5 w-5 text-berry" />
          <h2 class="mt-3 text-sm font-semibold">Operational control</h2>
          <p class="mt-1 text-sm text-graphite">Dashboards for staff, quality, finance, and system health.</p>
        </div>
      </div>
    </div>
  </section>
</template>
