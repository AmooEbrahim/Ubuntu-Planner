<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  date: {
    type: Object,
    required: true,
  },
  sessions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['edit', 'delete', 'start-session', 'view-details'])

// Generate hours from 0 to 23
const hours = Array.from({ length: 24 }, (_, i) => i)

// Calculate position and height for session item
function getSessionStyle(session) {
  const start = dayjs(session.start_time)
  const end = session.end_time ? dayjs(session.end_time) : dayjs()

  const startHour = start.hour()
  const startMinute = start.minute()

  // Calculate position as percentage from start of day
  const topPercent = ((startHour * 60 + startMinute) / (24 * 60)) * 100

  // Calculate height as percentage of day
  const durationMinutes = end.diff(start, 'minute')
  const heightPercent = (durationMinutes / (24 * 60)) * 100

  return {
    top: `${topPercent}%`,
    height: `${Math.max(heightPercent, 2.08)}%`, // Minimum 30px (2.08% of 1440px)
    minHeight: '30px',
  }
}

// Get session status color
function getSessionStatusColor(session) {
  if (!session.end_time) {
    return '#10b981' // Active - green
  }
  const duration = session.actual_duration || 0
  if (duration > session.planned_duration) {
    return '#f59e0b' // Overtime - orange
  }
  return '#6b7280' // Completed - gray
}

// Format time
function formatTime(datetime) {
  return dayjs(datetime).format('HH:mm')
}

// Format duration
function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

// Handle hour click to start session
function handleHourClick(hour) {
  emit('start-session', hour)
}

// Get actual duration
function getActualDuration(session) {
  if (session.actual_duration) return session.actual_duration
  if (session.end_time) {
    const start = dayjs(session.start_time)
    const end = dayjs(session.end_time)
    return Math.floor(end.diff(start, 'minute'))
  }
  // For active sessions
  const start = dayjs(session.start_time)
  const now = dayjs()
  return Math.floor(now.diff(start, 'minute'))
}
</script>

<template>
  <div class="session-calendar">
    <div class="timeline">
      <div class="time-labels">
        <div v-for="hour in hours" :key="hour" class="time-label">
          {{ String(hour).padStart(2, '0') }}:00
        </div>
      </div>

      <div class="sessions-container">
        <div
          v-for="hour in hours"
          :key="hour"
          class="hour-slot"
          @click="handleHourClick(hour)"
        ></div>

        <!-- Session items positioned absolutely -->
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          :style="{
            ...getSessionStyle(session),
            borderColor: getSessionStatusColor(session),
            backgroundColor: getSessionStatusColor(session) + '20',
          }"
          @click.stop="emit('view-details', session)"
        >
          <div class="session-header">
            <div class="session-time-range">
              <span class="time-start">{{ formatTime(session.start_time) }}</span>
              <span v-if="session.end_time" class="time-end">- {{ formatTime(session.end_time) }}</span>
              <span v-else class="active-indicator">● Active</span>
            </div>
            <div class="session-actions">
              <button @click.stop="emit('edit', session)" class="action-btn edit-btn" title="Edit">✎</button>
              <button @click.stop="emit('delete', session)" class="action-btn delete-btn" title="Delete">×</button>
            </div>
          </div>

          <div class="session-content">
            <!-- Project Name - Always Visible -->
            <div class="session-project">
              <span class="project-dot" :style="{ backgroundColor: session.project?.color || '#6b7280' }"></span>
              <span class="project-name-text" :style="{ color: session.project?.color || '#111827' }">
                {{ session.project?.name || 'No Project' }}
              </span>
            </div>

            <!-- Duration Info -->
            <div class="session-duration-info">
              <span class="duration">{{ formatDuration(getActualDuration(session)) }}</span>
              <span class="planned">({{ formatDuration(session.planned_duration) }})</span>
            </div>

            <!-- Tags (only show if space allows) -->
            <div v-if="session.tags && session.tags.length > 0" class="session-tags">
              <span
                v-for="tag in session.tags.slice(0, 2)"
                :key="tag.id"
                class="tag"
                :style="{ backgroundColor: tag.color }"
              >
                {{ tag.name }}
              </span>
              <span v-if="session.tags.length > 2" class="more-tags">+{{ session.tags.length - 2 }}</span>
            </div>

            <!-- Satisfaction (only show if space allows) -->
            <div v-if="session.satisfaction_score && session.satisfaction_score > 0" class="session-satisfaction">
              <span class="satisfaction-value">{{ session.satisfaction_score }}/100</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.session-calendar {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.timeline {
  display: flex;
  position: relative;
}

.time-labels {
  width: 80px;
  flex-shrink: 0;
  border-right: 2px solid #e5e7eb;
}

.time-label {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: #6b7280;
  border-bottom: 1px solid #f3f4f6;
}

.sessions-container {
  flex: 1;
  position: relative;
  min-height: calc(24 * 60px);
}

.hour-slot {
  height: 60px;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background-color 0.2s;
}

.hour-slot:hover {
  background-color: #f9fafb;
}

.session-item {
  position: absolute;
  left: 8px;
  right: 8px;
  border-left: 4px solid;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.session-item:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
  transform: translateX(2px);
  z-index: 10;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.session-time-range {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
}

.time-start {
  color: #111827;
}

.time-end {
  color: #6b7280;
}

.active-indicator {
  color: #10b981;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  gap: 2px;
}

.session-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.action-btn {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 3px;
  cursor: pointer;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.edit-btn:hover {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.delete-btn:hover {
  background-color: #ef4444;
  color: white;
  border-color: #ef4444;
}

.session-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.session-project {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.project-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.project-name-text {
  font-weight: 700;
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.session-duration-info {
  font-size: 0.75rem;
  color: #374151;
}

.duration {
  font-weight: 600;
}

.planned {
  color: #9ca3af;
  margin-left: 4px;
}

.session-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 3px;
  color: white;
  font-weight: 500;
}

.more-tags {
  font-size: 0.65rem;
  color: #9ca3af;
}

.session-satisfaction {
  font-size: 0.7rem;
  color: #6b7280;
}

.satisfaction-value {
  font-weight: 600;
  color: #9ca3af;
}
</style>
