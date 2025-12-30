<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  date: {
    type: Object,
    required: true,
  },
  planning: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['click-slot', 'edit', 'delete'])

// Generate hours from 0 to 23
const hours = Array.from({ length: 24 }, (_, i) => i)

// Helper to get planning items for a specific hour
function getPlanningForHour(hour) {
  return props.planning.filter((p) => {
    const startHour = dayjs(p.scheduled_start).hour()
    const endHour = dayjs(p.scheduled_end).hour()
    const endMinute = dayjs(p.scheduled_end).minute()

    // Include if planning starts in this hour or spans across it
    return (
      startHour === hour ||
      (startHour < hour && (endHour > hour || (endHour === hour && endMinute > 0)))
    )
  })
}

// Calculate position and height for planning item
function getPlanningStyle(planning) {
  const start = dayjs(planning.scheduled_start)
  const end = dayjs(planning.scheduled_end)

  const startHour = start.hour()
  const startMinute = start.minute()
  const endHour = end.hour()
  const endMinute = end.minute()

  // Calculate position as percentage from start of day
  const topPercent = ((startHour * 60 + startMinute) / (24 * 60)) * 100

  // Calculate height as percentage of day
  const durationMinutes = end.diff(start, 'minute')
  const heightPercent = (durationMinutes / (24 * 60)) * 100

  return {
    top: `${topPercent}%`,
    height: `${heightPercent}%`,
    minHeight: '30px', // Ensure minimum visibility
  }
}

// Get priority color
function getPriorityColor(priority) {
  switch (priority) {
    case 'low':
      return '#6b7280'
    case 'medium':
      return '#3b82f6'
    case 'critical':
      return '#ef4444'
    default:
      return '#3b82f6'
  }
}

// Format time
function formatTime(datetime) {
  return dayjs(datetime).format('HH:mm')
}

// Handle hour click to create planning
function handleHourClick(hour) {
  const startTime = `${String(hour).padStart(2, '0')}:00`
  emit('click-slot', startTime)
}

// Calculate if planning should be displayed in this hour slot
function shouldDisplayInHour(planning, hour) {
  const startHour = dayjs(planning.scheduled_start).hour()
  return startHour === hour
}
</script>

<template>
  <div class="calendar-day">
    <div class="timeline">
      <div class="time-labels">
        <div v-for="hour in hours" :key="hour" class="time-label">
          {{ String(hour).padStart(2, '0') }}:00
        </div>
      </div>

      <div class="planning-container">
        <div
          v-for="hour in hours"
          :key="hour"
          class="hour-slot"
          @click="handleHourClick(hour)"
        ></div>

        <!-- Planning items positioned absolutely -->
        <div
          v-for="item in planning"
          :key="item.id"
          class="planning-item"
          :style="{
            ...getPlanningStyle(item),
            borderColor: getPriorityColor(item.priority),
            backgroundColor: getPriorityColor(item.priority) + '20',
          }"
          @click.stop
        >
          <div class="planning-header" :style="{ borderColor: getPriorityColor(item.priority) }">
            <span class="planning-time">
              {{ formatTime(item.scheduled_start) }} - {{ formatTime(item.scheduled_end) }}
            </span>
            <div class="planning-actions">
              <button @click="emit('edit', item)" class="action-btn edit-btn" title="Edit">✎</button>
              <button @click="emit('delete', item)" class="action-btn delete-btn" title="Delete">
                ×
              </button>
            </div>
          </div>
          <div class="planning-content">
            <div class="planning-project" :style="{ color: item.project.color }">
              {{ item.project.name }}
            </div>
            <div v-if="item.description" class="planning-description">
              {{ item.description }}
            </div>
            <div v-if="item.tags && item.tags.length > 0" class="planning-tags">
              <span
                v-for="tag in item.tags"
                :key="tag.id"
                class="tag"
                :style="{ backgroundColor: tag.color }"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-day {
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

.planning-container {
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

.planning-item {
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

.planning-item:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
  transform: translateX(2px);
}

.planning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  padding-bottom: 4px;
  border-bottom: 1px solid;
  border-color: inherit;
}

.planning-time {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
}

.planning-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.planning-item:hover .planning-actions {
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

.planning-content {
  flex: 1;
  overflow: hidden;
}

.planning-project {
  font-weight: 700;
  font-size: 0.9rem;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.planning-description {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.planning-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.tag {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 3px;
  color: white;
  font-weight: 500;
}
</style>
