<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-5xl space-y-4">

      <div v-if="store.isLoadingDetail" class="py-24 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else-if="store.detail">
        <!-- Back + header -->
        <div>
          <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
            <ArrowLeft class="size-3.5" /> Classes
          </button>
          <div class="rounded-lg border border-slate-200 bg-white p-6">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass(store.detail.status)">
                    {{ statusLabel(store.detail.status) }}
                  </span>
                  <span class="font-mono text-xs text-graphite">{{ store.detail.reference }}</span>
                </div>
                <h1 class="mt-2 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
                <p class="mt-0.5 text-sm text-graphite">{{ store.detail.subject }} · {{ store.detail.academic_level }}</p>
                <div class="mt-3 flex flex-wrap items-center gap-4 text-xs text-graphite">
                  <span class="flex items-center gap-1.5">
                    <Calendar class="size-3.5" />
                    {{ fmtDate(store.detail.start_date) }} — {{ fmtDate(store.detail.end_date) }}
                  </span>
                  <span class="flex items-center gap-1.5">
                    <UserCheck class="size-3.5" />
                    Client: <strong class="text-ink">{{ store.detail.client_username }}</strong>
                  </span>
                  <span v-if="store.detail.writer_username" class="flex items-center gap-1.5 text-emerald-700">
                    <Check class="size-3.5" />
                    Writer: {{ store.detail.writer_username }}
                  </span>
                  <span v-else class="flex items-center gap-1.5 text-amber-600">
                    <AlertCircle class="size-3.5" />
                    Unassigned
                  </span>
                </div>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-2xl font-bold text-ink">${{ store.detail.total_price }}</p>
                <p class="mt-0.5 text-xs capitalize text-graphite">{{ store.detail.payment_status }}</p>
              </div>
            </div>

            <!-- Progress bar -->
            <div class="mt-5">
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span class="text-graphite">{{ store.detail.completed_tasks }} of {{ store.detail.total_tasks }} tasks done</span>
                <span class="font-semibold text-ink">{{ progressPct }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="progressPct === 100 ? 'bg-emerald-500' : 'bg-berry'"
                  :style="{ width: `${progressPct}%` }"
                />
              </div>
            </div>

            <!-- Lifecycle actions (admin/superadmin only — support is view-only) -->
            <div class="mt-5 border-t border-slate-100 pt-4">
              <div class="flex flex-wrap items-center gap-2">
                <button
                  v-if="canManage && canAssignClassWriter"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
                  :disabled="store.isSaving"
                  type="button"
                  @click="openClassActionDialog('assign_writer')"
                >
                  <UserPlus class="size-3.5" />
                  Assign Writer
                </button>
                <button
                  v-if="canManage && canManualVerifyClassPayment"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 disabled:opacity-60"
                  :disabled="store.isSaving"
                  type="button"
                  @click="openClassActionDialog('manual_mark_paid')"
                >
                  <CircleDollarSign class="size-3.5" />
                  Verify Payment
                </button>
                <template v-if="canManage && ['pending', 'active'].includes(store.detail.status)">
                  <button
                    class="inline-flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-60"
                    :disabled="store.isSaving"
                    type="button"
                    @click="openClassActionDialog('cancel_class')"
                  >
                    <XCircle class="size-3.5" />
                    Cancel Class
                  </button>
                </template>
                <button
                  class="ml-auto inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50 hover:text-ink"
                  type="button"
                  @click="showGuide = !showGuide"
                >
                  <BookOpen class="size-3.5" />
                  {{ showGuide ? "Hide guide" : "State guide" }}
                </button>
              </div>

              <p v-if="canManage && !classAvailableActions.length" class="mt-3 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-graphite">
                No direct class action is available for this status.
              </p>

              <div v-if="classBlockedActions.length" class="mt-3 space-y-1.5">
                <div
                  v-for="item in classBlockedActions"
                  :key="item.action"
                  class="flex items-start gap-2 rounded-md border border-amber-100 bg-amber-50 px-3 py-2 text-xs text-amber-900"
                >
                  <Lock class="mt-0.5 size-3.5 shrink-0" />
                  <span><strong>{{ labelize(item.action) }}:</strong> {{ item.reason }}</span>
                </div>
              </div>

              <div v-if="showGuide" class="mt-4 overflow-x-auto rounded-lg border border-slate-200 bg-slate-50">
                <table class="min-w-full text-xs">
                  <thead class="bg-white text-left font-semibold uppercase text-graphite">
                    <tr>
                      <th class="px-3 py-2">Status</th>
                      <th class="px-3 py-2">Client</th>
                      <th class="px-3 py-2">Writer</th>
                      <th class="px-3 py-2">Staff</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-200">
                    <tr v-for="row in CLASS_STATE_GUIDE" :key="row.status">
                      <td class="px-3 py-2 font-semibold text-ink">{{ row.label }}</td>
                      <td class="px-3 py-2 text-graphite">{{ row.client }}</td>
                      <td class="px-3 py-2 text-graphite">{{ row.writer }}</td>
                      <td class="px-3 py-2 text-graphite">{{ row.staff }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>

        <!-- Summary cards -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Total</p>
            <p class="mt-1 text-lg font-bold text-ink">${{ store.detail.total_price }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Tasks</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.completed_tasks }}<span class="text-sm font-normal text-graphite">/{{ store.detail.total_tasks }}</span></p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Payment</p>
            <p class="mt-1 text-sm font-semibold capitalize text-graphite">{{ store.detail.payment_status }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Portal access</p>
            <p class="mt-1 text-sm font-semibold" :class="store.detail.portal_access_enabled ? 'text-emerald-700' : 'text-graphite'">
              {{ store.detail.portal_access_enabled ? 'Enabled' : 'Not set' }}
            </p>
          </div>
        </div>

        <section v-if="pricingSnapshot" class="rounded-lg border border-slate-200 bg-white p-5">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Scope & pricing preset</p>
              <h2 class="mt-1 text-base font-semibold text-ink">{{ pricingSnapshot.config_name || "Configured class request" }}</h2>
              <p class="mt-1 text-sm text-graphite">
                {{ snapshotPricingLabel }}
              </p>
            </div>
            <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-graphite">
              {{ labelize(String(pricingSnapshot.pricing_mode || "quote")) }}
            </span>
          </div>

          <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-3">
              <p class="text-xs text-graphite">Duration</p>
              <p class="mt-1 font-semibold text-ink">{{ pricingSnapshot.selected_duration?.label || "Not selected" }}</p>
              <p v-if="pricingSnapshot.selected_duration?.description" class="mt-1 text-xs text-graphite">{{ pricingSnapshot.selected_duration.description }}</p>
            </div>
            <div class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-3">
              <p class="text-xs text-graphite">Workload</p>
              <p class="mt-1 font-semibold text-ink">{{ pricingSnapshot.selected_workload?.label || "Not selected" }}</p>
              <p v-if="pricingSnapshot.selected_workload?.description" class="mt-1 text-xs text-graphite">{{ pricingSnapshot.selected_workload.description }}</p>
            </div>
            <div class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-3">
              <p class="text-xs text-graphite">Deposit</p>
              <p class="mt-1 font-semibold text-ink">{{ pricingSnapshot.payment_policy?.deposit_percentage || "0.00" }}%</p>
              <p class="mt-1 text-xs text-graphite">{{ pricingSnapshot.payment_policy?.require_deposit_before_start ? "Required before start" : "Flexible start policy" }}</p>
            </div>
            <div class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-3">
              <p class="text-xs text-graphite">Portal access</p>
              <p class="mt-1 font-semibold" :class="pricingSnapshot.portal_access_enabled ? 'text-emerald-700' : 'text-graphite'">
                {{ pricingSnapshot.portal_access_enabled ? "Expected" : "Not expected" }}
              </p>
              <p class="mt-1 text-xs text-graphite">{{ pricingSnapshot.payment_policy?.allow_installments ? "Installments allowed" : "No installments" }}</p>
            </div>
          </div>

          <div v-if="snapshotTasks.length" class="mt-4 border-t border-slate-100 pt-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Selected work</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <span
                v-for="task in snapshotTasks"
                :key="task.key"
                class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-graphite"
              >
                {{ task.label }}<span v-if="task.required"> · required</span>
              </span>
            </div>
          </div>
        </section>

        <!-- Tabs -->
        <div class="flex gap-1 rounded-lg border border-slate-200 bg-white p-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition-colors"
            :class="activeTab === tab.key ? 'bg-berry text-white shadow-sm' : 'text-graphite hover:text-ink'"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <!-- Tasks tab -->
        <div v-if="activeTab === 'tasks'" class="space-y-3">
          <div v-if="!store.detail.tasks.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            No tasks yet.
          </div>
          <div
            v-for="task in store.detail.tasks"
            :key="task.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs text-graphite">#{{ task.sequence }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="taskStatusClass(task.status)">
                    {{ taskStatusLabel(task.status) }}
                  </span>
                </div>
                <h3 class="mt-1.5 font-semibold text-ink">{{ task.title }}</h3>
                <p class="mt-0.5 text-sm text-graphite">{{ task.description }}</p>
              </div>
              <p class="shrink-0 text-xs text-graphite">Due {{ fmtDate(task.due_date) }}</p>
            </div>

            <div v-if="task.submission_notes" class="mt-3 rounded-lg bg-slate-50 px-4 py-2.5 text-sm text-graphite">
              <span class="font-medium text-ink">Submission notes:</span> {{ task.submission_notes }}
            </div>

            <!-- Existing grade -->
            <div v-if="task.grade" class="mt-3 flex items-center gap-2 text-sm">
              <span class="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700">Grade: {{ task.grade }}</span>
              <span v-if="task.grade_feedback" class="text-graphite">{{ task.grade_feedback }}</span>
            </div>

            <!-- Grade inline form -->
            <div v-if="gradingTaskId === task.id" class="mt-4 space-y-2.5">
              <div class="flex gap-2">
                <input v-model="gradeValue" placeholder="Grade (e.g. A, B+, 92%)" class="w-40 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
                <input v-model="gradeFeedback" placeholder="Feedback (optional)" class="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
              </div>
              <div class="flex gap-2">
                <button
                  class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
                  :disabled="store.isSaving || !gradeValue.trim()"
                  @click="confirmGrade(task.id)"
                >
                  <Check class="size-4" /> Save Grade
                </button>
                <button class="rounded-lg border border-slate-200 px-4 py-1.5 text-sm text-graphite hover:text-ink" @click="gradingTaskId = null">Cancel</button>
              </div>
            </div>

            <div v-else-if="task.status === 'submitted'" class="mt-4">
              <button
                class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-700 hover:bg-emerald-100 transition-colors"
                @click="startGrade(task.id)"
              >
                <Award class="size-4" /> Grade Task
              </button>
            </div>
          </div>
        </div>

        <!-- Installments tab -->
        <div v-else-if="activeTab === 'installments'" class="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <div v-if="!store.detail.installments.length" class="py-14 text-center text-sm text-graphite">
            No installment schedule set.
          </div>
          <PaymentDisclosureBanner v-else class="m-4 mb-0" />
          <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-graphite">
              <tr>
                <th class="px-3 py-2 text-left">Payment</th>
                <th class="px-3 py-2 text-left">Due</th>
                <th class="px-3 py-2 text-right">Amount</th>
                <th class="px-3 py-2 text-center">Status</th>
                <th class="px-3 py-2 text-left">Reference</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="inst in store.detail.installments" :key="inst.id">
                <td class="px-3 py-2.5 font-medium text-ink">{{ inst.label }}</td>
                <td class="px-3 py-2.5 text-graphite">{{ fmtDate(inst.due_date) }}</td>
                <td class="px-3 py-2.5 text-right font-bold text-ink">${{ inst.amount }}</td>
                <td class="px-3 py-2.5 text-center">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="installmentStatusClass(inst.status)">
                    {{ inst.status }}
                  </span>
                </td>
                <td class="px-3 py-2.5 font-mono text-xs text-graphite">{{ inst.payment_reference ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>

        <!-- Portal Access tab -->
        <div v-else-if="activeTab === 'portal'" class="rounded-lg border border-slate-200 bg-white p-6">
          <div class="flex items-center gap-2 mb-4">
            <Globe class="size-4 text-blue-600" />
            <h3 class="font-semibold text-ink">Portal / LMS Access</h3>
          </div>
          <div v-if="store.detail.portal_access" class="space-y-3 rounded-lg bg-slate-50 px-5 py-4 text-sm">
            <div class="flex items-center gap-3">
              <span class="w-36 shrink-0 text-graphite">Status</span>
              <span :class="store.detail.portal_access.enabled ? 'text-emerald-700 font-semibold' : 'text-graphite'">
                {{ store.detail.portal_access.enabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
            <div v-if="store.detail.portal_access.portal_url" class="flex items-center gap-3">
              <span class="w-36 shrink-0 text-graphite">URL</span>
              <a :href="store.detail.portal_access.portal_url" target="_blank" rel="noreferrer" class="flex items-center gap-1 text-berry hover:underline break-all">
                {{ store.detail.portal_access.portal_url }}
                <ExternalLink class="size-3 shrink-0" />
              </a>
            </div>
            <div v-if="store.detail.portal_access.username" class="flex items-center gap-3">
              <span class="w-36 shrink-0 text-graphite">Username</span>
              <span class="font-mono text-ink">{{ store.detail.portal_access.username }}</span>
            </div>
            <div v-if="store.detail.portal_access.password_hint" class="flex items-center gap-3">
              <span class="w-36 shrink-0 text-graphite">Password hint</span>
              <span class="text-ink">{{ store.detail.portal_access.password_hint }}</span>
            </div>
            <div v-if="store.detail.portal_access.notes" class="flex items-start gap-3">
              <span class="w-36 shrink-0 text-graphite">Notes</span>
              <span class="text-ink">{{ store.detail.portal_access.notes }}</span>
            </div>
            <div v-if="store.detail.portal_access.last_accessed_at" class="flex items-center gap-3 border-t border-slate-200 pt-3">
              <span class="w-36 shrink-0 text-graphite">Last accessed</span>
              <span class="text-graphite">{{ fmtDateTime(store.detail.portal_access.last_accessed_at) }}</span>
            </div>
          </div>
          <div v-else class="mt-4 rounded-lg border border-dashed border-slate-200 bg-slate-50 p-5 text-center">
            <p class="text-sm text-graphite">Portal access is not loaded.</p>
            <button
              class="focus-ring mt-3 inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
              :disabled="store.isSaving"
              @click="store.loadPortalAccess(store.detail.id).catch(() => undefined)"
            >
              {{ store.isSaving ? "Loading..." : "View access details" }}
            </button>
          </div>
        </div>

      </template>
    </div>

    <BaseModal
      :open="classActionDialog.open"
      :title="currentClassActionCopy?.title ?? 'Confirm class action'"
      :description="currentClassActionCopy?.description"
      size="md"
      @close="closeClassActionDialog"
    >
      <div v-if="store.detail && currentClassActionCopy" class="space-y-4">
        <div
          class="rounded-lg border px-4 py-3"
          :class="{
            'border-slate-200 bg-slate-50': currentClassActionCopy.tone === 'neutral',
            'border-emerald-200 bg-emerald-50': currentClassActionCopy.tone === 'success',
            'border-rose-200 bg-rose-50': currentClassActionCopy.tone === 'danger',
          }"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="font-semibold text-ink">{{ store.detail.reference }} · {{ store.detail.title }}</p>
              <p class="mt-1 text-xs text-graphite">
                Client {{ store.detail.client_username }} · Writer {{ store.detail.writer_username || "Unassigned" }}
              </p>
            </div>
            <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass(store.detail.status)">
              {{ statusLabel(store.detail.status) }}
            </span>
          </div>
          <div class="mt-3 grid gap-2 text-xs text-graphite sm:grid-cols-3">
            <span>Payment: {{ store.detail.payment_status }}</span>
            <span>Window: {{ fmtDate(store.detail.start_date) }} - {{ fmtDate(store.detail.end_date) }}</span>
            <span>{{ formatMoney(store.detail.total_price, store.detail.currency) }}</span>
          </div>
        </div>

        <label v-if="classActionDialog.action === 'assign_writer'" class="block text-sm font-medium text-ink">
          Writer ID <span class="text-rose-500">*</span>
          <input
            v-model.trim="classActionDialog.writerId"
            class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
            inputmode="numeric"
            placeholder="Enter writer ID"
          >
        </label>

        <div v-if="classActionDialog.action === 'manual_mark_paid'" class="grid gap-3 sm:grid-cols-2">
          <label class="block text-sm font-medium text-ink">
            Amount <span class="text-rose-500">*</span>
            <input
              v-model.trim="classActionDialog.amount"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              inputmode="decimal"
              placeholder="0.00"
            >
          </label>
          <label class="block text-sm font-medium text-ink">
            Transaction reference <span class="text-rose-500">*</span>
            <input
              v-model.trim="classActionDialog.transactionReference"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              placeholder="Gateway, bank, wallet, or receipt reference"
            >
          </label>
          <label class="block text-sm font-medium text-ink sm:col-span-2">
            Payment method
            <input
              v-model.trim="classActionDialog.paymentMethod"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              placeholder="Stripe, bank transfer, wallet, etc."
            >
          </label>
        </div>

        <label v-if="classActionDialog.action === 'cancel_class' || classActionDialog.action === 'manual_mark_paid'" class="block text-sm font-medium text-ink">
          {{ classActionDialog.action === "manual_mark_paid" ? "Verification note" : "Cancellation reason" }} <span class="text-rose-500">*</span>
          <textarea
            v-model.trim="classActionDialog.reason"
            class="focus-ring mt-1 min-h-24 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
            :placeholder="classActionDialog.action === 'manual_mark_paid' ? 'Record how the transaction was verified and who/what confirmed it...' : 'Explain why this class is being cancelled...'"
          />
          <span class="mt-1 block text-xs text-graphite">
            Minimum 10 characters. This note is retained for verification and audit.
          </span>
        </label>

        <div v-if="currentClassActionCopy.tone === 'danger'" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-800">
          Cancelling a class affects tasks, installments, writer work, and client visibility. Confirm after reviewing the class state.
        </div>
      </div>

      <template #footer>
        <div class="flex flex-wrap justify-end gap-2">
          <button
            class="focus-ring h-10 rounded-md border border-slate-200 px-4 text-sm font-semibold text-graphite hover:text-ink"
            type="button"
            @click="closeClassActionDialog"
          >
            Cancel
          </button>
          <button
            class="focus-ring h-10 rounded-md px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            :class="{
              'bg-ink hover:bg-slate-800': currentClassActionCopy?.tone === 'neutral',
              'bg-emerald-600 hover:bg-emerald-700': currentClassActionCopy?.tone === 'success',
              'bg-rose-600 hover:bg-rose-700': currentClassActionCopy?.tone === 'danger',
            }"
            type="button"
            :disabled="!classActionCanSubmit"
            @click="confirmClassActionDialog"
          >
            {{ store.isSaving ? "Working..." : currentClassActionCopy?.confirm }}
          </button>
        </div>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AlertCircle, ArrowLeft, Award, BookOpen, Calendar, Check, CircleDollarSign, ExternalLink, Globe, Lock, UserCheck, UserPlus, XCircle } from "@lucide/vue";
import { useClassesStore } from "@/stores/classes";
import { useAuthStore } from "@/stores/auth";
import PaymentDisclosureBanner from "@/components/payment/PaymentDisclosureBanner.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import type { ClassConfigOption, ClassPricingSnapshot, ClassStatus, ClassTaskStatus, InstallmentStatus } from "@/types/classes";

const route = useRoute();
const router = useRouter();
const store = useClassesStore();
const auth = useAuthStore();

// Support can view but cannot assign writers or modify the class — ops are admin-only.
const canManage = computed(() =>
  auth.role === "admin" || auth.role === "superadmin" || auth.isPreviewSession,
);

const showGuide = ref(false);

const classAvailableActions = computed(() => store.detail?.available_actions ?? []);
const classBlockedActions = computed(() => store.detail?.blocked_actions ?? []);
const isClassPaidForStaffing = computed(() =>
  store.detail?.status === "paid" && store.detail.payment_status === "paid",
);
const canAssignClassWriter = computed(() =>
  Boolean(canManage.value && store.detail && !store.detail.writer_username && isClassPaidForStaffing.value),
);
const canManualVerifyClassPayment = computed(() =>
  Boolean(
    store.detail
    && !["paid", "refunded"].includes(store.detail.payment_status)
    && !["completed", "cancelled", "archived"].includes(store.detail.status),
  ),
);

const CLASS_STATE_GUIDE = [
  { status: "draft", label: "Draft", client: "Finish request", writer: "-", staff: "Review once submitted" },
  { status: "submitted", label: "Submitted", client: "Wait for review", writer: "-", staff: "Review scope, request info, propose price" },
  { status: "price_proposed", label: "Price proposed", client: "Accept or negotiate", writer: "-", staff: "Revise proposal if needed" },
  { status: "pending_payment", label: "Pending payment", client: "Pay deposit/full amount", writer: "-", staff: "Monitor payment" },
  { status: "paid", label: "Paid", client: "Wait for staffing", writer: "-", staff: "Assign writer, configure tasks" },
  { status: "assigned", label: "Assigned", client: "Track progress", writer: "Start class work", staff: "Reassign or support writer" },
  { status: "active", label: "Active", client: "Submit class materials", writer: "Work tasks", staff: "Cancel, grade tasks, manage installments" },
  { status: "quality_review", label: "Quality review", client: "Wait for QA", writer: "Respond to revisions", staff: "Approve, return task, grade" },
  { status: "completed", label: "Completed", client: "Review final work", writer: "-", staff: "Archive or support follow-up" },
  { status: "cancelled", label: "Cancelled", client: "-", writer: "-", staff: "No lifecycle action" },
];

onMounted(() => store.loadDetail(route.params.id as string));

const tabs = [
  { key: "tasks", label: "Tasks" },
  { key: "installments", label: "Installments" },
  { key: "portal", label: "Portal Access" },
];
const activeTab = ref("tasks");

const statusLabels: Partial<Record<ClassStatus, string>> = {
  draft: "Draft",
  submitted: "Submitted",
  needs_client_info: "Needs Info",
  under_review: "Under Review",
  price_proposed: "Price Proposed",
  negotiating: "Negotiating",
  accepted: "Accepted",
  pending_payment: "Pending Payment",
  partially_paid: "Partially Paid",
  paid: "Paid",
  assigned: "Assigned",
  in_progress: "In Progress",
  pending: "Pending Review",
  active: "Active",
  paused: "Paused",
  quality_review: "Quality Review",
  completed: "Completed",
  cancelled: "Cancelled",
  archived: "Archived",
};

const statusClasses: Partial<Record<ClassStatus, string>> = {
  draft: "bg-slate-100 text-graphite",
  submitted: "bg-blue-100 text-blue-700",
  needs_client_info: "bg-amber-100 text-amber-700",
  under_review: "bg-violet-100 text-violet-700",
  price_proposed: "bg-blue-100 text-blue-700",
  negotiating: "bg-amber-100 text-amber-700",
  accepted: "bg-emerald-100 text-emerald-700",
  pending_payment: "bg-amber-100 text-amber-700",
  partially_paid: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  assigned: "bg-blue-100 text-blue-700",
  in_progress: "bg-berry/10 text-berry",
  pending: "bg-amber-100 text-amber-700",
  active: "bg-emerald-100 text-emerald-700",
  paused: "bg-slate-100 text-graphite",
  quality_review: "bg-purple-100 text-purple-700",
  completed: "bg-blue-100 text-blue-700",
  cancelled: "bg-rose-100 text-rose-700",
  archived: "bg-slate-100 text-slate-400",
};

const taskStatusLabels: Partial<Record<ClassTaskStatus, string>> = {
  pending: "Pending",
  assigned: "Assigned",
  in_progress: "In Progress",
  submitted: "Submitted",
  revision_requested: "Revision",
  approved: "Approved",
  completed: "Completed",
  cancelled: "Cancelled",
};

const taskStatusClasses: Partial<Record<ClassTaskStatus, string>> = {
  pending: "bg-slate-100 text-graphite",
  assigned: "bg-blue-100 text-blue-700",
  in_progress: "bg-amber-100 text-amber-700",
  submitted: "bg-purple-100 text-purple-700",
  revision_requested: "bg-rose-100 text-rose-700",
  approved: "bg-emerald-100 text-emerald-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
};

const installmentStatusClasses: Partial<Record<InstallmentStatus, string>> = {
  pending: "bg-amber-100 text-amber-700",
  due: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  overdue: "bg-rose-100 text-rose-700",
  waived: "bg-slate-100 text-graphite",
  cancelled: "bg-slate-100 text-slate-400",
};

function labelize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function statusLabel(status: ClassStatus): string {
  return statusLabels[status] ?? labelize(status);
}

function statusClass(status: ClassStatus): string {
  return statusClasses[status] ?? "bg-slate-100 text-graphite";
}

function taskStatusLabel(status: ClassTaskStatus): string {
  return taskStatusLabels[status] ?? labelize(status);
}

function taskStatusClass(status: ClassTaskStatus): string {
  return taskStatusClasses[status] ?? "bg-slate-100 text-graphite";
}

function installmentStatusClass(status: InstallmentStatus): string {
  return installmentStatusClasses[status] ?? "bg-slate-100 text-graphite";
}

function formatMoney(amount: string | number, currency = "USD"): string {
  const numeric = Number(amount);
  if (!Number.isFinite(numeric)) return `${currency} ${amount}`;
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

const progressPct = computed(() => {
  const d = store.detail;
  if (!d || !d.total_tasks) return 0;
  return Math.round((d.completed_tasks / d.total_tasks) * 100);
});

const pricingSnapshot = computed<ClassPricingSnapshot | null>(() => {
  const snapshot = store.detail?.pricing_snapshot;
  return snapshot && Object.keys(snapshot).length ? snapshot : null;
});

const snapshotTasks = computed<ClassConfigOption[]>(() =>
  pricingSnapshot.value?.selected_tasks ?? [],
);

const snapshotPricingLabel = computed(() => {
  const snapshot = pricingSnapshot.value;
  if (!snapshot) return "";
  const currency = snapshot.currency || store.detail?.currency || "USD";
  const basePrice = Number(snapshot.base_price || 0);
  const quoteHours = snapshot.payment_policy?.quote_expiry_hours;
  if (snapshot.pricing_mode === "package" && basePrice > 0) {
    return `Package estimate starts at ${formatMoney(basePrice, currency)}.`;
  }
  if (quoteHours) return `Quote after review, valid for ${quoteHours} hours.`;
  return "Quote after review.";
});

// Grading
const gradingTaskId = ref<number | null>(null);
const gradeValue = ref("");
const gradeFeedback = ref("");

function startGrade(taskId: number) {
  gradingTaskId.value = taskId;
  gradeValue.value = "";
  gradeFeedback.value = "";
}

async function confirmGrade(taskId: number) {
  if (!store.detail) return;
  await store.gradeTask(store.detail.id, taskId, { grade: gradeValue.value, grade_feedback: gradeFeedback.value });
  gradingTaskId.value = null;
}

type ClassAction = "assign_writer" | "manual_mark_paid" | "cancel_class";

const classActionDialog = reactive({
  open: false,
  action: null as ClassAction | null,
  writerId: "",
  amount: "",
  transactionReference: "",
  paymentMethod: "",
  reason: "",
});

const classActionCopy: Record<ClassAction, { title: string; description: string; confirm: string; tone: "neutral" | "success" | "danger" }> = {
  assign_writer: {
    title: "Assign writer",
    description: "Attach this class to a writer and move the work into a clearer ownership state.",
    confirm: "Assign writer",
    tone: "neutral",
  },
  manual_mark_paid: {
    title: "Verify class payment",
    description: "Apply a manually verified payment that did not reflect automatically. Transaction reference and audit note are required.",
    confirm: "Verify payment",
    tone: "success",
  },
  cancel_class: {
    title: "Cancel class",
    description: "Cancel the class after reviewing the client, writer, installment, and task state.",
    confirm: "Cancel class",
    tone: "danger",
  },
};

const currentClassActionCopy = computed(() =>
  classActionDialog.action ? classActionCopy[classActionDialog.action] : null,
);

const classActionCanSubmit = computed(() => {
  if (store.isSaving || !classActionDialog.action) return false;
  if (classActionDialog.action === "assign_writer") return canAssignClassWriter.value && Number(classActionDialog.writerId) > 0;
  if (classActionDialog.action === "manual_mark_paid") {
    return canManualVerifyClassPayment.value
      && Number(classActionDialog.amount) > 0
      && classActionDialog.transactionReference.trim().length >= 4
      && classActionDialog.reason.trim().length >= 10;
  }
  if (classActionDialog.action === "cancel_class") return classActionDialog.reason.trim().length >= 10;
  return false;
});

function openClassActionDialog(action: ClassAction) {
  classActionDialog.open = true;
  classActionDialog.action = action;
  classActionDialog.writerId = "";
  classActionDialog.amount = action === "manual_mark_paid" ? String(store.detail?.total_price ?? "") : "";
  classActionDialog.transactionReference = "";
  classActionDialog.paymentMethod = "";
  classActionDialog.reason = "";
}

function closeClassActionDialog() {
  classActionDialog.open = false;
  classActionDialog.action = null;
  classActionDialog.writerId = "";
  classActionDialog.amount = "";
  classActionDialog.transactionReference = "";
  classActionDialog.paymentMethod = "";
  classActionDialog.reason = "";
}

async function confirmClassActionDialog() {
  if (!store.detail || !classActionCanSubmit.value || !classActionDialog.action) return;
  if (classActionDialog.action === "assign_writer") {
    await store.assignWriter(store.detail.id, Number(classActionDialog.writerId));
  } else if (classActionDialog.action === "manual_mark_paid") {
    await store.manualVerifyPayment(store.detail.id, {
      amount: classActionDialog.amount,
      transaction_reference: classActionDialog.transactionReference.trim(),
      verification_note: classActionDialog.reason.trim(),
      payment_method: classActionDialog.paymentMethod.trim(),
    });
  } else if (classActionDialog.action === "cancel_class") {
    await store.cancelClass(store.detail.id, classActionDialog.reason.trim());
  }
  closeClassActionDialog();
}

function fmtDate(v: string): string {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}

function fmtDateTime(v: string): string {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}
</script>
