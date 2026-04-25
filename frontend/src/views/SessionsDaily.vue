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
const expandedSessions = ref(new Set()) // Track which sessions are expanded

const selectedDate = ref(dayjs())
const viewMode = ref('calendar') // 'calendar', 'day', '3days', or 'week'
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
      sessionStore.fetchRecentSessions(100), // Fetch more sessions for daily view
      projectStore.projects.length === 0 ? projectStore.fetchProjects() : Promise.resolve()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

// Get sessions grouped by date
const sessionsByDate = computed(() => {
  const grouped = {}
  const sessions = sessionStore.recentSessions || []

  sessions.forEach(session => {
    const dateKey = dayjs(session.start_time).format('YYYY-MM-DD')
    if (!grouped[dateKey]) {
      grouped[dateKey] = []
    }
    grouped[dateKey].push(session)
  })

  // Sort sessions within each day by start time
  Object.keys(grouped).forEach(dateKey => {
    grouped[dateKey].sort((a, b) =>
      dayjs(a.start_time).valueOf() - dayjs(b.start_time).valueOf()
    )
  })

  return grouped
})

// Get sessions for calendar view (single day)
const calendarSessions = computed(() => {
  const dateKey = selectedDate.value.format('YYYY-MM-DD')
  return sessionsByDate.value[dateKey] || []
})

// Get dates to display based on view mode
const displayDates = computed(() => {
  if (viewMode.value === 'calendar' || viewMode.value === 'day') {
    return [selectedDate.value]
  } else if (viewMode.value === '3days') {
    // Show 3 days centered on selected date
    return [
      selectedDate.value.subtract(1, 'day'),
      selectedDate.value,
      selectedDate.value.add(1, 'day')
    ]
  } else {
    // Show week view (7 days)
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

function goToToday() {
  selectedDate.value = dayjs()
}

function openStartDialog() {
  showStartDialog.value = true
}

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
    // Update session with the new times
    await sessionStore.updateSession(data.sessionId, {
      start_time: data.start_time,
      end_time: data.end_time
    })
    // Refresh the data to show updated times
    await loadData()
    // Update the modal view with fresh data
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
  if (session.actual_duration) {
    return session.actual_duration
  }
  if (session.end_time) {
    const start = dayjs(session.start_time)
    const end = dayjs(session.end_time)
    return Math.floor(end.diff(start, 'minute'))
  }
  return session.planned_duration
}

function getSessionStatus(session) {
  if (!session.end_time) {
    return 'active'
  }
  const duration = getSessionDuration(session)
  if (duration > session.planned_duration) {
    return 'overtime'
  }
  return 'completed'
}

function getStatusColor(status) {
  switch (status) {
    case 'active': return '#10b981'
    case 'overtime': return '#f59e0b'
    case 'completed': return '#6b7280'
    default: return '#6b7280'
  }
}

function getDayStats(dateKey) {
  const sessions = sessionsByDate.value[dateKey] || []
  const totalPlanned = sessions.reduce((sum, s) => sum + s.planned_duration, 0)
  const totalActual = sessions.reduce((sum, s) => sum + getSessionDuration(s), 0)
  const completed = sessions.filter(s => s.end_time).length

  return {
    total: sessions.length,
    completed,
    active: sessions.length - completed,
    totalPlanned,
    totalActual
  }
}

function getSatisfactionClass(score) {
  if (score >= 80) return 'satisfaction-high'
  if (score >= 60) return 'satisfaction-medium'
  return 'satisfaction-low'
}

function toggleSessionExpansion(sessionId) {
  if (expandedSessions.value.has(sessionId)) {
    expandedSessions.value.delete(sessionId)
  } else {
    expandedSessions.value.add(sessionId)
  }
  // Force reactivity update
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
  <div class="sessions-daily-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Sessions</h1>

      <div class="header-actions">
        <!-- View Mode Toggle -->
        <div class="view-toggle">
          <button
            :class="['toggle-btn', { active: viewMode === 'calendar' }]"
            @click="viewMode = 'calendar'"
          >
            📅 Calendar
          </button>
          <button
            :class="['toggle-btn', { active: viewMode === 'day' }]"
            @click="viewMode = 'day'"
          >
            Day
          </button>
          <button
            :class="['toggle-btn', { active: viewMode === '3days' }]"
            @click="viewMode = '3days'"
          >
            3 Days
          </button>
          <button
            :class="['toggle-btn', { active: viewMode === 'week' }]"
            @click="viewMode = 'week'"
          >
            Week
          </button>
        </div>

        <!-- Navigation -->
        <div class="date-navigation">
          <button @click="previousPeriod" class="nav-btn" title="Previous">‹</button>
          <button
            type="button"
            class="date-pill"
            @click="openDatePicker"
            :title="'Click to pick a date'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span class="date-pill-label">{{ headerDateLabel }}</span>
            <input
              ref="datePickerRef"
              v-model="selectedDateISO"
              type="date"
              class="date-pill-native"
              aria-label="Pick a date"
            />
          </button>
          <button @click="goToToday" class="today-btn" :disabled="selectedDate.isSame(dayjs(), 'day')">Today</button>
          <button @click="nextPeriod" class="nav-btn" title="Next">›</button>
        </div>

        <!-- Link to list view -->
        <router-link to="/sessions/list" class="list-view-link">
          List View
        </router-link>

        <!-- Start Session Button -->
        <button
          @click="openStartDialog"
          :disabled="activeSession !== null"
          class="start-session-btn"
          :title="activeSession ? 'A session is already active' : 'Start a new session'"
        >
          {{ activeSession ? 'Session Active' : '+ Start Session' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading sessions...</p>
    </div>

    <!-- Calendar View -->
    <div v-else-if="viewMode === 'calendar'" class="calendar-view">
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
    <div v-else class="sessions-grid">
      <div
        v-for="date in displayDates"
        :key="date.format('YYYY-MM-DD')"
        class="day-column"
      >
        <!-- Day Header -->
        <div class="day-header" :class="{ today: date.isSame(dayjs(), 'day') }">
          <div class="day-name">{{ date.format('ddd') }}</div>
          <div class="day-date">{{ date.format('MMM D') }}</div>

          <!-- Day Stats -->
          <div v-if="sessionsByDate[date.format('YYYY-MM-DD')]" class="day-stats">
            <span class="stat-item">
              {{ getDayStats(date.format('YYYY-MM-DD')).total }} sessions
            </span>
            <span class="stat-item">
              {{ formatDuration(getDayStats(date.format('YYYY-MM-DD')).totalActual) }}
            </span>
          </div>
        </div>

        <!-- Sessions List -->
        <div class="sessions-list">
          <div
            v-for="session in sessionsByDate[date.format('YYYY-MM-DD')] || []"
            :key="session.id"
            class="session-card"
            :style="{ borderLeftColor: getStatusColor(getSessionStatus(session)) }"
          >
            <!-- Main compact row -->
            <div class="session-main-row">
              <div class="session-left">
                <div class="session-project" v-if="session.project">
                  <span class="project-dot" :style="{ backgroundColor: session.project.color }"></span>
                  <span class="project-name">{{ session.project.name }}</span>
                  <span v-if="session.satisfaction_score && session.satisfaction_score > 0" class="satisfaction-inline">
                    ({{ session.satisfaction_score }}/100)
                  </span>
                </div>
                <div v-else class="session-project no-project">
                  <span class="project-name">No Project</span>
                  <span v-if="session.satisfaction_score && session.satisfaction_score > 0" class="satisfaction-inline">
                    ({{ session.satisfaction_score }}/100)
                  </span>
                </div>
              </div>

              <div class="session-right">
                <div class="session-time-info">
                  <span class="start-time">{{ dayjs(session.start_time).format('HH:mm') }}</span>
                  <span class="separator">·</span>
                  <span class="duration-info">
                    <span v-if="session.end_time" class="actual-duration">
                      {{ formatDuration(getSessionDuration(session)) }}
                    </span>
                    <span v-else class="active-status">Active</span>
                    <span class="planned-duration">({{ formatDuration(session.planned_duration) }})</span>
                  </span>
                </div>
              </div>

              <!-- Actions - show on hover -->
              <div class="session-actions-compact">
                <button @click.stop="openEditDialog(session)" class="action-btn-compact edit" title="Edit">✎</button>
                <button @click.stop="handleDeleteSession(session)" class="action-btn-compact delete" title="Delete">×</button>
              </div>
            </div>

            <!-- Second row - optional metadata -->
            <div v-if="(session.tags && session.tags.length > 0) || hasTasksOrNotes(session)" class="session-meta-row">
              <!-- Tags -->
              <div v-if="session.tags && session.tags.length > 0" class="session-tags-compact">
                <span
                  v-for="tag in session.tags.slice(0, 2)"
                  :key="tag.id"
                  class="tag-chip-compact"
                  :style="{ backgroundColor: tag.color + '30', color: tag.color }"
                >
                  {{ tag.name }}
                </span>
                <span v-if="session.tags.length > 2" class="more-tags-compact">
                  +{{ session.tags.length - 2 }}
                </span>
              </div>

              <!-- Expand toggle for tasks/notes -->
              <button
                v-if="hasTasksOrNotes(session)"
                @click.stop="toggleSessionExpansion(session.id)"
                class="expand-toggle-compact"
                :title="isSessionExpanded(session.id) ? 'Hide details' : 'Show details'"
              >
                <span class="toggle-icon-compact" :class="{ expanded: isSessionExpanded(session.id) }">▼</span>
              </button>
            </div>

            <!-- Expandable details -->
            <div v-if="isSessionExpanded(session.id)" class="session-details-compact">
              <div v-if="session.tasks_done && session.tasks_done.trim()" class="detail-item">
                <span class="detail-icon">✓</span>
                <span class="detail-text">{{ session.tasks_done }}</span>
              </div>
              <div v-if="session.notes && session.notes.trim()" class="detail-item">
                <span class="detail-icon">📝</span>
                <span class="detail-text">{{ session.notes }}</span>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="!sessionsByDate[date.format('YYYY-MM-DD')]" class="empty-day">
            <span class="empty-icon">📭</span>
            <span class="empty-text">No sessions</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Start Session Dialog -->
    <StartSessionDialog
      v-if="showStartDialog"
      @close="showStartDialog = false"
      @started="handleSessionStarted"
    />

    <!-- Edit Session Dialog -->
    <EditSessionDialog
      v-if="showEditDialog"
      :session="sessionToEdit"
      @close="showEditDialog = false"
      @saved="handleSessionUpdated"
    />

    <!-- Session Details Modal -->
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

<style scoped>
.sessions-daily-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
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
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-toggle {
  display: flex;
  background-color: #f3f4f6;
  border-radius: 6px;
  padding: 0.25rem;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.2s;
}

.toggle-btn.active {
  background-color: white;
  color: #10b981;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.date-navigation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-btn,
.today-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  color: #374151;
  transition: all 0.2s;
}

.nav-btn {
  font-size: 1.25rem;
}

.nav-btn:hover,
.today-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #10b981;
}

.today-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.date-pill {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  color: #1f2937;
  transition: all 0.2s;
  min-width: 200px;
  justify-content: center;
}

.date-pill:hover {
  border-color: #10b981;
  color: #059669;
  background: #f0fdf4;
}

.date-pill svg {
  color: #10b981;
  flex-shrink: 0;
}

.date-pill-label {
  white-space: nowrap;
}

.date-pill-native {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  border: none;
  padding: 0;
  font: inherit;
  pointer-events: none;
}

.list-view-link {
  padding: 0.5rem 1rem;
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
}

.list-view-link:hover {
  background-color: #e5e7eb;
  border-color: #10b981;
}

.start-session-btn {
  padding: 0.5rem 1rem;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.start-session-btn:hover:not(:disabled) {
  background-color: #059669;
}

.start-session-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
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
  to { transform: rotate(360deg); }
}

.calendar-view {
  margin-bottom: 2rem;
}

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.day-column {
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.day-header {
  background-color: #f9fafb;
  padding: 1rem;
  border-radius: 8px 8px 0 0;
  border: 1px solid #e5e7eb;
  border-bottom: none;
}

.day-header.today {
  background-color: #ecfdf5;
  border-color: #10b981;
}

.day-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
}

.day-date {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1f2937;
  margin-top: 0.25rem;
}

.day-stats {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-item {
  font-size: 0.75rem;
  color: #6b7280;
}

.sessions-list {
  flex: 1;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0 0 8px 8px;
  padding: 0.5rem;
  overflow-y: auto;
  max-height: 600px;
}

/* Compact Session Card */
.session-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-left: 3px solid;
  border-radius: 4px;
  padding: 0.5rem;
  margin-bottom: 0.375rem;
  transition: all 0.2s;
  position: relative;
}

.session-card:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border-left-width: 4px;
}

/* Main Row - Project and Time */
.session-main-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  position: relative;
}

.session-left {
  flex: 1;
  min-width: 0;
}

.session-project {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
}

.session-project.no-project {
  color: #9ca3af;
  font-style: italic;
  font-weight: 500;
}

.project-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.project-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.satisfaction-inline {
  font-size: 0.7rem;
  color: #9ca3af;
  font-weight: 500;
  margin-left: 0.25rem;
}

.session-right {
  flex-shrink: 0;
}

.session-time-info {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
}

.start-time {
  font-weight: 600;
  color: #374151;
}

.separator {
  color: #d1d5db;
}

.duration-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6b7280;
}

.actual-duration {
  font-weight: 600;
  color: #059669;
}

.active-status {
  font-weight: 600;
  color: #10b981;
}

.planned-duration {
  color: #9ca3af;
  font-size: 0.7rem;
}

/* Compact Actions - Show on Hover */
.session-actions-compact {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
  background: white;
  padding-left: 0.5rem;
}

.session-card:hover .session-actions-compact {
  opacity: 1;
}

.action-btn-compact {
  width: 24px;
  height: 24px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.action-btn-compact.edit:hover {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.action-btn-compact.delete:hover {
  background-color: #ef4444;
  color: white;
  border-color: #ef4444;
}

/* Meta Row - Tags, Satisfaction, Expand */
.session-meta-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.375rem;
  flex-wrap: wrap;
}

.session-tags-compact {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}

.tag-chip-compact {
  font-size: 0.65rem;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  font-weight: 500;
}

.more-tags-compact {
  font-size: 0.65rem;
  color: #9ca3af;
}

.expand-toggle-compact {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.125rem 0.25rem;
  color: #9ca3af;
  transition: color 0.2s;
}

.expand-toggle-compact:hover {
  color: #374151;
}

.toggle-icon-compact {
  font-size: 0.625rem;
  transition: transform 0.2s;
  display: inline-block;
}

.toggle-icon-compact.expanded {
  transform: rotate(180deg);
}

/* Compact Details */
.session-details-compact {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #f9fafb;
  border-radius: 3px;
  border: 1px solid #e5e7eb;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.detail-item {
  display: flex;
  gap: 0.375rem;
  margin-bottom: 0.375rem;
  font-size: 0.7rem;
  line-height: 1.4;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-icon {
  flex-shrink: 0;
}

.detail-text {
  color: #6b7280;
  flex: 1;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.empty-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #9ca3af;
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.empty-text {
  font-size: 0.875rem;
}
</style>
