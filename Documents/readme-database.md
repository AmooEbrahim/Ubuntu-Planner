# Database Schema

Database structure for Ubuntu Planner using MySQL.

## Database Name

`os_services_planner`

## Connection

- **Host**: stored in `.env` file `DB_HOST`
- **User**: stored in `.env` file `DB_USERNAME`
- **Password**: stored in `.env` file `DB_PASSWORD`
- **Engine**: stored in `.env` file `DB_CONNECTION` (for now we support MySQL)
- **Engine**: stored in `.env` file `DB_DATABASE` (for now we support MySQL)

## Tables

### 1. projects

Stores project information with hierarchical structure.

```sql
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INT NULL,
    color VARCHAR(7) NOT NULL,  -- Hex color code
    description TEXT NULL,
    default_duration INT NOT NULL DEFAULT 60,  -- minutes
    notification_interval INT NULL,  -- minutes, NULL = use global default
    is_archived BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES projects(id) ON DELETE SET NULL
);
```

**Key Points:**
- `parent_id`: Allows unlimited nesting depth
- `default_duration`: Default session length for this project
- `notification_interval`: How often to repeat notifications (NULL = use global setting)
- `is_archived`: Archived projects don't show in selection lists
- `is_pinned`: Pinned projects show in quick-start menu

### 2. tags

Stores tags that can be global or project-specific.

```sql
CREATE TABLE tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) NOT NULL,  -- Hex color code
    project_id INT NULL,  -- NULL = global tag
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_tag_per_project (name, project_id)
);
```

**Key Points:**
- `project_id = NULL`: Tag is global (usable by all projects)
- `project_id = X`: Tag is specific to project X (and its children)
- Tags from parent projects are inherited by children

### 3. planning

Stores scheduled work sessions.

```sql
CREATE TABLE planning (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    scheduled_start DATETIME NOT NULL,
    scheduled_end DATETIME NOT NULL,
    priority ENUM('low', 'medium', 'critical') DEFAULT 'medium',
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

**Key Points:**
- No overlapping allowed (validated before insert/update)
- `scheduled_start` and `scheduled_end` must be on the same day
- Priority helps visual differentiation

### 4. planning_tags

Many-to-many relationship between planning and tags.

```sql
CREATE TABLE planning_tags (
    planning_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (planning_id, tag_id),
    FOREIGN KEY (planning_id) REFERENCES planning(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

### 5. sessions

Stores actual work sessions (execution tracking).

```sql
CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NULL,  -- NULL = session without project
    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,  -- NULL = session is active
    planned_duration INT NOT NULL,  -- minutes
    actual_duration INT GENERATED ALWAYS AS (
        CASE
            WHEN end_time IS NULL THEN NULL
            ELSE TIMESTAMPDIFF(MINUTE, start_time, end_time)
        END
    ) STORED,
    planning_id INT NULL,  -- Reference to planning if started from schedule
    notes TEXT NULL,
    satisfaction_score INT NULL CHECK (satisfaction_score BETWEEN 0 AND 100),
    tasks_done TEXT NULL,  -- What was accomplished
    notification_disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (planning_id) REFERENCES planning(id) ON DELETE SET NULL
);
```

**Key Points:**
- Only one session can be active at a time (`end_time = NULL`)
- `actual_duration`: Auto-calculated from start and end times
- `project_id = NULL`: Allowed for sessions without a specific project
- `satisfaction_score`: Default is 80 in UI

### 6. session_tags

Many-to-many relationship between sessions and tags.

```sql
CREATE TABLE session_tags (
    session_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (session_id, tag_id),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

### 7. settings

Global application settings.

```sql
CREATE TABLE settings (
    key_name VARCHAR(100) PRIMARY KEY,
    value_json JSON NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Initial Settings:**
```json
{
    "notification_interval_default": 10,  // minutes
    "session_poll_interval": 120,  // seconds (2 minutes)
    "language": "en"
}
```

## Indexes

```sql
-- For faster queries
CREATE INDEX idx_sessions_end_time ON sessions(end_time);
CREATE INDEX idx_planning_dates ON planning(scheduled_start, scheduled_end);
CREATE INDEX idx_projects_archived ON projects(is_archived);
CREATE INDEX idx_projects_pinned ON projects(is_pinned);
```

## Important Constraints

1. **Single Active Session**: Enforced by application logic (check before starting new session)
2. **No Overlapping Planning**: Enforced by application logic (check before insert/update)
3. **Same-Day Planning**: Enforced by application logic
4. **Tag Inheritance**: Project-specific tags can be used by the project and all its children

## Migration Strategy

Using **Alembic** for database migrations:
- All schema changes tracked in version control
- Easy rollback if needed
- Automated migration on deployment
