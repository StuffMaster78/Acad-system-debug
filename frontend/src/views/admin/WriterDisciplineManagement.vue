<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Writer Discipline Management</h1>
        <p class="mt-2 text-gray-600">Manage strikes, warnings, and view discipline history for writers</p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button
          @click="showIssueStrikeModal = true"
          class="btn btn-primary"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Issue Strike
        </button>
        <button
          @click="showIssueProbationModal = true"
          class="btn btn-secondary"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Place on Probation
        </button>
        <button
          @click="showSuspendModal = true"
          class="px-4 py-2 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 transition-colors duration-150 flex items-center"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          Suspend Writer
        </button>
        <button
          @click="showBlacklistModal = true"
          class="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors duration-150 flex items-center"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          Blacklist Writer
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="card p-4 bg-red-50 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Total Active Strikes</p>
        <p class="text-2xl font-bold text-red-900">{{ stats.totalStrikes || 0 }}</p>
      </div>
      <div class="card p-4 bg-yellow-50 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Active Warnings</p>
        <p class="text-2xl font-bold text-yellow-900">{{ stats.totalWarnings || 0 }}</p>
      </div>
      <div class="card p-4 bg-amber-50 border border-amber-200">
        <p class="text-sm font-medium text-amber-700 mb-1">Writers on Probation</p>
        <p class="text-2xl font-bold text-amber-900">{{ stats.writersOnProbation || 0 }}</p>
      </div>
      <div class="card p-4 bg-orange-50 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Suspended Writers</p>
        <p class="text-2xl font-bold text-orange-900">{{ stats.suspendedWriters || 0 }}</p>
      </div>
      <div class="card p-4 bg-gray-50 border border-gray-200">
        <p class="text-sm font-medium text-gray-700 mb-1">Blacklisted Writers</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.blacklistedWriters || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search Writer</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Username, email..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website" @change="loadStrikes" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">View</label>
          <select v-model="activeTab" @change="loadData" class="w-full border rounded px-3 py-2">
            <option value="strikes">Strikes</option>
            <option value="warnings">Warnings</option>
            <option value="probation">Probation</option>
            <option value="status">Writer Status</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Strikes Tab -->
    <div v-if="activeTab === 'strikes'" class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Issued By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="strike in strikes" :key="strike.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div>
                    <div class="font-medium text-gray-900">{{ strike.writer_username }}</div>
                    <div class="text-sm text-gray-500">{{ strike.writer_email }}</div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900 max-w-md truncate">{{ strike.reason }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ strike.issued_by_username || 'System' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(strike.issued_at) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <button
                    @click="revokeStrike(strike)"
                    class="text-red-600 hover:text-red-800 text-sm"
                    title="Revoke this strike"
                  >
                    Revoke
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!strikes.length" class="text-center py-12 text-gray-500">
          No strikes found.
        </div>
      </div>
    </div>

    <!-- Warnings Tab -->
    <div v-if="activeTab === 'warnings'" class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Issued By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="warning in warnings" :key="warning.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="font-medium text-gray-900">{{ warning.writer?.user?.username || 'N/A' }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="getWarningTypeClass(warning.warning_type)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ warning.warning_type }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900 max-w-md truncate">{{ warning.reason }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ warning.issued_by?.username || 'System' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(warning.issued_at) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="warning.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 rounded text-xs font-medium">
                    {{ warning.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <button
                    v-if="warning.is_active"
                    @click="deactivateWarning(warning)"
                    class="text-red-600 hover:text-red-800 text-sm"
                  >
                    Deactivate
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!warnings.length" class="text-center py-12 text-gray-500">
          No warnings found.
        </div>
      </div>
    </div>

    <!-- Probation Tab -->
    <div v-if="activeTab === 'probation'" class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">End Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Placed By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="probation in probations" :key="probation.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div>
                    <div class="font-medium text-gray-900">{{ probation.writer?.user?.username || probation.writer_username || 'N/A' }}</div>
                    <div class="text-sm text-gray-500">{{ probation.writer?.user?.email || probation.writer_email || '' }}</div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900 max-w-md truncate">{{ probation.reason }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(probation.start_date) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(probation.end_date) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ probation.placed_by?.username || 'System' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="probation.is_active ? 'bg-amber-100 text-amber-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 rounded text-xs font-medium">
                    {{ probation.is_active ? 'Active' : 'Expired' }}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <button
                    v-if="probation.is_active"
                    @click="endProbation(probation)"
                    class="text-red-600 hover:text-red-800 text-sm"
                    title="End probation early"
                  >
                    End Probation
                  </button>
                  <span v-else class="text-sm text-gray-400">Completed</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!probations.length" class="text-center py-12 text-gray-500">
          No probation records found.
        </div>
      </div>
    </div>

    <!-- Writer Status Tab -->
    <div v-if="activeTab === 'status'" class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active Strikes</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Strike</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="status in writerStatuses" :key="status.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="font-medium text-gray-900">{{ status.writer?.user?.username || 'N/A' }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="getStatusBadgeClass(status)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ getStatusText(status) }}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                  {{ status.active_strikes || 0 }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ status.last_strike_at ? formatDate(status.last_strike_at) : 'Never' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <button
                      @click="viewWriterDetails(status.writer)"
                      class="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View Details
                    </button>
                    <span v-if="!status.is_suspended && !status.is_blacklisted" class="text-gray-300">|</span>
                    <button
                      v-if="!status.is_suspended"
                      @click="openSuspendWriterModal(status.writer)"
                      class="text-orange-600 hover:text-orange-800 text-sm font-medium"
                      title="Suspend this writer immediately"
                    >
                      Suspend
                    </button>
                    <button
                      v-else
                      @click="unsuspendWriter(status.writer)"
                      class="text-green-600 hover:text-green-800 text-sm font-medium"
                      title="Unsuspend this writer"
                    >
                      Unsuspend
                    </button>
                    <span v-if="!status.is_blacklisted" class="text-gray-300">|</span>
                    <button
                      v-if="!status.is_blacklisted"
                      @click="openBlacklistWriterModal(status.writer)"
                      class="text-red-600 hover:text-red-800 text-sm font-medium"
                      title="Blacklist this writer immediately"
                    >
                      Blacklist
                    </button>
                    <button
                      v-else
                      @click="unblacklistWriter(status.writer)"
                      class="text-green-600 hover:text-green-800 text-sm font-medium"
                      title="Remove from blacklist"
                    >
                      Unblacklist
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!writerStatuses.length" class="text-center py-12 text-gray-500">
          No writer statuses found.
        </div>
      </div>
    </div>

    <!-- Issue Strike Modal -->
    <div v-if="showIssueStrikeModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Issue Strike to Writer</h2>
          <button @click="closeStrikeModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <h3 class="font-semibold text-blue-900 mb-2">What is a Strike?</h3>
          <p class="text-sm text-blue-800">
            A strike is a formal disciplinary action recorded against a writer for policy violations. 
            Strikes accumulate and can trigger automatic suspensions or blacklisting based on your 
            discipline configuration. Each strike should have a clear reason documented.
          </p>
        </div>

        <form @submit.prevent="issueStrike" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Select Writer *</label>
            <select v-model="strikeForm.writer" required class="w-full border rounded px-3 py-2">
              <option value="">Choose a writer...</option>
              <option v-for="writer in availableWriters" :key="writer.id" :value="writer.id">
                {{ formatWriterName(writer) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Reason for Strike *</label>
            <textarea
              v-model="strikeForm.reason"
              rows="4"
              required
              placeholder="Describe the policy violation or issue that warrants this strike..."
              class="w-full border rounded px-3 py-2"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">
              Be specific and clear. This reason will be visible to the writer and used for records.
            </p>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeStrikeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Issuing...' : 'Issue Strike' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Issue Probation Modal -->
    <div v-if="showIssueProbationModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Place Writer on Probation</h2>
          <button @click="closeProbationModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
          <h3 class="font-semibold text-amber-900 mb-2">What is Probation?</h3>
          <p class="text-sm text-amber-800">
            Probation is a disciplinary period where a writer is monitored closely. Writers on probation 
            may have restrictions on their account and will be reviewed at the end of the probation period. 
            Probation can be set for a specific duration and will automatically expire.
          </p>
        </div>

        <form @submit.prevent="issueProbation" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Select Writer *</label>
            <select v-model="probationForm.writer" required class="w-full border rounded px-3 py-2">
              <option value="">Choose a writer...</option>
              <option v-for="writer in availableWriters" :key="writer.id" :value="writer.id">
                {{ formatWriterName(writer) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Reason for Probation *</label>
            <textarea
              v-model="probationForm.reason"
              rows="4"
              required
              placeholder="Describe why this writer is being placed on probation..."
              class="w-full border rounded px-3 py-2"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">
              Be specific and clear. This reason will be visible to the writer and used for records.
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Duration (Days) *</label>
            <input
              v-model.number="probationForm.duration_days"
              type="number"
              min="1"
              max="365"
              required
              placeholder="30"
              class="w-full border rounded px-3 py-2"
            />
            <p class="text-xs text-gray-500 mt-1">
              Number of days the probation will last. Default is 30 days.
            </p>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeProbationModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Placing...' : 'Place on Probation' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Suspend Writer Modal -->
    <div v-if="showSuspendModal || showSuspendWriterModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] my-auto flex flex-col shadow-xl">
        <!-- Header - Fixed -->
        <div class="flex items-center justify-between p-6 pb-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Suspend Writer</h2>
          <button 
            @click="closeSuspendModal" 
            class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label="Close modal"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Scrollable Content -->
        <div class="overflow-y-auto flex-1 px-6 py-4">
          <div class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4 mb-4">
            <h3 class="font-semibold text-orange-900 dark:text-orange-200 mb-2">⚠️ Immediate Suspension</h3>
            <p class="text-sm text-orange-800 dark:text-orange-200">
              Suspending a writer will immediately prevent them from:
              <ul class="list-disc list-inside mt-2 space-y-1">
                <li>Accessing their account</li>
                <li>Receiving new orders</li>
                <li>Submitting work</li>
                <li>Withdrawing payments</li>
              </ul>
              This action overrides automatic discipline rules and takes effect immediately.
            </p>
          </div>

          <form @submit.prevent="suspendWriter" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Select Writer *</label>
              <select 
                v-model="suspendForm.writer" 
                required 
                :disabled="selectedWriterForSuspend"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed"
              >
                <option value="">Choose a writer...</option>
                <option v-for="writer in availableWriters" :key="writer.id" :value="writer.id">
                  {{ formatWriterName(writer) }}
                </option>
              </select>
              <p v-if="selectedWriterForSuspend" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Writer: {{ selectedWriterForSuspend?.user?.username || 'N/A' }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Reason for Suspension *</label>
              <textarea
                v-model="suspendForm.reason"
                rows="4"
                required
                placeholder="Describe why this writer is being suspended..."
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              ></textarea>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Be specific and clear. This reason will be visible to the writer and used for records.
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Duration (Days)</label>
              <input
                v-model.number="suspendForm.duration_days"
                type="number"
                min="1"
                placeholder="30"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Number of days the suspension will last. Leave empty for indefinite suspension.
              </p>
            </div>
          </form>
        </div>

        <!-- Footer - Fixed -->
        <div class="flex justify-end gap-2 p-6 pt-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
          <button 
            type="button" 
            @click="closeSuspendModal" 
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-150"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            @click="suspendWriter"
            :disabled="saving" 
            class="px-4 py-2 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 transition-colors duration-150 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Suspending...' : 'Suspend Writer' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Blacklist Writer Modal -->
    <div v-if="showBlacklistModal || showBlacklistWriterModal" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] my-auto flex flex-col shadow-xl">
        <!-- Header - Fixed -->
        <div class="flex items-center justify-between p-6 pb-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Blacklist Writer</h2>
          <button 
            @click="closeBlacklistModal" 
            class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label="Close modal"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Scrollable Content -->
        <div class="overflow-y-auto flex-1 px-6 py-4">
          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
            <h3 class="font-semibold text-red-900 dark:text-red-200 mb-2">🚫 Permanent Blacklist</h3>
            <p class="text-sm text-red-800 dark:text-red-200">
              Blacklisting a writer will permanently:
              <ul class="list-disc list-inside mt-2 space-y-1">
                <li>Prevent them from accessing the system</li>
                <li>Block their email from registering again</li>
                <li>Cancel all pending orders</li>
                <li>Freeze their account and payments</li>
              </ul>
              <strong>This is a permanent action and should only be used for serious violations.</strong>
              This action overrides automatic discipline rules and takes effect immediately.
            </p>
          </div>

          <form @submit.prevent="blacklistWriter" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Select Writer *</label>
              <select 
                v-model="blacklistForm.writer" 
                required 
                :disabled="selectedWriterForBlacklist"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed"
              >
                <option value="">Choose a writer...</option>
                <option v-for="writer in availableWriters" :key="writer.id" :value="writer.id">
                  {{ formatWriterName(writer) }}
                </option>
              </select>
              <p v-if="selectedWriterForBlacklist" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Writer: {{ selectedWriterForBlacklist?.user?.username || 'N/A' }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Reason for Blacklisting *</label>
              <textarea
                v-model="blacklistForm.reason"
                rows="4"
                required
                placeholder="Describe why this writer is being blacklisted (e.g., fraud, policy violation, etc.)..."
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              ></textarea>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Be specific and clear. This reason will be used for records and auditing.
              </p>
            </div>
          </form>
        </div>

        <!-- Footer - Fixed -->
        <div class="flex justify-end gap-2 p-6 pt-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
          <button 
            type="button" 
            @click="closeBlacklistModal" 
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-150"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            @click="blacklistWriter"
            :disabled="saving" 
            class="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors duration-150 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Blacklisting...' : 'Blacklist Writer' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Issue Warning Modal -->
    <div v-if="showIssueWarningModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Issue Warning to Writer</h2>
          <button @click="closeWarningModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <h3 class="font-semibold text-yellow-900 mb-2">What is a Warning?</h3>
          <p class="text-sm text-yellow-800">
            A warning is a less severe disciplinary action than a strike. Warnings can accumulate 
            and may trigger automatic probation or suspension based on your escalation configuration. 
            Use warnings for minor infractions before issuing strikes.
          </p>
        </div>

        <form @submit.prevent="issueWarning" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Select Writer *</label>
            <select v-model="warningForm.writer" required class="w-full border rounded px-3 py-2">
              <option value="">Choose a writer...</option>
              <option v-for="writer in availableWriters" :key="writer.id" :value="writer.id">
                {{ formatWriterName(writer) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Warning Type *</label>
            <select v-model="warningForm.warning_type" required class="w-full border rounded px-3 py-2">
              <option value="minor">Minor</option>
              <option value="major">Major</option>
              <option value="critical">Critical</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">
              Critical warnings are more serious and may trigger immediate action.
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Reason *</label>
            <textarea
              v-model="warningForm.reason"
              rows="4"
              required
              placeholder="Describe the issue..."
              class="w-full border rounded px-3 py-2"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Expires At (Optional)</label>
            <input
              v-model="warningForm.expires_at"
              type="datetime-local"
              class="w-full border rounded px-3 py-2"
            />
            <p class="text-xs text-gray-500 mt-1">
              Leave empty for warnings that don't expire automatically.
            </p>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeWarningModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Issuing...' : 'Issue Warning' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { writerManagementAPI, appealsAPI, adminManagementAPI } from '@/api'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'
import { formatWriterName } from '@/utils/formatDisplay'

const { showToast } = useToast()

const loading = ref(false)
const saving = ref(false)
const activeTab = ref('strikes')
const strikes = ref([])
const warnings = ref([])
const probations = ref([])
const writerStatuses = ref([])
const availableWriters = ref([])
const websites = ref([])
const message = ref('')
const messageSuccess = ref(false)

const showIssueStrikeModal = ref(false)
const showIssueWarningModal = ref(false)
const showIssueProbationModal = ref(false)
const showSuspendModal = ref(false)
const showBlacklistModal = ref(false)
const showSuspendWriterModal = ref(false)
const showBlacklistWriterModal = ref(false)
const selectedWriterForSuspend = ref(null)
const selectedWriterForBlacklist = ref(null)

const stats = ref({
  totalStrikes: 0,
  totalWarnings: 0,
  writersOnProbation: 0,
  suspendedWriters: 0,
  blacklistedWriters: 0,
})

const filters = ref({
  search: '',
  website: '',
})

const strikeForm = ref({
  writer: '',
  reason: '',
})

const warningForm = ref({
  writer: '',
  warning_type: 'minor',
  reason: '',
  expires_at: '',
})

const probationForm = ref({
  writer: '',
  reason: '',
  duration_days: 30,
})

const suspendForm = ref({
  writer: '',
  reason: '',
  duration_days: 30,
})

const blacklistForm = ref({
  writer: '',
  reason: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadData()
  }, 500)
}

const loadData = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'strikes') {
      await loadStrikes()
    } else if (activeTab.value === 'warnings') {
      await loadWarnings()
    } else if (activeTab.value === 'probation') {
      await loadProbations()
    } else if (activeTab.value === 'status') {
      await loadWriterStatuses()
    }
  } catch (e) {
    message.value = 'Failed to load data: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const loadStrikes = async () => {
  try {
    const params = {}
    if (filters.value.website) params.website = filters.value.website
    if (filters.value.search) params.search = filters.value.search
    
    const res = await writerManagementAPI.listStrikes(params)
    strikes.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    stats.value.totalStrikes = strikes.value.length
  } catch (e) {
    console.error('Failed to load strikes:', e)
  }
}

const loadWarnings = async () => {
  try {
    const params = {}
    if (filters.value.website) params.website = filters.value.website
    
    const res = await writerManagementAPI.listWarnings(params)
    warnings.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    stats.value.totalWarnings = warnings.value.filter(w => w.is_active).length
  } catch (e) {
    console.error('Failed to load warnings:', e)
  }
}

const loadProbations = async () => {
  try {
    // Try to load probations from writer-management API first
    let res
    try {
      res = await apiClient.get('/writer-management/probations/', { params: { is_active: true } })
    } catch (e) {
      // If that fails, try admin-management API
      res = await apiClient.get('/admin-management/probations/', { params: { is_active: true } })
    }
    probations.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    stats.value.writersOnProbation = probations.value.filter(p => p.is_active).length
  } catch (e) {
    console.error('Failed to load probations:', e)
    // Also count from writer statuses
    stats.value.writersOnProbation = writerStatuses.value.filter(s => s.is_on_probation).length
  }
}

const loadWriterStatuses = async () => {
  try {
    const res = await writerManagementAPI.listWriterStatuses()
    writerStatuses.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    stats.value.suspendedWriters = writerStatuses.value.filter(s => s.is_suspended).length
    stats.value.blacklistedWriters = writerStatuses.value.filter(s => s.is_blacklisted).length
    stats.value.writersOnProbation = writerStatuses.value.filter(s => s.is_on_probation).length
  } catch (e) {
    console.error('Failed to load writer statuses:', e)
  }
}

const loadWriters = async () => {
  try {
    const res = await writerManagementAPI.listWriters()
    availableWriters.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (e) {
    console.error('Failed to load writers:', e)
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/')
    websites.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const issueStrike = async () => {
  saving.value = true
  message.value = ''
  try {
    await writerManagementAPI.createStrike({
      writer: strikeForm.value.writer,
      reason: strikeForm.value.reason,
    })
    message.value = 'Strike issued successfully'
    messageSuccess.value = true
    closeStrikeModal()
    await loadStrikes()
    showToast('Strike issued successfully', 'success')
  } catch (e) {
    message.value = 'Failed to issue strike: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const issueWarning = async () => {
  saving.value = true
  message.value = ''
  try {
    await writerManagementAPI.createWarning({
      writer: warningForm.value.writer,
      warning_type: warningForm.value.warning_type,
      reason: warningForm.value.reason,
      expires_at: warningForm.value.expires_at || null,
    })
    message.value = 'Warning issued successfully'
    messageSuccess.value = true
    closeWarningModal()
    await loadWarnings()
    showToast('Warning issued successfully', 'success')
  } catch (e) {
    message.value = 'Failed to issue warning: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const revokeStrike = async (strike) => {
  if (!confirm(`Are you sure you want to revoke this strike?\n\nReason: ${strike.reason}\n\nThis action cannot be undone.`)) return
  
  try {
    await writerManagementAPI.revokeStrike(strike.id)
    message.value = 'Strike revoked successfully'
    messageSuccess.value = true
    await loadStrikes()
    showToast('Strike revoked successfully', 'success')
  } catch (e) {
    message.value = 'Failed to revoke strike: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const deactivateWarning = async (warning) => {
  if (!confirm('Are you sure you want to deactivate this warning?')) return
  
  try {
    await writerManagementAPI.deactivateWarning(warning.id)
    message.value = 'Warning deactivated successfully'
    messageSuccess.value = true
    await loadWarnings()
    showToast('Warning deactivated successfully', 'success')
  } catch (e) {
    message.value = 'Failed to deactivate warning: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const issueProbation = async () => {
  saving.value = true
  message.value = ''
  try {
    // Find the writer's user ID
    const writer = availableWriters.value.find(w => w.id === probationForm.value.writer)
    if (!writer || !writer.user?.id) {
      throw new Error('Writer not found or invalid')
    }
    
    await adminManagementAPI.placeOnProbation(
      writer.user.id,
      probationForm.value.reason,
      probationForm.value.duration_days
    )
    message.value = 'Writer placed on probation successfully'
    messageSuccess.value = true
    closeProbationModal()
    await loadProbations()
    await loadWriterStatuses()
    showToast('Writer placed on probation successfully', 'success')
  } catch (e) {
    message.value = 'Failed to place writer on probation: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const endProbation = async (probation) => {
  if (!confirm(`Are you sure you want to end this probation early?\n\nReason: ${probation.reason}\n\nThis action cannot be undone.`)) return
  
  try {
    // Find the writer's user ID
    const writerId = probation.writer?.user?.id || probation.writer_id
    if (!writerId) {
      throw new Error('Writer ID not found')
    }
    
    await adminManagementAPI.removeFromProbation(writerId)
    message.value = 'Probation ended successfully'
    messageSuccess.value = true
    await loadProbations()
    await loadWriterStatuses()
    showToast('Probation ended successfully', 'success')
  } catch (e) {
    message.value = 'Failed to end probation: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const viewWriterDetails = (writer) => {
  // Navigate to writer detail page or show modal
  window.location.href = `/admin/user-management?role=writer&search=${writer?.user?.username || ''}`
}

const closeStrikeModal = () => {
  showIssueStrikeModal.value = false
  strikeForm.value = { writer: '', reason: '' }
}

const closeWarningModal = () => {
  showIssueWarningModal.value = false
  warningForm.value = { writer: '', warning_type: 'minor', reason: '', expires_at: '' }
}

const closeProbationModal = () => {
  showIssueProbationModal.value = false
  probationForm.value = { writer: '', reason: '', duration_days: 30 }
}

const openSuspendWriterModal = (writer) => {
  selectedWriterForSuspend.value = writer
  suspendForm.value.writer = writer?.user?.id || writer?.id || ''
  showSuspendWriterModal.value = true
}

const openBlacklistWriterModal = (writer) => {
  selectedWriterForBlacklist.value = writer
  blacklistForm.value.writer = writer?.user?.id || writer?.id || ''
  showBlacklistWriterModal.value = true
}

const closeSuspendModal = () => {
  showSuspendModal.value = false
  showSuspendWriterModal.value = false
  selectedWriterForSuspend.value = null
  suspendForm.value = { writer: '', reason: '', duration_days: 30 }
}

const closeBlacklistModal = () => {
  showBlacklistModal.value = false
  showBlacklistWriterModal.value = false
  selectedWriterForBlacklist.value = null
  blacklistForm.value = { writer: '', reason: '' }
}

const suspendWriter = async () => {
  saving.value = true
  message.value = ''
  try {
    // Find the writer's user ID
    let userId
    if (selectedWriterForSuspend.value) {
      userId = selectedWriterForSuspend.value.user?.id || selectedWriterForSuspend.value.id
    } else {
      const writer = availableWriters.value.find(w => w.id === suspendForm.value.writer)
      if (!writer || !writer.user?.id) {
        throw new Error('Writer not found or invalid')
      }
      userId = writer.user.id
    }
    
    await adminManagementAPI.suspendUser(
      userId,
      suspendForm.value.reason.trim(),
      suspendForm.value.duration_days || 30
    )
    message.value = 'Writer suspended successfully'
    messageSuccess.value = true
    closeSuspendModal()
    await loadWriterStatuses()
    showToast('Writer suspended successfully', 'success')
  } catch (e) {
    message.value = 'Failed to suspend writer: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const unsuspendWriter = async (writer) => {
  if (!confirm(`Are you sure you want to unsuspend ${writer?.user?.username || 'this writer'}?`)) return
  
  try {
    const userId = writer?.user?.id || writer?.id
    if (!userId) {
      throw new Error('Writer ID not found')
    }
    
    await adminManagementAPI.unsuspendUser(userId)
    message.value = 'Writer unsuspended successfully'
    messageSuccess.value = true
    await loadWriterStatuses()
    showToast('Writer unsuspended successfully', 'success')
  } catch (e) {
    message.value = 'Failed to unsuspend writer: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const blacklistWriter = async () => {
  saving.value = true
  message.value = ''
  try {
    // Find the writer's user ID
    let userId
    if (selectedWriterForBlacklist.value) {
      userId = selectedWriterForBlacklist.value.user?.id || selectedWriterForBlacklist.value.id
    } else {
      const writer = availableWriters.value.find(w => w.id === blacklistForm.value.writer)
      if (!writer || !writer.user?.id) {
        throw new Error('Writer not found or invalid')
      }
      userId = writer.user.id
    }
    
    await adminManagementAPI.blacklistUser(
      userId,
      blacklistForm.value.reason.trim()
    )
    message.value = 'Writer blacklisted successfully'
    messageSuccess.value = true
    closeBlacklistModal()
    await loadWriterStatuses()
    showToast('Writer blacklisted successfully', 'success')
  } catch (e) {
    message.value = 'Failed to blacklist writer: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const unblacklistWriter = async (writer) => {
  if (!confirm(`Are you sure you want to remove ${writer?.user?.username || 'this writer'} from the blacklist?\n\nThis will allow them to access the system again.`)) return
  
  try {
    const userId = writer?.user?.id || writer?.id
    if (!userId) {
      throw new Error('Writer ID not found')
    }
    
    // Note: There might not be an unblacklist endpoint, so we may need to use a different approach
    // For now, we'll try to update the user's blacklist status
    await adminManagementAPI.patchUser(userId, { is_blacklisted: false })
    message.value = 'Writer removed from blacklist successfully'
    messageSuccess.value = true
    await loadWriterStatuses()
    showToast('Writer removed from blacklist successfully', 'success')
  } catch (e) {
    message.value = 'Failed to remove writer from blacklist: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// formatWriterName is now imported from utils

const getWarningTypeClass = (type) => {
  const classes = {
    minor: 'bg-yellow-100 text-yellow-800',
    major: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getStatusBadgeClass = (status) => {
  if (status.is_blacklisted) return 'bg-black text-white'
  if (status.is_suspended) return 'bg-red-100 text-red-800'
  if (status.is_on_probation) return 'bg-yellow-100 text-yellow-800'
  if (status.is_active) return 'bg-green-100 text-green-800'
  return 'bg-gray-100 text-gray-800'
}

const getStatusText = (status) => {
  if (status.is_blacklisted) return 'Blacklisted'
  if (status.is_suspended) return 'Suspended'
  if (status.is_on_probation) return 'On Probation'
  if (status.is_active) return 'Active'
  return 'Inactive'
}

onMounted(async () => {
  await Promise.all([loadData(), loadWriters(), loadWebsites()])
})
</script>

<style scoped>
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.btn-primary {
  background-color: #2563eb;
  color: white;
}
.btn-primary:hover {
  background-color: #1d4ed8;
}
.btn-secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}
.btn-secondary:hover {
  background-color: #d1d5db;
}
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  padding: 1.5rem;
}
</style>

