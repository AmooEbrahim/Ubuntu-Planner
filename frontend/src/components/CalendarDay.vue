<script setup>
import { computed, ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'

dayjs.extend(utc)

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

const emit = defineEmits(['click-slot', 'edit', 'delete', 'drag-end'])

const hours = Array.from({ length: 24 }, (_, i) => i)
const draggingId = ref(null)
const draggingItem = ref(null)
const dragMouseY = ref(0)
const dragSnappedMinutes = ref(0)
const planningAreaRef = ref(null)
const nowMinutes = ref(currentMinutesOfDay())
let nowTimer = null

const pxPerMinute = 1
const GUTTER_PX = 4
const SIDE_PAD_PX = 6

function currentMinutesOfDay() {
  const now = dayjs()
  return now.hour() * 60 + now.minute()
}

const isToday = computed(() => dayjs(props.date).isSame(dayjs(), 'day'))

function itemRange(item) {
  const start = dayjs.utc(item.scheduled_start).local()
  const end = dayjs.utc(item.scheduled_end).local()
  const startMin = Math.max(0, start.hour() * 60 + start.minute())
  const endMin = Math.min(24 * 60, Math.max(startMin + 1, startMin + end.diff(start, 'minute')))
  return { startMin, endMin }
}

const layoutById = computed(() => {
  const items = props.planning
    .map((p) => ({ item: p, ...itemRange(p) }))
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
      result.set(p.item.id, { column: p.col, columnsInGroup: total })
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

function getPlanningStyle(item) {
  const { startMin, endMin } = itemRange(item)
  const durationMinutes = endMin - startMin

  const topPx = startMin * pxPerMinute
  const heightPx = Math.max(28, durationMinutes * pxPerMinute)

  const layout = layoutById.value.get(item.id) || { column: 0, columnsInGroup: 1 }
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

function getProjectColor(item) {
  return item.project?.color || '#6366f1'
}

function getPriorityIndicator(item) {
  switch (item.priority) {
    case 'critical':
      return { color: '#ef4444', icon: '!!' }
    case 'medium':
      return { color: '#3b82f6', icon: '!' }
    default:
      return { color: '#94a3b8', icon: '' }
  }
}

function formatTimeShort(datetime) {
  return dayjs.utc(datetime).local().format('h:mm A')
}

function handleHourClick(hour) {
  const startTime = `${String(hour).padStart(2, '0')}:00`
  emit('click-slot', startTime)
}

function handleDragStart(event, item) {
  draggingId.value = item.id
  draggingItem.value = item
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', item.id)

  const ghost = event.target
  ghost.style.opacity = '0.4'
  setTimeout(() => {
    if (ghost) ghost.style.opacity = ''
  }, 0)
}

function handleDragOver(event) {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'

  if (!draggingItem.value || !planningAreaRef.value) return

  const rect = planningAreaRef.value.getBoundingClientRect()
  const scrollTop = planningAreaRef.value.scrollTop
  const y = event.clientY - rect.top + scrollTop

  dragMouseY.value = event.clientY

  const snappedMinutes = Math.round(y / pxPerMinute / 15) * 15
  dragSnappedMinutes.value = Math.max(0, Math.min(23 * 60 + 45, snappedMinutes))
}

function handleDrop(event) {
  event.preventDefault()
  if (!draggingId.value || !draggingItem.value) return

  const item = draggingItem.value
  const duration = dayjs.utc(item.scheduled_end).local().diff(dayjs.utc(item.scheduled_start).local(), 'minute')

  const newStartMinutes = dragSnappedMinutes.value
  const baseDate = dayjs().startOf('day')
  const newStart = baseDate.hour(Math.floor(newStartMinutes / 60)).minute(newStartMinutes % 60).second(0)
  const newEnd = newStart.add(duration, 'minute')

  emit('drag-end', {
    id: item.id,
    scheduled_start: newStart.toISOString(),
    scheduled_end: newEnd.toISOString(),
  })

  resetDrag()
}

function handleDragEnd() {
  resetDrag()
}

function resetDrag() {
  draggingId.value = null
  draggingItem.value = null
  dragMouseY.value = 0
  dragSnappedMinutes.value = 0
}

function getGhostBlockStyle() {
  const item = draggingItem.value
  if (!item) return {}

  const start = dayjs.utc(item.scheduled_start).local()
  const end = dayjs.utc(item.scheduled_end).local()
  const duration = end.diff(start, 'minute')

  const topPx = dragSnappedMinutes.value * pxPerMinute
  const heightPx = Math.max(28, duration * pxPerMinute)
  const color = getProjectColor(item)

  return {
    top: `${Math.max(0, topPx)}px`,
    height: `${heightPx}px`,
    backgroundColor: color + '35',
    borderLeftColor: color,
  }
}

function getGhostTime() {
  if (!draggingItem.value) return ''
  const baseDate = dayjs().startOf('day')
  const start = baseDate.hour(Math.floor(dragSnappedMinutes.value / 60)).minute(dragSnappedMinutes.value % 60)
  const duration = dayjs.utc(draggingItem.value.scheduled_end).local().diff(dayjs.utc(draggingItem.value.scheduled_start).local(), 'minute')
  const end = start.add(duration, 'minute')
  return `${start.format('h:mm A')} – ${end.format('h:mm A')}`
}

function getGhostLineTop() {
  return dragSnappedMinutes.value * pxPerMinute
}

function getHourLabel(hour) {
  if (hour === 0) return '12 AM'
  if (hour < 12) return `${hour} AM`
  if (hour === 12) return '12 PM'
  return `${hour - 12} PM`
}

function scrollToInterestingHour() {
  const area = planningAreaRef.value
  if (!area) return
  let targetMinutes
  if (isToday.value) {
    targetMinutes = nowMinutes.value
  } else if (props.planning.length > 0) {
    targetMinutes = Math.min(...props.planning.map((p) => itemRange(p).startMin))
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
  () => {
    nextTick(scrollToInterestingHour)
  }
)
</script>

<template>
  <div class="calendar-day glass-card overflow-hidden">
    <div ref="planningAreaRef" class="timeline-scroll">
      <div class="timeline-wrapper" :style="{ minHeight: `${24 * 60}px` }">
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
          class="planning-area"
          :class="{ 'is-drag-active': draggingId }"
          @dragover="handleDragOver"
          @drop="handleDrop"
        >
        <div
          v-for="hour in hours"
          :key="hour"
          class="hour-line"
          :style="{ top: `${hour * 60}px` }"
          @click="handleHourClick(hour)"
        >
          <div class="hour-line-inner"></div>
        </div>

        <div
          v-for="item in planning"
          :key="item.id"
          class="planning-block"
          :class="{ 'is-dragging': draggingId === item.id }"
          :style="{
            ...getPlanningStyle(item),
            backgroundColor: getProjectColor(item) + '22',
            borderLeftColor: getProjectColor(item),
          }"
          draggable="true"
          @dragstart="handleDragStart($event, item)"
          @dragend="handleDragEnd"
          @click.stop="emit('edit', item)"
        >
          <div class="block-accent" :style="{ backgroundColor: getProjectColor(item) }"></div>

          <div class="block-content">
            <div class="block-top-row">
              <span class="block-project" :style="{ color: getProjectColor(item) }">
                {{ item.project?.name || 'Unknown' }}
              </span>
              <div
                v-if="getPriorityIndicator(item).icon"
                class="priority-dot"
                :style="{ backgroundColor: getPriorityIndicator(item).color }"
                :title="item.priority"
              >
                {{ getPriorityIndicator(item).icon }}
              </div>
            </div>

            <div class="block-time">
              {{ formatTimeShort(item.scheduled_start) }} – {{ formatTimeShort(item.scheduled_end) }}
            </div>

            <div v-if="item.description" class="block-desc">
              {{ item.description }}
            </div>

            <div v-if="item.tags && item.tags.length > 0" class="block-tags">
              <span
                v-for="tag in item.tags"
                :key="tag.id"
                class="block-tag"
                :style="{ backgroundColor: tag.color + '20', color: tag.color }"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>

          <div class="block-actions">
            <button
              type="button"
              class="block-action-btn edit"
              @click.stop="emit('edit', item)"
              title="Edit"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button
              type="button"
              class="block-action-btn delete"
              @click.stop="emit('delete', item)"
              title="Delete"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        </div>

        <div
          v-if="draggingId && draggingItem"
          class="ghost-block"
          :style="getGhostBlockStyle()"
        >
          <div class="ghost-accent" :style="{ backgroundColor: getProjectColor(draggingItem) }"></div>
          <div class="ghost-content">
            <span class="ghost-project" :style="{ color: getProjectColor(draggingItem) }">
              {{ draggingItem.project?.name || 'Unknown' }}
            </span>
            <span class="ghost-time">{{ getGhostTime() }}</span>
          </div>
        </div>

        <div
          v-if="draggingId"
          class="drag-drop-line"
          :style="{ top: `${getGhostLineTop()}px` }"
        >
          <div class="drop-line-dot"></div>
          <div class="drop-line"></div>
          <div class="drop-line-label" v-if="draggingItem">
            {{ getGhostTime() }}
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
.timeline-scroll {
  max-height: 800px;
  overflow-y: auto;
  overflow-x: hidden;
}

.timeline-wrapper {
  display: flex;
  position: relative;
}

.time-labels {
  width: 70px;
  flex-shrink: 0;
  position: relative;
  border-right: 1px solid rgb(var(--glass-divider) / var(--glass-divider-alpha));
  background: rgb(var(--glass-bg) / 0.25);
}

.time-label {
  position: absolute;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 0.7rem;
  font-weight: 500;
  color: rgb(var(--fg-subtle));
  transform: translateY(-8px);
  padding: 0 0.5rem;
}

.planning-area {
  flex: 1;
  position: relative;
}

.planning-area.is-drag-active {
  background: rgb(var(--accent) / 0.04);
}

.hour-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 60px;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.hour-line:hover {
  background: rgb(var(--accent) / 0.05);
}

.planning-area.is-drag-active .hour-line:hover {
  background: rgb(var(--accent) / 0.08);
}

.hour-line-inner {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  border-top: 1px solid rgb(var(--glass-divider) / var(--glass-divider-alpha));
}

.planning-block {
  position: absolute;
  border-left: 3px solid;
  border-radius: 10px;
  overflow: hidden;
  cursor: grab;
  transition: box-shadow 0.2s ease, transform 0.15s ease;
  z-index: 10;
  background-clip: padding-box;
  backdrop-filter: blur(8px);
}

.planning-block:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 20;
}

.planning-block:active {
  cursor: grabbing;
}

.planning-block.is-dragging {
  opacity: 0.3;
  transform: scale(0.98);
  border-style: dashed;
}

.block-accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  border-radius: 8px 0 0 8px;
}

.block-content {
  padding: 6px 8px 6px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
  height: 100%;
}

.block-top-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.block-project {
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.priority-dot {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.55rem;
  font-weight: 800;
  color: white;
  flex-shrink: 0;
}

.block-time {
  font-size: 0.7rem;
  color: rgb(var(--fg-muted));
  font-weight: 500;
  white-space: nowrap;
}

.block-desc {
  font-size: 0.7rem;
  color: rgb(var(--fg-subtle));
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.block-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  margin-top: 2px;
}

.block-tag {
  font-size: 0.6rem;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: 600;
  white-space: nowrap;
}

.block-actions {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.planning-block:hover .block-actions {
  opacity: 1;
}

.block-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: none;
  background: rgb(var(--glass-bg) / 0.85);
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  transition: all 0.15s ease;
  backdrop-filter: blur(6px);
}

.block-action-btn.edit {
  color: rgb(var(--accent));
}

.block-action-btn.edit:hover {
  background: rgb(var(--accent));
  color: white;
}

.block-action-btn.delete {
  color: rgb(var(--danger));
}

.block-action-btn.delete:hover {
  background: rgb(var(--danger));
  color: white;
}

.ghost-block {
  position: absolute;
  left: 6px;
  right: 6px;
  border-left: 3px solid;
  border-radius: 10px;
  overflow: hidden;
  z-index: 100;
  pointer-events: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: ghostPulse 1.5s ease-in-out infinite;
  backdrop-filter: blur(8px);
}

@keyframes ghostPulse {
  0%, 100% { opacity: 0.85; }
  50% { opacity: 1; }
}

.ghost-accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  border-radius: 8px 0 0 8px;
}

.ghost-content {
  padding: 4px 8px 4px 10px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.ghost-project {
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ghost-time {
  font-size: 0.65rem;
  color: rgb(var(--fg-muted));
  font-weight: 500;
}

.drag-drop-line {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 90;
  pointer-events: none;
  display: flex;
  align-items: center;
}

.drop-line-dot {
  width: 10px;
  height: 10px;
  background: rgb(var(--accent));
  border-radius: 50%;
  margin-left: 65px;
  flex-shrink: 0;
  box-shadow: 0 0 0 4px rgb(var(--accent) / 0.2);
}

.drop-line {
  flex: 1;
  height: 2px;
  background: repeating-linear-gradient(
    90deg,
    rgb(var(--accent)) 0px,
    rgb(var(--accent)) 6px,
    transparent 6px,
    transparent 10px
  );
}

.drop-line-label {
  position: absolute;
  right: 12px;
  background: rgb(var(--accent));
  color: white;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgb(var(--accent) / 0.3);
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
  background: rgb(var(--danger));
  margin-left: -5px;
  box-shadow: 0 0 0 3px rgb(var(--danger) / 0.18);
  flex-shrink: 0;
}

.now-bar {
  flex: 1;
  height: 2px;
  background: rgb(var(--danger));
}

@media (max-width: 768px) {
  .time-labels {
    width: 50px;
  }

  .time-label {
    font-size: 0.6rem;
  }

  .drop-line-dot {
    margin-left: 45px;
  }
}
</style>
