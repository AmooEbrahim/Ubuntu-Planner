# Statistics and Analytics

Statistics page with charts and insights.

## Backend API

Create `backend/app/api/statistics.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import Dict, List
from app.core.database import get_db
from app.models.session import Session as WorkSession
from app.models.project import Project

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

@router.get("/overview")
def get_overview(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
) -> Dict:
    """Get overview statistics."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    # Total time and sessions
    stats = db.query(
        func.count(WorkSession.id).label('total_sessions'),
        func.sum(WorkSession.actual_duration).label('total_minutes'),
        func.avg(WorkSession.satisfaction_score).label('avg_satisfaction')
    ).filter(
        WorkSession.start_time >= start_date,
        WorkSession.start_time <= end_date,
        WorkSession.end_time.isnot(None)
    ).first()

    return {
        'total_sessions': stats.total_sessions or 0,
        'total_minutes': int(stats.total_minutes or 0),
        'avg_satisfaction': round(stats.avg_satisfaction or 0, 1)
    }

@router.get("/by-project")
def get_by_project(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Get time spent per project."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    results = db.query(
        Project.name,
        Project.color,
        func.count(WorkSession.id).label('session_count'),
        func.sum(WorkSession.actual_duration).label('total_minutes')
    ).join(
        WorkSession, WorkSession.project_id == Project.id
    ).filter(
        WorkSession.start_time >= start_date,
        WorkSession.start_time <= end_date,
        WorkSession.end_time.isnot(None)
    ).group_by(
        Project.id
    ).order_by(
        func.sum(WorkSession.actual_duration).desc()
    ).all()

    return [
        {
            'project_name': r.name,
            'color': r.color,
            'session_count': r.session_count,
            'total_minutes': int(r.total_minutes or 0)
        }
        for r in results
    ]

@router.get("/daily-activity")
def get_daily_activity(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Get daily activity summary."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    results = db.query(
        func.date(WorkSession.start_time).label('date'),
        func.count(WorkSession.id).label('session_count'),
        func.sum(WorkSession.actual_duration).label('total_minutes'),
        func.avg(WorkSession.satisfaction_score).label('avg_satisfaction')
    ).filter(
        WorkSession.start_time >= start_date,
        WorkSession.start_time <= end_date,
        WorkSession.end_time.isnot(None)
    ).group_by(
        func.date(WorkSession.start_time)
    ).order_by(
        func.date(WorkSession.start_time)
    ).all()

    return [
        {
            'date': str(r.date),
            'session_count': r.session_count,
            'total_minutes': int(r.total_minutes or 0),
            'avg_satisfaction': round(r.avg_satisfaction or 0, 1)
        }
        for r in results
    ]

# Add more endpoints as needed
```

Include router in main.py.

## Frontend

Create `frontend/src/views/Statistics.vue`:

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import { Chart as ChartJS, ... } from 'chart.js'
import api from '@/services/api'
import dayjs from 'dayjs'

// Register ChartJS components
ChartJS.register(...)

const timeRange = ref('month') // week, month, year
const stats = ref(null)
const projectStats = ref([])
const dailyActivity = ref([])

const chartData = computed(() => {
  // Transform data for charts
  return {
    labels: dailyActivity.value.map(d => dayjs(d.date).format('MMM DD')),
    datasets: [{
      label: 'Minutes Worked',
      data: dailyActivity.value.map(d => d.total_minutes),
      backgroundColor: '#3b82f6'
    }]
  }
})

onMounted(async () => {
  await loadStatistics()
})

async function loadStatistics() {
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

  const params = {
    start_date: startDate.format('YYYY-MM-DD'),
    end_date: endDate.format('YYYY-MM-DD')
  }

  const [overview, byProject, daily] = await Promise.all([
    api.get('/api/statistics/overview', { params }),
    api.get('/api/statistics/by-project', { params }),
    api.get('/api/statistics/daily-activity', { params })
  ])

  stats.value = overview.data
  projectStats.value = byProject.data
  dailyActivity.value = daily.data
}
</script>

<template>
  <div class="statistics-page">
    <h1>Statistics</h1>

    <div class="time-range-selector">
      <button
        v-for="range in ['week', 'month', 'year']"
        :key="range"
        @click="timeRange = range; loadStatistics()"
        :class="{ active: timeRange === range }"
      >
        {{ range }}
      </button>
    </div>

    <!-- Overview Stats -->
    <div class="stats-overview">
      <!-- Display stats.value -->
    </div>

    <!-- Charts -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3>Daily Activity</h3>
        <Bar :data="chartData" :options="chartOptions" />
      </div>

      <div class="chart-card">
        <h3>Time by Project</h3>
        <!-- Pie or bar chart for projects -->
      </div>

      <!-- More charts -->
    </div>
  </div>
</template>
```

Use a charting library like Chart.js or ApexCharts.

## Checklist

- [ ] Statistics API endpoints created
- [ ] Statistics page created
- [ ] Charts library integrated
- [ ] Daily activity chart works
- [ ] Project breakdown chart works
- [ ] Time range selector works
- [ ] Data loads correctly
