# Phase 1: Projects & Tags

Implement core project and tag management with full CRUD operations.

## Objectives

- Create Projects management system (backend + frontend)
- Create Tags management system (backend + frontend)
- Implement hierarchical project structure
- Implement tag inheritance (global/project-specific)
- Build functional UI for both features

## Why This Phase First?

Projects and Tags are foundational:
- All other features depend on Projects
- Tags are used by both Planning and Sessions
- Getting these right early makes everything else easier

## What We're Building

### 1. Projects Feature
**Backend:**
- SQLAlchemy model (already created in Phase 0)
- CRUD API endpoints
- Business logic for hierarchical structure
- Validation (circular references, etc.)

**Frontend:**
- Projects list page with tree view
- Create/Edit project form
- Archive/Unarchive functionality
- Pin/Unpin functionality
- Delete with warnings

### 2. Tags Feature
**Backend:**
- SQLAlchemy model
- CRUD API endpoints
- Tag inheritance logic
- Validation (uniqueness per scope)

**Frontend:**
- Tags management page
- Tag selector component (reusable)
- Color picker integration
- Project scope selector

## Success Criteria

- [ ] Can create, edit, delete projects via web UI
- [ ] Can create nested projects (unlimited depth)
- [ ] Can archive/unarchive projects
- [ ] Can pin/unpin projects
- [ ] Can create, edit, delete tags via web UI
- [ ] Can assign tags to projects or make them global
- [ ] Tag inheritance works correctly
- [ ] UI is clean and functional
- [ ] All validation works correctly

## Out of Scope

- Planning (Phase 2)
- Sessions (Phase 3)
- Statistics (Phase 4)
- Advanced UI features

## Files to Create

See detailed implementation in:
- `projects-backend.md` - Backend implementation for projects
- `projects-frontend.md` - Frontend implementation for projects
- `tags-backend.md` - Backend implementation for tags
- `tags-frontend.md` - Frontend implementation for tags
- `testing.md` - Testing checklist

## Estimated Complexity

**Medium** - Straightforward CRUD with some complexity in:
- Hierarchical project structure
- Tag inheritance logic
- Tree view UI

## Dependencies

- Phase 0 must be complete
- Database schema already created
- Basic models already defined

## Next Phase

After completing Phase 1, proceed to Phase 2 (Planning).
