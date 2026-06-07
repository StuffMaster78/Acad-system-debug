<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-5xl space-y-4">

      <div v-if="store.isLoadingDetail" class="py-24 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else-if="store.detail">
        <!-- Back + header -->
        <div>
          <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
            <ArrowLeft class="size-3.5" /> Special Orders
          </button>
          <div class="rounded-lg border border-slate-200 bg-white p-6">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass[store.detail.status] ?? 'bg-slate-100 text-graphite'">
                    {{ statusLabel[store.detail.status] ?? store.detail.status.replace(/_/g, ' ') }}
                  </span>
                  <span class="font-mono text-xs text-graphite">{{ store.detail.reference }}</span>
                </div>
                <h1 class="mt-2 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
                <p class="mt-1 text-sm leading-5 text-graphite">{{ store.detail.inquiry_details || store.detail.description }}</p>
                <div class="mt-3 flex flex-wrap items-center gap-4 text-xs text-graphite">
                  <span v-if="store.detail.duration_days">{{ store.detail.duration_days }} day turnaround</span>
                  <span class="flex items-center gap-1.5">
                    <UserCheck class="size-3.5" />
                    Client: <strong class="ml-0.5 text-ink">{{ store.detail.client_username }}</strong>
                  </span>
                  <span v-if="store.detail.writer_username" class="flex items-center gap-1.5 text-emerald-700">
                    <Check class="size-3.5" />
                    Writer: {{ store.detail.writer_username }}
                  </span>
                  <span v-else class="flex items-center gap-1.5 text-amber-600">
                    <AlertCircle class="size-3.5" />
                    No writer assigned
                  </span>
                  <span v-if="store.detail.attachments_count > 0" class="flex items-center gap-1.5">
                    <Paperclip class="size-3.5" />
                    {{ store.detail.attachments_count }} attachment{{ store.detail.attachments_count !== 1 ? 's' : '' }}
                  </span>
                </div>
              </div>
              <div class="shrink-0 text-right">
                <p v-if="store.detail.quoted_price" class="text-2xl font-bold text-ink">${{ store.detail.quoted_price }}</p>
                <p v-else class="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">No quote yet</p>
                <p v-if="store.detail.quoted_price" class="mt-0.5 text-xs text-graphite">Latest quoted amount</p>
              </div>
            </div>

            <!-- Milestone progress -->
            <div v-if="store.detail.total_milestones > 0" class="mt-5">
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span class="text-graphite">{{ store.detail.completed_milestones }}/{{ store.detail.total_milestones }} milestones</span>
                <span class="font-semibold text-ink">{{ milestonePct }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full bg-berry transition-all duration-500"
                  :style="{ width: `${milestonePct}%` }"
                />
              </div>
            </div>

            <!-- Admin lifecycle actions (hidden from support/editor who are view-only) -->
            <div class="mt-5 border-t border-slate-100 pt-4">
              <div class="flex flex-wrap items-center gap-2">
                <button
                  v-if="canManage && canAssignSpecialWriter"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
                  :disabled="store.isSaving"
                  type="button"
                  @click="openSpecialActionDialog('assign_writer')"
                >
                  <UserPlus class="size-3.5" />
                  Assign Writer
                </button>
                <button
                  v-if="canManage && canManualVerifySpecialPayment"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 disabled:opacity-60"
                  :disabled="store.isSaving"
                  type="button"
                  @click="openSpecialActionDialog('manual_mark_paid')"
                >
                  <CircleDollarSign class="size-3.5" />
                  Verify Payment
                </button>
                <button
                  v-if="canManage && hasSpecialAction('create_quote', ['inquiry', 'quote_pending', 'quote_sent'].includes(store.detail.status))"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
                  type="button"
                  @click="store.showQuoteForm = !store.showQuoteForm"
                >
                  <FileText class="size-3.5" />
                  {{ store.showQuoteForm ? 'Cancel Quote' : 'Create Quote' }}
                </button>
                <button
                  v-if="canManage && hasSpecialAction('complete_order', ['in_progress', 'submitted', 'ready_for_delivery'].includes(store.detail.status))"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 disabled:opacity-60"
                  :disabled="store.isSaving"
                  type="button"
                  @click="openSpecialActionDialog('complete_order')"
                >
                  <CheckCircle class="size-3.5" />
                  Mark Complete
                </button>
                <button
                  v-if="canManage && hasSpecialAction('cancel_order', !['completed', 'cancelled', 'approved', 'refunded'].includes(store.detail.status))"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-60"
                  :disabled="store.isSaving"
                  type="button"
                  @click="openSpecialActionDialog('cancel_order')"
                >
                  <XCircle class="size-3.5" />
                  Cancel Order
                </button>
                <button
                  class="ml-auto inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50 hover:text-ink"
                  type="button"
                  @click="showGuide = !showGuide"
                >
                  <BookOpen class="size-3.5" />
                  {{ showGuide ? "Hide guide" : "State guide" }}
                </button>
              </div>

              <p v-if="canManage && !specialAvailableActions.length" class="mt-3 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-graphite">
                No direct special-order action is available for this status.
              </p>

              <div v-if="specialBlockedActions.length" class="mt-3 space-y-1.5">
                <div
                  v-for="item in specialBlockedActions"
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
                    <tr v-for="row in SPECIAL_STATE_GUIDE" :key="row.status">
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
            <p class="text-xs text-graphite">Quoted price</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.quoted_price ? `$${store.detail.quoted_price}` : '—' }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Milestones</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.completed_milestones }}<span class="text-sm font-normal text-graphite">/{{ store.detail.total_milestones }}</span></p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Funding milestones</p>
            <p class="mt-1 text-sm font-semibold text-graphite">{{ store.detail.total_milestones ? 'Tracked per milestone' : 'Not generated' }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Quotes submitted</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.quotes.length }}</p>
          </div>
        </div>

        <!-- Quote creation form -->
        <div v-if="store.showQuoteForm" class="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
          <h3 class="font-semibold text-ink">New Quote</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-graphite mb-1">Total Price *</label>
              <input v-model="store.quoteForm.price" placeholder="e.g. 850.00" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
            </div>
            <div>
              <label class="block text-xs font-medium text-graphite mb-1">Valid Until</label>
              <input v-model="store.quoteForm.valid_until" type="date" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-graphite mb-1">Notes for client</label>
            <textarea v-model="(store.quoteForm.notes as string)" rows="3" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring resize-none" />
          </div>

          <!-- Milestones -->
          <div>
            <div class="mb-2 flex items-center justify-between">
              <label class="text-xs font-semibold text-graphite uppercase tracking-wide">Milestones</label>
              <button class="text-xs font-medium text-berry hover:underline" @click="addMilestone">+ Add milestone</button>
            </div>
            <div class="space-y-2">
              <div v-for="(m, i) in store.quoteForm.milestones" :key="i" class="flex items-center gap-2">
                <input v-model="m.label" placeholder="Milestone label" class="flex-1 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <input v-model="m.due_date" type="date" class="w-36 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <input v-model="m.price" placeholder="Price" class="w-24 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <button class="text-rose-400 hover:text-rose-600 text-sm" @click="removeMilestone(i)"></button>
              </div>
            </div>
          </div>

          <div class="flex gap-2 pt-1">
            <button
              class="inline-flex items-center gap-1.5 rounded-lg bg-berry px-5 py-2 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60"
              :disabled="store.isSaving || !store.quoteForm.price"
              @click="handleSubmitQuote"
            >
              <Check class="size-4" /> Send Quote to Client
            </button>
            <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm text-graphite hover:text-ink" @click="store.showQuoteForm = false">
              Discard
            </button>
          </div>
        </div>

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

        <!-- Milestones tab -->
        <div v-if="activeTab === 'milestones'" class="space-y-3">
          <div v-if="!store.detail.milestones.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            Milestones will appear after a quote is accepted by the client.
          </div>
          <div
            v-for="m in store.detail.milestones"
            :key="m.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs text-graphite">#{{ m.sequence }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="milestoneStatusClass[m.status] ?? 'bg-slate-100 text-graphite'">
                    {{ m.status.replace(/_/g, " ") }}
                  </span>
                </div>
                <h3 class="mt-1.5 font-semibold text-ink">{{ m.label }}</h3>
                <p v-if="m.description" class="mt-0.5 text-sm text-graphite">{{ m.description }}</p>
                <p v-if="m.writer_username" class="mt-1 text-xs text-graphite">
                  Writer: <span class="font-medium text-ink">{{ m.writer_username }}</span>
                </p>
              </div>
              <div class="shrink-0 text-right">
                <p v-if="m.price" class="font-bold text-ink">${{ m.price }}</p>
                <p v-if="m.due_date" class="mt-0.5 text-xs text-graphite">Due {{ fmtDate(m.due_date) }}</p>
              </div>
            </div>

            <div v-if="m.delivery_notes" class="mt-3 rounded-lg bg-slate-50 px-4 py-2.5 text-sm text-graphite">
              <span class="font-medium text-ink">Delivery notes:</span> {{ m.delivery_notes }}
            </div>
            <div v-if="m.revision_notes" class="mt-2 rounded-lg border border-rose-100 bg-rose-50 px-4 py-2.5 text-sm text-rose-700">
              <span class="font-medium">Revision requested:</span> {{ m.revision_notes }}
            </div>

            <div v-if="m.deliverable_status === 'uploaded'" class="mt-4">
              <button
                class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-sm font-semibold text-emerald-700 hover:bg-emerald-100 disabled:opacity-60 transition-colors"
                :disabled="approvingId === m.id || store.isSaving"
                @click="openSpecialActionDialog('approve_milestone', m)"
              >
                <CheckCircle class="size-4" />
                {{ approvingId === m.id ? 'Approving…' : 'Approve Milestone' }}
              </button>
            </div>

            <div v-if="m.delivered_at || m.approved_at" class="mt-3 flex flex-wrap gap-4 border-t border-slate-100 pt-3 text-xs text-graphite">
              <span v-if="m.delivered_at">Delivered {{ fmtDateTime(m.delivered_at) }}</span>
              <span v-if="m.approved_at" class="text-emerald-700">Approved {{ fmtDateTime(m.approved_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Quotes tab -->
        <div v-else-if="activeTab === 'quotes'" class="space-y-3">
          <div v-if="!store.detail.quotes.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            No quotes submitted yet.
          </div>
          <div
            v-for="q in store.detail.quotes"
            :key="q.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xl font-bold text-ink">${{ q.price }}</p>
                <p class="mt-0.5 text-xs text-graphite">By {{ q.created_by }} · {{ fmtDateTime(q.created_at) }}</p>
                <p v-if="q.valid_until" class="text-xs text-graphite">Valid until {{ fmtDate(q.valid_until) }}</p>
              </div>
              <span
                class="rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize"
                :class="{
                  'bg-emerald-100 text-emerald-700': q.status === 'accepted',
                  'bg-rose-100 text-rose-700': q.status === 'rejected',
                  'bg-blue-100 text-blue-700': q.status === 'sent',
                  'bg-slate-100 text-graphite': ['draft', 'superseded'].includes(q.status),
                }"
              >{{ q.status }}</span>
            </div>
            <p v-if="q.notes" class="mt-3 text-sm text-graphite">{{ q.notes }}</p>
            <p v-if="q.rejection_reason" class="mt-2 text-sm text-rose-600">Client reason: {{ q.rejection_reason }}</p>

            <div v-if="q.milestones_preview.length" class="mt-4 space-y-1.5 border-t border-slate-100 pt-3">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Milestones</p>
              <div v-for="(mp, i) in q.milestones_preview" :key="i" class="flex items-center justify-between text-sm">
                <span class="text-graphite">{{ mp.label }}</span>
                <span class="font-medium text-ink">${{ mp.price }} · {{ fmtDate(mp.due_date) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Access notes tab -->
        <div v-else-if="activeTab === 'access'" class="rounded-lg border border-slate-200 bg-white p-6">
          <div class="flex items-center gap-2 mb-4">
            <Lock class="size-4 text-graphite" />
            <h3 class="font-semibold text-ink">Sensitive Access Information</h3>
          </div>
          <div v-if="store.detail.sensitive_access" class="space-y-3 rounded-lg bg-slate-50 px-5 py-4 text-sm">
            <div v-if="store.detail.sensitive_access.portal_url" class="flex items-start gap-3">
              <span class="w-36 shrink-0 text-graphite">Portal URL</span>
              <span class="font-mono text-ink break-all">{{ store.detail.sensitive_access.portal_url }}</span>
            </div>
            <div v-if="store.detail.sensitive_access.credentials_hint" class="flex items-start gap-3">
              <span class="w-36 shrink-0 text-graphite">Credentials</span>
              <span class="text-ink">{{ store.detail.sensitive_access.credentials_hint }}</span>
            </div>
            <div v-if="store.detail.sensitive_access.notes" class="flex items-start gap-3">
              <span class="w-36 shrink-0 text-graphite">Notes</span>
              <span class="text-ink">{{ store.detail.sensitive_access.notes }}</span>
            </div>
            <p
              v-if="!store.detail.sensitive_access.portal_url && !store.detail.sensitive_access.credentials_hint && !store.detail.sensitive_access.notes"
              class="text-graphite"
            >
              No access information recorded for this order.
            </p>
          </div>
          <p v-else class="mt-2 text-sm text-graphite">No access information provided.</p>
        </div>

      </template>
    </div>

    <BaseModal
      :open="specialActionDialog.open"
      :title="currentSpecialActionCopy?.title ?? 'Confirm special-order action'"
      :description="currentSpecialActionCopy?.description"
      size="md"
      @close="closeSpecialActionDialog"
    >
      <div v-if="store.detail && currentSpecialActionCopy" class="space-y-4">
        <div
          class="rounded-lg border px-4 py-3"
          :class="{
            'border-slate-200 bg-slate-50': currentSpecialActionCopy.tone === 'neutral',
            'border-emerald-200 bg-emerald-50': currentSpecialActionCopy.tone === 'success',
            'border-rose-200 bg-rose-50': currentSpecialActionCopy.tone === 'danger',
          }"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="font-semibold text-ink">{{ store.detail.reference }} · {{ store.detail.title }}</p>
              <p class="mt-1 text-xs text-graphite">
                Client {{ store.detail.client_username || "External" }} · Writer {{ store.detail.writer_username || "Unassigned" }}
              </p>
            </div>
            <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass[store.detail.status] ?? 'bg-slate-100 text-graphite'">
              {{ statusLabel[store.detail.status] ?? labelize(store.detail.status) }}
            </span>
          </div>
          <div class="mt-3 grid gap-2 text-xs text-graphite sm:grid-cols-3">
            <span>Quote: {{ store.detail.quoted_price ? formatMoney(store.detail.quoted_price, store.detail.currency) : "Not quoted" }}</span>
            <span>Milestones: {{ store.detail.completed_milestones }}/{{ store.detail.total_milestones }}</span>
            <span>Turnaround: {{ store.detail.duration_days ? `${store.detail.duration_days} days` : "Not set" }}</span>
          </div>
        </div>

        <div v-if="specialActionDialog.milestone" class="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm">
          <p class="font-semibold text-ink">Milestone #{{ specialActionDialog.milestone.sequence }}: {{ specialActionDialog.milestone.label }}</p>
          <p v-if="specialActionDialog.milestone.description" class="mt-1 text-graphite">{{ specialActionDialog.milestone.description }}</p>
          <div class="mt-3 grid gap-2 text-xs text-graphite sm:grid-cols-3">
            <span>Amount: {{ specialActionDialog.milestone.price ? formatMoney(specialActionDialog.milestone.price, specialActionDialog.milestone.currency) : "Not priced" }}</span>
            <span>Due: {{ fmtDate(specialActionDialog.milestone.due_date) }}</span>
            <span>Status: {{ labelize(specialActionDialog.milestone.deliverable_status || specialActionDialog.milestone.status) }}</span>
          </div>
        </div>

        <label v-if="specialActionDialog.action === 'assign_writer'" class="block text-sm font-medium text-ink">
          Writer ID <span class="text-rose-500">*</span>
          <input
            v-model.trim="specialActionDialog.writerId"
            class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
            inputmode="numeric"
            placeholder="Enter writer ID"
          >
        </label>

        <div v-if="specialActionDialog.action === 'manual_mark_paid'" class="grid gap-3 sm:grid-cols-2">
          <label class="block text-sm font-medium text-ink">
            Amount <span class="text-rose-500">*</span>
            <input
              v-model.trim="specialActionDialog.amount"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              inputmode="decimal"
              placeholder="0.00"
            >
          </label>
          <label class="block text-sm font-medium text-ink">
            Transaction reference <span class="text-rose-500">*</span>
            <input
              v-model.trim="specialActionDialog.transactionReference"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              placeholder="Gateway, bank, wallet, or receipt reference"
            >
          </label>
          <label class="block text-sm font-medium text-ink sm:col-span-2">
            Payment method
            <input
              v-model.trim="specialActionDialog.paymentMethod"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              placeholder="Stripe, bank transfer, wallet, etc."
            >
          </label>
        </div>

        <label v-if="specialActionDialog.action === 'cancel_order' || specialActionDialog.action === 'manual_mark_paid'" class="block text-sm font-medium text-ink">
          {{ specialActionDialog.action === "manual_mark_paid" ? "Verification note" : "Cancellation reason" }} <span class="text-rose-500">*</span>
          <textarea
            v-model.trim="specialActionDialog.reason"
            class="focus-ring mt-1 min-h-24 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
            :placeholder="specialActionDialog.action === 'manual_mark_paid' ? 'Record how the transaction was verified and who/what confirmed it...' : 'Explain why this special order is being cancelled...'"
          />
          <span class="mt-1 block text-xs text-graphite">
            Minimum 10 characters. This keeps the finance and operations trail clear.
          </span>
        </label>

        <div v-if="currentSpecialActionCopy.tone === 'danger'" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-800">
          This action can affect quotes, milestones, deposits, writer assignment, and client visibility. Confirm only after reviewing the current state.
        </div>
      </div>

      <template #footer>
        <div class="flex flex-wrap justify-end gap-2">
          <button
            class="focus-ring h-10 rounded-md border border-slate-200 px-4 text-sm font-semibold text-graphite hover:text-ink"
            type="button"
            @click="closeSpecialActionDialog"
          >
            Cancel
          </button>
          <button
            class="focus-ring h-10 rounded-md px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            :class="{
              'bg-ink hover:bg-slate-800': currentSpecialActionCopy?.tone === 'neutral',
              'bg-emerald-600 hover:bg-emerald-700': currentSpecialActionCopy?.tone === 'success',
              'bg-rose-600 hover:bg-rose-700': currentSpecialActionCopy?.tone === 'danger',
            }"
            type="button"
            :disabled="!specialActionCanSubmit"
            @click="confirmSpecialActionDialog"
          >
            {{ store.isSaving ? "Working..." : currentSpecialActionCopy?.confirm }}
          </button>
        </div>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AlertCircle, ArrowLeft, BookOpen, Check, CheckCircle, CircleDollarSign, FileText, Lock, Paperclip, UserCheck, UserPlus, XCircle } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import { specialOrdersApi } from "@/api/specialOrders";
import { useAuthStore } from "@/stores/auth";
import BaseModal from "@/components/ui/BaseModal.vue";
import type { MilestoneStatus, SpecialOrderMilestone, SpecialOrderStatus } from "@/types/specialOrders";

const route = useRoute();
const router = useRouter();
const store = useSpecialOrdersStore();
const auth = useAuthStore();

// Support can view but cannot assign, approve, or cancel — ops are admin-only.
const canManage = computed(() =>
  auth.role === "admin" || auth.role === "superadmin" || auth.isPreviewSession,
);

const showGuide = ref(false);
const specialAvailableActions = computed(() => store.detail?.available_actions ?? []);
const specialBlockedActions = computed(() => store.detail?.blocked_actions ?? []);
const isSpecialFundedForStaffing = computed(() =>
  store.detail?.status === "ready_for_staffing" || (store.detail?.status === "assigned" && !store.detail.writer_username),
);
const canAssignSpecialWriter = computed(() =>
  Boolean(
    canManage.value
    && store.detail
    && !store.detail.writer_username
    && isSpecialFundedForStaffing.value
    && hasSpecialAction("assign_writer", store.detail.status === "ready_for_staffing"),
  ),
);
const canManualVerifySpecialPayment = computed(() =>
  Boolean(
    canManage.value
    && store.detail
    && !["ready_for_staffing", "assigned", "in_progress", "submitted", "ready_for_delivery", "completed", "approved", "cancelled", "refunded"].includes(store.detail.status)
    && hasSpecialAction(
      "manual_mark_paid",
      ["quote_accepted", "awaiting_payment", "partially_funded"].includes(store.detail.status),
    ),
  ),
);

const SPECIAL_STATE_GUIDE = [
  { status: "inquiry", label: "Inquiry", client: "Submit scope", writer: "-", staff: "Create quote, hold, cancel" },
  { status: "quote_sent", label: "Quote sent", client: "Accept or reject quote", writer: "-", staff: "Revise quote, hold, cancel" },
  { status: "awaiting_payment", label: "Awaiting payment", client: "Pay deposit/full quote", writer: "-", staff: "Monitor payment" },
  { status: "ready_for_staffing", label: "Ready for staffing", client: "Wait for assignment", writer: "-", staff: "Assign writer, hold, cancel" },
  { status: "assigned", label: "Assigned", client: "Track progress", writer: "Start work", staff: "Start work, hold, cancel" },
  { status: "in_progress", label: "In progress", client: "Track milestones", writer: "Submit work", staff: "Hold, cancel, manage milestones" },
  { status: "submitted", label: "Submitted", client: "Review delivery", writer: "-", staff: "Complete, request revision, hold" },
  { status: "ready_for_delivery", label: "Ready for delivery", client: "Review delivery", writer: "-", staff: "Complete, request revision" },
  { status: "completed", label: "Completed", client: "Approve or request revision", writer: "-", staff: "Approve, request revision" },
  { status: "cancelled", label: "Cancelled", client: "-", writer: "-", staff: "No lifecycle action" },
];

function labelize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function hasSpecialAction(action: string, fallback = false) {
  if (specialAvailableActions.value.length) return specialAvailableActions.value.includes(action);
  return fallback;
}

onMounted(() => store.loadDetail(route.params.id as string));

const tabs = [
  { key: "milestones", label: "Milestones" },
  { key: "quotes", label: "Quotes" },
  { key: "access", label: "Access Notes" },
];
const activeTab = ref("milestones");

const statusLabel: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "Inquiry",
  quote_pending: "Awaiting Quote",
  quote_sent: "Quote Sent",
  quote_accepted: "Quote Accepted",
  awaiting_payment: "Awaiting Payment",
  partially_funded: "Partially Funded",
  ready_for_staffing: "Ready for Staffing",
  assigned: "Assigned",
  on_hold: "On Hold",
  submitted: "Submitted",
  in_progress: "In Progress",
  ready_for_delivery: "Ready for Delivery",
  completed: "Completed",
  cancelled: "Cancelled",
  approved: "Approved",
  revision_requested: "Revision Requested",
  on_revision: "On Revision",
  refunded: "Refunded",
};

const statusClass: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "bg-slate-100 text-graphite",
  quote_pending: "bg-amber-100 text-amber-700",
  quote_sent: "bg-blue-100 text-blue-700",
  quote_accepted: "bg-emerald-100 text-emerald-700",
  awaiting_payment: "bg-amber-100 text-amber-700",
  partially_funded: "bg-amber-100 text-amber-700",
  ready_for_staffing: "bg-blue-100 text-blue-700",
  assigned: "bg-blue-100 text-blue-700",
  on_hold: "bg-slate-100 text-graphite",
  submitted: "bg-purple-100 text-purple-700",
  in_progress: "bg-purple-100 text-purple-700",
  ready_for_delivery: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
  approved: "bg-emerald-100 text-emerald-700",
  revision_requested: "bg-rose-100 text-rose-700",
  on_revision: "bg-amber-100 text-amber-700",
  refunded: "bg-slate-100 text-slate-400",
};

const milestoneStatusClass: Partial<Record<MilestoneStatus, string>> = {
  pending: "bg-slate-100 text-graphite",
  partially_paid: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  overdue: "bg-rose-100 text-rose-700",
  cancelled: "bg-slate-100 text-slate-400",
  refunded: "bg-slate-100 text-slate-400",
};

const milestonePct = computed(() => {
  const d = store.detail;
  if (!d || !d.total_milestones) return 0;
  return Math.round((d.completed_milestones / d.total_milestones) * 100);
});

function formatMoney(amount: string | number, currency = "USD"): string {
  const numeric = Number(amount);
  if (!Number.isFinite(numeric)) return `${currency} ${amount}`;
  return new Intl.NumberFormat("en", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

const specialOutstandingAmount = computed(() => {
  const detail = store.detail;
  if (!detail) return "";
  const milestoneBalance = detail.milestones.reduce((total, milestone) => {
    const balance = Number(milestone.balance_amount ?? milestone.amount_due ?? 0);
    return Number.isFinite(balance) ? total + balance : total;
  }, 0);
  if (milestoneBalance > 0) return milestoneBalance.toFixed(2);
  const quoted = Number(detail.quoted_price ?? 0);
  return Number.isFinite(quoted) && quoted > 0 ? quoted.toFixed(2) : "";
});

// Quote
function addMilestone() {
  store.quoteForm.milestones.push({ label: "", due_date: "", price: "" });
}
function removeMilestone(i: number) {
  store.quoteForm.milestones.splice(i, 1);
}
async function handleSubmitQuote() {
  if (!store.detail) return;
  await store.submitQuote(store.detail.id);
}

// Milestone approval
const approvingId = ref<number | null>(null);

function fmtDate(v: string | null): string {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}

function fmtDateTime(v: string | null): string {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

type SpecialAction = "assign_writer" | "manual_mark_paid" | "complete_order" | "cancel_order" | "approve_milestone";

const specialActionDialog = reactive({
  open: false,
  action: null as SpecialAction | null,
  writerId: "",
  amount: "",
  transactionReference: "",
  paymentMethod: "",
  reason: "",
  milestone: null as SpecialOrderMilestone | null,
});

const specialActionCopy: Record<SpecialAction, { title: string; description: string; confirm: string; tone: "neutral" | "success" | "danger" }> = {
  assign_writer: {
    title: "Assign writer",
    description: "Assign this special order to a writer after confirming the quote, scope, and current state.",
    confirm: "Assign writer",
    tone: "neutral",
  },
  manual_mark_paid: {
    title: "Verify special-order payment",
    description: "Apply a verified external payment that did not reflect automatically. Transaction reference and audit note are required.",
    confirm: "Verify payment",
    tone: "success",
  },
  complete_order: {
    title: "Mark special order complete",
    description: "Close the active special-order workflow after confirming all deliverables are ready for the client.",
    confirm: "Mark complete",
    tone: "success",
  },
  cancel_order: {
    title: "Cancel special order",
    description: "Cancel this special order and keep a clear reason for the operational and finance trail.",
    confirm: "Cancel order",
    tone: "danger",
  },
  approve_milestone: {
    title: "Approve milestone",
    description: "Approve the uploaded deliverable for this milestone and update the milestone progress.",
    confirm: "Approve milestone",
    tone: "success",
  },
};

const currentSpecialActionCopy = computed(() =>
  specialActionDialog.action ? specialActionCopy[specialActionDialog.action] : null,
);

const specialActionCanSubmit = computed(() => {
  if (store.isSaving || !specialActionDialog.action) return false;
  if (specialActionDialog.action === "assign_writer") return canAssignSpecialWriter.value && Number(specialActionDialog.writerId) > 0;
  if (specialActionDialog.action === "manual_mark_paid") {
    return canManualVerifySpecialPayment.value
      && Number(specialActionDialog.amount) > 0
      && specialActionDialog.transactionReference.trim().length >= 4
      && specialActionDialog.reason.trim().length >= 10;
  }
  if (specialActionDialog.action === "cancel_order") return specialActionDialog.reason.trim().length >= 10;
  if (specialActionDialog.action === "approve_milestone") return Boolean(specialActionDialog.milestone);
  return true;
});

function openSpecialActionDialog(action: SpecialAction, milestone: SpecialOrderMilestone | null = null) {
  specialActionDialog.open = true;
  specialActionDialog.action = action;
  specialActionDialog.writerId = "";
  specialActionDialog.amount = action === "manual_mark_paid" ? specialOutstandingAmount.value : "";
  specialActionDialog.transactionReference = "";
  specialActionDialog.paymentMethod = "";
  specialActionDialog.reason = "";
  specialActionDialog.milestone = milestone;
}

function closeSpecialActionDialog() {
  specialActionDialog.open = false;
  specialActionDialog.action = null;
  specialActionDialog.writerId = "";
  specialActionDialog.amount = "";
  specialActionDialog.transactionReference = "";
  specialActionDialog.paymentMethod = "";
  specialActionDialog.reason = "";
  specialActionDialog.milestone = null;
}

async function confirmSpecialActionDialog() {
  if (!store.detail || !specialActionCanSubmit.value || !specialActionDialog.action) return;

  if (specialActionDialog.action === "assign_writer") {
    if (!auth.isPreviewSession) {
      await specialOrdersApi.assignWriter(store.detail.id, Number(specialActionDialog.writerId));
      await store.loadDetail(store.detail.id);
    }
  } else if (specialActionDialog.action === "manual_mark_paid") {
    await specialOrdersApi.manualVerifyPayment(store.detail.id, {
      amount: specialActionDialog.amount,
      transaction_reference: specialActionDialog.transactionReference.trim(),
      verification_note: specialActionDialog.reason.trim(),
      payment_method: specialActionDialog.paymentMethod.trim(),
    });
    await store.loadDetail(store.detail.id);
  } else if (specialActionDialog.action === "complete_order") {
    await specialOrdersApi.complete(store.detail.id);
    await store.loadDetail(store.detail.id);
  } else if (specialActionDialog.action === "cancel_order") {
    await specialOrdersApi.cancel(store.detail.id, specialActionDialog.reason.trim());
    await store.loadDetail(store.detail.id);
  } else if (specialActionDialog.action === "approve_milestone" && specialActionDialog.milestone) {
    approvingId.value = specialActionDialog.milestone.id;
    try {
      await store.approveMilestone(store.detail.id, specialActionDialog.milestone.id);
    } finally {
      approvingId.value = null;
    }
  }

  closeSpecialActionDialog();
}
</script>
