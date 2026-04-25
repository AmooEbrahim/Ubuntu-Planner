<script setup>
import { ref, computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  session: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'edit', 'delete', 'update-times'])

const editingTimes = ref(false)
const startTime = ref('')
const endTime = ref('')
const saving = ref(false)

function startEditingTimes() {
  editingTimes.value = true
  startTime.value = dayjs(props.session.start_time).format('YYYY-MM-DDTHH:mm')
  if (props.session.end_time) {
    endTime.value = dayjs(props.session.end_time).format('YYYY-MM-DDTHH:mm')
  }
}

function cancelEditingTimes() {
  editingTimes.value = false
  startTime.value = ''
  endTime.value = ''
}

function saveTimeChanges() {
  saving.value = true
  emit('update-times', {
    sessionId: props.session.id,
    start_time: startTime.value ? dayjs(startTime.value).toISOString() : null,
    end_time: endTime.value ? dayjs(endTime.value).toISOString() : null
  })
  editingTimes.value = false
  saving.value = false
}

function formatDateTime(datetime) {
  return dayjs(datetime).format('MMM D, YYYY HH:mm')
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

const actualDuration = computed(() => {
  if (props.session.actual_duration) return props.session.actual_duration
  if (props.session.end_time) {
    const start = dayjs(props.session.start_time)
    const end = dayjs(props.session.end_time)
    return Math.floor(end.diff(start, 'minute'))
  }
  const start = dayjs(props.session.start_time)
  const now = dayjs()
  return Math.floor(now.diff(start, 'minute'))
})

const isOvertime = computed(() => {
  return actualDuration.value > props.session.planned_duration
})
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="glass-panel w-full max-w-xl max-h-[90vh] flex flex-col overflow-hidden">
      <div class="flex justify-between items-center p-6 border-b border-fg-subtle/15">
        <h2 class="text-xl font-bold text-fg">Session Details</h2>
        <button @click="emit('close')" class="icon-btn" title="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="p-6 overflow-y-auto flex-1 space-y-5">
        <!-- Project -->
        <div>
          <div class="label">Project</div>
          <div v-if="session.project" class="glass-inset flex items-center gap-2 p-3">
            <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: session.project.color }"></span>
            <span class="text-base font-semibold text-fg">{{ session.project.name }}</span>
          </div>
          <div v-else class="glass-inset p-3 italic text-fg-subtle">No Project</div>
        </div>

        <!-- Time -->
        <div>
          <div class="flex justify-between items-center mb-2">
            <div class="label !mb-0">Time</div>
            <button
              v-if="!editingTimes"
              @click="startEditingTimes"
              class="btn btn-secondary btn-sm"
              title="Edit times"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Edit
            </button>
          </div>

          <div v-if="!editingTimes" class="space-y-2">
            <div class="glass-inset flex justify-between items-center p-3">
              <span class="text-sm font-semibold text-muted">Started:</span>
              <span class="text-sm text-fg">{{ formatDateTime(session.start_time) }}</span>
            </div>
            <div v-if="session.end_time" class="glass-inset flex justify-between items-center p-3">
              <span class="text-sm font-semibold text-muted">Ended:</span>
              <span class="text-sm text-fg">{{ formatDateTime(session.end_time) }}</span>
            </div>
            <div v-else class="flex justify-center">
              <span class="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-success text-white text-sm font-semibold">
                <span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
                Active Session
              </span>
            </div>
          </div>

          <div v-else class="space-y-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-sm font-semibold text-fg">Start Time:</label>
              <input
                type="datetime-local"
                v-model="startTime"
                class="input"
              />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-sm font-semibold text-fg">End Time:</label>
              <input
                type="datetime-local"
                v-model="endTime"
                class="input"
              />
            </div>
            <div class="flex justify-end gap-2 mt-2">
              <button @click="cancelEditingTimes" class="btn btn-secondary btn-sm">Cancel</button>
              <button @click="saveTimeChanges" :disabled="saving" class="btn btn-primary btn-sm">
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Duration -->
        <div>
          <div class="label">Duration</div>
          <div class="grid grid-cols-2 gap-3">
            <div class="glass-inset p-3 text-center">
              <span class="block text-xs font-semibold text-muted mb-1">Planned</span>
              <span class="block text-xl font-bold text-success">{{ formatDuration(session.planned_duration) }}</span>
            </div>
            <div class="glass-inset p-3 text-center">
              <span class="block text-xs font-semibold text-muted mb-1">Actual</span>
              <span class="block text-xl font-bold" :class="isOvertime ? 'text-warning' : 'text-success'">
                {{ formatDuration(actualDuration) }}
                <span v-if="isOvertime" class="block text-xs text-warning font-medium mt-1">Overtime</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Tags -->
        <div v-if="session.tags && session.tags.length > 0">
          <div class="label">Tags</div>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in session.tags"
              :key="tag.id"
              class="px-3 py-1.5 rounded-md text-white text-sm font-medium"
              :style="{ backgroundColor: tag.color }"
            >
              {{ tag.name }}
            </span>
          </div>
        </div>

        <!-- Satisfaction -->
        <div v-if="session.satisfaction_score && session.satisfaction_score > 0">
          <div class="label">Satisfaction Score</div>
          <div class="flex items-center gap-3">
            <div class="flex-1 h-3 rounded-full bg-fg-subtle/20 overflow-hidden">
              <div class="h-full rounded-full transition-[width] duration-300" :style="{ width: session.satisfaction_score + '%', background: 'linear-gradient(to right, rgb(var(--danger)), rgb(var(--warning)), rgb(var(--success)))' }"></div>
            </div>
            <div class="text-base font-bold text-fg min-w-[4rem] text-right">{{ session.satisfaction_score }}/100</div>
          </div>
        </div>

        <!-- Tasks -->
        <div v-if="session.tasks_done && session.tasks_done.trim()">
          <div class="label flex items-center gap-1.5"><span class="text-success">✓</span> Tasks Accomplished</div>
          <div class="glass-inset p-3 text-sm text-fg leading-relaxed whitespace-pre-wrap break-words">{{ session.tasks_done }}</div>
        </div>

        <!-- Notes -->
        <div v-if="session.notes && session.notes.trim()">
          <div class="label flex items-center gap-1.5"><span>📝</span> Notes</div>
          <div class="glass-inset p-3 text-sm text-fg leading-relaxed whitespace-pre-wrap break-words">{{ session.notes }}</div>
        </div>
      </div>

      <div class="flex justify-end gap-2 p-6 border-t border-fg-subtle/15">
        <button @click="emit('close')" class="btn btn-secondary">Close</button>
        <button @click="emit('edit', session)" class="btn btn-primary">Edit</button>
        <button @click="emit('delete', session)" class="btn btn-danger">Delete</button>
      </div>
    </div>
  </div>
</template>
