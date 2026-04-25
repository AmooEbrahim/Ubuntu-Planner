<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import StartSessionDialog from '@/components/StartSessionDialog.vue'
import EditSessionDialog from '@/components/EditSessionDialog.vue'
import SessionCalendarDay from '@/components/SessionCalendarDay.vue'
import SessionDetailsModal from '@/components/SessionDetailsModal.vue'
import dayjs from 'dayjs'
import isoWeek from 'dayjs/plugin/isoWeek'

dayjs.extend(isoWeek)

const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const showStartDialog = ref(false)
const showEditDialog = ref(false)
const showDetailsModal = ref(false)
const sessionToEdit = ref(null)
const sessionToView = ref(null)
const expandedSessions = ref(new Set())

const selectedDate = ref(dayjs())
const viewMode = ref('calendar')
const loading = ref(false)
const datePickerRef = ref(null)

const selectedDateISO = computed({
  get: () => selectedDate.value.format('YYYY-MM-DD'),
  set: (val) => {
    if (!val) return
    selectedDate.value = dayjs(val)
  },
})

const headerDateLabel = computed(() => {
  const d = selectedDate.value
  if (d.isSame(dayjs(), 'day')) return `Today · ${d.format('MMM D, YYYY')}`
  if (d.isSame(dayjs().subtract(1, 'day'), 'day')) return `Yesterday · ${d.format('MMM D, YYYY')}`
  if (d.isSame(dayjs().add(1, 'day'), 'day')) return `Tomorrow · ${d.format('MMM D, YYYY')}`
  return d.format('ddd, MMM D, YYYY')
})

function openDatePicker() {
  const el = datePickerRef.value
  if (!el) return
  if (typeof el.showPicker === 'function') {
    try { el.showPicker(); return } catch (_) { /* fallback */ }
  }
  el.focus()
  el.click()
}

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    await Promise.all([
      sessionStore.fetchRecentSessions(100),
      projectStore.projects.length === 0 ? projectStore.fetchProjects() : Promise.resolve()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

const sessionsByDate = computed(() => {
  const grouped = {}
  const sessions = sessionStore.recentSessions || []
  sessions.forEach(session => {
    const dateKey = dayjs(session.start_time).format('YYYY-MM-DD')
    if (!grouped[dateKey]) grouped[dateKey] = []
    grouped[dateKey].push(session)
  })
  Object.keys(grouped).forEach(dateKey => {
    grouped[dateKey].sort((a, b) =>
      dayjs(a.start_time).valueOf() - dayjs(b.start_time).valueOf()
    )
  })
  return grouped
})

const calendarSessions = computed(() => {
  const dateKey = selectedDate.value.format('YYYY-MM-DD')
  return sessionsByDate.value[dateKey] || []
})

const displayDates = computed(() => {
  if (viewMode.value === 'calendar' || viewMode.value === 'day') {
    return [selectedDate.value]
  } else if (viewMode.value === '3days') {
    return [
      selectedDate.value.subtract(1, 'day'),
      selectedDate.value,
      selectedDate.value.add(1, 'day')
    ]
  } else {
    const startOfWeek = selectedDate.value.startOf('isoWeek')
    return Array.from({ length: 7 }, (_, i) => startOfWeek.add(i, 'day'))
  }
})

function previousPeriod() {
  if (viewMode.value === 'calendar' || viewMode.value === 'day') {
    selectedDate.value = selectedDate.value.subtract(1, 'day')
  } else if (viewMode.value === '3days') {
    selectedDate.value = selectedDate.value.subtract(3, 'day')
  } else {
    selectedDate.value = selectedDate.value.subtract(1, 'week')
  }
}

function nextPeriod() {
  if (viewMode.value === 'calendar' || viewMode.value === 'day') {
    selectedDate.value = selectedDate.value.add(1, 'day')
  } else if (viewMode.value === '3days') {
    selectedDate.value = selectedDate.value.add(3, 'day')
  } else {
    selectedDate.value = selectedDate.value.add(1, 'week')
  }
}

function goToToday() { selectedDate.value = dayjs() }
function openStartDialog() { showStartDialog.value = true }

function handleSessionStarted() {
  showStartDialog.value = false
  loadData()
}

function openEditDialog(session) {
  sessionToEdit.value = session
  showEditDialog.value = true
}

function handleSessionUpdated() {
  showEditDialog.value = false
  sessionToEdit.value = null
  loadData()
}

function openDetailsModal(session) {
  sessionToView.value = session
  showDetailsModal.value = true
}

function handleDetailsEdit(session) {
  showDetailsModal.value = false
  sessionToView.value = null
  openEditDialog(session)
}

async function handleDetailsDelete(session) {
  showDetailsModal.value = false
  sessionToView.value = null
  await handleDeleteSession(session)
}

async function handleUpdateTimes(data) {
  try {
    await sessionStore.updateSession(data.sessionId, {
      start_time: data.start_time,
      end_time: data.end_time
    })
    await loadData()
    if (sessionToView.value) {
      sessionToView.value = await sessionStore.getSession(data.sessionId)
    }
  } catch (err) {
    alert('Error updating session times: ' + (err.response?.data?.detail || err.message))
    throw err
  }
}

async function handleDeleteSession(session) {
  if (confirm(`Delete session for ${session.project?.name || 'No Project'}?`)) {
    try {
      await sessionStore.deleteSession(session.id)
      await loadData()
    } catch (err) {
      alert('Error deleting session: ' + (err.response?.data?.detail || err.message))
    }
  }
}

const activeSession = computed(() => sessionStore.activeSession)

function formatDuration(minutes) {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours > 0) {
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }
  return `${mins}m`
}

function getSessionDuration(session) {
  if (session.actual_duration) return session.actual_duration
  if (session.end_time) {
    const start = dayjs(session.start_time)
    const end = dayjs(session.end_time)
    return Math.floor(end.diff(start, 'minute'))
  }
  return session.planned_duration
}

function getSessionStatus(session) {
  if (!session.end_time) return 'active'
  const duration = getSessionDuration(session)
  if (duration > session.planned_duration) return 'overtime'
  return 'completed'
}

function getStatusColor(status) {
  switch (status) {
    case 'active': return 'rgb(var(--success))'
    case 'overtime': return 'rgb(var(--warning))'
    case 'completed': return 'rgb(var(--fg-subtle))'
    default: return 'rgb(var(--fg-subtle))'
  }
}

function getDayStats(dateKey) {
  const sessions = sessionsByDate.value[dateKey] || []
  const totalPlanned = sessions.reduce((sum, s) => sum + s.planned_duration, 0)
  const totalActual = sessions.reduce((sum, s) => sum + getSessionDuration(s), 0)
  const completed = sessions.filter(s => s.end_time).length
  return { total: sessions.length, completed, active: sessions.length - completed, totalPlanned, totalActual }
}

function toggleSessionExpansion(sessionId) {
  if (expandedSessions.value.has(sessionId)) {
    expandedSessions.value.delete(sessionId)
  } else {
    expandedSessions.value.add(sessionId)
  }
  expandedSessions.value = new Set(expandedSessions.value)
}

function isSessionExpanded(sessionId) {
  return expandedSessions.value.has(sessionId)
}

function hasTasksOrNotes(session) {
  return (session.tasks_done && session.tasks_done.trim()) || (session.notes && session.notes.trim())
}
</script>

<template>
  <div class="p-6 max-w-[1400px] mx-auto space-y-5">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <h1 class="page-title">Sessions</h1>

      <div class="flex items-center gap-3 flex-wrap">
        <!-- View Mode Toggle -->
        <div class="glass-inset p-1 inline-flex gap-0.5">
          <button
            v-for="mode in [
              { id: 'calendar', label: 'Calendar' },
              { id: 'day', label: 'Day' },
              { id: '3days', label: '3 Days' },
              { id: 'week', label: 'Week' },
            ]"
            :key="mode.id"
            class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150"
            :class="viewMode === mode.id
              ? 'bg-accent text-white shadow-sm shadow-accent/30'
              : 'text-fg-muted hover:text-fg'"
            @click="viewMode = mode.id"
          >
            {{ mode.label }}
          </button>
        </div>

        <!-- Navigation -->
        <div class="flex items-center gap-1.5">
          <button @click="previousPeriod" class="icon-btn" title="Previous">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <button
            type="button"
            class="relative inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-fg-subtle/20 bg-white/30 dark:bg-white/5 hover:border-accent/40 hover:bg-accent/5 transition-all min-w-[200px] justify-center text-sm font-semibold text-fg"
            @click="openDatePicker"
            title="Click to pick a date"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14" class="text-accent">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span class="whitespace-nowrap">{{ headerDateLabel }}</span>
            <input
              ref="datePickerRef"
              v-model="selectedDateISO"
              type="date"
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer pointer-events-none"
              aria-label="Pick a date"
            />
          </button>
          <button
            @click="goToToday"
            :disabled="selectedDate.isSame(dayjs(), 'day')"
            class="btn btn-secondary btn-sm !text-accent"
          >Today</button>
          <button @click="nextPeriod" class="icon-btn" title="Next">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>

        <router-link to="/sessions/list" class="btn btn-secondary btn-sm">
          List View
        </router-link>

        <button
          @click="openStartDialog"
          :disabled="activeSession !== null"
          class="btn btn-success"
          :title="activeSession ? 'A session is already active' : 'Start a new session'"
        >
          <svg v-if="!activeSession" viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          {{ activeSession ? 'Session Active' : 'Start Session' }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="glass-card flex flex-col items-center justify-center py-16 px-6 text-muted">
      <div class="spinner mb-4"></div>
      <p>Loading sessions...</p>
    </div>

    <!-- Calendar View -->
    <div v-else-if="viewMode === 'calendar'">
      <SessionCalendarDay
        :date="selectedDate"
        :sessions="calendarSessions"
        @view-details="openDetailsModal"
        @edit="openEditDialog"
        @delete="handleDeleteSession"
        @start-session="openStartDialog"
      />
    </div>

    <!-- Sessions Grid -->
    <div v-else class="grid gap-4" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
      <div
        v-for="date in displayDates"
        :key="date.format('YYYY-MM-DD')"
        class="flex flex-col min-h-[400px] glass-card overflow-hidden"
      >
        <div
          class="p-4 border-b border-fg-subtle/15"
          :class="date.isSame(dayjs(), 'day') ? 'bg-accent/10' : ''"
        >
          <div class="text-xs font-semibold uppercase tracking-wide text-muted">{{ date.format('ddd') }}</div>
          <div class="text-base font-bold text-fg mt-0.5">{{ date.format('MMM D') }}</div>

          <div v-if="sessionsByDate[date.format('YYYY-MM-DD')]" class="mt-2 flex flex-col gap-0.5">
            <span class="text-xs text-subtle">{{ getDayStats(date.format('YYYY-MM-DD')).total }} sessions</span>
            <span class="text-xs text-subtle">{{ formatDuration(getDayStats(date.format('YYYY-MM-DD')).totalActual) }}</span>
          </div>
        </div>

        <div class="flex-1 p-2 overflow-y-auto max-h-[600px] space-y-1.5">
          <div
            v-for="session in sessionsByDate[date.format('YYYY-MM-DD')] || []"
            :key="session.id"
            class="group relative glass-row p-2 border-l-[3px] hover:bg-fg-subtle/10 cursor-pointer"
            :style="{ borderLeftColor: getStatusColor(getSessionStatus(session)) }"
            @click="openDetailsModal(session)"
          >
            <div class="flex items-center justify-between gap-2 relative">
              <div class="flex-1 min-w-0">
                <div v-if="session.project" class="flex items-center gap-1.5 text-sm font-semibold text-fg">
                  <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :style="{ backgroundColor: session.project.color }"></span>
                  <span class="truncate">{{ session.project.name }}</span>
                  <span v-if="session.satisfaction_score && session.satisfaction_score > 0" class="text-[11px] text-subtle font-normal ml-0.5">
                    ({{ session.satisfaction_score }}/100)
                  </span>
                </div>
                <div v-else class="flex items-center gap-1.5 text-sm font-medium italic text-fg-subtle">
                  <span class="truncate">No Project</span>
                  <span v-if="session.satisfaction_score && session.satisfaction_score > 0" class="text-[11px] font-normal ml-0.5">
                    ({{ session.satisfaction_score }}/100)
                  </span>
                </div>
              </div>

              <div class="flex items-center gap-1 text-xs flex-shrink-0">
                <span class="font-semibold text-muted">{{ dayjs(session.start_time).format('HH:mm') }}</span>
                <span class="text-fg-subtle">·</span>
                <span class="flex items-center gap-1">
                  <span v-if="session.end_time" class="font-semibold text-success">{{ formatDuration(getSessionDuration(session)) }}</span>
                  <span v-else class="font-semibold text-success">Active</span>
                  <span class="text-subtle text-[11px]">({{ formatDuration(session.planned_duration) }})</span>
                </span>
              </div>

              <div class="absolute right-0 top-1/2 -translate-y-1/2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm pl-2 rounded">
                <button
                  @click.stop="openEditDialog(session)"
                  class="w-6 h-6 rounded border border-fg-subtle/20 bg-white/80 dark:bg-slate-800/80 text-fg-muted hover:bg-accent hover:text-white hover:border-accent flex items-center justify-center text-xs transition-colors"
                  title="Edit"
                >✎</button>
                <button
                  @click.stop="handleDeleteSession(session)"
                  class="w-6 h-6 rounded border border-fg-subtle/20 bg-white/80 dark:bg-slate-800/80 text-fg-muted hover:bg-danger hover:text-white hover:border-danger flex items-center justify-center text-xs transition-colors"
                  title="Delete"
                >×</button>
              </div>
            </div>

            <div v-if="(session.tags && session.tags.length > 0) || hasTasksOrNotes(session)" class="flex items-center gap-2 mt-1.5 flex-wrap">
              <div v-if="session.tags && session.tags.length > 0" class="flex items-center gap-1 flex-1">
                <span
                  v-for="tag in session.tags.slice(0, 2)"
                  :key="tag.id"
                  class="text-[10px] px-1.5 py-0.5 rounded font-medium"
                  :style="{ backgroundColor: tag.color + '30', color: tag.color }"
                >{{ tag.name }}</span>
                <span v-if="session.tags.length > 2" class="text-[10px] text-fg-subtle">+{{ session.tags.length - 2 }}</span>
              </div>
              <button
                v-if="hasTasksOrNotes(session)"
                @click.stop="toggleSessionExpansion(session.id)"
                class="text-fg-subtle hover:text-fg p-0.5 transition-colors"
                :title="isSessionExpanded(session.id) ? 'Hide details' : 'Show details'"
              >
                <span
                  class="inline-block text-[10px] transition-transform"
                  :class="{ 'rotate-180': isSessionExpanded(session.id) }"
                >▼</span>
              </button>
            </div>

            <div v-if="isSessionExpanded(session.id)" class="mt-2 p-2 rounded glass-inset space-y-1.5">
              <div v-if="session.tasks_done && session.tasks_done.trim()" class="flex gap-1.5 text-[11px] leading-snug">
                <span class="text-success flex-shrink-0">✓</span>
                <span class="text-muted whitespace-pre-wrap break-words">{{ session.tasks_done }}</span>
              </div>
              <div v-if="session.notes && session.notes.trim()" class="flex gap-1.5 text-[11px] leading-snug">
                <span class="text-info flex-shrink-0">📝</span>
                <span class="text-muted whitespace-pre-wrap break-words">{{ session.notes }}</span>
              </div>
            </div>
          </div>

          <div v-if="!sessionsByDate[date.format('YYYY-MM-DD')]" class="flex flex-col items-center justify-center py-12 px-4 text-fg-subtle">
            <span class="text-2xl mb-2">📭</span>
            <span class="text-sm">No sessions</span>
          </div>
        </div>
      </div>
    </div>

    <StartSessionDialog
      v-if="showStartDialog"
      @close="showStartDialog = false"
      @started="handleSessionStarted"
    />

    <EditSessionDialog
      v-if="showEditDialog"
      :session="sessionToEdit"
      @close="showEditDialog = false"
      @saved="handleSessionUpdated"
    />

    <SessionDetailsModal
      v-if="showDetailsModal"
      :session="sessionToView"
      @close="showDetailsModal = false"
      @edit="handleDetailsEdit"
      @delete="handleDetailsDelete"
      @update-times="handleUpdateTimes"
    />
  </div>
</template>
