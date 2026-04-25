<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanningStore } from '@/stores/planning'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import StartSessionDialog from '@/components/StartSessionDialog.vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

const planningStore = usePlanningStore()
const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const showStartDialog = ref(false)
const loading = ref(false)
const error = ref('')

const activeSession = computed(() => sessionStore.activeSession)
const todayPlanning = computed(() => planningStore.todayPlanning)
const recentSessions = computed(() => sessionStore.recentSessions.slice(0, 5))

const greeting = computed(() => {
  const h = dayjs().hour()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
})

const todayStats = computed(() => {
  const today = dayjs().format('YYYY-MM-DD')
  const todaySessions = sessionStore.recentSessions.filter(s =>
    dayjs(s.start_time).format('YYYY-MM-DD') === today && s.end_time !== null
  )
  const totalMinutes = todaySessions.reduce((sum, s) => sum + (s.actual_duration || 0), 0)
  const avgSatisfaction = todaySessions.length > 0
    ? Math.round(todaySessions.reduce((sum, s) => sum + (s.satisfaction_score || 0), 0) / todaySessions.length)
    : 0
  return {
    sessionsCount: todaySessions.length,
    totalTime: totalMinutes,
    avgSatisfaction
  }
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([
      planningStore.fetchPlanningForDate(new Date()),
      sessionStore.fetchRecentSessions(50),
      projectStore.fetchProjects()
    ])
  } catch (err) {
    error.value = 'Failed to load dashboard data'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

function formatTime(datetime) {
  return dayjs(datetime).format('h:mm A')
}

function getSatisfactionColor(score) {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

function getPriorityBadge(priority) {
  const map = {
    low: { cls: 'badge badge-neutral', label: 'Low' },
    medium: { cls: 'badge badge-info', label: 'Medium' },
    critical: { cls: 'badge badge-danger', label: 'Critical' },
  }
  return map[priority] || map.medium
}

function openStartDialog() {
  showStartDialog.value = true
}

function handleSessionStarted() {
  showStartDialog.value = false
  loadData()
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
      <div>
        <h1 class="page-title">{{ greeting }} 👋</h1>
        <p class="page-subtitle mt-1">Here's your overview for today, {{ dayjs().format('MMMM D') }}</p>
      </div>
      <button
        @click="openStartDialog"
        :disabled="activeSession !== null"
        class="btn btn-success"
        :title="activeSession ? 'A session is already active' : 'Start a new session'"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        {{ activeSession ? 'Session Active' : 'Start Session' }}
      </button>
    </div>

    <!-- Error banner -->
    <div
      v-if="error"
      class="glass-card border-l-4 border-danger/60 bg-danger/5 text-danger flex items-center gap-2.5 px-4 py-3 text-sm"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="flex-shrink-0">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span class="flex-1">{{ error }}</span>
      <button @click="loadData" class="btn btn-secondary btn-sm">Retry</button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16 gap-3 text-muted">
      <div class="spinner"></div>
      <p class="text-sm">Loading dashboard...</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Stats grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="glass-card p-5 flex items-center gap-4">
          <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-accent/15 text-accent flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="flex flex-col min-w-0">
            <span class="text-2xl font-bold text-fg leading-tight">{{ todayStats.sessionsCount }}</span>
            <span class="text-xs text-muted">Sessions</span>
          </div>
        </div>

        <div class="glass-card p-5 flex items-center gap-4">
          <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-success/15 text-success flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="flex flex-col min-w-0">
            <span class="text-2xl font-bold text-fg leading-tight">{{ formatDuration(todayStats.totalTime) }}</span>
            <span class="text-xs text-muted">Total Time</span>
          </div>
        </div>

        <div class="glass-card p-5 flex items-center gap-4">
          <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-warning/15 text-warning flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
              <line x1="9" y1="9" x2="9.01" y2="9"></line>
              <line x1="15" y1="9" x2="15.01" y2="9"></line>
            </svg>
          </div>
          <div class="flex flex-col min-w-0">
            <span class="text-2xl font-bold leading-tight" :style="{ color: getSatisfactionColor(todayStats.avgSatisfaction) }">
              {{ todayStats.avgSatisfaction }}%
            </span>
            <span class="text-xs text-muted">Satisfaction</span>
          </div>
        </div>

        <div class="glass-card p-5 flex items-center gap-4">
          <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-info/15 text-info flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div class="flex flex-col min-w-0">
            <span class="text-2xl font-bold text-fg leading-tight">{{ todayPlanning.length }}</span>
            <span class="text-xs text-muted">Plans Today</span>
          </div>
        </div>
      </div>

      <!-- Content grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Today's Schedule -->
        <section class="glass-card p-6">
          <div class="flex items-center justify-between mb-5">
            <h2 class="section-title">Today's Schedule</h2>
            <RouterLink
              to="/planning"
              class="text-sm font-medium text-accent hover:text-accent-hover transition-colors"
            >View calendar &rarr;</RouterLink>
          </div>

          <div v-if="todayPlanning.length === 0" class="flex flex-col items-center justify-center py-12 px-4 text-center">
            <div class="flex items-center justify-center w-14 h-14 rounded-full bg-fg-subtle/15 text-fg-subtle mb-4">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <p class="text-sm text-muted mb-3">No plans for today</p>
            <RouterLink to="/planning" class="text-sm font-semibold text-accent hover:text-accent-hover transition-colors">
              Add a plan
            </RouterLink>
          </div>

          <div v-else class="flex flex-col gap-2">
            <div
              v-for="plan in todayPlanning"
              :key="plan.id"
              class="glass-row flex items-center gap-3 px-4 py-3"
            >
              <div class="flex flex-col items-center min-w-[64px] flex-shrink-0">
                <span class="text-xs font-semibold text-fg">{{ formatTime(plan.scheduled_start) }}</span>
                <span class="text-[11px] text-subtle">{{ formatDuration(dayjs.utc(plan.scheduled_end).local().diff(dayjs.utc(plan.scheduled_start).local(), 'minute')) }}</span>
              </div>
              <div class="w-1 h-9 rounded-full flex-shrink-0" :style="{ backgroundColor: plan.project.color }"></div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold truncate" :style="{ color: plan.project.color }">
                  {{ plan.project.name }}
                </div>
                <div v-if="plan.description" class="text-xs text-muted truncate mt-0.5">{{ plan.description }}</div>
              </div>
              <div class="flex-shrink-0">
                <span :class="getPriorityBadge(plan.priority).cls">
                  {{ getPriorityBadge(plan.priority).label }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Recent Sessions -->
        <section class="glass-card p-6">
          <div class="flex items-center justify-between mb-5">
            <h2 class="section-title">Recent Sessions</h2>
            <RouterLink
              to="/sessions"
              class="text-sm font-medium text-accent hover:text-accent-hover transition-colors"
            >View all &rarr;</RouterLink>
          </div>

          <div v-if="recentSessions.length === 0" class="flex flex-col items-center justify-center py-12 px-4 text-center">
            <div class="flex items-center justify-center w-14 h-14 rounded-full bg-fg-subtle/15 text-fg-subtle mb-4">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <p class="text-sm text-muted mb-3">No sessions yet</p>
            <button
              @click="openStartDialog"
              class="text-sm font-semibold text-accent hover:text-accent-hover transition-colors"
            >
              Start your first session
            </button>
          </div>

          <div v-else class="flex flex-col gap-2">
            <div
              v-for="session in recentSessions"
              :key="session.id"
              class="glass-row flex items-center gap-3 px-4 py-3"
            >
              <div class="w-1 h-8 rounded-full flex-shrink-0" :style="{ backgroundColor: session.project?.color || '#94a3b8' }"></div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-sm font-semibold text-fg truncate">{{ session.project?.name || 'No Project' }}</span>
                  <span class="text-xs font-semibold text-success flex-shrink-0">{{ formatDuration(session.actual_duration || 0) }}</span>
                </div>
                <div class="flex items-center justify-between gap-2 mt-0.5">
                  <span class="text-xs text-subtle">{{ dayjs(session.start_time).fromNow() }}</span>
                  <span
                    v-if="session.satisfaction_score !== null"
                    class="text-xs font-semibold"
                    :style="{ color: getSatisfactionColor(session.satisfaction_score) }"
                  >
                    {{ session.satisfaction_score }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <Transition name="modal">
      <StartSessionDialog
        v-if="showStartDialog"
        @close="showStartDialog = false"
        @started="handleSessionStarted"
      />
    </Transition>
  </div>
</template>
