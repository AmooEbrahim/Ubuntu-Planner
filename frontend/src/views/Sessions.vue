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
  <div class="p-6 max-w-7xl mx-auto space-y-5">
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h1 class="page-title">Sessions</h1>
        <p class="page-subtitle">Track and review your work sessions</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="openStartDialog"
          :disabled="activeSession !== null"
          class="btn btn-success"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          {{ activeSession ? 'Session Active' : 'Start Session' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="glass-card border-l-4 border-danger/60 bg-danger/5 flex items-center gap-2 px-4 py-3 text-danger text-sm">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" class="flex-shrink-0">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span class="flex-1">{{ error }}</span>
      <button @click="loadData" class="btn btn-secondary btn-sm">Retry</button>
    </div>

    <div v-if="activeSession" class="glass-card border-l-4 border-success/60 bg-success/5 flex items-center gap-3 px-4 py-3">
      <div class="w-2.5 h-2.5 bg-success rounded-full animate-pulse flex-shrink-0"></div>
      <div class="flex flex-col">
        <span class="text-[11px] font-bold text-success uppercase tracking-wide">Active session</span>
        <span class="text-sm font-semibold text-fg">{{ activeSession.project?.name || 'No Project' }}</span>
        <span class="text-xs text-muted">Started {{ dayjs(activeSession.start_time).fromNow() }} · {{ formatDuration(sessionStore.elapsedMinutes) }} elapsed</span>
      </div>
    </div>

    <div v-if="loading" class="glass-card flex flex-col items-center justify-center py-16 px-6 text-muted">
      <div class="spinner mb-4"></div>
      <p>Loading sessions...</p>
    </div>

    <div v-else class="space-y-5">
      <div class="grid grid-cols-3 sm:flex sm:flex-row gap-3">
        <div class="glass-card p-4 flex flex-col items-center flex-1 min-w-[120px]">
          <span class="text-2xl font-bold text-fg">{{ summaryStats.count }}</span>
          <span class="text-xs text-muted uppercase tracking-wide mt-0.5">Sessions</span>
        </div>
        <div class="glass-card p-4 flex flex-col items-center flex-1 min-w-[120px]">
          <span class="text-2xl font-bold text-fg">{{ formatDuration(summaryStats.totalMin) }}</span>
          <span class="text-xs text-muted uppercase tracking-wide mt-0.5">Total Time</span>
        </div>
        <div class="glass-card p-4 flex flex-col items-center flex-1 min-w-[120px]">
          <span class="text-2xl font-bold" :style="{ color: getSatisfactionColor(summaryStats.avgSat) }">{{ summaryStats.avgSat }}%</span>
          <span class="text-xs text-muted uppercase tracking-wide mt-0.5">Avg Satisfaction</span>
        </div>
      </div>

      <div class="glass-card p-4 flex flex-wrap items-end gap-3">
        <div class="flex flex-col gap-1">
          <label class="text-xs font-semibold text-muted">From</label>
          <input type="date" v-model="filters.dateFrom" class="input text-xs py-1.5 w-auto">
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs font-semibold text-muted">To</label>
          <input type="date" v-model="filters.dateTo" class="input text-xs py-1.5 w-auto">
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs font-semibold text-muted">Project</label>
          <select v-model="filters.projectId" class="input text-xs py-1.5 w-auto">
            <option :value="null">All</option>
            <option v-for="p in projectStore.activeProjects" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs font-semibold text-muted">Min Satisfaction</label>
          <input type="number" v-model.number="filters.minSatisfaction" min="0" max="100" placeholder="Any" class="input text-xs py-1.5 w-24">
        </div>
        <div class="flex gap-2 ml-auto">
          <button @click="clearFilters" class="btn btn-ghost btn-sm">Clear</button>
          <button @click="exportToCSV" class="btn btn-secondary btn-sm" title="Export CSV">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Export
          </button>
        </div>
      </div>

      <div v-if="filteredSessions.length === 0" class="glass-card flex flex-col items-center justify-center py-16 px-6 text-center">
        <div class="flex items-center justify-center w-16 h-16 rounded-full bg-fg-subtle/15 text-fg-subtle mb-4">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="28" height="28">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <h3 class="text-base font-semibold text-fg mb-1">No sessions found</h3>
        <p class="text-sm text-muted mb-4">Start your first session to track your work!</p>
        <button @click="openStartDialog" class="btn btn-success">
          <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          Start Session
        </button>
      </div>

      <div v-else class="space-y-2.5">
        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="glass-card flex overflow-hidden transition-all duration-200 hover:-translate-y-0.5"
        >
          <div class="w-1 flex-shrink-0" :style="{ backgroundColor: session.project?.color || '#94a3b8' }"></div>
          <div class="flex-1 p-5 min-w-0">
            <div class="flex justify-between items-start gap-4 mb-3">
              <div class="min-w-0">
                <h3 class="text-base font-semibold text-fg">{{ session.project?.name || 'No Project' }}</h3>
                <span class="text-xs text-subtle mt-0.5 block">{{ dayjs(session.start_time).format('MMM D, YYYY · h:mm A') }}</span>
              </div>
              <div class="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-success/15 text-success text-sm font-semibold flex-shrink-0">
                {{ formatDuration(session.actual_duration || 0) }}
                <span v-if="session.actual_duration > session.planned_duration" class="text-danger text-xs">
                  +{{ formatDuration(session.actual_duration - session.planned_duration) }}
                </span>
              </div>
            </div>

            <div class="flex gap-6 mb-3">
              <div class="flex flex-col gap-0.5">
                <span class="text-[11px] text-subtle uppercase tracking-wide">Planned</span>
                <span class="text-sm font-semibold text-fg">{{ formatDuration(session.planned_duration) }}</span>
              </div>
              <div v-if="session.satisfaction_score !== null" class="flex flex-col gap-0.5">
                <span class="text-[11px] text-subtle uppercase tracking-wide">Satisfaction</span>
                <span class="text-sm font-bold" :style="{ color: getSatisfactionColor(session.satisfaction_score) }">{{ session.satisfaction_score }}%</span>
              </div>
            </div>

            <div v-if="session.tasks_done" class="glass-inset flex items-start gap-2 px-3 py-2 mb-2 text-sm text-muted">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14" class="flex-shrink-0 mt-0.5 text-fg-subtle">
                <polyline points="9 11 12 14 22 4"></polyline>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              <span>{{ session.tasks_done }}</span>
            </div>

            <div v-if="session.notes" class="glass-inset flex items-start gap-2 px-3 py-2 mb-2 text-sm text-muted">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14" class="flex-shrink-0 mt-0.5 text-fg-subtle">
                <line x1="17" y1="10" x2="3" y2="10"></line>
                <line x1="21" y1="6" x2="3" y2="6"></line>
                <line x1="21" y1="14" x2="3" y2="14"></line>
                <line x1="17" y1="18" x2="3" y2="18"></line>
              </svg>
              <pre class="m-0 whitespace-pre-wrap font-sans text-fg-muted text-sm">{{ session.notes }}</pre>
            </div>

            <div v-if="session.tags && session.tags.length > 0" class="flex flex-wrap gap-1.5 mt-2">
              <span
                v-for="tag in session.tags"
                :key="tag.id"
                class="px-2 py-0.5 rounded-md text-xs font-semibold"
                :style="{ backgroundColor: tag.color + '20', color: tag.color }"
              >{{ tag.name }}</span>
            </div>
          </div>

          <div class="flex flex-col justify-center gap-1 p-3 border-l border-fg-subtle/15">
            <button @click="openEditDialog(session)" class="icon-btn !w-8 !h-8 hover:!text-accent hover:!bg-accent/15" title="Edit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button @click="handleDeleteSession(session)" class="icon-btn !w-8 !h-8 hover:!text-danger hover:!bg-danger/15" title="Delete">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
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
