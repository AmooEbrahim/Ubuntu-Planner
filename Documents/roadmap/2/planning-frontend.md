# Planning Frontend Implementation

Calendar UI and planning management.

## Store

Create `frontend/src/stores/planning.js`:

```javascript
import { defineStore } from 'pinia'
import api from '@/services/api'
import dayjs from 'dayjs'

export const usePlanningStore = defineStore('planning', {
  state: () => ({
    planning: [],
    currentDate: dayjs().format('YYYY-MM-DD'),
    loading: false,
    error: null
  }),

  getters: {
    todayPlanning: (state) => {
      const today = dayjs().format('YYYY-MM-DD')
      return state.planning.filter(p =>
        dayjs(p.scheduled_start).format('YYYY-MM-DD') === today
      )
    },

    planningByDate: (state) => (date) => {
      const dateStr = dayjs(date).format('YYYY-MM-DD')
      return state.planning.filter(p =>
        dayjs(p.scheduled_start).format('YYYY-MM-DD') === dateStr
      )
    }
  },

  actions: {
    async fetchPlanningForDate(date) {
      this.loading = true
      try {
        const response = await api.get('/api/planning/', {
          params: { date: dayjs(date).format('YYYY-MM-DD') }
        })
        this.planning = response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createPlanning(planningData) {
      const response = await api.post('/api/planning/', planningData)
      this.planning.push(response.data)
      return response.data
    },

    async updatePlanning(planningId, planningData) {
      const response = await api.put(`/api/planning/${planningId}`, planningData)
      const index = this.planning.findIndex(p => p.id === planningId)
      if (index !== -1) {
        this.planning[index] = response.data
      }
      return response.data
    },

    async deletePlanning(planningId) {
      await api.delete(`/api/planning/${planningId}`)
      this.planning = this.planning.filter(p => p.id !== planningId)
    }
  }
})
```

## Planning Page (Calendar View)

Create `frontend/src/views/Planning.vue`:

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanningStore } from '@/stores/planning'
import dayjs from 'dayjs'
import CalendarDay from '@/components/CalendarDay.vue'
import PlanningForm from '@/components/PlanningForm.vue'

const planningStore = usePlanningStore()
const currentDate = ref(dayjs())
const showForm = ref(false)
const editingPlanning = ref(null)
const viewMode = ref('day') // 'day' or 'week'

const displayDate = computed(() => currentDate.value.format('YYYY-MM-DD'))

const planning = computed(() =>
  planningStore.planningByDate(currentDate.value)
)

onMounted(() => {
  loadPlanning()
})

async function loadPlanning() {
  await planningStore.fetchPlanningForDate(currentDate.value)
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
  showForm.value = true
  // Pass timeSlot if clicked on calendar
}

function openEditForm(planning) {
  editingPlanning.value = planning
  showForm.value = true
}

async function handleDelete(planning) {
  if (confirm('Delete this planning?')) {
    await planningStore.deletePlanning(planning.id)
  }
}
</script>

<template>
  <div class="planning-page">
    <div class="header">
      <h1>Planning</h1>
      <div class="controls">
        <button @click="previousDay">←</button>
        <button @click="goToToday">Today</button>
        <button @click="nextDay">→</button>
        <span class="date-display">{{ displayDate }}</span>
      </div>
      <button @click="openCreateForm" class="btn-primary">
        + Add Planning
      </button>
    </div>

    <CalendarDay
      :date="currentDate"
      :planning="planning"
      @click-slot="openCreateForm"
      @edit="openEditForm"
      @delete="handleDelete"
    />

    <PlanningForm
      v-if="showForm"
      :planning="editingPlanning"
      :default-date="currentDate"
      @close="showForm = false"
      @saved="showForm = false; loadPlanning()"
    />
  </div>
</template>
```

## Planning Form Component

Create `frontend/src/components/PlanningForm.vue`:

```vue
<script setup>
import { ref, computed } from 'vue'
import { usePlanningStore } from '@/stores/planning'
import { useProjectStore } from '@/stores/projects'
import dayjs from 'dayjs'
import TagSelector from '@/components/TagSelector.vue'

const props = defineProps({
  planning: Object,
  defaultDate: Object
})

const emit = defineEmits(['close', 'saved'])

const planningStore = usePlanningStore()
const projectStore = useProjectStore()

const formData = ref({
  project_id: props.planning?.project_id || null,
  scheduled_start: props.planning?.scheduled_start ||
    dayjs(props.defaultDate).hour(9).minute(0).toISOString(),
  scheduled_end: props.planning?.scheduled_end ||
    dayjs(props.defaultDate).hour(10).minute(0).toISOString(),
  priority: props.planning?.priority || 'medium',
  description: props.planning?.description || '',
  tag_ids: props.planning?.tags?.map(t => t.id) || []
})

const isEdit = computed(() => !!props.planning)

const durationMinutes = computed(() => {
  const start = dayjs(formData.value.scheduled_start)
  const end = dayjs(formData.value.scheduled_end)
  return end.diff(start, 'minute')
})

function addDuration(minutes) {
  const start = dayjs(formData.value.scheduled_start)
  formData.value.scheduled_end = start.add(minutes, 'minute').toISOString()
}

async function handleSubmit() {
  try {
    if (isEdit.value) {
      await planningStore.updatePlanning(props.planning.id, formData.value)
    } else {
      await planningStore.createPlanning(formData.value)
    }
    emit('saved')
  } catch (error) {
    if (error.response?.data?.detail) {
      alert(error.response.data.detail)
    } else {
      alert('Error saving planning: ' + error.message)
    }
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <h2>{{ isEdit ? 'Edit' : 'Create' }} Planning</h2>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Project *</label>
          <select v-model="formData.project_id" required>
            <option :value="null">Select project</option>
            <option
              v-for="p in projectStore.activeProjects"
              :key="p.id"
              :value="p.id"
            >
              {{ p.name }}
            </option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Start Time *</label>
            <input
              type="datetime-local"
              v-model="formData.scheduled_start"
              required
            >
          </div>

          <div class="form-group">
            <label>End Time *</label>
            <input
              type="datetime-local"
              v-model="formData.scheduled_end"
              required
            >
          </div>
        </div>

        <div class="duration-info">
          Duration: {{ durationMinutes }} minutes
          <div class="quick-durations">
            <button type="button" @click="addDuration(30)">+30m</button>
            <button type="button" @click="addDuration(60)">+1h</button>
            <button type="button" @click="addDuration(120)">+2h</button>
          </div>
        </div>

        <div class="form-group">
          <label>Priority</label>
          <div class="priority-buttons">
            <button
              type="button"
              :class="{ active: formData.priority === 'low' }"
              @click="formData.priority = 'low'"
            >
              Low
            </button>
            <button
              type="button"
              :class="{ active: formData.priority === 'medium' }"
              @click="formData.priority = 'medium'"
            >
              Medium
            </button>
            <button
              type="button"
              :class="{ active: formData.priority === 'critical' }"
              @click="formData.priority = 'critical'"
            >
              Critical
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea v-model="formData.description"></textarea>
        </div>

        <div class="form-group">
          <label>Tags</label>
          <TagSelector
            :project-id="formData.project_id"
            v-model="formData.tag_ids"
          />
        </div>

        <div class="form-actions">
          <button type="button" @click="emit('close')">Cancel</button>
          <button type="submit" class="btn-primary">Save</button>
        </div>
      </form>
    </div>
  </div>
</template>
```

## Calendar Day Component

Create `frontend/src/components/CalendarDay.vue` to display planning in a timeline view.

## Checklist

- [ ] Planning store created
- [ ] Planning page with calendar created
- [ ] Planning form created
- [ ] Calendar day component created
- [ ] Can create planning
- [ ] Can edit planning
- [ ] Can delete planning
- [ ] Overlap errors displayed
- [ ] Priority visual indicators work
- [ ] Tag selector integrated
