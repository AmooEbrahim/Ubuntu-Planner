# Dashboard Implementation

Main dashboard with overview and quick actions.

## Dashboard Page

Create `frontend/src/views/Dashboard.vue`:

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanningStore } from '@/stores/planning'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import StartSessionDialog from '@/components/StartSessionDialog.vue'
import dayjs from 'dayjs'

const planningStore = usePlanningStore()
const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const showStartDialog = ref(false)

const todayPlanning = computed(() => planningStore.todayPlanning)
const recentSessions = computed(() => sessionStore.recentSessions.slice(0, 5))

const todayStats = computed(() => {
  const today = dayjs().format('YYYY-MM-DD')
  const todaySessions = sessionStore.recentSessions.filter(s =>
    dayjs(s.start_time).format('YYYY-MM-DD') === today
  )

  const totalMinutes = todaySessions.reduce((sum, s) => sum + (s.actual_duration || 0), 0)
  const avgSatisfaction = todaySessions.length > 0
    ? Math.round(todaySessions.reduce((sum, s) => sum + (s.satisfaction_score || 0), 0) / todaySessions.length)
    : 0

  return {
    sessionsCount: todaySessions.length,
    totalTime: totalMinutes,
    avgSatisfaction
  }
})

onMounted(async () => {
  await Promise.all([
    planningStore.fetchPlanningForDate(new Date()),
    sessionStore.fetchRecentSessions(),
    projectStore.fetchProjects()
  ])
})

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

function formatTime(datetime) {
  return dayjs(datetime).format('HH:mm')
}
</script>

<template>
  <div class="dashboard">
    <h1>Dashboard</h1>

    <!-- Today's Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ todayStats.sessionsCount }}</div>
        <div class="stat-label">Sessions Today</div>
      </div>

      <div class="stat-card">
        <div class="stat-value">{{ formatDuration(todayStats.totalTime) }}</div>
        <div class="stat-label">Total Time</div>
      </div>

      <div class="stat-card">
        <div class="stat-value">{{ todayStats.avgSatisfaction }}%</div>
        <div class="stat-label">Avg Satisfaction</div>
      </div>

      <div class="stat-card action" @click="showStartDialog = true">
        <div class="stat-icon">▶️</div>
        <div class="stat-label">Start Session</div>
      </div>
    </div>

    <!-- Two Column Layout -->
    <div class="content-grid">
      <!-- Left Column: Today's Planning -->
      <div class="section">
        <h2>Today's Planning</h2>

        <div v-if="todayPlanning.length === 0" class="empty-state">
          No planning for today
        </div>

        <div v-else class="planning-list">
          <div
            v-for="plan in todayPlanning"
            :key="plan.id"
            class="planning-item"
            :class="{ critical: plan.priority === 'critical' }"
          >
            <div class="time">{{ formatTime(plan.scheduled_start) }}</div>
            <div class="project" :style="{ color: plan.project.color }">
              {{ plan.project.name }}
            </div>
            <div v-if="plan.description" class="description">
              {{ plan.description }}
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Recent Sessions -->
      <div class="section">
        <h2>Recent Sessions</h2>

        <div v-if="recentSessions.length === 0" class="empty-state">
          No recent sessions
        </div>

        <div v-else class="sessions-list">
          <div
            v-for="session in recentSessions"
            :key="session.id"
            class="session-item"
          >
            <div class="session-header">
              <div class="project">
                {{ session.project?.name || 'No Project' }}
              </div>
              <div class="duration">
                {{ formatDuration(session.actual_duration || 0) }}
              </div>
            </div>
            <div class="session-meta">
              <span class="time">
                {{ formatTime(session.start_time) }}
              </span>
              <span v-if="session.satisfaction_score" class="satisfaction">
                {{ session.satisfaction_score }}% satisfaction
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <StartSessionDialog
      v-if="showStartDialog"
      @close="showStartDialog = false"
      @started="showStartDialog = false"
    />
  </div>
</template>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-card.action {
  cursor: pointer;
  background: #3b82f6;
  color: white;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>
```

## Checklist

- [ ] Dashboard page created
- [ ] Today's stats displayed
- [ ] Today's planning list shown
- [ ] Recent sessions shown
- [ ] Quick start session button works
- [ ] Layout is clean and functional
