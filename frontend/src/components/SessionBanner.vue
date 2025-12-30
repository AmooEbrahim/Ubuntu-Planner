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

  // Update elapsed time every second for smooth display
  updateInterval.value = setInterval(() => {
    // Force reactive update by accessing computed properties
    if (session.value) {
      // This triggers reactivity
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
  <div v-if="session" class="session-banner" :class="{ minimized, overtime: isOvertime }">
    <!-- Minimized View -->
    <div v-if="minimized" class="banner-minimized" @click="minimized = false">
      <span class="status-indicator">🟢</span>
      <span class="minimized-text">
        {{ session.project?.name || 'Session' }} •
        {{ formatDuration(elapsed) }} / {{ formatDuration(session.planned_duration) }}
        <span v-if="isOvertime" class="overtime-badge">+{{ formatDuration(overtimeMinutes) }}</span>
      </span>
      <button class="expand-btn" title="Expand">▼</button>
    </div>

    <!-- Expanded View -->
    <div v-else class="banner-expanded">
      <div class="banner-header">
        <div class="project-info">
          <span class="status-indicator">🟢</span>
          <span class="project-name">{{ session.project?.name || 'No Project' }}</span>
        </div>

        <div class="time-info">
          <span class="elapsed">{{ formatDuration(elapsed) }}</span>
          <span class="separator">/</span>
          <span class="planned">{{ formatDuration(session.planned_duration) }}</span>
          <span v-if="!isOvertime && remaining > 0" class="remaining">
            ({{ formatDuration(remaining) }} left)
          </span>
          <span v-if="isOvertime" class="overtime-text">
            (+{{ formatDuration(overtimeMinutes) }} over)
          </span>
        </div>

        <button @click="minimized = true" class="minimize-btn" title="Minimize">▲</button>
      </div>

      <div class="progress-bar">
        <div
          class="progress-fill"
          :class="{ overtime: progress >= 100 }"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>

      <div class="banner-actions">
        <button @click="handleAddTime" class="action-btn" title="Add 15 minutes">
          <span>⏱</span>
          <span class="btn-text">+15 min</span>
        </button>

        <button @click="openNoteDialog" class="action-btn" title="Add note">
          <span>📝</span>
          <span class="btn-text">Add Note</span>
        </button>

        <button
          @click="handleToggleNotifications"
          class="action-btn"
          :title="session.notification_disabled ? 'Enable notifications' : 'Disable notifications'"
        >
          {{ session.notification_disabled ? '🔕' : '🔔' }}
        </button>

        <button @click="handleQuickStop" class="action-btn danger" title="Stop without review">
          <span>⏹</span>
          <span class="btn-text">Quick Stop</span>
        </button>

        <button @click="openReview" class="action-btn primary" title="Stop and review">
          <span>✓</span>
          <span class="btn-text">Stop & Review</span>
        </button>
      </div>
    </div>

    <!-- Note Dialog -->
    <div v-if="showNoteDialog" class="note-dialog-overlay" @click.self="showNoteDialog = false">
      <div class="note-dialog-content">
        <h3>Add Note</h3>
        <textarea
          v-model="noteText"
          placeholder="Enter note..."
          rows="3"
          class="note-textarea"
          autofocus
        ></textarea>
        <div class="note-actions">
          <button @click="showNoteDialog = false" class="btn btn-secondary">Cancel</button>
          <button @click="saveNote" class="btn btn-primary" :disabled="!noteText.trim()">
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Review Dialog -->
    <SessionReviewDialog
      v-if="showReview"
      :session="session"
      @close="showReview = false"
      @saved="showReview = false"
    />
  </div>
</template>

<style scoped>
.session-banner {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: white;
  border-bottom: 2px solid #10b981;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.session-banner.overtime {
  border-bottom-color: #ef4444;
}

.banner-minimized {
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.banner-minimized:hover {
  background-color: #f9fafb;
}

.status-indicator {
  font-size: 0.875rem;
  line-height: 1;
}

.minimized-text {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.overtime-badge {
  color: #ef4444;
  font-weight: 700;
  margin-left: 0.25rem;
}

.expand-btn,
.minimize-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  font-size: 0.75rem;
  padding: 0.25rem;
  transition: color 0.2s;
}

.expand-btn:hover,
.minimize-btn:hover {
  color: #374151;
}

.banner-expanded {
  padding: 1rem;
}

.banner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.project-name {
  font-weight: 700;
  font-size: 1rem;
  color: #111827;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.elapsed {
  color: #10b981;
  font-size: 1rem;
}

.separator {
  color: #9ca3af;
}

.planned {
  color: #6b7280;
}

.remaining {
  color: #6b7280;
  font-weight: 400;
  font-size: 0.875rem;
}

.overtime-text {
  color: #ef4444;
  font-weight: 700;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #3b82f6);
  transition: width 0.3s ease;
}

.progress-fill.overtime {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

.banner-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-btn.primary {
  background: #10b981;
  color: white;
  border-color: #10b981;
  font-weight: 600;
}

.action-btn.primary:hover {
  background: #059669;
}

.action-btn.danger {
  color: #dc2626;
  border-color: #dc2626;
}

.action-btn.danger:hover {
  background: #fee2e2;
}

.btn-text {
  display: none;
}

@media (min-width: 640px) {
  .btn-text {
    display: inline;
  }
}

.note-dialog-overlay {
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

.note-dialog-content {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.note-dialog-content h3 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.note-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 1rem;
}

.note-textarea:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.note-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn {
  padding: 0.5rem 1rem;
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
