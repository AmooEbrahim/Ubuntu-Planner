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
  if (s >= 80) return '#10b981'
  if (s >= 60) return '#3b82f6'
  if (s >= 40) return '#f59e0b'
  return '#ef4444'
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
  <div class="statistics-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Statistics</h1>
        <p class="page-subtitle">{{ dateRange.label }}</p>
      </div>
      <div class="time-range-selector">
        <button
          v-for="range in ['week', 'month', 'year']"
          :key="range"
          @click="changeTimeRange(range)"
          :class="['range-btn', { active: timeRange === range }]"
        >
          {{ range === 'week' ? 'Week' : range === 'month' ? 'Month' : 'Year' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span>{{ error }}</span>
      <button @click="loadStatistics" class="retry-btn">Retry</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading statistics...</p>
    </div>

    <div v-else-if="stats" class="statistics-content" :class="{ animating }">
      <div class="stats-overview">
        <div class="stat-card gradient-purple">
          <div class="stat-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_sessions }}</span>
            <span class="stat-label">Sessions</span>
          </div>
        </div>

        <div class="stat-card gradient-emerald">
          <div class="stat-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <path d="M12 2v20M2 12h20"></path>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatDuration(stats.total_minutes) }}</span>
            <span class="stat-label">Total Time</span>
          </div>
        </div>

        <div class="stat-card gradient-amber">
          <div class="stat-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
              <line x1="9" y1="9" x2="9.01" y2="9"></line>
              <line x1="15" y1="9" x2="15.01" y2="9"></line>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value" :style="{ color: satisfactionColor }">{{ stats.avg_satisfaction }}%</span>
            <span class="stat-label">Satisfaction</span>
          </div>
        </div>

        <div class="stat-card gradient-blue">
          <div class="stat-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ formatDuration(avgDailyMinutes) }}</span>
            <span class="stat-label">Daily Average</span>
          </div>
        </div>
      </div>

      <div class="daily-chart-card">
        <div class="chart-header">
          <div>
            <h3 class="chart-title">Daily Activity</h3>
            <span class="chart-subtitle">Minutes worked per day</span>
          </div>
          <div v-if="bestDay" class="chart-badge">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            Best: {{ formatDuration(bestDay.minutes) }}
          </div>
        </div>

        <div v-if="dailyActivity.length === 0" class="empty-chart">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
          </div>
          <p>No activity in this period</p>
        </div>

        <div v-else class="bar-chart">
          <div
            v-for="(day, index) in dailyActivity"
            :key="day.date"
            class="bar-item"
            :style="{ animationDelay: `${index * 40}ms` }"
          >
            <div class="bar-tooltip">
              <span class="tooltip-date">{{ formatDate(day.date) }}</span>
              <span class="tooltip-value">{{ formatDuration(day.total_minutes) }}</span>
            </div>
            <div class="bar-wrapper">
              <div
                class="bar-fill"
                :class="{ 'is-best': bestDay && day.date === bestDay.date }"
                :style="{ height: getBarHeight(day.total_minutes, maxDailyMinutes) }"
              ></div>
            </div>
            <div class="bar-label">{{ formatDate(day.date) }}</div>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <div>
              <h3 class="chart-title">Time by Project</h3>
              <span class="chart-subtitle">{{ formatDuration(totalProjectMinutes) }} across {{ projectStats.length }} projects</span>
            </div>
          </div>

          <div v-if="projectStats.length === 0" class="empty-chart">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <p>No project data</p>
          </div>

          <div v-else class="horizontal-chart">
            <div
              v-for="(project, index) in projectStats"
              :key="project.project_name"
              class="h-bar-item"
              :style="{ animationDelay: `${index * 60}ms` }"
            >
              <div class="h-bar-label">
                <div class="h-bar-dot" :style="{ backgroundColor: project.color }"></div>
                <span class="h-bar-name">{{ project.project_name }}</span>
              </div>
              <div class="h-bar-track">
                <div
                  class="h-bar-fill"
                  :style="{ width: getBarHeight(project.total_minutes, maxProjectMinutes), backgroundColor: project.color }"
                ></div>
              </div>
              <div class="h-bar-value">
                <span class="h-bar-duration">{{ formatDuration(project.total_minutes) }}</span>
                <span class="h-bar-pct">{{ getProjectPercentage(project.total_minutes) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <div>
              <h3 class="chart-title">Time by Tag</h3>
              <span class="chart-subtitle">{{ tagStats.length }} tags in this period</span>
            </div>
          </div>

          <div v-if="tagStats.length === 0" class="empty-chart">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                <line x1="7" y1="7" x2="7.01" y2="7"></line>
              </svg>
            </div>
            <p>No tag data</p>
          </div>

          <div v-else class="tags-list">
            <div
              v-for="(tag, index) in tagStats"
              :key="tag.tag_name"
              class="tag-item"
              :style="{ animationDelay: `${index * 50}ms` }"
            >
              <div class="tag-item-left">
                <div class="tag-dot" :style="{ backgroundColor: tag.color }"></div>
                <span class="tag-item-name">{{ tag.tag_name }}</span>
              </div>
              <div class="tag-item-track">
                <div
                  class="tag-item-fill"
                  :style="{ width: getBarHeight(tag.total_minutes, maxDailyMinutes * 3), backgroundColor: tag.color + '50' }"
                ></div>
              </div>
              <div class="tag-item-right">
                <span class="tag-item-duration">{{ formatDuration(tag.total_minutes) }}</span>
                <span class="tag-item-count">{{ tag.session_count }} sessions</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.statistics-page { max-width: 1280px; margin: 0 auto; padding: 2rem; --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.page-title { font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.025em; }
.page-subtitle { color: #64748b; margin: 0.25rem 0 0; font-size: 0.95rem; font-weight: 500; }

.time-range-selector { display: flex; background: #f1f5f9; border-radius: 10px; padding: 3px; }
.range-btn { padding: 0.5rem 1rem; border: none; background: transparent; color: #64748b; font-weight: 600; font-size: 0.85rem; cursor: pointer; border-radius: 8px; transition: all var(--transition); }
.range-btn:hover { color: #334155; }
.range-btn.active { background: white; color: #6366f1; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

.error-banner { display: flex; align-items: center; gap: 0.625rem; padding: 0.75rem 1rem; background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; color: #dc2626; font-size: 0.875rem; margin-bottom: 1.5rem; }
.retry-btn { margin-left: auto; padding: 0.375rem 0.75rem; background: white; border: 1px solid #fecaca; border-radius: 6px; color: #dc2626; font-size: 0.8rem; font-weight: 600; cursor: pointer; }
.retry-btn:hover { background: #fef2f2; }

.loading-state { display: flex; flex-direction: column; align-items: center; padding: 4rem 2rem; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #6366f1; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Stat Cards */
.stats-overview { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { position: relative; display: flex; align-items: center; gap: 1rem; padding: 1.25rem; border-radius: 16px; overflow: hidden; color: white; transition: transform var(--transition), box-shadow var(--transition); }
.stat-card::before { content: ''; position: absolute; inset: 0; opacity: 0.9; z-index: 0; }
.stat-card.gradient-purple::before { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
.stat-card.gradient-emerald::before { background: linear-gradient(135deg, #10b981, #059669); }
.stat-card.gradient-amber::before { background: linear-gradient(135deg, #f59e0b, #d97706); }
.stat-card.gradient-blue::before { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12); }
.stat-card > * { position: relative; z-index: 1; }

.stat-icon-wrap { display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; background: rgba(255, 255, 255, 0.2); border-radius: 12px; flex-shrink: 0; }
.stat-info { display: flex; flex-direction: column; gap: 0.125rem; }
.stat-value { font-size: 1.5rem; font-weight: 700; }
.stat-label { font-size: 0.8rem; opacity: 0.85; font-weight: 500; }

/* Daily Activity Chart - Full Width */
.daily-chart-card { background: white; border-radius: 16px; border: 1px solid #e2e8f0; padding: 1.5rem; margin-bottom: 1.5rem; }

.chart-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; gap: 1rem; }
.chart-title { font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0; }
.chart-subtitle { font-size: 0.8rem; color: #94a3b8; margin-top: 0.125rem; }

.chart-badge { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.3rem 0.625rem; background: #fef3c7; border-radius: 8px; font-size: 0.75rem; font-weight: 600; color: #d97706; flex-shrink: 0; }

.empty-chart { display: flex; flex-direction: column; align-items: center; padding: 3rem 1rem; text-align: center; color: #94a3b8; }
.empty-icon { width: 56px; height: 56px; background: #f1f5f9; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; }
.empty-icon svg { width: 24px; height: 24px; color: #cbd5e1; }
.empty-chart p { margin: 0; font-size: 0.9rem; }

.bar-chart { display: flex; align-items: flex-end; justify-content: space-between; gap: 6px; height: 240px; padding-top: 0.5rem; }
.bar-item { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; position: relative; }
.bar-item:hover .bar-tooltip { opacity: 1; transform: translateX(-50%) translateY(-4px); pointer-events: auto; }

.bar-tooltip { position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%) translateY(0); background: #0f172a; color: white; padding: 0.375rem 0.625rem; border-radius: 8px; font-size: 0.7rem; white-space: nowrap; opacity: 0; transition: all 0.2s ease; pointer-events: none; z-index: 10; }
.bar-tooltip::after { content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%); border: 4px solid transparent; border-top-color: #0f172a; }
.tooltip-date { display: block; opacity: 0.7; margin-bottom: 0.125rem; }
.tooltip-value { display: block; font-weight: 700; }

.bar-wrapper { width: 100%; height: 85%; display: flex; align-items: flex-end; }
.bar-fill { width: 100%; border-radius: 6px 6px 0 0; background: linear-gradient(180deg, #6366f1, #818cf8); transition: all 0.3s ease; min-height: 2px; }
.bar-fill.is-best { background: linear-gradient(180deg, #f59e0b, #fbbf24); }
.bar-fill:hover { opacity: 0.85; }
.bar-label { font-size: 0.65rem; color: #94a3b8; margin-top: 0.5rem; white-space: nowrap; }

/* Charts Grid */
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.chart-card { background: white; border-radius: 16px; border: 1px solid #e2e8f0; padding: 1.5rem; }

/* Horizontal Bars */
.horizontal-chart { display: flex; flex-direction: column; gap: 0.875rem; }
.h-bar-item { display: grid; grid-template-columns: 140px 1fr 90px; align-items: center; gap: 0.75rem; }
.h-bar-label { display: flex; align-items: center; gap: 0.5rem; min-width: 0; }
.h-bar-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.h-bar-name { font-size: 0.85rem; font-weight: 600; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.h-bar-track { height: 28px; background: #f1f5f9; border-radius: 8px; overflow: hidden; }
.h-bar-fill { height: 100%; border-radius: 8px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); min-width: 2px; }
.h-bar-value { display: flex; flex-direction: column; align-items: flex-end; gap: 0.125rem; }
.h-bar-duration { font-size: 0.85rem; font-weight: 600; color: #334155; }
.h-bar-pct { font-size: 0.7rem; color: #94a3b8; }

/* Tags List */
.tags-list { display: flex; flex-direction: column; gap: 0.625rem; }
.tag-item { display: grid; grid-template-columns: 120px 1fr 100px; align-items: center; gap: 0.75rem; }
.tag-item-left { display: flex; align-items: center; gap: 0.5rem; min-width: 0; }
.tag-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.tag-item-name { font-size: 0.85rem; font-weight: 600; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tag-item-track { height: 20px; background: #f1f5f9; border-radius: 6px; overflow: hidden; }
.tag-item-fill { height: 100%; border-radius: 6px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); min-width: 2px; }
.tag-item-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.125rem; }
.tag-item-duration { font-size: 0.85rem; font-weight: 600; color: #334155; }
.tag-item-count { font-size: 0.7rem; color: #94a3b8; }

/* Animations */
.statistics-content.animating .bar-fill,
.statistics-content.animating .h-bar-fill,
.statistics-content.animating .tag-item-fill { animation: barGrow 0.5s cubic-bezier(0.4, 0, 0.2, 1) both; }
@keyframes barGrow { from { transform: scaleY(0); } to { transform: scaleY(1); } }

@media (max-width: 1024px) { .stats-overview { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .statistics-page { padding: 1rem; }
  .page-header { flex-direction: column; gap: 1rem; }
  .stats-overview { grid-template-columns: 1fr 1fr; }
  .charts-grid { grid-template-columns: 1fr; }
  .h-bar-item { grid-template-columns: 1fr; gap: 0.375rem; }
  .h-bar-value { flex-direction: row; gap: 0.5rem; }
  .h-bar-pct { text-align: left; }
  .tag-item { grid-template-columns: 1fr; gap: 0.375rem; }
  .tag-item-right { flex-direction: row; gap: 0.5rem; }
}
@media (max-width: 480px) { .stats-overview { grid-template-columns: 1fr; } }
</style>
