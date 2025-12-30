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

const displayDate = computed(() => currentDate.value.format('MMMM D, YYYY'))
const isToday = computed(() => currentDate.value.isSame(dayjs(), 'day'))

const planning = computed(() => planningStore.planningByDate(currentDate.value))

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
  try {
    await planningStore.fetchPlanningForDate(currentDate.value)
  } catch (err) {
    console.error('Error loading planning:', err)
    throw err
  }
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

function openEditForm(planning) {
  editingPlanning.value = planning
  defaultStartTime.value = null
  showForm.value = true
}

async function handleDelete(planning) {
  if (confirm(`Delete planning for "${planning.project.name}"?`)) {
    try {
      await planningStore.deletePlanning(planning.id)
    } catch (err) {
      alert('Failed to delete planning: ' + (err.response?.data?.detail || err.message))
    }
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
      <button @click="openCreateForm()" class="btn-primary">+ Add Planning</button>
    </div>

    <div v-if="error" class="error-banner">
      {{ error }}
      <button @click="loadData" class="retry-btn">Retry</button>
    </div>

    <div class="calendar-controls">
      <div class="date-navigation">
        <button @click="previousDay" class="nav-btn" title="Previous Day">←</button>
        <button @click="goToToday" class="today-btn" :disabled="isToday">Today</button>
        <button @click="nextDay" class="nav-btn" title="Next Day">→</button>
      </div>
      <div class="current-date">
        {{ displayDate }}
        <span v-if="isToday" class="today-badge">Today</span>
      </div>
      <div class="stats">
        <span class="stat-item">{{ planning.length }} planning(s)</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading planning...</p>
    </div>

    <div v-else class="calendar-wrapper">
      <CalendarDay
        :date="currentDate"
        :planning="planning"
        @click-slot="openCreateForm"
        @edit="openEditForm"
        @delete="handleDelete"
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

.calendar-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.date-navigation {
  display: flex;
  gap: 0.5rem;
}

.nav-btn,
.today-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.today-btn {
  background-color: #10b981;
  color: white;
  border-color: #10b981;
}

.today-btn:hover:not(:disabled) {
  background-color: #059669;
}

.today-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.current-date {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.today-badge {
  background-color: #10b981;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.stats {
  display: flex;
  gap: 1rem;
}

.stat-item {
  font-size: 0.9rem;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 0.5rem 1rem;
  border-radius: 4px;
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

.calendar-wrapper {
  margin-bottom: 2rem;
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

.btn-primary:hover {
  background-color: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
}
</style>
