"""add_notification_settings

Revision ID: d18df8ecd983
Revises: c551c22e5004
Create Date: 2025-12-30 12:41:29.947220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd18df8ecd983'
down_revision: Union[str, None] = 'c551c22e5004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add notification settings for sound configuration."""
    # Insert default notification settings
    op.execute("""
        INSERT INTO settings (key_name, value_json) VALUES
        ('notification_planning_start_enabled', 'true'),
        ('notification_planning_start_configuration', '{"sound_enabled": true, "sound_file": "complete.oga", "sound_repeat": 1}'),
        ('notification_session_end_enabled', 'true'),
        ('notification_session_end_configuration', '{"sound_enabled": true, "sound_file": "complete.oga", "sound_repeat": 1}'),
        ('notification_session_reminder_enabled', 'true'),
        ('notification_session_reminder_configuration', '{"sound_enabled": true, "sound_file": "dialog-warning.oga", "sound_repeat": 2}')
        ON DUPLICATE KEY UPDATE key_name=key_name
    """)


def downgrade() -> None:
    """Remove notification settings."""
    op.execute("""
        DELETE FROM settings WHERE key_name IN (
            'notification_planning_start_enabled',
            'notification_planning_start_configuration',
            'notification_session_end_enabled',
            'notification_session_end_configuration',
            'notification_session_reminder_enabled',
            'notification_session_reminder_configuration'
        )
    """)
