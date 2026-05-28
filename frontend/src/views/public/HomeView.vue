<script setup lang="ts">
import { RouterLink } from "vue-router";
import {
  ArrowRight,
  ClipboardCheck,
  CreditCard,
  FileCheck2,
  MessageSquare,
  ShieldCheck,
  Upload,
  UserCheck,
} from "@lucide/vue";

const steps = [
  {
    number: "01",
    icon: ClipboardCheck,
    title: "Place your order",
    body: "Describe your task — subject, pages, deadline, academic level. Pay securely via card or wallet.",
  },
  {
    number: "02",
    icon: UserCheck,
    title: "Writer is matched",
    body: "A qualified writer claims your order from the pool or is assigned by our staffing team.",
  },
  {
    number: "03",
    icon: Upload,
    title: "Work submitted for QA",
    body: "The completed draft goes through an editorial quality check before reaching you.",
  },
  {
    number: "04",
    icon: FileCheck2,
    title: "Delivered to you",
    body: "Download your files directly from your order page. Request a revision if anything needs adjustment.",
  },
];

const highlights = [
  {
    icon: ShieldCheck,
    title: "Quality-gated delivery",
    body: "Every order passes through an assigned editor before being marked ready for download.",
    color: "text-berry",
  },
  {
    icon: MessageSquare,
    title: "Order-scoped messaging",
    body: "Chat with your writer or support team directly inside the order, with full history.",
    color: "text-saffron",
  },
  {
    icon: CreditCard,
    title: "Flexible payments",
    body: "Pay by card or top up a pre-paid wallet. Refunds and disputes handled through the platform.",
    color: "text-signal",
  },
];
</script>

<template>
  <div>
    <section class="mx-auto grid min-h-[calc(100vh-4rem)] max-w-7xl items-center gap-10 px-4 py-16 lg:grid-cols-[minmax(0,1fr)_440px] lg:px-6">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Academic writing platform</p>
        <h1 class="mt-3 max-w-2xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
          Academic writing operations,<br class="hidden md:block" /> built around orders.
        </h1>
        <p class="mt-5 max-w-xl text-base leading-7 text-graphite">
          Clients, writers, editors, support, and admins get focused workspaces
          connected to the same backend workflows — from order creation to file delivery.
        </p>
        <div class="mt-8 flex flex-wrap gap-3">
          <RouterLink
            class="focus-ring inline-flex h-11 items-center gap-2 rounded-md bg-ink px-5 text-sm font-semibold text-white hover:bg-graphite"
            to="/auth/login"
          >
            Open workspace
            <ArrowRight class="h-4 w-4" />
          </RouterLink>
          <RouterLink
            class="focus-ring inline-flex h-11 items-center rounded-md border border-slate-200 bg-white px-5 text-sm font-semibold text-ink hover:bg-slate-50"
            to="/services"
          >
            View services
          </RouterLink>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Platform capabilities</p>
        <div class="mt-4 space-y-3">
          <div class="rounded-lg bg-slate-50 p-4">
            <ClipboardCheck class="h-5 w-5 text-signal" />
            <h2 class="mt-3 text-sm font-semibold text-ink">Order lifecycle</h2>
            <p class="mt-1 text-sm leading-6 text-graphite">Create, pay, staff, submit, review, revise, and archive — all tracked in one place.</p>
          </div>
          <div class="rounded-lg bg-slate-50 p-4">
            <MessageSquare class="h-5 w-5 text-saffron" />
            <h2 class="mt-3 text-sm font-semibold text-ink">Threaded communication</h2>
            <p class="mt-1 text-sm leading-6 text-graphite">Tickets, messages, escalations, files, and saved replies per order.</p>
          </div>
          <div class="rounded-lg bg-slate-50 p-4">
            <ShieldCheck class="h-5 w-5 text-berry" />
            <h2 class="mt-3 text-sm font-semibold text-ink">Operational control</h2>
            <p class="mt-1 text-sm leading-6 text-graphite">Dashboards for staff, quality, finance, and system health.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="border-t border-slate-200 bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 lg:px-6">
        <div class="mx-auto max-w-2xl text-center">
          <p class="text-sm font-semibold uppercase tracking-wide text-signal">How it works</p>
          <h2 class="mt-3 text-3xl font-semibold text-ink">From order to delivery in four steps</h2>
          <p class="mt-4 text-base leading-7 text-graphite">
            Every order follows a structured lifecycle with dedicated touchpoints for the client, writer, editor, and support team.
          </p>
        </div>

        <div class="mt-14 grid gap-8 md:grid-cols-2 xl:grid-cols-4">
          <div
            v-for="step in steps"
            :key="step.number"
            class="relative rounded-lg border border-slate-200 bg-white p-6"
          >
            <span class="text-4xl font-semibold text-slate-100">{{ step.number }}</span>
            <component :is="step.icon" class="mt-3 h-6 w-6 text-signal" />
            <h3 class="mt-3 text-base font-semibold text-ink">{{ step.title }}</h3>
            <p class="mt-2 text-sm leading-6 text-graphite">{{ step.body }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="border-t border-slate-200 bg-slate-50 py-20">
      <div class="mx-auto max-w-7xl px-4 lg:px-6">
        <div class="mx-auto max-w-2xl text-center">
          <p class="text-sm font-semibold uppercase tracking-wide text-signal">Platform strengths</p>
          <h2 class="mt-3 text-3xl font-semibold text-ink">Built for reliability, not shortcuts</h2>
        </div>

        <div class="mt-12 grid gap-6 md:grid-cols-3">
          <div
            v-for="item in highlights"
            :key="item.title"
            class="rounded-lg border border-slate-200 bg-white p-6"
          >
            <component :is="item.icon" class="h-6 w-6" :class="item.color" />
            <h3 class="mt-4 text-base font-semibold text-ink">{{ item.title }}</h3>
            <p class="mt-2 text-sm leading-6 text-graphite">{{ item.body }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="border-t border-slate-200 bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 lg:px-6">
        <div class="mx-auto max-w-3xl rounded-2xl bg-ink px-8 py-14 text-center text-white">
          <h2 class="text-3xl font-semibold">Ready to place your first order?</h2>
          <p class="mt-4 text-base leading-7 text-white/70">
            Create an account, describe your task, and have a writer working on it today.
          </p>
          <div class="mt-8 flex flex-wrap justify-center gap-3">
            <RouterLink
              class="focus-ring inline-flex h-11 items-center gap-2 rounded-md bg-white px-5 text-sm font-semibold text-ink hover:bg-slate-100"
              to="/auth/login"
            >
              Get started
              <ArrowRight class="h-4 w-4" />
            </RouterLink>
            <RouterLink
              class="focus-ring inline-flex h-11 items-center rounded-md border border-white/30 px-5 text-sm font-semibold text-white hover:bg-white/10"
              to="/services"
            >
              Browse services
            </RouterLink>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
