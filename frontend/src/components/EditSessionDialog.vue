<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import TagMultiSelect from '@/components/TagMultiSelect.vue'
import dayjs from 'dayjs'

const props = defineProps({ session: { type: Object, required: true } })
const emit = defineEmits(['close', 'saved'])

const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const form = ref({
  project_id: props.session.project_id,
  start_time: props.session.start_time ? dayjs(props.session.start_time).format('YYYY-MM-DDTHH:mm') : '',
  end_time: props.session.end_time ? dayjs(props.session.end_time).format('YYYY-MM-DDTHH:mm') : '',
  planned_duration: props.session.planned_duration,
  actual_duration: props.session.actual_duration,
  satisfaction_score: props.session.satisfaction_score,
  tasks_done: props.session.tasks_done,
  notes: props.session.notes,
  tag_ids: props.session.tags ? props.session.tags.map(t => t.id) : []
})

const saving = ref(false)
const error = ref('')
const activeTab = ref('details')

onMounted(async () => {
  if (projectStore.projects.length === 0) { await projectStore.fetchProjects() }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''
  try {
    const updateData = {
      ...form.value,
      start_time: form.value.start_time ? dayjs(form.value.start_time).toISOString() : null,
      end_time: form.value.end_time ? dayjs(form.value.end_time).toISOString() : null
    }
    await sessionStore.updateSession(props.session.id, updateData)
    emit('saved')
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to update session'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')" @keydown.escape="emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <div class="header-content">
          <div class="header-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" width="20" height="20">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </div>
          <div>
            <h2 class="modal-title">Edit Session</h2>
            <p class="modal-subtitle">Update session details</p>
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

      <div class="modal-tabs">
        <button :class="['tab-btn', { active: activeTab === 'details' }]" @click="activeTab = 'details'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          Details
        </button>
        <button :class="['tab-btn', { active: activeTab === 'reflection' }]" @click="activeTab = 'reflection'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
            <line x1="9" y1="9" x2="9.01" y2="9"></line>
            <line x1="15" y1="9" x2="15.01" y2="9"></line>
          </svg>
          Reflection
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="body-scroll">
          <div v-show="activeTab === 'details'" class="tab-content">
            <div class="form-group">
              <label class="section-label">Project</label>
              <select v-model="form.project_id" class="form-input">
                <option :value="null">No Project</option>
                <option v-for="project in projectStore.activeProjects" :key="project.id" :value="project.id">{{ project.name }}</option>
              </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="section-label">Start Time</label>
                <input type="datetime-local" v-model="form.start_time" class="form-input" required>
              </div>
              <div class="form-group">
                <label class="section-label">End Time</label>
                <input type="datetime-local" v-model="form.end_time" class="form-input">
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="section-label">Planned Duration</label>
                <div class="input-with-unit">
                  <input type="number" v-model.number="form.planned_duration" min="1" max="480" class="form-input">
                  <span class="unit">min</span>
                </div>
              </div>
              <div class="form-group">
                <label class="section-label">Actual Duration</label>
                <div class="input-with-unit">
                  <input type="number" v-model.number="form.actual_duration" min="1" max="480" class="form-input">
                  <span class="unit">min</span>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="section-label">Tags</label>
              <TagMultiSelect v-model="form.tag_ids" />
            </div>
          </div>

          <div v-show="activeTab === 'reflection'" class="tab-content">
            <div class="form-group">
              <label class="section-label">Satisfaction</label>
              <div class="satisfaction-control">
                <div class="satisfaction-value" :style="{ color: form.satisfaction_score !== null ? (form.satisfaction_score >= 80 ? '#10b981' : form.satisfaction_score >= 60 ? '#3b82f6' : form.satisfaction_score >= 40 ? '#f59e0b' : '#ef4444') : '#94a3b8' }">
                  {{ form.satisfaction_score !== null ? form.satisfaction_score + '%' : 'Not set' }}
                </div>
                <input type="range" v-model.number="form.satisfaction_score" min="0" max="100" step="5" class="satisfaction-slider">
                <button type="button" @click="form.satisfaction_score = null" class="clear-link">Clear</button>
              </div>
            </div>

            <div class="form-group">
              <label class="section-label">Tasks Accomplished</label>
              <textarea v-model="form.tasks_done" rows="3" class="form-textarea" placeholder="What did you accomplish?"></textarea>
            </div>

            <div class="form-group">
              <label class="section-label">Notes</label>
              <textarea v-model="form.notes" rows="3" class="form-textarea" placeholder="Any additional notes..."></textarea>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" @click="emit('close')" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="saving" class="btn-primary">
            <svg v-if="saving" class="btn-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"></circle>
            </svg>
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 1rem; animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-container { background: white; border-radius: 20px; width: 100%; max-width: 520px; height: 560px; display: flex; flex-direction: column; box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15); animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px) scale(0.97); } to { opacity: 1; transform: translateY(0) scale(1); } }

.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 1.5rem 1rem; flex-shrink: 0; }
.header-content { display: flex; align-items: center; gap: 1rem; }
.header-icon { display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; background: #eef2ff; border-radius: 12px; }
.modal-title { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0; }
.modal-subtitle { font-size: 0.85rem; color: #64748b; margin: 0.125rem 0 0; }
.close-btn { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border: none; background: #f1f5f9; border-radius: 10px; cursor: pointer; color: #64748b; transition: all 0.2s ease; }
.close-btn:hover { background: #e2e8f0; color: #0f172a; }

.error-banner { display: flex; align-items: center; gap: 0.625rem; margin: 0 1.5rem; padding: 0.75rem 1rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; color: #dc2626; font-size: 0.875rem; flex-shrink: 0; }

.modal-tabs { display: flex; gap: 0.25rem; padding: 1rem 1.5rem 0; background: #f8fafc; margin: 0 1.5rem; border-radius: 10px; flex-shrink: 0; }
.tab-btn { display: flex; align-items: center; gap: 0.5rem; flex: 1; padding: 0.625rem 1rem; border: none; background: transparent; border-radius: 8px; font-size: 0.875rem; font-weight: 500; color: #64748b; cursor: pointer; transition: all 0.2s ease; }
.tab-btn.active { background: white; color: #6366f1; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.tab-btn:hover:not(.active) { color: #334155; }

.modal-body { display: flex; flex-direction: column; flex: 1; min-height: 0; padding: 0 1.5rem 1.5rem; }
.body-scroll { flex: 1; min-height: 0; overflow-y: auto; padding-top: 1.25rem; }
.tab-content { display: flex; flex-direction: column; gap: 1.25rem; }

.section-label { font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 0.5rem; }
.form-input { width: 100%; padding: 0.625rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.9rem; color: #0f172a; background: white; transition: all 0.2s ease; }
.form-input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
.form-textarea { width: 100%; padding: 0.75rem 1rem; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.9rem; color: #0f172a; background: white; transition: all 0.2s ease; resize: vertical; font-family: inherit; }
.form-textarea:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
.form-textarea::placeholder { color: #94a3b8; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.input-with-unit { display: flex; align-items: center; gap: 0.5rem; }
.input-with-unit .form-input { flex: 1; }
.unit { font-size: 0.85rem; color: #64748b; flex-shrink: 0; }

.satisfaction-control { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; padding: 1rem; background: #f8fafc; border-radius: 10px; }
.satisfaction-value { font-size: 1.5rem; font-weight: 700; }
.satisfaction-slider { width: 100%; accent-color: #6366f1; }
.clear-link { background: none; border: none; color: #6366f1; font-size: 0.85rem; font-weight: 500; cursor: pointer; }
.clear-link:hover { text-decoration: underline; }

.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid #f1f5f9; flex-shrink: 0; }
.btn-secondary { padding: 0.75rem 1.25rem; border: 1px solid #e2e8f0; background: white; border-radius: 10px; font-size: 0.9rem; font-weight: 500; color: #334155; cursor: pointer; transition: all 0.2s ease; }
.btn-secondary:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border: none; border-radius: 10px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-spinner { width: 16px; height: 16px; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) { .modal-container { border-radius: 16px; margin: 0.5rem; } .form-row { grid-template-columns: 1fr; } }
</style>
