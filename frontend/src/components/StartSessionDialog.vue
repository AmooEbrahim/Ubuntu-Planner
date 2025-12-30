<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import { usePlanningStore } from '@/stores/planning'
import dayjs from 'dayjs'

const emit = defineEmits(['close', 'started'])

const sessionStore = useSessionStore()
const projectStore = useProjectStore()
const planningStore = usePlanningStore()

const selectedProject = ref(null)
const selectedPlanning = ref(null)
const duration = ref(60)
const mode = ref('project') // 'project' or 'planning'
const loading = ref(false)
const error = ref('')

const todayPlanning = computed(() => planningStore.todayPlanning)
const pinnedProjects = computed(() => projectStore.pinnedProjects)
const activeProjects = computed(() => projectStore.activeProjects)

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      projectStore.projects.length === 0 ? projectStore.fetchProjects() : Promise.resolve(),
      planningStore.fetchTodayPlanning(),
    ])
  } catch (err) {
    error.value = 'Failed to load data'
  } finally {
    loading.value = false
  }
})

function selectProject(project) {
  selectedProject.value = project
  selectedPlanning.value = null
  duration.value = project.default_duration || 60
  mode.value = 'project'
}

function selectPlanning(planning) {
  selectedPlanning.value = planning
  selectedProject.value = planning.project
  const start = dayjs(planning.scheduled_start)
  const end = dayjs(planning.scheduled_end)
  duration.value = Math.floor(end.diff(start, 'minute'))
  mode.value = 'planning'
}

async function handleStart() {
  if (!selectedProject.value && !selectedPlanning.value) {
    error.value = 'Please select a project or planning'
    return
  }

  const sessionData = {
    project_id: selectedProject.value?.id || null,
    planned_duration: duration.value,
    planning_id: mode.value === 'planning' ? selectedPlanning.value?.id : null,
    tag_ids: [],
  }

  try {
    loading.value = true
    error.value = ''
    await sessionStore.startSession(sessionData)
    emit('started')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Error starting session'
  } finally {
    loading.value = false
  }
}

function formatTime(datetime) {
  return dayjs(datetime).format('HH:mm')
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content large">
      <div class="modal-header">
        <h2>Start Session</h2>
        <button @click="emit('close')" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading...</p>
        </div>

        <div v-else>
          <!-- Today's Planning -->
          <div v-if="todayPlanning.length > 0" class="section">
            <h3 class="section-title">Today's Planning</h3>
            <div class="planning-grid">
              <button
                v-for="plan in todayPlanning"
                :key="plan.id"
                @click="selectPlanning(plan)"
                :class="['planning-card', { selected: selectedPlanning?.id === plan.id }]"
                type="button"
              >
                <div class="planning-time">{{ formatTime(plan.scheduled_start) }}</div>
                <div class="planning-project" :style="{ color: plan.project.color }">
                  {{ plan.project.name }}
                </div>
                <div v-if="plan.description" class="planning-description">
                  {{ plan.description }}
                </div>
                <div class="planning-duration">{{ Math.floor((new Date(plan.scheduled_end) - new Date(plan.scheduled_start)) / 1000 / 60) }} min</div>
              </button>
            </div>
          </div>

          <!-- Pinned Projects -->
          <div v-if="pinnedProjects.length > 0" class="section">
            <h3 class="section-title">Pinned Projects</h3>
            <div class="projects-grid">
              <button
                v-for="project in pinnedProjects"
                :key="project.id"
                @click="selectProject(project)"
                :class="['project-card', { selected: selectedProject?.id === project.id && mode === 'project' }]"
                type="button"
              >
                <div class="color-indicator" :style="{ backgroundColor: project.color }"></div>
                <div class="project-name">{{ project.name }}</div>
                <div class="project-duration">{{ project.default_duration }} min</div>
              </button>
            </div>
          </div>

          <!-- All Projects -->
          <div v-if="activeProjects.length > 0" class="section">
            <h3 class="section-title">All Projects</h3>
            <div class="projects-list">
              <button
                v-for="project in activeProjects"
                :key="project.id"
                @click="selectProject(project)"
                :class="['project-list-item', { selected: selectedProject?.id === project.id && mode === 'project' }]"
                type="button"
              >
                <div class="color-indicator" :style="{ backgroundColor: project.color }"></div>
                <span>{{ project.name }}</span>
              </button>
            </div>
          </div>

          <!-- Duration Setting -->
          <div v-if="selectedProject || selectedPlanning" class="section">
            <h3 class="section-title">Duration</h3>
            <div class="duration-controls">
              <input
                type="number"
                v-model.number="duration"
                min="5"
                step="5"
                class="duration-input"
              />
              <span class="duration-label">minutes</span>
              <div class="quick-buttons">
                <button type="button" @click="duration = 30" class="quick-btn">30m</button>
                <button type="button" @click="duration = 60" class="quick-btn">1h</button>
                <button type="button" @click="duration = 90" class="quick-btn">1.5h</button>
                <button type="button" @click="duration = 120" class="quick-btn">2h</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-footer">
        <button @click="emit('close')" class="btn btn-secondary">Cancel</button>
        <button
          @click="handleStart"
          :disabled="(!selectedProject && !selectedPlanning) || loading"
          class="btn btn-primary"
        >
          {{ loading ? 'Starting...' : 'Start Session' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-content.large {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6b7280;
  line-height: 1;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.error-message {
  padding: 0.75rem;
  margin-bottom: 1rem;
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  border-radius: 4px;
  font-size: 0.9rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
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

.section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #374151;
}

.planning-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.planning-card {
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  background: white;
  transition: all 0.2s;
}

.planning-card:hover {
  border-color: #10b981;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.planning-card.selected {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.planning-time {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.planning-project {
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.planning-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.planning-duration {
  font-size: 0.75rem;
  color: #9ca3af;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.75rem;
}

.project-card {
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  background: white;
  transition: all 0.2s;
  position: relative;
}

.project-card:hover {
  border-color: #10b981;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.project-card.selected {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.color-indicator {
  width: 4px;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  border-radius: 6px 0 0 6px;
}

.project-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
  padding-left: 0.5rem;
}

.project-duration {
  font-size: 0.75rem;
  color: #9ca3af;
  padding-left: 0.5rem;
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
}

.project-list-item {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
  background: white;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
}

.project-list-item:hover {
  border-color: #10b981;
  background-color: #f9fafb;
}

.project-list-item.selected {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.project-list-item .color-indicator {
  position: static;
  width: 4px;
  height: 24px;
  border-radius: 2px;
  flex-shrink: 0;
}

.duration-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.duration-input {
  width: 100px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 1rem;
}

.duration-label {
  color: #6b7280;
}

.quick-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 0.5rem 0.75rem;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.quick-btn:hover {
  background-color: #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background-color: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #d1d5db;
}

.btn-primary {
  background-color: #10b981;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #059669;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
