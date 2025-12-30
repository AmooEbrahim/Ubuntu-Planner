<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import dayjs from 'dayjs'

const timeRange = ref('month') // week, month, year
const loading = ref(false)
const error = ref('')

const stats = ref(null)
const projectStats = ref([])
const dailyActivity = ref([])
const tagStats = ref([])

const dateRange = computed(() => {
  const endDate = dayjs()
  let startDate

  switch (timeRange.value) {
    case 'week':
      startDate = endDate.subtract(7, 'day')
      break
    case 'month':
      startDate = endDate.subtract(30, 'day')
      break
    case 'year':
      startDate = endDate.subtract(365, 'day')
      break
  }

  return {
    start: startDate.format('YYYY-MM-DD'),
    end: endDate.format('YYYY-MM-DD')
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

onMounted(async () => {
  await loadStatistics()
})

async function loadStatistics() {
  loading.value = true
  error.value = ''
  try {
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end
    }

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
  }
}

function formatDuration(minutes) {
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

async function changeTimeRange(range) {
  timeRange.value = range
  await loadStatistics()
}
</script>

<template>
  <div class="statistics-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Statistics</h1>
        <p class="page-subtitle">Analytics and insights about your work</p>
      </div>

      <div class="time-range-selector">
        <button
          v-for="range in ['week', 'month', 'year']"
          :key="range"
          @click="changeTimeRange(range)"
          :class="{ active: timeRange === range }"
          class="range-btn"
        >
          {{ range.charAt(0).toUpperCase() + range.slice(1) }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">
      {{ error }}
      <button @click="loadStatistics" class="retry-btn">Retry</button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading statistics...</p>
    </div>

    <div v-else-if="stats" class="statistics-content">
      <!-- Overview Stats -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_sessions }}</div>
          <div class="stat-label">Total Sessions</div>
        </div>

        <div class="stat-card">
          <div class="stat-value">{{ formatDuration(stats.total_minutes) }}</div>
          <div class="stat-label">Total Time</div>
        </div>

        <div class="stat-card">
          <div class="stat-value">{{ stats.avg_satisfaction }}%</div>
          <div class="stat-label">Avg Satisfaction</div>
        </div>
      </div>

      <!-- Charts Grid -->
      <div class="charts-grid">
        <!-- Daily Activity Chart -->
        <div class="chart-card">
          <h3 class="chart-title">Daily Activity</h3>

          <div v-if="dailyActivity.length === 0" class="empty-chart">
            No activity in this period
          </div>

          <div v-else class="bar-chart">
            <div
              v-for="day in dailyActivity"
              :key="day.date"
              class="bar-item"
              :title="`${formatDate(day.date)}: ${formatDuration(day.total_minutes)}`"
            >
              <div class="bar-column">
                <div
                  class="bar-fill"
                  :style="{
                    height: getBarHeight(day.total_minutes, maxDailyMinutes),
                    backgroundColor: '#3b82f6'
                  }"
                ></div>
              </div>
              <div class="bar-label">{{ formatDate(day.date) }}</div>
            </div>
          </div>
        </div>

        <!-- Time by Project Chart -->
        <div class="chart-card">
          <h3 class="chart-title">Time by Project</h3>

          <div v-if="projectStats.length === 0" class="empty-chart">
            No project data
          </div>

          <div v-else class="horizontal-chart">
            <div
              v-for="project in projectStats"
              :key="project.project_name"
              class="h-bar-item"
            >
              <div class="h-bar-label">{{ project.project_name }}</div>
              <div class="h-bar-container">
                <div
                  class="h-bar-fill"
                  :style="{
                    width: getBarHeight(project.total_minutes, maxProjectMinutes),
                    backgroundColor: project.color
                  }"
                ></div>
              </div>
              <div class="h-bar-value">{{ formatDuration(project.total_minutes) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tags Section -->
      <div v-if="tagStats.length > 0" class="tags-section">
        <h3 class="section-title">Time by Tag</h3>
        <div class="tags-grid">
          <div
            v-for="tag in tagStats"
            :key="tag.tag_name"
            class="tag-stat-card"
          >
            <div class="tag-header">
              <span class="tag-badge" :style="{ backgroundColor: tag.color }">
                {{ tag.tag_name }}
              </span>
            </div>
            <div class="tag-stats">
              <div class="tag-stat">
                <span class="tag-stat-value">{{ tag.session_count }}</span>
                <span class="tag-stat-label">sessions</span>
              </div>
              <div class="tag-stat">
                <span class="tag-stat-value">{{ formatDuration(tag.total_minutes) }}</span>
                <span class="tag-stat-label">total time</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.statistics-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
  margin: 0.25rem 0 0 0;
}

.time-range-selector {
  display: flex;
  gap: 0.5rem;
  background: white;
  padding: 0.25rem;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.range-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: #6b7280;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.range-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.range-btn.active {
  background: #3b82f6;
  color: white;
}

.error-banner {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.retry-btn {
  background-color: white;
  border: 1px solid #b91c1c;
  color: #b91c1c;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.retry-btn:hover {
  background-color: #fef2f2;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 1.5rem 0;
}

.empty-chart {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.25rem;
  height: 200px;
  padding: 1rem 0;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}

.bar-column {
  width: 100%;
  height: 90%;
  display: flex;
  align-items: flex-end;
}

.bar-fill {
  width: 100%;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
  cursor: pointer;
}

.bar-fill:hover {
  opacity: 0.8;
}

.bar-label {
  font-size: 0.625rem;
  color: #6b7280;
  margin-top: 0.25rem;
  text-align: center;
  writing-mode: horizontal-tb;
  transform: rotate(-45deg);
  transform-origin: center;
}

.horizontal-chart {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.h-bar-item {
  display: grid;
  grid-template-columns: 120px 1fr 80px;
  align-items: center;
  gap: 0.75rem;
}

.h-bar-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.h-bar-container {
  height: 28px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.h-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: all 0.3s;
}

.h-bar-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
}

.tags-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 1.5rem 0;
}

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.tag-stat-card {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
}

.tag-header {
  margin-bottom: 0.75rem;
}

.tag-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.tag-stats {
  display: flex;
  justify-content: space-around;
}

.tag-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.tag-stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.tag-stat-label {
  font-size: 0.75rem;
  color: #6b7280;
}
</style>
