<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import StartSessionDialog from '@/components/StartSessionDialog.vue'
import dayjs from 'dayjs'

const sessionStore = useSessionStore()
const showStartDialog = ref(false)
const loading = ref(false)
const error = ref('')

const activeSession = computed(() => sessionStore.activeSession)
const recentSessions = computed(() => sessionStore.recentSessions)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([sessionStore.fetchActiveSession(), sessionStore.fetchRecentSessions(50)])
  } catch (err) {
    error.value = 'Failed to load sessions'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function openStartDialog() {
  showStartDialog.value = true
}

function handleSessionStarted() {
  showStartDialog.value = false
  loadData()
}

function formatDateTime(datetime) {
  return dayjs(datetime).format('MMM D, YYYY HH:mm')
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

function getSatisfactionColor(score) {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

function getSatisfactionEmoji(score) {
  if (score >= 80) return '😊'
  if (score >= 60) return '🙂'
  if (score >= 40) return '😐'
  return '😞'
}
</script>

<template>
  <div class="sessions-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Sessions</h1>
        <p class="page-subtitle">Track and review your work sessions</p>
      </div>
      <button
        @click="openStartDialog"
        :disabled="activeSession !== null"
        class="btn-primary"
        :title="activeSession ? 'A session is already active' : 'Start a new session'"
      >
        {{ activeSession ? 'Session Active' : '+ Start Session' }}
      </button>
    </div>

    <div v-if="error" class="error-banner">
      {{ error }}
      <button @click="loadData" class="retry-btn">Retry</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading sessions...</p>
    </div>

    <div v-else class="sessions-content">
      <!-- Active Session Info -->
      <div v-if="activeSession" class="active-session-notice">
        <div class="notice-content">
          <span class="status-indicator">🟢</span>
          <div>
            <strong>Active Session:</strong> {{ activeSession.project?.name || 'No Project' }}
            <div class="notice-details">
              Started {{ formatDateTime(activeSession.start_time) }} •
              {{ formatDuration(sessionStore.elapsedMinutes) }} elapsed
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Sessions -->
      <div class="sessions-section">
        <h2 class="section-title">Recent Sessions</h2>

        <div v-if="recentSessions.length === 0" class="empty-state">
          <p>No sessions yet</p>
          <p class="empty-hint">Start your first session to track your work!</p>
        </div>

        <div v-else class="sessions-list">
          <div v-for="session in recentSessions" :key="session.id" class="session-card">
            <div class="session-header">
              <div class="session-project">
                <div
                  v-if="session.project"
                  class="project-color"
                  :style="{ backgroundColor: session.project.color }"
                ></div>
                <span class="project-name">{{ session.project?.name || 'No Project' }}</span>
              </div>
              <div class="session-date">
                {{ formatDateTime(session.start_time) }}
              </div>
            </div>

            <div class="session-stats">
              <div class="stat">
                <span class="stat-label">Duration:</span>
                <span class="stat-value">{{ formatDuration(session.actual_duration) }}</span>
                <span v-if="session.actual_duration > session.planned_duration" class="overtime">
                  (+{{ formatDuration(session.actual_duration - session.planned_duration) }})
                </span>
              </div>
              <div class="stat">
                <span class="stat-label">Planned:</span>
                <span class="stat-value">{{ formatDuration(session.planned_duration) }}</span>
              </div>
              <div v-if="session.satisfaction_score !== null" class="stat">
                <span class="stat-label">Satisfaction:</span>
                <span
                  class="stat-value satisfaction"
                  :style="{ color: getSatisfactionColor(session.satisfaction_score) }"
                >
                  {{ getSatisfactionEmoji(session.satisfaction_score) }}
                  {{ session.satisfaction_score }}%
                </span>
              </div>
            </div>

            <div v-if="session.tasks_done" class="session-tasks">
              <strong>Tasks:</strong> {{ session.tasks_done }}
            </div>

            <div v-if="session.notes" class="session-notes">
              <strong>Notes:</strong>
              <pre class="notes-content">{{ session.notes }}</pre>
            </div>

            <div v-if="session.tags && session.tags.length > 0" class="session-tags">
              <span
                v-for="tag in session.tags"
                :key="tag.id"
                class="tag"
                :style="{ backgroundColor: tag.color }"
              >
                {{ tag.name }}
              </span>
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
.sessions-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.btn-primary:hover:not(:disabled) {
  background-color: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
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

.active-session-notice {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border: 2px solid #10b981;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.notice-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-indicator {
  font-size: 1.25rem;
}

.notice-details {
  font-size: 0.875rem;
  color: #059669;
  margin-top: 0.25rem;
}

.sessions-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #111827;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.empty-hint {
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.session-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.session-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.session-project {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.project-color {
  width: 4px;
  height: 24px;
  border-radius: 2px;
}

.project-name {
  font-weight: 700;
  font-size: 1.125rem;
  color: #111827;
}

.session-date {
  font-size: 0.875rem;
  color: #6b7280;
}

.session-stats {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.stat-label {
  color: #6b7280;
}

.stat-value {
  font-weight: 600;
  color: #111827;
}

.overtime {
  color: #ef4444;
  font-weight: 600;
}

.satisfaction {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.session-tasks,
.session-notes {
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: #374151;
}

.notes-content {
  margin-top: 0.25rem;
  white-space: pre-wrap;
  font-family: inherit;
  color: #6b7280;
}

.session-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}
</style>
