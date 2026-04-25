<script setup>
import { ref, onMounted } from 'vue'
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

function satisfactionColor(score) {
  if (score === null || score === undefined) return 'rgb(var(--fg-subtle))'
  if (score >= 80) return 'rgb(var(--success))'
  if (score >= 60) return 'rgb(var(--info))'
  if (score >= 40) return 'rgb(var(--warning))'
  return 'rgb(var(--danger))'
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')" @keydown.escape="emit('close')">
    <div class="glass-panel w-full max-w-xl max-h-[90vh] flex flex-col">
      <div class="flex justify-between items-center p-6 pb-4 flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-accent/15 text-accent">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-fg">Edit Session</h2>
            <p class="text-xs text-muted mt-0.5">Update session details</p>
          </div>
        </div>
        <button @click="emit('close')" class="icon-btn" title="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div v-if="error" class="mx-6 mb-4 flex items-center gap-2 px-3 py-2 rounded-xl border border-danger/30 bg-danger/10 text-danger text-sm">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" class="flex-shrink-0">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{{ error }}</span>
      </div>

      <div class="mx-6 mb-3 glass-inset p-1 inline-flex gap-0.5 flex-shrink-0">
        <button
          :class="['flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
            activeTab === 'details' ? 'bg-accent text-white shadow-sm' : 'text-fg-muted hover:text-fg']"
          @click="activeTab = 'details'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          Details
        </button>
        <button
          :class="['flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
            activeTab === 'reflection' ? 'bg-accent text-white shadow-sm' : 'text-fg-muted hover:text-fg']"
          @click="activeTab = 'reflection'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
            <line x1="9" y1="9" x2="9.01" y2="9"></line>
            <line x1="15" y1="9" x2="15.01" y2="9"></line>
          </svg>
          Reflection
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="flex flex-col flex-1 min-h-0 px-6 pb-6">
        <div class="flex-1 min-h-0 overflow-y-auto pt-2">
          <div v-show="activeTab === 'details'" class="space-y-5">
            <div>
              <label class="label">Project</label>
              <select v-model="form.project_id" class="input">
                <option :value="null">No Project</option>
                <option v-for="project in projectStore.activeProjects" :key="project.id" :value="project.id">{{ project.name }}</option>
              </select>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="label">Start Time</label>
                <input type="datetime-local" v-model="form.start_time" class="input" required>
              </div>
              <div>
                <label class="label">End Time</label>
                <input type="datetime-local" v-model="form.end_time" class="input">
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="label">Planned Duration</label>
                <div class="flex items-center gap-2">
                  <input type="number" v-model.number="form.planned_duration" min="1" max="480" class="input">
                  <span class="text-sm text-muted flex-shrink-0">min</span>
                </div>
              </div>
              <div>
                <label class="label">Actual Duration</label>
                <div class="flex items-center gap-2">
                  <input type="number" v-model.number="form.actual_duration" min="1" max="480" class="input">
                  <span class="text-sm text-muted flex-shrink-0">min</span>
                </div>
              </div>
            </div>

            <div>
              <label class="label">Tags</label>
              <TagMultiSelect v-model="form.tag_ids" />
            </div>
          </div>

          <div v-show="activeTab === 'reflection'" class="space-y-5">
            <div>
              <label class="label">Satisfaction</label>
              <div class="glass-inset flex flex-col items-center gap-3 p-4">
                <div class="text-2xl font-bold" :style="{ color: satisfactionColor(form.satisfaction_score) }">
                  {{ form.satisfaction_score !== null ? form.satisfaction_score + '%' : 'Not set' }}
                </div>
                <input type="range" v-model.number="form.satisfaction_score" min="0" max="100" step="5" class="w-full" style="accent-color: rgb(var(--accent))">
                <button type="button" @click="form.satisfaction_score = null" class="text-sm text-accent hover:underline">Clear</button>
              </div>
            </div>

            <div>
              <label class="label">Tasks Accomplished</label>
              <textarea v-model="form.tasks_done" rows="3" class="input" placeholder="What did you accomplish?"></textarea>
            </div>

            <div>
              <label class="label">Notes</label>
              <textarea v-model="form.notes" rows="3" class="input" placeholder="Any additional notes..."></textarea>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-5 pt-4 border-t border-fg-subtle/15 flex-shrink-0">
          <button type="button" @click="emit('close')" class="btn btn-secondary">Cancel</button>
          <button type="submit" :disabled="saving" class="btn btn-primary">
            <svg v-if="saving" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="animate-spin">
              <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"></circle>
            </svg>
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
