<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import SessionReviewDialog from './SessionReviewDialog.vue'

const sessionStore = useSessionStore()
const minimized = ref(false)
const showReview = ref(false)
const showNoteDialog = ref(false)
const noteText = ref('')
const updateInterval = ref(null)

const session = computed(() => sessionStore.activeSession)
const elapsed = computed(() => sessionStore.elapsedMinutes)
const remaining = computed(() => sessionStore.remainingMinutes)
const isOvertime = computed(() => sessionStore.isOvertime)
const overtimeMinutes = computed(() => sessionStore.overtimeMinutes)

const progress = computed(() => {
  if (!session.value) return 0
  return Math.min((elapsed.value / session.value.planned_duration) * 100, 100)
})

onMounted(async () => {
  await sessionStore.fetchActiveSession()

  updateInterval.value = setInterval(() => {
    if (session.value) {
      const _ = elapsed.value
    }
  }, 1000)
})

onUnmounted(() => {
  sessionStore.stopPolling()
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }
})

watch(session, (newSession) => {
  if (newSession && !updateInterval.value) {
    updateInterval.value = setInterval(() => {
      const _ = elapsed.value
    }, 1000)
  } else if (!newSession && updateInterval.value) {
    clearInterval(updateInterval.value)
    updateInterval.value = null
  }
})

async function handleAddTime() {
  try {
    await sessionStore.addTime(session.value.id, 15)
  } catch (err) {
    alert('Error adding time: ' + (err.response?.data?.detail || err.message))
  }
}

async function handleToggleNotifications() {
  try {
    await sessionStore.toggleNotifications(session.value.id)
  } catch (err) {
    alert('Error toggling notifications: ' + (err.response?.data?.detail || err.message))
  }
}

function openNoteDialog() {
  showNoteDialog.value = true
  noteText.value = ''
}

async function saveNote() {
  if (noteText.value.trim()) {
    try {
      await sessionStore.addNote(session.value.id, noteText.value.trim())
      showNoteDialog.value = false
      noteText.value = ''
    } catch (err) {
      alert('Error saving note: ' + (err.response?.data?.detail || err.message))
    }
  }
}

async function handleQuickStop() {
  if (confirm('Stop session without review?')) {
    try {
      await sessionStore.stopSession(session.value.id)
    } catch (err) {
      alert('Error stopping session: ' + (err.response?.data?.detail || err.message))
    }
  }
}

function openReview() {
  showReview.value = true
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}
</script>

<template>
  <div v-if="session" class="px-3 pt-3">
    <div
      class="glass-card overflow-hidden transition-all duration-300"
      :class="[
        isOvertime
          ? 'ring-2 ring-danger/40 shadow-danger/10'
          : 'ring-1 ring-success/30 shadow-success/10'
      ]"
    >
      <!-- Minimized View -->
      <button
        v-if="minimized"
        type="button"
        class="w-full px-4 py-2.5 flex items-center gap-3 text-left hover:bg-white/30 dark:hover:bg-white/5 transition-colors"
        @click="minimized = false"
      >
        <span
          class="inline-flex w-2.5 h-2.5 rounded-full flex-shrink-0"
          :class="isOvertime ? 'bg-danger animate-pulse' : 'bg-success'"
        ></span>
        <span class="flex-1 text-sm font-semibold truncate">
          {{ session.project?.name || 'Session' }}
          <span class="text-fg-muted font-normal">·</span>
          <span class="font-mono text-fg-muted">{{ formatDuration(elapsed) }} / {{ formatDuration(session.planned_duration) }}</span>
          <span v-if="isOvertime" class="badge badge-danger ml-2">+{{ formatDuration(overtimeMinutes) }}</span>
        </span>
        <span class="text-fg-subtle">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </span>
      </button>

      <!-- Expanded View -->
      <div v-else class="p-4">
        <div class="flex items-center justify-between gap-3 mb-3">
          <div class="flex items-center gap-2 min-w-0">
            <span
              class="inline-flex w-2.5 h-2.5 rounded-full flex-shrink-0"
              :class="isOvertime ? 'bg-danger animate-pulse' : 'bg-success'"
            ></span>
            <span class="font-semibold truncate">{{ session.project?.name || 'No Project' }}</span>
          </div>

          <div class="flex items-center gap-2 text-sm">
            <span
              class="font-mono font-bold text-base"
              :class="isOvertime ? 'text-danger' : 'text-success'"
            >{{ formatDuration(elapsed) }}</span>
            <span class="text-fg-subtle">/</span>
            <span class="font-mono text-muted">{{ formatDuration(session.planned_duration) }}</span>
            <span v-if="!isOvertime && remaining > 0" class="text-muted hidden sm:inline">
              ({{ formatDuration(remaining) }} left)
            </span>
            <span v-if="isOvertime" class="badge badge-danger hidden sm:inline">
              +{{ formatDuration(overtimeMinutes) }} over
            </span>
          </div>

          <button
            @click="minimized = true"
            class="icon-btn"
            title="Minimize"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
          </button>
        </div>

        <div class="h-1.5 rounded-full bg-fg-subtle/20 overflow-hidden mb-3">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="progress >= 100
              ? 'bg-gradient-to-r from-danger to-rose-600'
              : 'bg-gradient-to-r from-success to-accent'"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <button @click="handleAddTime" class="btn btn-secondary btn-sm" title="Add 15 minutes">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 8v4l3 2"></path>
            </svg>
            <span>+15 min</span>
          </button>

          <button @click="openNoteDialog" class="btn btn-secondary btn-sm" title="Add note">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <span class="hidden sm:inline">Add Note</span>
          </button>

          <button
            @click="handleToggleNotifications"
            class="icon-btn"
            :title="session.notification_disabled ? 'Enable notifications' : 'Disable notifications'"
          >
            <svg v-if="session.notification_disabled" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              <path d="M18 8a6 6 0 0 0-9.33-5"></path>
              <path d="M6.26 6.26A6 6 0 0 0 6 8c0 7-3 9-3 9h14"></path>
              <line x1="2" y1="2" x2="22" y2="22"></line>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
          </button>

          <div class="flex-1"></div>

          <button @click="handleQuickStop" class="btn btn-secondary btn-sm text-danger" title="Stop without review">
            <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
              <rect x="5" y="5" width="14" height="14" rx="1"></rect>
            </svg>
            <span class="hidden sm:inline">Quick Stop</span>
          </button>

          <button @click="openReview" class="btn btn-success btn-sm" title="Stop and review">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span>Stop &amp; Review</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Note Dialog -->
    <Transition name="modal">
      <div v-if="showNoteDialog" class="modal-overlay" @click.self="showNoteDialog = false">
        <div class="glass-panel p-6 w-full max-w-md">
          <h3 class="text-lg font-bold mb-4">Add Note</h3>
          <textarea
            v-model="noteText"
            placeholder="Enter note..."
            rows="3"
            class="input mb-4"
            autofocus
          ></textarea>
          <div class="flex justify-end gap-2">
            <button @click="showNoteDialog = false" class="btn btn-secondary">Cancel</button>
            <button @click="saveNote" class="btn btn-primary" :disabled="!noteText.trim()">
              Save
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Review Dialog -->
    <SessionReviewDialog
      v-if="showReview"
      :session="session"
      @close="showReview = false"
      @saved="showReview = false"
    />
  </div>
</template>
