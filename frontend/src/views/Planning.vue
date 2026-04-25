<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanningStore } from '@/stores/planning'
import { useProjectStore } from '@/stores/projects'
import dayjs from 'dayjs'
import CalendarDay from '@/components/CalendarDay.vue'
import PlanningForm from '@/components/PlanningForm.vue'

const planningStore = usePlanningStore()
const projectStore = useProjectStore()

const currentDate = ref(dayjs())
const showForm = ref(false)
const editingPlanning = ref(null)
const defaultStartTime = ref(null)
const loading = ref(false)
const error = ref('')
const dragSaving = ref(false)
const datePickerRef = ref(null)

const currentDateISO = computed({
  get: () => currentDate.value.format('YYYY-MM-DD'),
  set: (val) => {
    if (!val) return
    currentDate.value = dayjs(val)
    loadPlanning()
  },
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

const displayDate = computed(() => currentDate.value.format('MMMM D, YYYY'))
const isToday = computed(() => currentDate.value.isSame(dayjs(), 'day'))
const dayName = computed(() => currentDate.value.format('dddd'))

const planning = computed(() => planningStore.planningByDate(currentDate.value))

const totalDuration = computed(() => {
  const minutes = planning.value.reduce((sum, p) => {
    const start = dayjs.utc(p.scheduled_start).local()
    const end = dayjs.utc(p.scheduled_end).local()
    return sum + end.diff(start, 'minute')
  }, 0)
  if (minutes < 60) return `${minutes}m`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m > 0 ? `${h}h ${m}m` : `${h}h`
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadPlanning(), loadProjects()])
  } catch (err) {
    error.value = 'Failed to load data. Please try again.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function loadPlanning() {
  await planningStore.fetchPlanningForDate(currentDate.value)
}

async function loadProjects() {
  if (projectStore.projects.length === 0) {
    await projectStore.fetchProjects()
  }
}

function previousDay() {
  currentDate.value = currentDate.value.subtract(1, 'day')
  loadPlanning()
}

function nextDay() {
  currentDate.value = currentDate.value.add(1, 'day')
  loadPlanning()
}

function goToToday() {
  currentDate.value = dayjs()
  loadPlanning()
}

function openCreateForm(timeSlot = null) {
  editingPlanning.value = null
  defaultStartTime.value = timeSlot
  showForm.value = true
}

function openEditForm(item) {
  editingPlanning.value = item
  defaultStartTime.value = null
  showForm.value = true
}

async function handleDelete(item) {
  if (confirm(`Delete planning for "${item.project?.name}"?`)) {
    try {
      await planningStore.deletePlanning(item.id)
    } catch (err) {
      alert('Failed to delete planning: ' + (err.response?.data?.detail || err.message))
    }
  }
}

async function handleDragEnd(data) {
  dragSaving.value = true
  try {
    await planningStore.updatePlanning(data.id, {
      scheduled_start: data.scheduled_start,
      scheduled_end: data.scheduled_end,
    })
  } catch (err) {
    alert('Failed to move planning: ' + (err.response?.data?.detail || err.message))
  } finally {
    dragSaving.value = false
  }
}

function handleFormSaved() {
  showForm.value = false
  loadPlanning()
}

function closeForm() {
  showForm.value = false
  editingPlanning.value = null
  defaultStartTime.value = null
}
</script>

<template>
  <div class="planning-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Planning Calendar</h1>
        <p class="page-subtitle">Schedule and manage your work</p>
      </div>
      <button @click="openCreateForm()" class="btn-primary">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Add Planning
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

    <div class="calendar-controls">
      <div class="date-navigation">
        <button @click="previousDay" class="nav-btn" title="Previous Day">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <button @click="goToToday" class="today-btn" :disabled="isToday">Today</button>
        <button @click="nextDay" class="nav-btn" title="Next Day">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      <button
        type="button"
        class="current-date date-pill"
        @click="openDatePicker"
        title="Click to pick a date"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" aria-hidden="true">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <span class="date-day">{{ dayName }}</span>
        <span class="date-full">{{ displayDate }}</span>
        <span v-if="isToday" class="today-badge">Today</span>
        <input
          ref="datePickerRef"
          v-model="currentDateISO"
          type="date"
          class="date-pill-native"
          aria-label="Pick a date"
        />
      </button>

      <div class="stats">
        <div class="stat-item">
          <span class="stat-count">{{ planning.length }}</span>
          <span class="stat-label">plans</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-count">{{ totalDuration }}</span>
          <span class="stat-label">total</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading planning...</p>
    </div>

    <div v-else-if="dragSaving" class="drag-save-indicator">
      <div class="mini-spinner"></div>
      <span>Moving plan...</span>
    </div>

    <div v-else class="calendar-wrapper">
      <CalendarDay
        :date="currentDate"
        :planning="planning"
        @click-slot="openCreateForm"
        @edit="openEditForm"
        @delete="handleDelete"
        @drag-end="handleDragEnd"
      />
    </div>

    <PlanningForm
      v-if="showForm"
      :planning="editingPlanning"
      :default-date="currentDate"
      :default-start-time="defaultStartTime"
      @close="closeForm"
      @saved="handleFormSaved"
    />
  </div>
</template>

<style scoped>
.planning-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
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

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

.icon {
  width: 18px;
  height: 18px;
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

.retry-btn:hover {
  background: #fef2f2;
}

.calendar-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem 1.25rem;
  background: white;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  gap: 1rem;
  flex-wrap: wrap;
}

.date-navigation {
  display: flex;
  gap: 0.375rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
  transition: all var(--transition);
}

.nav-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #334155;
}

.today-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  color: #6366f1;
  transition: all var(--transition);
}

.today-btn:hover:not(:disabled) {
  background: #eef2ff;
  border-color: #6366f1;
}

.today-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.current-date {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.date-pill {
  position: relative;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  padding: 0.5rem 0.875rem;
  cursor: pointer;
  font: inherit;
  color: inherit;
  transition: all var(--transition);
}

.date-pill:hover {
  border-color: #6366f1;
  background: #f5f3ff;
}

.date-pill > svg {
  color: #6366f1;
  margin-right: 0.25rem;
  flex-shrink: 0;
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

.date-day {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6366f1;
}

.date-full {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
}

.today-badge {
  background: #ecfdf5;
  color: #059669;
  padding: 0.2rem 0.625rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stats {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.125rem;
}

.stat-count {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
}

.stat-label {
  font-size: 0.7rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: #e2e8f0;
}

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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.drag-save-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 10px;
  color: #6366f1;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #c7d2fe;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.calendar-wrapper {
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .planning-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .calendar-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .date-navigation {
    justify-content: center;
  }

  .current-date {
    justify-content: center;
  }

  .stats {
    justify-content: center;
  }
}
</style>
