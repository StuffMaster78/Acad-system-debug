<template>
  <div class="order-messages-tabbed">

    <!-- Header with New Message Button -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">Conversations</h2>
          <p v-if="authStore.isWriter" class="text-sm text-gray-600 dark:text-gray-400">
            Message the client, admin, support, or editor about this order
          </p>
        </div>
        <button
          @click="openNewMessageModal"
          class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium transition-all shadow-sm hover:shadow-md"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          New Message
        </button>
      </div>
    </div>

    <!-- Recipient Type Tabs -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6 overflow-hidden">
      <nav class="flex border-b border-gray-200 dark:border-gray-700" aria-label="Tabs">
        <button
          v-for="tab in recipientTabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors relative',
            activeTab === tab.id
              ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50'
          ]"
        >
          <component :is="tab.icon" class="w-5 h-5" />
          <span>{{ tab.label }}</span>
          <span
            v-if="getUnreadCountForTab(tab.id) > 0"
            class="ml-1 px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold"
          >
            {{ getUnreadCountForTab(tab.id) }}
          </span>
          <span
            v-if="activeTab === tab.id"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400"
          ></span>
        </button>
      </nav>
    </div>

    <!-- Threads List -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div v-if="loadingThreads" class="p-16 text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600 dark:text-gray-400 font-medium">Loading conversations...</p>
      </div>

      <div v-else-if="filteredThreads.length === 0" class="p-16 text-center">
        <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
          <svg class="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {{ threads.length === 0 ? 'No conversations yet' : 'No conversations in this tab' }}
        </h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-6 max-w-md mx-auto">
          <span v-if="threads.length === 0">
            Start a new conversation by clicking "New Message" above to communicate about this order.
          </span>
          <span v-else>
            There are {{ threads.length }} conversation(s) for this order, but none match the "{{ recipientTabs.find(t => t.id === activeTab)?.label || activeTab }}" tab. Try switching to another tab.
          </span>
        </p>
        <button
          v-if="threads.length === 0"
          @click="openNewMessageModal"
          class="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm hover:shadow-md"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Start Conversation
        </button>
      </div>

      <div v-else class="space-y-6">
        <!-- Group: From Client to Me -->
        <div v-if="groupedThreads.fromClient.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            From Client to Me
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in groupedThreads.fromClient"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div 
                @click="expandThread(thread)"
                class="p-5 cursor-pointer"
              >
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span
                            v-if="thread.unread_count > 0"
                            class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0"
                          >
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">
                          {{ getThreadSubtitle(thread) }}
                        </p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button
                  @click.stop="openThread(thread)"
                  class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm"
                >
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Group: From Me to Client -->
        <div v-if="groupedThreads.toClient.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            From Me to Client
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in groupedThreads.toClient"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div @click="expandThread(thread)" class="p-5 cursor-pointer">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span v-if="thread.unread_count > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0">
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ getThreadSubtitle(thread) }}</p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button @click.stop="openThread(thread)" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm">
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Group: From Admin/SuperAdmin/Support to Me -->
        <div v-if="groupedThreads.fromAdmin.length > 0 || groupedThreads.fromSupport.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            From Admin/Support to Me
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in [...groupedThreads.fromAdmin, ...groupedThreads.fromSupport]"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div @click="expandThread(thread)" class="p-5 cursor-pointer">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span v-if="thread.unread_count > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0">
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ getThreadSubtitle(thread) }}</p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button @click.stop="openThread(thread)" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm">
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Group: From Me to Admin/SuperAdmin/Support -->
        <div v-if="groupedThreads.toAdmin.length > 0 || groupedThreads.toSupport.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            From Me to Admin/Support
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in [...groupedThreads.toAdmin, ...groupedThreads.toSupport]"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div @click="expandThread(thread)" class="p-5 cursor-pointer">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span v-if="thread.unread_count > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0">
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ getThreadSubtitle(thread) }}</p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button @click.stop="openThread(thread)" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm">
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Group: From Writer to Me -->
        <div v-if="groupedThreads.fromWriter.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            From Writer to Me
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in groupedThreads.fromWriter"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div @click="expandThread(thread)" class="p-5 cursor-pointer">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span v-if="thread.unread_count > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0">
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ getThreadSubtitle(thread) }}</p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button @click.stop="openThread(thread)" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm">
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Group: From Me to Writer -->
        <div v-if="groupedThreads.toWriter.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            From Me to Writer
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in groupedThreads.toWriter"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div @click="expandThread(thread)" class="p-5 cursor-pointer">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span v-if="thread.unread_count > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0">
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ getThreadSubtitle(thread) }}</p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button @click.stop="openThread(thread)" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm">
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Group: From Editor to Me -->
        <div v-if="groupedThreads.fromEditor.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            From Editor to Me
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in groupedThreads.fromEditor"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div @click="expandThread(thread)" class="p-5 cursor-pointer">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span v-if="thread.unread_count > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0">
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ getThreadSubtitle(thread) }}</p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button @click.stop="openThread(thread)" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm">
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Group: From Me to Editor -->
        <div v-if="groupedThreads.toEditor.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            From Me to Editor
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in groupedThreads.toEditor"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div @click="expandThread(thread)" class="p-5 cursor-pointer">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span v-if="thread.unread_count > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0">
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ getThreadSubtitle(thread) }}</p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button @click.stop="openThread(thread)" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm">
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Group: Other -->
        <div v-if="groupedThreads.other.length > 0" class="space-y-3">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide px-2">
            Other Conversations
          </h3>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="thread in groupedThreads.other"
              :key="thread.id"
              class="transition-all border-l-4"
              :class="thread.unread_count > 0 
                ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
                : selectedThreadId === thread.id
                  ? 'bg-gray-50 dark:bg-gray-700/50 border-l-gray-400'
                  : 'border-l-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'"
            >
              <div @click="expandThread(thread)" class="p-5 cursor-pointer">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-4 mb-3">
                      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold shrink-0 shadow-sm">
                        {{ getThreadInitials(thread) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-base">
                            {{ getThreadTitle(thread) }}
                          </h3>
                          <span v-if="thread.unread_count > 0" class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-semibold shrink-0">
                            {{ thread.unread_count }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{{ getThreadSubtitle(thread) }}</p>
                      </div>
                    </div>
                    <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 ml-16">
                      {{ thread.last_message.message || '📎 File attachment' }}
                    </p>
                  </div>
                  <div class="flex flex-col items-end gap-2 shrink-0">
                    <span class="text-xs font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="px-5 pb-3 flex items-center gap-2 border-t border-gray-200 dark:border-gray-700">
                <button @click.stop="openThread(thread)" class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors text-sm">
                  Open Full View
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Message Modal (Order-Specific) -->
    <OrderNewMessageModal
      v-if="showNewMessageModal"
      :show="showNewMessageModal"
      :order-id="orderId"
      :default-recipient-type="activeTab"
      @close="showNewMessageModal = false"
      @message-sent="handleMessageSent"
    />

    <!-- Expanded Thread View (Inline) -->
    <div v-if="selectedThread" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6 overflow-hidden">
      <div class="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4 flex-1">
            <div class="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white font-bold text-lg">
              {{ getThreadInitials(selectedThread) }}
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-xl font-bold text-white truncate">{{ getThreadTitle(selectedThread) }}</h3>
              <div class="flex items-center gap-4 mt-1 text-sm text-blue-100">
                <span>{{ getThreadSubtitle(selectedThread) }}</span>
                <span v-if="selectedThread.order || selectedThread.order_id" class="flex items-center gap-1">
                  <span>•</span>
                  <span>Order #{{ selectedThread.order?.id || selectedThread.order_id }}</span>
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <router-link
              :to="`/messages/thread/${selectedThread.id}`"
              class="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg font-medium transition-colors text-sm"
            >
              Open Full View
            </router-link>
            <button 
              @click="closeThread" 
              class="text-white/80 hover:text-white hover:bg-white/20 rounded-lg p-1.5 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Thread Details -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-600 dark:text-gray-400 font-medium">Sender:</span>
            <span class="ml-2 text-gray-900 dark:text-white">
              {{ getSenderInfo(selectedThread) }}
            </span>
          </div>
          <div>
            <span class="text-gray-600 dark:text-gray-400 font-medium">Recipient:</span>
            <span class="ml-2 text-gray-900 dark:text-white">
              {{ getRecipientInfo(selectedThread) }}
            </span>
          </div>
          <div>
            <span class="text-gray-600 dark:text-gray-400 font-medium">Last Message:</span>
            <span class="ml-2 text-gray-900 dark:text-white">
              {{ formatTime(selectedThread.last_message?.sent_at || selectedThread.updated_at) }}
            </span>
          </div>
          <div>
            <span class="text-gray-600 dark:text-gray-400 font-medium">Status:</span>
            <span class="ml-2">
              <span 
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="selectedThread.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'"
              >
                {{ selectedThread.is_active ? 'Active' : 'Inactive' }}
              </span>
            </span>
          </div>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <router-link
          :to="`/messages/thread/${selectedThread.id}`"
          class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          View All Messages
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { communicationsAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import messagesStore from '@/stores/messages'
import OrderNewMessageModal from '@/components/order/OrderNewMessageModal.vue'
import { useToast } from '@/composables/useToast'
import { useRouter } from 'vue-router'

const { success: showSuccess, error: showError } = useToast()

const props = defineProps({
  orderId: {
    type: [Number, String],
    required: true
  },
  orderTopic: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['unread-count-update'])

const router = useRouter()
const authStore = useAuthStore()
const currentUser = authStore.user

// Initialize state variables first
// Admin/support default to "all" tab to see all messages
const getInitialTab = () => {
  if (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) {
    return 'all'
  }
  return 'admin'
}
const activeTab = ref(getInitialTab())
const threads = ref([])
const loadingThreads = ref(false)
const showNewMessageModal = ref(false)
const selectedThread = ref(null)
const selectedThreadId = ref(null)

// Tabs configuration based on user role
const recipientTabs = computed(() => {
  const role = currentUser?.role
  const tabs = []

  if (role === 'client') {
    tabs.push(
      { id: 'admin', label: 'To Admin', icon: 'AdminIcon', roles: ['admin', 'superadmin'] },
      { id: 'support', label: 'To Support', icon: 'SupportIcon', roles: ['support'] },
      { id: 'writer', label: 'To Writer', icon: 'WriterIcon', roles: ['writer'] },
      { id: 'editor', label: 'To Editor', icon: 'EditorIcon', roles: ['editor'] }
    )
  } else if (role === 'writer') {
    tabs.push(
      { id: 'client', label: 'To Client', icon: 'ClientIcon', roles: ['client'] },
      { id: 'admin', label: 'To Admin', icon: 'AdminIcon', roles: ['admin', 'superadmin'] },
      { id: 'support', label: 'To Support', icon: 'SupportIcon', roles: ['support'] },
      { id: 'editor', label: 'To Editor', icon: 'EditorIcon', roles: ['editor'] }
    )
  } else if (role === 'admin' || role === 'superadmin') {
    // Admin/support see all tabs and can view all conversations
    tabs.push(
      { id: 'all', label: 'All Messages', icon: 'AllIcon', roles: ['client', 'writer', 'admin', 'superadmin', 'support', 'editor'] },
      { id: 'client', label: 'To Client', icon: 'ClientIcon', roles: ['client'] },
      { id: 'writer', label: 'To Writer', icon: 'WriterIcon', roles: ['writer'] },
      { id: 'editor', label: 'To Editor', icon: 'EditorIcon', roles: ['editor'] },
      { id: 'support', label: 'To Support', icon: 'SupportIcon', roles: ['support'] }
    )
  } else if (role === 'support') {
    // Support sees all tabs and can view all conversations
    tabs.push(
      { id: 'all', label: 'All Messages', icon: 'AllIcon', roles: ['client', 'writer', 'admin', 'superadmin', 'support', 'editor'] },
      { id: 'client', label: 'To Client', icon: 'ClientIcon', roles: ['client'] },
      { id: 'writer', label: 'To Writer', icon: 'WriterIcon', roles: ['writer'] },
      { id: 'admin', label: 'To Admin', icon: 'AdminIcon', roles: ['admin', 'superadmin'] },
      { id: 'editor', label: 'To Editor', icon: 'EditorIcon', roles: ['editor'] }
    )
  } else if (role === 'editor') {
    tabs.push(
      { id: 'client', label: 'To Client', icon: 'ClientIcon', roles: ['client'] },
      { id: 'writer', label: 'To Writer', icon: 'WriterIcon', roles: ['writer'] },
      { id: 'admin', label: 'To Admin', icon: 'AdminIcon', roles: ['admin', 'superadmin'] },
      { id: 'support', label: 'To Support', icon: 'SupportIcon', roles: ['support'] }
    )
  }

  return tabs
})

// Set active tab after recipientTabs is computed
watch(recipientTabs, (tabs) => {
  if (tabs.length > 0 && !tabs.find(t => t.id === activeTab.value)) {
    activeTab.value = tabs[0].id
  }
}, { immediate: true })

// Computed property for total unread count across all tabs
const totalUnreadCount = computed(() => {
  if (!threads.value || !Array.isArray(threads.value)) {
    return 0
  }
  const orderThreads = threads.value.filter(thread => {
    const threadOrderId = thread.order || thread.order_id
    return threadOrderId && parseInt(threadOrderId) === parseInt(props.orderId)
  })
  
  return orderThreads.reduce((sum, thread) => {
    return sum + (thread.unread_count || 0)
  }, 0)
})

// Watch for changes in total unread count and emit to parent
watch(totalUnreadCount, (newCount) => {
  if (threads.value !== undefined) {
    emit('unread-count-update', newCount)
  }
}, { immediate: true }) // Changed to immediate: true to emit initial count

// Icon components
const AdminIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>' }
const ClientIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>' }
const WriterIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>' }
const EditorIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>' }
const SupportIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" /></svg>' }
const AllIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>' }

// Helper: derive the "other participant" role for this thread relative to the current user.
// We prioritize the recipient_role from the last message to determine which tab to show it under.
// This ensures threads appear in only ONE tab based on who the message was sent TO.
const getOtherParticipantRoles = (thread) => {
  const roles = new Set()
  const viewerRole = currentUser?.role || null

  // PRIORITY 1: Use recipient_role from last message (most reliable for tab filtering)
  // This tells us who the message was sent TO, which determines the tab
  const last = thread.last_message
  if (last && last.recipient_role) {
    // The recipient_role is the definitive answer for which tab this thread belongs to
    // If admin sends to support, recipient_role is 'support' -> appears in Support tab only
    // If admin sends to client, recipient_role is 'client' -> appears in Client tab only
    // IMPORTANT: We ONLY use recipient_role and ignore participant roles to prevent
    // threads from appearing in multiple tabs
    const recipientRole = last.recipient_role
    // Normalize role (e.g., 'superadmin' -> 'admin' for tab matching)
    if (recipientRole === 'superadmin') {
      roles.add('admin')
    } else {
      roles.add(recipientRole)
    }
    // Return early with just the recipient role to avoid matching multiple tabs
    return Array.from(roles)
  }

  // PRIORITY 2: Fallback to participant roles if no last message
  // But only if we're the viewer, we want to know who the OTHER participants are
  const participants = thread.participants || []
  const otherParticipants = participants.filter(p => {
    const participantId = typeof p === 'object' ? p.id : p
    return participantId !== currentUser?.id
  })

  // Extract roles from other participants (fallback only)
  otherParticipants.forEach(p => {
    const role = typeof p === 'object' ? p.role : null
    if (role) roles.add(role)
  })

  return Array.from(roles)
}

const filteredThreads = computed(() => {
  const activeTabData = recipientTabs.value.find(t => t.id === activeTab.value)
  if (!activeTabData) return []

  // Filter threads that are related to this order
  const orderThreads = threads.value.filter(thread => {
    const threadOrderId = thread.order || thread.order_id
    return threadOrderId && parseInt(threadOrderId) === parseInt(props.orderId)
  })

  // If "All Messages" tab is selected (for admin/support), show all threads
  if (activeTab.value === 'all' && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)) {
    return orderThreads.sort((a, b) => {
      const aTime = a.last_message?.sent_at || a.updated_at || a.created_at
      const bTime = b.last_message?.sent_at || b.updated_at || b.created_at
      return new Date(bTime) - new Date(aTime)
    })
  }

  // Filter threads based on the recipient role of the last message
  // This ensures threads appear under the correct tab (only ONE tab)
  return orderThreads.filter(thread => {
    const otherRoles = getOtherParticipantRoles(thread)
    if (!otherRoles.length) {
      // If no roles found, check if thread has participants with roles
      const participants = thread.participants || []
      const otherParticipants = participants.filter(p => {
        const participantId = typeof p === 'object' ? p.id : p
        return participantId !== currentUser?.id
      })
      
      // Extract roles from participants
      const participantRoles = otherParticipants
        .map(p => typeof p === 'object' ? p.role : null)
        .filter(Boolean)
      
      if (participantRoles.length > 0) {
        // Only match if ONE of the participant roles matches the active tab
        return participantRoles.some(role => activeTabData.roles.includes(role))
      }
      
      return false
    }
    
    // Check if the recipient role (from last message) matches the active tab
    // This ensures threads appear in only ONE tab based on who the message was sent TO
    return otherRoles.some(role => activeTabData.roles.includes(role))
  }).sort((a, b) => {
    // Sort by last message time or updated time (newest first)
    const aTime = a.last_message?.sent_at || a.updated_at || a.created_at
    const bTime = b.last_message?.sent_at || b.updated_at || b.created_at
    return new Date(bTime) - new Date(aTime)
  })
})

// Group threads by direction
const groupedThreads = computed(() => {
  const groups = {
    fromClient: [],
    toClient: [],
    fromAdmin: [],
    toAdmin: [],
    fromSupport: [],
    toSupport: [],
    fromWriter: [],
    toWriter: [],
    fromEditor: [],
    toEditor: [],
    other: []
  }

  filteredThreads.value.forEach(thread => {
    const lastMessage = thread.last_message
    if (!lastMessage) {
      groups.other.push(thread)
      return
    }

    const senderRole = lastMessage.sender_role
    const recipientRole = lastMessage.recipient_role
    const senderId = lastMessage.sender?.id || (typeof lastMessage.sender === 'object' ? lastMessage.sender?.id : lastMessage.sender)
    const isFromMe = senderId === currentUser?.id

    // Determine direction based on last message
    // "From X to Me" means sender is X and I'm the recipient
    // "From Me to X" means I'm the sender and recipient is X
    
    if (senderRole === 'client' && !isFromMe) {
      // Client sent to me
      groups.fromClient.push(thread)
    } else if (recipientRole === 'client' && isFromMe) {
      // I sent to client
      groups.toClient.push(thread)
    } else if ((senderRole === 'admin' || senderRole === 'superadmin') && !isFromMe) {
      // Admin/SuperAdmin sent to me
      groups.fromAdmin.push(thread)
    } else if ((recipientRole === 'admin' || recipientRole === 'superadmin') && isFromMe) {
      // I sent to Admin/SuperAdmin
      groups.toAdmin.push(thread)
    } else if (senderRole === 'support' && !isFromMe) {
      // Support sent to me
      groups.fromSupport.push(thread)
    } else if (recipientRole === 'support' && isFromMe) {
      // I sent to Support
      groups.toSupport.push(thread)
    } else if (senderRole === 'writer' && !isFromMe) {
      // Writer sent to me
      groups.fromWriter.push(thread)
    } else if (recipientRole === 'writer' && isFromMe) {
      // I sent to Writer
      groups.toWriter.push(thread)
    } else if (senderRole === 'editor' && !isFromMe) {
      // Editor sent to me
      groups.fromEditor.push(thread)
    } else if (recipientRole === 'editor' && isFromMe) {
      // I sent to Editor
      groups.toEditor.push(thread)
    } else {
      // Fallback: use participant roles if last message doesn't have role info
      const otherParticipants = thread.participants?.filter(p => {
        const participantId = typeof p === 'object' ? p.id : p
        return participantId !== currentUser?.id
      }) || []
      
      if (otherParticipants.length > 0) {
        const otherRole = typeof otherParticipants[0] === 'object' ? otherParticipants[0].role : null
        if (otherRole === 'client') {
          groups.fromClient.push(thread)
        } else if (otherRole === 'writer') {
          groups.fromWriter.push(thread)
        } else if (otherRole === 'editor') {
          groups.fromEditor.push(thread)
        } else if (otherRole === 'support') {
          groups.fromSupport.push(thread)
        } else if (otherRole === 'admin' || otherRole === 'superadmin') {
          groups.fromAdmin.push(thread)
        } else {
          groups.other.push(thread)
        }
      } else {
        groups.other.push(thread)
      }
    }
  })

  return groups
})

const loadThreads = async (forceRefresh = false) => {
  loadingThreads.value = true
  try {
    // Always use direct API call with order filter for order-specific messages
    // This ensures we get all threads for this specific order
    const response = await communicationsAPI.listThreads({ order: props.orderId })
    const allThreads = response.data?.results || response.data || []
    
    // Filter threads that belong to this order (double-check)
    threads.value = allThreads.filter(thread => {
      const threadOrderId = thread.order || thread.order_id
      const matches = threadOrderId && parseInt(threadOrderId) === parseInt(props.orderId)
      return matches
    })
    
    // Debug logging for admin/support
    if (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) {
      console.log(`[OrderMessagesTabbed] Loaded ${threads.value.length} threads for order ${props.orderId}`, {
        totalFromAPI: allThreads.length,
        filtered: threads.value.length,
        threads: threads.value.map(t => ({ id: t.id, order: t.order || t.order_id, unread: t.unread_count }))
      })
    }
  } catch (error) {
    console.error('Failed to load threads:', error)
    // Show user-friendly error message
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to load conversations'
    showError(errorMsg)
    threads.value = [] // Clear threads on error
    
    // For admin/support, show more detailed error
    if (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport) {
      console.error('[OrderMessagesTabbed] Error details:', {
        orderId: props.orderId,
        error: error.response?.data || error.message,
        status: error.response?.status
      })
    }
  } finally {
    loadingThreads.value = false
  }
}

const getUnreadCountForTab = (tabId) => {
  const activeTabData = recipientTabs.value.find(t => t.id === tabId)
  if (!activeTabData) return 0

  // Use the same filtering logic as filteredThreads to ensure count matches visible threads
  const orderThreads = threads.value.filter(thread => {
    const threadOrderId = thread.order || thread.order_id
    return threadOrderId && parseInt(threadOrderId) === parseInt(props.orderId)
  })

  // If "all" tab, return total unread count
  if (tabId === 'all') {
    return orderThreads.reduce((sum, thread) => sum + (thread.unread_count || 0), 0)
  }

  return orderThreads.reduce((sum, thread) => {
    // Use the same logic as filteredThreads - prioritize recipient_role from last message
    const otherRoles = getOtherParticipantRoles(thread)
    
    // Check if the thread matches the active tab using the same logic as filteredThreads
    let matchesTab = false
    if (otherRoles.length > 0) {
      matchesTab = otherRoles.some(role => activeTabData.roles.includes(role))
    } else {
      // Fallback to participant roles if no recipient_role
      const participants = thread.participants || []
      const otherParticipants = participants.filter(p => {
        const participantId = typeof p === 'object' ? p.id : p
        return participantId !== currentUser?.id
      })
      
      const participantRoles = otherParticipants
        .map(p => typeof p === 'object' ? p.role : null)
        .filter(Boolean)
      
      if (participantRoles.length > 0) {
        matchesTab = participantRoles.some(role => activeTabData.roles.includes(role))
      }
    }

    return matchesTab ? sum + (thread.unread_count || 0) : sum
  }, 0)
}

const getThreadTitle = (thread) => {
  const otherParticipants = thread.participants?.filter(p => 
    (typeof p === 'object' ? p.id : p) !== currentUser?.id
  ) || []

  if (otherParticipants.length === 0) return 'Conversation'
  if (otherParticipants.length === 1) {
    const p = otherParticipants[0]
    return typeof p === 'object' ? (p.username || p.email) : 'User'
  }
  return `${otherParticipants.length} participants`
}

const getThreadSubtitle = (thread) => {
  const otherParticipants = thread.participants?.filter(p => 
    (typeof p === 'object' ? p.id : p) !== currentUser?.id
  ) || []

  if (otherParticipants.length === 0) return 'No other participants'
  
  const roles = otherParticipants.map(p => {
    const role = typeof p === 'object' ? p.role : null
    return role ? role.charAt(0).toUpperCase() + role.slice(1) : 'User'
  })
  
  return roles.join(', ')
}

const getThreadInitials = (thread) => {
  const title = getThreadTitle(thread)
  const words = title.split(' ')
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return title.substring(0, 2).toUpperCase()
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    const now = new Date()
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }
    
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    
    // Show relative time for recent messages
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    
    // For older messages, show formatted date and time
    const isToday = date.toDateString() === now.toDateString()
    const isYesterday = date.toDateString() === new Date(now.getTime() - 86400000).toDateString()
    
    if (isToday) {
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
    } else if (isYesterday) {
      return `Yesterday ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}`
    } else if (days < 365) {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true })
    } else {
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    }
  } catch (error) {
    console.error('Error formatting time:', error, dateString)
    return 'Invalid date'
  }
}

const openNewMessageModal = () => {
  showNewMessageModal.value = true
}

const openThread = (thread) => {
  if (!thread || !thread.id) {
    console.error('Invalid thread:', thread)
    showError('Invalid conversation')
    return
  }
  // Navigate to dedicated thread detail page
  router.push(`/messages/thread/${thread.id}`)
}

const expandThread = (thread) => {
  if (!thread || !thread.id) {
    console.error('Invalid thread:', thread)
    showError('Invalid conversation')
    return
  }
  selectedThread.value = thread
  selectedThreadId.value = thread.id
}

const getSenderInfo = (thread) => {
  if (!thread || !thread.last_message) return 'N/A'
  const sender = thread.last_message.sender
  if (typeof sender === 'object') {
    return `${sender.username || sender.email} (${sender.role || 'User'})`
  }
  return thread.last_message.sender_name || 'Unknown'
}

const getRecipientInfo = (thread) => {
  if (!thread || !thread.last_message) {
    // Fallback to participants
    const otherParticipants = thread.participants?.filter(p => {
      const participantId = typeof p === 'object' ? p.id : p
      return participantId !== currentUser?.id
    }) || []
    if (otherParticipants.length > 0) {
      const p = otherParticipants[0]
      if (typeof p === 'object') {
        return `${p.username || p.email} (${p.role || 'User'})`
      }
    }
    return 'N/A'
  }
  const recipientRole = thread.last_message.recipient_role
  if (recipientRole) {
    return `${recipientRole.charAt(0).toUpperCase() + recipientRole.slice(1)}`
  }
  return 'N/A'
}

const closeThread = () => {
  selectedThread.value = null
  selectedThreadId.value = null
}

const handleMessageSent = (success = true) => {
  if (success) {
    showSuccess('Message sent successfully!')
    showNewMessageModal.value = false
    // Invalidate cache and reload
    messagesStore.invalidateThreadsCache()
    loadThreads(true) // Force refresh
  } else {
    showError('Failed to send message. Please try again.')
  }
}

const handleThreadUpdated = async (success = true) => {
  if (success) {
    // Invalidate cache and reload threads to get updated unread_count values
    messagesStore.invalidateThreadsCache()
    await loadThreads(true) // Force refresh - this will update totalUnreadCount computed
    
    // Also directly fetch unread count from API to ensure accuracy
    // This handles cases where the backend might have stale unread_count in thread data
    try {
      const apiCount = await loadUnreadMessageCount(props.orderId)
      // Emit the API count directly to ensure parent has accurate count
      emit('unread-count-update', apiCount)
    } catch (error) {
      // If API call fails, rely on computed totalUnreadCount
      if (import.meta.env.DEV) {
        console.warn('Failed to refresh unread count from API:', error)
      }
    }
  } else {
    showError('Failed to update thread. Please try again.')
  }
}

watch(activeTab, () => {
  selectedThread.value = null
  selectedThreadId.value = null
})

watch(() => props.orderId, () => {
  if (props.orderId) {
    loadThreads()
  }
})

onMounted(async () => {
  if (props.orderId) {
    await loadThreads()
    // Emit initial count after threads are loaded
    emit('unread-count-update', totalUnreadCount.value)
    // Prefer SSE-based updates over polling to reduce HTTP chatter
    messagesStore.connectRealtime()
  }
})

onUnmounted(() => {
  // Keep SSE connection alive for other consumers; no explicit disconnect here.
})
</script>

<style scoped>
.order-messages-tabbed {
  min-height: 400px;
}
</style>

