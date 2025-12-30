# Active Session Banner Component

Persistent banner showing active session status across all pages.

## Component

Create `frontend/src/components/SessionBanner.vue`:

```vue
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import SessionReviewDialog from './SessionReviewDialog.vue'

const sessionStore = useSessionStore()
const minimized = ref(false)
const showReview = ref(false)
const showNoteDialog = ref(false)
const noteText = ref('')

const session = computed(() => sessionStore.activeSession)
const elapsed = computed(() => sessionStore.elapsedMinutes)
const remaining = computed(() => sessionStore.remainingMinutes)
const progress = computed(() => {
  if (!session.value) return 0
  return (elapsed.value / session.value.planned_duration) * 100
})

onMounted(() => {
  sessionStore.fetchActiveSession()
  sessionStore.startPolling()
})

onUnmounted(() => {
  sessionStore.stopPolling()
})

async function handleAddTime() {
  await sessionStore.addTime(session.value.id, 15)
}

async function handleToggleNotifications() {
  await sessionStore.toggleNotifications(session.value.id)
}

function openNoteDialog() {
  showNoteDialog.value = true
  noteText.value = ''
}

async function saveNote() {
  if (noteText.value.trim()) {
    await sessionStore.addNote(session.value.id, noteText.value)
    showNoteDialog.value = false
  }
}

async function handleQuickStop() {
  if (confirm('Stop session without review?')) {
    await sessionStore.stopSession(session.value.id)
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
  <div v-if="session" class="session-banner" :class="{ minimized }">
    <!-- Minimized View -->
    <div v-if="minimized" class="banner-minimized" @click="minimized = false">
      🟢 {{ session.project?.name || 'Session' }} •
      {{ formatDuration(elapsed) }} / {{ formatDuration(session.planned_duration) }}
      <button class="expand-btn">▼</button>
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
          <span v-if="remaining > 0" class="remaining">
            ({{ formatDuration(remaining) }} left)
          </span>
          <span v-else class="overtime">
            ({{ formatDuration(-remaining) }} over)
          </span>
        </div>

        <button @click="minimized = true" class="minimize-btn">▲</button>
      </div>

      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${Math.min(progress, 100)}%` }"></div>
      </div>

      <div class="banner-actions">
        <button @click="handleAddTime" class="action-btn">
          +15 min
        </button>

        <button @click="openNoteDialog" class="action-btn">
          Add Note
        </button>

        <button @click="handleToggleNotifications" class="action-btn">
          {{ session.notification_disabled ? '🔕' : '🔔' }}
        </button>

        <button @click="handleQuickStop" class="action-btn danger">
          Quick Stop
        </button>

        <button @click="openReview" class="action-btn primary">
          Stop & Review
        </button>
      </div>
    </div>

    <!-- Note Dialog -->
    <div v-if="showNoteDialog" class="note-dialog">
      <div class="note-dialog-content">
        <h3>Add Note</h3>
        <textarea v-model="noteText" placeholder="Enter note..." rows="3"></textarea>
        <div class="note-actions">
          <button @click="showNoteDialog = false">Cancel</button>
          <button @click="saveNote" class="btn-primary">Save</button>
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
  border-bottom: 2px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.banner-minimized {
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
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
}

.action-btn:hover {
  background: #f3f4f6;
}

.action-btn.primary {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.action-btn.danger {
  color: #dc2626;
}
</style>
```

## Integration

In `frontend/src/App.vue`:

```vue
<template>
  <div id="app">
    <SessionBanner />
    <router-view />
  </div>
</template>

<script setup>
import SessionBanner from '@/components/SessionBanner.vue'
</script>
```

## Checklist

- [ ] SessionBanner component created
- [ ] Shows active session info
- [ ] Minimized/expanded states work
- [ ] Progress bar updates
- [ ] All action buttons work
- [ ] Integrated in App.vue
- [ ] Visible on all pages
