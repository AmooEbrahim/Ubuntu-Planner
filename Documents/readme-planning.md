# Planning

Work scheduling system with overlap detection, priorities, and smart notifications.

## Overview

Planning allows users to schedule work sessions in advance. Features:
- Schedule work sessions with start/end times
- Assign priorities (low, medium, critical)
- Prevent overlapping schedules
- Get notified when it's time to start
- Add tags for categorization
- Optional descriptions

## Planning Attributes

### Required Fields
- **Project**: Which project to work on
- **Scheduled Start**: When to start (datetime)
- **Scheduled End**: When to finish (datetime)

### Optional Fields
- **Priority**: low, medium (default), critical
- **Description**: Notes about what to do in this session
- **Tags**: Multiple tags for categorization

### System Fields
- **Created At**: Auto-generated timestamp
- **Updated At**: Auto-updated timestamp

## Scheduling Rules

### Same-Day Constraint
- Start and end must be on the same day
- No overnight planning allowed
- Simplifies display and logic

**Why?**
- UI is organized by day
- Avoids complexity of multi-day sessions
- If you need to work overnight, create separate sessions

### No Overlap
Planning sessions cannot overlap.

**Validation:**
```python
def check_overlap(new_start, new_end, existing_planning):
    for plan in existing_planning:
        if (new_start < plan.end) and (new_end > plan.start):
            return True  # Overlap detected
    return False
```

**UI Feedback:**
- If overlap detected: Show error message
- Highlight conflicting planning
- Suggest nearest available time slots

### Minimum Duration
Suggested minimum: 5 minutes (not enforced, but recommended in UI)

## Priority Levels

### Low Priority
- **Use case**: Nice-to-do tasks, flexible timing
- **UI**: Gray or muted color
- **Notification**: Standard notifications

### Medium Priority (Default)
- **Use case**: Normal scheduled work
- **UI**: Project color
- **Notification**: Standard notifications

### Critical Priority
- **Use case**: Deadlines, important meetings
- **UI**: Red accent or bold highlight
- **Notification**: More prominent, maybe different sound

## CRUD Operations

### Create
1. User selects project
2. Selects date, start time, end time
3. Optionally sets priority
4. Optionally adds description and tags
5. System validates (no overlap, same day)
6. If valid: Save and show in calendar
7. If invalid: Show error and suggest alternatives

### Read/List
**Daily View** (primary view):
- Calendar-style for selected day
- Shows all planning for that day
- Color-coded by project
- Priority indicators
- Time blocks proportional to duration

**Weekly View**:
- 7-day overview
- Smaller blocks
- Quick navigation

**List View**:
- Filterable by project, tags, priority
- Sortable by time, priority, project
- Shows upcoming planning

### Update
- All fields editable
- Re-validate overlap on save
- If changing time: Check for new overlaps
- If changing project: Tags may need review

### Delete
- Simple confirmation
- Remove planning
- Does not affect past sessions
- If session was started from this planning, session remains but `planning_id` becomes orphaned

## Notifications

### Start Notification
**When**: At `scheduled_start` time

**Message**:
```
Time to start: [Project Name]
[Description if available]
Duration: X minutes
```

**Actions** (if supported):
- Start session
- Snooze (5, 10, 15 minutes)
- Dismiss

### Repeated Notifications
If user doesn't start a session:

**When**: Every N minutes (default: 10)
- N is configurable globally
- Can be overridden per project

**Condition**: Keep sending until:
- User starts any session (even different project)
- Scheduled end time passes
- User dismisses permanently

**Message**:
```
Reminder: [Project Name]
Started X minutes ago (or "Should have started X minutes ago")
```

### End Notification
No notification when planned session ends if not started.
(Notifications for running sessions are in execution, not planning)

## UI Components

### Calendar View
**Layout:**
- Header: Date selector, navigation
- Timeline: Hour markers (configurable, e.g., 6 AM - 11 PM)
- Planning blocks: Positioned by time, sized by duration

**Block Display:**
```
┌─────────────────────┐
│ 14:00 - 15:30      │ ← Time
│ Project Name        │ ← Project
│ [!] Critical       │ ← Priority (if not medium)
│ Description...     │ ← Description (truncated)
│ [tag1] [tag2]      │ ← Tags
└─────────────────────┘
```

**Interactions:**
- Click block: Open detail view
- Double-click: Edit
- Drag: Move (with overlap validation)
- Resize: Change duration (with overlap validation)
- Right-click: Context menu (Edit, Delete, Start Session)

### Planning Form
**Fields:**
- Project selector (dropdown with search)
- Date picker (default: today)
- Start time picker (hour:minute)
- End time picker (hour:minute)
  - Auto-calculate duration display
  - Quick buttons: +30min, +1h, +2h
- Priority selector (3 buttons: low, medium, critical)
  - Visual: medium is default/highlighted
- Description textarea (optional)
- Tag selector (multi-select)

**Validation:**
- Real-time overlap check
- Start < End validation
- Same-day validation
- Visual feedback for errors

### Quick Add
Simplified form for fast planning:
```
[Project ▼] from [14:00] to [15:30] on [Today ▼]
              [Add]  [Add with Details]
```

- "Add": Save with defaults
- "Add with Details": Open full form

## Business Logic

### Overlap Detection
Before saving (create or update):
```python
# Get all planning for the same day
same_day_planning = get_planning_for_date(date)

# Exclude current planning (if editing)
if editing:
    same_day_planning = exclude(current_planning_id)

# Check overlap
if has_overlap(new_start, new_end, same_day_planning):
    return error("Overlap detected")
```

### Duration Calculation
```python
duration_minutes = (scheduled_end - scheduled_start).total_seconds() / 60
```

### Default Values
- **Date**: Today
- **Start Time**: Current time rounded to next quarter hour
- **End Time**: Start + project's default duration
- **Priority**: Medium

### Smart Suggestions
When user selects a project:
- Suggest duration based on project's default duration
- Suggest tags based on frequently used tags for this project
- Suggest time based on past planning patterns (optional, future)

## Integration with Execution

### Starting from Planning
When user starts a session from planning:
1. Create session record
2. Set `session.planning_id = planning.id`
3. Set `session.planned_duration` from planning duration
4. Set `session.project_id = planning.project_id`
5. User can still modify duration before starting

### Planning vs Actual
Comparison metrics:
- Did session start on time?
- Did session use the same project?
- How does actual duration compare to planned?
- Was planned session skipped?

## Filtering and Search

### Filters
- **Date range**: Today, This week, Next week, Custom
- **Project**: Single or multiple projects
- **Priority**: Any combination of low/medium/critical
- **Tags**: Any/All of selected tags
- **Status**: Upcoming, Past, Missed (planned but not executed)

### Search
- Search in description
- Search by project name
- Search by tag name

## API Endpoints

```
GET    /api/planning                # List planning (with filters)
GET    /api/planning/today          # Today's planning
GET    /api/planning/week           # This week
GET    /api/planning/:id            # Get single planning
POST   /api/planning                # Create planning
PUT    /api/planning/:id            # Update planning
DELETE /api/planning/:id            # Delete planning
POST   /api/planning/validate       # Validate without saving (for real-time feedback)
```

## Validation Rules

1. **Project**: Required, must exist
2. **Scheduled Start**: Required, datetime
3. **Scheduled End**: Required, datetime, must be after start
4. **Same Day**: Start and end must be on same day
5. **No Overlap**: Must not overlap with existing planning
6. **Priority**: Must be one of: low, medium, critical
7. **Tags**: Must be valid tag IDs, compatible with project

## Statistics and Insights

### Planning Adherence
- Percentage of planning actually executed
- Average delay in starting sessions
- Which planning are most often skipped

### Planning Patterns
- What times are most planned
- Which projects are planned most
- How accurate are duration estimates

### Calendar Heat Map
Visual representation:
- Which days have most planning
- Which time slots are most used
- Planning density over weeks/months

## Future Enhancements

- Recurring planning (daily, weekly patterns)
- Template planning (save common schedules)
- Smart scheduling (suggest optimal times based on productivity patterns)
- Conflicts with external calendars (iCal integration)
- Planning from voice/chat interface
