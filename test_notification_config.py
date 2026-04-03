#!/usr/bin/env python3
"""Test notification configuration retrieval."""

import sys
sys.path.insert(0, '/home/ebrhaim/bin/bash/Ubuntu-Planner/backend')

from app.core.database import SessionLocal
from app.services.notification_service import notification_service
from app.models.setting import Setting

db = SessionLocal()

try:
    print("=== Testing Notification Configuration ===\n")

    # Test planning_start
    print("1. Testing planning_start:")
    config = notification_service._get_notification_config("planning_start", db)
    print(f"   Config: {config}")
    print()

    # Test session_end
    print("2. Testing session_end:")
    config = notification_service._get_notification_config("session_end", db)
    print(f"   Config: {config}")
    print()

    # Test session_reminder
    print("3. Testing session_reminder:")
    config = notification_service._get_notification_config("session_reminder", db)
    print(f"   Config: {config}")
    print()

    # Check raw database values
    print("4. Raw database values:")
    for key in ['notification_planning_start_enabled', 'notification_session_end_enabled', 'notification_session_reminder_enabled']:
        setting = db.query(Setting).filter(Setting.key_name == key).first()
        if setting:
            print(f"   {key}:")
            print(f"     value_json = {setting.value_json}")
            print(f"     type = {type(setting.value_json)}")
            print(f"     bool check = {bool(setting.value_json)}")
            print(f"     not check = {not setting.value_json}")
        else:
            print(f"   {key}: NOT FOUND")
        print()

    # Test full notification creation for session_end
    print("5. Testing full notification config creation:")
    config_content = notification_service._create_config(
        title="Test Session Complete",
        message="Test message",
        urgency="normal",
        icon=None,
        timeout=5000,
        notification_type="session_end",
        db=db
    )
    print(config_content)

finally:
    db.close()
