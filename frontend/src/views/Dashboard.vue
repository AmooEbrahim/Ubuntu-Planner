<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanningStore } from '@/stores/planning'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import StartSessionDialog from '@/components/StartSessionDialog.vue'
import dayjs from 'dayjs'

const planningStore = usePlanningStore()
const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const showStartDialog = ref(false)
const loading = ref(false)
const error = ref('')

const activeSession = computed(() => sessionStore.activeSession)
const todayPlanning = computed(() => planningStore.todayPlanning)
const recentSessions = computed(() => sessionStore.recentSessions.slice(0, 5))

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
  return dayjs(datetime).format('HH:mm')
}

function formatDateTime(datetime) {
  return dayjs(datetime).format('MMM D, HH:mm')
}

function getSatisfactionColor(score) {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
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
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Overview of your work today</p>
    </div>

    <div v-if="error" class="error-banner">
      {{ error }}
      <button @click="loadData" class="retry-btn">Retry</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading dashboard...</p>
    </div>

    <div v-else class="dashboard-content">
      <!-- Today's Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ todayStats.sessionsCount }}</div>
          <div class="stat-label">Sessions Today</div>
        </div>

        <div class="stat-card">
          <div class="stat-value">{{ formatDuration(todayStats.totalTime) }}</div>
          <div class="stat-label">Total Time</div>
        </div>

        <div class="stat-card">
          <div class="stat-value" :style="{ color: getSatisfactionColor(todayStats.avgSatisfaction) }">
            {{ todayStats.avgSatisfaction }}%
          </div>
          <div class="stat-label">Avg Satisfaction</div>
        </div>

        <div
          class="stat-card action"
          @click="openStartDialog"
          :class="{ disabled: activeSession !== null }"
          :title="activeSession ? 'A session is already active' : 'Start a new session'"
        >
          <div class="stat-icon">▶️</div>
          <div class="stat-label">{{ activeSession ? 'Session Active' : 'Start Session' }}</div>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div class="content-grid">
        <!-- Left Column: Today's Planning -->
        <div class="section">
          <div class="section-header">
            <h2 class="section-title">Today's Planning</h2>
            <RouterLink to="/planning" class="section-link">View All →</RouterLink>
          </div>

          <div v-if="todayPlanning.length === 0" class="empty-state">
            <p>No planning for today</p>
            <RouterLink to="/planning" class="empty-link">Add Planning</RouterLink>
          </div>

          <div v-else class="planning-list">
            <div
              v-for="plan in todayPlanning"
              :key="plan.id"
              class="planning-item"
              :class="{ critical: plan.priority === 'critical' }"
            >
              <div class="planning-time">{{ formatTime(plan.scheduled_start) }}</div>
              <div class="planning-content">
                <div class="planning-project" :style="{ borderLeftColor: plan.project.color }">
                  {{ plan.project.name }}
                </div>
                <div v-if="plan.description" class="planning-description">
                  {{ plan.description }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Recent Sessions -->
        <div class="section">
          <div class="section-header">
            <h2 class="section-title">Recent Sessions</h2>
            <RouterLink to="/sessions" class="section-link">View All →</RouterLink>
          </div>

          <div v-if="recentSessions.length === 0" class="empty-state">
            <p>No recent sessions</p>
            <button @click="openStartDialog" class="empty-link">Start Session</button>
          </div>

          <div v-else class="sessions-list">
            <div
              v-for="session in recentSessions"
              :key="session.id"
              class="session-item"
            >
              <div class="session-header">
                <div class="session-project">
                  <div
                    v-if="session.project"
                    class="project-color"
                    :style="{ backgroundColor: session.project.color }"
                  ></div>
                  <span class="project-name">{{ session.project?.name || 'No Project' }}</span>
                </div>
                <div class="session-duration">
                  {{ formatDuration(session.actual_duration || 0) }}
                </div>
              </div>
              <div class="session-meta">
                <span class="session-time">
                  {{ formatDateTime(session.start_time) }}
                </span>
                <span v-if="session.satisfaction_score !== null" class="session-satisfaction">
                  <span :style="{ color: getSatisfactionColor(session.satisfaction_score) }">
                    {{ session.satisfaction_score }}%
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <StartSessionDialog
      v-if="showStartDialog"
      @close="showStartDialog = false"
      @started="handleSessionStarted"
    />
  </div>
</template>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
  margin: 0.25rem 0 0 0;
}

.error-banner {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.retry-btn {
  background-color: white;
  border: 1px solid #b91c1c;
  color: #b91c1c;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.retry-btn:hover {
  background-color: #fef2f2;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: all 0.2s;
}

.stat-card.action {
  cursor: pointer;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.stat-card.action:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
}

.stat-card.action.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #6b7280;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

.stat-card.action .stat-value {
  color: white;
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-card.action .stat-label {
  color: white;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.section-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 600;
  transition: color 0.2s;
}

.section-link:hover {
  color: #2563eb;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty-state p {
  margin: 0 0 0.5rem 0;
}

.empty-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 600;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
}

.empty-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

.planning-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.planning-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 6px;
  background: #f9fafb;
  transition: all 0.2s;
}

.planning-item:hover {
  background: #f3f4f6;
}

.planning-item.critical {
  background: #fef2f2;
  border-left: 3px solid #ef4444;
}

.planning-time {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  min-width: 45px;
}

.planning-content {
  flex: 1;
}

.planning-project {
  font-weight: 600;
  color: #111827;
  font-size: 0.875rem;
  padding-left: 0.5rem;
  border-left: 3px solid;
}

.planning-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
  padding-left: 0.5rem;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.session-item {
  padding: 0.75rem;
  border-radius: 6px;
  background: #f9fafb;
  transition: all 0.2s;
}

.session-item:hover {
  background: #f3f4f6;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.session-project {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.project-color {
  width: 3px;
  height: 20px;
  border-radius: 1px;
}

.project-name {
  font-weight: 600;
  color: #111827;
  font-size: 0.875rem;
}

.session-duration {
  font-weight: 600;
  color: #10b981;
  font-size: 0.875rem;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: #6b7280;
}

.session-satisfaction {
  font-weight: 600;
}
</style>
