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
const projectSearch = ref('')
const projectDropdownOpen = ref(false)
const projectDropdownRef = ref(null)
const loading = ref(false)
const error = ref('')

const selectedProject = computed(() => {
  return projectStore.projects.find(p => p.id === selectedProjectId.value)
})

const filteredProjects = computed(() => {
  const q = projectSearch.value.toLowerCase()
  return projectStore.activeProjects
    .filter(p => !q || p.name.toLowerCase().includes(q) || projectStore.getProjectPath(p.id).toLowerCase().includes(q))
    .slice(0, 15)
})

const endTime = computed(() => {
  if (!duration.value) return null
  return dayjs().add(duration.value, 'minute').format('h:mm A')
})

function openProjectDropdown() {
  projectDropdownOpen.value = true
  projectSearch.value = ''
  setTimeout(() => {
    const input = document.querySelector('.project-search-input')
    if (input) input.focus()
  }, 50)
}

function selectProject(projectId) {
  selectedProjectId.value = projectId
  const project = projectStore.projects.find(p => p.id === projectId)
  if (project?.default_duration) {
    duration.value = project.default_duration
  }
  projectDropdownOpen.value = false
  projectSearch.value = ''
}

function clearProject() {
  selectedProjectId.value = null
  projectDropdownOpen.value = false
}

function handleClickOutside(e) {
  if (projectDropdownRef.value && !projectDropdownRef.value.contains(e.target)) {
    projectDropdownOpen.value = false
  }
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

onMounted(async () => {
  if (projectStore.projects.length === 0) {
    await projectStore.fetchProjects()
  }
  document.addEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')" @keydown.escape="emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <div class="header-content">
          <div class="header-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" width="22" height="22">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
          </div>
          <div>
            <h2 class="modal-title">Start Session</h2>
            <p class="modal-subtitle">Begin tracking your work time</p>
          </div>
        </div>
        <button @click="emit('close')" class="close-btn" title="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div v-if="error" class="error-banner">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{{ error }}</span>
      </div>

      <form @submit.prevent="handleStart" class="modal-body">
        <div class="form-group">
          <label class="section-label">Project</label>
          <div ref="projectDropdownRef" class="project-select" @click="openProjectDropdown">
            <div v-if="!selectedProject" class="project-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
              <span>Select a project (optional)</span>
            </div>
            <div v-else class="project-selected">
              <div class="project-dot" :style="{ backgroundColor: selectedProject.color }"></div>
              <span class="project-name">{{ selectedProject.name }}</span>
              <button type="button" @click.stop="clearProject" class="project-clear" title="Clear">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <svg class="project-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>

            <Transition name="dropdown">
              <div v-if="projectDropdownOpen" class="project-dropdown" @click.stop>
                <div class="project-search">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  </svg>
                  <input v-model="projectSearch" class="project-search-input" placeholder="Search projects..." @click.stop>
                </div>
                <div class="project-list">
                  <button v-for="p in filteredProjects" :key="p.id" type="button" :class="['project-option', { active: selectedProjectId === p.id }]" @click="selectProject(p.id)">
                    <div class="project-dot" :style="{ backgroundColor: p.color }"></div>
                    <span>{{ projectStore.getProjectPath(p.id) }}</span>
                    <span class="duration-hint">{{ p.default_duration }}m</span>
                  </button>
                  <div v-if="filteredProjects.length === 0" class="project-empty">No projects found</div>
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <div class="form-group">
          <label class="section-label">Duration</label>
          <div class="duration-row">
            <div class="duration-input-wrap">
              <input type="number" v-model.number="duration" min="5" step="5" class="duration-input">
              <span class="duration-unit">min</span>
            </div>
            <div class="duration-presets">
              <button type="button" @click="duration = 30" :class="['preset-btn', { active: duration === 30 }]">30m</button>
              <button type="button" @click="duration = 60" :class="['preset-btn', { active: duration === 60 }]">1h</button>
              <button type="button" @click="duration = 90" :class="['preset-btn', { active: duration === 90 }]">1.5h</button>
              <button type="button" @click="duration = 120" :class="['preset-btn', { active: duration === 120 }]">2h</button>
            </div>
          </div>
          <div v-if="endTime" class="end-time-hint">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            Session will end at approximately <strong>{{ endTime }}</strong>
          </div>
        </div>

        <div class="form-group">
          <label class="section-label">Tags</label>
          <TagMultiSelect v-model="selectedTags" />
        </div>

        <div class="modal-footer">
          <button type="button" @click="emit('close')" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="!duration || loading" class="btn-primary">
            <svg v-if="loading" class="btn-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"></circle>
            </svg>
            {{ loading ? 'Starting...' : 'Start Session' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 1rem; animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-container { background: white; border-radius: 20px; width: 100%; max-width: 480px; height: 540px; display: flex; flex-direction: column; box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15); animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px) scale(0.97); } to { opacity: 1; transform: translateY(0) scale(1); } }

.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 1.5rem 1rem; flex-shrink: 0; }
.header-content { display: flex; align-items: center; gap: 1rem; }
.header-icon { display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: #ecfdf5; border-radius: 12px; }
.modal-title { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0; }
.modal-subtitle { font-size: 0.85rem; color: #64748b; margin: 0.125rem 0 0; }
.close-btn { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border: none; background: #f1f5f9; border-radius: 10px; cursor: pointer; color: #64748b; transition: all 0.2s ease; }
.close-btn:hover { background: #e2e8f0; color: #0f172a; }

.error-banner { display: flex; align-items: center; gap: 0.625rem; margin: 0 1.5rem; padding: 0.75rem 1rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; color: #dc2626; font-size: 0.875rem; flex-shrink: 0; }

.modal-body { display: flex; flex-direction: column; flex: 1; min-height: 0; padding: 1.25rem 1.5rem 1.5rem; gap: 1.25rem; overflow-y: auto; }

.section-label { font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 0.5rem; }

.project-select { position: relative; cursor: pointer; }
.project-placeholder, .project-selected { display: flex; align-items: center; gap: 0.625rem; padding: 0.75rem 1rem; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.95rem; color: #0f172a; background: white; transition: all 0.2s ease; }
.project-placeholder { color: #94a3b8; }
.project-select:hover .project-placeholder, .project-select:hover .project-selected { border-color: #cbd5e1; }
.project-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.project-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.project-clear { display: flex; align-items: center; justify-content: center; width: 20px; height: 20px; border: none; background: transparent; border-radius: 4px; cursor: pointer; color: #94a3b8; flex-shrink: 0; }
.project-clear:hover { background: #f1f5f9; color: #64748b; }
.project-chevron { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: #94a3b8; pointer-events: none; }

.project-dropdown { position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12); z-index: 200; overflow: hidden; }
.project-search { display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 0.75rem; border-bottom: 1px solid #f1f5f9; }
.project-search svg { color: #94a3b8; flex-shrink: 0; }
.project-search-input { flex: 1; border: none; outline: none; font-size: 0.875rem; color: #0f172a; background: transparent; }
.project-search-input::placeholder { color: #94a3b8; }
.project-list { max-height: 180px; overflow-y: auto; padding: 0.375rem; }
.project-option { display: flex; align-items: center; gap: 0.625rem; width: 100%; padding: 0.5rem 0.625rem; border: none; background: transparent; border-radius: 8px; font-size: 0.85rem; color: #334155; cursor: pointer; transition: all 0.15s ease; text-align: left; }
.project-option:hover { background: #f8fafc; }
.project-option.active { background: #ecfdf5; color: #059669; }
.duration-hint { margin-left: auto; color: #94a3b8; font-size: 0.75rem; flex-shrink: 0; }
.project-empty { padding: 1rem; text-align: center; font-size: 0.85rem; color: #94a3b8; }

.duration-row { display: flex; align-items: center; gap: 0.75rem; }
.duration-input-wrap { position: relative; width: 100px; flex-shrink: 0; }
.duration-input { width: 100%; padding: 0.625rem 2.5rem 0.625rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 1rem; font-weight: 600; color: #0f172a; text-align: center; }
.duration-input:focus { outline: none; border-color: #10b981; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1); }
.duration-unit { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font-size: 0.8rem; color: #94a3b8; pointer-events: none; }
.duration-presets { display: flex; gap: 0.375rem; flex-wrap: wrap; }
.preset-btn { padding: 0.5rem 0.75rem; border: 1px solid #e2e8f0; background: white; border-radius: 8px; font-size: 0.85rem; font-weight: 500; color: #64748b; cursor: pointer; transition: all 0.15s ease; }
.preset-btn:hover { border-color: #10b981; color: #10b981; }
.preset-btn.active { background: #10b981; border-color: #10b981; color: white; }

.end-time-hint { display: flex; align-items: center; gap: 0.375rem; padding: 0.5rem 0.75rem; background: #ecfdf5; border-radius: 8px; color: #059669; font-size: 0.8rem; }
.end-time-hint svg { flex-shrink: 0; }

.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: auto; padding-top: 1rem; border-top: 1px solid #f1f5f9; flex-shrink: 0; }
.btn-secondary { padding: 0.75rem 1.25rem; border: 1px solid #e2e8f0; background: white; border-radius: 10px; font-size: 0.9rem; font-weight: 500; color: #334155; cursor: pointer; transition: all 0.2s ease; }
.btn-secondary:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; border-radius: 10px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-spinner { width: 16px; height: 16px; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.dropdown-enter-active, .dropdown-leave-active { transition: all 0.15s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-4px); }

@media (max-width: 640px) { .modal-container { border-radius: 16px; margin: 0.5rem; } }
</style>
