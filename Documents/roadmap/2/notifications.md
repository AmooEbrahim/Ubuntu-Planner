# Planning Notifications

Background worker logic for planning start notifications.

## Overview

Send notifications when:
1. Planning start time arrives
2. User hasn't started a session (repeated every N minutes)

## Implementation

Update `backend/app/tasks/notification_worker.py` (created in Phase 0):

```python
from datetime import datetime, timedelta
from app.models.planning import Planning
from app.models.session import Session

class NotificationWorker:
    # ... existing code ...

    async def _check_planning_notifications(self, db: Session):
        """Check for planning that should trigger notifications."""
        now = datetime.now()

        # Get planning that should have started (within last 5 minutes to now)
        window_start = now - timedelta(minutes=5)

        planning_list = db.query(Planning).filter(
            Planning.scheduled_start >= window_start,
            Planning.scheduled_start <= now
        ).all()

        for plan in planning_list:
            # Check if session started from this planning
            session_from_plan = db.query(Session).filter(
                Session.planning_id == plan.id
            ).first()

            if session_from_plan:
                continue  # Session started, no notification needed

            # Check if ANY session started after planning start time
            any_recent_session = db.query(Session).filter(
                Session.start_time >= plan.scheduled_start,
                Session.end_time.is_(None)  # Still active
            ).first()

            if any_recent_session:
                continue  # User started a different session, don't nag

            # Calculate time since planning start
            elapsed_minutes = (now - plan.scheduled_start).total_seconds() / 60

            # Determine if we should send notification
            should_notify = False

            if elapsed_minutes < 1:
                # First notification (at start time)
                should_notify = True
            else:
                # Repeated notifications every 10 minutes (or project-specific)
                interval = 10  # Default
                if plan.project and plan.project.notification_interval:
                    interval = plan.project.notification_interval

                # Send if we're at an interval boundary
                if int(elapsed_minutes) % interval == 0:
                    should_notify = True

            if should_notify:
                # Check if we already sent notification recently (avoid duplicates)
                if not self._was_notification_sent_recently(plan.id, 'planning'):
                    self._send_planning_notification(plan, elapsed_minutes)
                    self._mark_notification_sent(plan.id, 'planning')

    def _send_planning_notification(self, plan: Planning, elapsed_minutes: float):
        """Send notification for planning start."""
        urgency = "critical" if plan.priority == "critical" else "normal"

        if elapsed_minutes < 1:
            # Initial notification
            title = "Scheduled Work"
            message = f"Time to start: {plan.project.name}"
            if plan.description:
                message += f"\n{plan.description}"
        else:
            # Reminder notification
            title = "Planning Reminder"
            message = f"Reminder: {plan.project.name}"
            message += f"\nScheduled {int(elapsed_minutes)} minutes ago"
            if plan.description:
                message += f"\n{plan.description}"

        notification_service.send_notification(
            title=title,
            message=message,
            urgency=urgency
        )

    # Helper methods for tracking sent notifications
    # (Implement using a simple in-memory cache or database table)

    _notification_cache = {}

    def _was_notification_sent_recently(self, item_id: int, item_type: str) -> bool:
        """Check if notification was sent in last minute."""
        key = f"{item_type}_{item_id}"
        last_sent = self._notification_cache.get(key)

        if not last_sent:
            return False

        return (datetime.now() - last_sent).total_seconds() < 60

    def _mark_notification_sent(self, item_id: int, item_type: str):
        """Mark that notification was sent."""
        key = f"{item_type}_{item_id}"
        self._notification_cache[key] = datetime.now()
```

## Notification Flow

```
Every minute:
  ├─ Get planning in time window (past 5 min to now)
  ├─ For each planning:
  │   ├─ Check if session started from this planning → Skip
  │   ├─ Check if any session started → Skip
  │   └─ Calculate elapsed time:
  │       ├─ < 1 min → Send initial notification
  │       └─ At interval (10 min) → Send reminder
  └─ Mark notification as sent
```

## Testing

Test notifications:
1. Create planning for 2 minutes from now
2. Wait for notification to appear
3. Don't start session
4. Wait 10 minutes, should get reminder
5. Start any session
6. Should stop getting reminders

## Checklist

- [ ] Planning notification logic added to worker
- [ ] Initial notification works
- [ ] Repeated notifications work
- [ ] Stops when session started
- [ ] Priority affects urgency
- [ ] No duplicate notifications
- [ ] Project-specific interval respected
