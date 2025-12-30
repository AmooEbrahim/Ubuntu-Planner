# Sessions Frontend Implementation

Session management UI components.

## Store

Create `frontend/src/stores/sessions.js`:

```javascript
import { defineStore } from 'pinia'
import api from '@/services/api'

export const useSessionStore = defineStore('sessions', {
  state: () => ({
    activeSession: null,
    recentSessions: [],
    loading: false,
    error: null,
    pollInterval: null
  }),

  getters: {
    isSessionActive: (state) => state.activeSession !== null,

    elapsedMinutes: (state) => {
      if (!state.activeSession) return 0
      const start = new Date(state.activeSession.start_time)
      const now = new Date()
      return Math.floor((now - start) / 1000 / 60)
    },

    remainingMinutes: (state) => {
      if (!state.activeSession) return 0
      const elapsed = state.elapsedMinutes
      return Math.max(0, state.activeSession.planned_duration - elapsed)
    }
  },

  actions: {
    async fetchActiveSession() {
      try {
        const response = await api.get('/api/sessions/active')
        this.activeSession = response.data
      } catch (error) {
        this.error = error.message
      }
    },

    async fetchRecentSessions() {
      try {
        const response = await api.get('/api/sessions/recent')
        this.recentSessions = response.data
      } catch (error) {
        this.error = error.message
      }
    },

    async startSession(sessionData) {
      const response = await api.post('/api/sessions/', sessionData)
      this.activeSession = response.data
      this.startPolling()
      return response.data
    },

    async stopSession(sessionId, reviewData = null) {
      const response = await api.post(`/api/sessions/${sessionId}/stop`, reviewData)
      this.activeSession = null
      this.stopPolling()
      await this.fetchRecentSessions()
      return response.data
    },

    async addNote(sessionId, note) {
      await api.post(`/api/sessions/${sessionId}/add-note`, { note })
      await this.fetchActiveSession()
    },

    async addTime(sessionId, minutes = 15) {
      await api.post(`/api/sessions/${sessionId}/add-time`, { minutes })
      await this.fetchActiveSession()
    },

    async toggleNotifications(sessionId) {
      await api.post(`/api/sessions/${sessionId}/toggle-notifications`)
      await this.fetchActiveSession()
    },

    startPolling() {
      if (this.pollInterval) return

      this.pollInterval = setInterval(() => {
        this.fetchActiveSession()
      }, 120000) // Poll every 2 minutes
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    }
  }
})
```

## Start Session Dialog

Create `frontend/src/components/StartSessionDialog.vue`:

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import { usePlanningStore } from '@/stores/planning'

const emit = defineEmits(['close', 'started'])

const sessionStore = useSessionStore()
const projectStore = useProjectStore()
const planningStore = usePlanningStore()

const selectedProject = ref(null)
const selectedPlanning = ref(null)
const duration = ref(60)
const mode = ref('project') // 'project' or 'planning'

const todayPlanning = computed(() => planningStore.todayPlanning)
const pinnedProjects = computed(() => projectStore.pinnedProjects)

onMounted(async () => {
  await projectStore.fetchProjects()
  await planningStore.fetchPlanningForDate(new Date())
})

function selectProject(project) {
  selectedProject.value = project
  duration.value = project.default_duration
  mode.value = 'project'
}

function selectPlanning(planning) {
  selectedPlanning.value = planning
  selectedProject.value = planning.project
  const start = new Date(planning.scheduled_start)
  const end = new Date(planning.scheduled_end)
  duration.value = Math.floor((end - start) / 1000 / 60)
  mode.value = 'planning'
}

async function handleStart() {
  const sessionData = {
    project_id: selectedProject.value?.id || null,
    planned_duration: duration.value,
    planning_id: mode.value === 'planning' ? selectedPlanning.value?.id : null
  }

  try {
    await sessionStore.startSession(sessionData)
    emit('started')
  } catch (error) {
    alert('Error starting session: ' + error.message)
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal large">
      <h2>Start Session</h2>

      <!-- Today's Planning -->
      <div v-if="todayPlanning.length" class="section">
        <h3>Today's Planning</h3>
        <div class="planning-grid">
          <button
            v-for="plan in todayPlanning"
            :key="plan.id"
            @click="selectPlanning(plan)"
            :class="['planning-card', { selected: selectedPlanning?.id === plan.id }]"
          >
            <div class="time">{{ formatTime(plan.scheduled_start) }}</div>
            <div class="project-name">{{ plan.project.name }}</div>
            <div v-if="plan.description" class="description">{{ plan.description }}</div>
          </button>
        </div>
      </div>

      <!-- Pinned Projects -->
      <div v-if="pinnedProjects.length" class="section">
        <h3>Pinned Projects</h3>
        <div class="projects-grid">
          <button
            v-for="project in pinnedProjects"
            :key="project.id"
            @click="selectProject(project)"
            :class="['project-card', { selected: selectedProject?.id === project.id }]"
            :style="{ borderColor: project.color }"
          >
            <div class="color-indicator" :style="{ backgroundColor: project.color }"></div>
            <div class="project-name">{{ project.name }}</div>
          </button>
        </div>
      </div>

      <!-- Duration Setting -->
      <div v-if="selectedProject" class="section">
        <h3>Duration</h3>
        <div class="duration-controls">
          <input type="number" v-model.number="duration" min="5" step="5">
          <span>minutes</span>
          <div class="quick-buttons">
            <button @click="duration = 30">30</button>
            <button @click="duration = 60">60</button>
            <button @click="duration = 90">90</button>
            <button @click="duration = 120">120</button>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <button @click="emit('close')">Cancel</button>
        <button
          @click="handleStart"
          :disabled="!selectedProject"
          class="btn-primary"
        >
          Start Session
        </button>
      </div>
    </div>
  </div>
</template>
```

## Session Review Dialog

Create `frontend/src/components/SessionReviewDialog.vue`:

```vue
<script setup>
import { ref } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import TagSelector from '@/components/TagSelector.vue'

const props = defineProps({
  session: Object
})

const emit = defineEmits(['close', 'saved'])

const sessionStore = useSessionStore()

const formData = ref({
  satisfaction_score: 80,
  tasks_done: '',
  notes: '',
  tag_ids: []
})

const actualDuration = computed(() => {
  const start = new Date(props.session.start_time)
  const now = new Date()
  return Math.floor((now - start) / 1000 / 60)
})

async function handleSave() {
  try {
    await sessionStore.stopSession(props.session.id, formData.value)
    emit('saved')
  } catch (error) {
    alert('Error saving review: ' + error.message)
  }
}

async function handleQuickSave() {
  try {
    await sessionStore.stopSession(props.session.id)
    emit('saved')
  } catch (error) {
    alert('Error stopping session: ' + error.message)
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <h2>Session Review</h2>

      <div class="session-summary">
        <div>Project: {{ session.project?.name || 'No Project' }}</div>
        <div>Duration: {{ actualDuration }} minutes ({{ session.planned_duration }} planned)</div>
      </div>

      <form @submit.prevent="handleSave">
        <div class="form-group">
          <label>Satisfaction (0-100)</label>
          <input type="range" v-model.number="formData.satisfaction_score" min="0" max="100">
          <span>{{ formData.satisfaction_score }}</span>
        </div>

        <div class="form-group">
          <label>What did you accomplish?</label>
          <textarea v-model="formData.tasks_done" rows="4"></textarea>
        </div>

        <div class="form-group">
          <label>Additional notes</label>
          <textarea v-model="formData.notes" rows="3"></textarea>
        </div>

        <div class="form-group">
          <label>Tags</label>
          <TagSelector
            :project-id="session.project_id"
            v-model="formData.tag_ids"
          />
        </div>

        <div class="form-actions">
          <button type="button" @click="handleQuickSave">Save Without Review</button>
          <button type="submit" class="btn-primary">Save Review</button>
        </div>
      </form>
    </div>
  </div>
</template>
```

## Checklist

- [ ] Sessions store created with polling
- [ ] Start session dialog created
- [ ] Session review dialog created
- [ ] Can start session from planning
- [ ] Can start session from pinned projects
- [ ] Duration can be adjusted
- [ ] Review form works
- [ ] Quick save works
