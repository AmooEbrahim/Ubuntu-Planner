# Phase 2: Planning

Implement work scheduling with calendar UI, overlap detection, and notifications.

## Objectives

- Create Planning CRUD (backend + frontend)
- Build calendar interface for daily/weekly view
- Implement overlap detection
- Implement priority system (low, medium, critical)
- Set up planning start notifications
- Integrate with background worker

## Dependencies

- Phase 0: Complete (database, basic setup)
- Phase 1: Complete (projects and tags exist)

## What We're Building

### Backend
- Planning model (already in database)
- Planning-Tags many-to-many relationship
- CRUD API endpoints
- Overlap detection logic
- Validation (same-day constraint)

### Frontend
- Planning calendar view (daily/weekly)
- Planning form (create/edit)
- Quick add functionality
- Filter by project/priority/tags
- Visual indicators for priorities

### Background Worker
- Check for planning start times
- Send notifications when planning is due
- Repeated notifications if not started

## Success Criteria

- [ ] Can create planning via calendar UI
- [ ] Overlap detection prevents conflicts
- [ ] Same-day validation works
- [ ] Can view planning in calendar (daily/weekly)
- [ ] Can edit/delete planning
- [ ] Priority system works (visual + functional)
- [ ] Notifications sent at planning start time
- [ ] Repeated notifications work correctly
- [ ] Can filter by project, priority, tags

## Files

- `overview.md` - This file
- `planning-backend.md` - Backend implementation
- `planning-frontend.md` - Frontend calendar and forms
- `notifications.md` - Notification logic for planning

## Next Phase

Phase 3: Sessions/Execution
