<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/sessions'
import TagMultiSelect from '@/components/TagMultiSelect.vue'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()

const session = ref(null)
const satisfaction = ref(80)
const tasks = ref('')
const notes = ref('')
const selectedTags = ref([])
const loading = ref(true)

const satisfactionFeedback = computed(() => {
  const val = satisfaction.value
  if (val >= 90) return "Excellent! Keep up the good work."
  if (val >= 70) return "Good job! You're making progress."
  if (val >= 50) return "Not bad. Room for improvement."
  if (val >= 30) return "Could be better. What went wrong?"
  return "Tough session. Let's analyze what happened."
})

const tasksCharCount = computed(() => tasks.value.length)
const notesCharCount = computed(() => notes.value.length)

const satisfactionColor = computed(() => {
  if (satisfaction.value >= 80) return 'rgb(var(--success))'
  if (satisfaction.value >= 60) return 'rgb(var(--info))'
  if (satisfaction.value >= 40) return 'rgb(var(--warning))'
  return 'rgb(var(--danger))'
})

onMounted(async () => {
  try {
    session.value = await sessionStore.getSession(route.params.id)
    if (session.value.satisfaction_score !== null && session.value.satisfaction_score !== undefined) {
      satisfaction.value = session.value.satisfaction_score
    }
    if (session.value.tasks_done) tasks.value = session.value.tasks_done
    if (session.value.notes) notes.value = session.value.notes
    if (session.value.tags) selectedTags.value = session.value.tags.map(t => t.id)
  } catch (error) {
    console.error('Failed to load session:', error)
  } finally {
    loading.value = false
  }
})

async function saveReview() {
  try {
    await sessionStore.updateSessionReview(route.params.id, {
      satisfaction: satisfaction.value,
      tasks: tasks.value || null,
      notes: notes.value || null,
      tag_ids: selectedTags.value
    })
    router.push('/sessions')
  } catch (error) {
    console.error('Failed to save review:', error)
    alert('Failed to save review. Please try again.')
  }
}

function skipReview() {
  router.push('/sessions')
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

function formatDateTime(dateTime) {
  if (!dateTime) return 'N/A'
  const date = new Date(dateTime)
  return date.toLocaleString('en-US', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <div v-if="loading" class="glass-card flex flex-col items-center justify-center py-16 text-muted">
      <div class="spinner mb-4"></div>
      <p>Loading session...</p>
    </div>

    <div v-else-if="session" class="glass-card p-8">
      <h1 class="page-title mb-6">Session Review</h1>

      <div class="glass-inset p-4 mb-6 space-y-1">
        <div class="flex justify-between py-1.5">
          <span class="font-semibold text-muted">Project:</span>
          <span class="text-fg">{{ session.project?.name || 'No Project' }}</span>
        </div>
        <div class="flex justify-between py-1.5">
          <span class="font-semibold text-muted">Planned:</span>
          <span class="text-fg">{{ formatDuration(session.planned_duration) }}</span>
        </div>
        <div class="flex justify-between py-1.5">
          <span class="font-semibold text-muted">Actual:</span>
          <span class="text-fg">{{ formatDuration(session.actual_duration) }}</span>
        </div>
        <div class="flex justify-between py-1.5">
          <span class="font-semibold text-muted">Started:</span>
          <span class="text-fg">{{ formatDateTime(session.start_time) }}</span>
        </div>
        <div class="flex justify-between py-1.5">
          <span class="font-semibold text-muted">Ended:</span>
          <span class="text-fg">{{ formatDateTime(session.end_time) }}</span>
        </div>
      </div>

      <div class="mb-8">
        <label class="block font-semibold text-base mb-3 text-fg">How satisfied are you with your performance?</label>

        <div class="flex items-center gap-4 mb-2">
          <input
            v-model.number="satisfaction"
            type="range"
            min="0"
            max="100"
            class="satisfaction-slider flex-1 h-2 rounded-full outline-none appearance-none"
          />
          <div class="text-2xl font-bold min-w-[3rem] text-center" :style="{ color: satisfactionColor }">{{ satisfaction }}</div>
        </div>

        <div class="flex justify-between text-sm text-muted">
          <span>0</span>
          <span>100</span>
        </div>

        <div class="mt-4 px-4 py-2.5 rounded-xl border-l-4 font-medium text-sm" :style="{ borderColor: satisfactionColor, color: satisfactionColor, backgroundColor: satisfactionColor + '15' }">{{ satisfactionFeedback }}</div>
      </div>

      <div class="mb-6">
        <label class="block font-semibold text-base mb-3 text-fg">What did you accomplish?</label>
        <textarea
          v-model="tasks"
          placeholder="List tasks, achievements, or progress made..."
          rows="5"
          maxlength="500"
          class="input"
        ></textarea>
        <div class="text-right text-xs text-muted mt-1">{{ tasksCharCount }} / 500 characters</div>
      </div>

      <div class="mb-6">
        <label class="block font-semibold text-base mb-3 text-fg">Personal Notes (Optional)</label>
        <textarea
          v-model="notes"
          placeholder="Reflections, challenges, learnings, distractions..."
          rows="5"
          maxlength="1000"
          class="input"
        ></textarea>
        <div class="text-right text-xs text-muted mt-1">{{ notesCharCount }} / 1000 characters</div>
      </div>

      <div class="mb-6">
        <label class="block font-semibold text-base mb-3 text-fg">Tags (Optional)</label>
        <TagMultiSelect v-model="selectedTags" />
      </div>

      <div class="flex gap-3 justify-end mt-8 pt-6 border-t border-fg-subtle/15">
        <button @click="skipReview" class="btn btn-secondary">
          Skip Review
        </button>
        <button @click="saveReview" class="btn btn-primary">
          Save &amp; Continue
        </button>
      </div>
    </div>

    <div v-else class="glass-card text-center py-12 text-muted">
      Session not found.
    </div>
  </div>
</template>

<style scoped>
.satisfaction-slider {
  background: linear-gradient(to right, rgb(var(--danger)), rgb(var(--warning)), rgb(var(--success)));
  -webkit-appearance: none;
  appearance: none;
}
.satisfaction-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgb(var(--accent));
  cursor: pointer;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
.satisfaction-slider::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgb(var(--accent));
  cursor: pointer;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
</style>
