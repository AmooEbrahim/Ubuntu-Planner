<script setup>
import { computed, onMounted, onBeforeUnmount, nextTick, ref, watch } from 'vue'
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

const hours = Array.from({ length: 24 }, (_, i) => i)
const sessionsAreaRef = ref(null)
const nowMinutes = ref(currentMinutesOfDay())
let nowTimer = null

const pxPerMinute = 1
const GUTTER_PX = 4
const SIDE_PAD_PX = 8

function currentMinutesOfDay() {
  const now = dayjs()
  return now.hour() * 60 + now.minute()
}

const isToday = computed(() => dayjs(props.date).isSame(dayjs(), 'day'))

function sessionRange(session) {
  const start = dayjs(session.start_time)
  const end = session.end_time ? dayjs(session.end_time) : dayjs()
  // Clamp to the displayed day so a session that ran across midnight still shows.
  const dayStart = dayjs(props.date).startOf('day')
  const dayEnd = dayjs(props.date).endOf('day')
  const effStart = start.isBefore(dayStart) ? dayStart : start
  const effEnd = end.isAfter(dayEnd) ? dayEnd : end
  const startMin = Math.max(0, (effStart.hour() * 60) + effStart.minute())
  const durationMin = Math.max(1, effEnd.diff(effStart, 'minute'))
  const endMin = Math.min(24 * 60, startMin + durationMin)
  return { startMin, endMin }
}

const layoutById = computed(() => {
  const items = props.sessions
    .map((s) => ({ session: s, ...sessionRange(s) }))
    .sort((a, b) => a.startMin - b.startMin || a.endMin - b.endMin)

  const result = new Map()
  let group = []
  let groupEnd = -1

  function flushGroup(g) {
    const columnsEnd = []
    const placed = []
    for (const entry of g) {
      let col = -1
      for (let i = 0; i < columnsEnd.length; i++) {
        if (columnsEnd[i] <= entry.startMin) { col = i; break }
      }
      if (col === -1) { col = columnsEnd.length; columnsEnd.push(0) }
      columnsEnd[col] = entry.endMin
      placed.push({ ...entry, col })
    }
    const total = columnsEnd.length
    for (const p of placed) {
      result.set(p.session.id, { column: p.col, columnsInGroup: total })
    }
  }

  for (const entry of items) {
    if (group.length === 0 || entry.startMin < groupEnd) {
      group.push(entry)
      groupEnd = Math.max(groupEnd, entry.endMin)
    } else {
      flushGroup(group)
      group = [entry]
      groupEnd = entry.endMin
    }
  }
  if (group.length > 0) flushGroup(group)
  return result
})

function getSessionStyle(session) {
  const { startMin, endMin } = sessionRange(session)
  const durationMin = endMin - startMin

  const topPx = startMin * pxPerMinute
  const heightPx = Math.max(28, durationMin * pxPerMinute)

  const layout = layoutById.value.get(session.id) || { column: 0, columnsInGroup: 1 }
  const cols = Math.max(1, layout.columnsInGroup)
  const widthPct = 100 / cols
  const leftPct = layout.column * widthPct

  return {
    top: `${topPx}px`,
    height: `${heightPx}px`,
    left: `calc(${leftPct}% + ${SIDE_PAD_PX}px)`,
    width: `calc(${widthPct}% - ${SIDE_PAD_PX * 2}px - ${(cols - 1) * GUTTER_PX / cols}px)`,
  }
}

function getDensity(session) {
  const { startMin, endMin } = sessionRange(session)
  const heightPx = Math.max(28, (endMin - startMin) * pxPerMinute)
  if (heightPx < 44) return 'tiny'    // single inline row
  if (heightPx < 75) return 'compact' // project + time + duration
  return 'full'                       // everything
}

function getSessionStatusColor(session) {
  if (!session.end_time) return '#10b981'
  const duration = session.actual_duration || 0
  if (duration > session.planned_duration) return '#f59e0b'
  return '#6b7280'
}

function formatTime(datetime) {
  return dayjs(datetime).format('HH:mm')
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

function handleHourClick(hour) {
  emit('start-session', hour)
}

function getActualDuration(session) {
  if (session.actual_duration) return session.actual_duration
  if (session.end_time) {
    const start = dayjs(session.start_time)
    const end = dayjs(session.end_time)
    return Math.floor(end.diff(start, 'minute'))
  }
  const start = dayjs(session.start_time)
  return Math.floor(dayjs().diff(start, 'minute'))
}

function getHourLabel(hour) {
  return `${String(hour).padStart(2, '0')}:00`
}

function scrollToInterestingHour() {
  const area = sessionsAreaRef.value
  if (!area) return
  let targetMinutes
  if (isToday.value) {
    targetMinutes = nowMinutes.value
  } else if (props.sessions.length > 0) {
    targetMinutes = Math.min(...props.sessions.map((s) => sessionRange(s).startMin))
  } else {
    targetMinutes = 8 * 60
  }
  area.scrollTop = Math.max(0, targetMinutes * pxPerMinute - 80)
}

onMounted(() => {
  nowTimer = setInterval(() => {
    nowMinutes.value = currentMinutesOfDay()
  }, 60_000)
  nextTick(scrollToInterestingHour)
})

onBeforeUnmount(() => {
  if (nowTimer) clearInterval(nowTimer)
})

watch(
  () => props.date.format('YYYY-MM-DD'),
  () => nextTick(scrollToInterestingHour)
)
</script>

<template>
  <div class="session-calendar">
    <div ref="sessionsAreaRef" class="timeline-scroll">
      <div class="timeline" :style="{ minHeight: `${24 * 60}px` }">
        <div class="time-labels">
          <div
            v-for="hour in hours"
            :key="hour"
            class="time-label"
            :style="{ top: `${hour * 60}px` }"
          >
            {{ getHourLabel(hour) }}
          </div>
        </div>

        <div
          class="sessions-container"
        >
        <div
          v-for="hour in hours"
          :key="hour"
          class="hour-slot"
          :style="{ top: `${hour * 60}px` }"
          @click="handleHourClick(hour)"
        ></div>

        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          :class="`density-${getDensity(session)}`"
          :style="{
            ...getSessionStyle(session),
            borderColor: getSessionStatusColor(session),
            backgroundColor: getSessionStatusColor(session) + '20',
          }"
          :title="`${session.project?.name || 'No Project'} · ${formatTime(session.start_time)}${session.end_time ? '–' + formatTime(session.end_time) : ' (active)'} · ${formatDuration(getActualDuration(session))}`"
          @click.stop="emit('view-details', session)"
        >
          <div class="session-headline">
            <span class="project-dot" :style="{ backgroundColor: session.project?.color || '#6b7280' }"></span>
            <span class="project-name-text" :style="{ color: session.project?.color || '#111827' }">
              {{ session.project?.name || 'No Project' }}
            </span>
            <span class="time-range">
              {{ formatTime(session.start_time) }}<template v-if="session.end_time">–{{ formatTime(session.end_time) }}</template><span v-else class="active-pill">● now</span>
            </span>
            <div class="session-actions">
              <button @click.stop="emit('edit', session)" class="action-btn edit-btn" title="Edit">✎</button>
              <button @click.stop="emit('delete', session)" class="action-btn delete-btn" title="Delete">×</button>
            </div>
          </div>

          <div v-if="getDensity(session) !== 'tiny'" class="session-meta">
            <span class="duration">{{ formatDuration(getActualDuration(session)) }}</span>
            <span class="planned">planned {{ formatDuration(session.planned_duration) }}</span>
            <span v-if="session.satisfaction_score && session.satisfaction_score > 0" class="satisfaction-pill">
              {{ session.satisfaction_score }}/100
            </span>
          </div>

          <div v-if="getDensity(session) === 'full' && session.tags && session.tags.length > 0" class="session-tags">
            <span
              v-for="tag in session.tags.slice(0, 3)"
              :key="tag.id"
              class="tag"
              :style="{ backgroundColor: tag.color + '30', color: tag.color }"
            >
              {{ tag.name }}
            </span>
            <span v-if="session.tags.length > 3" class="more-tags">+{{ session.tags.length - 3 }}</span>
          </div>
        </div>

        <div
          v-if="isToday"
          class="now-line"
          :style="{ top: `${nowMinutes * pxPerMinute}px` }"
          aria-hidden="true"
        >
          <div class="now-dot"></div>
          <div class="now-bar"></div>
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

.timeline-scroll {
  max-height: 800px;
  overflow-y: auto;
  overflow-x: hidden;
}

.timeline {
  display: flex;
  position: relative;
}

.time-labels {
  width: 70px;
  flex-shrink: 0;
  position: relative;
  border-right: 1px solid #e5e7eb;
  background: #fafbfc;
}

.time-label {
  position: absolute;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
  transform: translateY(-8px);
  padding: 0 0.5rem;
}

.sessions-container {
  flex: 1;
  position: relative;
}

.hour-slot {
  position: absolute;
  left: 0;
  right: 0;
  height: 60px;
  border-top: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background-color 0.2s;
}

.hour-slot:hover {
  background-color: #f9fafb;
}

.session-item {
  position: absolute;
  border-left: 4px solid;
  border-radius: 6px;
  padding: 4px 6px 4px 8px;
  cursor: pointer;
  transition: box-shadow 0.2s, z-index 0s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 2px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  z-index: 10;
  background-clip: padding-box;
}

.session-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 20;
}

.session-item.density-tiny {
  padding: 2px 6px 2px 8px;
  gap: 0;
}

.session-headline {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  position: relative;
  padding-right: 0;
}

.project-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.project-name-text {
  font-weight: 700;
  font-size: 0.82rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
  line-height: 1.25;
}

.time-range {
  font-size: 0.7rem;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.active-pill {
  margin-left: 4px;
  color: #10b981;
  font-size: 0.65rem;
}

.session-actions {
  position: absolute;
  right: 2px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 3px;
  opacity: 0;
  transition: opacity 0.15s ease;
  flex-shrink: 0;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.95) 25%);
  padding: 0 2px 0 18px;
  border-radius: 4px;
  pointer-events: none;
}

.session-item:hover .session-actions {
  opacity: 1;
  pointer-events: auto;
}

.action-btn {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  line-height: 1;
  transition: all 0.15s ease;
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

.session-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.7rem;
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-wrap: wrap;
  row-gap: 2px;
}

.duration {
  font-weight: 600;
  color: #0f172a;
}

.planned {
  color: #94a3b8;
  font-weight: 500;
}

.satisfaction-pill {
  background: rgba(99, 102, 241, 0.12);
  color: #4f46e5;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 999px;
  font-size: 0.65rem;
}

.session-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  margin-top: 2px;
}

.tag {
  font-size: 0.6rem;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 600;
  white-space: nowrap;
}

.more-tags {
  font-size: 0.6rem;
  color: #94a3b8;
  align-self: center;
}

.now-line {
  position: absolute;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  z-index: 50;
  pointer-events: none;
}

.now-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ef4444;
  margin-left: -5px;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.18);
  flex-shrink: 0;
}

.now-bar {
  flex: 1;
  height: 2px;
  background: #ef4444;
}

@media (max-width: 768px) {
  .time-labels { width: 50px; }
  .time-label { font-size: 0.65rem; }
}
</style>
