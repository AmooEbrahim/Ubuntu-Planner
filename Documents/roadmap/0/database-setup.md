# Database Setup Details

Detailed instructions for setting up the MySQL database schema.

## Database Creation

### 1. Create Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE os_services_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE os_services_planner;
```

### 2. Verify Database

```sql
SHOW DATABASES;
SELECT DATABASE();
```

## Schema Creation via Alembic

The preferred method is using Alembic migrations (covered in setup.md).

## Manual Schema Creation (Alternative)

If Alembic is not used, here's the manual SQL schema:

### Projects Table

```sql
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id INT NULL,
    color VARCHAR(7) NOT NULL,
    description TEXT NULL,
    default_duration INT NOT NULL DEFAULT 60,
    notification_interval INT NULL,
    is_archived BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES projects(id) ON DELETE SET NULL,
    INDEX idx_archived (is_archived),
    INDEX idx_pinned (is_pinned)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Tags Table

```sql
CREATE TABLE tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) NOT NULL,
    project_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_tag_per_project (name, project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Planning Table

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
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_planning_dates (scheduled_start, scheduled_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Planning Tags (Many-to-Many)

```sql
CREATE TABLE planning_tags (
    planning_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (planning_id, tag_id),
    FOREIGN KEY (planning_id) REFERENCES planning(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Sessions Table

```sql
CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,
    planned_duration INT NOT NULL,
    actual_duration INT GENERATED ALWAYS AS (
        CASE
            WHEN end_time IS NULL THEN NULL
            ELSE TIMESTAMPDIFF(MINUTE, start_time, end_time)
        END
    ) STORED,
    planning_id INT NULL,
    notes TEXT NULL,
    satisfaction_score INT NULL CHECK (satisfaction_score BETWEEN 0 AND 100),
    tasks_done TEXT NULL,
    notification_disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (planning_id) REFERENCES planning(id) ON DELETE SET NULL,
    INDEX idx_sessions_end_time (end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Session Tags (Many-to-Many)

```sql
CREATE TABLE session_tags (
    session_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (session_id, tag_id),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Settings Table

```sql
CREATE TABLE settings (
    key_name VARCHAR(100) PRIMARY KEY,
    value_json JSON NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Initial Settings Data

```sql
INSERT INTO settings (key_name, value_json) VALUES
('notification_interval_default', '10'),
('session_poll_interval', '120'),
('language', '"en"');
```

## Verification

### Check Tables

```sql
SHOW TABLES;
```

Expected output:
```
+--------------------------------+
| Tables_in_os_services_planner |
+--------------------------------+
| planning                       |
| planning_tags                  |
| projects                       |
| session_tags                   |
| sessions                       |
| settings                       |
| tags                           |
+--------------------------------+
```

### Check Table Structure

```sql
DESCRIBE projects;
DESCRIBE tags;
DESCRIBE planning;
DESCRIBE sessions;
```

### Test Insert

```sql
-- Insert test project
INSERT INTO projects (name, color, description, default_duration)
VALUES ('Test Project', '#3B82F6', 'A test project', 60);

-- Verify
SELECT * FROM projects;

-- Clean up
DELETE FROM projects WHERE name = 'Test Project';
```

## Backup and Restore

### Backup

```bash
mysqldump -u root -p os_services_planner > backup.sql
```

### Restore

```bash
mysql -u root -p os_services_planner < backup.sql
```

## Troubleshooting

### Issue: Access denied
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON os_services_planner.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### Issue: Character encoding problems
Ensure database and tables use utf8mb4:
```sql
ALTER DATABASE os_services_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Issue: Foreign key constraint fails
Check that parent records exist before inserting children.
