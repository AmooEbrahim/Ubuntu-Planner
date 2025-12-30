# Execution (Sessions)

Real-time work tracking with notifications, reviews, and productivity insights.

## Overview

Execution tracking records actual work sessions. Features:
- Start/stop session tracking via web or system tray
- Track sessions with or without projects
- Track sessions from planning or ad-hoc
- Real-time duration tracking
- Smart notifications when time expires
- Optional detailed review after completion
- Manual notes during work
- Desktop integration with system tray icon (Phase 5)

## Session Lifecycle

### States
1. **Active**: Session is running (`end_time = NULL`)
2. **Completed**: Session finished (`end_time != NULL`)

Only one session can be active at a time.

## Session Attributes

### Required Fields
- **Start Time**: When session started (auto-set)
- **Planned Duration**: How long user plans to work (minutes)

### Optional Fields
- **Project**: Which project (can be NULL for projectless sessions)
- **Planning**: Reference to planning if started from schedule
- **End Time**: When session ended (NULL while active)
- **Notes**: General notes added during or after session
- **Tasks Done**: What was accomplished (added during review)
- **Satisfaction Score**: 0-100, default 80 in UI (added during review)
- **Tags**: Multiple tags (added during review)
- **Notification Disabled**: User can disable notifications for this session

### Calculated Fields
- **Actual Duration**: Auto-calculated from end_time - start_time

### System Fields
- **Created At**: Auto-generated
- **Updated At**: Auto-updated

## Starting a Session

### Method 1: From Planning
User sees planned session and clicks to start:

1. System shows planning details
2. Pre-fills:
   - Project from planning
   - Planned duration from planning duration
   - Tags from planning (optional)
3. User can modify duration
4. Session starts with `planning_id` reference

### Method 2: Ad-hoc Start
User starts session manually:

1. User clicks "Start Session"
2. Quick start menu appears:
   - **Pinned projects** (3-5 projects marked as pinned)
   - **Recent projects** (2-3 most recently used)
   - **Search/Browse** (all active projects)
   - **No project** (for breaks, untracked work)
3. User selects project (or no project)
4. System shows planned duration:
   - From project's default duration
   - User can modify
5. Session starts

### Method 3: Continue Last
Quick restart of last project:

1. User clicks "Continue Last"
2. System loads last project
3. Uses default duration
4. Session starts immediately (or with duration confirmation)

## During Session

### UI Display
**Session Banner** (always visible in web interface):
```
🟢 Active: [Project Name]          ⏱️ 45:30 / 60:00
[+15 min] [Add Note] [Stop] [⚙️ Options]
```

**Minimized View:**
```
🟢 [Project] 45:30 [▼]
```

### Available Actions

#### Add Note
- Opens simple text input
- Note is appended to session notes
- Timestamped automatically
- Format: `[14:35] User note here`

#### Add 15 Minutes
- Extends planned duration by 15 minutes
- Adjusts notification time accordingly
- Can be clicked multiple times

#### Disable Notifications
- Stops all notifications for this session
- Session continues running
- Can be re-enabled

#### Stop Session
Two options:
1. **Quick Stop**: Ends immediately, no review
2. **Stop & Review**: Opens review form

### Session Polling
Web interface polls backend every 2 minutes:
- Updates elapsed time
- Checks for notification triggers
- Updates UI

Manual refresh button available for immediate update.

## Notifications

### Session End Notification

**When**: When elapsed time reaches planned duration

**Message**:
```
Session Complete: [Project Name]
Time is up! Consider taking a break or starting something else.
Duration: X minutes
```

**Actions** (if supported):
- Stop session
- Add 15 minutes
- Disable notifications

### Repeated Notifications

If session continues after planned duration:

**When**: Every N minutes (configurable)
- N = project's notification_interval (if set)
- N = global default (10 minutes) otherwise

**Condition**: Keep sending until:
- User stops session
- User disables notifications

**Message**:
```
Still Working: [Project Name]
X minutes over planned time
Planned: Y minutes, Actual: Z minutes so far
```

**Logic:**
```python
def should_send_notification(session):
    if session.notification_disabled:
        return False

    elapsed = now() - session.start_time
    if elapsed < session.planned_duration:
        return False

    overtime = elapsed - session.planned_duration
    interval = session.project.notification_interval or global_default

    return (overtime % interval) < 1  # Within 1 minute of interval
```

## Desktop Integration (System Tray)

**Phase 5** adds system tray icon for quick access.

### Tray Icon States
- **Idle** (gray): No active session
- **Active** (green/blue): Session running on time
- **Overtime** (orange/red): Session exceeded planned duration

### Tray Menu - No Active Session
- Start from current planning (if scheduled)
- Start session without project
- Pinned projects (quick start)
- Recent projects (last 3)
- Open web interface
- Quit

### Tray Menu - Active Session
- Session info (project name, time elapsed/planned)
- Stop & Review (opens review page in browser)
- Quick Stop (end without review)
- Toggle Notifications (enable/disable for this session)
- Open web interface
- Quit

### Tray Features
- Automatic polling (updates every 30 seconds)
- Icon changes based on session state
- Click to access quick actions
- No need to keep browser open

**See:** `Documents/roadmap/5/tray-icon.md` for implementation details

## Ending a Session

### Quick Stop
1. User clicks "Stop" (web or tray)
2. Session ends immediately
3. `end_time` set to now
4. No review form shown
5. Session saved with minimal data

**Use case**: Quick tasks, interruptions, forgot to stop

### Stop & Review
1. User clicks "Stop & Review" (web or tray)
2. Session ends (`end_time` set)
3. Review page opens (in browser if from tray)

**Review Page:** `/session-review/:id`
```
Session Review: [Project Name]
Duration: [Actual duration] ([Planned duration] planned)

Satisfaction Score: [────●────] 80/100

What did you accomplish?
[Textarea for tasks done]

Personal notes:
[Textarea for additional notes]

Tags:
[Tag selector - multi-select]
Available: [Global tags] [Project tags] [Parent tags]

[Save] [Save & Start Next Session]
```

**Fields:**
- **Satisfaction Score**: Slider, 0-100, default 80
- **Tasks Done**: What was accomplished
- **Notes**: Personal reflections
- **Tags**: Add relevant tags

**Save Options:**
1. **Save**: Complete review and return
2. **Save & Start Next**: Complete review and immediately show "Start Session" dialog

## Projectless Sessions

Sessions can exist without a project (`project_id = NULL`).

**Use cases:**
- Break time
- Untracked work
- Transition between tasks

**Behavior:**
- No default duration (user must specify)
- No project-specific tags (only global tags)
- No notification interval from project (uses global)
- Can still be reviewed and tagged

**UI:**
Display as: `[No Project]` or `[Break]`

## Session Management

### View Sessions

**Recent Sessions:**
- List view of recent sessions
- Sortable by date, project, duration
- Filterable by project, tags, date range

**Session Detail:**
Shows all information:
- Project (with hierarchy)
- Start and end times
- Planned vs actual duration
- Satisfaction score
- Tasks accomplished
- Notes
- Tags

**Actions:**
- Edit session (modify notes, tags, satisfaction)
- Delete session (with confirmation)

### Edit Completed Session

User can edit:
- Notes
- Tasks done
- Satisfaction score
- Tags

Cannot edit:
- Start time (historical data)
- End time (historical data)
- Project (use caution, maybe allow with warning)
- Planned duration (historical)

### Delete Session

1. Confirmation required
2. Show session details
3. Options:
   - Cancel
   - Delete (permanent)

No cascade deletes (planning remains if linked).

## Active Session Management

### Single Active Session Rule
Only one session can be active at a time.

**Enforcement:**
Before starting new session:
```python
active_session = get_active_session()
if active_session:
    # Show warning
    options = [
        "Cancel (keep current session)",
        "Stop current and start new",
        "Review current and start new"
    ]
    # User chooses
```

### Restart After Crash
If application restarts:
1. Check for active sessions (`end_time = NULL`)
2. If found:
   - Show notification
   - Options:
     - Continue (keep running)
     - Stop now (end session)
     - Stop and review

## Integration with Planning

### Starting from Planning
When session starts from planning:
- `session.planning_id` = planning ID
- Initial duration from planning
- Can still modify before start

### Comparing Plan vs Actual
Metrics:
- Start time delta (planned vs actual)
- Duration delta (planned vs actual)
- Same project? (yes/no)
- Satisfaction with execution

### Skipped Planning
Planning that was never executed:
- Mark as "skipped" in reports
- Show in planning adherence metrics

## Background Worker

Continuous monitoring for:

### Active Session Checks
Every 1 minute:
1. Get active session
2. Calculate elapsed time
3. If elapsed >= planned duration:
   - Check if notification due
   - Send notification if needed
   - Log notification sent

### Planning Start Checks
Every 1 minute:
1. Get planning for current time window
2. Check if session started
3. If not started:
   - Check if notification due (initial or repeated)
   - Send notification if needed

**Logic:**
```python
def check_planning_notifications():
    now = current_time()
    current_planning = get_planning_in_range(now - 5min, now + 5min)

    for plan in current_planning:
        if now >= plan.scheduled_start:
            # Check if session started from this plan
            session = get_session_by_planning_id(plan.id)

            if not session:
                # Check if any session started after plan start
                any_session = get_session_started_after(plan.scheduled_start)

                if not any_session:
                    # Send notification
                    send_planning_notification(plan)
```

## UI Components

### Session Banner (Active)
Persistent banner at top of all pages:
- Project name and color
- Elapsed / planned time
- Progress bar
- Quick actions

### Start Session Dialog
Modal or side panel:
- Project selector
  - Pinned (large buttons)
  - Recent (smaller buttons)
  - Search/browse
  - No project option
- Duration input (with quick buttons: 30, 60, 90, 120 min)
- Start button

### Review Dialog
Modal form:
- Read-only summary (project, times)
- Editable fields (satisfaction, tasks, notes, tags)
- Save options

### Session List
Table or card view:
- Columns: Date, Project, Duration, Satisfaction, Tags
- Filters: Date range, Project, Tags
- Sort: Date, Duration, Satisfaction
- Actions: View, Edit, Delete

## API Endpoints

```
GET    /api/sessions                # List sessions (with filters)
GET    /api/sessions/active         # Get active session
GET    /api/sessions/recent         # Recent sessions
GET    /api/sessions/:id            # Get single session
POST   /api/sessions                # Start new session
PUT    /api/sessions/:id            # Update session (add notes, end, review)
DELETE /api/sessions/:id            # Delete session
PATCH  /api/sessions/:id/add-time   # Add time to active session
PATCH  /api/sessions/:id/disable-notif  # Toggle notification
POST   /api/sessions/active/stop    # Quick stop active session
POST   /api/sessions/active/review  # Stop and get review form
```

## Validation Rules

1. **Project**: Must exist or NULL
2. **Planned Duration**: Required, positive integer (minutes)
3. **Start Time**: Auto-set, cannot be in future
4. **End Time**: Must be after start time (if set)
5. **Only One Active**: Enforce single active session
6. **Satisfaction Score**: 0-100 or NULL
7. **Tags**: Must be valid and compatible with project

## Statistics and Insights

### Session Metrics
- Total time per project
- Average session duration per project
- Planned vs actual duration accuracy
- Satisfaction trends

### Productivity Patterns
- Most productive times of day
- Most productive days of week
- Session length sweet spots
- Break frequency recommendations

### Project Insights
- Time distribution across projects
- Which projects have highest satisfaction
- Which projects run over time most often

## Future Enhancements

- Pomodoro timer integration
- Auto-pause detection (idle detection)
- Integration with activity tracking
- Session templates
- Voice commands for start/stop
- Mobile app for on-the-go tracking
