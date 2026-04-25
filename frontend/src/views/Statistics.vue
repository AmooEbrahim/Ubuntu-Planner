<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import dayjs from 'dayjs'

const timeRange = ref('week')
const loading = ref(false)
const error = ref('')
const animating = ref(false)

const stats = ref(null)
const projectStats = ref([])
const dailyActivity = ref([])
const tagStats = ref([])

const dateRange = computed(() => {
  const endDate = dayjs()
  let startDate
  switch (timeRange.value) {
    case 'week': startDate = endDate.subtract(7, 'day'); break
    case 'month': startDate = endDate.subtract(30, 'day'); break
    case 'year': startDate = endDate.subtract(365, 'day'); break
  }
  return {
    start: startDate,
    end: endDate,
    startStr: startDate.format('YYYY-MM-DD'),
    endStr: endDate.format('YYYY-MM-DD'),
    label: `${startDate.format('MMM D')} – ${endDate.format('MMM D, YYYY')}`
  }
})

const maxDailyMinutes = computed(() => {
  if (dailyActivity.value.length === 0) return 0
  return Math.max(...dailyActivity.value.map(d => d.total_minutes))
})

const maxProjectMinutes = computed(() => {
  if (projectStats.value.length === 0) return 0
  return Math.max(...projectStats.value.map(p => p.total_minutes))
})

const totalProjectMinutes = computed(() => {
  return projectStats.value.reduce((sum, p) => sum + p.total_minutes, 0)
})

const avgDailyMinutes = computed(() => {
  if (dailyActivity.value.length === 0) return 0
  return Math.round(dailyActivity.value.reduce((sum, d) => sum + d.total_minutes, 0) / dailyActivity.value.length)
})

const bestDay = computed(() => {
  if (dailyActivity.value.length === 0) return null
  const best = dailyActivity.value.reduce((a, b) => a.total_minutes > b.total_minutes ? a : b)
  return { date: best.date, minutes: best.total_minutes }
})

const satisfactionColor = computed(() => {
  const s = stats.value?.avg_satisfaction || 0
  if (s >= 80) return 'rgb(var(--success))'
  if (s >= 60) return 'rgb(var(--info))'
  if (s >= 40) return 'rgb(var(--warning))'
  return 'rgb(var(--danger))'
})

onMounted(async () => { await loadStatistics() })

async function loadStatistics() {
  animating.value = true
  loading.value = true
  error.value = ''
  try {
    const params = { start_date: dateRange.value.startStr, end_date: dateRange.value.endStr }
    const [overview, byProject, daily, byTag] = await Promise.all([
      api.get('/api/statistics/overview', { params }),
      api.get('/api/statistics/by-project', { params }),
      api.get('/api/statistics/daily-activity', { params }),
      api.get('/api/statistics/by-tag', { params })
    ])
    stats.value = overview.data
    projectStats.value = byProject.data
    dailyActivity.value = daily.data
    tagStats.value = byTag.data
  } catch (err) {
    error.value = 'Failed to load statistics'
    console.error(err)
  } finally {
    loading.value = false
    setTimeout(() => { animating.value = false }, 400)
  }
}

function formatDuration(minutes) {
  if (!minutes || minutes < 0) return '0m'
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

function formatDate(dateStr) {
  return dayjs(dateStr).format('MMM D')
}

function getBarHeight(value, max) {
  if (max === 0) return '0%'
  return `${(value / max) * 100}%`
}

function getProjectPercentage(minutes) {
  if (totalProjectMinutes.value === 0) return '0%'
  return `${Math.round((minutes / totalProjectMinutes.value) * 100)}%`
}

async function changeTimeRange(range) {
  if (range === timeRange.value) return
  timeRange.value = range
  await loadStatistics()
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-5">
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h1 class="page-title">Statistics</h1>
        <p class="page-subtitle">{{ dateRange.label }}</p>
      </div>
      <div class="glass-inset p-1 inline-flex gap-0.5">
        <button
          v-for="range in ['week', 'month', 'year']"
          :key="range"
          @click="changeTimeRange(range)"
          class="px-4 py-1.5 rounded-lg text-sm font-semibold transition-all"
          :class="timeRange === range
            ? 'bg-accent text-white shadow-sm shadow-accent/30'
            : 'text-fg-muted hover:text-fg'"
        >
          {{ range === 'week' ? 'Week' : range === 'month' ? 'Month' : 'Year' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="glass-card border-l-4 border-danger/60 bg-danger/5 flex items-center gap-2 px-4 py-3 text-danger text-sm">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" class="flex-shrink-0">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span class="flex-1">{{ error }}</span>
      <button @click="loadStatistics" class="btn btn-secondary btn-sm">Retry</button>
    </div>

    <div v-if="loading" class="glass-card flex flex-col items-center justify-center py-16 px-6 text-muted">
      <div class="spinner mb-4"></div>
      <p>Loading statistics...</p>
    </div>

    <div v-else-if="stats" :class="{ animating }" class="space-y-5">
      <!-- Overview cards -->
      <div class="grid gap-4" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));">
        <div class="glass-card p-5 flex items-center gap-3">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-accent/15 text-accent flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="flex flex-col">
            <span class="text-2xl font-bold text-fg leading-none">{{ stats.total_sessions }}</span>
            <span class="text-xs text-muted uppercase tracking-wide mt-1">Sessions</span>
          </div>
        </div>

        <div class="glass-card p-5 flex items-center gap-3">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-success/15 text-success flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
              <path d="M12 2v20M2 12h20"></path>
            </svg>
          </div>
          <div class="flex flex-col">
            <span class="text-2xl font-bold text-fg leading-none">{{ formatDuration(stats.total_minutes) }}</span>
            <span class="text-xs text-muted uppercase tracking-wide mt-1">Total Time</span>
          </div>
        </div>

        <div class="glass-card p-5 flex items-center gap-3">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-warning/15 text-warning flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
              <line x1="9" y1="9" x2="9.01" y2="9"></line>
              <line x1="15" y1="9" x2="15.01" y2="9"></line>
            </svg>
          </div>
          <div class="flex flex-col">
            <span class="text-2xl font-bold leading-none" :style="{ color: satisfactionColor }">{{ stats.avg_satisfaction }}%</span>
            <span class="text-xs text-muted uppercase tracking-wide mt-1">Satisfaction</span>
          </div>
        </div>

        <div class="glass-card p-5 flex items-center gap-3">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-info/15 text-info flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
          </div>
          <div class="flex flex-col">
            <span class="text-2xl font-bold text-fg leading-none">{{ formatDuration(avgDailyMinutes) }}</span>
            <span class="text-xs text-muted uppercase tracking-wide mt-1">Daily Average</span>
          </div>
        </div>
      </div>

      <!-- Daily activity -->
      <div class="glass-card p-6">
        <div class="flex justify-between items-start gap-4 mb-5">
          <div>
            <h3 class="section-title">Daily Activity</h3>
            <span class="text-xs text-subtle mt-0.5 block">Minutes worked per day</span>
          </div>
          <div v-if="bestDay" class="badge badge-warning">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            Best: {{ formatDuration(bestDay.minutes) }}
          </div>
        </div>

        <div v-if="dailyActivity.length === 0" class="flex flex-col items-center py-12 px-4 text-center text-fg-subtle">
          <div class="w-14 h-14 rounded-full bg-fg-subtle/15 flex items-center justify-center mb-4">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="24" height="24">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
          </div>
          <p class="text-sm">No activity in this period</p>
        </div>

        <div v-else class="bar-chart flex items-end justify-between gap-1.5 h-60 pt-2">
          <div
            v-for="(day, index) in dailyActivity"
            :key="day.date"
            class="bar-item flex-1 flex flex-col items-center h-full relative group"
            :style="{ animationDelay: `${index * 40}ms` }"
          >
            <div class="absolute bottom-full mb-2 px-2 py-1 rounded-lg bg-fg text-[10px] font-semibold text-white opacity-0 group-hover:opacity-100 transition-all whitespace-nowrap pointer-events-none z-10" style="left: 50%; transform: translateX(-50%);">
              <span class="block opacity-70">{{ formatDate(day.date) }}</span>
              <span class="block">{{ formatDuration(day.total_minutes) }}</span>
            </div>
            <div class="w-full h-[85%] flex items-end">
              <div
                class="w-full rounded-t-md transition-[height] duration-300"
                :class="bestDay && day.date === bestDay.date
                  ? 'bg-gradient-to-b from-warning to-amber-300'
                  : 'bg-gradient-to-b from-accent to-accent-hover'"
                :style="{ height: getBarHeight(day.total_minutes, maxDailyMinutes), minHeight: '2px' }"
              ></div>
            </div>
            <div class="text-[10px] text-fg-subtle mt-2 whitespace-nowrap">{{ formatDate(day.date) }}</div>
          </div>
        </div>
      </div>

      <!-- Project + Tag side-by-side -->
      <div class="grid gap-5 lg:grid-cols-2">
        <div class="glass-card p-6">
          <div class="flex justify-between items-start gap-4 mb-5">
            <div>
              <h3 class="section-title">Time by Project</h3>
              <span class="text-xs text-subtle mt-0.5 block">{{ formatDuration(totalProjectMinutes) }} across {{ projectStats.length }} projects</span>
            </div>
          </div>

          <div v-if="projectStats.length === 0" class="flex flex-col items-center py-12 px-4 text-center text-fg-subtle">
            <div class="w-14 h-14 rounded-full bg-fg-subtle/15 flex items-center justify-center mb-4">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="24" height="24">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <p class="text-sm">No project data</p>
          </div>

          <div v-else class="flex flex-col gap-3.5">
            <div
              v-for="(project, index) in projectStats"
              :key="project.project_name"
              class="grid items-center gap-3"
              style="grid-template-columns: 140px 1fr 90px;"
              :style="{ animationDelay: `${index * 60}ms` }"
            >
              <div class="flex items-center gap-2 min-w-0">
                <div class="w-2 h-2 rounded-full flex-shrink-0" :style="{ backgroundColor: project.color }"></div>
                <span class="text-sm font-semibold text-fg truncate">{{ project.project_name }}</span>
              </div>
              <div class="h-7 rounded-lg bg-fg-subtle/15 overflow-hidden">
                <div
                  class="h-full rounded-lg transition-[width] duration-700"
                  :style="{ width: getBarHeight(project.total_minutes, maxProjectMinutes), backgroundColor: project.color, minWidth: '2px' }"
                ></div>
              </div>
              <div class="flex flex-col items-end gap-0.5">
                <span class="text-sm font-semibold text-fg">{{ formatDuration(project.total_minutes) }}</span>
                <span class="text-[10px] text-fg-subtle">{{ getProjectPercentage(project.total_minutes) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex justify-between items-start gap-4 mb-5">
            <div>
              <h3 class="section-title">Time by Tag</h3>
              <span class="text-xs text-subtle mt-0.5 block">{{ tagStats.length }} tags in this period</span>
            </div>
          </div>

          <div v-if="tagStats.length === 0" class="flex flex-col items-center py-12 px-4 text-center text-fg-subtle">
            <div class="w-14 h-14 rounded-full bg-fg-subtle/15 flex items-center justify-center mb-4">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="24" height="24">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                <line x1="7" y1="7" x2="7.01" y2="7"></line>
              </svg>
            </div>
            <p class="text-sm">No tag data</p>
          </div>

          <div v-else class="flex flex-col gap-2.5">
            <div
              v-for="(tag, index) in tagStats"
              :key="tag.tag_name"
              class="grid items-center gap-3"
              style="grid-template-columns: 120px 1fr 100px;"
              :style="{ animationDelay: `${index * 50}ms` }"
            >
              <div class="flex items-center gap-2 min-w-0">
                <div class="w-2 h-2 rounded-full flex-shrink-0" :style="{ backgroundColor: tag.color }"></div>
                <span class="text-sm font-semibold text-fg truncate">{{ tag.tag_name }}</span>
              </div>
              <div class="h-5 rounded-md bg-fg-subtle/15 overflow-hidden">
                <div
                  class="h-full rounded-md transition-[width] duration-700"
                  :style="{ width: getBarHeight(tag.total_minutes, maxDailyMinutes * 3), backgroundColor: tag.color + '50', minWidth: '2px' }"
                ></div>
              </div>
              <div class="flex flex-col items-end gap-0.5">
                <span class="text-sm font-semibold text-fg">{{ formatDuration(tag.total_minutes) }}</span>
                <span class="text-[10px] text-fg-subtle">{{ tag.session_count }} sessions</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animating .bar-item > div:nth-child(2) > div,
.animating .grid > div:nth-child(2) > div {
  animation: barGrow 0.5s cubic-bezier(0.4, 0, 0.2, 1) both;
  transform-origin: bottom;
}
@keyframes barGrow {
  from { transform: scaleY(0); }
  to { transform: scaleY(1); }
}
</style>
