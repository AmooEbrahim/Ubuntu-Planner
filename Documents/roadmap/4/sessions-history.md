# Sessions History Page

Detailed sessions history with filtering and export.

## Frontend Implementation

Enhance existing Sessions view (created in Phase 3) with:

### Filters

```vue
<script setup>
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import dayjs from 'dayjs'

const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const filters = ref({
  dateFrom: dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dateTo: dayjs().format('YYYY-MM-DD'),
  projectId: null,
  minSatisfaction: null
})

const filteredSessions = computed(() => {
  let sessions = sessionStore.recentSessions

  // Apply filters
  if (filters.value.projectId) {
    sessions = sessions.filter(s => s.project_id === filters.value.projectId)
  }

  if (filters.value.minSatisfaction !== null) {
    sessions = sessions.filter(s =>
      s.satisfaction_score >= filters.value.minSatisfaction
    )
  }

  // Date range
  sessions = sessions.filter(s => {
    const date = dayjs(s.start_time).format('YYYY-MM-DD')
    return date >= filters.value.dateFrom && date <= filters.value.dateTo
  })

  return sessions
})

function exportToCSV() {
  const headers = ['Date', 'Project', 'Duration', 'Satisfaction', 'Tasks', 'Notes']
  const rows = filteredSessions.value.map(s => [
    dayjs(s.start_time).format('YYYY-MM-DD HH:mm'),
    s.project?.name || 'No Project',
    s.actual_duration || 0,
    s.satisfaction_score || '',
    s.tasks_done || '',
    s.notes || ''
  ])

  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(cell =>
      `"${String(cell).replace(/"/g, '""')}"`
    ).join(','))
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `sessions-${dayjs().format('YYYY-MM-DD')}.csv`
  a.click()
}
</script>

<template>
  <div class="sessions-history">
    <h1>Sessions History</h1>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>From</label>
        <input type="date" v-model="filters.dateFrom">
      </div>

      <div class="filter-group">
        <label>To</label>
        <input type="date" v-model="filters.dateTo">
      </div>

      <div class="filter-group">
        <label>Project</label>
        <select v-model="filters.projectId">
          <option :value="null">All Projects</option>
          <option
            v-for="p in projectStore.activeProjects"
            :key="p.id"
            :value="p.id"
          >
            {{ p.name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Min Satisfaction</label>
        <input
          type="number"
          v-model.number="filters.minSatisfaction"
          min="0"
          max="100"
          placeholder="Any"
        >
      </div>

      <button @click="exportToCSV" class="btn-secondary">
        Export CSV
      </button>
    </div>

    <!-- Sessions List -->
    <div class="sessions-list">
      <div
        v-for="session in filteredSessions"
        :key="session.id"
        class="session-card"
      >
        <!-- Session details -->
      </div>
    </div>
  </div>
</template>
```

## Backend Enhancements

Add filtering to sessions endpoint:

```python
@router.get("/", response_model=List[SessionResponse])
def list_sessions(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    project_id: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """List sessions with filters."""
    query = db.query(WorkSession).filter(WorkSession.end_time.isnot(None))

    if start_date:
        query = query.filter(WorkSession.start_time >= start_date)

    if end_date:
        query = query.filter(WorkSession.start_time <= end_date)

    if project_id:
        query = query.filter(WorkSession.project_id == project_id)

    return query.order_by(WorkSession.start_time.desc()).limit(limit).all()
```

## Checklist

- [ ] Filters implemented
- [ ] Date range filter works
- [ ] Project filter works
- [ ] Satisfaction filter works
- [ ] CSV export works
- [ ] Export includes all relevant data
- [ ] Large datasets handled efficiently
