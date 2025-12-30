# Session Review Page

Detailed session completion page for collecting feedback and notes.

## Overview

Dedicated page for reviewing completed sessions with:
- Satisfaction rating
- Tasks completed tracking
- Personal notes
- Redirect to sessions list after save

## Route

**Path:** `/session-review/:id`

**Access:** Opened when user clicks "Stop & Review" from tray or web interface

## Page Structure

### URL Parameters

- `id` - Session ID to review

### Data Loading

1. Load session details from API
2. Pre-fill form with existing data (if any)
3. Show session summary (project, duration, elapsed time)

## UI Components

### Session Summary (Read-only)

```
┌─────────────────────────────────────┐
│ Session Review                      │
│                                     │
│ Project: Web Development            │
│ Planned: 60 minutes                 │
│ Actual: 75 minutes                  │
│ Started: 2025-12-30 14:00          │
│ Ended: 2025-12-30 15:15            │
└─────────────────────────────────────┘
```

### Satisfaction Rating

```
┌─────────────────────────────────────┐
│ How satisfied are you with your     │
│ performance?                        │
│                                     │
│ [━━━━━━━━━━━━━━━━━━━━━━━━━] 80     │
│ 0 ────────────────────────── 100   │
│                                     │
│ Excellent! Keep up the good work.   │
└─────────────────────────────────────┘
```

- Slider from 0 to 100
- Default value: 80
- Show feedback text based on value:
  - 90-100: "Excellent! Keep up the good work."
  - 70-89: "Good job! You're making progress."
  - 50-69: "Not bad. Room for improvement."
  - 30-49: "Could be better. What went wrong?"
  - 0-29: "Tough session. Let's analyze what happened."

### Tasks Completed

```
┌─────────────────────────────────────┐
│ What did you accomplish?            │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ - Implemented user auth         │ │
│ │ - Fixed login bug               │ │
│ │ - Wrote unit tests              │ │
│ │                                 │ │
│ │                                 │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 145 / 500 characters               │
└─────────────────────────────────────┘
```

- Textarea, 5 rows
- Max 500 characters
- Optional
- Placeholder: "List tasks, achievements, or progress made..."

### Personal Notes

```
┌─────────────────────────────────────┐
│ Personal Notes (Optional)           │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Got distracted by emails.       │ │
│ │ Need to improve focus next time.│ │
│ │                                 │ │
│ │                                 │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 82 / 1000 characters               │
└─────────────────────────────────────┘
```

- Textarea, 5 rows
- Max 1000 characters
- Optional
- Placeholder: "Reflections, challenges, learnings, distractions..."

### Action Buttons

```
┌─────────────────────────────────────┐
│ [ Skip Review ]  [ Save & Continue ]│
└─────────────────────────────────────┘
```

- **Skip Review**: Save session without additional data, redirect to /sessions
- **Save & Continue**: Save all review data, redirect to /sessions

## Implementation

### Frontend Component

Create `frontend/src/views/SessionReview.vue`:

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/sessions'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()

const session = ref(null)
const satisfaction = ref(80)
const tasks = ref('')
const notes = ref('')
const loading = ref(true)

const satisfactionFeedback = computed(() => {
  const val = satisfaction.value
  if (val >= 90) return "Excellent! Keep up the good work."
  if (val >= 70) return "Good job! You're making progress."
  if (val >= 50) return "Not bad. Room for improvement."
  if (val >= 30) return "Could be better. What went wrong?"
  return "Tough session. Let's analyze what happened."
})

const tasksCharCount = computed(() => tasks.value.length)
const notesCharCount = computed(() => notes.value.length)

onMounted(async () => {
  try {
    session.value = await sessionStore.getSession(route.params.id)

    // Pre-fill if data exists
    if (session.value.satisfaction !== null) {
      satisfaction.value = session.value.satisfaction
    }
    if (session.value.tasks) {
      tasks.value = session.value.tasks
    }
    if (session.value.notes) {
      notes.value = session.value.notes
    }
  } catch (error) {
    console.error('Failed to load session:', error)
  } finally {
    loading.value = false
  }
})

async function saveReview() {
  try {
    await sessionStore.updateSessionReview(route.params.id, {
      satisfaction: satisfaction.value,
      tasks: tasks.value || null,
      notes: notes.value || null
    })

    router.push('/sessions')
  } catch (error) {
    console.error('Failed to save review:', error)
    alert('Failed to save review. Please try again.')
  }
}

function skipReview() {
  router.push('/sessions')
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}
</script>

<template>
  <div class="session-review-page">
    <div v-if="loading" class="loading">Loading session...</div>

    <div v-else-if="session" class="review-container">
      <h1>Session Review</h1>

      <!-- Session Summary -->
      <div class="session-summary">
        <div class="summary-item">
          <span class="label">Project:</span>
          <span class="value">{{ session.project?.name || 'No Project' }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Planned:</span>
          <span class="value">{{ formatDuration(session.planned_duration) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Actual:</span>
          <span class="value">{{ formatDuration(session.actual_duration) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Started:</span>
          <span class="value">{{ dayjs(session.start_time).format('YYYY-MM-DD HH:mm') }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Ended:</span>
          <span class="value">{{ dayjs(session.end_time).format('YYYY-MM-DD HH:mm') }}</span>
        </div>
      </div>

      <!-- Satisfaction Rating -->
      <div class="form-section">
        <label class="section-title">How satisfied are you with your performance?</label>

        <div class="slider-container">
          <input
            v-model.number="satisfaction"
            type="range"
            min="0"
            max="100"
            class="satisfaction-slider"
          />
          <div class="slider-value">{{ satisfaction }}</div>
        </div>

        <div class="slider-labels">
          <span>0</span>
          <span>100</span>
        </div>

        <div class="satisfaction-feedback">{{ satisfactionFeedback }}</div>
      </div>

      <!-- Tasks Completed -->
      <div class="form-section">
        <label class="section-title">What did you accomplish?</label>
        <textarea
          v-model="tasks"
          placeholder="List tasks, achievements, or progress made..."
          rows="5"
          maxlength="500"
          class="form-textarea"
        ></textarea>
        <div class="char-count">{{ tasksCharCount }} / 500 characters</div>
      </div>

      <!-- Personal Notes -->
      <div class="form-section">
        <label class="section-title">Personal Notes (Optional)</label>
        <textarea
          v-model="notes"
          placeholder="Reflections, challenges, learnings, distractions..."
          rows="5"
          maxlength="1000"
          class="form-textarea"
        ></textarea>
        <div class="char-count">{{ notesCharCount }} / 1000 characters</div>
      </div>

      <!-- Actions -->
      <div class="actions">
        <button @click="skipReview" class="btn btn-secondary">
          Skip Review
        </button>
        <button @click="saveReview" class="btn btn-primary">
          Save & Continue
        </button>
      </div>
    </div>

    <div v-else class="error">
      Session not found.
    </div>
  </div>
</template>

<style scoped>
.session-review-page {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.review-container {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

h1 {
  font-size: 1.875rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.session-summary {
  background: #f9fafb;
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 2rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.summary-item .label {
  font-weight: 600;
  color: #6b7280;
}

.summary-item .value {
  color: #111827;
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  display: block;
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 1rem;
  color: #111827;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.satisfaction-slider {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  outline: none;
  -webkit-appearance: none;
  background: linear-gradient(to right, #ef4444, #f59e0b, #10b981);
}

.satisfaction-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.satisfaction-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.slider-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #3b82f6;
  min-width: 3rem;
  text-align: center;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #6b7280;
}

.satisfaction-feedback {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #eff6ff;
  border-left: 4px solid #3b82f6;
  border-radius: 0.25rem;
  color: #1e40af;
  font-weight: 500;
}

.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-family: inherit;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  ring: 2px;
  ring-color: #3b82f6;
  ring-opacity: 0.5;
}

.char-count {
  text-align: right;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  border: 1px solid #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}
</style>
```

### Backend API

Add to `backend/app/api/sessions.py`:

```python
@router.put("/{session_id}/review")
async def update_session_review(
    session_id: int,
    review_data: SessionReviewUpdate,
    db: Session = Depends(get_db)
):
    """Update session review data."""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.satisfaction = review_data.satisfaction
    session.tasks = review_data.tasks
    session.notes = review_data.notes
    session.updated_at = datetime.now()

    db.commit()
    db.refresh(session)

    return session
```

### Pydantic Schema

```python
class SessionReviewUpdate(BaseModel):
    satisfaction: int = Field(ge=0, le=100)
    tasks: Optional[str] = None
    notes: Optional[str] = None
```

### Router Integration

Update `frontend/src/router/index.js`:

```javascript
{
  path: '/session-review/:id',
  name: 'SessionReview',
  component: () => import('@/views/SessionReview.vue')
}
```

## Checklist

- [ ] Route configured
- [ ] Component created
- [ ] Session data loads
- [ ] Satisfaction slider works
- [ ] Character counters work
- [ ] Skip button redirects to /sessions
- [ ] Save button saves and redirects
- [ ] Backend API endpoint works
- [ ] Pre-fills existing data
- [ ] Feedback messages change based on rating
- [ ] Responsive design
- [ ] Error handling

## Notes

- Page can be accessed directly via URL
- If session already has review data, it pre-fills
- Can re-review sessions by visiting page again
- Character limits enforced on both frontend and backend
