<template>
  <div class="space-y-6">
    <PageHeader
      title="Email Management"
      subtitle="Manage mass emails, digests, and broadcast messages"
      @refresh="loadData"
    />

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-3 border-b-2 font-medium text-sm transition-all duration-200 flex items-center gap-2',
            activeTab === tab.id
              ? 'border-primary-500 text-primary-600 bg-primary-50'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
          ]"
        >
          <span v-if="tab.icon" class="text-base">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </nav>
    </div>

    <!-- Mass Emails Tab -->
    <div v-if="activeTab === 'mass-emails'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Email Campaigns</h2>
        <button @click="createMassEmail" class="btn btn-primary">+ Create Campaign</button>
      </div>

      <FilterBar
        :filters="massEmailFilters"
        :loading="massEmailsLoading"
        @update:filter="updateMassEmailFilter"
        @clear="clearMassEmailFilters"
      >
        <template #filters>
          <select
            v-model="massEmailFilters.website_id"
            class="border rounded px-3 py-2 text-sm"
            @change="loadMassEmails"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
          <select
            v-model="massEmailFilters.status"
            class="border rounded px-3 py-2 text-sm"
            @change="loadMassEmails"
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="scheduled">Scheduled</option>
            <option value="sending">Sending</option>
            <option value="sent">Sent</option>
            <option value="failed">Failed</option>
          </select>
          <select
            v-model="massEmailFilters.email_type"
            class="border rounded px-3 py-2 text-sm"
            @change="loadMassEmails"
          >
            <option value="">All Types</option>
            <option value="marketing">Marketing</option>
            <option value="promos">Promos</option>
            <option value="communication">Communication</option>
            <option value="updates">Updates</option>
          </select>
        </template>
      </FilterBar>

      <DataTable
        :columns="massEmailColumns"
        :data="formattedMassEmails"
        :loading="massEmailsLoading"
        :pagination="massEmailPagination"
        @page-change="handleMassEmailPageChange"
        @page-size-change="handleMassEmailPageSizeChange"
        @export="exportMassEmailsToCSV"
      >
        <template #actions="{ row }">
          <button @click="viewMassEmail(row)" class="text-blue-600 hover:underline mr-2">View</button>
          <button @click="editMassEmail(row)" class="text-indigo-600 hover:underline mr-2" v-if="row.status === 'draft'">Edit</button>
          <button @click="sendMassEmailNow(row.id)" class="text-green-600 hover:underline mr-2" v-if="row.status === 'draft' || row.status === 'scheduled'">Send Now</button>
          <button @click="viewAnalytics(row.id)" class="text-purple-600 hover:underline" v-if="row.status === 'sent'">Analytics</button>
        </template>
      </DataTable>
    </div>

    <!-- Email Digests Tab -->
    <div v-if="activeTab === 'digests'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Email Digests</h2>
        <div class="flex gap-2">
          <button @click="sendDueDigests" class="btn btn-secondary">Send Due Digests</button>
          <button @click="createDigest" class="btn btn-primary">+ Create Digest</button>
        </div>
      </div>

      <FilterBar
        :filters="digestFilters"
        :loading="digestsLoading"
        @update:filter="updateDigestFilter"
        @clear="clearDigestFilters"
      >
        <template #filters>
          <select
            v-model="digestFilters.website_id"
            class="border rounded px-3 py-2 text-sm"
            @change="loadDigests"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
          <select
            v-model="digestFilters.is_sent"
            class="border rounded px-3 py-2 text-sm"
            @change="loadDigests"
          >
            <option value="">All</option>
            <option value="true">Sent</option>
            <option value="false">Pending</option>
          </select>
        </template>
      </FilterBar>

      <DataTable
        :columns="digestColumns"
        :data="formattedDigests"
        :loading="digestsLoading"
        :pagination="digestPagination"
        @page-change="handleDigestPageChange"
        @page-size-change="handleDigestPageSizeChange"
        @export="exportDigestsToCSV"
      >
        <template #actions="{ row }">
          <button @click="editDigest(row)" class="text-indigo-600 hover:underline mr-2" v-if="!row.is_sent">Edit</button>
          <button @click="sendDigestNow(row.id)" class="text-green-600 hover:underline" v-if="!row.is_sent">Send Now</button>
        </template>
      </DataTable>
    </div>

    <!-- Broadcast Messages Tab -->
    <div v-if="activeTab === 'broadcasts'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Broadcast Messages</h2>
        <button @click="createBroadcast" class="btn btn-primary">+ Create Broadcast</button>
      </div>

      <FilterBar
        :filters="broadcastFilters"
        :loading="broadcastsLoading"
        @update:filter="updateBroadcastFilter"
        @clear="clearBroadcastFilters"
      >
        <template #filters>
          <select
            v-model="broadcastFilters.website_id"
            class="border rounded px-3 py-2 text-sm"
            @change="loadBroadcasts"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
          <select
            v-model="broadcastFilters.is_active"
            class="border rounded px-3 py-2 text-sm"
            @change="loadBroadcasts"
          >
            <option value="">All</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </template>
      </FilterBar>

      <DataTable
        :columns="broadcastColumns"
        :data="formattedBroadcasts"
        :loading="broadcastsLoading"
        :pagination="broadcastPagination"
        @page-change="handleBroadcastPageChange"
        @page-size-change="handleBroadcastPageSizeChange"
        @export="exportBroadcastsToCSV"
      >
        <template #actions="{ row }">
          <button @click="editBroadcast(row)" class="text-indigo-600 hover:underline mr-2">Edit</button>
          <button @click="sendBroadcastNow(row.id)" class="text-green-600 hover:underline mr-2">Send Now</button>
          <button @click="previewBroadcast(row.id)" class="text-blue-600 hover:underline mr-2">Preview</button>
          <button @click="viewBroadcastStats(row.id)" class="text-purple-600 hover:underline">Stats</button>
        </template>
      </DataTable>
    </div>

    <!-- Mass Email Modal -->
    <div v-if="showMassEmailModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingMassEmail ? 'Edit Campaign' : 'Create Campaign' }}
        </h2>
        <form @submit.prevent="saveMassEmail" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Website *</label>
            <select v-model="massEmailForm.website" required class="w-full border rounded px-3 py-2">
              <option value="">Select Website</option>
              <option v-for="website in websites" :key="website.id" :value="website.id">
                {{ website.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Title *</label>
            <input v-model="massEmailForm.title" type="text" required class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Subject *</label>
            <input v-model="massEmailForm.subject" type="text" required class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Email Type *</label>
            <select v-model="massEmailForm.email_type" required class="w-full border rounded px-3 py-2">
              <option value="marketing">Marketing</option>
              <option value="promos">Promos</option>
              <option value="communication">Communication</option>
              <option value="updates">Updates</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Target Roles *</label>
            <div class="space-y-2">
              <label v-for="role in ['client', 'writer', 'editor', 'admin']" :key="role" class="flex items-center">
                <input type="checkbox" :value="role" v-model="massEmailForm.target_roles" class="mr-2" />
                <span class="capitalize">{{ role }}</span>
              </label>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Body *</label>
            <RichTextEditor
              v-model="massEmailForm.body"
              :required="true"
              placeholder="Write your email content..."
              toolbar="full"
              height="300px"
              :allow-images="true"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Scheduled Time (optional)</label>
            <input v-model="massEmailForm.scheduled_time" type="datetime-local" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeMassEmailModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingMassEmail ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Mass Email Detail Modal -->
    <div v-if="showMassEmailDetailModal && selectedMassEmail" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold">{{ selectedMassEmail.title }}</h2>
          <button @click="closeMassEmailDetailModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <strong>Subject:</strong> {{ selectedMassEmail.subject }}
          </div>
          <div>
            <strong>Status:</strong> <span class="px-2 py-1 rounded" :class="getStatusClass(selectedMassEmail.status)">{{ selectedMassEmail.status }}</span>
          </div>
          <div>
            <strong>Type:</strong> {{ selectedMassEmail.email_type }}
          </div>
          <div>
            <strong>Website:</strong> {{ selectedMassEmail.website_name }}
          </div>
          <div>
            <strong>Body:</strong>
            <div class="mt-2 p-4 bg-gray-50 rounded" v-html="selectedMassEmail.body"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Digest Modal -->
    <div v-if="showDigestModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingDigest ? 'Edit Digest' : 'Create Digest' }}
        </h2>
        <form @submit.prevent="saveDigest" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Website *</label>
            <select v-model="digestForm.website" required class="w-full border rounded px-3 py-2">
              <option value="">Select Website</option>
              <option v-for="website in websites" :key="website.id" :value="website.id">
                {{ website.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">User *</label>
            <input v-model="digestForm.user" type="number" required class="w-full border rounded px-3 py-2" placeholder="User ID" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Event Key *</label>
            <input v-model="digestForm.event_key" type="text" required class="w-full border rounded px-3 py-2" placeholder="e.g., order_updates" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Digest Group *</label>
            <input v-model="digestForm.digest_group" type="text" required class="w-full border rounded px-3 py-2" placeholder="e.g., daily_summary" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Event *</label>
            <input v-model="digestForm.event" type="text" required class="w-full border rounded px-3 py-2" placeholder="e.g., order_updates" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Scheduled For *</label>
            <input v-model="digestForm.scheduled_for" type="datetime-local" required class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Payload (JSON)</label>
            <textarea v-model="digestForm.payload" rows="5" class="w-full border rounded px-3 py-2" placeholder='{"key": "value"}'></textarea>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeDigestModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingDigest ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Broadcast Modal -->
    <div v-if="showBroadcastModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingBroadcast ? 'Edit Broadcast' : 'Create Broadcast' }}
        </h2>
        <form @submit.prevent="saveBroadcast" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Website</label>
            <select v-model="broadcastForm.website" class="w-full border rounded px-3 py-2">
              <option value="">All Websites</option>
              <option v-for="website in websites" :key="website.id" :value="website.id">
                {{ website.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Title *</label>
            <input v-model="broadcastForm.title" type="text" required class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Event Type *</label>
            <input v-model="broadcastForm.event_type" type="text" required class="w-full border rounded px-3 py-2" placeholder="e.g., system_announcement" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Message *</label>
            <div class="flex items-center justify-between mb-2">
              <p class="text-xs text-gray-500">
                Use this message for in‑app and email broadcasts. You can embed images and links.
              </p>
              <button
                type="button"
                @click="openMediaPicker"
                class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg border border-gray-200"
              >
                <span>📚</span>
                <span>Insert from Media Library</span>
              </button>
            </div>
            <RichTextEditor
              ref="broadcastEditorRef"
              v-model="broadcastForm.message"
              :required="true"
              placeholder="Write your broadcast message..."
              toolbar="basic"
              height="200px"
              :allow-images="true"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Target Roles</label>
            <div class="space-y-2">
              <label v-for="role in ['client', 'writer', 'editor', 'admin']" :key="role" class="flex items-center">
                <input type="checkbox" :value="role" v-model="broadcastForm.target_roles" class="mr-2" />
                <span class="capitalize">{{ role }}</span>
              </label>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Channels</label>
            <div class="space-y-2">
              <label v-for="channel in ['in_app', 'email', 'sms', 'push']" :key="channel" class="flex items-center">
                <input type="checkbox" :value="channel" v-model="broadcastForm.channels" class="mr-2" />
                <span class="capitalize">{{ channel.replace('_', ' ') }}</span>
              </label>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <label class="flex items-center">
              <input type="checkbox" v-model="broadcastForm.is_active" class="mr-2" />
              <span>Active</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" v-model="broadcastForm.send_email" class="mr-2" />
              <span>Send Email</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" v-model="broadcastForm.require_acknowledgement" class="mr-2" />
              <span>Require Acknowledgement</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" v-model="broadcastForm.pinned" class="mr-2" />
              <span>Pinned</span>
            </label>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Scheduled For (optional)</label>
            <input v-model="broadcastForm.scheduled_for" type="datetime-local" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Expires At (optional)</label>
            <input v-model="broadcastForm.expires_at" type="datetime-local" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeBroadcastModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingBroadcast ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Media Picker Modal for Broadcasts -->
    <div
      v-if="showMediaPicker"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click.self="showMediaPicker = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">Insert from Media Library</h2>
            <p class="text-xs text-gray-500 mt-1">
              Choose an asset to insert into the broadcast message. Images will be embedded; other files will be added as links.
            </p>
          </div>
          <button
            type="button"
            @click="showMediaPicker = false"
            class="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        <div class="px-6 py-4 space-y-4">
          <div class="flex items-center justify-between gap-3">
            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                @click="setMediaTypeAndReload('image')"
                :class="[
                  'px-3 py-1.5 text-xs rounded-full border',
                  mediaTypeFilter === 'image'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-gray-100 text-gray-700 border-gray-200'
                ]"
              >
                Images
              </button>
              <button
                type="button"
                @click="setMediaTypeAndReload('video')"
                :class="[
                  'px-3 py-1.5 text-xs rounded-full border',
                  mediaTypeFilter === 'video'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-gray-100 text-gray-700 border-gray-200'
                ]"
              >
                Videos
              </button>
              <button
                type="button"
                @click="setMediaTypeAndReload('file')"
                :class="[
                  'px-3 py-1.5 text-xs rounded-full border',
                  mediaTypeFilter === 'file'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-gray-100 text-gray-700 border-gray-200'
                ]"
              >
                Documents / Infographics
              </button>
            </div>
          </div>

          <div v-if="mediaLoading" class="py-12 text-center text-gray-500">
            Loading media…
          </div>
          <div v-else-if="!mediaAssets.length" class="py-12 text-center text-gray-500">
            No media found for this filter. Try a different type or upload assets via the Media Library page.
          </div>
          <div
            v-else
            class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4"
          >
            <button
              v-for="asset in mediaAssets"
              :key="asset.id"
              type="button"
              @click="insertMediaIntoBroadcast(asset)"
              class="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow text-left"
            >
              <div class="aspect-square bg-gray-100 flex items-center justify-center">
                <img
                  v-if="asset.type === 'image' && asset.url"
                  :src="asset.url"
                  :alt="asset.alt_text || asset.title"
                  class="w-full h-full object-cover"
                />
                <div v-else class="flex flex-col items-center justify-center text-xs text-gray-500 p-3">
                  <span v-if="asset.type === 'video'">🎥 Video</span>
                  <span v-else>📎 File</span>
                </div>
              </div>
              <div class="px-3 py-2">
                <p class="text-xs font-medium text-gray-900 truncate">
                  {{ asset.title || asset.filename || 'Untitled' }}
                </p>
                <p class="text-[11px] text-gray-500 mt-0.5 capitalize">
                  {{ asset.type }}
                </p>
              </div>
            </button>
          </div>
        </div>
        <div class="px-6 py-3 border-t border-gray-200 text-right">
          <button
            type="button"
            @click="showMediaPicker = false"
            class="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Analytics Modal -->
    <div v-if="showAnalyticsModal && analyticsData" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold">Campaign Analytics</h2>
          <button @click="closeAnalyticsModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="card">
            <div class="text-sm text-gray-500">Total Recipients</div>
            <div class="text-2xl font-bold">{{ analyticsData.total_recipients }}</div>
          </div>
          <div class="card">
            <div class="text-sm text-gray-500">Sent</div>
            <div class="text-2xl font-bold text-green-600">{{ analyticsData.sent }}</div>
          </div>
          <div class="card">
            <div class="text-sm text-gray-500">Opened</div>
            <div class="text-2xl font-bold text-blue-600">{{ analyticsData.opened }}</div>
          </div>
          <div class="card">
            <div class="text-sm text-gray-500">Open Rate</div>
            <div class="text-2xl font-bold text-purple-600">{{ analyticsData.open_rate?.toFixed(2) }}%</div>
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button @click="closeAnalyticsModal" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Stats Modal -->
    <div v-if="showStatsModal && statsData" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold">Broadcast Statistics</h2>
          <button @click="closeStatsModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="card">
            <div class="text-sm text-gray-500">Total Recipients</div>
            <div class="text-2xl font-bold">{{ statsData.total_recipients }}</div>
          </div>
          <div class="card">
            <div class="text-sm text-gray-500">Acknowledged</div>
            <div class="text-2xl font-bold text-green-600">{{ statsData.acknowledged }}</div>
          </div>
          <div class="card col-span-2">
            <div class="text-sm text-gray-500">Acknowledgement Rate</div>
            <div class="text-2xl font-bold text-purple-600">{{ statsData.acknowledgement_rate?.toFixed(2) }}%</div>
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button @click="closeStatsModal" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { debounce } from '@/utils/debounce'
import { exportToCSV } from '@/utils/export'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import DataTable from '@/components/common/DataTable.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import emailsAPI from '@/api/emails'
import apiClient from '@/api/client'
import mediaAPI from '@/api/media'

const activeTab = ref('mass-emails')
const tabs = [
  { id: 'mass-emails', label: 'Mass Emails', icon: '📧' },
  { id: 'templates', label: 'Templates', icon: '📝' },
  { id: 'digests', label: 'Email Digests', icon: '📬' },
  { id: 'broadcasts', label: 'Broadcast Messages', icon: '📢' },
]

// Mass Emails
const massEmails = ref([])
const massEmailsLoading = ref(false)
const massEmailFilters = ref({
  search: '',
  website_id: '',
  status: '',
  email_type: '',
  page: 1,
  page_size: 50,
})
const massEmailPagination = ref({
  count: 0,
  next: null,
  previous: null,
})

// Digests
const digests = ref([])
const digestsLoading = ref(false)
const digestFilters = ref({
  search: '',
  website_id: '',
  is_sent: '',
  page: 1,
  page_size: 50,
})
const digestPagination = ref({
  count: 0,
  next: null,
  previous: null,
})

// Broadcasts
const broadcasts = ref([])
const broadcastsLoading = ref(false)
const broadcastFilters = ref({
  search: '',
  website_id: '',
  is_active: '',
  page: 1,
  page_size: 50,
})
const broadcastPagination = ref({
  count: 0,
  next: null,
  previous: null,
})

// Broadcast editor + media picker
const broadcastEditorRef = ref(null)
const showMediaPicker = ref(false)
const mediaAssets = ref([])
const mediaLoading = ref(false)
const mediaTypeFilter = ref('image')

const websites = ref([])

// Email Templates
const templates = ref([])
const templatesLoading = ref(false)
const showTemplateModal = ref(false)
const editingTemplate = ref(null)
const templateForm = ref({
  name: '',
  subject: '',
  body: '',
  is_global: false,
})

// Modal states
const showMassEmailModal = ref(false)
const showMassEmailDetailModal = ref(false)
const showDigestModal = ref(false)
const showBroadcastModal = ref(false)
const showAnalyticsModal = ref(false)
const showStatsModal = ref(false)

const editingMassEmail = ref(null)
const editingDigest = ref(null)
const editingBroadcast = ref(null)
const selectedMassEmail = ref(null)
const analyticsData = ref(null)
const statsData = ref(null)
const saving = ref(false)

// Forms
const massEmailForm = ref({
  website: '',
  title: '',
  subject: '',
  body: '',
  email_type: 'marketing',
  target_roles: [],
  scheduled_time: '',
})

const digestForm = ref({
  website: '',
  user: '',
  event_key: '',
  digest_group: '',
  event: '',
  scheduled_for: '',
  payload: '{}',
})

const broadcastForm = ref({
  website: '',
  title: '',
  message: '',
  event_type: '',
  target_roles: [],
  channels: ['in_app', 'email'],
  is_active: true,
  send_email: false,
  require_acknowledgement: true,
  pinned: false,
  scheduled_for: '',
  expires_at: '',
})

// Columns
const massEmailColumns = computed(() => [
  { key: 'title', label: 'Title', sortable: true },
  { key: 'subject', label: 'Subject' },
  { key: 'status', label: 'Status' },
  { key: 'email_type', label: 'Type' },
  { key: 'website_name', label: 'Website' },
  { key: 'scheduled_time', label: 'Scheduled' },
  { key: 'sent_time', label: 'Sent' },
])

const digestColumns = computed(() => [
  { key: 'event_key', label: 'Event Key', sortable: true },
  { key: 'user_email', label: 'User' },
  { key: 'website_name', label: 'Website' },
  { key: 'scheduled_for', label: 'Scheduled For', sortable: true },
  { key: 'is_sent', label: 'Status' },
  { key: 'sent_at', label: 'Sent At' },
])

const broadcastColumns = computed(() => [
  { key: 'title', label: 'Title', sortable: true },
  { key: 'event_type', label: 'Event Type' },
  { key: 'website_name', label: 'Website' },
  { key: 'is_active', label: 'Active' },
  { key: 'scheduled_for', label: 'Scheduled' },
  { key: 'sent_at', label: 'Sent At' },
])

// Formatted data
const formattedMassEmails = computed(() => {
  return massEmails.value.map(item => ({
    ...item,
    scheduled_time: item.scheduled_time ? new Date(item.scheduled_time).toLocaleString() : 'N/A',
    sent_time: item.sent_time ? new Date(item.sent_time).toLocaleString() : 'N/A',
  }))
})

const formattedDigests = computed(() => {
  return digests.value.map(item => ({
    ...item,
    scheduled_for: item.scheduled_for ? new Date(item.scheduled_for).toLocaleString() : 'N/A',
    sent_at: item.sent_at ? new Date(item.sent_at).toLocaleString() : 'N/A',
    is_sent: item.is_sent ? 'Sent' : 'Pending',
  }))
})

const formattedBroadcasts = computed(() => {
  return broadcasts.value.map(item => ({
    ...item,
    scheduled_for: item.scheduled_for ? new Date(item.scheduled_for).toLocaleString() : 'N/A',
    sent_at: item.sent_at ? new Date(item.sent_at).toLocaleString() : 'N/A',
    is_active: item.is_active ? 'Active' : 'Inactive',
  }))
})

// Load functions
const loadMassEmails = async () => {
  massEmailsLoading.value = true
  try {
    const params = {
      page: massEmailFilters.value.page,
      page_size: massEmailFilters.value.page_size,
    }
    if (massEmailFilters.value.website_id) params.website_id = massEmailFilters.value.website_id
    if (massEmailFilters.value.status) params.status = massEmailFilters.value.status
    if (massEmailFilters.value.email_type) params.email_type = massEmailFilters.value.email_type

    const res = await emailsAPI.listMassEmails(params)
    massEmails.value = res.data.results || []
    massEmailPagination.value = {
      count: res.data.count || 0,
      next: res.data.next,
      previous: res.data.previous,
    }
  } catch (e) {
    console.error('Failed to load mass emails:', e)
  } finally {
    massEmailsLoading.value = false
  }
}

const loadDigests = async () => {
  digestsLoading.value = true
  try {
    const params = {
      page: digestFilters.value.page,
      page_size: digestFilters.value.page_size,
    }
    if (digestFilters.value.website_id) params.website_id = digestFilters.value.website_id
    if (digestFilters.value.is_sent) params.is_sent = digestFilters.value.is_sent

    const res = await emailsAPI.listDigests(params)
    digests.value = res.data.results || []
    digestPagination.value = {
      count: res.data.count || 0,
      next: res.data.next,
      previous: res.data.previous,
    }
  } catch (e) {
    console.error('Failed to load digests:', e)
  } finally {
    digestsLoading.value = false
  }
}

const loadBroadcasts = async () => {
  broadcastsLoading.value = true
  try {
    const params = {
      page: broadcastFilters.value.page,
      page_size: broadcastFilters.value.page_size,
    }
    if (broadcastFilters.value.website_id) params.website_id = broadcastFilters.value.website_id
    if (broadcastFilters.value.is_active) params.is_active = broadcastFilters.value.is_active

    const res = await emailsAPI.listBroadcasts(params)
    broadcasts.value = res.data.results || []
    broadcastPagination.value = {
      count: res.data.count || 0,
      next: res.data.next,
      previous: res.data.previous,
    }
  } catch (e) {
    console.error('Failed to load broadcasts:', e)
  } finally {
    broadcastsLoading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadData = () => {
  if (activeTab.value === 'mass-emails') {
    loadMassEmails()
  } else if (activeTab.value === 'templates') {
    loadTemplates()
  } else if (activeTab.value === 'digests') {
    loadDigests()
  } else if (activeTab.value === 'broadcasts') {
    loadBroadcasts()
  }
}

// Filter functions
const updateMassEmailFilter = (key, value) => {
  massEmailFilters.value[key] = value
  massEmailFilters.value.page = 1
  loadMassEmails()
}

const clearMassEmailFilters = () => {
  massEmailFilters.value = {
    search: '',
    website_id: '',
    status: '',
    email_type: '',
    page: 1,
    page_size: 50,
  }
  loadMassEmails()
}

const updateDigestFilter = (key, value) => {
  digestFilters.value[key] = value
  digestFilters.value.page = 1
  loadDigests()
}

const clearDigestFilters = () => {
  digestFilters.value = {
    search: '',
    website_id: '',
    is_sent: '',
    page: 1,
    page_size: 50,
  }
  loadDigests()
}

const updateBroadcastFilter = (key, value) => {
  broadcastFilters.value[key] = value
  broadcastFilters.value.page = 1
  loadBroadcasts()
}

const clearBroadcastFilters = () => {
  broadcastFilters.value = {
    search: '',
    website_id: '',
    is_active: '',
    page: 1,
    page_size: 50,
  }
  loadBroadcasts()
}

// Pagination
const handleMassEmailPageChange = (url) => {
  if (!url) return
  const urlObj = new URL(url)
  massEmailFilters.value.page = parseInt(urlObj.searchParams.get('page')) || 1
  loadMassEmails()
}

const handleMassEmailPageSizeChange = () => {
  massEmailFilters.value.page = 1
  loadMassEmails()
}

const handleDigestPageChange = (url) => {
  if (!url) return
  const urlObj = new URL(url)
  digestFilters.value.page = parseInt(urlObj.searchParams.get('page')) || 1
  loadDigests()
}

const handleDigestPageSizeChange = () => {
  digestFilters.value.page = 1
  loadDigests()
}

const handleBroadcastPageChange = (url) => {
  if (!url) return
  const urlObj = new URL(url)
  broadcastFilters.value.page = parseInt(urlObj.searchParams.get('page')) || 1
  loadBroadcasts()
}

const handleBroadcastPageSizeChange = () => {
  broadcastFilters.value.page = 1
  loadBroadcasts()
}

// Media picker for broadcasts
const loadMediaAssets = async () => {
  mediaLoading.value = true
  try {
    const params = {
      page: 1,
      page_size: 30,
      type: mediaTypeFilter.value || undefined,
    }
    if (broadcastForm.value.website) {
      params.website_id = broadcastForm.value.website
    }
    const res = await mediaAPI.list(params)
    mediaAssets.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load media assets for picker:', e)
  } finally {
    mediaLoading.value = false
  }
}

const openMediaPicker = () => {
  showMediaPicker.value = true
  loadMediaAssets()
}

const setMediaTypeAndReload = (type) => {
  mediaTypeFilter.value = type
  loadMediaAssets()
}

const insertMediaIntoBroadcast = (asset) => {
  if (!asset || !asset.url) return
  const editorApi = broadcastEditorRef.value
  const quill = editorApi?.getQuillInstance?.()
  if (!quill) {
    console.warn('Broadcast editor Quill instance not available')
    return
  }

  const range = quill.getSelection(true) || { index: quill.getLength(), length: 0 }

  if (asset.type === 'image') {
    quill.insertEmbed(range.index, 'image', asset.url)
    quill.setSelection(range.index + 1, 0)
  } else {
    const label = asset.title || asset.filename || asset.url
    const linkText = `[${asset.type}] ${label}`
    quill.insertText(range.index, linkText + ' ', 'link', asset.url)
    quill.setSelection(range.index + linkText.length + 1, 0)
  }

  showMediaPicker.value = false
}

// Actions
const createMassEmail = () => {
  editingMassEmail.value = null
  massEmailForm.value = {
    website: '',
    title: '',
    subject: '',
    body: '',
    email_type: 'marketing',
    target_roles: [],
    scheduled_time: '',
  }
  showMassEmailModal.value = true
}

const editMassEmail = async (row) => {
  try {
    const res = await emailsAPI.getMassEmail(row.id)
    const data = res.data
    editingMassEmail.value = data
    // Handle website - could be ID or object
    let websiteId = ''
    if (typeof data.website === 'object' && data.website?.id) {
      websiteId = data.website.id
    } else if (typeof data.website === 'number') {
      websiteId = data.website
    } else {
      // Try to find by name if it's a string
      const website = websites.value.find(w => w.name === data.website || w.id === data.website)
      websiteId = website?.id || ''
    }
    
    massEmailForm.value = {
      website: websiteId,
      title: data.title || '',
      subject: data.subject || '',
      body: data.body || '',
      email_type: data.email_type || 'marketing',
      target_roles: data.target_roles || [],
      scheduled_time: data.scheduled_time ? new Date(data.scheduled_time).toISOString().slice(0, 16) : '',
    }
    showMassEmailModal.value = true
  } catch (e) {
    alert('Failed to load campaign: ' + (e.response?.data?.detail || e.message))
  }
}

const saveMassEmail = async () => {
  saving.value = true
  try {
    const data = {
      ...massEmailForm.value,
      scheduled_time: massEmailForm.value.scheduled_time || null,
    }
    if (editingMassEmail.value) {
      await emailsAPI.updateMassEmail(editingMassEmail.value.id, data)
    } else {
      await emailsAPI.createMassEmail(data)
    }
    showMassEmailModal.value = false
    loadMassEmails()
  } catch (e) {
    alert('Failed to save campaign: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message))
  } finally {
    saving.value = false
  }
}

const closeMassEmailModal = () => {
  showMassEmailModal.value = false
  editingMassEmail.value = null
}

const viewMassEmail = async (row) => {
  try {
    const res = await emailsAPI.getMassEmail(row.id)
    selectedMassEmail.value = res.data
    showMassEmailDetailModal.value = true
  } catch (e) {
    alert('Failed to load campaign details: ' + (e.response?.data?.detail || e.message))
  }
}

const closeMassEmailDetailModal = () => {
  showMassEmailDetailModal.value = false
  selectedMassEmail.value = null
}

const sendMassEmailNow = async (id) => {
  if (!confirm('Are you sure you want to send this campaign now?')) return
  try {
    await emailsAPI.sendMassEmailNow(id)
    alert('Campaign sending started')
    loadMassEmails()
  } catch (e) {
    alert('Failed to send campaign: ' + (e.response?.data?.detail || e.message))
  }
}

const viewAnalytics = async (id) => {
  try {
    const res = await emailsAPI.getMassEmailAnalytics(id)
    analyticsData.value = res.data
    showAnalyticsModal.value = true
  } catch (e) {
    alert('Failed to load analytics: ' + (e.response?.data?.detail || e.message))
  }
}

const closeAnalyticsModal = () => {
  showAnalyticsModal.value = false
  analyticsData.value = null
}

const createDigest = () => {
  editingDigest.value = null
  digestForm.value = {
    website: '',
    user: '',
    event_key: '',
    digest_group: '',
    event: '',
    scheduled_for: '',
    payload: '{}',
  }
  showDigestModal.value = true
}

const editDigest = (row) => {
  editingDigest.value = row
  // Handle website - could be ID or object
  let websiteId = ''
  if (typeof row.website === 'object' && row.website?.id) {
    websiteId = row.website.id
  } else if (typeof row.website === 'number') {
    websiteId = row.website
  } else {
    const website = websites.value.find(w => w.name === row.website || w.id === row.website)
    websiteId = website?.id || ''
  }
  
  // Handle user - could be ID or object
  let userId = ''
  if (typeof row.user === 'object' && row.user?.id) {
    userId = row.user.id
  } else if (typeof row.user === 'number') {
    userId = row.user
  } else {
    userId = row.user || ''
  }
  
  digestForm.value = {
    website: websiteId,
    user: userId,
    event_key: row.event_key || '',
    digest_group: row.digest_group || '',
    event: row.event || '',
    scheduled_for: row.scheduled_for ? new Date(row.scheduled_for).toISOString().slice(0, 16) : '',
    payload: typeof row.payload === 'string' ? row.payload : JSON.stringify(row.payload || {}),
  }
  showDigestModal.value = true
}

const saveDigest = async () => {
  saving.value = true
  try {
    const data = {
      ...digestForm.value,
      scheduled_for: digestForm.value.scheduled_for || null,
      payload: digestForm.value.payload ? JSON.parse(digestForm.value.payload) : {},
    }
    if (editingDigest.value) {
      await emailsAPI.updateDigest(editingDigest.value.id, data)
    } else {
      await emailsAPI.createDigest(data)
    }
    showDigestModal.value = false
    loadDigests()
  } catch (e) {
    alert('Failed to save digest: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message))
  } finally {
    saving.value = false
  }
}

const closeDigestModal = () => {
  showDigestModal.value = false
  editingDigest.value = null
}

const sendDigestNow = async (id) => {
  if (!confirm('Are you sure you want to send this digest now?')) return
  try {
    await emailsAPI.sendDigestNow(id)
    alert('Digest sent')
    loadDigests()
  } catch (e) {
    alert('Failed to send digest: ' + (e.response?.data?.detail || e.message))
  }
}

const sendDueDigests = async () => {
  if (!confirm('Are you sure you want to send all due digests?')) return
  try {
    await emailsAPI.sendDueDigests()
    alert('Due digests sent')
    loadDigests()
  } catch (e) {
    alert('Failed to send digests: ' + (e.response?.data?.detail || e.message))
  }
}

const createBroadcast = () => {
  editingBroadcast.value = null
  broadcastForm.value = {
    website: '',
    title: '',
    message: '',
    event_type: '',
    target_roles: [],
    channels: ['in_app', 'email'],
    is_active: true,
    send_email: false,
    require_acknowledgement: true,
    pinned: false,
    scheduled_for: '',
    expires_at: '',
  }
  showBroadcastModal.value = true
}

const editBroadcast = (row) => {
  editingBroadcast.value = row
  // Handle website - could be ID, object, or null
  let websiteId = ''
  if (row.website) {
    if (typeof row.website === 'object' && row.website?.id) {
      websiteId = row.website.id
    } else if (typeof row.website === 'number') {
      websiteId = row.website
    } else {
      const website = websites.value.find(w => w.name === row.website || w.id === row.website)
      websiteId = website?.id || ''
    }
  }
  
  broadcastForm.value = {
    website: websiteId,
    title: row.title || '',
    message: row.message || '',
    event_type: row.event_type || '',
    target_roles: row.target_roles || [],
    channels: row.channels || ['in_app', 'email'],
    is_active: row.is_active !== false,
    send_email: row.send_email || false,
    require_acknowledgement: row.require_acknowledgement !== false,
    pinned: row.pinned || false,
    scheduled_for: row.scheduled_for ? new Date(row.scheduled_for).toISOString().slice(0, 16) : '',
    expires_at: row.expires_at ? new Date(row.expires_at).toISOString().slice(0, 16) : '',
  }
  showBroadcastModal.value = true
}

const saveBroadcast = async () => {
  saving.value = true
  try {
    const data = {
      ...broadcastForm.value,
      scheduled_for: broadcastForm.value.scheduled_for || null,
      expires_at: broadcastForm.value.expires_at || null,
      website: broadcastForm.value.website || null,
    }
    if (editingBroadcast.value) {
      await emailsAPI.updateBroadcast(editingBroadcast.value.id, data)
    } else {
      await emailsAPI.createBroadcast(data)
    }
    showBroadcastModal.value = false
    loadBroadcasts()
  } catch (e) {
    alert('Failed to save broadcast: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message))
  } finally {
    saving.value = false
  }
}

const closeBroadcastModal = () => {
  showBroadcastModal.value = false
  editingBroadcast.value = null
}

const sendBroadcastNow = async (id) => {
  if (!confirm('Are you sure you want to send this broadcast now?')) return
  try {
    await emailsAPI.sendBroadcastNow(id)
    alert('Broadcast sent')
    loadBroadcasts()
  } catch (e) {
    alert('Failed to send broadcast: ' + (e.response?.data?.detail || e.message))
  }
}

const previewBroadcast = async (id) => {
  try {
    await emailsAPI.previewBroadcast(id)
    alert('Preview sent to your email')
  } catch (e) {
    alert('Failed to send preview: ' + (e.response?.data?.detail || e.message))
  }
}

const viewBroadcastStats = async (id) => {
  try {
    const res = await emailsAPI.getBroadcastStats(id)
    statsData.value = res.data
    showStatsModal.value = true
  } catch (e) {
    alert('Failed to load stats: ' + (e.response?.data?.detail || e.message))
  }
}

const closeStatsModal = () => {
  showStatsModal.value = false
  statsData.value = null
}

const getStatusClass = (status) => {
  const classes = {
    draft: 'bg-gray-100 text-gray-800',
    scheduled: 'bg-blue-100 text-blue-800',
    sending: 'bg-yellow-100 text-yellow-800',
    sent: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

// Export
const exportMassEmailsToCSV = () => {
  exportToCSV(formattedMassEmails.value, 'mass-emails.csv')
}

const exportDigestsToCSV = () => {
  exportToCSV(formattedDigests.value, 'digests.csv')
}

const exportBroadcastsToCSV = () => {
  exportToCSV(formattedBroadcasts.value, 'broadcasts.csv')
}

// Template Management
const loadTemplates = async () => {
  templatesLoading.value = true
  try {
    const res = await emailsAPI.listTemplates()
    templates.value = res.data.results || res.data || []
  } catch (e) {
    console.error('Failed to load templates:', e)
    alert('Failed to load templates: ' + (e.response?.data?.detail || e.message))
  } finally {
    templatesLoading.value = false
  }
}

const createTemplate = () => {
  editingTemplate.value = null
  templateForm.value = {
    name: '',
    subject: '',
    body: '',
    is_global: false,
  }
  showTemplateModal.value = true
}

const editTemplate = (template) => {
  editingTemplate.value = template
  templateForm.value = {
    name: template.name,
    subject: template.subject,
    body: template.body,
    is_global: template.is_global,
  }
  showTemplateModal.value = true
}

const saveTemplate = async () => {
  saving.value = true
  try {
    if (editingTemplate.value) {
      await emailsAPI.updateTemplate(editingTemplate.value.id, templateForm.value)
    } else {
      await emailsAPI.createTemplate(templateForm.value)
    }
    showTemplateModal.value = false
    loadTemplates()
  } catch (e) {
    alert('Failed to save template: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

const deleteTemplate = async (id) => {
  if (!confirm('Are you sure you want to delete this template?')) return
  try {
    await emailsAPI.deleteTemplate(id)
    loadTemplates()
  } catch (e) {
    alert('Failed to delete template: ' + (e.response?.data?.detail || e.message))
  }
}

const useTemplate = (template) => {
  activeTab.value = 'mass-emails'
  massEmailForm.value.subject = template.subject
  massEmailForm.value.body = template.body
  createMassEmail()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// Watch for tab changes
watch(activeTab, () => {
  if (activeTab.value === 'templates') {
    loadTemplates()
  } else {
    loadData()
  }
})

onMounted(async () => {
  await loadWebsites()
  loadData()
})
</script>

<style scoped>
@reference "tailwindcss";
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-200 text-gray-700 hover:bg-gray-300;
}
.card {
  @apply bg-white rounded-lg shadow-sm p-4;
}
</style>

