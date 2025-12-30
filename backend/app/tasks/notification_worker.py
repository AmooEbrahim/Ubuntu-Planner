"""Background worker for sending planning notifications."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.planning import Planning
from app.models.session import Session as SessionModel
from app.services.notification_service import notification_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationWorker:
    """Background worker to check and send planning notifications."""

    def __init__(self):
        """Initialize notification worker."""
        self._notification_cache: Dict[str, datetime] = {}
        self._running = False

    async def start(self):
        """Start the notification worker."""
        self._running = True
        logger.info("Notification worker started")

        while self._running:
            try:
                await self._check_planning_notifications()
                # Check every minute
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in notification worker: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        """Stop the notification worker."""
        self._running = False
        logger.info("Notification worker stopped")

    async def _check_planning_notifications(self):
        """Check for planning that should trigger notifications."""
        db = SessionLocal()
        try:
            now = datetime.now()

            # Get planning that should have started (within last 5 minutes to now)
            window_start = now - timedelta(minutes=5)

            planning_list = (
                db.query(Planning)
                .filter(
                    Planning.scheduled_start >= window_start,
                    Planning.scheduled_start <= now,
                )
                .all()
            )

            for plan in planning_list:
                await self._process_planning_notification(db, plan, now)

        except Exception as e:
            logger.error(f"Error checking planning notifications: {e}")
        finally:
            db.close()

    async def _process_planning_notification(
        self, db: Session, plan: Planning, now: datetime
    ):
        """Process notification for a single planning item.

        Args:
            db: Database session
            plan: Planning item to process
            now: Current time
        """
        # Check if session started from this planning
        session_from_plan = (
            db.query(SessionModel).filter(SessionModel.planning_id == plan.id).first()
        )

        if session_from_plan:
            return  # Session started, no notification needed

        # Check if ANY session started after planning start time
        any_recent_session = (
            db.query(SessionModel)
            .filter(
                SessionModel.start_time >= plan.scheduled_start,
                SessionModel.end_time.is_(None),  # Still active
            )
            .first()
        )

        if any_recent_session:
            return  # User started a different session, don't nag

        # Calculate time since planning start
        elapsed_minutes = (now - plan.scheduled_start).total_seconds() / 60

        # Determine if we should send notification
        should_notify = False

        if elapsed_minutes < 1:
            # First notification (at start time)
            should_notify = True
        else:
            # Repeated notifications every N minutes
            interval = 10  # Default interval
            if plan.project and plan.project.notification_interval:
                interval = plan.project.notification_interval

            # Send if we're at an interval boundary (with 1 minute tolerance)
            minutes_since_last = elapsed_minutes % interval
            if minutes_since_last < 1:
                should_notify = True

        if should_notify:
            # Check if we already sent notification recently (avoid duplicates)
            if not self._was_notification_sent_recently(plan.id, "planning"):
                self._send_planning_notification(plan, elapsed_minutes)
                self._mark_notification_sent(plan.id, "planning")

    def _send_planning_notification(self, plan: Planning, elapsed_minutes: float):
        """Send notification for planning start.

        Args:
            plan: Planning item
            elapsed_minutes: Minutes elapsed since scheduled start
        """
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

        success = notification_service.send_notification(
            title=title, message=message, urgency=urgency
        )

        if success:
            logger.info(f"Sent planning notification for: {plan.project.name}")
        else:
            logger.warning(
                f"Failed to send planning notification for: {plan.project.name}"
            )

    def _was_notification_sent_recently(self, item_id: int, item_type: str) -> bool:
        """Check if notification was sent in last minute.

        Args:
            item_id: ID of the item
            item_type: Type of item (e.g., 'planning')

        Returns:
            True if notification was sent recently, False otherwise
        """
        key = f"{item_type}_{item_id}"
        last_sent = self._notification_cache.get(key)

        if not last_sent:
            return False

        return (datetime.now() - last_sent).total_seconds() < 60

    def _mark_notification_sent(self, item_id: int, item_type: str):
        """Mark that notification was sent.

        Args:
            item_id: ID of the item
            item_type: Type of item (e.g., 'planning')
        """
        key = f"{item_type}_{item_id}"
        self._notification_cache[key] = datetime.now()

        # Clean up old entries (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        keys_to_remove = [
            k for k, v in self._notification_cache.items() if v < cutoff_time
        ]
        for k in keys_to_remove:
            del self._notification_cache[k]


# Singleton instance
notification_worker = NotificationWorker()
