<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";
import { ArrowRight, Clock } from "@lucide/vue";

interface Service {
  title: string;
  description: string;
  category: string;
  levels: string[];
  turnaround: string;
  from: string;
}

const services: Service[] = [
  {
    title: "Essays",
    description: "Argumentative, descriptive, compare-and-contrast, reflective, and narrative essays across all academic levels.",
    category: "Academic writing",
    levels: ["High school", "Undergraduate", "Graduate"],
    turnaround: "From 3 hours",
    from: "$12",
  },
  {
    title: "Research papers",
    description: "Primary and secondary research papers with proper sourcing, citations, and literature synthesis.",
    category: "Academic writing",
    levels: ["Undergraduate", "Graduate", "PhD"],
    turnaround: "From 6 hours",
    from: "$15",
  },
  {
    title: "Case studies",
    description: "In-depth analysis of real-world scenarios applied to business, law, medicine, and social sciences.",
    category: "Academic writing",
    levels: ["Undergraduate", "Graduate"],
    turnaround: "From 6 hours",
    from: "$14",
  },
  {
    title: "Annotated bibliography",
    description: "Source summaries with critical evaluation, formatted to APA, MLA, Chicago, or Harvard style.",
    category: "Academic writing",
    levels: ["Undergraduate", "Graduate", "PhD"],
    turnaround: "From 3 hours",
    from: "$11",
  },
  {
    title: "Dissertations & theses",
    description: "Full chapter-by-chapter support — literature review, methodology, analysis, and conclusions.",
    category: "Dissertations",
    levels: ["Graduate", "PhD"],
    turnaround: "From 5 days",
    from: "$20",
  },
  {
    title: "Capstone projects",
    description: "Comprehensive final-year projects integrating coursework knowledge with applied research.",
    category: "Dissertations",
    levels: ["Undergraduate", "Graduate"],
    turnaround: "From 3 days",
    from: "$18",
  },
  {
    title: "Proofreading",
    description: "Grammar, syntax, punctuation, and clarity corrections on your existing draft with tracked changes.",
    category: "Editing",
    levels: ["All levels"],
    turnaround: "From 2 hours",
    from: "$7",
  },
  {
    title: "Substantive editing",
    description: "Structural reorganization, argument strengthening, and cohesion improvements beyond surface corrections.",
    category: "Editing",
    levels: ["Undergraduate", "Graduate", "PhD"],
    turnaround: "From 4 hours",
    from: "$10",
  },
  {
    title: "Formatting & citation",
    description: "APA, MLA, Chicago, Harvard, and Vancouver formatting applied to an existing document.",
    category: "Editing",
    levels: ["All levels"],
    turnaround: "From 1 hour",
    from: "$8",
  },
  {
    title: "Business reports",
    description: "Market analysis, feasibility studies, strategic plans, and executive summaries.",
    category: "Business writing",
    levels: ["Undergraduate", "Professional"],
    turnaround: "From 6 hours",
    from: "$15",
  },
  {
    title: "Cover letters & CVs",
    description: "Professionally crafted application documents tailored to your target role and industry.",
    category: "Business writing",
    levels: ["All levels"],
    turnaround: "From 2 hours",
    from: "$12",
  },
  {
    title: "Lab reports",
    description: "Structured scientific reports covering hypothesis, methodology, results, and discussion.",
    category: "STEM",
    levels: ["Undergraduate", "Graduate"],
    turnaround: "From 4 hours",
    from: "$14",
  },
  {
    title: "Math problem sets",
    description: "Step-by-step worked solutions for calculus, statistics, algebra, and discrete mathematics.",
    category: "STEM",
    levels: ["High school", "Undergraduate", "Graduate"],
    turnaround: "From 3 hours",
    from: "$13",
  },
  {
    title: "Programming assignments",
    description: "Python, Java, JavaScript, SQL, and R assignments with documented, runnable code.",
    category: "STEM",
    levels: ["Undergraduate", "Graduate"],
    turnaround: "From 4 hours",
    from: "$16",
  },
  {
    title: "PowerPoint presentations",
    description: "Visually consistent slide decks with speaker notes, charts, and branded layouts.",
    category: "Multimedia",
    levels: ["All levels"],
    turnaround: "From 3 hours",
    from: "$12",
  },
  {
    title: "Online course help",
    description: "Assignment completion, quiz support, and discussion post contributions for online learning.",
    category: "Multimedia",
    levels: ["Undergraduate", "Graduate"],
    turnaround: "Varies",
    from: "$10",
  },
];

const categories = computed(() => ["All", ...new Set(services.map((s) => s.category))]);
const active = ref("All");

const filtered = computed(() =>
  active.value === "All" ? services : services.filter((s) => s.category === active.value),
);
</script>

<template>
  <div>
    <section class="border-b border-slate-200 bg-white py-14">
      <div class="mx-auto max-w-7xl px-4 lg:px-6">
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Services</p>
        <h1 class="mt-3 text-4xl font-semibold text-ink">Service catalog</h1>
        <p class="mt-4 max-w-2xl text-base leading-7 text-graphite">
          Academic writing, editing, business documents, and STEM assignments — all delivered through a managed order workflow with writer matching and editorial QA.
        </p>
        <RouterLink
          class="focus-ring mt-6 inline-flex h-11 items-center gap-2 rounded-md bg-ink px-5 text-sm font-semibold text-white hover:bg-graphite"
          to="/auth/login"
        >
          Place an order
          <ArrowRight class="h-4 w-4" />
        </RouterLink>
      </div>
    </section>

    <section class="mx-auto max-w-7xl px-4 py-12 lg:px-6">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="cat in categories"
          :key="cat"
          class="focus-ring rounded-full px-4 py-2 text-sm font-semibold transition-colors"
          :class="active === cat
            ? 'bg-ink text-white'
            : 'border border-slate-200 bg-white text-graphite hover:border-slate-300 hover:text-ink'"
          type="button"
          @click="active = cat"
        >
          {{ cat }}
        </button>
      </div>

      <div class="mt-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="service in filtered"
          :key="service.title"
          class="flex flex-col rounded-xl border border-slate-200 bg-white p-6 shadow-panel"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-signal">{{ service.category }}</p>
              <h2 class="mt-1 text-base font-semibold text-ink">{{ service.title }}</h2>
            </div>
            <div class="shrink-0 text-right">
              <p class="text-xs text-graphite">from</p>
              <p class="text-lg font-semibold text-ink">{{ service.from }}<span class="text-xs font-normal">/page</span></p>
            </div>
          </div>

          <p class="mt-3 flex-1 text-sm leading-6 text-graphite">{{ service.description }}</p>

          <div class="mt-4 flex flex-wrap gap-1.5">
            <span
              v-for="level in service.levels"
              :key="level"
              class="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-graphite"
            >
              {{ level }}
            </span>
          </div>

          <div class="mt-4 flex items-center justify-between gap-3 border-t border-slate-100 pt-4">
            <div class="flex items-center gap-1.5 text-xs text-graphite">
              <Clock class="h-3.5 w-3.5" />
              {{ service.turnaround }}
            </div>
            <RouterLink
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
              to="/auth/login"
            >
              Order now
              <ArrowRight class="h-3 w-3" />
            </RouterLink>
          </div>
        </article>
      </div>
    </section>

    <section class="border-t border-slate-200 bg-slate-50 py-14">
      <div class="mx-auto max-w-7xl px-4 lg:px-6">
        <div class="rounded-2xl bg-ink px-8 py-12 text-center text-white md:px-14">
          <h2 class="text-2xl font-semibold">Don't see what you need?</h2>
          <p class="mt-3 text-base leading-7 text-white/70">
            Our support team can match almost any academic or professional writing task to a qualified writer.
          </p>
          <RouterLink
            class="focus-ring mt-6 inline-flex h-11 items-center gap-2 rounded-md bg-white px-5 text-sm font-semibold text-ink hover:bg-slate-100"
            to="/auth/login"
          >
            Sign in and ask support
            <ArrowRight class="h-4 w-4" />
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>
