"""Seed script for test data. Clears all existing data and populates with sample data."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from sqlalchemy import text

def clear_all_data(db):
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    db.execute(text("DELETE FROM session_tags"))
    db.execute(text("DELETE FROM planning_tags"))
    db.execute(text("DELETE FROM sessions"))
    db.execute(text("DELETE FROM planning"))
    db.execute(text("DELETE FROM tags"))
    db.execute(text("DELETE FROM projects"))
    db.execute(text("ALTER TABLE projects AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE tags AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE planning AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE sessions AUTO_INCREMENT = 1"))
    db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    db.commit()
    print("Cleared all data and reset auto-increment")

def seed(db):
    # --- Projects ---
    projects = [
        ("Website Redesign", None, "#6366f1", "Complete overhaul of the company website", 90, True),
        ("Mobile App", None, "#10b981", "Cross-platform mobile application", 120, True),
        ("Backend API", None, "#f59e0b", "REST API development and maintenance", 60, False),
        ("Data Analytics", None, "#ec4899", "Analytics dashboard and reporting", 60, False),
    ]

    for name, parent_id, color, desc, duration, pinned in projects:
        db.execute(text(
            "INSERT INTO projects (name, parent_id, color, description, default_duration, is_archived, is_pinned, created_at, updated_at) "
            "VALUES (:name, :parent_id, :color, :desc, :duration, 0, :pinned, NOW(), NOW())"
        ), {"name": name, "parent_id": parent_id, "color": color, "desc": desc, "duration": duration, "pinned": pinned})

    db.commit()
    # Get IDs for root projects
    root_ids = {}
    for name, _, _, _, _, _ in projects:
        row = db.execute(text("SELECT id FROM projects WHERE name = :name"), {"name": name}).first()
        root_ids[name] = row[0]

    # Child projects
    children = [
        ("UI Design", "Website Redesign", "#8b5cf6", "Figma mockups and design system", 60, False),
        ("Frontend Dev", "Website Redesign", "#a855f7", "React/Next.js implementation", 90, False),
        ("iOS Development", "Mobile App", "#34d399", "Swift implementation", 90, False),
        ("Android Development", "Mobile App", "#059669", "Kotlin implementation", 90, False),
        ("Database Migration", "Backend API", "#f97316", "PostgreSQL migration scripts", 45, False),
        ("API Documentation", "Backend API", "#eab308", "OpenAPI/Swagger docs", 30, False),
    ]

    for name, parent_name, color, desc, duration, pinned in children:
        parent_id = root_ids[parent_name]
        db.execute(text(
            "INSERT INTO projects (name, parent_id, color, description, default_duration, is_archived, is_pinned, created_at, updated_at) "
            "VALUES (:name, :parent_id, :color, :desc, :duration, 0, :pinned, NOW(), NOW())"
        ), {"name": name, "parent_id": parent_id, "color": color, "desc": desc, "duration": duration, "pinned": pinned})

    db.commit()
    print(f"Created 10 projects")

    # --- Tags ---
    tags = [
        ("urgent", "#ef4444", None),
        ("review", "#3b82f6", None),
        ("research", "#8b5cf6", None),
        ("bugfix", "#f97316", None),
        ("feature", "#10b981", None),
        ("testing", "#ec4899", None),
        ("documentation", "#6366f1", None),
        ("meeting", "#64748b", None),
        ("frontend", "#a855f7", root_ids["Website Redesign"]),
        ("backend", "#f59e0b", root_ids["Backend API"]),
    ]

    for name, color, project_id in tags:
        db.execute(text(
            "INSERT INTO tags (name, color, project_id, created_at, updated_at) "
            "VALUES (:name, :color, :project_id, NOW(), NOW())"
        ), {"name": name, "color": color, "project_id": project_id})

    db.commit()
    print("Created 10 tags")

    # Get tag IDs
    tag_ids = {}
    for name, _, _ in tags:
        row = db.execute(text("SELECT id FROM tags WHERE name = :name"), {"name": name}).first()
        tag_ids[name] = row[0]

    # Get project IDs for planning
    proj_ids = {}
    all_proj_names = [p[0] for p in projects] + [c[0] for c in children]
    for name in all_proj_names:
        row = db.execute(text("SELECT id FROM projects WHERE name = :name"), {"name": name}).first()
        proj_ids[name] = row[0]

    # --- Planning entries ---
    planning_entries = [
        # April 3 (yesterday)
        ("Website Redesign", "2026-04-03 09:00:00", "2026-04-03 10:30:00", "critical", "Review homepage wireframes"),
        ("Mobile App", "2026-04-03 11:00:00", "2026-04-03 12:00:00", "medium", "Setup React Native environment"),
        ("Backend API", "2026-04-03 14:00:00", "2026-04-03 15:00:00", "low", "Write API documentation for auth endpoints"),
        ("UI Design", "2026-04-03 15:30:00", "2026-04-03 16:30:00", "medium", "Design system color palette"),

        # April 4 (today)
        ("Website Redesign", "2026-04-04 09:00:00", "2026-04-04 10:30:00", "critical", "Finalize homepage design"),
        ("Frontend Dev", "2026-04-04 10:30:00", "2026-04-04 12:00:00", "critical", "Implement responsive navigation"),
        ("Backend API", "2026-04-04 13:00:00", "2026-04-04 14:00:00", "medium", "Review and merge PR #42"),
        ("iOS Development", "2026-04-04 14:00:00", "2026-04-04 15:30:00", "medium", "Implement push notification service"),
        ("Data Analytics", "2026-04-04 16:00:00", "2026-04-04 17:00:00", "low", "Setup analytics tracking events"),

        # April 5 (tomorrow)
        ("Mobile App", "2026-04-05 09:00:00", "2026-04-05 11:00:00", "critical", "Build login screen components"),
        ("Android Development", "2026-04-05 11:00:00", "2026-04-05 12:30:00", "medium", "Implement bottom navigation"),
        ("Database Migration", "2026-04-05 14:00:00", "2026-04-05 14:45:00", "low", "Run migration scripts on staging"),
        ("Website Redesign", "2026-04-05 15:00:00", "2026-04-05 16:30:00", "medium", "Implement contact page"),
        ("API Documentation", "2026-04-05 16:30:00", "2026-04-05 17:00:00", "low", "Update API docs with new endpoints"),
    ]

    planning_ids = []
    for proj_name, start, end, priority, desc in planning_entries:
        result = db.execute(text(
            "INSERT INTO planning (project_id, scheduled_start, scheduled_end, priority, description, created_at, updated_at) "
            "VALUES (:project_id, :start, :end, :priority, :desc, NOW(), NOW())"
        ), {"project_id": proj_ids[proj_name], "start": start, "end": end, "priority": priority, "desc": desc})
        planning_ids.append(result.lastrowid)

    db.commit()
    print(f"Created {len(planning_entries)} planning entries")

    # --- Sessions ---
    sessions = [
        # April 3 sessions (completed)
        ("Website Redesign", "2026-04-03 09:05:00", "2026-04-03 10:20:00", 90, 85, "Reviewed all 5 pages, approved 3, requested changes on 2", "Completed wireframe review, left some notes on Figma", planning_ids[0]),
        ("Mobile App", "2026-04-03 11:10:00", "2026-04-03 12:30:00", 120, 70, "Had some issues with CocoaPods but resolved", "Setup complete, created first test project", planning_ids[1]),
        ("Backend API", "2026-04-03 14:00:00", "2026-04-03 14:45:00", 60, 60, None, "Documented auth and user endpoints", planning_ids[2]),
        ("UI Design", "2026-04-03 15:30:00", "2026-04-03 16:45:00", 60, 90, "Created 3 theme variants", "Finalized color palette and typography scale", planning_ids[3]),

        # April 4 sessions
        ("Website Redesign", "2026-04-04 09:00:00", "2026-04-04 10:15:00", 90, 80, "Still need hero section animation", "Homepage design 90% done", planning_ids[4]),
        ("Frontend Dev", "2026-04-04 10:30:00", "2026-04-04 11:45:00", 90, 75, "Mobile menu needs more work", "Navigation component built", planning_ids[5]),
        ("Backend API", "2026-04-04 13:00:00", "2026-04-04 13:50:00", 60, 90, None, "Reviewed 3 PRs, merged 2", planning_ids[6]),
        # Active session (no end_time)
        ("iOS Development", "2026-04-04 14:00:00", None, 90, None, None, None, planning_ids[7]),
    ]

    for proj_name, start, end, planned, satisfaction, tasks, notes, planning_id in sessions:
        db.execute(text(
            "INSERT INTO sessions (project_id, start_time, end_time, planned_duration, satisfaction_score, tasks_done, notes, planning_id, notification_disabled, created_at, updated_at) "
            "VALUES (:project_id, :start, :end, :planned, :satisfaction, :tasks, :notes, :planning_id, 0, NOW(), NOW())"
        ), {
            "project_id": proj_ids[proj_name], "start": start, "end": end,
            "planned": planned, "satisfaction": satisfaction,
            "tasks": tasks, "notes": notes, "planning_id": planning_id
        })

    db.commit()
    print(f"Created {len(sessions)} sessions")

    # Get session IDs
    session_ids = []
    for proj_name, start, _, _, _, _, _, _ in sessions:
        row = db.execute(text(
            "SELECT id FROM sessions WHERE project_id = :pid AND start_time = :start ORDER BY id DESC LIMIT 1"
        ), {"pid": proj_ids[proj_name], "start": start}).first()
        session_ids.append(row[0])

    # --- Session tags ---
    session_tags = [
        (session_ids[0], tag_ids["urgent"]),
        (session_ids[0], tag_ids["review"]),
        (session_ids[1], tag_ids["feature"]),
        (session_ids[1], tag_ids["testing"]),
        (session_ids[2], tag_ids["documentation"]),
        (session_ids[3], tag_ids["research"]),
        (session_ids[4], tag_ids["urgent"]),
        (session_ids[4], tag_ids["frontend"]),
        (session_ids[5], tag_ids["frontend"]),
        (session_ids[6], tag_ids["meeting"]),
        (session_ids[7], tag_ids["backend"]),
    ]

    for sid, tid in session_tags:
        db.execute(text(
            "INSERT INTO session_tags (session_id, tag_id) VALUES (:session_id, :tag_id)"
        ), {"session_id": sid, "tag_id": tid})

    db.commit()
    print(f"Created {len(session_tags)} session-tag links")

    # --- Planning tags ---
    planning_tags = [
        (planning_ids[0], tag_ids["review"]),
        (planning_ids[1], tag_ids["feature"]),
        (planning_ids[2], tag_ids["documentation"]),
        (planning_ids[3], tag_ids["research"]),
        (planning_ids[4], tag_ids["urgent"]),
        (planning_ids[5], tag_ids["frontend"]),
        (planning_ids[6], tag_ids["meeting"]),
        (planning_ids[7], tag_ids["feature"]),
        (planning_ids[8], tag_ids["urgent"]),
        (planning_ids[9], tag_ids["research"]),
        (planning_ids[10], tag_ids["feature"]),
        (planning_ids[11], tag_ids["frontend"]),
        (planning_ids[12], tag_ids["backend"]),
        (planning_ids[13], tag_ids["frontend"]),
    ]

    for pid, tid in planning_tags:
        db.execute(text(
            "INSERT INTO planning_tags (planning_id, tag_id) VALUES (:planning_id, :tag_id)"
        ), {"planning_id": pid, "tag_id": tid})

    db.commit()
    print(f"Created {len(planning_tags)} planning-tag links")

def main():
    db = SessionLocal()
    try:
        clear_all_data(db)
        seed(db)
        print("\nSeeding complete!")
    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
