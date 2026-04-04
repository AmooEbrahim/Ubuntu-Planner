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
    low: { bg: '#f1f5f9', color: '#64748b', label: 'Low' },
    medium: { bg: '#eff6ff', color: '#3b82f6', label: 'Medium' },
    critical: { bg: '#fef2f2', color: '#ef4444', label: 'Critical' },
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
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ greeting }} 👋</h1>
        <p class="page-subtitle">Here's your overview for today, {{ dayjs().format('MMMM D') }}</p>
      </div>
      <button
        @click="openStartDialog"
        :disabled="activeSession !== null"
        class="btn-start"
        :title="activeSession ? 'A session is already active' : 'Start a new session'"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        {{ activeSession ? 'Session Active' : 'Start Session' }}
      </button>
    </div>

    <div v-if="error" class="error-banner">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span>{{ error }}</span>
      <button @click="loadData" class="retry-btn">Retry</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading dashboard...</p>
    </div>

    <div v-else class="dashboard-content">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon-wrap sessions">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ todayStats.sessionsCount }}</span>
            <span class="stat-label">Sessions</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon-wrap time">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatDuration(todayStats.totalTime) }}</span>
            <span class="stat-label">Total Time</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon-wrap satisfaction">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
              <line x1="9" y1="9" x2="9.01" y2="9"></line>
              <line x1="15" y1="9" x2="15.01" y2="9"></line>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value" :style="{ color: getSatisfactionColor(todayStats.avgSatisfaction) }">
              {{ todayStats.avgSatisfaction }}%
            </span>
            <span class="stat-label">Satisfaction</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon-wrap plans">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ todayPlanning.length }}</span>
            <span class="stat-label">Plans Today</span>
          </div>
        </div>
      </div>

      <div class="content-grid">
        <div class="section">
          <div class="section-header">
            <h2 class="section-title">Today's Schedule</h2>
            <RouterLink to="/planning" class="section-link">View calendar →</RouterLink>
          </div>

          <div v-if="todayPlanning.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <p>No plans for today</p>
            <RouterLink to="/planning" class="empty-action">Add a plan</RouterLink>
          </div>

          <div v-else class="planning-list">
            <div
              v-for="plan in todayPlanning"
              :key="plan.id"
              class="planning-item"
            >
              <div class="planning-time-col">
                <span class="planning-time">{{ formatTime(plan.scheduled_start) }}</span>
                <span class="planning-duration">{{ formatDuration(dayjs.utc(plan.scheduled_end).local().diff(dayjs.utc(plan.scheduled_start).local(), 'minute')) }}</span>
              </div>
              <div class="planning-accent" :style="{ backgroundColor: plan.project.color }"></div>
              <div class="planning-body">
                <div class="planning-project-name" :style="{ color: plan.project.color }">
                  {{ plan.project.name }}
                </div>
                <div v-if="plan.description" class="planning-desc">{{ plan.description }}</div>
              </div>
              <div class="planning-priority">
                <span
                  class="priority-badge"
                  :style="{ backgroundColor: getPriorityBadge(plan.priority).bg, color: getPriorityBadge(plan.priority).color }"
                >
                  {{ getPriorityBadge(plan.priority).label }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="section">
          <div class="section-header">
            <h2 class="section-title">Recent Sessions</h2>
            <RouterLink to="/sessions" class="section-link">View all →</RouterLink>
          </div>

          <div v-if="recentSessions.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <p>No sessions yet</p>
            <button @click="openStartDialog" class="empty-action">Start your first session</button>
          </div>

          <div v-else class="sessions-list">
            <div
              v-for="session in recentSessions"
              :key="session.id"
              class="session-item"
            >
              <div class="session-color" :style="{ backgroundColor: session.project?.color || '#94a3b8' }"></div>
              <div class="session-body">
                <div class="session-top">
                  <span class="session-project">{{ session.project?.name || 'No Project' }}</span>
                  <span class="session-duration">{{ formatDuration(session.actual_duration || 0) }}</span>
                </div>
                <div class="session-meta">
                  <span class="session-time">{{ dayjs(session.start_time).fromNow() }}</span>
                  <span
                    v-if="session.satisfaction_score !== null"
                    class="session-satisfaction"
                    :style="{ color: getSatisfactionColor(session.satisfaction_score) }"
                  >
                    {{ session.satisfaction_score }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
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

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1280px;
  margin: 0 auto;
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.025em;
}

.page-subtitle {
  color: #64748b;
  margin: 0.25rem 0 0 0;
  font-size: 0.95rem;
}

.btn-start {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-start:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.btn-start:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #64748b;
  box-shadow: none;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.retry-btn {
  margin-left: auto;
  padding: 0.375rem 0.75rem;
  background: white;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
}

.retry-btn:hover { background: #fef2f2; }

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: white;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  transition: all var(--transition);
}

.stat-card:hover {
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.stat-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-icon-wrap.sessions { background: #eef2ff; color: #6366f1; }
.stat-icon-wrap.time { background: #ecfdf5; color: #10b981; }
.stat-icon-wrap.satisfaction { background: #fef3c7; color: #f59e0b; }
.stat-icon-wrap.plans { background: #fce7f3; color: #ec4899; }

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.section {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.section-link {
  color: #6366f1;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: color var(--transition);
}

.section-link:hover { color: #4f46e5; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: #94a3b8;
}

.empty-icon {
  width: 56px;
  height: 56px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.empty-icon svg { width: 24px; height: 24px; color: #cbd5e1; }

.empty-state p { margin: 0 0 0.75rem; font-size: 0.95rem; }

.empty-action {
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.875rem;
  background: none;
  border: none;
  cursor: pointer;
}

.empty-action:hover { color: #4f46e5; }

.planning-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.planning-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: #f8fafc;
  border-radius: 10px;
  transition: all var(--transition);
}

.planning-item:hover { background: #f1f5f9; }

.planning-time-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 64px;
  flex-shrink: 0;
}

.planning-time {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}

.planning-duration {
  font-size: 0.7rem;
  color: #94a3b8;
}

.planning-accent {
  width: 3px;
  height: 36px;
  border-radius: 2px;
  flex-shrink: 0;
}

.planning-body { flex: 1; min-width: 0; }

.planning-project-name {
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.planning-desc {
  font-size: 0.8rem;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 0.125rem;
}

.planning-priority { flex-shrink: 0; }

.priority-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 10px;
  transition: all var(--transition);
}

.session-item:hover { background: #f1f5f9; }

.session-color {
  width: 3px;
  height: 32px;
  border-radius: 2px;
  flex-shrink: 0;
}

.session-body { flex: 1; min-width: 0; }

.session-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-project {
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-duration {
  font-size: 0.8rem;
  font-weight: 600;
  color: #10b981;
  flex-shrink: 0;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.125rem;
}

.session-time {
  font-size: 0.75rem;
  color: #94a3b8;
}

.session-satisfaction {
  font-size: 0.75rem;
  font-weight: 600;
}

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .dashboard { padding: 1rem; }
  .page-header { flex-direction: column; gap: 1rem; }
  .content-grid { grid-template-columns: 1fr; }
}
</style>
