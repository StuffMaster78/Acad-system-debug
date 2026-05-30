<template>
  <div class="min-h-screen bg-white">

    <div v-if="isLoading" class="mx-auto max-w-3xl px-6 py-20 animate-pulse space-y-6">
      <div class="h-8 w-2/3 rounded bg-slate-200" />
      <div class="h-4 w-1/2 rounded bg-slate-100" />
      <div class="h-40 rounded-xl bg-slate-100" />
    </div>

    <div v-else-if="notFound" class="py-32 text-center">
      <RouterLink to="/resources" class="text-sm text-berry hover:underline">← Resources</RouterLink>
      <p class="mt-4 font-semibold text-ink">Resource not found.</p>
    </div>

    <template v-else-if="resource">
      <!-- Header -->
      <div class="border-b border-slate-100 bg-slate-50 px-6 py-14">
        <div class="mx-auto max-w-3xl">
          <RouterLink to="/resources" class="mb-4 inline-flex items-center gap-1.5 text-xs text-graphite hover:text-ink">
            <ArrowLeft class="size-3" /> All resources
          </RouterLink>

          <div class="flex flex-wrap gap-2 mb-4">
            <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-graphite capitalize">
              {{ resource.attachment_type.replace(/_/g, " ") }}
            </span>
            <span
              class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
              :class="gateBadgeClass(resource.gate_type)"
            >{{ gateLabel(resource.gate_type) }}</span>
          </div>

          <h1 class="text-3xl font-extrabold text-ink">{{ resource.title }}</h1>
          <p v-if="resource.description" class="mt-3 text-lg text-graphite">{{ resource.description }}</p>

          <div class="mt-4 flex flex-wrap gap-4 text-xs text-graphite">
            <span v-if="resource.page_count">{{ resource.page_count }} pages</span>
            <span v-if="resource.file_format" class="uppercase font-semibold">{{ resource.file_format }}</span>
            <span v-if="resource.academic_level">{{ resource.academic_level }}</span>
            <span v-if="resource.formatting_style">{{ resource.formatting_style }}</span>
            <span v-if="resource.download_count" class="ml-auto">{{ resource.download_count.toLocaleString() }} downloads</span>
          </div>
        </div>
      </div>

      <!-- Gate / Download section -->
      <div class="mx-auto max-w-3xl px-6 py-10">
        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-8">

          <!-- Free download -->
          <template v-if="access?.allowed">
            <div class="text-center">
              <CheckCircle class="mx-auto mb-3 size-10 text-signal" />
              <h2 class="text-xl font-bold text-ink">Ready to download</h2>
              <p class="mt-1 text-sm text-graphite">Click below to get your free copy.</p>
              <button
                class="mt-6 inline-flex items-center gap-2 rounded-xl bg-signal px-8 py-3.5 font-bold text-white shadow hover:bg-emerald-700 disabled:opacity-60"
                :disabled="isDownloading"
                @click="handleDownload"
              >
                <Loader2 v-if="isDownloading" class="size-5 animate-spin" />
                <Download v-else class="size-5" />
                {{ isDownloading ? "Preparing…" : "Download now" }}
              </button>
              <p v-if="downloadError" class="mt-3 text-sm text-berry">{{ downloadError }}</p>
            </div>
          </template>

          <!-- Email gate -->
          <template v-else-if="access?.requires_email">
            <h2 class="mb-1 text-xl font-bold text-ink">Enter your email to download</h2>
            <p class="mb-5 text-sm text-graphite">We'll send the download link to your inbox. No spam, unsubscribe anytime.</p>
            <form class="space-y-3" @submit.prevent="submitEmail">
              <input
                v-model.trim="email"
                type="email"
                placeholder="you@example.com"
                class="focus-ring w-full rounded-xl border border-slate-200 px-4 py-3 text-sm"
                required
                :disabled="isDownloading"
              />
              <label class="flex items-start gap-2 text-xs text-graphite">
                <input v-model="consentMarketing" type="checkbox" class="mt-0.5 rounded border-slate-300" />
                I'd like to receive occasional writing tips and resource updates.
              </label>
              <p v-if="downloadError" class="text-xs text-berry">{{ downloadError }}</p>
              <button
                type="submit"
                class="w-full rounded-xl bg-berry py-3 font-bold text-white shadow hover:bg-rose-700 disabled:opacity-60"
                :disabled="isDownloading || !email"
              >
                <Loader2 v-if="isDownloading" class="inline size-4 animate-spin mr-1" />
                Get free download
              </button>
            </form>
          </template>

          <!-- Account gate -->
          <template v-else-if="access?.requires_account">
            <div class="text-center">
              <Lock class="mx-auto mb-3 size-10 text-graphite" />
              <h2 class="text-xl font-bold text-ink">Sign in to download</h2>
              <p class="mt-1 text-sm text-graphite">This resource is available to registered users.</p>
              <div class="mt-6 flex justify-center gap-3">
                <RouterLink to="/auth/login" class="rounded-xl bg-ink px-6 py-2.5 font-bold text-white hover:bg-slate-800">
                  Sign in
                </RouterLink>
                <RouterLink to="/auth/register" class="rounded-xl border border-slate-200 bg-white px-6 py-2.5 font-semibold text-ink hover:bg-slate-50">
                  Create account
                </RouterLink>
              </div>
            </div>
          </template>

          <!-- Paid gate -->
          <template v-else-if="access?.requires_purchase">
            <div class="text-center">
              <CreditCard class="mx-auto mb-3 size-10 text-saffron" />
              <h2 class="text-xl font-bold text-ink">Premium resource</h2>
              <p v-if="resource.price" class="mt-1 text-3xl font-extrabold text-ink">${{ resource.price }}</p>
              <p class="mt-1 text-sm text-graphite">Place an order to get access to this resource.</p>
              <RouterLink
                to="/auth/register"
                class="mt-6 inline-flex items-center gap-2 rounded-xl bg-berry px-7 py-3.5 font-bold text-white shadow hover:bg-rose-700"
              >
                Get started <ArrowRight class="size-4" />
              </RouterLink>
            </div>
          </template>

          <!-- Loading access check -->
          <div v-else class="py-8 text-center">
            <Loader2 class="mx-auto size-6 animate-spin text-slate-400" />
          </div>
        </div>

        <!-- Author card -->
        <div v-if="resource.author" class="mt-8 flex items-center gap-4 rounded-xl border border-slate-200 bg-slate-50 p-5">
          <img
            v-if="resource.author.profile_photo?.meta?.download_url"
            :src="resource.author.profile_photo.meta.download_url"
            :alt="resource.author.name"
            class="size-12 rounded-full object-cover"
          />
          <div>
            <p class="text-xs text-graphite">Created by</p>
            <RouterLink :to="`/authors/${resource.author.slug}`" class="font-semibold text-ink hover:text-berry">
              {{ resource.author.name }}
            </RouterLink>
            <p v-if="resource.author.credentials" class="text-xs text-graphite">{{ resource.author.credentials }}</p>
          </div>
        </div>

        <!-- Related service -->
        <div v-if="resource.related_service" class="mt-4 rounded-xl border border-slate-200 bg-white p-5">
          <p class="text-xs text-graphite">Related service</p>
          <RouterLink :to="`/services/${resource.related_service.slug}`" class="font-semibold text-berry hover:underline">
            {{ resource.related_service.title }} →
          </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { ArrowLeft, ArrowRight, CheckCircle, CreditCard, Download, Lock, Loader2 } from "@lucide/vue";
import { cmsApi, type AttachmentSummary, type AccessCheckResult } from "@/api/cms";
import { useMeta } from "@/composables/useMeta";

const route       = useRoute();
const isLoading   = ref(true);
const notFound    = ref(false);
const resource    = ref<AttachmentSummary | null>(null);
const access      = ref<AccessCheckResult | null>(null);
const isDownloading = ref(false);
const downloadError = ref("");
const email           = ref("");
const consentMarketing = ref(false);

async function load() {
  const slug = route.params.slug as string;
  isLoading.value   = true;
  notFound.value    = false;
  resource.value    = null;
  access.value      = null;

  try {
    const [resRes, accessRes] = await Promise.all([
      cmsApi.attachment(slug),
      cmsApi.checkAccess(slug),
    ]);
    resource.value = resRes.data;
    access.value   = accessRes.data;

    useMeta({
      title: resource.value.title,
      description: resource.value.description ?? `Download ${resource.value.title} — free academic resource.`,
      url: window.location.href,
    });
  } catch {
    notFound.value = true;
  } finally {
    isLoading.value = false;
  }
}

async function handleDownload() {
  if (!resource.value) return;
  isDownloading.value = true;
  downloadError.value = "";
  try {
    const { data } = await cmsApi.download(resource.value.slug);
    if (data.download_url) {
      window.open(data.download_url, "_blank", "noopener,noreferrer");
    }
  } catch {
    downloadError.value = "Download failed. Please try again.";
  } finally {
    isDownloading.value = false;
  }
}

async function submitEmail() {
  if (!resource.value || !email.value) return;
  isDownloading.value = true;
  downloadError.value = "";
  try {
    const { data } = await cmsApi.download(resource.value.slug, {
      email: email.value,
      consent_marketing: consentMarketing.value,
    });
    if (data.download_url) {
      window.open(data.download_url, "_blank", "noopener,noreferrer");
      access.value = { allowed: true };
    } else {
      downloadError.value = data.error ?? "Something went wrong.";
    }
  } catch {
    downloadError.value = "Submission failed. Please try again.";
  } finally {
    isDownloading.value = false;
  }
}

function gateBadgeClass(gate: string): string {
  if (gate === "free")    return "bg-emerald-100 text-emerald-700";
  if (gate === "email")   return "bg-amber-100 text-amber-700";
  if (gate === "account") return "bg-blue-100 text-blue-700";
  return "bg-rose-100 text-rose-700";
}

function gateLabel(gate: string): string {
  const map: Record<string, string> = { free: "Free", email: "Email required", account: "Sign in", customer: "Customers only", paid: "Paid" };
  return map[gate] ?? gate;
}

onMounted(load);
watch(() => route.params.slug, load);
</script>
