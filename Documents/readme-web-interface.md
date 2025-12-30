# Web Interface

Modern, minimal, and functional web interface for Ubuntu Planner.

## Overview

Single-page application (SPA) built with Vue 3, providing complete access to all features:
- Project management
- Tag management
- Planning calendar
- Session tracking
- Statistics and insights

## Design Principles

### Minimalism
- Clean, uncluttered interface
- Focus on essential features
- No unnecessary decorations
- Fast load times

### Usability
- Intuitive navigation
- Quick access to common actions
- Keyboard shortcuts
- Responsive feedback

### Modern
- Contemporary design language
- Smooth animations
- Consistent styling (Tailwind CSS)
- Dark/light theme support (future)

## Main Layout

```
┌─────────────────────────────────────────────────┐
│ [Logo] Ubuntu Planner    [Nav]    [Active Now] │ ← Header
├─────────────────────────────────────────────────┤
│                                                 │
│                                                 │
│              Main Content Area                  │
│                                                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Header
- **Logo/Title**: Ubuntu Planner
- **Navigation**: Dashboard, Projects, Tags, Planning, Sessions, Stats, Settings (Phase 5)
- **Active Session Banner**: Shows when session is active (collapsible)

### Active Session Banner

**Expanded:**
```
🟢 Working on: Web Development          ⏱️ 45:32 / 60:00
[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━░░░░░░] 76%
[+15 min] [Add Note] [Stop] [Stop & Review] [Disable Notif] [▲]
```

**Minimized:**
```
🟢 Web Development • 45:32 [▼]
```

**Not Active:**
```
[Start Session] button in header
```

## Pages

### 1. Dashboard

**Purpose**: Overview of today's activity

**Sections:**
- **Today's Planning**: List of scheduled sessions
- **Active Session**: Prominent display if session running
- **Recent Sessions**: Last 5-10 sessions
- **Quick Stats**: Today's total time, sessions count
- **Quick Actions**: Start session, Add planning

**Layout:**
```
┌──────────────────┬──────────────────┐
│ Today's Planning │ Active Session   │
│                  │  or              │
│ [List]           │ [Start Session]  │
├──────────────────┴──────────────────┤
│ Recent Sessions                     │
│ [Cards]                             │
├─────────────────────────────────────┤
│ Quick Stats                         │
│ ⏱️ 3h 45m  📊 4 sessions  ⭐ 85 avg│
└─────────────────────────────────────┘
```

### 2. Projects

**Purpose**: Manage projects

**Features:**
- Tree view of project hierarchy
- Filter: Active / Archived / All
- Search bar
- Actions: Create, Edit, Archive, Delete, Pin

**Layout:**
```
[Search: ________] [+ New Project] [Filters ▼]

Projects (showing active)
├─ 📌 Work                          [Edit] [Archive] [Unpin]
│  ├─ Client A
│  │  └─ Project X                  [Edit] [Archive] [Pin]
│  └─ Client B
└─ Personal                         [Edit] [Archive] [Pin]
   └─ Learning

[Show Archived (5)]
```

**Project Card/Row:**
- Color indicator
- Name (with hierarchy path)
- Icons: 📌 pinned, 📦 archived
- Stats: Total time, Session count
- Actions: Edit, Archive/Unarchive, Pin/Unpin, Delete

**Project Form:**
```
Create/Edit Project

Name: [____________]
Color: [🎨 Color Picker]
Parent: [None ▼] or [Select parent project ▼]
Description: [________________]

Default Session Duration: [60] minutes
Notification Interval: [Use default (10 min) ▼]

☐ Pin this project
☐ Archive this project

[Save] [Cancel]
```

### 3. Tags

**Purpose**: Manage tags

**Features:**
- List of all tags (global and project-specific)
- Filter by global/project-specific
- Search
- Create, Edit, Delete

**Layout:**
```
[Search: ________] [+ New Tag] [Filter: All ▼]

Global Tags (15)
[urgent] [blocked] [quick-win] [waiting] ...

Project Tags (23)
Work › [meeting] [email] [planning]
Client A › [review] [testing]
Project X › [development] [deployment]
...

[Tag details on click]
```

**Tag Form:**
```
Create/Edit Tag

Name: [____________]
Color: [🎨 Color Picker]
Scope: ● Global  ○ Project-specific

Project: [Select project ▼] (if project-specific)

[Preview: Tag Name]

Used in: X sessions, Y planning

[Save] [Cancel]
```

### 4. Planning

**Purpose**: Schedule work sessions

**Default View**: Daily calendar

**Features:**
- Date navigation (prev/next day, jump to date)
- Week view toggle
- Create, Edit, Delete planning
- Quick add
- Filter by project, priority, tags

**Layout (Daily):**
```
← [Today: December 30, 2025] →   [Week View] [+ Quick Add]

     ┌─────────────────────────┐
09:00│                         │
     ├─────────────────────────┤
10:00│ 📧 Email Processing     │
     │ Low priority            │
11:00├─────────────────────────┤
     │                         │
12:00├─────────────────────────┤
     │                         │
13:00├─────────────────────────┤
     │                         │
14:00├─────────────────────────┤
     │ 💻 Project X Dev        │
     │ Critical                │
15:00│ [development] [testing] │
     ├─────────────────────────┤
16:00│                         │
     └─────────────────────────┘

[Filters: All Projects ▼] [All Priorities ▼] [All Tags ▼]
```

**Planning Block (on click):**
```
Project X Development
14:00 - 15:30 (90 minutes)
Priority: Critical
Description: Implement new feature X
Tags: [development] [testing]

[Start Session] [Edit] [Delete]
```

**Planning Form:**
```
Create/Edit Planning

Project: [Select project ▼]
Date: [2025-12-30 📅]

Start: [14:00 🕐]  End: [15:30 🕐]
Duration: 90 minutes (calculated)

Quick durations: [30min] [60min] [90min] [2h]

Priority: ○ Low  ● Medium  ○ Critical

Description (optional):
[___________________________________]

Tags (optional):
[Tag selector with available tags]

[Save] [Cancel]
```

**Quick Add:**
```
[Project ▼] from [14:00] to [15:30] on [Today ▼]
[Add] [Full Form]
```

### 5. Sessions

**Purpose**: View and manage completed sessions

**Features:**
- List/card view toggle
- Filter: Date range, Project, Tags, Satisfaction
- Sort: Date, Duration, Satisfaction
- Export (future)

**Layout:**
```
[View: List ▼] [Filters ▼] [Search: ________]

Today
┌──────────────────────────────────────────────────┐
│ 09:00 - 10:30 • Web Development        90min    │
│ Satisfaction: ████████░░ 80/100                  │
│ [development] [testing]                          │
│ Tasks: Implemented feature X, Fixed bug Y        │
└──────────────────────────────────────────────────┘

Yesterday
┌──────────────────────────────────────────────────┐
│ 14:00 - 15:15 • Email Processing        75min   │
│ Satisfaction: ██████████ 95/100                  │
│ [email] [urgent]                                 │
└──────────────────────────────────────────────────┘

[Load More]

Filters:
Date: [Last 7 days ▼]
Project: [All ▼]
Tags: [All ▼]
Satisfaction: [All ▼]
```

**Session Detail (on click):**
```
Session Details

Project: Web Development (Work › Client A › Project X)
Started: Dec 30, 2025 09:00
Ended: Dec 30, 2025 10:30
Duration: 90 minutes (90 planned) ✓

Satisfaction: ████████░░ 80/100

Tasks Accomplished:
- Implemented feature X
- Fixed bug Y
- Code review

Notes:
Good focus session. Minimal distractions.

Tags: [development] [testing]

[Edit] [Delete] [Close]
```

### 6. Statistics

**Purpose**: Analytics and insights

**Sections:**
- Overview (total time, sessions, average satisfaction)
- Time per project (bar chart)
- Daily activity (calendar heat map)
- Hourly distribution (when do you work most?)
- Planning adherence (planned vs actual)
- Satisfaction trends (line chart over time)
- Tag usage (most used tags)

**Layout:**
```
[Time Range: This Month ▼]

Overview
┌──────────────┬──────────────┬──────────────┐
│ Total Time   │ Sessions     │ Avg Satisfy  │
│ 45h 30min   │ 42           │ 82/100      │
└──────────────┴──────────────┴──────────────┘

Time per Project
[Bar Chart]

Daily Activity (Heat Map)
[Calendar with color intensity based on work time]

Hourly Distribution
[Bar chart: 6AM - 11PM]

Planning Adherence
Planned sessions: 35
Executed: 28 (80%)
On-time starts: 22 (63%)

[More charts...]
```

### 7. Session Review (Phase 5)

**Route:** `/session-review/:id`

**Purpose**: Detailed session completion with feedback

**Accessed**: After clicking "Stop & Review" from web or tray

**Layout:**
```
Session Review

Project: Web Development
Planned: 60 minutes
Actual: 75 minutes
Started: 2025-12-30 14:00
Ended: 2025-12-30 15:15

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

How satisfied are you with your performance?

[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 80
0 ─────────────────────────────────── 100

Good job! You're making progress.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What did you accomplish?

┌─────────────────────────────────────┐
│ - Implemented user authentication   │
│ - Fixed login bug                   │
│ - Wrote unit tests                  │
│                                     │
└─────────────────────────────────────┘
145 / 500 characters

Personal Notes (Optional)

┌─────────────────────────────────────┐
│ Got distracted by emails midway.    │
│ Need to improve focus next time.    │
│                                     │
└─────────────────────────────────────┘
82 / 1000 characters

[Skip Review]  [Save & Continue]
```

**Features:**
- Session summary (read-only)
- Satisfaction slider (0-100, default 80)
- Dynamic feedback based on rating
- Tasks completed textarea (500 char limit)
- Personal notes textarea (1000 char limit)
- Character counters
- Skip or save options
- Redirects to Sessions page after save

**See:** `Documents/roadmap/5/session-review.md`

### 8. Settings (Phase 5)

**Route:** `/settings`

**Purpose**: Application configuration

**Sections:**
- General Settings
- Notification Settings (3 types)
- Sound Management

**Layout:**
```
Settings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
General Settings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Language
[English ▼]

Default Reminder Interval (minutes)
[10]
How often to remind about unstarted planned work.

Session Poll Interval (seconds)
[120]
How often to check for session updates.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Notification Settings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Planning Start Notification
When scheduled work time arrives

☑ Enable notifications

  ☑ Play sound

    Sound File
    [complete.oga ▼] [▶ Preview]

    Play Count
    [1 time ▼]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session End Notification
When session time is up (first notification)

☑ Enable notifications
  ☑ Play sound
    [complete.oga ▼] [▶ Preview]
    [1 time ▼]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session Reminder Notification
Repeated reminders after session time is up

☑ Enable notifications
  ☑ Play sound
    [dialog-warning.oga ▼] [▶ Preview]
    [2 times ▼]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Reset to Defaults]  [Save Changes]
```

**Features:**
- All settings editable in one page
- Sound preview without saving
- Per-notification-type configuration
- Bulk save (all changes at once)
- Reset to defaults option
- Real-time validation
- Available sounds auto-populated

**See:** `Documents/roadmap/5/settings.md` and `Documents/readme-settings.md`

## Components

### Start Session Dialog

**Trigger**: Click "Start Session" button

**Layout:**
```
Start New Session

Pinned Projects
┌──────────┐ ┌──────────┐ ┌──────────┐
│ 💻 Work  │ │ 📚 Study │ │ 🏃 Gym   │
└──────────┘ └──────────┘ └──────────┘

Recent Projects
[Client A] [Project X] [Email]

Or search/browse:
[Search projects: ________]
[All Projects ▼]

[No Project (Break)]

Duration: [60] minutes
Quick: [30] [60] [90] [120]

[Start] [Cancel]
```

### Review Session Dialog

**Trigger**: Click "Stop & Review" on active session

**Layout:**
```
Session Review

Project: Web Development
Duration: 92 minutes (90 planned)

How satisfied are you with this session?
[━━━━━━━━━━━━━━━━━━━━━━━━━●━━━━━━━] 80/100

What did you accomplish?
[________________________________]
[________________________________]

Additional notes:
[________________________________]

Tags:
[Available: development, testing, urgent, ...]
Selected: [development] [testing]

[Save] [Save & Start Next]
```

### Tag Selector Component

**Used in**: Planning form, Session review

**Layout:**
```
Select Tags

🔍 [Search or create tag...]

Frequent:
[urgent] [development] [meeting]

Global:
[urgent] [blocked] [quick-win] [waiting]

Current Project (Project X):
[development] [deployment]

From Parent Projects:
Client A: [review] [testing]
Work: [meeting] [email]

Selected (3): [development ×] [testing ×] [urgent ×]
```

## Notifications

All notifications use the existing notification service.

**In-App Notifications** (optional):
- Toast messages for actions (saved, deleted, etc.)
- Error messages
- Success confirmations

## Responsiveness

**Desktop** (primary):
- Full layout as described
- Optimal: 1280px+ width

**Tablet** (future):
- Simplified navigation
- Stacked layouts
- Touch-friendly controls

**Mobile** (future):
- Dedicated mobile app or PWA
- Condensed views
- Bottom navigation

## Keyboard Shortcuts

**Global:**
- `S`: Start session
- `P`: Add planning
- `Esc`: Close dialogs
- `/`: Focus search

**Navigation:**
- `1-6`: Jump to page (Dashboard, Projects, Tags, Planning, Sessions, Stats)

**Active Session:**
- `+`: Add 15 minutes
- `N`: Add note
- `Space`: Stop session

## Color Scheme

**Primary Colors:**
- Background: Light gray (#F5F5F5) or white
- Text: Dark gray (#333333)
- Accent: Blue (#3B82F6)
- Success: Green (#10B981)
- Warning: Yellow (#F59E0B)
- Error: Red (#EF4444)

**Project Colors:**
User-defined via color picker, used for:
- Project indicators
- Planning blocks
- Session tags

## Loading States

**Page Load:**
- Skeleton screens
- Progress indicators

**Actions:**
- Button loading states
- Optimistic UI updates

## Error Handling

**API Errors:**
- Toast notification with error message
- Retry option if applicable
- Rollback optimistic updates

**Validation Errors:**
- Inline field errors
- Form-level error summary

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus indicators
- Color contrast (WCAG AA)

## Technology Stack

- **Framework**: Vue 3 (Composition API)
- **State**: Pinia
- **Routing**: Vue Router
- **Styling**: Tailwind CSS
- **HTTP**: Axios
- **Charts**: Chart.js or ApexCharts
- **Date/Time**: Day.js
- **Notifications**: Custom integration with existing service

## File Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── assets/          # Images, fonts
│   ├── components/      # Reusable components
│   │   ├── SessionBanner.vue
│   │   ├── StartSessionDialog.vue
│   │   ├── ReviewDialog.vue
│   │   ├── TagSelector.vue
│   │   └── ...
│   ├── views/           # Page components
│   │   ├── Dashboard.vue
│   │   ├── Projects.vue
│   │   ├── Tags.vue
│   │   ├── Planning.vue
│   │   ├── Sessions.vue
│   │   └── Statistics.vue
│   ├── lang/            # i18n files
│   │   ├── en.json
│   │   └── fa.json (future)
│   ├── stores/          # Pinia stores
│   │   ├── projects.js
│   │   ├── tags.js
│   │   ├── planning.js
│   │   ├── sessions.js
│   │   └── settings.js
│   ├── services/        # API services
│   │   └── api.js
│   ├── router/
│   │   └── index.js
│   ├── App.vue
│   └── main.js
├── package.json
└── vite.config.js
```

## Future Enhancements

- Dark theme
- Drag-and-drop for planning
- Customizable dashboard
- Export/import data
- Calendar integrations
- Keyboard-only mode
- Progressive Web App (PWA)
- Mobile app
