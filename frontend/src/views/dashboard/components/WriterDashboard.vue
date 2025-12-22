<template>
  <div class="space-y-6">
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <QuickActionCard
        to="/orders"
        icon="📝"
        title="My Orders"
        description="View assigned orders"
      />
      <QuickActionCard
        to="/writer/queue"
        icon="🎯"
        title="Available Orders"
        description="Take new orders"
      />
      <QuickActionCard
        to="/writer/payments"
        icon="💰"
        title="Payments"
        description="View payment history"
      />
      <QuickActionCard
        to="/writer/advance-payments"
        icon="💳"
        title="Advance Payments"
        description="Request advance payments"
      />
      <QuickActionCard
        to="/writer/performance"
        icon="⭐"
        title="Badges & Performance"
        description="View achievements"
      />
    </div>

    <!-- Additional Quick Actions -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <QuickActionCard
        to="/writer/calendar"
        icon="📅"
        title="Deadline Calendar"
        description="View order deadlines"
      />
      <QuickActionCard
        to="/writer/workload"
        icon="⚖️"
        title="Workload & Capacity"
        description="Track your capacity"
      />
      <QuickActionCard
        to="/writer/order-requests"
        icon="📋"
        title="Order Requests"
        description="Track request status"
      />
      <QuickActionCard
        to="/writer/communications"
        icon="💬"
        title="Communications"
        description="Client messages"
      />
    </div>

    <!-- Real-time Focus Widgets -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Next Deadline -->
      <div class="card bg-white rounded-lg shadow-sm border border-gray-100 p-6 flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Next Deadline</p>
            <p class="text-2xl font-bold text-gray-900 mt-1">
              {{ nextDeadlineInfo ? formatDate(nextDeadlineInfo.deadline) : 'No deadlines' }}
            </p>
          </div>
          <span class="text-3xl">⏳</span>
        </div>
        <p class="text-sm text-gray-600">
          {{ nextDeadlineInfo ? (nextDeadlineInfo.topic || 'Assigned order') : 'Enjoy the calm before the next assignment.' }}
        </p>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-gray-500 uppercase tracking-wide">Time Remaining</p>
            <p class="text-xl font-semibold text-primary-600">{{ deadlineCountdown }}</p>
          </div>
          <router-link
            v-if="nextDeadlineOrderLink"
            :to="nextDeadlineOrderLink"
            class="px-3 py-1.5 text-sm font-medium text-primary-600 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
          >
            Open Order
          </router-link>
        </div>
      </div>

      <!-- Availability -->
      <div class="card bg-white rounded-lg shadow-sm border border-gray-100 p-6 flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Availability</p>
            <p class="text-2xl font-bold" :class="isAvailabilityOnline ? 'text-green-600' : 'text-gray-600'">
              {{ isAvailabilityOnline ? 'Available' : 'On Break' }}
            </p>
          </div>
          <span class="text-3xl">{{ isAvailabilityOnline ? '🟢' : '🛌' }}</span>
        </div>
        <p class="text-sm text-gray-600">
          {{ isAvailabilityOnline ? 'You appear in the pool for instant assignments.' : 'You will not auto-receive urgent orders.' }}
        </p>
        <p v-if="availabilityMessage" class="text-xs text-gray-500 italic">
          "{{ availabilityMessage }}"
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="toggleAvailability"
            :disabled="availabilityLoading"
            class="flex-1 px-3 py-2 rounded-lg text-sm font-semibold transition-colors"
            :class="isAvailabilityOnline ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-green-50 text-green-600 hover:bg-green-100'"
          >
            {{ isAvailabilityOnline ? 'Mark as On Break' : 'Mark as Available' }}
          </button>
          <button
            @click="pingAvailability"
            :disabled="availabilityLoading"
            class="px-3 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            title="Ping the system to refresh your live status"
          >
            Ping
          </button>
        </div>
        <p class="text-xs text-gray-500">
          Last ping: {{ lastAvailabilityPing ? new Date(lastAvailabilityPing).toLocaleTimeString() : 'Never' }}
        </p>
      </div>

      <!-- Queue Auto Refresh -->
      <div class="card bg-white rounded-lg shadow-sm border border-gray-100 p-6 flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Auto Refresh</p>
            <p class="text-2xl font-bold text-gray-900">{{ autoRefreshEnabled ? 'Enabled' : 'Disabled' }}</p>
          </div>
          <span class="text-3xl">{{ autoRefreshEnabled ? '🔁' : '⏱️' }}</span>
        </div>
        <p class="text-sm text-gray-600">
          {{ autoRefreshEnabled ? 'Queue refreshes every 30s so you never miss a drop.' : 'Turn on auto refresh to watch new orders appear in real-time.' }}
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="toggleAutoRefresh"
            class="flex-1 px-3 py-2 rounded-lg text-sm font-semibold transition-colors"
            :class="autoRefreshEnabled ? 'bg-green-50 text-green-600 hover:bg-green-100' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
          >
            {{ autoRefreshEnabled ? 'Disable Auto Refresh' : 'Enable Auto Refresh' }}
          </button>
          <button
            @click="requestQueueRefresh"
            class="px-3 py-2 text-sm text-primary-600 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
          >
            Refresh Now
          </button>
        </div>
        <div class="text-xs text-gray-500">
          <p>Available orders: <span class="font-semibold text-gray-800">{{ queueStats.available }}</span></p>
          <p>Preferred orders: <span class="font-semibold text-gray-800">{{ queueStats.preferred }}</span></p>
          <p>Last refresh: {{ lastQueueRefreshLabel }}</p>
        </div>
      </div>
    </div>

    <!-- Additional Real-time Widgets -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div
        v-if="realtimeOrdersReady"
        class="card bg-white rounded-lg shadow-sm border border-orange-100 p-6 flex flex-col gap-3"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-orange-500 uppercase tracking-wide">Orders Ready</p>
            <p class="text-2xl font-bold text-gray-900">{{ realtimeOrdersReady.count || 0 }}</p>
          </div>
          <span class="text-3xl">🚀</span>
        </div>
        <p class="text-sm text-gray-600">
          {{ realtimeOrdersReady.count ? 'Orders that are nearly ready to submit.' : 'All caught up!' }}
        </p>
        <div v-if="realtimeOrdersReady.orders?.length" class="space-y-3">
          <div
            v-for="order in realtimeOrdersReady.orders"
            :key="`ready-${order.id}`"
            class="p-3 border border-orange-200 rounded-lg bg-orange-50"
          >
            <div class="flex items-center justify-between gap-2">
              <router-link
                :to="`/orders/${order.id}`"
                class="font-semibold text-gray-900 hover:text-primary-600"
              >
                #{{ order.id }} • {{ order.topic || 'Untitled' }}
              </router-link>
              <span class="text-xs font-medium text-orange-700 capitalize">{{ order.status || 'ready' }}</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Due {{ order.deadline ? formatDate(order.deadline) : 'TBD' }} • {{ order.pages || 0 }} pages
            </p>
          </div>
        </div>
      </div>

      <div
        v-if="realtimeGoalProgress"
        class="card bg-linear-to-br from-indigo-50 to-indigo-100 rounded-lg shadow-sm border border-indigo-200 p-6 flex flex-col gap-3"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold text-indigo-600 uppercase tracking-wide">Goal Progress</p>
            <p class="text-xl font-bold text-gray-900">
              {{ realtimeGoalProgress.next_level_name || 'Next level' }}
            </p>
          </div>
          <span class="text-3xl">🎯</span>
        </div>
        <div class="w-full bg-white rounded-full h-3 border border-indigo-200">
          <div
            class="h-3 rounded-full bg-indigo-500 transition-all"
            :style="{ width: `${Math.min(100, realtimeGoalProgress.progress_percentage || 0)}%` }"
          ></div>
        </div>
        <div class="flex items-center justify-between text-sm text-gray-600">
          <span>{{ formatScore(realtimeGoalProgress.current_score) }} pts</span>
          <span>{{ formatScore(realtimeGoalProgress.required_score) }} required</span>
        </div>
        <p class="text-xs text-gray-500">
          {{ realtimeGoalProgress.points_needed > 0 ? `${realtimeGoalProgress.points_needed} pts to go` : 'Ready for promotion!' }}
        </p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Earnings"
        :value="writerEarningsData?.total_earnings ? `$${writerEarningsData.total_earnings.toFixed(2)}` : '$0.00'"
        icon="💰"
        :subtitle="writerEarningsData?.this_month ? `$${writerEarningsData.this_month.toFixed(2)} this month` : ''"
      />
      <StatsCard
        name="Completed Orders"
        :value="writerPerformanceData?.completed_orders || 0"
        icon="✅"
        :subtitle="writerPerformanceData?.completion_rate ? `${writerPerformanceData.completion_rate.toFixed(1)}% completion rate` : 'No data'"
      />
      <StatsCard
        name="On-Time Rate"
        :value="writerPerformanceData?.on_time_rate ? `${writerPerformanceData.on_time_rate.toFixed(1)}%` : '0%'"
        icon="⏰"
        :subtitle="writerPerformanceData?.on_time_orders ? `${writerPerformanceData.on_time_orders}/${writerPerformanceData.completed_orders || 0} on time` : 'No data'"
      />
      <StatsCard
        name="Pending Payments"
        :value="writerEarningsData?.pending_payments ? `$${writerEarningsData.pending_payments.toFixed(2)}` : '$0.00'"
        icon="💳"
        subtitle="Awaiting payment"
      />
    </div>

    <!-- Earnings Dashboard -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartWidget
        title="Earnings Trends (Last 30 Days)"
        type="area"
        :series="earningsTrendSeries"
        :options="earningsTrendOptions"
        :loading="loading"
      />
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Earnings Breakdown</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">This Week</div>
              <div class="text-2xl font-bold text-green-600">${{ writerEarningsData?.this_week?.toFixed(2) || '0.00' }}</div>
            </div>
            <span class="text-3xl">📅</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">This Month</div>
              <div class="text-2xl font-bold text-blue-600">${{ writerEarningsData?.this_month?.toFixed(2) || '0.00' }}</div>
            </div>
            <span class="text-3xl">💰</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">This Year</div>
              <div class="text-2xl font-bold text-purple-600">${{ writerEarningsData?.this_year?.toFixed(2) || '0.00' }}</div>
            </div>
            <span class="text-3xl">📊</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-orange-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Avg per Order</div>
              <div class="text-2xl font-bold text-orange-600">${{ writerEarningsData?.avg_per_order?.toFixed(2) || '0.00' }}</div>
            </div>
            <span class="text-3xl">📈</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Analytics -->
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-bold text-gray-900">Performance Analytics</h2>
        <router-link to="/writer/performance" class="text-primary-600 text-sm hover:underline">View detailed analytics →</router-link>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          name="Completion Rate"
          :value="writerPerformanceData?.completion_rate ? `${writerPerformanceData.completion_rate.toFixed(1)}%` : '0.0%'"
          icon="✅"
          :subtitle="`${writerPerformanceData?.completed_orders || 0}/${writerPerformanceData?.total_orders || 0} orders`"
          bgColor="bg-blue-100"
        />
        <StatsCard
          name="On-Time Rate"
          :value="writerPerformanceData?.on_time_rate ? `${writerPerformanceData.on_time_rate.toFixed(1)}%` : '0.0%'"
          icon="⏰"
          :subtitle="`${writerPerformanceData?.on_time_orders || 0} on time`"
          bgColor="bg-green-100"
        />
        <StatsCard
          name="Average Rating"
          :value="writerPerformanceData?.avg_rating ? writerPerformanceData.avg_rating.toFixed(1) : 'N/A'"
          icon="⭐"
          subtitle="Client satisfaction"
          bgColor="bg-yellow-100"
        />
        <StatsCard
          name="Revision Rate"
          :value="writerPerformanceData?.revision_rate ? `${writerPerformanceData.revision_rate.toFixed(1)}%` : '0.0%'"
          icon="📝"
          :subtitle="`${writerPerformanceData?.revised_orders || 0} revised`"
          bgColor="bg-orange-100"
        />
      </div>

      <ChartWidget
        title="Performance Trends (Last 30 Days)"
        type="line"
        :series="performanceTrendSeries"
        :options="performanceTrendOptions"
        :loading="loading"
      />
    </div>

    <!-- Badges & Level -->
    <div v-if="writerBadgesData" class="card bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Badges & Achievements</h2>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">Total: {{ writerBadgesData?.total_badges || 0 }}</span>
          <router-link to="/writer/badges" class="text-primary-600 text-sm">Manage badges</router-link>
        </div>
      </div>
      
      <div v-if="writerBadgesData.badge_counts_by_type && Object.keys(writerBadgesData.badge_counts_by_type).length" class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div 
          v-for="(count, type) in writerBadgesData.badge_counts_by_type" 
          :key="type"
          class="text-center p-3 bg-gray-50 rounded-lg"
        >
          <div class="text-2xl font-bold text-primary-600">{{ count }}</div>
          <div class="text-xs text-gray-600 capitalize">{{ type }}</div>
        </div>
      </div>
      
      <div v-if="writerBadgesData.recent_badges && writerBadgesData.recent_badges.length" class="space-y-3">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Recent Badges</h3>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <div 
            v-for="badge in writerBadgesData.recent_badges.slice(0, 10)" 
            :key="badge.id"
            class="flex flex-col items-center p-4 bg-linear-to-br from-yellow-50 to-yellow-100 rounded-lg border border-yellow-200 hover:shadow-md transition-shadow"
            :title="badge.name"
          >
            <div class="text-4xl mb-2">{{ badge.icon || '🏆' }}</div>
            <div class="text-sm font-medium text-center text-gray-900">{{ badge.name }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ badge.issued_at ? new Date(badge.issued_at).toLocaleDateString() : '' }}</div>
            <div class="text-xs text-gray-400 mt-1 capitalize">{{ badge.type }}</div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        <div class="text-4xl mb-2">🏆</div>
        <div>No badges earned yet</div>
        <div class="text-sm text-gray-400 mt-2">Complete orders to earn badges!</div>
      </div>
    </div>

    <!-- Revision Requests Widget -->
    <div v-if="writerSummaryData?.revision_requests?.count > 0" class="card bg-white rounded-lg shadow-sm p-6 border-l-4 border-orange-500">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-bold text-gray-900">⚠️ Revision Requests</h2>
          <p class="text-sm text-gray-600 mt-1">{{ writerSummaryData.revision_requests.count }} order(s) need revision</p>
        </div>
        <router-link to="/writer/orders?status=revision_requested" class="text-primary-600 text-sm hover:underline font-medium">
          View All →
        </router-link>
      </div>
      <div class="space-y-3">
        <div
          v-for="order in writerSummaryData.revision_requests.orders.slice(0, 3)"
          :key="order.id"
          class="flex items-center justify-between p-3 bg-orange-50 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors"
        >
          <div class="flex-1">
            <router-link
              :to="`/orders/${order.id}`"
              class="font-medium text-gray-900 hover:text-primary-600"
            >
              Order #{{ order.id }}
            </router-link>
            <p class="text-sm text-gray-600 mt-1">{{ order.topic }}</p>
            <p class="text-xs text-gray-500 mt-1">
              {{ order.pages }} pages • Updated: {{ formatDate(order.updated_at) }}
            </p>
          </div>
          <router-link
            :to="`/orders/${order.id}`"
            class="btn btn-warning text-sm whitespace-nowrap ml-4"
          >
            Review
          </router-link>
        </div>
      </div>
    </div>

    <!-- Tips & Fines Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Tips Summary -->
      <div v-if="writerSummaryData?.tips" class="card bg-linear-to-br from-green-50 to-green-100 rounded-lg shadow-sm p-6 border border-green-200">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-gray-900">💰 Tips</h2>
            <p class="text-sm text-gray-600 mt-1">Total tips received</p>
          </div>
          <router-link to="/writer/tips" class="text-green-700 text-sm hover:underline font-medium">
            View All →
          </router-link>
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between p-4 bg-white rounded-lg border border-green-200">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Tips</p>
              <p class="text-3xl font-bold text-green-600">${{ formatCurrency(writerSummaryData.tips.total) }}</p>
            </div>
            <span class="text-4xl">🎁</span>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="p-3 bg-white rounded-lg border border-green-200">
              <p class="text-xs text-gray-600">This Month</p>
              <p class="text-lg font-bold text-green-700">${{ formatCurrency(writerSummaryData.tips.this_month) }}</p>
            </div>
            <div class="p-3 bg-white rounded-lg border border-green-200">
              <p class="text-xs text-gray-600">Count</p>
              <p class="text-lg font-bold text-green-700">{{ writerSummaryData.tips.count }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Fines Summary -->
      <div v-if="writerSummaryData?.fines" class="card bg-linear-to-br from-red-50 to-red-100 rounded-lg shadow-sm p-6 border border-red-200">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-gray-900">⚖️ Fines</h2>
            <p class="text-sm text-gray-600 mt-1">Fines incurred</p>
          </div>
          <span class="text-sm text-gray-600">{{ writerSummaryData.fines.count }} fine(s)</span>
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between p-4 bg-white rounded-lg border border-red-200">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Fines</p>
              <p class="text-3xl font-bold text-red-600">${{ formatCurrency(writerSummaryData.fines.total) }}</p>
            </div>
            <span class="text-4xl">⚠️</span>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="p-3 bg-white rounded-lg border border-red-200">
              <p class="text-xs text-gray-600">This Month</p>
              <p class="text-lg font-bold text-red-700">${{ formatCurrency(writerSummaryData.fines.this_month) }}</p>
            </div>
            <div class="p-3 bg-white rounded-lg border border-red-200">
              <p class="text-xs text-gray-600">Unpaid</p>
              <p class="text-lg font-bold text-red-700">${{ formatCurrency(writerSummaryData.fines.unpaid) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Reviews & Level Progress -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Reviews -->
      <div v-if="writerSummaryData?.reviews" class="card bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-gray-900">⭐ Recent Reviews</h2>
            <p class="text-sm text-gray-600 mt-1">
              Average: {{ writerSummaryData.reviews.average_rating ? writerSummaryData.reviews.average_rating.toFixed(1) : 'N/A' }} 
              ({{ writerSummaryData.reviews.total_count }} total)
            </p>
          </div>
          <router-link to="/writer/reviews" class="text-primary-600 text-sm hover:underline font-medium">
            View All →
          </router-link>
        </div>
        <div v-if="writerSummaryData.reviews.recent.length === 0" class="text-center py-8 text-gray-500">
          <div class="text-4xl mb-2">⭐</div>
          <div>No reviews yet</div>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="review in writerSummaryData.reviews.recent"
            :key="review.id"
            class="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <div class="flex">
                    <span
                      v-for="i in 5"
                      :key="i"
                      :class="i <= (review.rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
                      class="text-lg"
                    >
                      ★
                    </span>
                  </div>
                  <span class="text-sm text-gray-600">{{ review.client_name }}</span>
                </div>
                <p v-if="review.comment" class="text-sm text-gray-700 mt-2 line-clamp-2">{{ review.comment }}</p>
                <p class="text-xs text-gray-500 mt-2">
                  Order #{{ review.order_id }} • {{ formatDate(review.created_at) }}
                </p>
              </div>
              <router-link
                v-if="review.order_id"
                :to="`/orders/${review.order_id}`"
                class="text-primary-600 text-sm hover:underline ml-4"
              >
                View
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Level Progress -->
      <div v-if="writerSummaryData?.level_progress || writerSummaryData?.current_level" class="card bg-linear-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm p-6 border border-blue-200">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-gray-900">📊 Level Progress</h2>
            <p class="text-sm text-gray-600 mt-1">
              Current: <span class="font-medium">{{ writerSummaryData.current_level?.name || 'None' }}</span>
            </p>
          </div>
          <span class="text-3xl">🎯</span>
        </div>
        
        <div v-if="writerSummaryData.level_progress" class="space-y-4">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Progress to {{ writerSummaryData.level_progress.next_level_name }}</span>
              <span class="text-sm font-bold text-blue-700">{{ writerSummaryData.level_progress.progress_percentage }}%</span>
            </div>
            
            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 rounded-full h-4 mb-2">
              <div
                class="h-4 rounded-full bg-linear-to-r from-blue-500 to-blue-600 flex items-center justify-center text-xs font-medium text-white transition-all"
                :style="{ width: `${Math.min(writerSummaryData.level_progress.progress_percentage, 100)}%` }"
              >
                {{ writerSummaryData.level_progress.progress_percentage >= 10 ? `${Math.round(writerSummaryData.level_progress.progress_percentage)}%` : '' }}
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-3 mt-4">
              <div class="p-3 bg-white rounded-lg border border-blue-200">
                <p class="text-xs text-gray-600">Current Score</p>
                <p class="text-lg font-bold text-blue-700">{{ writerSummaryData.level_progress.current_score.toFixed(1) }}</p>
              </div>
              <div class="p-3 bg-white rounded-lg border border-blue-200">
                <p class="text-xs text-gray-600">Required Score</p>
                <p class="text-lg font-bold text-blue-700">{{ writerSummaryData.level_progress.required_score.toFixed(1) }}</p>
              </div>
            </div>
            
            <div v-if="writerSummaryData.level_progress.ready_for_promotion" class="mt-4 p-3 bg-green-100 border border-green-300 rounded-lg">
              <p class="text-sm font-medium text-green-800">
                ✅ Ready for promotion to {{ writerSummaryData.level_progress.next_level_name }}!
              </p>
            </div>
            <div v-else-if="writerSummaryData.level_progress.points_needed > 0" class="mt-4 p-3 bg-blue-100 border border-blue-300 rounded-lg">
              <p class="text-sm font-medium text-blue-800">
                {{ writerSummaryData.level_progress.points_needed.toFixed(1) }} points needed for next level
              </p>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          <div class="text-sm">Level progress data not available</div>
        </div>
      </div>
    </div>

    <!-- Writer Hierarchy & Level Info -->
    <div class="space-y-6">
      <!-- Hierarchy Overview Card -->
      <div class="card bg-linear-to-br from-indigo-50 via-blue-50 to-purple-50 rounded-lg shadow-sm p-6 border-2 border-indigo-200">
        <!-- Loading State -->
        <div v-if="!writerLevelData && loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p class="text-sm text-gray-600">Loading hierarchy information...</p>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="!writerLevelData" class="text-center py-8">
          <span class="text-4xl mb-4 block">📊</span>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Writer Hierarchy</h2>
          <p class="text-sm text-gray-600 mb-4">Your level information is being set up</p>
          <p class="text-xs text-gray-500">Please contact admin to assign your writer level</p>
        </div>
        
        <!-- Hierarchy Content -->
        <div v-else>
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Writer Hierarchy</h2>
            <p class="text-sm text-gray-600 mt-1">Your current level and earning structure</p>
          </div>
          <span class="text-4xl">📊</span>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <!-- Current Level Badge -->
          <div class="bg-white rounded-lg p-4 border-2 border-indigo-300 text-center">
            <p class="text-xs text-gray-600 mb-1">Current Level</p>
            <p class="text-2xl font-bold text-indigo-700">{{ writerLevelData?.current_level?.name || 'Not Assigned' }}</p>
            <p v-if="writerLevelData?.current_level?.description" class="text-xs text-gray-500 mt-2 line-clamp-2">
              {{ writerLevelData?.current_level?.description }}
            </p>
          </div>
          
          <!-- Earning Summary -->
          <div class="bg-white rounded-lg p-4 border-2 border-green-300 text-center">
            <p class="text-xs text-gray-600 mb-1">Earning Rate</p>
            <div v-if="writerLevelData?.current_level?.earning_mode === 'fixed_per_page'">
              <p class="text-xl font-bold text-green-700">${{ parseFloat(writerLevelData?.current_level?.base_pay_per_page || 0).toFixed(2) }}/page</p>
              <p v-if="writerLevelData?.current_level?.base_pay_per_slide > 0" class="text-xs text-gray-600 mt-1">
                ${{ parseFloat(writerLevelData?.current_level?.base_pay_per_slide || 0).toFixed(2) }}/slide
              </p>
            </div>
            <div v-else-if="writerLevelData?.current_level?.earning_mode === 'percentage_of_order_cost'">
              <p class="text-xl font-bold text-green-700">{{ parseFloat(writerLevelData?.current_level?.earnings_percentage_of_cost || 0).toFixed(1) }}%</p>
              <p class="text-xs text-gray-600 mt-1">of order cost</p>
            </div>
            <div v-else-if="writerLevelData?.current_level?.earning_mode === 'percentage_of_order_total'">
              <p class="text-xl font-bold text-green-700">{{ parseFloat(writerLevelData?.current_level?.earnings_percentage_of_total || 0).toFixed(1) }}%</p>
              <p class="text-xs text-gray-600 mt-1">of order total</p>
            </div>
            <p v-else class="text-sm text-gray-500">Not configured</p>
          </div>
          
          <!-- Capacity Status -->
          <div class="bg-white rounded-lg p-4 border-2 border-purple-300 text-center">
            <p class="text-xs text-gray-600 mb-1">Order Capacity</p>
            <p class="text-xl font-bold text-purple-700">
              {{ writerLevelData?.current_stats?.total_takes || 0 }} / {{ writerLevelData?.current_level?.max_orders || 0 }}
            </p>
            <div class="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all"
                :class="{
                  'bg-green-500': (writerLevelData?.current_stats?.total_takes || 0) < (writerLevelData?.current_level?.max_orders || 1) * 0.7,
                  'bg-yellow-500': (writerLevelData?.current_stats?.total_takes || 0) >= (writerLevelData?.current_level?.max_orders || 1) * 0.7 && (writerLevelData?.current_stats?.total_takes || 0) < (writerLevelData?.current_level?.max_orders || 1) * 0.9,
                  'bg-red-500': (writerLevelData?.current_stats?.total_takes || 0) >= (writerLevelData?.current_level?.max_orders || 1) * 0.9
                }"
                :style="{ width: `${Math.min(((writerLevelData?.current_stats?.total_takes || 0) / (writerLevelData?.current_level?.max_orders || 1)) * 100, 100)}%` }"
              ></div>
            </div>
            <p class="text-xs text-gray-500 mt-1">Current takes / Max allowed</p>
          </div>
        </div>

        <!-- Current Level - Detailed Card -->
        <div v-if="writerLevelData" class="card bg-linear-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm p-6 border border-blue-200">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">Level Details</h2>
              <p class="text-sm text-gray-600 mt-1">{{ writerLevelData?.current_level?.name || 'Not Assigned' }}</p>
            </div>
            <span class="text-4xl">📊</span>
          </div>
          
          <p v-if="writerLevelData?.current_level?.description" class="text-sm text-gray-700 mb-4 p-3 bg-white rounded-lg border border-blue-200">
            {{ writerLevelData?.current_level?.description }}
          </p>

          <!-- Detailed Level Information Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Earnings Structure -->
            <div class="bg-white rounded-lg p-4 border border-blue-200">
              <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                <span class="mr-2">💰</span>
                Earnings Structure
              </h3>
              <div v-if="writerLevelData?.current_level?.earning_mode === 'fixed_per_page'" class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-600">Per Page:</span>
                  <span class="text-lg font-bold text-green-700">${{ parseFloat(writerLevelData?.current_level?.base_pay_per_page || 0).toFixed(2) }}</span>
                </div>
                <div v-if="writerLevelData?.current_level?.base_pay_per_slide > 0" class="flex items-center justify-between">
                  <span class="text-xs text-gray-600">Per Slide:</span>
                  <span class="text-lg font-bold text-green-700">${{ parseFloat(writerLevelData?.current_level?.base_pay_per_slide || 0).toFixed(2) }}</span>
                </div>
              </div>
              <div v-else-if="writerLevelData?.current_level?.earning_mode === 'percentage_of_order_cost'" class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-600">Percentage:</span>
                  <span class="text-lg font-bold text-green-700">{{ parseFloat(writerLevelData?.current_level?.earnings_percentage_of_cost || 0).toFixed(1) }}%</span>
                </div>
                <p class="text-xs text-gray-500">of order cost (before discounts)</p>
              </div>
              <div v-else-if="writerLevelData?.current_level?.earning_mode === 'percentage_of_order_total'" class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-600">Percentage:</span>
                  <span class="text-lg font-bold text-green-700">{{ parseFloat(writerLevelData?.current_level?.earnings_percentage_of_total || 0).toFixed(1) }}%</span>
                </div>
                <p class="text-xs text-gray-500">of order total (after discounts)</p>
              </div>
            </div>

          <!-- Urgency Adjustments -->
          <div class="bg-white rounded-lg p-4 border border-yellow-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span class="mr-2">⚡</span>
              Urgency Adjustments
            </h3>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Urgency Hours:</span>
                <span class="text-sm font-bold text-yellow-700">{{ writerLevelData.current_level?.urgent_order_deadline_hours || 0 }}h</span>
              </div>
              <div v-if="writerLevelData?.current_level?.urgency_percentage_increase > 0" class="flex items-center justify-between">
                <span class="text-xs text-gray-600">% Increase:</span>
                <span class="text-sm font-bold text-yellow-700">+{{ parseFloat(writerLevelData?.current_level?.urgency_percentage_increase || 0).toFixed(1) }}%</span>
              </div>
              <div v-if="writerLevelData?.current_level?.urgency_additional_per_page > 0" class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Extra Per Page:</span>
                <span class="text-sm font-bold text-yellow-700">+${{ parseFloat(writerLevelData?.current_level?.urgency_additional_per_page || 0).toFixed(2) }}</span>
              </div>
              <p class="text-xs text-gray-500 mt-2">Orders within {{ writerLevelData?.current_level?.urgent_order_deadline_hours || 0 }} hours get urgency bonuses</p>
            </div>
          </div>

          <!-- Technical Adjustments -->
          <div class="bg-white rounded-lg p-4 border border-purple-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span class="mr-2">🔧</span>
              Technical Orders
            </h3>
            <div class="space-y-2">
              <div v-if="writerLevelData?.current_level?.technical_order_adjustment_per_page > 0" class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Extra Per Page:</span>
                <span class="text-sm font-bold text-purple-700">+${{ parseFloat(writerLevelData?.current_level?.technical_order_adjustment_per_page || 0).toFixed(2) }}</span>
              </div>
              <div v-if="writerLevelData?.current_level?.technical_order_adjustment_per_slide > 0" class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Extra Per Slide:</span>
                <span class="text-sm font-bold text-purple-700">+${{ parseFloat(writerLevelData?.current_level?.technical_order_adjustment_per_slide || 0).toFixed(2) }}</span>
              </div>
              <p v-if="!writerLevelData?.current_level?.technical_order_adjustment_per_page && !writerLevelData?.current_level?.technical_order_adjustment_per_slide" class="text-xs text-gray-500">No technical adjustments</p>
            </div>
          </div>

          <!-- Capacity & Limits -->
          <div class="bg-white rounded-lg p-4 border border-indigo-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span class="mr-2">📋</span>
              Capacity & Limits
            </h3>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Max Orders:</span>
                <span class="text-sm font-bold text-indigo-700">{{ writerLevelData.current_level?.max_orders || 0 }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Current Takes:</span>
                <span class="text-sm font-bold text-indigo-700">{{ writerLevelData.current_stats?.total_takes || 0 }}</span>
              </div>
              <p class="text-xs text-gray-500 mt-2">
                Your maximum concurrent orders and current takes are shown here. Detailed deadline allocation is managed by admins.
              </p>
            </div>
          </div>

          <!-- Performance Stats -->
          <div class="bg-white rounded-lg p-4 border border-green-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span class="mr-2">⭐</span>
              Your Performance
            </h3>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Average Rating:</span>
                <span class="text-sm font-bold text-green-700">
                  {{ writerLevelData.current_stats?.avg_rating ? writerLevelData.current_stats.avg_rating.toFixed(1) : 'N/A' }}
                  <span v-if="writerLevelData.current_stats?.avg_rating" class="text-yellow-500 ml-1">★</span>
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Completed Orders:</span>
                <span class="text-sm font-bold text-green-700">{{ writerLevelData.current_stats?.total_completed_orders || 0 }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Completion Rate:</span>
                <span class="text-sm font-bold text-green-700">{{ writerLevelData.current_stats?.completion_rate ? `${writerLevelData.current_stats.completion_rate.toFixed(1)}%` : 'N/A' }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Revision Rate:</span>
                <span class="text-sm font-bold" :class="writerLevelData.current_stats?.revision_rate > 20 ? 'text-red-700' : 'text-green-700'">
                  {{ writerLevelData.current_stats?.revision_rate ? `${writerLevelData.current_stats.revision_rate.toFixed(1)}%` : 'N/A' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Bonuses -->
          <div v-if="writerLevelData?.current_level?.bonus_per_order_completed > 0 || writerLevelData?.current_level?.bonus_per_rating_above_threshold > 0" class="bg-white rounded-lg p-4 border border-orange-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span class="mr-2">🎁</span>
              Available Bonuses
            </h3>
            <div class="space-y-2">
              <div v-if="writerLevelData?.current_level?.bonus_per_order_completed > 0" class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Per Order:</span>
                <span class="text-sm font-bold text-orange-700">+${{ parseFloat(writerLevelData?.current_level?.bonus_per_order_completed || 0).toFixed(2) }}</span>
              </div>
              <div v-if="writerLevelData?.current_level?.bonus_per_rating_above_threshold > 0" class="flex items-center justify-between">
                <span class="text-xs text-gray-600">Rating ≥{{ writerLevelData?.current_level?.rating_threshold_for_bonus }}:</span>
                <span class="text-sm font-bold text-orange-700">+${{ parseFloat(writerLevelData?.current_level?.bonus_per_rating_above_threshold || 0).toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
        
          <!-- Quick Reference Summary -->
          <div class="mt-6 p-4 bg-white rounded-lg border border-blue-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">Quick Reference</h3>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
              <div>
                <p class="text-gray-600">Urgency Threshold:</p>
                <p class="font-bold text-gray-900">{{ writerLevelData?.current_level?.urgent_order_deadline_hours || 0 }} hours</p>
              </div>
              <div>
                <p class="text-gray-600">Urgency Bonus:</p>
                <p class="font-bold text-gray-900" v-if="writerLevelData?.current_level?.urgency_percentage_increase > 0">
                  +{{ parseFloat(writerLevelData?.current_level?.urgency_percentage_increase || 0).toFixed(1) }}%
                  <span v-if="writerLevelData?.current_level?.urgency_additional_per_page > 0">
                    +${{ parseFloat(writerLevelData?.current_level?.urgency_additional_per_page || 0).toFixed(2) }}/page
                  </span>
                </p>
                <p v-else class="font-bold text-gray-500">None</p>
              </div>
              <div>
                <p class="text-gray-600">Technical Bonus:</p>
                <p class="font-bold text-gray-900" v-if="writerLevelData?.current_level?.technical_order_adjustment_per_page > 0">
                  +${{ parseFloat(writerLevelData?.current_level?.technical_order_adjustment_per_page || 0).toFixed(2) }}/page
                </p>
                <p v-else class="font-bold text-gray-500">None</p>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- Next Level & Ranking Row -->
      <div v-if="writerLevelData" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
        <!-- Next Level Requirements -->
        <div v-if="writerLevelData.next_level" class="card bg-linear-to-br from-purple-50 to-purple-100 rounded-lg shadow-sm p-6 border border-purple-200">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-xl font-bold text-gray-900">Next Level</h2>
              <p class="text-sm text-gray-600 mt-1">Progress to advance</p>
            </div>
            <span class="text-3xl">🎯</span>
          </div>
          <div class="space-y-3">
            <div>
              <p class="text-lg font-bold text-purple-700 mb-2">{{ writerLevelData?.next_level?.next_level?.name || 'N/A' }}</p>
              <div v-if="writerLevelData?.next_level?.is_eligible" class="p-3 bg-green-100 border border-green-300 rounded-lg">
                <p class="text-sm font-medium text-green-800">✅ You're eligible for this level!</p>
                <p class="text-xs text-green-700 mt-1">Contact admin to be promoted</p>
              </div>
              <div v-else class="space-y-3">
                <p class="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">Requirements to Unlock:</p>
                <div class="space-y-2">
                  <div v-if="writerLevelData?.current_stats?.total_completed_orders < writerLevelData?.next_level?.requirements?.min_orders" class="p-2 bg-white rounded border border-purple-200">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs text-gray-600">Completed Orders:</span>
                      <span class="text-xs font-bold" :class="(writerLevelData?.current_stats?.total_completed_orders || 0) >= (writerLevelData?.next_level?.requirements?.min_orders || 0) ? 'text-green-700' : 'text-purple-700'">
                        {{ writerLevelData?.current_stats?.total_completed_orders || 0 }}/{{ writerLevelData?.next_level?.requirements?.min_orders || 0 }}
                      </span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        class="h-1.5 rounded-full transition-all"
                        :class="(writerLevelData?.current_stats?.total_completed_orders || 0) >= (writerLevelData?.next_level?.requirements?.min_orders || 0) ? 'bg-green-500' : 'bg-purple-500'"
                        :style="{ width: `${Math.min(((writerLevelData?.current_stats?.total_completed_orders || 0) / (writerLevelData?.next_level?.requirements?.min_orders || 1)) * 100, 100)}%` }"
                      ></div>
                    </div>
                  </div>
                  <div v-if="(writerLevelData?.current_stats?.avg_rating || 0) < (writerLevelData?.next_level?.requirements?.min_rating || 0)" class="p-2 bg-white rounded border border-purple-200">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs text-gray-600">Average Rating:</span>
                      <span class="text-xs font-bold" :class="(writerLevelData?.current_stats?.avg_rating || 0) >= (writerLevelData?.next_level?.requirements?.min_rating || 0) ? 'text-green-700' : 'text-purple-700'">
                        {{ (writerLevelData?.current_stats?.avg_rating || 0).toFixed(1) }}/{{ (writerLevelData?.next_level?.requirements?.min_rating || 0).toFixed(1) }}
                        <span class="text-yellow-500 ml-1">★</span>
                      </span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        class="h-1.5 rounded-full transition-all"
                        :class="(writerLevelData?.current_stats?.avg_rating || 0) >= (writerLevelData?.next_level?.requirements?.min_rating || 0) ? 'bg-green-500' : 'bg-purple-500'"
                        :style="{ width: `${Math.min(((writerLevelData?.current_stats?.avg_rating || 0) / (writerLevelData?.next_level?.requirements?.min_rating || 1)) * 100, 100)}%` }"
                      ></div>
                    </div>
                  </div>
                  <div v-if="(writerLevelData?.current_stats?.completion_rate || 0) < (writerLevelData?.next_level?.requirements?.min_completion_rate || 0)" class="p-2 bg-white rounded border border-purple-200">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs text-gray-600">Completion Rate:</span>
                      <span class="text-xs font-bold" :class="(writerLevelData?.current_stats?.completion_rate || 0) >= (writerLevelData?.next_level?.requirements?.min_completion_rate || 0) ? 'text-green-700' : 'text-purple-700'">
                        {{ (writerLevelData?.current_stats?.completion_rate || 0).toFixed(1) }}%/{{ (writerLevelData?.next_level?.requirements?.min_completion_rate || 0).toFixed(1) }}%
                      </span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        class="h-1.5 rounded-full transition-all"
                        :class="(writerLevelData?.current_stats?.completion_rate || 0) >= (writerLevelData?.next_level?.requirements?.min_completion_rate || 0) ? 'bg-green-500' : 'bg-purple-500'"
                        :style="{ width: `${Math.min(((writerLevelData?.current_stats?.completion_rate || 0) / (writerLevelData?.next_level?.requirements?.min_completion_rate || 1)) * 100, 100)}%` }"
                      ></div>
                    </div>
                  </div>
                  <div v-if="(writerLevelData?.next_level?.requirements?.min_takes || 0) > 0 && (writerLevelData?.current_stats?.total_takes || 0) < (writerLevelData?.next_level?.requirements?.min_takes || 0)" class="p-2 bg-white rounded border border-purple-200">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs text-gray-600">Successful Takes:</span>
                      <span class="text-xs font-bold" :class="(writerLevelData?.current_stats?.total_takes || 0) >= (writerLevelData?.next_level?.requirements?.min_takes || 0) ? 'text-green-700' : 'text-purple-700'">
                        {{ writerLevelData?.current_stats?.total_takes || 0 }}/{{ writerLevelData?.next_level?.requirements?.min_takes || 0 }}
                      </span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        class="h-1.5 rounded-full transition-all"
                        :class="(writerLevelData?.current_stats?.total_takes || 0) >= (writerLevelData?.next_level?.requirements?.min_takes || 0) ? 'bg-green-500' : 'bg-purple-500'"
                        :style="{ width: `${Math.min(((writerLevelData?.current_stats?.total_takes || 0) / (writerLevelData?.next_level?.requirements?.min_takes || 1)) * 100, 100)}%` }"
                      ></div>
                    </div>
                  </div>
              </div>
            </div>
          </div>
        </div>
      </div>
        
        <!-- Ranking -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Ranking</h2>
          <span class="text-3xl">🏆</span>
        </div>
        <div v-if="writerLevelData?.ranking_position" class="text-center py-8">
          <div class="text-5xl font-bold text-primary-600 mb-2">#{{ writerLevelData?.ranking_position }}</div>
          <div class="text-sm text-gray-600">Your ranking position</div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          <div class="text-sm">Ranking data not available</div>
        </div>
        </div>
      </div>
    </div>

    <!-- Order Queue -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Available Orders</h2>
        <router-link to="/writer/queue" class="text-primary-600 text-sm">View all</router-link>
      </div>
      <div v-if="writerQueueData && writerQueueData.available_orders && writerQueueData.available_orders.length" class="space-y-3">
        <div 
          v-for="order in writerQueueData.available_orders.slice(0, 5)" 
          :key="order.id"
          class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div class="flex-1">
            <div class="font-medium">#{{ order.id }} · {{ order.topic }}</div>
            <div class="text-sm text-gray-500 mt-1">
              {{ order.service_type }} · {{ (order.pages || order.number_of_pages || 0) }} pages · 
              Deadline: {{ order.deadline ? new Date(order.deadline).toLocaleDateString() : 'N/A' }}
            </div>
          </div>
          <div class="text-right mr-4">
            <div class="text-lg font-bold text-green-600">${{ (order.price || 0).toFixed(2) }}</div>
          </div>
          <button 
            v-if="!order.is_requested"
            @click="openRequestModal(order)"
            :disabled="requestingOrder === order.id"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
          >
            {{ requestingOrder === order.id ? 'Requesting...' : 'Request' }}
          </button>
          <button 
            v-else
            disabled
            class="px-4 py-2 bg-gray-400 text-white rounded-lg cursor-not-allowed text-sm flex items-center gap-1"
            title="You have already requested this order. Waiting for admin review."
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Already Requested
          </button>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        {{ writerQueueData ? 'No available orders' : 'Loading order queue...' }}
      </div>
    </div>

    <!-- Payment Status Widget -->
    <div v-if="writerPaymentStatus" class="mt-6">
      <PaymentStatusWidget
        :payment-status="writerPaymentStatus"
        :loading="loading"
      />
    </div>

    <!-- Recent Orders -->
    <div class="card bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200">
      <div class="bg-linear-to-r from-emerald-50 to-green-50 border-b-2 border-emerald-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            My Orders
          </h2>
          <router-link to="/orders" class="text-emerald-600 hover:text-emerald-800 text-sm font-semibold flex items-center gap-1 transition-colors">
            View all
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </div>
      <div v-if="recentOrdersLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
      <div v-else-if="!recentOrders.length" class="text-center py-12 text-gray-500">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No orders assigned yet</p>
        <router-link to="/writer/queue" class="mt-2 inline-block text-emerald-600 hover:text-emerald-800 text-sm font-medium">
          Browse available orders →
        </router-link>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200" style="min-width: 1000px;">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Order ID</th>
              <th class="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Topic</th>
              <th class="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Status</th>
              <th class="px-6 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Deadline</th>
              <th class="px-6 py-3 text-center text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr v-for="o in recentOrders.slice(0, 5)" :key="o.id" class="hover:bg-emerald-50/50 transition-all duration-150">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-linear-to-br from-emerald-400 to-green-500 flex items-center justify-center text-white text-xs font-bold">
                    #
                  </div>
                  <span class="text-sm font-semibold text-gray-900">#{{ o.id }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 max-w-md truncate" :title="o.topic">
                  {{ o.topic || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold shadow-sm"
                      :class="getOrderStatusClass(o.status)">
                  {{ o.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ o.deadline ? formatDate(o.deadline) : 'N/A' }}</div>
                <div v-if="o.deadline" class="text-xs text-gray-500">{{ formatTime(o.deadline) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <router-link 
                  :to="`/orders/${o.id}`" 
                  class="inline-flex items-center px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-xs font-semibold shadow-sm"
                >
                  View Order
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import QuickActionCard from '@/components/dashboard/QuickActionCard.vue'
import ChartWidget from '@/components/dashboard/ChartWidget.vue'
import Modal from '@/components/common/Modal.vue'
import PaymentStatusWidget from '@/components/writer/PaymentStatusWidget.vue'
import writerOrderRequestsAPI from '@/api/writer-order-requests'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'
import onlineStatusAPI from '@/api/online-status'

const props = defineProps({
  writerEarningsData: Object,
  writerPerformanceData: Object,
  writerQueueData: Object,
  writerBadgesData: Object,
  writerLevelData: Object,
  writerSummaryData: Object,
  writerPaymentStatus: Object,
  recentOrders: Array,
  recentOrdersLoading: Boolean,
  loading: Boolean,
  availabilityStatus: Object,
  realtimeWidgetData: Object
})

const emit = defineEmits(['order-requested', 'refresh-requested', 'availability-updated'])

const earningsTrendSeries = computed(() => {
  if (!props.writerEarningsData?.earnings_trend?.length) return []
  return [{
    name: 'Earnings',
    data: props.writerEarningsData.earnings_trend.map(t => t.total)
  }]
})

const earningsTrendOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false } },
  xaxis: { 
    categories: props.writerEarningsData?.earnings_trend?.map(t => new Date(t.date).toLocaleDateString()) || [],
    labels: { rotate: -45 }
  },
  yaxis: { title: { text: 'Earnings ($)' } },
  stroke: { curve: 'smooth' },
  colors: ['#10B981'],
}))

const performanceTrendSeries = computed(() => {
  if (!props.writerPerformanceData?.performance_trend?.length) return []
  return [
    { name: 'Completed Orders', data: props.writerPerformanceData.performance_trend.map(t => t.completed) },
    { name: 'Total Orders', data: props.writerPerformanceData.performance_trend.map(t => t.total) }
  ]
})

const performanceTrendOptions = computed(() => ({
  chart: { 
    type: 'line', 
    toolbar: { show: false },
    zoom: { enabled: false }
  },
  xaxis: { 
    categories: props.writerPerformanceData?.performance_trend?.map(t => new Date(t.date).toLocaleDateString()) || [],
    labels: { rotate: -45, style: { fontSize: '12px' } }
  },
  yaxis: { 
    title: { text: 'Number of Orders' },
    min: 0
  },
  stroke: { curve: 'smooth', width: 2 },
  colors: ['#3B82F6', '#10B981'],
  legend: {
    position: 'top',
    horizontalAlign: 'right'
  },
  grid: {
    borderColor: '#e5e7eb',
    strokeDashArray: 4
  }
}))

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const formatScore = (value) => {
  if (value === null || value === undefined || value === '') return '0.0'
  return Number(value).toFixed(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getOrderStatusClass = (status) => {
  const statusMap = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'in_progress': 'bg-blue-100 text-blue-800',
    'on_revision': 'bg-orange-100 text-orange-800',
    'completed': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800',
    'disputed': 'bg-purple-100 text-purple-800',
  }
  return statusMap[status?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

// Real-time widgets ----------------------------------------------------------
const nextDeadlineInfo = computed(() => {
  const realtime = props.realtimeWidgetData?.next_deadline
  if (realtime?.deadline) {
    return {
      deadline: realtime.deadline,
      orderId: realtime.order_id || realtime.orderId || null,
      topic: realtime.topic || '',
    }
  }

  const deadlines = []
  if (props.writerSummaryData?.next_deadline) {
    deadlines.push({
      deadline: props.writerSummaryData.next_deadline,
      orderId: props.writerSummaryData.next_deadline_order_id || null,
      topic: props.writerSummaryData.next_deadline_topic || '',
    })
  }
  ;(props.recentOrders || []).forEach(order => {
    const deadline = order.writer_deadline || order.deadline || order.client_deadline
    if (deadline) {
      deadlines.push({
        deadline,
        orderId: order.id,
        topic: order.topic,
      })
    }
  })
  if (!deadlines.length) return null
  return deadlines.sort((a, b) => new Date(a.deadline) - new Date(b.deadline))[0]
})

const nextDeadlineOrderLink = computed(() =>
  nextDeadlineInfo.value?.orderId ? `/orders/${nextDeadlineInfo.value.orderId}` : null
)

const deadlineCountdown = ref('No deadlines')
let countdownTimer = null

const updateDeadlineCountdown = () => {
  const info = nextDeadlineInfo.value
  if (!info) {
    deadlineCountdown.value = 'No deadlines'
    return
  }
  const diff = new Date(info.deadline) - new Date()
  if (diff <= 0) {
    deadlineCountdown.value = 'Due now'
    return
  }
  const days = Math.floor(diff / 86400000)
  const hours = Math.floor((diff % 86400000) / 3600000)
  const minutes = Math.floor((diff % 3600000) / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  if (days > 0) {
    deadlineCountdown.value = `${days}d ${hours}h`
  } else if (hours > 0) {
    deadlineCountdown.value = `${hours}h ${minutes}m`
  } else if (minutes > 0) {
    deadlineCountdown.value = `${minutes}m ${seconds}s`
  } else {
    deadlineCountdown.value = `${seconds}s`
  }
}

const startCountdown = () => {
  stopCountdown()
  updateDeadlineCountdown()
  countdownTimer = setInterval(updateDeadlineCountdown, 1000)
}

const stopCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

watch(nextDeadlineInfo, () => {
  startCountdown()
})

watch(
  () => props.availabilityStatus,
  (status) => {
    if (!status) return
    if (typeof status.is_available === 'boolean') {
      isAvailabilityOnline.value = status.is_available
    }
    if (status.last_changed) {
      lastAvailabilityPing.value = new Date(status.last_changed)
    }
  },
  { immediate: true }
)

watch(
  () => props.realtimeWidgetData?.availability,
  (availability) => {
    if (!availability) return
    if (typeof availability.is_available === 'boolean') {
      isAvailabilityOnline.value = availability.is_available
    }
    const reference = availability.last_active || availability.last_changed
    if (reference) {
      lastAvailabilityPing.value = new Date(reference)
    }
  }
)

const isAvailabilityOnline = ref(true)
const availabilityLoading = ref(false)
const lastAvailabilityPing = ref(null)

const pingAvailability = async (skipLoader = false) => {
  if (!skipLoader) {
    availabilityLoading.value = true
  }
  try {
    await onlineStatusAPI.updateStatus()
    lastAvailabilityPing.value = new Date()
  } catch (error) {
    console.error('Failed to ping availability:', error)
    showError(getErrorMessage(error, 'Unable to update availability'))
  } finally {
    if (!skipLoader) {
      availabilityLoading.value = false
    }
  }
}

const toggleAvailability = async () => {
  const nextValue = !isAvailabilityOnline.value
  availabilityLoading.value = true
  try {
    const response = await writerDashboardAPI.updateAvailability({
      is_available: nextValue,
    })
    isAvailabilityOnline.value = nextValue
    emit('availability-updated', response?.data || null)
    if (nextValue) {
      await pingAvailability(true)
    }
  } catch (error) {
    showError(getErrorMessage(error, 'Unable to update availability'))
  } finally {
    availabilityLoading.value = false
  }
}

const queueStats = computed(() => {
  if (props.realtimeWidgetData?.queue) {
    return {
      available: props.realtimeWidgetData.queue.available || 0,
      preferred: props.realtimeWidgetData.queue.preferred || 0,
      requests: props.realtimeWidgetData.queue.requests || 0,
    }
  }
  return {
    available: props.writerQueueData?.available_orders?.length || 0,
    preferred: props.writerQueueData?.preferred_orders?.length || 0,
    requests:
      (props.writerQueueData?.writer_requests?.length || 0) +
      (props.writerQueueData?.order_requests?.length || 0),
  }
})

const realtimeOrdersReady = computed(() => props.realtimeWidgetData?.orders_ready || null)
const realtimeGoalProgress = computed(() => props.realtimeWidgetData?.goal_progress || null)
const availabilityMessage = computed(() =>
  props.availabilityStatus?.message ||
  props.realtimeWidgetData?.availability?.message ||
  ''
)

const lastQueueRefresh = ref(props.writerQueueData ? new Date() : null)
const lastQueueRefreshLabel = computed(() => {
  if (!lastQueueRefresh.value) return 'Never'
  return lastQueueRefresh.value.toLocaleTimeString()
})

watch(
  () => props.writerQueueData,
  () => {
    lastQueueRefresh.value = new Date()
  }
)

const autoRefreshEnabled = ref(
  localStorage.getItem('writerQueueAutoRefresh') === 'true'
)
let autoRefreshTimer = null

const requestQueueRefresh = () => {
  emit('refresh-requested', { scope: 'queue' })
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  requestQueueRefresh()
  autoRefreshTimer = setInterval(requestQueueRefresh, 30000)
}

const stopAutoRefresh = () => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

const toggleAutoRefresh = () => {
  autoRefreshEnabled.value = !autoRefreshEnabled.value
  localStorage.setItem('writerQueueAutoRefresh', autoRefreshEnabled.value)
  if (autoRefreshEnabled.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

onMounted(() => {
  startCountdown()
  if (isAvailabilityOnline.value) {
    pingAvailability()
  }
  if (autoRefreshEnabled.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopCountdown()
  stopAutoRefresh()
})

// ---------------------------------------------------------------------------

// Order request functionality
const { success: showSuccess, error: showError } = useToast()
const requestingOrder = ref(null)
const showRequestModal = ref(false)
const selectedOrderForRequest = ref(null)
const requestReason = ref('')

const openRequestModal = (order) => {
  if (!order || !order.id) return
  selectedOrderForRequest.value = order
  requestReason.value = ''
  showRequestModal.value = true
}

const closeRequestModal = () => {
  showRequestModal.value = false
  selectedOrderForRequest.value = null
  requestReason.value = ''
}

const requestOrder = async () => {
  const order = selectedOrderForRequest.value
  if (!order || !order.id) return
  
  // Validate reason
  if (!requestReason.value || !requestReason.value.trim()) {
    showError('Please provide a reason for requesting this order.')
    return
  }
  
  requestingOrder.value = order.id
  try {
    await writerOrderRequestsAPI.create({
      order_id: order.id,
      reason: requestReason.value.trim(),
    })
    showSuccess('Order request submitted successfully! Your request is pending admin review.')
    
    // Emit event to parent to refresh queue data
    emit('order-requested', { orderId: order.id })
    
    // Close modal
    closeRequestModal()
  } catch (error) {
    console.error('Failed to request order:', error)
    const errorMsg = getErrorMessage(error, 'Failed to request order. Please try again.')
    showError(errorMsg)
  } finally {
    requestingOrder.value = null
  }
}
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}
</style>

