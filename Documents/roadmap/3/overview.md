# Phase 3: Sessions / Execution

Implement actual work tracking with sessions, reviews, and real-time UI.

## Objectives

- Create Sessions CRUD (backend + frontend)
- Build active session banner in web UI
- Implement session start/stop workflows
- Create session review form
- Implement session end notifications
- Add quick actions (add time, add note, disable notifications)

## Dependencies

- Phase 0: Complete
- Phase 1: Complete (projects and tags)
- Phase 2: Complete (planning exists for integration)

## What We're Building

### Backend
- Session model (already in database)
- Session-Tags many-to-many
- CRUD API endpoints
- Single active session enforcement
- Session duration calculation

### Frontend
- Active session banner (persistent across all pages)
- Start session dialog
- Session review form
- Quick actions during session
- Sessions history page

### Background Worker
- Check active session duration
- Send notifications when time expires
- Repeated notifications

## Success Criteria

- [ ] Can start session from web UI
- [ ] Can start from planning or ad-hoc
- [ ] Only one active session at a time
- [ ] Active session banner shows in all pages
- [ ] Can add notes during session
- [ ] Can add 15 minutes to active session
- [ ] Can disable notifications
- [ ] Can stop session (quick or with review)
- [ ] Session review form works
- [ ] Notifications sent when session time expires
- [ ] Repeated notifications work
- [ ] Can view session history

## Files

- `overview.md` - This file
- `sessions-backend.md` - Backend API
- `sessions-frontend.md` - Frontend UI
- `session-banner.md` - Active session banner component
- `notifications.md` - Session notifications

## Next Phase

Phase 4: Statistics & Polish
