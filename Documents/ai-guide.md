# AI Development Guide

Guidelines for AI assistants working on Ubuntu Planner project.

## Purpose

This document provides instructions for AI assistants to:
- Understand the project structure and standards
- Follow consistent coding practices
- Navigate version roadmaps
- Maintain code quality

## Code Standards

### General Principles

1. **Standard and Clean Code**
   - Follow Python PEP 8 style guide
   - Follow Vue.js style guide
   - Write modular, reusable code
   - Use meaningful variable and function names

2. **English for Code**
   - All code in English
   - All comments in English
   - All documentation in English
   - Variable names, function names, class names: English only

3. **Internationalization (i18n)**
   - User-facing text in separate language files
   - Support multiple languages via `lang/` directory
   - Default language: English
   - Future support: Persian/Farsi, others

4. **Organization**
   - Separate files for different concerns
   - Classes for logical groupings
   - Clear directory structure
   - No monolithic files

### Python Backend Standards

**Code Style:**
- PEP 8 compliance
- Type hints for function parameters and returns
- Docstrings for modules, classes, and functions (Google style)
- Max line length: 100 characters

**Example:**
```python
from typing import Optional, List
from datetime import datetime

def create_session(
    project_id: Optional[int],
    planned_duration: int,
    start_time: Optional[datetime] = None
) -> Session:
    """Create a new work session.

    Args:
        project_id: ID of the project, or None for projectless session
        planned_duration: Planned session duration in minutes
        start_time: Session start time, defaults to now

    Returns:
        Created session object

    Raises:
        ValueError: If another session is already active
    """
    # Implementation
    pass
```

**Structure:**
- Use SQLAlchemy models
- Service layer for business logic
- API layer thin (routing only)
- Separate files for models, services, API routes

**Error Handling:**
- Custom exceptions for business logic errors
- Proper HTTP status codes
- Detailed error messages
- Log errors appropriately

### Frontend Standards

**Code Style:**
- Vue 3 Composition API (preferred over Options API)
- TypeScript optional but recommended
- ESLint + Prettier for formatting
- Component naming: PascalCase

**Example:**
```vue
<script setup>
import { ref, computed } from 'vue'
import { useProjectStore } from '@/stores/projects'

const projectStore = useProjectStore()
const selectedProject = ref(null)

const activeProjects = computed(() =>
  projectStore.projects.filter(p => !p.is_archived)
)

function startSession() {
  // Implementation
}
</script>

<template>
  <div class="session-start">
    <!-- Template -->
  </div>
</template>
```

**Structure:**
- Single File Components (.vue)
- Composables for reusable logic
- Pinia stores for state management
- Separate API service layer

**Styling:**
- Tailwind CSS utility classes
- Custom CSS only when necessary
- Consistent spacing and sizing
- Responsive design considerations

### Database Standards

- Use Alembic migrations for all schema changes
- Never modify database directly
- Foreign keys for relationships
- Appropriate indexes for performance
- Consistent naming: snake_case for tables and columns

### Configuration

- **Environment Variables**: `.env` file for sensitive config
- **Settings File**: `settings.py` or similar for app config
- **Never commit secrets**: Use `.env.example` as template

**Example .env:**
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=os_services_planner

NOTIFICATION_HOST=localhost
NOTIFICATION_PORT=52346
```

## Project Structure Understanding

### Repository Layout
```
Ubuntu-Planner/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── services/    # Business logic
│   │   ├── tasks/       # Background tasks
│   │   └── main.py      # App entry point
│   ├── alembic/         # Database migrations
│   ├── tests/           # Backend tests
│   └── requirements.txt
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── views/       # Page components
│   │   ├── stores/      # Pinia stores
│   │   ├── services/    # API services
│   │   ├── lang/        # i18n language files
│   │   └── main.js
│   └── package.json
├── Documents/           # All documentation
│   ├── roadmap/        # Version roadmaps
│   ├── readme-*.md     # Feature docs
│   └── ai-guide.md     # This file
├── .env                # Environment config (not committed)
├── .env.example        # Environment template
└── README.md           # Main readme
```

### Key Files

- **Backend entry**: `backend/app/main.py`
- **Frontend entry**: `frontend/src/main.js`
- **Database models**: `backend/app/models/`
- **API routes**: `backend/app/api/`
- **Vue components**: `frontend/src/components/` and `frontend/src/views/`

## Working with Roadmaps

### Roadmap Structure

Roadmaps are organized by version in `Documents/roadmap/`:
```
Documents/roadmap/
├── 0/              # Phase 0: Setup
│   ├── setup.md
│   └── ...
├── 1/              # Phase 1: Core features
│   └── ...
└── 2/              # Phase 2: Advanced features
    └── ...
```

### How to Use Roadmaps

**When asked to implement a version:**

1. **Navigate to roadmap**:
   ```
   Read: Documents/roadmap/{version}/
   ```

2. **Read all files** in that version's directory:
   - Understand objectives
   - Review implementation steps
   - Check dependencies

3. **Follow the plan**:
   - Implement features in specified order
   - Check off completed items
   - Report progress

4. **Refer to feature docs**:
   - Use `Documents/readme-*.md` for detailed specs
   - Follow database schema in `readme-database.md`
   - Match UI specs in `readme-web-interface.md`

**Example interaction:**
```
User: "Implement version 0"

AI:
1. Read Documents/roadmap/0/setup.md
2. Review checklist and steps
3. Execute setup tasks:
   - Create database schema
   - Set up FastAPI project
   - Set up Vue project
   - Configure environment
4. Report completion
```

## Development Workflow

### Starting New Feature

1. **Understand requirements**:
   - Read relevant `readme-*.md` files
   - Check database schema
   - Review UI specifications

2. **Plan implementation**:
   - Database changes (if needed)
   - Backend API endpoints
   - Frontend components
   - Integration points

3. **Implement backend first**:
   - Models (if new)
   - Services (business logic)
   - API routes
   - Tests

4. **Implement frontend**:
   - Components
   - Store (if needed)
   - API integration
   - Styling

5. **Test integration**:
   - Manual testing
   - Check edge cases
   - Verify error handling

### Code Review Checklist

Before considering a feature complete:

- [ ] Code follows style standards
- [ ] Type hints/annotations present (Python)
- [ ] Error handling implemented
- [ ] User-facing text in language files
- [ ] Comments for complex logic
- [ ] No hardcoded values (use config)
- [ ] Database migrations created (if schema changed)
- [ ] API documented (FastAPI auto-docs)
- [ ] Frontend state management correct
- [ ] Responsive design considered
- [ ] Tested common and edge cases

## Common Patterns

### Backend API Endpoint Pattern

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.project import Project
from ..services.project_service import ProjectService
from ..dependencies import get_project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/", response_model=List[Project])
async def list_projects(
    include_archived: bool = False,
    service: ProjectService = Depends(get_project_service)
):
    """List all projects."""
    return service.get_projects(include_archived=include_archived)

@router.post("/", response_model=Project, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    service: ProjectService = Depends(get_project_service)
):
    """Create a new project."""
    try:
        return service.create_project(project_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Frontend Component Pattern

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useProjectStore } from '@/stores/projects'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const projectStore = useProjectStore()
const loading = ref(false)
const error = ref(null)

onMounted(async () => {
  await loadProjects()
})

async function loadProjects() {
  loading.value = true
  error.value = null
  try {
    await projectStore.fetchProjects()
  } catch (e) {
    error.value = t('errors.failed_to_load_projects')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="projects-list">
    <div v-if="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Content -->
    </div>
  </div>
</template>
```

### Notification Pattern

```python
import socket
import json
import tempfile
import os

def send_notification(title: str, message: str, urgency: str = 'normal'):
    """Send notification using existing notification service.

    Args:
        title: Notification title
        message: Notification message
        urgency: Urgency level (low, normal, critical)
    """
    # Create temporary config file
    config = {
        'title': title,
        'message': message,
        'urgency': urgency
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    try:
        # Send config path to notification service
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            sock.connect(('localhost', 52346))
            sock.sendall(f"{config_path}\n".encode('utf-8'))
    finally:
        # Clean up temp file
        try:
            os.unlink(config_path)
        except:
            pass
```

## Testing

### Backend Tests
- Use pytest
- Test services, not just routes
- Mock external dependencies
- Test edge cases and error conditions

### Frontend Tests
- Use Vitest + Vue Test Utils
- Test component behavior
- Test user interactions
- Mock API calls

## Debugging

### Common Issues

1. **CORS errors**: Check FastAPI CORS middleware
2. **Database connection**: Verify .env credentials
3. **Notification not working**: Check service is running on port 52346
4. **Active session conflict**: Check for existing active sessions in DB

## Performance Considerations

- **Database**: Use indexes, avoid N+1 queries
- **API**: Pagination for large lists
- **Frontend**: Lazy loading, virtual scrolling for long lists
- **Background tasks**: Use async where appropriate

## Security

- **No authentication required** (localhost only)
- **SQL injection**: Use ORM (SQLAlchemy) parameterized queries
- **XSS**: Vue escapes by default, be careful with v-html
- **Secrets**: Never commit .env file

## Deployment

- **systemd service**: For auto-start
- **Database migrations**: Run Alembic migrations on deployment
- **Static files**: Build frontend, serve from backend

## Version History

Track major changes:
- Version 0: Initial setup
- Version 1: Core features (projects, planning, execution)
- Version 2: Advanced features (stats, optimizations)

## Questions and Clarifications

When uncertain:
1. Check relevant `readme-*.md` documentation
2. Check database schema
3. Check existing code patterns
4. Ask user for clarification

## Summary

**Key Points:**
- Code in English, UI text in language files
- Follow standard patterns and structure
- Refer to roadmap for version implementation
- Maintain clean, modular code
- Test thoroughly
- Document as you go

**When implementing a version:**
1. Go to `Documents/roadmap/{version}/`
2. Read all markdown files
3. Follow implementation steps
4. Use `Documents/readme-*.md` for detailed specs
5. Report progress and completion
