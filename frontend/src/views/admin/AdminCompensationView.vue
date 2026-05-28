<template>
  <div class="p-6 space-y-4">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Writer Compensation</h1>
      <p class="text-sm text-gray-500 mt-0.5">Payout windows, settlements, advances &amp; cycle changes</p>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex gap-6">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'pb-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
            activeTab === tab.key
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700',
          ]"
        >
          {{ tab.label }}
          <span
            v-if="tab.badge"
            class="ml-1.5 inline-flex items-center justify-center w-5 h-5 text-xs font-bold rounded-full bg-amber-100 text-amber-700"
          >{{ tab.badge }}</span>
        </button>
      </nav>
    </div>

    <!-- ── Windows ───────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'windows'" class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">Payout cycles that define which earnings are settled and paid out.</p>
        <button @click="showCreateWindow = true" class="btn-primary text-sm">+ New Window</button>
      </div>

      <div v-if="loadingWindows" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!windows.length" class="text-center py-10 text-gray-400 text-sm">No payout windows found.</div>
      <div v-else class="space-y-3">
        <div
          v-for="win in windows"
          :key="win.id"
          class="bg-white rounded-lg border border-gray-200 overflow-hidden"
        >
          <div
            class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-gray-50"
            @click="toggleWindow(win.id)"
          >
            <div class="flex items-center gap-4">
              <span :class="windowStatusClass(win.status)" class="text-xs font-semibold px-2.5 py-1 rounded-full">
                {{ win.status }}
              </span>
              <div>
                <p class="font-medium text-gray-800 text-sm">{{ win.cycle_type }} &mdash; {{ win.start_date }} → {{ win.end_date }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Created {{ fmtDate(win.created_at) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-if="win.status === 'open'"
                @click.stop="doWindowAction(win.id, 'close')"
                :disabled="actioning"
                class="text-xs px-3 py-1.5 rounded border border-gray-200 hover:bg-gray-100 disabled:opacity-50"
              >Close</button>
              <button
                v-if="win.status === 'closed'"
                @click.stop="doWindowAction(win.id, 'start-processing')"
                :disabled="actioning"
                class="text-xs px-3 py-1.5 rounded border border-indigo-200 text-indigo-600 hover:bg-indigo-50 disabled:opacity-50"
              >Start Processing</button>
              <button
                v-if="win.status === 'processing'"
                @click.stop="doWindowAction(win.id, 'mark-done')"
                :disabled="actioning"
                class="text-xs px-3 py-1.5 rounded border border-green-200 text-green-600 hover:bg-green-50 disabled:opacity-50"
              >Mark Done</button>
              <span class="text-gray-300">›</span>
            </div>
          </div>

          <!-- Expanded: batch detail -->
          <div v-if="expandedWindow === win.id" class="border-t border-gray-100 px-5 py-4 space-y-4 bg-gray-50">
            <div v-if="loadingBatch" class="text-center text-gray-400 text-sm py-4">Loading batch…</div>
            <template v-else-if="activeBatch">
              <!-- Batch header -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-semibold text-gray-700">Batch #{{ activeBatch.id }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">
                    {{ activeBatch.total_writers }} writers · ${{ activeBatch.total_amount }}
                    &nbsp;·&nbsp; {{ activeBatch.paid_count }} paid, {{ activeBatch.held_count }} held, {{ activeBatch.pending_count }} pending
                  </p>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="doBulkConfirm(activeBatch.id)"
                    :disabled="actioning"
                    class="text-xs px-3 py-1.5 rounded border border-indigo-200 text-indigo-600 hover:bg-indigo-50 disabled:opacity-50"
                  >Bulk Confirm</button>
                  <button
                    @click="doBulkMarkPaid(activeBatch.id)"
                    :disabled="actioning"
                    class="text-xs px-3 py-1.5 rounded border border-green-200 text-green-600 hover:bg-green-50 disabled:opacity-50"
                  >Bulk Mark Paid</button>
                </div>
              </div>

              <!-- Payout records table -->
              <div class="overflow-x-auto rounded-lg border border-gray-200">
                <table class="w-full text-sm">
                  <thead class="bg-white text-xs text-gray-500 uppercase">
                    <tr>
                      <th class="px-4 py-2 text-left">Writer</th>
                      <th class="px-4 py-2 text-right">Amount</th>
                      <th class="px-4 py-2 text-left">Status</th>
                      <th class="px-4 py-2 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100 bg-white">
                    <tr v-for="rec in activeBatch.records" :key="rec.id" class="hover:bg-gray-50">
                      <td class="px-4 py-2">
                        <p class="font-medium text-gray-800">{{ rec.writer_name }}</p>
                        <p class="text-xs text-gray-400">{{ rec.writer_email }}</p>
                      </td>
                      <td class="px-4 py-2 text-right font-mono font-semibold text-gray-800">${{ rec.total_amount }}</td>
                      <td class="px-4 py-2">
                        <span :class="payoutStatusClass(rec.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ rec.status }}</span>
                        <p v-if="rec.hold_reason" class="text-xs text-red-500 mt-0.5">{{ rec.hold_reason }}</p>
                      </td>
                      <td class="px-4 py-2">
                        <div class="flex gap-1.5 flex-wrap">
                          <button
                            v-if="rec.status === 'pending'"
                            @click="doPayoutAction(rec, 'confirm')"
                            :disabled="actioning"
                            class="text-xs px-2 py-1 rounded border border-indigo-200 text-indigo-600 hover:bg-indigo-50 disabled:opacity-50"
                          >Confirm</button>
                          <button
                            v-if="rec.status === 'confirmed'"
                            @click="openMarkPaidDialog(rec)"
                            :disabled="actioning"
                            class="text-xs px-2 py-1 rounded border border-green-200 text-green-600 hover:bg-green-50 disabled:opacity-50"
                          >Mark Paid</button>
                          <button
                            v-if="rec.status === 'pending' || rec.status === 'confirmed'"
                            @click="openHoldDialog(rec)"
                            :disabled="actioning"
                            class="text-xs px-2 py-1 rounded border border-amber-200 text-amber-600 hover:bg-amber-50 disabled:opacity-50"
                          >Hold</button>
                          <button
                            v-if="rec.status === 'held'"
                            @click="doPayoutAction(rec, 'release')"
                            :disabled="actioning"
                            class="text-xs px-2 py-1 rounded border border-gray-200 hover:bg-gray-100 disabled:opacity-50"
                          >Release</button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </template>
            <p v-else class="text-sm text-gray-400 text-center py-4">No batch found for this window.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Settlements ────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'settlements'" class="space-y-4">
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">Per-writer settlement periods showing gross earnings, deductions, and net payable.</p>
        <button @click="showRunSettlement = true" class="btn-primary text-sm">Run Settlement</button>
      </div>

      <!-- Filter -->
      <div class="flex gap-3">
        <select v-model="settlementStatusFilter" class="input text-sm w-40">
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="finalized">Finalized</option>
          <option value="locked">Locked</option>
        </select>
      </div>

      <div v-if="loadingSettlements" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!filteredSettlements.length" class="text-center py-10 text-gray-400 text-sm">No settlements found.</div>
      <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Writer</th>
              <th class="px-3 py-2 text-right">Gross</th>
              <th class="px-3 py-2 text-right">Deductions</th>
              <th class="px-3 py-2 text-right">Net</th>
              <th class="px-3 py-2 text-left">Status</th>
              <th class="px-3 py-2 text-left">Window</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="s in filteredSettlements" :key="s.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-gray-700">#{{ s.writer }}</td>
              <td class="px-3 py-2 text-right font-mono text-gray-800">${{ s.gross_earnings }}</td>
              <td class="px-3 py-2 text-right font-mono text-red-600">-${{ s.total_deductions }}</td>
              <td class="px-3 py-2 text-right font-mono font-semibold text-green-700">${{ s.net_payable }}</td>
              <td class="px-3 py-2">
                <span :class="settlementStatusClass(s.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ s.status }}</span>
              </td>
              <td class="px-3 py-2 text-gray-400 text-xs">Win #{{ s.payment_window }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Advances ───────────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'advances'" class="space-y-4">
      <p class="text-sm text-gray-500">Writer advance payment requests requiring admin review.</p>

      <!-- Filter -->
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="s in ['all', 'pending', 'approved', 'rejected']"
          :key="s"
          @click="advanceFilter = s"
          :class="[
            'text-xs px-3 py-1.5 rounded-full border transition',
            advanceFilter === s
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'border-gray-200 text-gray-600 hover:bg-gray-50',
          ]"
        >{{ s.charAt(0).toUpperCase() + s.slice(1) }}</button>
      </div>

      <div v-if="loadingAdvances" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!filteredAdvances.length" class="text-center py-10 text-gray-400 text-sm">No advances found.</div>
      <div v-else class="space-y-3">
        <div
          v-for="adv in filteredAdvances"
          :key="adv.id"
          class="bg-white rounded-lg border border-gray-200 p-5 space-y-3"
        >
          <div class="flex items-start justify-between">
            <div>
              <p class="font-semibold text-gray-800 text-sm">{{ adv.writer_name }}</p>
              <p class="text-xs text-gray-400 mt-0.5">Requested {{ fmtDate(adv.created_at) }}</p>
            </div>
            <span :class="advanceStatusClass(adv.status)" class="text-xs font-semibold px-2.5 py-1 rounded-full">{{ adv.status }}</span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div class="bg-gray-50 rounded-lg p-2.5">
              <p class="text-gray-500">Requested</p>
              <p class="font-semibold text-gray-800 mt-0.5">${{ adv.requested_amount }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2.5">
              <p class="text-gray-500">Approved</p>
              <p class="font-semibold text-gray-800 mt-0.5">{{ adv.approved_amount ? '$' + adv.approved_amount : '—' }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2.5">
              <p class="text-gray-500">Recovered</p>
              <p class="font-semibold text-gray-800 mt-0.5">${{ adv.recovered_amount }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2.5">
              <p class="text-gray-500">Outstanding</p>
              <p class="font-semibold text-amber-700 mt-0.5">${{ adv.outstanding_balance }}</p>
            </div>
          </div>

          <p v-if="adv.reason" class="text-xs text-gray-500 italic">"{{ adv.reason }}"</p>
          <p v-if="adv.admin_notes" class="text-xs text-indigo-600">Admin: {{ adv.admin_notes }}</p>

          <div v-if="adv.status === 'pending'" class="flex gap-2 pt-1">
            <button @click="openApproveAdvance(adv)" class="text-xs px-3 py-1.5 rounded border border-green-200 text-green-600 hover:bg-green-50">Approve</button>
            <button @click="doRejectAdvance(adv.id)" :disabled="actioning" class="text-xs px-3 py-1.5 rounded border border-red-200 text-red-500 hover:bg-red-50 disabled:opacity-50">Reject</button>
          </div>
          <div v-if="adv.status === 'approved' && parseFloat(adv.outstanding_balance) > 0" class="flex gap-2 pt-1">
            <button @click="openRecoverAdvance(adv)" class="text-xs px-3 py-1.5 rounded border border-amber-200 text-amber-600 hover:bg-amber-50">Record Recovery</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Cycle Changes ──────────────────────────────────────────────────── -->
    <div v-if="activeTab === 'cycle-changes'" class="space-y-4">
      <p class="text-sm text-gray-500">Writers requesting a change to their payout cycle frequency.</p>

      <div v-if="loadingCycleChanges" class="text-center py-10 text-gray-400">Loading…</div>
      <div v-else-if="!cycleChanges.length" class="text-center py-10 text-gray-400 text-sm">No cycle change requests.</div>
      <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Writer</th>
              <th class="px-3 py-2 text-left">From</th>
              <th class="px-3 py-2 text-left">Requested</th>
              <th class="px-3 py-2 text-left">Reason</th>
              <th class="px-3 py-2 text-left">Status</th>
              <th class="px-3 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="cc in cycleChanges" :key="cc.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 font-medium text-gray-800">{{ cc.writer_name }}</td>
              <td class="px-3 py-2 text-gray-500 font-mono text-xs">{{ cc.from_cycle }}</td>
              <td class="px-3 py-2 text-indigo-700 font-mono text-xs font-semibold">{{ cc.requested_cycle }}</td>
              <td class="px-3 py-2 text-gray-500 max-w-xs truncate text-xs">{{ cc.reason ?? '—' }}</td>
              <td class="px-3 py-2">
                <span :class="cycleChangeStatusClass(cc.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ cc.status }}</span>
              </td>
              <td class="px-3 py-2">
                <div v-if="cc.status === 'pending'" class="flex gap-1.5">
                  <button
                    @click="doApproveCycleChange(cc.id)"
                    :disabled="actioning"
                    class="text-xs px-2.5 py-1 rounded border border-green-200 text-green-600 hover:bg-green-50 disabled:opacity-50"
                  >Approve</button>
                  <button
                    @click="openRejectCycleChange(cc)"
                    class="text-xs px-2.5 py-1 rounded border border-red-200 text-red-500 hover:bg-red-50"
                  >Reject</button>
                </div>
                <span v-else class="text-xs text-gray-400">{{ cc.reviewed_at ? fmtDate(cc.reviewed_at) : '—' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Dialogs ──────────────────────────────────────────────────────────── -->

    <!-- Create window -->
    <div v-if="showCreateWindow" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Create Payout Window</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Cycle Type</label>
            <select v-model="newWindow.cycle_type" class="input">
              <option value="weekly">Weekly</option>
              <option value="biweekly">Bi-Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Start Date</label>
            <input v-model="newWindow.start_date" type="date" class="input" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">End Date</label>
            <input v-model="newWindow.end_date" type="date" class="input" />
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button @click="showCreateWindow = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doCreateWindow" :disabled="actioning" class="btn-primary text-sm">
            {{ actioning ? 'Creating…' : 'Create' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Hold payout -->
    <div v-if="holdDialog.open" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Hold Payout — {{ holdDialog.writerName }}</h3>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Reason</label>
          <textarea v-model="holdDialog.reason" class="input h-20 resize-none" placeholder="Required" />
        </div>
        <div class="flex justify-end gap-3">
          <button @click="holdDialog.open = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doHold" :disabled="actioning || !holdDialog.reason.trim()" class="btn-primary text-sm">
            {{ actioning ? 'Holding…' : 'Hold' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Approve advance -->
    <div v-if="approveAdvanceDialog.open" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Approve Advance — {{ approveAdvanceDialog.writerName }}</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Approved Amount</label>
            <input v-model="approveAdvanceDialog.amount" type="number" step="0.01" min="0.01" class="input" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Admin Notes (optional)</label>
            <input v-model="approveAdvanceDialog.notes" class="input" />
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button @click="approveAdvanceDialog.open = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doApproveAdvance" :disabled="actioning || !approveAdvanceDialog.amount" class="btn-primary text-sm">
            {{ actioning ? 'Approving…' : 'Approve' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Recover advance -->
    <div v-if="recoverAdvanceDialog.open" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Record Recovery — {{ recoverAdvanceDialog.writerName }}</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Recovery Amount</label>
            <input v-model="recoverAdvanceDialog.amount" type="number" step="0.01" min="0.01" class="input" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Notes (optional)</label>
            <input v-model="recoverAdvanceDialog.notes" class="input" />
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button @click="recoverAdvanceDialog.open = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doRecoverAdvance" :disabled="actioning || !recoverAdvanceDialog.amount" class="btn-primary text-sm">
            {{ actioning ? 'Saving…' : 'Record' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Mark payout paid -->
    <div v-if="markPaidDialog.open" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Mark Paid — {{ markPaidDialog.writerName }}</h3>
        <p class="text-xs text-gray-500">${{ markPaidDialog.amount }} payout</p>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Payment Method</label>
            <select v-model="markPaidDialog.method" class="input">
              <option value="">— Select method —</option>
              <option value="Bank Transfer">Bank Transfer</option>
              <option value="PayPal">PayPal</option>
              <option value="Wise">Wise</option>
              <option value="M-Pesa">M-Pesa</option>
              <option value="Crypto">Crypto</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">External Reference / Transaction ID</label>
            <input v-model="markPaidDialog.external_reference" class="input" placeholder="e.g. WIRE-20240510-001" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Notes (optional)</label>
            <textarea v-model="markPaidDialog.notes" class="input h-16 resize-none" />
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button @click="markPaidDialog.open = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doMarkPaid" :disabled="actioning || !markPaidDialog.method" class="btn-primary text-sm">
            {{ actioning ? 'Saving…' : 'Mark Paid' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Reject cycle change -->
    <div v-if="rejectCycleDialog.open" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Reject Cycle Change — {{ rejectCycleDialog.writerName }}</h3>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Rejection Reason (optional)</label>
          <textarea v-model="rejectCycleDialog.reason" class="input h-20 resize-none" />
        </div>
        <div class="flex justify-end gap-3">
          <button @click="rejectCycleDialog.open = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doRejectCycleChange" :disabled="actioning" class="text-sm px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50">
            {{ actioning ? 'Rejecting…' : 'Reject' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Run settlement -->
    <div v-if="showRunSettlement" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h3 class="font-semibold text-gray-800">Run Settlement</h3>
        <p class="text-sm text-gray-500">This will compute settlement records for all writers in the selected window.</p>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Payment Window ID</label>
          <input v-model.number="runSettlementWindowId" type="number" class="input" placeholder="Enter window ID" />
        </div>
        <div class="flex justify-end gap-3">
          <button @click="showRunSettlement = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
          <button @click="doRunSettlement" :disabled="actioning || !runSettlementWindowId" class="btn-primary text-sm">
            {{ actioning ? 'Running…' : 'Run' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div
      v-if="toast"
      class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl shadow-lg text-sm text-white"
      :class="toast.type === 'error' ? 'bg-red-600' : 'bg-green-600'"
    >{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { adminCompensationApi } from "@/api/adminCompensation";
import type { PaymentWindow, PayoutBatch, PayoutRecord, CycleChangeRequest, Settlement, AdvanceRequest } from "@/api/adminCompensation";

// ── Tabs ───────────────────────────────────────────────────────────────────
const pendingAdvances = ref(0);
const pendingCycleChanges = ref(0);

const tabs = computed(() => [
  { key: "windows", label: "Payout Windows", badge: 0 },
  { key: "settlements", label: "Settlements", badge: 0 },
  { key: "advances", label: "Advances", badge: pendingAdvances.value || undefined },
  { key: "cycle-changes", label: "Cycle Changes", badge: pendingCycleChanges.value || undefined },
] as { key: string; label: string; badge?: number }[]);

const activeTab = ref("windows");

// ── Data ───────────────────────────────────────────────────────────────────
const windows = ref<PaymentWindow[]>([]);
const activeBatch = ref<PayoutBatch | null>(null);
const settlements = ref<Settlement[]>([]);
const advances = ref<AdvanceRequest[]>([]);
const cycleChanges = ref<CycleChangeRequest[]>([]);

const loadingWindows = ref(false);
const loadingBatch = ref(false);
const loadingSettlements = ref(false);
const loadingAdvances = ref(false);
const loadingCycleChanges = ref(false);
const actioning = ref(false);

const expandedWindow = ref<number | null>(null);
const settlementStatusFilter = ref("");
const advanceFilter = ref("all");

// ── Dialogs ────────────────────────────────────────────────────────────────
const showCreateWindow = ref(false);
const showRunSettlement = ref(false);
const runSettlementWindowId = ref<number | null>(null);

const newWindow = reactive({ cycle_type: "weekly", start_date: "", end_date: "" });

const holdDialog = reactive({ open: false, recordId: 0, writerName: "", reason: "" });
const markPaidDialog = reactive({ open: false, recordId: 0, writerName: "", amount: "", method: "", external_reference: "", notes: "" });
const approveAdvanceDialog = reactive({ open: false, advanceId: 0, writerName: "", amount: "", notes: "" });
const recoverAdvanceDialog = reactive({ open: false, advanceId: 0, writerName: "", amount: "", notes: "" });
const rejectCycleDialog = reactive({ open: false, requestId: 0, writerName: "", reason: "" });

const toast = ref<{ message: string; type: "success" | "error" } | null>(null);

// ── Computed ───────────────────────────────────────────────────────────────
const filteredSettlements = computed(() =>
  settlementStatusFilter.value
    ? settlements.value.filter((s) => s.status === settlementStatusFilter.value)
    : settlements.value,
);

const filteredAdvances = computed(() =>
  advanceFilter.value === "all"
    ? advances.value
    : advances.value.filter((a) => a.status === advanceFilter.value),
);

// ── Helpers ────────────────────────────────────────────────────────────────
function showToast(message: string, type: "success" | "error" = "success") {
  toast.value = { message, type };
  setTimeout(() => (toast.value = null), 3500);
}

function fmtDate(ts: string) {
  return new Date(ts).toLocaleDateString(undefined, { dateStyle: "medium" });
}

function windowStatusClass(status: string) {
  const map: Record<string, string> = {
    open: "bg-green-100 text-green-700",
    closed: "bg-gray-100 text-gray-600",
    processing: "bg-blue-100 text-blue-700",
    done: "bg-indigo-100 text-indigo-700",
  };
  return map[status] ?? "bg-gray-100 text-gray-600";
}

function payoutStatusClass(status: string) {
  const map: Record<string, string> = {
    pending: "bg-amber-100 text-amber-700",
    confirmed: "bg-blue-100 text-blue-700",
    paid: "bg-green-100 text-green-700",
    held: "bg-red-100 text-red-700",
  };
  return map[status] ?? "bg-gray-100 text-gray-600";
}

function settlementStatusClass(status: string) {
  const map: Record<string, string> = {
    pending: "bg-amber-100 text-amber-700",
    finalized: "bg-green-100 text-green-700",
    locked: "bg-gray-100 text-gray-600",
  };
  return map[status] ?? "bg-gray-100 text-gray-600";
}

function advanceStatusClass(status: string) {
  const map: Record<string, string> = {
    pending: "bg-amber-100 text-amber-700",
    approved: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
    recovered: "bg-gray-100 text-gray-600",
  };
  return map[status] ?? "bg-gray-100 text-gray-600";
}

function cycleChangeStatusClass(status: string) {
  const map: Record<string, string> = {
    pending: "bg-amber-100 text-amber-700",
    approved: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
  };
  return map[status] ?? "bg-gray-100 text-gray-600";
}

function extractList<T>(data: { count: number; next: string | null; previous: string | null; results: T[] } | T[]): T[] {
  return Array.isArray(data) ? data : data.results;
}

// ── Fetch ──────────────────────────────────────────────────────────────────
async function loadWindows() {
  loadingWindows.value = true;
  try {
    const resp = await adminCompensationApi.windows();
    windows.value = extractList(resp.data);
  } catch {
    showToast("Failed to load windows", "error");
  } finally {
    loadingWindows.value = false;
  }
}

async function loadSettlements() {
  loadingSettlements.value = true;
  try {
    const resp = await adminCompensationApi.settlements();
    settlements.value = extractList(resp.data);
  } catch {
    showToast("Failed to load settlements", "error");
  } finally {
    loadingSettlements.value = false;
  }
}

async function loadAdvances() {
  loadingAdvances.value = true;
  try {
    const resp = await adminCompensationApi.advances();
    advances.value = extractList(resp.data);
    pendingAdvances.value = advances.value.filter((a) => a.status === "pending").length;
  } catch {
    showToast("Failed to load advances", "error");
  } finally {
    loadingAdvances.value = false;
  }
}

async function loadCycleChanges() {
  loadingCycleChanges.value = true;
  try {
    const resp = await adminCompensationApi.cycleChanges();
    cycleChanges.value = extractList(resp.data);
    pendingCycleChanges.value = cycleChanges.value.filter((c) => c.status === "pending").length;
  } catch {
    showToast("Failed to load cycle changes", "error");
  } finally {
    loadingCycleChanges.value = false;
  }
}

// ── Window actions ─────────────────────────────────────────────────────────
async function toggleWindow(id: number) {
  if (expandedWindow.value === id) {
    expandedWindow.value = null;
    activeBatch.value = null;
    return;
  }
  expandedWindow.value = id;
  activeBatch.value = null;
  // Batch IDs are not directly on the window — we load summary first to find batch
  loadingBatch.value = true;
  try {
    const summary = await adminCompensationApi.windowSummary(id);
    const batchId = (summary.data as Record<string, unknown>).batch_id as number | undefined;
    if (batchId) {
      const bResp = await adminCompensationApi.batchDetail(batchId);
      activeBatch.value = bResp.data;
    }
  } catch {
    // Summary may not include batch_id — silently no-op
  } finally {
    loadingBatch.value = false;
  }
}

async function doWindowAction(windowId: number, action: "close" | "start-processing" | "mark-done") {
  actioning.value = true;
  try {
    if (action === "close") await adminCompensationApi.closeWindow(windowId);
    else if (action === "start-processing") await adminCompensationApi.startProcessing(windowId);
    else await adminCompensationApi.markDone(windowId);
    await loadWindows();
    showToast("Window updated");
  } catch {
    showToast("Action failed", "error");
  } finally {
    actioning.value = false;
  }
}

async function doCreateWindow() {
  if (!newWindow.start_date || !newWindow.end_date) return;
  actioning.value = true;
  try {
    await adminCompensationApi.createWindow(newWindow);
    showCreateWindow.value = false;
    Object.assign(newWindow, { cycle_type: "weekly", start_date: "", end_date: "" });
    await loadWindows();
    showToast("Window created");
  } catch {
    showToast("Failed to create window", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Batch actions ──────────────────────────────────────────────────────────
async function doBulkConfirm(batchId: number) {
  actioning.value = true;
  try {
    await adminCompensationApi.bulkConfirm(batchId);
    const resp = await adminCompensationApi.batchDetail(batchId);
    activeBatch.value = resp.data;
    showToast("All pending records confirmed");
  } catch {
    showToast("Bulk confirm failed", "error");
  } finally {
    actioning.value = false;
  }
}

async function doBulkMarkPaid(batchId: number) {
  actioning.value = true;
  try {
    await adminCompensationApi.bulkMarkPaid(batchId);
    const resp = await adminCompensationApi.batchDetail(batchId);
    activeBatch.value = resp.data;
    showToast("All confirmed records marked paid");
  } catch {
    showToast("Bulk mark-paid failed", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Payout item actions ────────────────────────────────────────────────────
function openHoldDialog(rec: PayoutRecord) {
  holdDialog.open = true;
  holdDialog.recordId = rec.id;
  holdDialog.writerName = rec.writer_name;
  holdDialog.reason = "";
}

function openMarkPaidDialog(rec: PayoutRecord) {
  markPaidDialog.open = true;
  markPaidDialog.recordId = rec.id;
  markPaidDialog.writerName = rec.writer_name;
  markPaidDialog.amount = rec.total_amount;
  markPaidDialog.method = "";
  markPaidDialog.external_reference = "";
  markPaidDialog.notes = "";
}

async function doMarkPaid() {
  if (!markPaidDialog.method) return;
  actioning.value = true;
  try {
    const updated = (await adminCompensationApi.markPaid(markPaidDialog.recordId, {
      method: markPaidDialog.method,
      external_reference: markPaidDialog.external_reference,
      notes: markPaidDialog.notes,
    })).data;
    if (activeBatch.value) {
      const idx = activeBatch.value.records.findIndex((r) => r.id === markPaidDialog.recordId);
      if (idx !== -1) activeBatch.value.records[idx] = updated;
    }
    markPaidDialog.open = false;
    showToast("Payout marked paid");
  } catch {
    showToast("Mark paid failed", "error");
  } finally {
    actioning.value = false;
  }
}

async function doPayoutAction(rec: PayoutRecord, action: "confirm" | "release") {
  actioning.value = true;
  try {
    let updated: PayoutRecord;
    if (action === "confirm") updated = (await adminCompensationApi.confirmPayout(rec.id)).data;
    else updated = (await adminCompensationApi.releasePayout(rec.id)).data;
    if (activeBatch.value) {
      const idx = activeBatch.value.records.findIndex((r) => r.id === rec.id);
      if (idx !== -1) activeBatch.value.records[idx] = updated;
    }
    showToast("Payout record updated");
  } catch {
    showToast("Action failed", "error");
  } finally {
    actioning.value = false;
  }
}

async function doHold() {
  if (!holdDialog.reason.trim()) return;
  actioning.value = true;
  try {
    const updated = (await adminCompensationApi.holdPayout(holdDialog.recordId, holdDialog.reason)).data;
    if (activeBatch.value) {
      const idx = activeBatch.value.records.findIndex((r) => r.id === holdDialog.recordId);
      if (idx !== -1) activeBatch.value.records[idx] = updated;
    }
    holdDialog.open = false;
    showToast("Payout held");
  } catch {
    showToast("Hold failed", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Advance actions ────────────────────────────────────────────────────────
function openApproveAdvance(adv: AdvanceRequest) {
  approveAdvanceDialog.open = true;
  approveAdvanceDialog.advanceId = adv.id;
  approveAdvanceDialog.writerName = adv.writer_name;
  approveAdvanceDialog.amount = adv.requested_amount;
  approveAdvanceDialog.notes = "";
}

function openRecoverAdvance(adv: AdvanceRequest) {
  recoverAdvanceDialog.open = true;
  recoverAdvanceDialog.advanceId = adv.id;
  recoverAdvanceDialog.writerName = adv.writer_name;
  recoverAdvanceDialog.amount = "";
  recoverAdvanceDialog.notes = "";
}

async function doApproveAdvance() {
  if (!approveAdvanceDialog.amount) return;
  actioning.value = true;
  try {
    const updated = (await adminCompensationApi.approveAdvance(
      approveAdvanceDialog.advanceId,
      approveAdvanceDialog.amount,
      approveAdvanceDialog.notes || undefined,
    )).data;
    const idx = advances.value.findIndex((a) => a.id === approveAdvanceDialog.advanceId);
    if (idx !== -1) advances.value[idx] = updated;
    pendingAdvances.value = advances.value.filter((a) => a.status === "pending").length;
    approveAdvanceDialog.open = false;
    showToast("Advance approved");
  } catch {
    showToast("Approval failed", "error");
  } finally {
    actioning.value = false;
  }
}

async function doRejectAdvance(id: number) {
  actioning.value = true;
  try {
    const updated = (await adminCompensationApi.rejectAdvance(id)).data;
    const idx = advances.value.findIndex((a) => a.id === id);
    if (idx !== -1) advances.value[idx] = updated;
    pendingAdvances.value = advances.value.filter((a) => a.status === "pending").length;
    showToast("Advance rejected");
  } catch {
    showToast("Rejection failed", "error");
  } finally {
    actioning.value = false;
  }
}

async function doRecoverAdvance() {
  if (!recoverAdvanceDialog.amount) return;
  actioning.value = true;
  try {
    const updated = (await adminCompensationApi.recoverAdvance(
      recoverAdvanceDialog.advanceId,
      recoverAdvanceDialog.amount,
      recoverAdvanceDialog.notes || undefined,
    )).data;
    const idx = advances.value.findIndex((a) => a.id === recoverAdvanceDialog.advanceId);
    if (idx !== -1) advances.value[idx] = updated;
    recoverAdvanceDialog.open = false;
    showToast("Recovery recorded");
  } catch {
    showToast("Recovery failed", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Cycle change actions ───────────────────────────────────────────────────
async function doApproveCycleChange(id: number) {
  actioning.value = true;
  try {
    await adminCompensationApi.approveCycleChange(id);
    await loadCycleChanges();
    showToast("Cycle change approved");
  } catch {
    showToast("Approval failed", "error");
  } finally {
    actioning.value = false;
  }
}

function openRejectCycleChange(cc: CycleChangeRequest) {
  rejectCycleDialog.open = true;
  rejectCycleDialog.requestId = cc.id;
  rejectCycleDialog.writerName = cc.writer_name;
  rejectCycleDialog.reason = "";
}

async function doRejectCycleChange() {
  actioning.value = true;
  try {
    await adminCompensationApi.rejectCycleChange(rejectCycleDialog.requestId, rejectCycleDialog.reason || undefined);
    await loadCycleChanges();
    rejectCycleDialog.open = false;
    showToast("Cycle change rejected");
  } catch {
    showToast("Rejection failed", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Settlement actions ─────────────────────────────────────────────────────
async function doRunSettlement() {
  if (!runSettlementWindowId.value) return;
  actioning.value = true;
  try {
    await adminCompensationApi.runSettlement({ payment_window: runSettlementWindowId.value });
    showRunSettlement.value = false;
    runSettlementWindowId.value = null;
    await loadSettlements();
    showToast("Settlement run complete");
  } catch {
    showToast("Settlement failed", "error");
  } finally {
    actioning.value = false;
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
onMounted(() => {
  loadWindows();
  loadSettlements();
  loadAdvances();
  loadCycleChanges();
});
</script>

<style scoped>
.input {
  @apply w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent;
}
.btn-primary {
  @apply px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition;
}
</style>
