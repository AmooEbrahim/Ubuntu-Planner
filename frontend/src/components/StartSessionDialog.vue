<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import TagMultiSelect from './TagMultiSelect.vue'
import dayjs from 'dayjs'

const emit = defineEmits(['close', 'started'])

const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const selectedProjectId = ref(null)
const duration = ref(60)
const selectedTags = ref([])
const searchQuery = ref('')
const loading = ref(false)
const projectsLoading = ref(false)
const error = ref('')

onMounted(async () => {
  if (projectStore.projects.length === 0) {
    projectsLoading.value = true
    await projectStore.fetchProjects()
    projectsLoading.value = false
  }
})

const filteredProjects = computed(() => {
  if (!searchQuery.value) {
    // Show top 5 projects when search is empty
    return projectStore.activeProjects.slice(0, 5)
  }
  const query = searchQuery.value.toLowerCase()
  return projectStore.activeProjects.filter(p =>
    p.name.toLowerCase().includes(query)
  ).slice(0, 10)
})

const selectedProject = computed(() => {
  return projectStore.projects.find(p => p.id === selectedProjectId.value)
})

const endTime = computed(() => {
  if (!duration.value) return null
  return dayjs().add(duration.value, 'minute').format('HH:mm')
})

function selectProject(projectId) {
  selectedProjectId.value = projectId
  const project = projectStore.projects.find(p => p.id === projectId)
  if (project?.default_duration) {
    duration.value = project.default_duration
  }
  searchQuery.value = ''
}

async function handleStart() {
  const sessionData = {
    project_id: selectedProjectId.value,
    planned_duration: duration.value,
    tag_ids: selectedTags.value,
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
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Start Session</h2>
        <button @click="emit('close')" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Project Selection -->
        <div class="form-group">
          <label>Project (optional)</label>
          <div class="project-select">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search projects or leave empty for no project..."
              class="search-input"
              :disabled="projectsLoading"
            />

            <!-- Loading State -->
            <div v-if="projectsLoading" class="dropdown">
              <div class="loading-state">Loading projects...</div>
            </div>

            <!-- Search Results / Initial Projects -->
            <div v-else-if="searchQuery || !selectedProject" class="dropdown">
              <div v-if="filteredProjects.length === 0" class="no-results">
                No projects found
              </div>
              <button
                v-else
                v-for="project in filteredProjects"
                :key="project.id"
                type="button"
                @click="selectProject(project.id)"
                class="project-option"
              >
                <span class="color-indicator" :style="{ backgroundColor: project.color }"></span>
                <span>{{ project.name }}</span>
                <span class="duration-hint">{{ project.default_duration }}m</span>
              </button>
            </div>
          </div>

          <!-- Selected Project Display -->
          <div v-if="selectedProject" class="selected-project">
            <span class="color-indicator" :style="{ backgroundColor: selectedProject.color }"></span>
            <span>{{ selectedProject.name }}</span>
            <button type="button" @click="selectedProjectId = null" class="clear-btn">×</button>
          </div>
        </div>

        <!-- Duration -->
        <div class="form-group">
          <label>Duration</label>
          <div class="duration-controls">
            <input
              type="number"
              v-model.number="duration"
              min="5"
              step="5"
              class="duration-input"
            />
            <span class="duration-label">minutes</span>

            <!-- Quick Buttons -->
            <div class="quick-buttons">
              <button type="button" @click="duration = 30" class="quick-btn">30m</button>
              <button type="button" @click="duration = 60" class="quick-btn">1h</button>
              <button type="button" @click="duration = 90" class="quick-btn">1.5h</button>
              <button type="button" @click="duration = 120" class="quick-btn">2h</button>
            </div>
          </div>

          <!-- End Time Display -->
          <div v-if="endTime" class="end-time-hint">
            Session will end at approximately <strong>{{ endTime }}</strong>
          </div>
        </div>

        <!-- Tags -->
        <div class="form-group">
          <label>Tags (optional)</label>
          <TagMultiSelect v-model="selectedTags" />
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-footer">
        <button @click="emit('close')" class="btn btn-secondary">Cancel</button>
        <button
          @click="handleStart"
          :disabled="!duration || loading"
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
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #374151;
}

.project-select {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #10b981;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
}

.project-option {
  width: 100%;
  padding: 0.625rem;
  border: none;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-align: left;
  transition: background-color 0.2s;
}

.project-option:hover {
  background-color: #f3f4f6;
}

.color-indicator {
  width: 4px;
  height: 24px;
  border-radius: 2px;
  flex-shrink: 0;
}

.duration-hint {
  margin-left: auto;
  color: #9ca3af;
  font-size: 0.85rem;
}

.loading-state,
.no-results {
  padding: 1rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.9rem;
}

.search-input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.selected-project {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #f3f4f6;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.clear-btn {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  line-height: 1;
  padding: 0 0.25rem;
}

.clear-btn:hover {
  color: #374151;
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
  padding: 0.375rem 0.75rem;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.quick-btn:hover {
  background-color: #e5e7eb;
  border-color: #10b981;
}

.end-time-hint {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #ecfdf5;
  border: 1px solid #10b981;
  border-radius: 4px;
  color: #047857;
  font-size: 0.875rem;
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
