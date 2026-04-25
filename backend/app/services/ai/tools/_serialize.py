"""Serialization helpers shared across tool modules."""
from __future__ import annotations

from typing import Any, Dict


def serialize_project(project) -> Dict[str, Any]:
    if project is None:
        return None
    return {
        "id": project.id,
        "name": project.name,
        "parent_id": project.parent_id,
        "color": project.color,
        "description": project.description,
        "default_duration": project.default_duration,
        "is_archived": project.is_archived,
        "is_pinned": project.is_pinned,
    }


def serialize_tag(tag) -> Dict[str, Any]:
    if tag is None:
        return None
    return {
        "id": tag.id,
        "name": tag.name,
        "color": tag.color,
        "project_id": tag.project_id,
    }


def serialize_planning(plan) -> Dict[str, Any]:
    if plan is None:
        return None
    return {
        "id": plan.id,
        "project_id": plan.project_id,
        "scheduled_start": plan.scheduled_start.isoformat() if plan.scheduled_start else None,
        "scheduled_end": plan.scheduled_end.isoformat() if plan.scheduled_end else None,
        "priority": plan.priority.value if hasattr(plan.priority, "value") else plan.priority,
        "description": plan.description,
        "project": serialize_project(getattr(plan, "project", None)),
        "tags": [serialize_tag(t) for t in (getattr(plan, "tags", []) or [])],
    }


def serialize_session(session) -> Dict[str, Any]:
    if session is None:
        return None
    return {
        "id": session.id,
        "project_id": session.project_id,
        "planning_id": session.planning_id,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "planned_duration": session.planned_duration,
        "actual_duration": session.actual_duration,
        "notes": session.notes,
        "satisfaction_score": session.satisfaction_score,
        "tasks_done": session.tasks_done,
        "notification_disabled": session.notification_disabled,
        "project": serialize_project(getattr(session, "project", None)),
        "tags": [serialize_tag(t) for t in (getattr(session, "tags", []) or [])],
    }


def serialize_day_memory(row) -> Dict[str, Any]:
    if row is None:
        return None
    return {
        "id": row.id,
        "date": row.date.isoformat() if row.date else None,
        "is_ai": bool(row.is_ai),
        "intentions": row.intentions,
        "reflection": row.reflection,
        "lessons": row.lessons,
        "completed": row.completed,
        "gratitude": row.gratitude,
        "free_notes": row.free_notes,
        "mood": row.mood,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }
