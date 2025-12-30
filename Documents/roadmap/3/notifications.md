# Session Notifications

Background worker logic for session end notifications.

## Implementation

Update `backend/app/tasks/notification_worker.py`:

```python
async def _check_session_notifications(self, db: Session):
    """Check for active sessions that should trigger notifications."""
    # Get active session
    active_session = db.query(WorkSession).filter(
        WorkSession.end_time.is_(None)
    ).first()

    if not active_session:
        return

    # Skip if notifications disabled for this session
    if active_session.notification_disabled:
        return

    now = datetime.now()
    elapsed_minutes = (now - active_session.start_time).total_seconds() / 60

    # Check if session time has expired
    if elapsed_minutes < active_session.planned_duration:
        return  # Not yet time

    overtime_minutes = elapsed_minutes - active_session.planned_duration

    # Determine notification interval
    interval = 10  # Default
    if active_session.project and active_session.project.notification_interval:
        interval = active_session.project.notification_interval
    else:
        # Get global default from settings
        settings = db.query(Settings).filter(
            Settings.key_name == 'notification_interval_default'
        ).first()
        if settings:
            interval = int(settings.value_json)

    # Send notification at interval boundaries
    should_notify = False

    if overtime_minutes < 1:
        # First notification (just finished)
        should_notify = True
    else:
        # Repeated notifications at interval
        if int(overtime_minutes) % interval == 0:
            should_notify = True

    if should_notify:
        # Check if we sent notification recently (avoid duplicates)
        if not self._was_notification_sent_recently(active_session.id, 'session'):
            self._send_session_notification(active_session, overtime_minutes)
            self._mark_notification_sent(active_session.id, 'session')

def _send_session_notification(self, session: WorkSession, overtime: float):
    """Send notification for session end."""
    project_name = session.project.name if session.project else "Session"

    if overtime < 1:
        # Initial notification (time's up)
        title = f"Session Complete: {project_name}"
        message = f"Time is up! You've worked for {session.planned_duration} minutes.\n"
        message += "Consider taking a break or starting something else."
    else:
        # Repeated notification (overtime)
        title = f"Still Working: {project_name}"
        message = f"You're {int(overtime)} minutes over planned time.\n"
        message += f"Planned: {session.planned_duration} min, "
        message += f"Elapsed: {int(overtime + session.planned_duration)} min"

    notification_service.send_notification(
        title=title,
        message=message,
        urgency="normal"
    )
```

## Notification Flow

```
Every minute:
  ├─ Get active session
  ├─ If no active session → Skip
  ├─ If notifications disabled → Skip
  └─ Calculate elapsed time:
      ├─ < planned duration → Skip
      ├─ Just finished (< 1 min over) → Send initial notification
      └─ At interval (10 min over) → Send reminder
```

## Testing

1. Start a session with 2-minute duration
2. Wait for notification when 2 minutes pass
3. Don't stop session
4. Wait 10 minutes, should get reminder
5. Click "Disable Notifications"
6. Should stop getting reminders
7. Click "Enable Notifications"
8. Should resume getting reminders

## Checklist

- [ ] Session notification logic added to worker
- [ ] Initial "time's up" notification works
- [ ] Repeated "overtime" notifications work
- [ ] Respects notification_disabled flag
- [ ] Uses project-specific interval if set
- [ ] Falls back to global default interval
- [ ] No duplicate notifications
