<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import StartSessionDialog from '@/components/StartSessionDialog.vue'
import EditSessionDialog from '@/components/EditSessionDialog.vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

const sessionStore = useSessionStore()
const projectStore = useProjectStore()
const showStartDialog = ref(false)
const showEditDialog = ref(false)
const sessionToEdit = ref(null)
const loading = ref(false)
const error = ref('')

const filters = ref({
  dateFrom: dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dateTo: dayjs().format('YYYY-MM-DD'),
  projectId: null,
  minSatisfaction: null
})

const activeSession = computed(() => sessionStore.activeSession)

const filteredSessions = computed(() => {
  let sessions = sessionStore.recentSessions.filter(s => s.end_time !== null)
  if (filters.value.projectId) {
    sessions = sessions.filter(s => s.project_id === filters.value.projectId)
  }
  if (filters.value.minSatisfaction !== null && filters.value.minSatisfaction !== '') {
    sessions = sessions.filter(s =>
      s.satisfaction_score !== null && s.satisfaction_score >= filters.value.minSatisfaction
    )
  }
  sessions = sessions.filter(s => {
    const date = dayjs(s.start_time).format('YYYY-MM-DD')
    return date >= filters.value.dateFrom && date <= filters.value.dateTo
  })
  return sessions
})

const summaryStats = computed(() => {
  const sessions = filteredSessions.value
  const totalMin = sessions.reduce((sum, s) => sum + (s.actual_duration || 0), 0)
  const avgSat = sessions.filter(s => s.satisfaction_score !== null)
  const avg = avgSat.length > 0 ? Math.round(avgSat.reduce((s, x) => s + x.satisfaction_score, 0) / avgSat.length) : 0
  return { count: sessions.length, totalMin, avgSat: avg }
})

onMounted(async () => { await loadData() })

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([
      sessionStore.fetchActiveSession(),
      sessionStore.fetchRecentSessions(200),
      projectStore.fetchProjects()
    ])
  } catch (err) {
    error.value = 'Failed to load sessions'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function exportToCSV() {
  const headers = ['Date', 'Project', 'Planned (min)', 'Actual (min)', 'Satisfaction (%)', 'Tasks', 'Notes', 'Tags']
  const rows = filteredSessions.value.map(s => [
    dayjs(s.start_time).format('YYYY-MM-DD HH:mm'),
    s.project?.name || 'No Project',
    s.planned_duration || 0,
    s.actual_duration || 0,
    s.satisfaction_score !== null ? s.satisfaction_score : '',
    s.tasks_done || '',
    s.notes || '',
    s.tags ? s.tags.map(t => t.name).join('; ') : ''
  ])
  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
  ].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `sessions-${dayjs().format('YYYY-MM-DD')}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function clearFilters() {
  filters.value = {
    dateFrom: dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
    dateTo: dayjs().format('YYYY-MM-DD'),
    projectId: null,
    minSatisfaction: null
  }
}

function openStartDialog() { showStartDialog.value = true }
function handleSessionStarted() { showStartDialog.value = false; loadData() }

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

function openEditDialog(session) { sessionToEdit.value = session; showEditDialog.value = true }
function handleSessionUpdated() { showEditDialog.value = false; sessionToEdit.value = null; loadData() }

async function handleDeleteSession(session) {
  if (confirm(`Delete session for ${session.project?.name || 'No Project'}?`)) {
    try { await sessionStore.deleteSession(session.id) }
    catch (err) { alert('Error deleting session: ' + (err.response?.data?.detail || err.message)) }
  }
}
</script>

<template>
  <div class="sessions-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Sessions</h1>
        <p class="page-subtitle">Track and review your work sessions</p>
      </div>
      <div class="header-actions">
        <button
          @click="openStartDialog"
          :disabled="activeSession !== null"
          class="btn-primary"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          {{ activeSession ? 'Session Active' : 'Start Session' }}
        </button>
      </div>
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

    <div v-if="activeSession" class="active-banner">
      <div class="active-dot"></div>
      <div class="active-info">
        <span class="active-label">Active session</span>
        <span class="active-project">{{ activeSession.project?.name || 'No Project' }}</span>
        <span class="active-time">Started {{ dayjs(activeSession.start_time).fromNow() }} · {{ formatDuration(sessionStore.elapsedMinutes) }} elapsed</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading sessions...</p>
    </div>

    <div v-else class="sessions-content">
      <div class="summary-row">
        <div class="summary-card">
          <span class="summary-value">{{ summaryStats.count }}</span>
          <span class="summary-label">Sessions</span>
        </div>
        <div class="summary-card">
          <span class="summary-value">{{ formatDuration(summaryStats.totalMin) }}</span>
          <span class="summary-label">Total Time</span>
        </div>
        <div class="summary-card">
          <span class="summary-value" :style="{ color: getSatisfactionColor(summaryStats.avgSat) }">{{ summaryStats.avgSat }}%</span>
          <span class="summary-label">Avg Satisfaction</span>
        </div>
      </div>

      <div class="filters-bar">
        <div class="filter-field">
          <label class="filter-label">From</label>
          <input type="date" v-model="filters.dateFrom" class="filter-input">
        </div>
        <div class="filter-field">
          <label class="filter-label">To</label>
          <input type="date" v-model="filters.dateTo" class="filter-input">
        </div>
        <div class="filter-field">
          <label class="filter-label">Project</label>
          <select v-model="filters.projectId" class="filter-select">
            <option :value="null">All</option>
            <option v-for="p in projectStore.activeProjects" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="filter-field">
          <label class="filter-label">Min Satisfaction</label>
          <input type="number" v-model.number="filters.minSatisfaction" min="0" max="100" placeholder="Any" class="filter-input">
        </div>
        <div class="filter-actions">
          <button @click="clearFilters" class="filter-clear">Clear</button>
          <button @click="exportToCSV" class="filter-export" title="Export CSV">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Export
          </button>
        </div>
      </div>

      <div v-if="filteredSessions.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <h3>No sessions found</h3>
        <p>Start your first session to track your work!</p>
        <button @click="openStartDialog" class="btn-primary mt-4">
          <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          Start Session
        </button>
      </div>

      <div v-else class="sessions-list">
        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="session-card"
        >
          <div class="session-accent" :style="{ backgroundColor: session.project?.color || '#94a3b8' }"></div>
          <div class="session-body">
            <div class="session-top-row">
              <div class="session-project-info">
                <h3 class="session-project-name">{{ session.project?.name || 'No Project' }}</h3>
                <span class="session-date">{{ dayjs(session.start_time).format('MMM D, YYYY · h:mm A') }}</span>
              </div>
              <div class="session-duration-badge">
                {{ formatDuration(session.actual_duration || 0) }}
                <span v-if="session.actual_duration > session.planned_duration" class="overtime-tag">
                  +{{ formatDuration(session.actual_duration - session.planned_duration) }}
                </span>
              </div>
            </div>

            <div class="session-metrics">
              <div class="metric">
                <span class="metric-label">Planned</span>
                <span class="metric-value">{{ formatDuration(session.planned_duration) }}</span>
              </div>
              <div v-if="session.satisfaction_score !== null" class="metric">
                <span class="metric-label">Satisfaction</span>
                <span class="metric-value sat" :style="{ color: getSatisfactionColor(session.satisfaction_score) }">
                  {{ session.satisfaction_score }}%
                </span>
              </div>
            </div>

            <div v-if="session.tasks_done" class="session-tasks">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <polyline points="9 11 12 14 22 4"></polyline>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              <span>{{ session.tasks_done }}</span>
            </div>

            <div v-if="session.notes" class="session-notes">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <line x1="17" y1="10" x2="3" y2="10"></line>
                <line x1="21" y1="6" x2="3" y2="6"></line>
                <line x1="21" y1="14" x2="3" y2="14"></line>
                <line x1="17" y1="18" x2="3" y2="18"></line>
              </svg>
              <pre class="notes-text">{{ session.notes }}</pre>
            </div>

            <div v-if="session.tags && session.tags.length > 0" class="session-tags">
              <span
                v-for="tag in session.tags"
                :key="tag.id"
                class="session-tag"
                :style="{ backgroundColor: tag.color + '20', color: tag.color }"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>

          <div class="session-actions">
            <button @click="openEditDialog(session)" class="action-btn edit" title="Edit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button @click="handleDeleteSession(session)" class="action-btn delete" title="Delete">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <Transition name="modal">
      <StartSessionDialog v-if="showStartDialog" @close="showStartDialog = false" @started="handleSessionStarted" />
    </Transition>
    <Transition name="modal">
      <EditSessionDialog v-if="showEditDialog && sessionToEdit" :session="sessionToEdit" @close="showEditDialog = false" @saved="handleSessionUpdated" />
    </Transition>
  </div>
</template>

<style scoped>
.sessions-page { max-width: 1280px; margin: 0 auto; padding: 2rem; --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.page-title { font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.025em; }
.page-subtitle { color: #64748b; margin: 0.25rem 0 0; font-size: 0.95rem; }

.btn-primary {
  display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669); color: white; border: none;
  border-radius: 12px; font-size: 0.95rem; font-weight: 600; cursor: pointer;
  transition: all var(--transition); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; background: #64748b; box-shadow: none; }

.error-banner { display: flex; align-items: center; gap: 0.625rem; padding: 0.75rem 1rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; color: #dc2626; font-size: 0.875rem; margin-bottom: 1.5rem; }
.retry-btn { margin-left: auto; padding: 0.375rem 0.75rem; background: white; border: 1px solid #fecaca; border-radius: 6px; color: #dc2626; font-size: 0.8rem; font-weight: 600; cursor: pointer; }
.retry-btn:hover { background: #fef2f2; }

.active-banner { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.25rem; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; margin-bottom: 1.5rem; }
.active-dot { width: 10px; height: 10px; background: #10b981; border-radius: 50%; animation: pulse 2s ease-in-out infinite; flex-shrink: 0; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.active-info { display: flex; flex-direction: column; gap: 0.125rem; }
.active-label { font-size: 0.7rem; font-weight: 600; color: #059669; text-transform: uppercase; letter-spacing: 0.05em; }
.active-project { font-size: 0.95rem; font-weight: 600; color: #065f46; }
.active-time { font-size: 0.8rem; color: #6ee7b7; }

.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #10b981; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

.summary-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.summary-card { display: flex; flex-direction: column; align-items: center; padding: 1rem 1.5rem; background: white; border-radius: 12px; border: 1px solid #e2e8f0; min-width: 120px; }
.summary-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; }
.summary-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.125rem; }

.filters-bar { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: flex-end; padding: 1rem 1.25rem; background: white; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem; }
.filter-field { display: flex; flex-direction: column; gap: 0.25rem; }
.filter-label { font-size: 0.75rem; font-weight: 600; color: #64748b; }
.filter-input, .filter-select { padding: 0.5rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.85rem; color: #0f172a; background: white; }
.filter-input:focus, .filter-select:focus { outline: none; border-color: #10b981; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1); }
.filter-actions { display: flex; gap: 0.5rem; margin-left: auto; align-self: flex-end; }
.filter-clear { padding: 0.5rem 0.75rem; border: none; background: transparent; color: #64748b; font-size: 0.85rem; font-weight: 500; cursor: pointer; border-radius: 8px; }
.filter-clear:hover { background: #f1f5f9; }
.filter-export { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.5rem 0.75rem; border: 1px solid #e2e8f0; background: white; border-radius: 8px; font-size: 0.85rem; font-weight: 500; color: #334155; cursor: pointer; }
.filter-export:hover { background: #f8fafc; border-color: #10b981; color: #10b981; }

.empty-state { display: flex; flex-direction: column; align-items: center; padding: 4rem 2rem; text-align: center; }
.empty-icon { width: 80px; height: 80px; background: #f1f5f9; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem; }
.empty-icon svg { width: 36px; height: 36px; color: #94a3b8; }
.empty-state h3 { font-size: 1.25rem; font-weight: 600; color: #0f172a; margin: 0 0 0.5rem; }
.empty-state p { color: #64748b; margin: 0; }

.sessions-list { display: flex; flex-direction: column; gap: 0.75rem; }
.session-card { display: flex; background: white; border-radius: 14px; border: 1px solid #e2e8f0; overflow: hidden; transition: all var(--transition); }
.session-card:hover { border-color: transparent; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06); }
.session-accent { width: 4px; flex-shrink: 0; }
.session-body { flex: 1; padding: 1.25rem; min-width: 0; }
.session-top-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 0.75rem; }
.session-project-info { min-width: 0; }
.session-project-name { font-size: 1rem; font-weight: 600; color: #0f172a; margin: 0; }
.session-date { font-size: 0.8rem; color: #94a3b8; margin-top: 0.125rem; }
.session-duration-badge { display: flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.75rem; background: #ecfdf5; border-radius: 8px; font-size: 0.85rem; font-weight: 600; color: #059669; flex-shrink: 0; }
.overtime-tag { color: #ef4444; font-size: 0.75rem; }

.session-metrics { display: flex; gap: 1.5rem; margin-bottom: 0.75rem; }
.metric { display: flex; flex-direction: column; gap: 0.125rem; }
.metric-label { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-value { font-size: 0.9rem; font-weight: 600; color: #334155; }
.metric-value.sat { font-weight: 700; }

.session-tasks, .session-notes { display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.5rem 0.75rem; background: #f8fafc; border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.85rem; color: #475569; }
.session-tasks svg, .session-notes svg { flex-shrink: 0; margin-top: 2px; color: #94a3b8; }
.notes-text { margin: 0; white-space: pre-wrap; font-family: inherit; color: #64748b; font-size: 0.85rem; }

.session-tags { display: flex; flex-wrap: wrap; gap: 0.375rem; margin-top: 0.5rem; }
.session-tag { padding: 0.2rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }

.session-actions { display: flex; flex-direction: column; justify-content: center; gap: 0.375rem; padding: 1rem; border-left: 1px solid #f1f5f9; }
.action-btn { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: none; background: transparent; border-radius: 8px; cursor: pointer; transition: all var(--transition); }
.action-btn.edit { color: #6366f1; }
.action-btn.edit:hover { background: #6366f1; color: white; }
.action-btn.delete { color: #ef4444; }
.action-btn.delete:hover { background: #ef4444; color: white; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .sessions-page { padding: 1rem; }
  .page-header { flex-direction: column; gap: 1rem; }
  .summary-row { flex-wrap: wrap; }
  .filters-bar { flex-direction: column; align-items: stretch; }
  .filter-actions { margin-left: 0; justify-content: flex-end; }
  .session-card { flex-direction: column; }
  .session-actions { flex-direction: row; border-left: none; border-top: 1px solid #f1f5f9; padding: 0.75rem 1rem; }
}
</style>
