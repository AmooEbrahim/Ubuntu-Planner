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
  <div class="p-6 max-w-[1400px] mx-auto space-y-5">
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h1 class="page-title">Planning Calendar</h1>
        <p class="page-subtitle">Schedule and manage your work</p>
      </div>
      <button @click="openCreateForm()" class="btn btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Add Planning
      </button>
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

    <div class="glass-card flex justify-between items-center p-4 gap-4 flex-wrap">
      <div class="flex gap-1.5">
        <button @click="previousDay" class="icon-btn" title="Previous Day">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <button
          @click="goToToday"
          :disabled="isToday"
          class="btn btn-secondary btn-sm !text-accent"
        >Today</button>
        <button @click="nextDay" class="icon-btn" title="Next Day">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      <button
        type="button"
        @click="openDatePicker"
        title="Click to pick a date"
        class="relative inline-flex items-center gap-2.5 px-3.5 py-2 rounded-xl border border-fg-subtle/20 bg-white/30 dark:bg-white/5 hover:border-accent/40 hover:bg-accent/5 transition-all"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14" class="text-accent" aria-hidden="true">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <span class="text-sm font-semibold text-accent">{{ dayName }}</span>
        <span class="text-base font-bold text-fg">{{ displayDate }}</span>
        <span v-if="isToday" class="badge badge-success">Today</span>
        <input
          ref="datePickerRef"
          v-model="currentDateISO"
          type="date"
          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer pointer-events-none"
          aria-label="Pick a date"
        />
      </button>

      <div class="flex items-center gap-3">
        <div class="flex flex-col items-center">
          <span class="text-base font-bold text-fg">{{ planning.length }}</span>
          <span class="text-[10px] text-subtle uppercase tracking-wide">plans</span>
        </div>
        <div class="divider-v h-7"></div>
        <div class="flex flex-col items-center">
          <span class="text-base font-bold text-fg">{{ totalDuration }}</span>
          <span class="text-[10px] text-subtle uppercase tracking-wide">total</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="glass-card flex flex-col items-center justify-center py-16 px-6 text-muted">
      <div class="spinner mb-4"></div>
      <p>Loading planning...</p>
    </div>

    <div v-else-if="dragSaving" class="glass-card border border-accent/30 bg-accent/5 flex items-center justify-center gap-2 p-3 text-accent text-sm font-medium">
      <div class="w-4 h-4 border-2 border-accent/30 border-t-accent rounded-full animate-spin"></div>
      <span>Moving plan...</span>
    </div>

    <div v-else>
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
